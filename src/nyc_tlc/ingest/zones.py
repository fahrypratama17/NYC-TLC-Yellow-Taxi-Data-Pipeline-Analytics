"""Download and unpack NYC taxi zone shapefile."""

from __future__ import annotations

import zipfile
from pathlib import Path

import requests

from nyc_tlc import config
from nyc_tlc.utils import get_logger

log = get_logger(__name__)


def _download_zip(url: str, dest: Path) -> None:
    log.info("zones.download", url=url)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 20):
            f.write(chunk)


def download_zones(overwrite: bool = False) -> Path:
    out_dir = config.BRONZE_DIR / "taxi_zones"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "taxi_zones.zip"

    shp = next(out_dir.glob("*.shp"), None)
    if shp is not None and not overwrite:
        log.info("zones.skip", shp=str(shp))
        return out_dir

    _download_zip(config.TLC_ZONES_URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)
    log.info("zones.done", out=str(out_dir))
    return out_dir
