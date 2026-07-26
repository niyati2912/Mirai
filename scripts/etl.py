"""
ETL pipeline: loads raw CSVs, standardizes columns, cleans types,
merges everything into one feature table, and saves it to processed/.
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def load_raw_datasets(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Load every CSV in raw_dir into a dict keyed by filename (no extension)."""
    datasets = {}
    for file in raw_dir.glob("*.csv"):
        datasets[file.stem] = pd.read_csv(file)
    log.info("Loaded %d raw datasets: %s", len(datasets), list(datasets.keys()))
    return datasets


def standardize_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Rename whatever the date column is called to 'Date'."""
    rename_map = {"Unnamed: 0": "Date", "date": "Date"}
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df


def clean_yahoo_format(df: pd.DataFrame) -> pd.DataFrame:
    """yfinance CSVs have a junk 2-row header and use 'Price' for the date column."""
    if "Price" in df.columns:
        df = df.rename(columns={"Price": "Date"})
        df = df.iloc[2:].reset_index(drop=True)
    return df


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Date to datetime, drop invalid dates, sort chronologically,
    and convert everything else to numeric."""
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

    for col in df.columns:
        if col != "Date":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline for a single dataset."""
    df = standardize_date_column(df)
    df = clean_yahoo_format(df)
    df = convert_types(df)
    return df


def inspect(datasets: dict[str, pd.DataFrame]) -> None:
    """Print shape/dtypes/missing-value/date-range summary for each dataset. Debug use only."""
    for name, df in datasets.items():
        log.info("=" * 60)
        log.info(name.upper())
        log.info("shape=%s", df.shape)
        log.info("columns=%s", df.columns.tolist())
        log.info("missing=\n%s", df.isnull().sum())
        if "Date" in df.columns:
            log.info(
                "Date Range: %s -> %s",
                df["Date"].min(),
                df["Date"].max(),
            )


def save_cleaned_datasets(datasets: dict[str, pd.DataFrame]) -> None:
    """Save each cleaned dataset to processed/ as its own CSV."""
    for name, df in datasets.items():
        df.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
    log.info("Saved %d cleaned datasets.", len(datasets))


def merge_datasets(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Outer-merge every dataset on Date into one wide feature table."""
    merged = None
    for name, df in datasets.items():
        if "Date" not in df.columns:
            log.warning("Skipping '%s' — no Date column after cleaning", name)
            continue
        # prefix non-date columns so overlapping names (e.g. 'Close') don't collide
        df = df.rename(columns={c: f"{name}_{c}" for c in df.columns if c != "Date"})
        merged = df if merged is None else pd.merge(merged, df, on="Date", how="outer")
    return merged.sort_values("Date").reset_index(drop=True)


def main(debug: bool = False) -> pd.DataFrame:
    datasets = load_raw_datasets(RAW_DIR)
    datasets = {name: clean_dataset(df) for name, df in datasets.items()}

    if debug:
        inspect(datasets)

    # Save every cleaned dataset (runs every time, not just in debug mode)
    save_cleaned_datasets(datasets)

    feature_table = merge_datasets(datasets)
    out_path = PROCESSED_DIR / "feature_table.csv"
    feature_table.to_csv(out_path, index=False)
    log.info("Saved merged feature table to %s — shape=%s", out_path, feature_table.shape)
    return feature_table


if __name__ == "__main__":
    main(debug=True)