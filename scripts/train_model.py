from __future__ import annotations

import argparse
import logging
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] train_model: %(message)s")
logger = logging.getLogger("train_model")

DEFAULT_FEATURES_PATH = "data/processed/master_features.csv"
DEFAULT_ESS_PATH = "data/processed/ess_timeline.csv"
DEFAULT_MODEL_DIR = "data/models"

ESTIMATORS = {
    "random_forest": lambda: RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42),
    "linear": lambda: LinearRegression(),
}

TEST_FRACTION = 0.2  # last 20% of the timeline held out, chronologically


def load_dataset(features_path: str, ess_path: str) -> pd.DataFrame:
    features = pd.read_csv(features_path, parse_dates=["month"])
    ess = pd.read_csv(ess_path, parse_dates=["month"])
    merged = features.merge(ess[["month", "ess"]], on="month", how="inner")
    merged = merged.sort_values("month").reset_index(drop=True)
    return merged


def build_xy(df: pd.DataFrame, horizon: int = 0):
    """
    horizon=0  -> reconstruct: X(t) predicts ess(t)
    horizon>0  -> forecast:    X(t) predicts ess(t + horizon)
    """
    feature_cols = [c for c in df.columns if c not in ("month", "ess")
                     and pd.api.types.is_numeric_dtype(df[c])]

    X = df[feature_cols].copy()
    if horizon > 0:
        y = df["ess"].shift(-horizon)
        X = X.iloc[: len(X) - horizon]
        y = y.iloc[: len(y) - horizon]
    else:
        y = df["ess"]

    valid = X.notna().all(axis=1) & y.notna()
    X, y = X[valid], y[valid]
    logger.info("Training matrix: %d rows, %d features (horizon=%d)", len(X), X.shape[1], horizon)
    return X, y, feature_cols


def time_ordered_split(X: pd.DataFrame, y: pd.Series, test_fraction: float = TEST_FRACTION):
    split_idx = int(len(X) * (1 - test_fraction))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    return X_train, X_test, y_train, y_test


def train_and_evaluate(X, y, estimator_name: str):
    X_train, X_test, y_train, y_test = time_ordered_split(X, y)

    model = ESTIMATORS[estimator_name]()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    logger.info("Held-out performance — MAE: %.3f | R^2: %.3f (n_test=%d)", mae, r2, len(y_test))

    if hasattr(model, "feature_importances_"):
        importances = pd.Series(model.feature_importances_, index=X.columns)
        top = importances.sort_values(ascending=False).head(15)
        logger.info("Top 15 feature importances:\n%s", top.to_string())

    return model, {"mae": mae, "r2": r2, "n_test": len(y_test)}


def main():
    parser = argparse.ArgumentParser(description="Train ESS reconstruction or forecasting models")
    parser.add_argument("--mode", choices=["reconstruct", "forecast"], required=True)
    parser.add_argument("--horizon", type=int, default=3, help="Months ahead to forecast (forecast mode only)")
    parser.add_argument("--estimator", choices=list(ESTIMATORS.keys()), default="random_forest")
    parser.add_argument("--features", default=DEFAULT_FEATURES_PATH)
    parser.add_argument("--ess", default=DEFAULT_ESS_PATH)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    df = load_dataset(args.features, args.ess)

    horizon = 0 if args.mode == "reconstruct" else args.horizon
    X, y, feature_cols = build_xy(df, horizon=horizon)

    model, metrics = train_and_evaluate(X, y, args.estimator)

    os.makedirs(args.model_dir, exist_ok=True)
    tag = "reconstruct" if args.mode == "reconstruct" else f"forecast_h{args.horizon}"
    model_path = os.path.join(args.model_dir, f"ess_{tag}_{args.estimator}.joblib")
    joblib.dump({"model": model, "feature_cols": feature_cols, "metrics": metrics}, model_path)
    logger.info("Model saved -> %s", model_path)

    return model, metrics


if __name__ == "__main__":
    main()
