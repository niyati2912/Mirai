from dotenv import load_dotenv
from fredapi import Fred
import pandas as pd
import os

# Load API key
load_dotenv()

api_key = os.getenv("FRED_API_KEY")

if api_key is None:
    raise ValueError("FRED_API_KEY not found in .env")

fred = Fred(api_key=api_key)


# FRED Indicators


INDICATORS = {
    "cpi": ("CPIAUCSL", "CPI"),
    "unemployment": ("UNRATE", "Unemployment"),
    "interest_rate": ("FEDFUNDS", "FederalFundsRate"),
    "industrial_production": ("INDPRO", "IndustrialProduction"),
    "consumer_sentiment": ("UMCSENT", "ConsumerSentiment"),

    "india_cpi": ("INDCPIALLMINMEI", "IndiaCPI"),
    "india_gdp": ("INDGDPNQDSMEI", "IndiaGDP"),
    "usd_inr": ("DEXINUS", "USDINR")
}


# dowload loop

for filename, (series_id, column_name) in INDICATORS.items():

    print(f"Downloading {column_name}...")

    data = fred.get_series(series_id)

    df = data.to_frame(name=column_name)

    df.to_csv(f"data/raw/{filename}.csv")

