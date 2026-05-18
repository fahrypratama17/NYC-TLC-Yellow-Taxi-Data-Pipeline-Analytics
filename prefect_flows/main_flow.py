"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE

End-to-end Prefect flow:
  ingest → clean → dbt run → ml train
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from prefect import flow, task

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = PROJECT_ROOT / "dbt_project"


@task(retries=2, retry_delay_seconds=30, log_prints=True)
def ingest_task() -> None:
    from nyc_tlc.ingest.run import run_ingest

    run_ingest()


@task(log_prints=True)
def clean_task() -> None:
    from nyc_tlc.clean.run import run_clean

    run_clean()


@task(log_prints=True)
def dbt_run_task() -> None:
    subprocess.run(
        ["dbt", "run", "--profiles-dir", "."],
        cwd=DBT_DIR,
        check=True,
    )


@task(log_prints=True)
def ml_train_task() -> None:
    from nyc_tlc.ml.train import main as ml_main

    ml_main()


@flow(name="nyc-tlc-pipeline", log_prints=True)
def nyc_tlc_pipeline() -> None:
    """Full pipeline: ingest → clean → dbt → train ML."""
    ingest_task()
    clean_task()
    dbt_run_task()
    ml_train_task()


if __name__ == "__main__":
    nyc_tlc_pipeline()
