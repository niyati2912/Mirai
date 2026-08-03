from pathlib import Path
import pandas as pd
from trendspy import Trends


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "trends"
RAW_DIR.mkdir(parents=True, exist_ok=True)

trends = Trends()


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


def download_category(category, keywords):

    print(f"\nDownloading {category}")

    try:

        df = trends.interest_over_time(
            keywords=keywords,
            geo="US",
            timeframe="all"
        )

        df.to_csv(
            RAW_DIR / f"{category}.csv",
            index=True
        )

        print(f"Saved {category}")

    except Exception as e:

        print(f"Failed {category}")
        print(e)



def main():

    print("=" * 60)
    print("MIRAI - GOOGLE TRENDS ETL")
    print("=" * 60)

    for category, keywords in BEHAVIORAL_VOCABULARY.items():

        download_category(category, keywords)

    print("\nFinished downloading TrendSpy datasets.")


if __name__ == "__main__":
    main()