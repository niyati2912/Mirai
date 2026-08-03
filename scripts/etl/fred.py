import os
from pathlib import Path

import pandas as pd
import pyfredapi as pf
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("FRED_API_KEY")

if not API_KEY:
    raise ValueError("FRED_API_KEY not found in .env")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fred"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# Economic Indicators


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



def download_series(series_name: str, series_id: str):

    print(f"\nDownloading {series_name} ({series_id})")

    try:

        df = pf.get_series(
            series_id=series_id,
            api_key=API_KEY,
        )

        if isinstance(df, pd.Series):
            df = df.reset_index()
            df.columns = ["Date", "Value"]

        elif isinstance(df, pd.DataFrame):

            cols = {c.lower(): c for c in df.columns}

            if "date" in cols:
                df.rename(columns={cols["date"]: "Date"}, inplace=True)

            if "value" in cols:
                df.rename(columns={cols["value"]: "Value"}, inplace=True)

        output_path = RAW_DIR / f"{series_name}.csv"

        df.to_csv(output_path, index=False)

        print(f"Saved -> {output_path}")

    except Exception as e:

        print(f"Failed -> {series_name}")
        print(e)



def main():

    print("=" * 60)
    print("MIRAI - FRED ETL")
    print("=" * 60)

    for name, sid in SERIES.items():
        download_series(name, sid)

    print("\nFinished downloading all FRED datasets.")


if __name__ == "__main__":
    main()