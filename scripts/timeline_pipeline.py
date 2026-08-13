from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("mirai.timeline")


def run_script(script: Path, *args: str) -> None:
    """Run another MIRAI script using the current Python environment."""

    logger.info("Running: %s %s", script.name, " ".join(args))

    command = [
        sys.executable,
        str(script),
        *args,
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{script.name} failed with exit code {result.returncode}"
        )


def run_etl() -> None:
    """Run all available external-data ingestion pipelines."""

    logger.info("=" * 70)
    logger.info("STEP 1: DATA INGESTION")
    logger.info("=" * 70)

    etl_dir = SCRIPTS_DIR / "etl"

    etl_scripts = [
        etl_dir / "fred.py",
        etl_dir / "eia_etl.py",
        etl_dir / "trends.py",
        etl_dir / "github_etl.py",
    ]

    for script in etl_scripts:

        if not script.exists():
            raise FileNotFoundError(
                f"ETL script not found: {script}"
            )

        run_script(script)


def run_merge() -> None:
    """Merge raw datasets into the master monthly dataset."""

    logger.info("=" * 70)
    logger.info("STEP 2: DATA MERGING")
    logger.info("=" * 70)

    run_script(
        SCRIPTS_DIR / "merge.py"
    )


def run_features() -> None:
    """Create engineered features from the master dataset."""

    logger.info("=" * 70)
    logger.info("STEP 3: FEATURE ENGINEERING")
    logger.info("=" * 70)

    run_script(
        SCRIPTS_DIR / "feature.py"
    )


def run_ess() -> None:
    """Build the Economic Stress Score."""

    logger.info("=" * 70)
    logger.info("STEP 4: ECONOMIC STRESS SCORE")
    logger.info("=" * 70)

    ess_script = SCRIPTS_DIR / "ess_builder.py"

    if not ess_script.exists():

        # Current repository contains ess_builer.py.
        # This fallback keeps the pipeline working until the filename
        # is corrected.
        old_script = SCRIPTS_DIR / "ess_builer.py"

        if old_script.exists():
            ess_script = old_script
        else:
            raise FileNotFoundError(
                "ESS builder not found. Expected ess_builder.py."
            )

    run_script(ess_script)


def run_training() -> None:
    """Train the ESS forecasting model."""

    logger.info("=" * 70)
    logger.info("STEP 5: MODEL TRAINING")
    logger.info("=" * 70)

    run_script(
        SCRIPTS_DIR / "train_model.py",
        "--mode",
        "forecast",
        "--horizon",
        "3",
    )


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Run the MIRAI economic intelligence pipeline."
    )

    parser.add_argument(
        "--skip-etl",
        action="store_true",
        help="Reuse existing raw datasets.",
    )

    parser.add_argument(
        "--train",
        action="store_true",
        help="Train the ESS forecasting model after processing.",
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("MIRAI ECONOMIC INTELLIGENCE PIPELINE")
    logger.info("=" * 70)

    try:

        if not args.skip_etl:
            run_etl()
        else:
            logger.info("Skipping ETL.")

        run_merge()
        run_features()
        run_ess()

        if args.train:
            run_training()

        logger.info("=" * 70)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)

    except Exception as exc:

        logger.error("=" * 70)
        logger.error("PIPELINE FAILED")
        logger.error("%s", exc)
        logger.error("=" * 70)

        raise SystemExit(1)


if __name__ == "__main__":
    main()