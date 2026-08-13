from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger("mirai.ess")


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "ess_dataset.csv"

FORECAST_HORIZON = 3

CHANGE_WINDOW = 3
ZSCORE_WINDOW = 12
MIN_PERIODS = 6


CATEGORY_WEIGHTS = {
    "macro": 0.45,
    "energy": 0.20,
    "behavioral": 0.35,
}


INDICATORS = {
    "macro": [
        ("fred_vix", True),
        ("fred_yield_curve", False),
        ("fred_unemployment_rate", True),
        ("fred_cpi", True),
        ("fred_federal_funds_rate", True),
        ("fred_industrial_production", False),
        ("fred_consumer_sentiment", False),
        ("fred_housing_starts", False),
        ("fred_retail_sales", False),
        ("fred_building_permits", False),
    ],

    "energy": [
        ("eia_electricity_demand", False),
        ("eia_electricity_generation", False),
        ("eia_natural_gas_prices", True),
        ("eia_petroleum_prices", True),
    ],

    "behavioral": [
        ("trends_consumer_caution", True),
        ("trends_economic_optimism", False),
        ("trends_employment_stress", True),
        ("trends_financial_anxiety", True),
        ("trends_housing_stress", True),
        ("trends_inflation_fear", True),
    ],
}


ENGINEERED_SUFFIXES = (
    "_pct_change",
    "_lag1",
    "_rolling3",
    "_rolling6",
    "_rolling3_std",
)


def find_indicator_columns(
    df: pd.DataFrame,
    prefix: str,
) -> list[str]:

    columns = []

    for column in df.columns:

        if column == prefix:
            columns.append(column)
            continue

        if not column.startswith(prefix + "_"):
            continue

        if column.endswith(ENGINEERED_SUFFIXES):
            continue

        columns.append(column)

    return columns


def calculate_change(
    series: pd.Series,
) -> pd.Series:

    series = pd.to_numeric(
        series,
        errors="coerce",
    )

    pct_change = series.pct_change(
        periods=CHANGE_WINDOW
    )

    absolute_change = series.diff(
        periods=CHANGE_WINDOW
    )

    invalid = (
        ~np.isfinite(pct_change)
        | series.shift(CHANGE_WINDOW).eq(0)
    )

    pct_change[invalid] = (
        absolute_change[invalid]
    )

    return pct_change.replace(
        [np.inf, -np.inf],
        np.nan,
    )


def calculate_trailing_zscore(
    series: pd.Series,
) -> pd.Series:

    rolling_mean = (
        series
        .rolling(
            window=ZSCORE_WINDOW,
            min_periods=MIN_PERIODS,
        )
        .mean()
    )

    rolling_std = (
        series
        .rolling(
            window=ZSCORE_WINDOW,
            min_periods=MIN_PERIODS,
        )
        .std()
    )

    rolling_std = rolling_std.replace(
        0,
        np.nan,
    )

    return (
        series - rolling_mean
    ) / rolling_std


def calculate_stress_signal(
    series: pd.Series,
    higher_is_stress: bool,
) -> pd.Series:

    change = calculate_change(series)

    score = calculate_trailing_zscore(
        change
    )

    if not higher_is_stress:
        score = -score

    return score


def build_indicator_score(
    df: pd.DataFrame,
    prefix: str,
    higher_is_stress: bool,
) -> pd.Series | None:

    columns = find_indicator_columns(
        df,
        prefix,
    )

    if not columns:

        log.warning(
            "No columns found for %s",
            prefix,
        )

        return None

    scores = []

    for column in columns:

        score = calculate_stress_signal(
            df[column],
            higher_is_stress,
        )

        scores.append(score)

    return pd.concat(
        scores,
        axis=1,
    ).mean(
        axis=1,
        skipna=True,
    )


