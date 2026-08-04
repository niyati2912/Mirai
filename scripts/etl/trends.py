from pathlib import Path
import logging
import time

import pandas as pd
from trendspy import Trends


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("mirai.trends")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "trends"
RAW_DIR.mkdir(parents=True, exist_ok=True)

TIMEFRAME = "today 5-y"
GEO = "US"
REQUEST_DELAY = 2

trends = Trends()


# --------------------------------------------------------------------------
# Behavioral Vocabulary
# --------------------------------------------------------------------------

BEHAVIORAL_VOCABULARY = {

    "financial_anxiety": [
        "layoffs",
        "bankruptcy",
        "debt consolidation",
        "pawn shop",
        "unemployment benefits"
    ],

    "consumer_caution": [
        "cheap groceries",
        "coupon",
        "thrift store",
        "used cars",
        "budget meals"
    ],

    "employment_stress": [
        "resume template",
        "linkedin jobs",
        "indeed jobs",
        "remote jobs",
        "interview questions"
    ],

    "housing_stress": [
        "mortgage rates",
        "rent increase",
        "eviction",
        "affordable housing",
        "home loan"
    ],

    "economic_optimism": [
        "vacation",
        "investment",
        "startup",
        "new house",
        "luxury watch"
    ],

    "inflation_fear": [
        "inflation",
        "recession",
        "food prices",
        "gas prices",
        "cost of living"
    ]
}


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def download_category(category: str, keywords: list[str]) -> bool:

    logger.info("=" * 60)
    logger.info("Downloading category: %s", category)
    logger.info("=" * 60)

    try:

        df = trends.interest_over_time(
            keywords=keywords,
            geo=GEO,
            timeframe=TIMEFRAME
        )

        if df.empty:
            raise ValueError("No data returned.")

        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        output_path = RAW_DIR / f"{category}.csv"

        df.to_csv(output_path, index=True)

        logger.info(
            "Saved %s (%d rows)",
            output_path.name,
            len(df)
        )

        time.sleep(REQUEST_DELAY)

        return True

    except Exception as e:

        logger.error(
            "Failed to download %s: %s",
            category,
            e
        )

        return False


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():

    print("=" * 60)
    print("MIRAI - GOOGLE TRENDS ETL")
    print("=" * 60)

    successful = 0

    for category, keywords in BEHAVIORAL_VOCABULARY.items():

        if download_category(category, keywords):
            successful += 1

    print("\nSummary")
    print(f"Downloaded: {successful}/{len(BEHAVIORAL_VOCABULARY)} datasets")

    if successful == len(BEHAVIORAL_VOCABULARY):
        print("All datasets downloaded successfully.")
    else:
        print("Some datasets failed. Check logs above.")


if __name__ == "__main__":
    main()