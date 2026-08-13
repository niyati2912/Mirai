from __future__ import annotations

import argparse
import logging
import subprocess
import sys

import ess_builder
import feature as feature_mod
import merge as merge_mod

sys.path.insert(0, "etl")
from etl import pipeline as eia_pipeline  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] timeline: %(message)s")
logger = logging.getLogger("timeline_pipeline")


def run_eia_etl():
    logger.info("=== Step 1a: EIA ETL ===")
    try:
        eia_pipeline.run_pipeline()
    except Exception as exc:  # noqa: BLE001
        logger.error("EIA ETL failed: %s — continuing, merge.py will skip missing sources", exc)


def run_fred_etl():
    logger.info("=== Step 1b: FRED ETL ===")
    logger.warning(
        "run_fred_etl() is a stub — point this at your actual FRED pipeline entry point "
        "so it writes data/processed/fred_master_monthly.csv. Skipping for now."
    )
    # Example once wired up:
    # subprocess.run(["python", "fred_etl/pipeline.py"], check=True)


def run_merge():
    """Calls merge.py's core function directly (not main()) so it doesn't
    try to parse timeline_pipeline.py's own CLI args from sys.argv."""
    logger.info("=== Step 2: Merge ===")
    import os
    paths = merge_mod.auto_discover()
    master = merge_mod.merge_sources(paths)
    os.makedirs("data/processed", exist_ok=True)
    master.to_csv(merge_mod.DEFAULT_OUTPUT, index=False)
    logger.info("Master dataset written -> %s (%d rows, %d cols)", merge_mod.DEFAULT_OUTPUT, *master.shape)
    return master


def run_feature_engineering():
    logger.info("=== Step 3: Feature engineering ===")
    import pandas as pd
    df = pd.read_csv(merge_mod.DEFAULT_OUTPUT, parse_dates=["month"])
    featured = feature_mod.build_features(df)
    featured.to_csv(feature_mod.DEFAULT_OUTPUT, index=False)
    logger.info("Feature dataset written -> %s (%d rows, %d cols)", feature_mod.DEFAULT_OUTPUT, *featured.shape)
    return featured


def run_ess_build():
    logger.info("=== Step 4: ESS build ===")
    import pandas as pd
    df = pd.read_csv(feature_mod.DEFAULT_OUTPUT, parse_dates=["month"])
    ess_df = ess_builder.build_ess(df)
    ess_df.to_csv(ess_builder.DEFAULT_OUTPUT, index=False)
    logger.info("ESS timeline written -> %s (%d rows)", ess_builder.DEFAULT_OUTPUT, len(ess_df))
    return ess_df


def run_model_training():
    logger.info("=== Step 5: Model training ===")
    subprocess.run(["python", "train_model.py", "--mode", "reconstruct"], check=True)
    subprocess.run(["python", "train_model.py", "--mode", "forecast", "--horizon", "3"], check=True)


def main():
    parser = argparse.ArgumentParser(description="Run the full MIRAI timeline build")
    parser.add_argument("--skip-etl", action="store_true", help="Skip EIA/FRED extraction, reuse existing CSVs")
    parser.add_argument("--train", action="store_true", help="Also train reconstruct + forecast models at the end")
    args = parser.parse_args()

    if not args.skip_etl:
        run_eia_etl()
        run_fred_etl()
    else:
        logger.info("Skipping ETL steps (--skip-etl); reusing existing data/processed CSVs")

    run_merge()
    run_feature_engineering()
    run_ess_build()

    if args.train:
        run_model_training()

    logger.info("Timeline build complete. See data/processed/ess_timeline.csv")


if __name__ == "__main__":
    main()
