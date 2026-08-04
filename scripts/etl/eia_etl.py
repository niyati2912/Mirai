"""
MIRAI EIA ETL
=============
Downloads national-level energy indicators from the EIA API and writes
monthly-resampled CSVs to data/raw/eia/.

Datasets:
    - petroleum_prices:      U.S. average retail regular gasoline price ($/gal, weekly -> monthly mean)
    - natural_gas_prices:    U.S. residential natural gas price ($/Mcf, monthly)
    - electricity_generation: U.S. Lower-48 total net generation, all fuel types (MWh, hourly -> monthly sum)
    - electricity_demand:    U.S. Lower-48 total demand (MWh, hourly -> monthly sum)

All series are scoped to national aggregates (duoarea='NUS' / respondent='US48')
to avoid pulling per-state/per-BA detail that isn't needed for a national ESS.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv

from eia import EIAClient

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mirai.eia_etl")

load_dotenv()

API_KEY = os.getenv("EIA_API_KEY")
if not API_KEY:
    raise ValueError("EIA_API_KEY not found in .env")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "eia"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Electricity data on the EIA v2 API only starts 2019-01-01; use that as the
# common start so all four series stay aligned when merged later.
START_DATE = "2019-01-01"
END_DATE = date.today().isoformat()

PAGE_SIZE = 5000
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
INTER_PAGE_SLEEP_SECONDS = 0.5  # be polite to the API between pages


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration for a single EIA dataset pull."""

    route: str
    facets: Dict[str, str]
    api_frequency: str          # frequency id EIA expects, e.g. 'hourly', 'monthly', 'weekly'
    resample_rule: str          # pandas resample rule, e.g. 'MS'
    resample_agg: str           # 'sum' or 'mean'
    value_col: str              # output column name
    sum_across_facet_groups: bool = False  # True if multiple rows share a period (e.g. per-fueltype)


DATASETS: Dict[str, DatasetConfig] = {
    "petroleum_prices": DatasetConfig(
        route="petroleum/pri/gnd/data",
        facets={"duoarea": "NUS", "product": "EPMR", "process": "PTE"},
        api_frequency="weekly",
        resample_rule="MS",
        resample_agg="mean",
        value_col="gasoline_price_usd_per_gal",
    ),
    "natural_gas_prices": DatasetConfig(
        route="natural-gas/pri/sum/data",
        facets={"duoarea": "NUS", "product": "EPG0", "process": "PRS"},
        api_frequency="monthly",
        resample_rule="MS",
        resample_agg="mean",
        value_col="nat_gas_residential_price_usd_per_mcf",
    ),
    "electricity_generation": DatasetConfig(
        route="electricity/rto/fuel-type-data",
        facets={"respondent": "US48"},
        api_frequency="hourly",
        resample_rule="MS",
        resample_agg="sum",
        value_col="generation_mwh",
        sum_across_facet_groups=True,  # multiple fueltype rows per timestamp; sum them
    ),
    "electricity_demand": DatasetConfig(
        route="electricity/rto/region-data",
        facets={"respondent": "US48", "type": "D"},
        api_frequency="hourly",
        resample_rule="MS",
        resample_agg="sum",
        value_col="demand_mwh",
    ),
}

client = EIAClient(api_key=API_KEY)


# --------------------------------------------------------------------------
# Core fetch logic
# --------------------------------------------------------------------------

