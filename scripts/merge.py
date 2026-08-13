import logging
from pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger("mirai.merge")


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
FRED_DIR = RAW_DIR / "fred"
EIA_DIR = RAW_DIR / "eia"
TRENDS_DIR = RAW_DIR / "trends"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "master_dataset.csv"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================================
# DATASET CONFIGURATION
# ============================================================================

FRED_FILES = {
    "vix": "vix.csv",
    "yield_curve": "yield_curve.csv",
    "building_permits": "building_permits.csv",
    "unemployment_rate": "unemployment_rate.csv",
    "consumer_sentiment": "consumer_sentiment.csv",
    "industrial_production": "industrial_production.csv",
    "federal_funds_rate": "federal_funds_rate.csv",
    "cpi": "cpi.csv",
    "housing_starts": "housing_starts.csv",
    "retail_sales": "retail_sales.csv",
}


EIA_FILES = {
    "electricity_demand": "electricity_demand.csv",
    "electricity_generation": "electricity_generation.csv",
    "natural_gas_prices": "natural_gas_prices.csv",
    "petroleum_prices": "petroleum_prices.csv",
}


TRENDS_FILES = {
    "consumer_caution": "consumer_caution.csv",
    "economic_optimism": "economic_optimism.csv",
    "employment_stress": "employment_stress.csv",
    "financial_anxiety": "financial_anxiety.csv",
    "housing_stress": "housing_stress.csv",
    "inflation_fear": "inflation_fear.csv",
}


# ============================================================================
# DATE HANDLING
# ============================================================================

DATE_COLUMNS = (
    "Date",
    "date",
    "DATE",
    "time",
    "Time",
    "time [UTC]",
    "period",
)


def find_date_column(
    df: pd.DataFrame,
) -> str:

    for column in DATE_COLUMNS:

        if column in df.columns:
            return column

    # Fallback: look for columns containing date/time.
    for column in df.columns:

        name = str(column).lower()

        if (
            "date" in name
            or "time" in name
            or "period" in name
        ):
            return column

    raise ValueError(
        f"No date column found. Columns: {list(df.columns)}"
    )


def standardize_month(
    series: pd.Series,
) -> pd.Series:

    dates = pd.to_datetime(
        series,
        errors="coerce",
        utc=True,
    )

    # Remove timezone after parsing.
    dates = dates.dt.tz_localize(None)

    # Convert every observation to the first day of its month.
    return dates.dt.to_period("M").dt.to_timestamp()


# ============================================================================
# COLUMN HANDLING
# ============================================================================

def clean_column_name(
    column: str,
) -> str:

    column = str(column).strip()

    column = (
        column
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
    )

    return column


def make_unique_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:

    columns = []
    counts = {}

    for column in df.columns:

        column = clean_column_name(
            column
        )

        if column not in counts:

            counts[column] = 0
            columns.append(column)

        else:

            counts[column] += 1

            columns.append(
                f"{column}_{counts[column]}"
            )

    df.columns = columns

    return df


# ============================================================================
# DATASET PREPARATION
# ============================================================================

def prepare_dataframe(
    df: pd.DataFrame,
    source_name: str,
) -> pd.DataFrame:

    df = df.copy()

    df = make_unique_columns(df)

    date_column = find_date_column(df)

    df["Date"] = standardize_month(
        df[date_column]
    )

    if date_column != "Date":
        df = df.drop(
            columns=[date_column]
        )

    # Remove rows with invalid dates.
    df = df.dropna(
        subset=["Date"]
    )

    # Remove completely empty columns.
    df = df.dropna(
        axis=1,
        how="all",
    )

    # Convert non-date columns to numeric where possible.
    for column in df.columns:

        if column == "Date":
            continue

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Remove columns that contain no numeric data.
    value_columns = [
        column
        for column in df.columns
        if column != "Date"
        and df[column].notna().any()
    ]

    df = df[
        ["Date"] + value_columns
    ]

    # Aggregate duplicate monthly observations.
    if df["Date"].duplicated().any():

        duplicate_count = int(
            df["Date"].duplicated().sum()
        )

        log.warning(
            "%s contains %d duplicate monthly dates. "
            "Aggregating duplicates using mean.",
            source_name,
            duplicate_count,
        )

        df = (
            df
            .groupby(
                "Date",
                as_index=False,
            )
            .mean(
                numeric_only=True
            )
        )

    # Prefix every source column.
    renamed = {
        column: f"{source_name}_{column}"
        for column in df.columns
        if column != "Date"
    }

    df = df.rename(
        columns=renamed
    )

    df = (
        df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return df


# ============================================================================
# LOAD ONE DATASET
# ============================================================================

def load_dataset(
    directory: Path,
    filename: str,
    source_name: str,
) -> pd.DataFrame:

    path = directory / filename

    if not path.exists():

        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    log.info(
        "Loading %s",
        path,
    )

    df = pd.read_csv(
        path
    )

    result = prepare_dataframe(
        df,
        source_name,
    )

    log.info(
        "%s -> %d rows, %d columns",
        source_name,
        len(result),
        len(result.columns),
    )

    if len(result) > 0:

        log.info(
            "%s date range: %s -> %s",
            source_name,
            result["Date"].min(),
            result["Date"].max(),
        )

    return result


# ============================================================================
# LOAD ALL DATASETS
# ============================================================================

def load_all_datasets() -> list[pd.DataFrame]:

    datasets = []

    log.info("=" * 70)
    log.info("LOADING FRED DATASETS")
    log.info("=" * 70)

    for name, filename in FRED_FILES.items():

        datasets.append(
            load_dataset(
                FRED_DIR,
                filename,
                f"fred_{name}",
            )
        )

    log.info("=" * 70)
    log.info("LOADING EIA DATASETS")
    log.info("=" * 70)

    for name, filename in EIA_FILES.items():

        datasets.append(
            load_dataset(
                EIA_DIR,
                filename,
                f"eia_{name}",
            )
        )

    log.info("=" * 70)
    log.info("LOADING GOOGLE TRENDS DATASETS")
    log.info("=" * 70)

    for name, filename in TRENDS_FILES.items():

        datasets.append(
            load_dataset(
                TRENDS_DIR,
                filename,
                f"trends_{name}",
            )
        )

    return datasets


# ============================================================================
# CREATE COMPLETE MONTHLY TIMELINE
# ============================================================================

def create_monthly_spine(
    datasets: list[pd.DataFrame],
) -> pd.DataFrame:

    minimum_dates = []
    maximum_dates = []

    for df in datasets:

        if df.empty:
            continue

        minimum_dates.append(
            df["Date"].min()
        )

        maximum_dates.append(
            df["Date"].max()
        )

    if not minimum_dates:

        raise RuntimeError(
            "No valid datasets were loaded."
        )

    start_date = min(
        minimum_dates
    )

    end_date = max(
        maximum_dates
    )

    timeline = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS",
    )

    spine = pd.DataFrame(
        {
            "Date": timeline
        }
    )

    log.info(
        "Complete monthly timeline: %s -> %s",
        start_date,
        end_date,
    )

    log.info(
        "Timeline contains %d months.",
        len(spine),
    )

    return spine


