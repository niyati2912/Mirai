import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from eia import API



load_dotenv()

API_KEY = os.getenv("EIA_API_KEY")

if not API_KEY:
    raise ValueError("EIA_API_KEY not found in .env")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "eia"
RAW_DIR.mkdir(parents=True, exist_ok=True)


api = API(API_KEY)


DATASETS = {

    "electricity_demand": {
        "route": "electricity/rto/region-data",
        "frequency": "monthly"
    },

    "fuel_type_generation": {
        "route": "electricity/rto/fuel-type-data",
        "frequency": "monthly"
    },

    "petroleum_prices": {
        "route": "petroleum/pri/gnd/data",
        "frequency": "monthly"
    },

    "natural_gas": {
        "route": "natural-gas/pri/sum/data",
        "frequency": "monthly"
    }

}


def download_dataset(name, config):

    print(f"\nDownloading {name}")

    try:

        data = api.data_by_route(
            route=config["route"],
            frequency=config["frequency"]
        )

        df = pd.DataFrame(data)

        output = RAW_DIR / f"{name}.csv"

        df.to_csv(output, index=False)

        print(f"Saved -> {output}")

    except Exception as e:

        print(f"Failed -> {name}")
        print(e)


def main():

    print("=" * 60)
    print("MIRAI - EIA ETL")
    print("=" * 60)

    for name, config in DATASETS.items():

        download_dataset(name, config)

    print("\nFinished downloading EIA datasets.")


if __name__ == "__main__":
    main()