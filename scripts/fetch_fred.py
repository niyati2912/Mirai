from dotenv import load_dotenv
from fredapi import Fred
import pandas as pd 
import os

load_dotenv()

api_key = os.getenv("FRED_API_KEY")

if api_key is None:
    raise ValueError("FRED_API_KEY not found in .env file")

fred = Fred(api_key=api_key)

cpi = fred.get_series("CPIAUCSL")

df = cpi.to_frame(name="CPI")

df.to_csv("data/cpi_data.csv", index=True)

#print("CPI data fetched and saved to data/cpi_data.csv")

