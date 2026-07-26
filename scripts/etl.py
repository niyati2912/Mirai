"""ETL: load raw CSVs, clean and standardize them, save cleaned versions."""

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)


def load_raw_datasets(raw_dir: Path) -> dict[str, pd.DataFrame]:
    datasets = {file.stem: pd.read_csv(file) for file in raw_dir.glob("*.csv")}
    log.info("Loaded %d datasets.", len(datasets))
    return datasets


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"Unnamed: 0": "Date", "date": "Date"})

    if "Price" in df.columns:
        df = df.rename(columns={"Price": "Date"}).iloc[2:].reset_index(drop=True)

    if "Date" not in df.columns:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    for col in df.columns:
        if col != "Date":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def inspect(datasets: dict[str, pd.DataFrame]) -> None:
    for name, df in datasets.items():
        log.info("=" * 60)
        log.info(name.upper())
        log.info("Shape: %s", df.shape)
        log.info("Columns: %s", df.columns.tolist())
        log.info("Missing values:\n%s", df.isnull().sum())
        if "Date" in df.columns:
            log.info("Date range: %s -> %s", df["Date"].min(), df["Date"].max())


def save_cleaned_datasets(datasets: dict[str, pd.DataFrame], processed_dir: Path) -> None:
    for name, df in datasets.items():
        df.to_csv(processed_dir / f"{name}.csv", index=False)
    log.info("Saved %d cleaned datasets.", len(datasets))