from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] ess_builder: %(message)s")
logger = logging.getLogger("ess_builder")

DEFAULT_INPUT = "data/processed/master_features.csv"
DEFAULT_OUTPUT = "data/processed/ess_timeline.csv"

# +1 = higher value means MORE economic stress
# -1 = higher value means LESS economic stress (i.e. economic strength)
INDICATOR_DIRECTIONS = {
    # Petroleum
    "wti_crude_price": 1,
    "brent_crude_price": 1,
    "gasoline_price": 1,
    "diesel_price": 1,
    "petroleum_inventories": -1,     # high inventories = weak demand -> ambiguous, treated as mild relief signal
    # Natural gas
    "henry_hub_price": 1,
    "residential_gas_price": 1,
    "commercial_gas_price": 1,
    "industrial_gas_price": 1,
    # Electricity
    "electricity_demand": -1,        # rising demand -> industrial/consumer activity -> less stress
    "electricity_fuel_mix": -1,
    # Common FRED-style macro columns (rename to match your actual FRED output)
    "unemployment_rate": 1,
    "cpi": 1,
    "inflation_rate": 1,
    "fed_funds_rate": 1,
    "gdp_growth": -1,
    "industrial_production": -1,
    "consumer_sentiment": -1,
}

# Optional custom weights; anything unlisted defaults to 1.0
INDICATOR_WEIGHTS: dict = {}


def select_zscore_columns(df: pd.DataFrame) -> list:
    """
    Use only base-indicator z-scores (e.g. 'wti_crude_price_zscore'),
    not z-scores of derived features, to avoid double-counting the
    same signal multiple times in the composite.
    """
    return [c for c in df.columns if c.endswith("_zscore")]


def base_indicator_name(zscore_col: str) -> str:
    return zscore_col[: -len("_zscore")]


def build_ess(df: pd.DataFrame) -> pd.DataFrame:
    zscore_cols = select_zscore_columns(df)
    if not zscore_cols:
        raise ValueError(
            "No '*_zscore' columns found — run feature.py first to produce rolling z-scores."
        )

    weighted_sum = pd.Series(0.0, index=df.index)
    weight_total = 0.0
    used, unmapped = [], []

    for zcol in zscore_cols:
        indicator = base_indicator_name(zcol)
        direction = INDICATOR_DIRECTIONS.get(indicator)
        if direction is None:
            direction = 1
            unmapped.append(indicator)
        weight = INDICATOR_WEIGHTS.get(indicator, 1.0)

        weighted_sum = weighted_sum.add(direction * weight * df[zcol].fillna(0), fill_value=0)
        weight_total += weight
        used.append(indicator)

    if unmapped:
        logger.warning(
            "%d indicator(s) had no entry in INDICATOR_DIRECTIONS and defaulted to +1: %s",
            len(unmapped), unmapped,
        )
    logger.info("ESS built from %d indicators: %s", len(used), used)

    ess_raw = weighted_sum / weight_total

    # Scale to 0-100 using min-max over the observed history.
    ess_min, ess_max = ess_raw.min(), ess_raw.max()
    if ess_max == ess_min:
        raise ValueError("ESS has zero variance — cannot scale to 0-100.")
    ess_scaled = 100 * (ess_raw - ess_min) / (ess_max - ess_min)

    out = df[["month"]].copy()
    out["ess_raw"] = ess_raw
    out["ess"] = ess_scaled
    return out


def main():
    parser = argparse.ArgumentParser(description="Build the composite Economic Stress Score")
    parser.add_argument("--in", dest="input_path", default=DEFAULT_INPUT)
    parser.add_argument("--out", dest="output_path", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input_path, parse_dates=["month"])
    ess_df = build_ess(df)

    ess_df.to_csv(args.output_path, index=False)
    logger.info("ESS timeline written -> %s (%d rows)", args.output_path, len(ess_df))
    return ess_df


if __name__ == "__main__":
    main()
