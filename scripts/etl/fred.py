"""
FRED ETL Pipeline
-----------------
Downloads economic indicators from the Federal Reserve (FRED)
and stores them in data/raw/fred/

Author: MIRAI
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pyfredapi import Fred


# =========================
# Load Environment Variables
# =========================

load_dotenv()

API_KEY = os.getenv("FRED_API_KEY")

if API_KEY is None:
    raise ValueError("FRED_API_KEY not found in .env")


# =========================
# Initialize Client
# =========================

fred = Fred(api_key=API_KEY)


# =========================
# Output Directory
# =========================

RAW_DIR = Path("data/raw/fred")
RAW_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# Economic Indicators
# =========================

SERIES = {
    "vix": "VIXCLS",
    "yield_curve": "T10Y2Y",
    "building_permits": "PERMIT",
    "unemployment_rate": "UNRATE",
    "consumer_confidence": "UMCSENT",
    "industrial_production": "INDPRO",
    "federal_funds_rate": "FEDFUNDS",
    "cpi": "CPIAUCSL",
    "housing_starts": "HOUST",
    "retail_sales": "RSAFS"
}


# =========================
# Download Function
# =========================

def download_series(name: str, series_id: str) -> None:
    """
    Downloads one FRED series and saves it as CSV.
    """

    print(f"Downloading {name} ({series_id})...")

    df = fred.get_series(series_id=series_id)

    if isinstance(df, pd.Series):
        df = df.reset_index()
        df.columns = ["Date", "Value"]

    output_file = RAW_DIR / f"{name}.csv"

    df.to_csv(output_file, index=False)

    print(f"Saved -> {output_file}")


# =========================
# Main
# =========================

def main():

    print("=" * 50)
    print("MIRAI FRED ETL")
    print("=" * 50)

    for name, sid in SERIES.items():
        try:
            download_series(name, sid)

        except Exception as e:
            print(f"Failed: {name}")
            print(e)

    print("\nDone!")


if __name__ == "__main__":
    main()