"""Open-Meteo Historical Weather API → bronze/weather/weather_hourly.parquet."""

from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests

from nyc_tlc import config
from nyc_tlc.utils import get_logger

log = get_logger(__name__)

_HOURLY_VARS = [
    "temperature_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "snowfall",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
    "visibility",
    "weather_code",
]


def _date_bounds(months: list[str]) -> tuple[date, date]:
    pairs = sorted(tuple(map(int, m.split("-"))) for m in months)
    y0, m0 = pairs[0]
    y1, m1 = pairs[-1]
    return date(y0, m0, 1), date(y1, m1, calendar.monthrange(y1, m1)[1])


def _fetch(start: date, end: date) -> dict:
    params = {
        "latitude": config.WEATHER_LAT,
        "longitude": config.WEATHER_LON,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "hourly": ",".join(_HOURLY_VARS),
        "timezone": config.WEATHER_TZ,
    }
    log.info("weather.fetch", start=str(start), end=str(end))
    r = requests.get(config.WEATHER_API_URL, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def download_weather(months: list[str], overwrite: bool = False) -> Path:
    out = config.BRONZE_DIR / "weather" / "weather_hourly.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not overwrite:
        log.info("weather.skip", path=str(out))
        return out

    start, end = _date_bounds(months)
    payload = _fetch(start, end)
    hourly = payload["hourly"]

    table = pa.table({k: hourly[k] for k in ["time", *_HOURLY_VARS]})
    pq.write_table(table, out, compression="zstd")
    log.info("weather.done", path=str(out), rows=table.num_rows)
    return out
