import wbdata
import pandas as pd


COUNTRY = "IND"

INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "FP.CPI.TOTL.ZG": "inflation",
    "NE.EXP.GNFS.ZS": "exports",
    "NE.IMP.GNFS.ZS": "imports",
    "SL.UEM.TOTL.ZS": "unemployment"
}


for code, filename in INDICATORS.items():

    print(f"Downloading {filename}...")

    df = wbdata.get_dataframe(
        {code: filename},
        country=COUNTRY
    )

    df.sort_index(inplace=True)

    df.to_csv(f"data/raw/{filename}_india.csv")
