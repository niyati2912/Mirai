from __future__ import annotations

import argparse
import glob
import logging
import os
from typing import List, Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] merge: %(message)s")
logger = logging.getLogger("merge")

# Known monthly source datasets. Add your FRED output path here.
SOURCE_FILES = [
    "data/processed/eia_master_monthly.csv",   # produced by etl/pipeline.py
    "data/processed/fred_master_monthly.csv",  # <- point this at your FRED ETL output
]

# Candidate column names that represent the month/date key across sources.
DATE_COL_CANDIDATES = ["month", "date", "period", "DATE", "Month"]

DEFAULT_OUTPUT = "data/processed/master_dataset.csv"


def _find_date_col(df: pd.DataFrame) -> Optional[str]:
    for cand in DATE_COL_CANDIDATES:
        if cand in df.columns:
            return cand
    return None


def load_source(path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        logger.warning("Source not found, skipping: %s", path)
        return None

    df = pd.read_csv(path)
    date_col = _find_date_col(df)
    if date_col is None:
        logger.warning("No date-like column found in %s (looked for %s), skipping",
                        path, DATE_COL_CANDIDATES)
        return None

    df = df.rename(columns={date_col: "month"})
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df = df.dropna(subset=["month"])
    # Normalize to first-of-month so sources at different granularities align.
    df["month"] = df["month"].values.astype("datetime64[M]")

    source_tag = os.path.splitext(os.path.basename(path))[0]
    logger.info("Loaded %s: %d rows, %d columns (%s)", path, len(df), df.shape[1], source_tag)
    return df


def auto_discover(root: str = "data/processed") -> List[str]:
    return sorted(glob.glob(os.path.join(root, "*_monthly.csv")))


def merge_sources(paths: List[str]) -> pd.DataFrame:
    master: Optional[pd.DataFrame] = None
    for path in paths:
        df = load_source(path)
        if df is None:
            continue
        # De-duplicate any repeated month rows within a single source before merging.
        df = df.drop_duplicates(subset=["month"])
        master = df if master is None else master.merge(df, on="month", how="outer", suffixes=("", "_dup"))

    if master is None:
        raise RuntimeError("No valid source files were merged — check SOURCE_FILES / --auto paths.")

    # Drop accidental duplicate columns created by overlapping merges.
    dup_cols = [c for c in master.columns if c.endswith("_dup")]
    if dup_cols:
        logger.warning("Dropping duplicate columns from overlapping sources: %s", dup_cols)
        master = master.drop(columns=dup_cols)

    master = master.sort_values("month").reset_index(drop=True)
    return master


def main():
    parser = argparse.ArgumentParser(description="Merge processed monthly datasets into one master file")
    parser.add_argument("--auto", action="store_true", help="Auto-discover *_monthly.csv in data/processed/")
    parser.add_argument("--out", default=DEFAULT_OUTPUT, help="Output path for merged master dataset")
    parser.add_argument("--source", action="append", dest="sources", help="Add an extra source CSV path")
    args = parser.parse_args()

    paths = auto_discover() if args.auto else list(SOURCE_FILES)
    if args.sources:
        paths.extend(args.sources)

    master = merge_sources(paths)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    master.to_csv(args.out, index=False)
    logger.info("Master dataset written -> %s (%d rows, %d cols)", args.out, *master.shape)
    return master


if __name__ == "__main__":
    main()