def _fetch_page(
    route: str,
    facets: Dict[str, str],
    frequency: str,
    offset: int,
) -> List[Dict[str, Any]]:
    """
    Fetch a single page of records from the EIA API, with retry on failure.

    Raises the last exception if all retries are exhausted.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.get_data(
                route=route,
                data_columns=["value"],
                facets=facets,
                frequency=frequency,
                start=START_DATE,
                end=END_DATE,
                sort=[{"column": "period", "direction": "asc"}],
                length=PAGE_SIZE,
                offset=offset,
            )
            return resp["data"]
        except Exception as exc:  # noqa: BLE001 - deliberately broad, we retry regardless of cause
            last_exc = exc
            logger.warning(
                "Fetch failed (route=%s, offset=%d, attempt %d/%d): %s",
                route, offset, attempt, MAX_RETRIES, exc,
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    assert last_exc is not None
    raise last_exc


def fetch_all_records(config: DatasetConfig) -> List[Dict[str, Any]]:
    """Paginate through the EIA API until all records for a dataset are retrieved."""
    all_records: List[Dict[str, Any]] = []
    offset = 0

    while True:
        logger.info(
            "Fetching %s (offset=%d, page_size=%d)",
            config.route, offset, PAGE_SIZE,
        )
        batch = _fetch_page(config.route, config.facets, config.api_frequency, offset)

        if not batch:
            break

        all_records.extend(batch)
        offset += PAGE_SIZE

        if len(batch) < PAGE_SIZE:
            break  # last page

        time.sleep(INTER_PAGE_SLEEP_SECONDS)

    logger.info("Retrieved %d total records for route=%s", len(all_records), config.route)
    return all_records


# --------------------------------------------------------------------------
# Transform
# --------------------------------------------------------------------------

def records_to_monthly_frame(records: List[Dict[str, Any]], config: DatasetConfig) -> pd.DataFrame:
    """
    Convert raw EIA records into a clean, monthly-resampled DataFrame with
    columns ['date', config.value_col].
    """
    if not records:
        raise ValueError("No records to process — upstream fetch returned empty result.")

    df = pd.DataFrame.from_records(records)

    if "period" not in df.columns or "value" not in df.columns:
        raise KeyError(
            f"Expected 'period' and 'value' columns, got: {list(df.columns)}"
        )

    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    n_before = len(df)
    df = df.dropna(subset=["period", "value"])
    n_dropped = n_before - len(df)
    if n_dropped:
        logger.warning("Dropped %d rows with null period/value (route-level nulls, e.g. outages)", n_dropped)

    if config.sum_across_facet_groups:
        # Multiple rows can share the same timestamp (e.g. one per fuel type).
        # Sum them first so each timestamp collapses to a single national total
        # before we resample to monthly.
        df = df.groupby("period", as_index=False)["value"].sum()

    df = df.set_index("period").sort_index()

    resampled = df["value"].resample(config.resample_rule).agg(config.resample_agg)
    resampled = resampled.rename(config.value_col).reset_index()
    resampled = resampled.rename(columns={"period": "date"})

    return resampled


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def download_dataset(name: str, config: DatasetConfig) -> Optional[pd.DataFrame]:
    """
    Fetch, transform, and save one dataset. Returns the resulting DataFrame,
    or None if the dataset failed (logged, not raised, so one bad dataset
    doesn't abort the whole run).
    """
    logger.info("=" * 60)
    logger.info("Processing dataset: %s", name)
    logger.info("=" * 60)

    try:
        records = fetch_all_records(config)
        df = records_to_monthly_frame(records, config)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to process dataset '%s': %s", name, exc, exc_info=True)
        return None

    output_path = RAW_DIR / f"{name}.csv"
    df.to_csv(output_path, index=False)
    logger.info(
        "Saved %s: %d rows, %s -> %s",
        output_path, len(df),
        df["date"].min().date() if not df.empty else "N/A",
        df["date"].max().date() if not df.empty else "N/A",
    )
    return df


def main() -> None:
    print("=" * 60)
    print("MIRAI EIA ETL")
    print("=" * 60)

    results: Dict[str, Optional[pd.DataFrame]] = {}
    for name, config in DATASETS.items():
        results[name] = download_dataset(name, config)

    print("\nSummary:")
    for name, df in results.items():
        status = f"{len(df)} rows" if df is not None else "FAILED"
        print(f"  {name}: {status}")

    n_failed = sum(1 for df in results.values() if df is None)
    if n_failed:
        print(f"\n{n_failed} dataset(s) failed — check logs above.")
    else:
        print("\nAll datasets completed successfully.")


if __name__ == "__main__":
    main()