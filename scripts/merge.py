from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("mirai.merge")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "merged_dataset.csv"


# --------------------------------------------------------------------------
# Datasets
# --------------------------------------------------------------------------

DATASETS = {

    # -------------------------
    # FRED
    # -------------------------

    "fred": [
        "vix",
        "yield_curve",
        "building_permits",
        "unemployment_rate",
        "consumer_sentiment",
        "industrial_production",
        "federal_funds_rate",
        "cpi",
        "housing_starts",
        "retail_sales",
    ],

    # -------------------------
    # EIA
    # -------------------------

    "eia": [
        "petroleum_prices",
        "natural_gas_prices",
        "electricity_generation",
        "electricity_demand",
    ],

    # -------------------------
    # Google Trends
    # -------------------------

    "trends": [
        "financial_anxiety",
        "consumer_caution",
        "employment_stress",
        "housing_stress",
        "economic_optimism",
        "inflation_fear",
    ],
}


# --------------------------------------------------------------------------
# Loader
# --------------------------------------------------------------------------

def load_csv(folder: str, filename: str) -> pd.DataFrame:

    path = RAW_DIR / folder / f"{filename}.csv"

    logger.info("Loading %s", path)

    df = pd.read_csv(path)

    date_column = None

    for col in df.columns:

        if col.lower() in ["date", "period"]:
            date_column = col
            break

    if date_column is None:
        raise ValueError(f"No date column found in {filename}")

    df.rename(columns={date_column: "date"}, inplace=True)

    df["date"] = pd.to_datetime(df["date"])

    return df


# --------------------------------------------------------------------------
# Merge
# --------------------------------------------------------------------------

def merge_all() -> pd.DataFrame:

    master = None

    for folder, datasets in DATASETS.items():

        for dataset in datasets:

            df = load_csv(folder, dataset)

            if master is None:

                master = df

            else:

                master = pd.merge(
                    master,
                    df,
                    on="date",
                    how="outer",
                )

    master = master.sort_values("date")

    return master


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():

    print("=" * 60)
    print("MIRAI DATA MERGER")
    print("=" * 60)

    merged = merge_all()

    merged.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Merged dataset saved to %s",
        OUTPUT_FILE,
    )

    logger.info(
        "Rows: %d | Columns: %d",
        len(merged),
        len(merged.columns),
    )


if __name__ == "__main__":
    main()