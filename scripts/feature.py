from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] feature: %(message)s")
logger = logging.getLogger("feature")

ROLLING_WINDOWS = [3, 6, 12]
ZSCORE_WINDOW = 24        # trailing window for a "current regime" z-score
LAG_PERIODS = [1, 3, 6]

DEFAULT_INPUT = "data/processed/master_dataset.csv"
DEFAULT_OUTPUT = "data/processed/master_features.csv"


def numeric_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if c != "month" and pd.api.types.is_numeric_dtype(df[c])]


def add_rolling_stats(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        for w in ROLLING_WINDOWS:
            df[f"{col}_ma{w}"] = df[col].rolling(window=w, min_periods=w).mean()
            df[f"{col}_std{w}"] = df[col].rolling(window=w, min_periods=w).std()
    return df


def add_pct_change(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        df[f"{col}_pct_change"] = df[col].pct_change()
    return df


def add_lags(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        for lag in LAG_PERIODS:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)
    return df


def add_rolling_zscore(df: pd.DataFrame, cols: list, window: int = ZSCORE_WINDOW) -> pd.DataFrame:
    """
    Trailing-window z-score: how far the current value sits from its
    own recent history, in standard deviations. This is the input
    ess_builder.py consumes to build the composite stress index.
    """
    df = df.copy()
    for col in cols:
        roll_mean = df[col].rolling(window=window, min_periods=max(6, window // 4)).mean()
        roll_std = df[col].rolling(window=window, min_periods=max(6, window // 4)).std()
        df[f"{col}_zscore"] = (df[col] - roll_mean) / roll_std.replace(0, np.nan)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = numeric_columns(df)
    if not cols:
        raise ValueError("No numeric columns found to engineer features from.")

    logger.info("Engineering features for %d columns: %s", len(cols), cols)

    out = df.copy()
    out = add_pct_change(out, cols)
    out = add_rolling_stats(out, cols)
    out = add_lags(out, cols)
    out = add_rolling_zscore(out, cols)
    return out


def main():
    parser = argparse.ArgumentParser(description="Engineer rolling/lag/z-score features on the master dataset")
    parser.add_argument("--in", dest="input_path", default=DEFAULT_INPUT)
    parser.add_argument("--out", dest="output_path", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input_path, parse_dates=["month"])
    featured = build_features(df)

    featured.to_csv(args.output_path, index=False)
    logger.info("Feature dataset written -> %s (%d rows, %d cols)",
                args.output_path, *featured.shape)
    return featured


if __name__ == "__main__":
    main()
