"""Orchestrate all three bronze ingest steps in one call."""

from __future__ import annotations

from nyc_tlc import config
from nyc_tlc.ingest.tlc import download_tlc_months
from nyc_tlc.ingest.weather import download_weather
from nyc_tlc.ingest.zones import download_zones
from nyc_tlc.utils import get_logger

log = get_logger(__name__)


def run_ingest(months_override: str | None = None, overwrite: bool = False) -> None:
    months = [m.strip() for m in months_override.split(",")] if months_override else config.MONTHS
    log.info("ingest.start", months=months)

    tlc_paths = download_tlc_months(months, overwrite=overwrite)
    weather_path = download_weather(months, overwrite=overwrite)
    zones_dir = download_zones(overwrite=overwrite)

    log.info(
        "ingest.done",
        tlc_files=len(tlc_paths),
        weather=str(weather_path),
        zones=str(zones_dir),
    )


def main() -> None:
    run_ingest()


if __name__ == "__main__":
    main()
