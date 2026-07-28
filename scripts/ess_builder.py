"""
Builds the Economic Stress Score (ESS) and future ESS target.

Pipeline:
feature_table.csv
        ↓
Compute rolling z-scores
        ↓
Category scores
        ↓
Weighted ESS
        ↓
Scale to 0-100
        ↓
ESS_target = ESS shifted 3 months
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FORECAST_HORIZON_MONTHS = 3
ROLLING_WINDOW = 60

CATEGORY_WEIGHTS = {
    "macro": 0.30,
    "market": 0.25,
    "commodities": 0.15,
    "behavioral": 0.20,
    "external": 0.10,
}

INDICATOR_CATEGORIES = {
    "macro": [
        {"column": "cpi_CPI_pct_change", "invert": False},
        {"column": "interest_rate_FederalFundsRate", "invert": False},
        {"column": "unemployment_Unemployment", "invert": False},
        {"column": "industrial_production_IndustrialProduction_pct_change", "invert": True},
        {"column": "india_gdp_IndiaGDP_pct_change", "invert": True},
    ],

    "market": [
        {"column": "sp500_Close_vol3", "invert": False},
        {"column": "sp500_Close_momentum", "invert": True},
        {"column": "nasdaq_Close_momentum", "invert": True},
        {"column": "sensex_Close_momentum", "invert": True},
        {"column": "nifty50_Close_momentum", "invert": True},
    ],

    "commodities": [
        {"column": "gold_Close_momentum", "invert": False},
        {"column": "oil_Close_momentum", "invert": False},
    ],

    "behavioral": [
        {"column": "consumer_sentiment_ConsumerSentiment", "invert": True},
    ],

    "external": [
        {"column": "usd_inr_USDINR", "invert": False},
    ],
}


def rolling_zscore(series, window):
    mean = series.rolling(window=window, min_periods=12).mean()
    std = series.rolling(window=window, min_periods=12).std()

    z = (series - mean) / std

    return z.fillna(0)


def compute_category_score(df, indicators):
    scores = []

    for indicator in indicators:
        column = indicator["column"]

        if column not in df.columns:
            log.warning("Missing column: %s", column)
            continue

        z = rolling_zscore(df[column], ROLLING_WINDOW)

        if indicator["invert"]:
            z = -z

        scores.append(z)

    if len(scores) == 0:
        return pd.Series(0, index=df.index)

    return pd.concat(scores, axis=1).mean(axis=1)


def build_ess(df):
    category_scores = {}

    for category, indicators in INDICATOR_CATEGORIES.items():
        category_scores[category] = compute_category_score(df, indicators)

    raw_score = pd.Series(0, index=df.index)

    for category, weight in CATEGORY_WEIGHTS.items():
        raw_score += category_scores[category] * weight

    # Convert approximately -3...+3 to 0...100
    ess = ((raw_score + 3) / 6) * 100

    ess = ess.clip(0, 100)

    return ess


def main():

    file_path = PROCESSED_DIR / "feature_table.csv"

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    log.info("Building Economic Stress Score...")

    df["ESS"] = build_ess(df)

    df["ESS_target"] = df["ESS"].shift(-FORECAST_HORIZON_MONTHS)

    rows_before = len(df)

    df = df.dropna(subset=["ESS_target"]).reset_index(drop=True)

    log.info(
        "Dropped %d rows because future target is unavailable.",
        rows_before - len(df),
    )

    df.to_csv(file_path, index=False)

    log.info("Saved %s", file_path)

    log.info("\nESS Statistics")

    log.info(df["ESS"].describe())

    log.info("\nColumns Added:")
    log.info("ESS")
    log.info("ESS_target")

    return df


if __name__ == "__main__":
    main()