from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "frontend" / "public" / "data"


def read_csv(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    return pd.read_csv(file_path)


def get_ess_data():
    return read_csv("ess_dataset.csv")


def get_feature_importance():
    return read_csv("feature_importance.csv")


def get_model_metrics():
    return read_csv("model_metrics.csv")


def get_model_predictions():
    return read_csv("model_predictions.csv")