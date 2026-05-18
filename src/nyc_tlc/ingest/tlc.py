"""Download NYC TLC Yellow Taxi parquet files to bronze/yellow_tripdata/."""

from __future__ import annotations

from pathlib import Path

import requests

from nyc_tlc import config
from nyc_tlc.utils import get_logger

log = get_logger(__name__)


def _file_url(month: str) -> str:
    return f"{config.TLC_BASE_URL}/{config.TLC_TAXI_TYPE}_tripdata_{month}.parquet"


def _local_path(month: str) -> Path:
    out = config.BRONZE_DIR / "yellow_tripdata" / f"yellow_tripdata_{month}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def _download(url: str, dest: Path) -> None:
    log.info("download.start", url=url)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    log.info("download.done", dest=str(dest), bytes=dest.stat().st_size)


def download_tlc_months(months: list[str], overwrite: bool = False) -> list[Path]:
    paths: list[Path] = []
    for month in months:
        dest = _local_path(month)
        if dest.exists() and not overwrite:
            log.info("download.skip", path=str(dest))
            paths.append(dest)
            continue
        _download(_file_url(month), dest)
        paths.append(dest)
    return paths
