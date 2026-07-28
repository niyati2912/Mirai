import logging
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
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
SPLIT_DATE = "2019-01-01"


def load_data():
    df = pd.read_csv(PROCESSED_DIR / "feature_table.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"{TARGET_COLUMN} not found.")

    return df


def split_data(df):
    train = df[df["Date"] < SPLIT_DATE].copy()
    test = df[df["Date"] >= SPLIT_DATE].copy()

    log.info(f"Training rows : {len(train)}")
    log.info(f"Testing rows  : {len(test)}")

    X_train = train.drop(columns=["Date", TARGET_COLUMN])
    y_train = train[TARGET_COLUMN]

    X_test = test.drop(columns=["Date", TARGET_COLUMN])
    y_test = test[TARGET_COLUMN]

    return X_train, X_test, y_train, y_test, test["Date"]


def train_model(X_train, y_train):
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=6,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    return model


def evaluate(model, X_test, y_test):

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    log.info(f"MAE  : {mae:.3f}")
    log.info(f"RMSE : {rmse:.3f}")
    log.info(f"R²   : {r2:.3f}")

    return predictions


def plot_predictions(dates, actual, predicted):

    plt.figure(figsize=(12,6))

    plt.plot(dates, actual, label="Actual ESS")
    plt.plot(dates, predicted, label="Predicted ESS")

    plt.xlabel("Date")
    plt.ylabel("Economic Stress Score")
    plt.title("ESS Prediction")

    plt.legend()

    plt.tight_layout()

    plt.savefig(MODELS_DIR / "ess_prediction_plot.png")


def feature_importance(model, feature_names):

    importance = (
        pd.DataFrame(
            {
                "Feature": feature_names,
                "Importance": model.feature_importances_,
            }
        )
        .sort_values("Importance", ascending=False)
    )

    print("\nTop 15 Features\n")
    print(importance.head(15))

    importance.to_csv(
        MODELS_DIR / "feature_importances.csv",
        index=False,
    )


def main():

    df = load_data()

    X_train, X_test, y_train, y_test, dates = split_data(df)

    model = train_model(X_train, y_train)

    predictions = evaluate(model, X_test, y_test)

    plot_predictions(
        dates,
        y_test,
        predictions,
    )

    feature_importance(
        model,
        X_train.columns,
    )

    joblib.dump(
        model,
        MODELS_DIR / "ess_model.pkl",
    )

    log.info("\nModel saved successfully.")


if __name__ == "__main__":
    main()