def build_category_score(
    df: pd.DataFrame,
    indicators: list[tuple[str, bool]],
    category: str,
) -> pd.Series:

    indicator_scores = []

    for prefix, higher_is_stress in indicators:

        score = build_indicator_score(
            df,
            prefix,
            higher_is_stress,
        )

        if score is None:
            continue

        indicator_scores.append(score)

        log.info(
            "%s: included %s",
            category,
            prefix,
        )

    if not indicator_scores:

        return pd.Series(
            np.nan,
            index=df.index,
        )

    return pd.concat(
        indicator_scores,
        axis=1,
    ).mean(
        axis=1,
        skipna=True,
    )


def build_ess(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    category_scores = {}

    for category, indicators in INDICATORS.items():

        score = build_category_score(
            result,
            indicators,
            category,
        )

        category_scores[category] = score

        result[f"ESS_{category}"] = score

    score_df = pd.DataFrame(
        category_scores,
        index=result.index,
    )

    weight_series = pd.Series(
        CATEGORY_WEIGHTS
    )

    available = score_df.notna()

    weighted_scores = score_df.mul(
        weight_series,
        axis=1,
    )

    available_weights = available.mul(
        weight_series,
        axis=1,
    )

    raw_ess = (
        weighted_scores.sum(
            axis=1,
            min_count=1,
        )
        /
        available_weights.sum(
            axis=1,
            min_count=1,
        )
    )

    raw_ess = raw_ess.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    result["ESS"] = (
        50 + raw_ess * 10
    ).clip(
        lower=0,
        upper=100,
    )

    return result


def create_target(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result["ESS_target"] = (
        result["ESS"]
        .shift(-FORECAST_HORIZON)
    )

    return result


def main():

    log.info("=" * 70)
    log.info("MIRAI ECONOMIC STRESS SCORE")
    log.info("=" * 70)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Feature table not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    if df.empty:

        raise RuntimeError(
            "feature_table.csv is empty."
        )

    if "Date" not in df.columns:

        raise ValueError(
            "Date column not found."
        )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    df = (
        df
        .dropna(subset=["Date"])
        .sort_values("Date")
        .reset_index(drop=True)
    )

    log.info(
        "Input shape: %d rows x %d columns",
        len(df),
        len(df.columns),
    )

    df = build_ess(df)

    valid_ess = int(
        df["ESS"].notna().sum()
    )

    log.info(
        "Valid ESS values: %d / %d",
        valid_ess,
        len(df),
    )

    if valid_ess == 0:

        raise RuntimeError(
            "No valid ESS values were produced."
        )

    before = len(df)

    df = (
        df
        .dropna(subset=["ESS"])
        .reset_index(drop=True)
    )

    log.info(
        "Removed %d rows without current ESS.",
        before - len(df),
    )

    df = create_target(df)

    before = len(df)

    df = (
        df
        .dropna(subset=["ESS_target"])
        .reset_index(drop=True)
    )

    log.info(
        "Removed %d rows without 3-month future ESS.",
        before - len(df),
    )

    log.info("=" * 70)
    log.info("ESS VALIDATION")
    log.info("=" * 70)

    log.info(
        "ESS count: %d",
        df["ESS"].count(),
    )

    log.info(
        "ESS mean: %.3f",
        df["ESS"].mean(),
    )

    log.info(
        "ESS std: %.3f",
        df["ESS"].std(),
    )

    log.info(
        "ESS min: %.3f",
        df["ESS"].min(),
    )

    log.info(
        "ESS max: %.3f",
        df["ESS"].max(),
    )

    log.info(
        "ESS target count: %d",
        df["ESS_target"].count(),
    )

    log.info(
        "Date range: %s -> %s",
        df["Date"].min(),
        df["Date"].max(),
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    log.info("=" * 70)
    log.info("ESS DATASET CREATED")
    log.info(
        "Output: %s",
        OUTPUT_FILE,
    )
    log.info(
        "Shape: %d rows x %d columns",
        len(df),
        len(df.columns),
    )
    log.info("=" * 70)


if __name__ == "__main__":
    main()