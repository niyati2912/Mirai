import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    SentinelHubCatalog,
    BBox,
    CRS,
)

load_dotenv()

CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Copernicus credentials not found in .env")


config = SHConfig()

config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "copernicus"
RAW_DIR.mkdir(parents=True, exist_ok=True)


REGIONS = {

    "india": BBox(
        bbox=[68.0, 6.0, 97.0, 37.0],
        crs=CRS.WGS84
    ),

    "usa": BBox(
        bbox=[-125.0, 24.0, -66.0, 49.0],
        crs=CRS.WGS84
    )

}

TIME_INTERVAL = (
    "2020-01-01",
    "2025-12-31",
)

def download_region(region_name, bbox):

    print(f"\nDownloading {region_name}")

    catalog = SentinelHubCatalog(config=config)

    search_iterator = catalog.search(
        collection="sentinel-2-l2a",
        bbox=bbox,
        time=TIME_INTERVAL,
    )

    records = []

    for item in search_iterator:

        records.append({

            "id": item["id"],

            "datetime": item["properties"]["datetime"],

            "cloud_cover": item["properties"].get(
                "eo:cloud_cover"
            ),

            "collection": item["collection"],

        })

    df = pd.DataFrame(records)

    output = RAW_DIR / f"{region_name}.csv"

    df.to_csv(output, index=False)

    print(f"Saved -> {output}")



def main():

    print("=" * 60)
    print("MIRAI - COPERNICUS ETL")
    print("=" * 60)

    for region, bbox in REGIONS.items():

        try:

            download_region(region, bbox)

        except Exception as e:

            print(f"Failed -> {region}")
            print(e)

    print("\nFinished downloading Copernicus datasets.")


if __name__ == "__main__":
    main()