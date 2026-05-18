"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR     = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data")))
DUCKDB_PATH  = Path(os.getenv("DUCKDB_PATH", str(DATA_DIR / "warehouse.duckdb")))

TLC_MONTHS    = os.getenv("TLC_MONTHS", "2025-01,2025-02,2025-03,2025-04,2025-05,2025-06")
MONTHS        = [m.strip() for m in TLC_MONTHS.split(",") if m.strip()]
TLC_BASE_URL  = "https://d37ci6vzurychx.cloudfront.net/trip-data"
TLC_ZONES_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
TLC_TAXI_TYPE = "yellow"

WEATHER_LAT     = 40.7580
WEATHER_LON     = -73.9855
WEATHER_TZ      = "America/New_York"
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"

BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
MARTS_DIR  = DATA_DIR / "marts"