# ============================================================================
# OUTER MERGE
# ============================================================================

def merge_datasets(
    datasets: list[pd.DataFrame],
) -> pd.DataFrame:

    master = create_monthly_spine(
        datasets
    )

    for dataset in datasets:

        master = master.merge(
            dataset,
            on="Date",
            how="left",
        )

    master = (
        master
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return master


# ============================================================================
# VALIDATION
# ============================================================================

def validate_master(
    df: pd.DataFrame,
) -> None:

    log.info("=" * 70)
    log.info("MASTER DATASET VALIDATION")
    log.info("=" * 70)

    if df.empty:

        raise RuntimeError(
            "Master dataset is empty."
        )

    if df["Date"].isna().any():

        raise RuntimeError(
            "Master dataset contains invalid dates."
        )

    if df["Date"].duplicated().any():

        raise RuntimeError(
            "Master dataset contains duplicate dates."
        )

    if not df["Date"].is_monotonic_increasing:

        raise RuntimeError(
            "Master dates are not sorted."
        )

    log.info(
        "Rows: %d",
        len(df),
    )

    log.info(
        "Columns: %d",
        len(df.columns),
    )

    log.info(
        "Date range: %s -> %s",
        df["Date"].min(),
        df["Date"].max(),
    )

    log.info(
        "Missing-value summary by source:"
    )

    for prefix in (
        "fred_",
        "eia_",
        "trends_",
    ):

        source_columns = [
            column
            for column in df.columns
            if column.startswith(prefix)
        ]

        if not source_columns:
            continue

        missing = int(
            df[source_columns]
            .isna()
            .sum()
            .sum()
        )

        total = (
            len(df)
            * len(source_columns)
        )

        percentage = (
            missing / total * 100
            if total
            else 0
        )

        log.info(
            "  %s -> %.2f%% missing",
            prefix.rstrip("_"),
            percentage,
        )

    # Specifically report the historical Trends gap.
    trends_columns = [
        column
        for column in df.columns
        if column.startswith("trends_")
    ]

    if trends_columns:

        trends_available = (
            df[trends_columns]
            .notna()
            .any(axis=1)
        )

        if trends_available.any():

            first_trends_date = (
                df.loc[
                    trends_available,
                    "Date",
                ].min()
            )

            log.info(
                "Google Trends coverage begins: %s",
                first_trends_date,
            )

            before_trends = df[
                df["Date"] < first_trends_date
            ]

            log.info(
                "Rows before Trends coverage: %d",
                len(before_trends),
            )


# ============================================================================
# MAIN
# ============================================================================

def main():

    log.info("=" * 70)
    log.info("MIRAI MASTER DATASET BUILDER")
    log.info("=" * 70)

    datasets = load_all_datasets()

    log.info("=" * 70)
    log.info("MERGING DATASETS")
    log.info("=" * 70)

    master = merge_datasets(
        datasets
    )

    log.info(
        "Merged dataset: %d rows x %d columns",
        len(master),
        len(master.columns),
    )

    validate_master(
        master
    )

    # Keep Date first.
    columns = [
        "Date"
    ] + [
        column
        for column in master.columns
        if column != "Date"
    ]

    master = master[
        columns
    ]

    master.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    log.info("=" * 70)
    log.info("MASTER DATASET CREATED")
    log.info("=" * 70)

    log.info(
        "Output: %s",
        OUTPUT_FILE,
    )

    log.info(
        "Shape: %d rows x %d columns",
        len(master),
        len(master.columns),
    )

    log.info(
        "Date range: %s -> %s",
        master["Date"].min(),
        master["Date"].max(),
    )

    log.info("=" * 70)


if __name__ == "__main__":
    main()