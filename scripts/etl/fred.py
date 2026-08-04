import logging
import os
import time
from pathlib import Path

import pandas as pd
import pyfredapi as pf
from dotenv import load_dotenv


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("mirai.fred")

load_dotenv()

API_KEY = os.getenv("FRED_API_KEY")

if not API_KEY:
    raise ValueError("FRED_API_KEY not found in .env")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fred"
RAW_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_DELAY = 1


# --------------------------------------------------------------------------
# Economic Indicators
# --------------------------------------------------------------------------

SERIES = {
    "vix": "VIXCLS",
    "yield_curve": "T10Y2Y",
    "building_permits": "PERMIT",
    "unemployment_rate": "UNRATE",
    "consumer_sentiment": "UMCSENT",
    "industrial_production": "INDPRO",
    "federal_funds_rate": "FEDFUNDS",
    "cpi": "CPIAUCSL",
    "housing_starts": "HOUST",
    "retail_sales": "RSAFS",
}


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def download_series(series_name: str, series_id: str) -> bool:

    logger.info("=" * 60)
    logger.info("Downloading series: %s (%s)", series_name, series_id)
    logger.info("=" * 60)

    try:

        df = pf.get_series(
            series_id=series_id,
            api_key=API_KEY,
        )

        # Convert Series -> DataFrame
        if isinstance(df, pd.Series):
            df = df.reset_index()
            df.columns = ["date", series_name]

        # Standardize DataFrame column names
        elif isinstance(df, pd.DataFrame):

            cols = {c.lower(): c for c in df.columns}

            if "date" in cols:
                df.rename(columns={cols["date"]: "date"}, inplace=True)

            if "value" in cols:
                df.rename(columns={cols["value"]: series_name}, inplace=True)

        if df.empty:
            raise ValueError("No data returned.")

        output_path = RAW_DIR / f"{series_name}.csv"

        df.to_csv(output_path, index=False)

        logger.info(
            "Saved %s (%d rows)",
            output_path.name,
            len(df),
        )

        time.sleep(REQUEST_DELAY)

        return True

    except Exception as e:

        logger.error(
            "Failed to download %s: %s",
            series_name,
            e,
        )

        return False


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():

    print("=" * 60)
    print("MIRAI - FRED ETL")
    print("=" * 60)

    successful = 0

    for name, sid in SERIES.items():

        if download_series(name, sid):
            successful += 1

    print("\nSummary")
    print(f"Downloaded: {successful}/{len(SERIES)} datasets")

    if successful == len(SERIES):
        print("All datasets downloaded successfully.")
    else:
        print("Some datasets failed. Check logs above.")


if __name__ == "__main__":
    main()