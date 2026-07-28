#TARGET OF MIRAI IS ECONOMIC STRESS SCORE


import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

TARGET_COLUMN = "ESS_target"
SPLIT_DATE = "2019-01-01"  # everything before = train, everything on/after = test


def load_feature_table() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "feature_table.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def chronological_split(df: pd.DataFrame, split_date: str):
    train = df[df["Date"] < split_date]
    test = df[df["Date"] >= split_date]
    log.info("Train: %d rows (%s -> %s)", len(train), train["Date"].min(), train["Date"].max())
    log.info("Test: %d rows (%s -> %s)", len(test), test["Date"].min(), test["Date"].max())
    return train, test


def split_xy(df: pd.DataFrame, target_column: str):
    X = df.drop(columns=["Date", target_column])
    y = df[target_column]
    return X, y


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestRegressor:
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=6,
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model: RandomForestRegressor, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)

    log.info("MAE: %.2f points", mae)
    log.info("RMSE: %.2f points", rmse)
    log.info("R2: %.3f", r2)


def feature_importance(model: RandomForestRegressor, X_train: pd.DataFrame, top_n: int = 15) -> pd.Series:
    importances = pd.Series(model.feature_importances_, index=X_train.columns)
    importances = importances.sort_values(ascending=False)
    log.info("Top %d features:\n%s", top_n, importances.head(top_n))
    return importances


def main():
    df = load_feature_table()
    train, test = chronological_split(df, SPLIT_DATE)

    X_train, y_train = split_xy(train, TARGET_COLUMN)
    X_test, y_test = split_xy(test, TARGET_COLUMN)

    model = train_model(X_train, y_train)
    evaluate(model, X_test, y_test)
    importances = feature_importance(model, X_train)

    model_path = MODELS_DIR / "ess_model.pkl"
    joblib.dump(model, model_path)
    log.info("Saved model -> %s", model_path)

    importances.to_csv(MODELS_DIR / "feature_importances.csv")

    return model


if __name__ == "__main__":
    main()