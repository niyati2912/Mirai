import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger("mirai.model")


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ess_dataset.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


TARGET = "ESS_target"

TEST_SIZE = 0.20

RANDOM_STATE = 42

MIN_TRAIN_ROWS = 20

MAX_SELECTED_FEATURES = 12


BEHAVIORAL_PREFIX = "trends_"


EXCLUDED_PREFIXES = (
    "ESS",
)


def load_data() -> pd.DataFrame:

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise RuntimeError(
            "ESS dataset is empty."
        )

    if "Date" not in df.columns:
        raise ValueError(
            "Date column not found."
        )

    if TARGET not in df.columns:
        raise ValueError(
            f"Target column '{TARGET}' not found."
        )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    df = (
        df
        .dropna(subset=["Date", TARGET])
        .sort_values("Date")
        .reset_index(drop=True)
    )

    log.info(
        "Loaded dataset: %d rows x %d columns",
        len(df),
        len(df.columns),
    )

    return df


def identify_features(
    df: pd.DataFrame,
) -> tuple[list[str], list[str]]:

    candidates = []

    for column in df.columns:

        if column in {
            "Date",
            "ESS",
            "ESS_target",
            "ESS_macro",
            "ESS_energy",
            "ESS_behavioral",
        }:
            continue

        if column.startswith(EXCLUDED_PREFIXES):
            continue

        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            continue

        candidates.append(column)

    conventional = [
        column
        for column in candidates
        if not column.startswith(
            BEHAVIORAL_PREFIX
        )
    ]

    behavioral = [
        column
        for column in candidates
        if column.startswith(
            BEHAVIORAL_PREFIX
        )
    ]

    if not conventional:
        raise RuntimeError(
            "No conventional predictors found."
        )

    if not behavioral:
        raise RuntimeError(
            "No behavioral predictors found."
        )

    log.info(
        "Conventional predictors: %d",
        len(conventional),
    )

    log.info(
        "Behavioral predictors: %d",
        len(behavioral),
    )

    return conventional, behavioral

def remove_bad_features(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:

    usable = []

    for column in features:

        train_values = pd.to_numeric(
            train[column],
            errors="coerce",
        )

        non_null_ratio = train_values.notna().mean()

        if non_null_ratio < 0.30:
            continue

        if train_values.nunique(
            dropna=True
        ) <= 1:
            continue

        usable.append(column)

    if not usable:
        raise RuntimeError(
            "No usable predictors remain after filtering."
        )

    log.info(
        "Removed %d unusable or sparse features.",
        len(features) - len(usable),
    )

    return (
        train[usable].copy(),
        test[usable].copy(),
        usable,
    )

def make_ridge_pipeline(
    n_features: int,
) -> Pipeline:

    k = min(
        MAX_SELECTED_FEATURES,
        n_features,
    )

    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "selector",
                SelectKBest(
                    score_func=f_regression,
                    k=k,
                ),
            ),
            (
                "model",
                Ridge(
                    alpha=10.0
                ),
            ),
        ]
    )


def make_rf_pipeline() -> Pipeline:

    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    max_depth=3,
                    min_samples_leaf=3,
                    max_features="sqrt",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def rmse(
    y_true,
    y_pred,
) -> float:

    return float(
        np.sqrt(
            mean_squared_error(
                y_true,
                y_pred,
            )
        )
    )


def evaluate(
    y_true,
    y_pred,
) -> dict:

    return {
        "MAE": float(
            mean_absolute_error(
                y_true,
                y_pred,
            )
        ),
        "RMSE": rmse(
            y_true,
            y_pred,
        ),
        "R2": float(
            r2_score(
                y_true,
                y_pred,
            )
        ),
    }


