"""Entry point: run the full pipeline from raw CSVs to master_dataset.csv."""

import logging
from pathlib import Path

from etl import load_raw_datasets, clean_dataset, inspect, save_cleaned_datasets
from timeline_pipeline import build_master_dataset, save_master_dataset

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def main(debug: bool = False):
    log.info("Loading raw datasets...")
    datasets = load_raw_datasets(RAW_DIR)

    log.info("Cleaning datasets...")
    datasets = {name: clean_dataset(df) for name, df in datasets.items()}

    if debug:
        inspect(datasets)

    save_cleaned_datasets(datasets, PROCESSED_DIR)

    log.info("Building master dataset...")
    master = build_master_dataset(datasets)
    save_master_dataset(master, PROCESSED_DIR)

    log.info("Master dataset shape: %s", master.shape)
    log.info("Remaining missing values: %d", master.isnull().sum().sum())

    return master


if __name__ == "__main__":
    main(debug=True)