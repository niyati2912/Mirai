import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Columns to turn into a percent-change feature (e.g. CPI -> inflation rate)
COLUMNS_FOR_PCT_CHANGE = [
    "fred_CPI",
    "fred_GDP",
    "fred_UnemploymentRate",
]

# Columns to compute rolling stats and momentum on (usually market data)
COLUMNS_FOR_ROLLING = [
    "yahoo_sp500_Close",
    "yahoo_gold_Close",
]

COLUMNS_FOR_LAG = [
    "fred_CPI",
    "fred_GDP",
    "yahoo_gold_Close",
]

ROLLING_WINDOWS = [3, 6]
LAG_PERIODS = [1]


def add_pct_change_features(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[f"{col}_pct_change"] = df[col].pct_change()
        else:
            log.warning("Column '%s' not found, skipping pct_change", col)
    return df


def add_rolling_features(df: pd.DataFrame, columns: list[str], windows: list[int]) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            log.warning("Column '%s' not found, skipping rolling features", col)
            continue
        for window in windows:
            df[f"{col}_ma{window}"] = df[col].rolling(window).mean()
            df[f"{col}_vol{window}"] = df[col].rolling(window).std()
        df[f"{col}_momentum"] = df[col] - df[col].shift(1)
    return df


def add_lag_features(df: pd.DataFrame, columns: list[str], periods: list[int]) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            log.warning("Column '%s' not found, skipping lag features", col)
            continue
        for period in periods:
            df[f"{col}_lag{period}"] = df[col].shift(period)
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df["Month"] = df["Date"].dt.month
    df["Quarter"] = df["Date"].dt.quarter
    df["Year"] = df["Date"].dt.year
    return df


def build_feature_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    df = add_pct_change_features(df, COLUMNS_FOR_PCT_CHANGE)
    df = add_rolling_features(df, COLUMNS_FOR_ROLLING, ROLLING_WINDOWS)
    df = add_lag_features(df, COLUMNS_FOR_LAG, LAG_PERIODS)
    df = add_time_features(df)

    rows_before = len(df)
    df = df.dropna().reset_index(drop=True)
    log.info("Feature table: %d -> %d rows after dropping NaNs from new features", rows_before, len(df))

    return df


def main():
    master_path = PROCESSED_DIR / "master_dataset.csv"
    df = pd.read_csv(master_path)

    features = build_feature_table(df)

    out_path = PROCESSED_DIR / "feature_table.csv"
    features.to_csv(out_path, index=False)
    log.info("Saved %s — shape=%s", out_path, features.shape)

    return features


if __name__ == "__main__":
    main()
