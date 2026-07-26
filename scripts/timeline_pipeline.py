"""
Phase 2: Time Alignment

Converts every cleaned dataset to a monthly timeline,
merges them into one master dataset,
fills missing values,
and saves the final dataset.
"""
import logging
from pathlib import Path
import pandas as pd

log = logging.getLogger(__name__)


def resample_to_monthly(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Convert any dataset to monthly frequency.
    Daily data  -> last value of each month
    Monthly data -> unchanged
    Quarterly/Yearly -> expanded later using forward fill
    """
    if "Date" not in df.columns:
        log.warning("Skipping '%s' (no Date column)", name)
        return df
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = (
        df.set_index("Date")
            .sort_index()
            .resample("MS")
            .last()
            .reset_index()
    )
    return df


def merge_monthly_datasets(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge all monthly datasets."""
    merged = None
    for name, df in datasets.items():
        if "Date" not in df.columns:
            continue
        df = df.rename(columns={col: f"{name}_{col}" for col in df.columns if col != "Date"})
        merged = df if merged is None else pd.merge(merged, df, on="Date", how="outer")
    merged = merged.sort_values("Date").reset_index(drop=True)
    return merged


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values: forward-fill, then back-fill, then drop what's left."""
    df = df.sort_values("Date").reset_index(drop=True)
    df = df.ffill()
    df = df.bfill()
    df = df.dropna().reset_index(drop=True)
    return df


def build_master_dataset(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Complete Phase 2 pipeline: resample -> merge -> fill."""
    log.info("Resampling datasets to monthly frequency...")
    monthly = {name: resample_to_monthly(df, name) for name, df in datasets.items()}

    log.info("Merging datasets...")
    merged = merge_monthly_datasets(monthly)
    log.info("Merged shape: %s", merged.shape)

    log.info("Filling missing values...")
    merged = fill_missing_values(merged)
    log.info("Final shape: %s", merged.shape)
    log.info("Remaining missing values: %d", merged.isnull().sum().sum())

    return merged


def save_master_dataset(df: pd.DataFrame, processed_dir: Path) -> Path:
    output = processed_dir / "master_dataset.csv"
    df.to_csv(output, index=False)
    log.info("Saved master dataset -> %s", output)
    return output