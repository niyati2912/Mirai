import logging
from pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger("mirai.feature")


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "master_dataset.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"

EXCLUDED_FEATURES = {
    "trends_consumer_caution_cheap groceries",
}


def create_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "Date" not in df.columns:
        raise ValueError("Date column not found.")

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date").reset_index(drop=True)

    base_columns = [
        col
        for col in df.columns
        if col != "Date"
        and pd.api.types.is_numeric_dtype(df[col])
        and col not in EXCLUDED_FEATURES
    ]

    log.info("Base features: %d", len(base_columns))

    # Remove unusable source columns
    df = df.drop(
        columns=list(EXCLUDED_FEATURES),
        errors="ignore",
    )

    engineered = {}

    for column in base_columns:

        series = df[column]

        engineered[f"{column}_pct_change"] = (
            series.pct_change()
        )

        engineered[f"{column}_lag1"] = (
            series.shift(1)
        )

        engineered[f"{column}_rolling3"] = (
            series.rolling(
                window=3,
                min_periods=3,
            ).mean()
        )

        engineered[f"{column}_rolling6"] = (
            series.rolling(
                window=6,
                min_periods=6,
            ).mean()
        )

        engineered[f"{column}_rolling3_std"] = (
            series.rolling(
                window=3,
                min_periods=3,
            ).std()
        )

    engineered_df = pd.DataFrame(
        engineered,
        index=df.index,
    )

    result = pd.concat(
        [df, engineered_df],
        axis=1,
    )

    log.info(
        "Created %d engineered features.",
        len(engineered_df.columns),
    )

    # The first 6 months cannot have complete 6-month
    # rolling features.
    result = result.iloc[6:].reset_index(drop=True)

    # Forward-fill only.
    #
    # Never back-fill because that would use future observations
    # to populate earlier dates.
    numeric_columns = result.select_dtypes(
        include="number"
    ).columns

    result[numeric_columns] = (
        result[numeric_columns]
        .ffill()
    )

    # Remove columns that still contain no usable information.
    all_nan_columns = [
        column
        for column in numeric_columns
        if result[column].isna().all()
    ]

    if all_nan_columns:

        log.warning(
            "Removing %d columns with no usable values.",
            len(all_nan_columns),
        )

        result = result.drop(
            columns=all_nan_columns
        )

    remaining_nan = int(
        result.select_dtypes(
            include="number"
        ).isna().sum().sum()
    )

    if remaining_nan:
        log.warning(
            "Remaining numeric NaN values: %d",
            remaining_nan,
        )
    else:
        log.info("No numeric NaN values remain.")

    return result


def main():

    log.info("=" * 70)
    log.info("MIRAI FEATURE ENGINEERING")
    log.info("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    log.info("Loading: %s", INPUT_FILE)

    df = pd.read_csv(INPUT_FILE)

    log.info(
        "Input shape: %d rows x %d columns",
        len(df),
        len(df.columns),
    )

    feature_table = create_features(df)

    feature_table.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    log.info("=" * 70)
    log.info("FEATURE TABLE CREATED")
    log.info("Output: %s", OUTPUT_FILE)
    log.info(
        "Shape: %d rows x %d columns",
        len(feature_table),
        len(feature_table.columns),
    )
    log.info(
        "Date range: %s -> %s",
        feature_table["Date"].min(),
        feature_table["Date"].max(),
    )
    log.info("=" * 70)


if __name__ == "__main__":
    main()