def walk_forward_score(
    pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> float:

    n_splits = min(
        4,
        len(X_train) // 6,
    )

    if n_splits < 2:
        return np.inf

    splitter = TimeSeriesSplit(
        n_splits=n_splits
    )

    scores = []

    for fold, (
        train_idx,
        validation_idx,
    ) in enumerate(
        splitter.split(X_train),
        start=1,
    ):

        X_tr = X_train.iloc[train_idx]
        X_val = X_train.iloc[validation_idx]

        y_tr = y_train.iloc[train_idx]
        y_val = y_train.iloc[validation_idx]

        model = pickle.loads(
            pickle.dumps(pipeline)
        )

        model.fit(
            X_tr,
            y_tr,
        )

        prediction = model.predict(
            X_val
        )

        fold_rmse = rmse(
            y_val,
            prediction,
        )

        scores.append(
            fold_rmse
        )

        log.info(
            "CV fold %d RMSE: %.4f",
            fold,
            fold_rmse,
        )

    return float(
        np.mean(scores)
    )


def get_selected_features(
    pipeline: Pipeline,
    feature_names: list[str],
) -> list[str]:

    selector = pipeline.named_steps.get(
        "selector"
    )

    if selector is None:
        return feature_names

    mask = selector.get_support()

    return [
        feature
        for feature, selected
        in zip(feature_names, mask)
        if selected
    ]


def save_feature_importance(
    model: Pipeline,
    feature_names: list[str],
    output_file: Path,
):

    rf = model.named_steps["model"]

    importance = rf.feature_importances_

    importance_df = (
        pd.DataFrame(
            {
                "feature": feature_names,
                "importance": importance,
            }
        )
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    importance_df.to_csv(
        output_file,
        index=False,
    )


def train_experiment(
    name: str,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
):

    log.info("=" * 70)
    log.info(
        "EXPERIMENT: %s",
        name,
    )
    log.info("=" * 70)

    X_train, X_test, features = (
        remove_bad_features(
            X_train,
            X_test,
            list(X_train.columns),
        )
    )

    log.info(
        "Usable features: %d",
        len(features),
    )

    ridge = make_ridge_pipeline(
        len(features)
    )

    rf = make_rf_pipeline()

    log.info(
        "Running walk-forward CV: Ridge"
    )

    ridge_cv = walk_forward_score(
        ridge,
        X_train,
        y_train,
    )

    log.info(
        "Ridge CV RMSE: %.4f",
        ridge_cv,
    )

    log.info(
        "Running walk-forward CV: Random Forest"
    )

    rf_cv = walk_forward_score(
        rf,
        X_train,
        y_train,
    )

    log.info(
        "Random Forest CV RMSE: %.4f",
        rf_cv,
    )

    if ridge_cv <= rf_cv:
        selected_name = "Ridge"
        selected_model = ridge
        selected_cv = ridge_cv
    else:
        selected_name = "RandomForest"
        selected_model = rf
        selected_cv = rf_cv

    log.info(
        "Selected model: %s",
        selected_name,
    )

    selected_model.fit(
        X_train,
        y_train,
    )

    prediction = selected_model.predict(
        X_test
    )

    metrics = evaluate(
        y_test,
        prediction,
    )

    metrics["CV_RMSE"] = selected_cv
    metrics["Model"] = selected_name
    metrics["Experiment"] = name
    metrics["Feature_Count"] = len(features)

    log.info(
        "Test MAE: %.4f",
        metrics["MAE"],
    )

    log.info(
        "Test RMSE: %.4f",
        metrics["RMSE"],
    )

    log.info(
        "Test R2: %.4f",
        metrics["R2"],
    )

    return (
        selected_model,
        selected_name,
        features,
        prediction,
        metrics,
    )


def main():

    log.info("=" * 70)
    log.info("MIRAI ECONOMIC STRESS FORECASTING")
    log.info("=" * 70)

    df = load_data()

    conventional, behavioral = (
        identify_features(df)
    )

    n_rows = len(df)

    test_rows = max(
        1,
        int(np.ceil(n_rows * TEST_SIZE)),
    )

    train_rows = n_rows - test_rows

    if train_rows < MIN_TRAIN_ROWS:
        raise RuntimeError(
            f"Only {train_rows} training rows available. "
            f"Need at least {MIN_TRAIN_ROWS}."
        )

    train_df = df.iloc[
        :train_rows
    ].copy()

    test_df = df.iloc[
        train_rows:
    ].copy()

    log.info(
        "Training period: %s -> %s",
        train_df["Date"].min(),
        train_df["Date"].max(),
    )

    log.info(
        "Test period: %s -> %s",
        test_df["Date"].min(),
        test_df["Date"].max(),
    )

    y_train = train_df[TARGET]
    y_test = test_df[TARGET]

    # ---------------------------------------------------------------
    # Experiment 1: Conventional indicators only
    # ---------------------------------------------------------------

    (
        conventional_model,
        conventional_model_name,
        conventional_features,
        conventional_prediction,
        conventional_metrics,
    ) = train_experiment(
        "conventional_only",
        train_df[conventional],
        test_df[conventional],
        y_train,
        y_test,
    )

    # ---------------------------------------------------------------
    # Experiment 2: Conventional + behavioral indicators
    # ---------------------------------------------------------------

    all_features = (
        conventional
        + behavioral
    )

    (
        full_model,
        full_model_name,
        full_features,
        full_prediction,
        full_metrics,
    ) = train_experiment(
        "conventional_plus_behavioral",
        train_df[all_features],
        test_df[all_features],
        y_train,
        y_test,
    )

    # ---------------------------------------------------------------
    # Persistence baseline
    #
    # Predict future ESS using current ESS.
    # ---------------------------------------------------------------

    persistence_prediction = (
        test_df["ESS"]
        .to_numpy()
    )

    persistence_metrics = evaluate(
        y_test,
        persistence_prediction,
    )

    persistence_metrics[
        "Model"
    ] = "Persistence"

    persistence_metrics[
        "Experiment"
    ] = "baseline"

    persistence_metrics[
        "Feature_Count"
    ] = 1

    log.info("=" * 70)
    log.info("PERSISTENCE BASELINE")
    log.info("=" * 70)

    log.info(
        "MAE: %.4f",
        persistence_metrics["MAE"],
    )

    log.info(
        "RMSE: %.4f",
        persistence_metrics["RMSE"],
    )

    log.info(
        "R2: %.4f",
        persistence_metrics["R2"],
    )

    # ---------------------------------------------------------------
    # Save predictions
    # ---------------------------------------------------------------

    predictions = pd.DataFrame(
        {
            "Date": test_df["Date"],
            "Actual_ESS_target": y_test,
            "Persistence": persistence_prediction,
            "Conventional": conventional_prediction,
            "Conventional_Behavioral": full_prediction,
        }
    )

    predictions.to_csv(
        OUTPUT_DIR
        / "model_predictions.csv",
        index=False,
    )

    # ---------------------------------------------------------------
    # Save metrics
    # ---------------------------------------------------------------

    metrics_df = pd.DataFrame(
        [
            persistence_metrics,
            conventional_metrics,
            full_metrics,
        ]
    )

    metrics_df.to_csv(
        OUTPUT_DIR
        / "model_metrics.csv",
        index=False,
    )

    # ---------------------------------------------------------------
    # Save selected feature lists
    # ---------------------------------------------------------------

    pd.DataFrame(
        {
            "feature": conventional_features
        }
    ).to_csv(
        OUTPUT_DIR
        / "selected_conventional_features.csv",
        index=False,
    )

    pd.DataFrame(
        {
            "feature": full_features
        }
    ).to_csv(
        OUTPUT_DIR
        / "selected_full_features.csv",
        index=False,
    )

    # ---------------------------------------------------------------
    # Save Random Forest importance when applicable
    # ---------------------------------------------------------------

    if full_model_name == "RandomForest":

        save_feature_importance(
            full_model,
            full_features,
            OUTPUT_DIR
            / "feature_importance.csv",
        )

    # ---------------------------------------------------------------
    # Save trained models
    # ---------------------------------------------------------------

    with open(
        MODEL_DIR
        / "mirai_conventional_model.pkl",
        "wb",
    ) as file:

        pickle.dump(
            conventional_model,
            file,
        )

    with open(
        MODEL_DIR
        / "mirai_full_model.pkl",
        "wb",
    ) as file:

        pickle.dump(
            full_model,
            file,
        )

    # ---------------------------------------------------------------
    # Behavioral contribution
    # ---------------------------------------------------------------

    conventional_rmse = (
        conventional_metrics["RMSE"]
    )

    full_rmse = (
        full_metrics["RMSE"]
    )

    if conventional_rmse != 0:

        improvement = (
            (
                conventional_rmse
                - full_rmse
            )
            / conventional_rmse
        ) * 100

    else:
        improvement = 0.0

    log.info("=" * 70)
    log.info("MIRAI MODEL COMPARISON")
    log.info("=" * 70)

    log.info(
        "Conventional RMSE: %.4f",
        conventional_rmse,
    )

    log.info(
        "Conventional + Behavioral RMSE: %.4f",
        full_rmse,
    )

    log.info(
        "Behavioral improvement: %.2f%%",
        improvement,
    )

    if improvement > 0:

        log.info(
            "Behavioral signals improved test RMSE."
        )

    else:

        log.info(
            "Behavioral signals did not improve test RMSE "
            "on this small holdout."
        )

    log.info("=" * 70)
    log.info("MODEL TRAINING COMPLETE")
    log.info("=" * 70)


if __name__ == "__main__":
    main()