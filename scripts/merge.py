from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger("mirai.merge")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FRED_DIR = RAW_DIR / "fred"
EIA_DIR = RAW_DIR / "eia"
TRENDS_DIR = RAW_DIR / "trends"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "master_dataset.csv"

# Google Trends currently begins in 2021.
# This gives us a common period where all three major sources
# can contribute to MIRAI.
START_DATE = pd.Timestamp("2021-08-01")


# ---------------------------------------------------------------------
# Dataset definitions
# ---------------------------------------------------------------------

FRED_DATASETS = {
    "vix": "vix.csv",
    "yield_curve": "yield_curve.csv",
    "building_permits": "building_permits.csv",
    "unemployment_rate": "unemployment_rate.csv",
    "consumer_sentiment": "consumer_sentiment.csv",
    "industrial_production": "industrial_production.csv",
    "federal_funds_rate": "federal_funds_rate.csv",
    "cpi": "cpi.csv",
    "housing_starts": "housing_starts.csv",
    "retail_sales": "retail_sales.csv",
}

EIA_DATASETS = {
    "electricity_demand": "electricity_demand.csv",
    "electricity_generation": "electricity_generation.csv",
    "natural_gas_prices": "natural_gas_prices.csv",
    "petroleum_prices": "petroleum_prices.csv",
}

TREND_DATASETS = {
    "consumer_caution": "consumer_caution.csv",
    "economic_optimism": "economic_optimism.csv",
    "employment_stress": "employment_stress.csv",
    "financial_anxiety": "financial_anxiety.csv",
    "housing_stress": "housing_stress.csv",
    "inflation_fear": "inflation_fear.csv",
}


# ---------------------------------------------------------------------
# Date handling
# ---------------------------------------------------------------------

def find_date_column(df: pd.DataFrame) -> str:
    candidates = [
        "Date",
        "date",
        "DATE",
        "period",
        "Period",
        "time",
        "Time",
        "time [UTC]",
        "Time [UTC]",
        "timestamp",
        "Timestamp",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        f"No date column found. Columns: {list(df.columns)}"
    )

def prepare_dataframe(
    df: pd.DataFrame,
    source_name: str,
) -> pd.DataFrame:

    date_column = find_date_column(df)

    df = df.copy()

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
        utc=True,
    )

    df = df.dropna(subset=[date_column])

    df[date_column] = df[date_column].dt.tz_localize(None)

    # Convert everything to monthly timestamps.
    df["Date"] = (
        df[date_column]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Find numeric indicator columns.
    value_columns = [
        column
        for column in df.columns
        if column != "Date"
        and column != date_column
        and pd.api.types.is_numeric_dtype(df[column])
    ]

    if not value_columns:
        raise ValueError(
            f"{source_name}: no numeric columns found."
        )

    result = df[["Date"] + value_columns].copy()

    # Prefix columns so names remain unique after merging.
    result = result.rename(
        columns={
            column: f"{source_name}_{column}"
            for column in value_columns
        }
    )

    # Multiple observations per month -> monthly mean.
    result = (
        result
        .groupby("Date", as_index=False)
        .mean(numeric_only=True)
    )

    return result


# ---------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------

def load_dataset(
    directory: Path,
    filename: str,
    source_name: str,
) -> pd.DataFrame:

    path = directory / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    log.info("Loading %s", path)

    df = pd.read_csv(path)

    result = prepare_dataframe(
        df,
        source_name,
    )

    log.info(
        "%s -> %d rows, %d columns",
        source_name,
        len(result),
        len(result.columns),
    )

    return result


def load_all_datasets() -> list[pd.DataFrame]:

    datasets = []

    # FRED
    for name, filename in FRED_DATASETS.items():
        datasets.append(
            load_dataset(
                FRED_DIR,
                filename,
                f"fred_{name}",
            )
        )

    # EIA
    for name, filename in EIA_DATASETS.items():
        datasets.append(
            load_dataset(
                EIA_DIR,
                filename,
                f"eia_{name}",
            )
        )

    # Google Trends
    for name, filename in TREND_DATASETS.items():
        datasets.append(
            load_dataset(
                TRENDS_DIR,
                filename,
                f"trends_{name}",
            )
        )

    return datasets


# ---------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------

def merge_datasets(
    datasets: list[pd.DataFrame],
) -> pd.DataFrame:

    if not datasets:
        raise RuntimeError("No datasets available.")

    master = datasets[0].copy()

    for dataset in datasets[1:]:

        master = master.merge(
            dataset,
            on="Date",
            how="outer",
        )

    master = (
        master
        .sort_values("Date")
        .drop_duplicates("Date")
        .reset_index(drop=True)
    )

    return master


# ---------------------------------------------------------------------
# Missing values
# ---------------------------------------------------------------------

def handle_missing_values(
    df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()

    value_columns = [
        column
        for column in df.columns
        if column != "Date"
    ]

    # Only forward-fill.
    #
    # We NEVER back-fill because that would use future observations
    # to populate earlier dates and create information leakage.
    df[value_columns] = df[value_columns].ffill()

    return df


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> pd.DataFrame:

    log.info("=" * 70)
    log.info("MIRAI MASTER DATASET BUILDER")
    log.info("=" * 70)

    datasets = load_all_datasets()

    log.info("=" * 70)
    log.info("MERGING DATASETS")
    log.info("=" * 70)

    master = merge_datasets(datasets)

    log.info(
        "Before date filtering: %d rows x %d columns",
        len(master),
        len(master.columns),
    )

    # Remove the old sparse FRED-only history.
    master = master[
        master["Date"] >= START_DATE
    ].copy()

    master = master.sort_values("Date").reset_index(drop=True)

    log.info(
        "After date filtering: %d rows",
        len(master),
    )

    # Fill only information that was already available.
    master = handle_missing_values(master)

    # Remove completely empty columns.
    empty_columns = [
        column
        for column in master.columns
        if column != "Date"
        and master[column].isna().all()
    ]

    if empty_columns:

        log.warning(
            "Removing %d completely empty columns: %s",
            len(empty_columns),
            empty_columns,
        )

        master = master.drop(
            columns=empty_columns
        )

    # Final validation.
    master = master.sort_values("Date").reset_index(drop=True)

    master.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    log.info("=" * 70)
    log.info("MASTER DATASET CREATED")
    log.info("Output: %s", OUTPUT_FILE)
    log.info(
        "Shape: %d rows x %d columns",
        len(master),
        len(master.columns),
    )
    log.info(
        "Date range: %s -> %s",
        master["Date"].min(),
        master["Date"].max(),
    )

    missing = master.isna().sum()

    remaining_missing = missing[
        missing > 0
    ].sort_values(ascending=False)

    if not remaining_missing.empty:

        log.info("Remaining missing values:")

        for column, count in remaining_missing.items():

            log.info(
                "  %-45s %d",
                column,
                count,
            )

    else:
        log.info("No missing values remain.")

    log.info("=" * 70)

    return master


if __name__ == "__main__":
    main()