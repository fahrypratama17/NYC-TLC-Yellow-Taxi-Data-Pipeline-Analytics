"""Bronze → Silver cleaning driven by DuckDB SQL."""

from __future__ import annotations

from pathlib import Path

from nyc_tlc import config
from nyc_tlc.utils import get_duckdb, get_logger

log = get_logger(__name__)


_TRIPS_SQL = """
WITH src AS (
    SELECT
        CAST(VendorID AS INTEGER)                   AS vendor_id,
        CAST(PULocationID AS INTEGER)               AS pu_location_id,
        CAST(DOLocationID AS INTEGER)               AS do_location_id,
        CAST(RatecodeID AS INTEGER)                 AS rate_code_id,
        CAST(payment_type AS INTEGER)               AS payment_type,
        CAST(tpep_pickup_datetime AS TIMESTAMP)     AS tpep_pickup_datetime,
        CAST(tpep_dropoff_datetime AS TIMESTAMP)    AS tpep_dropoff_datetime,
        CAST(passenger_count AS INTEGER)            AS passenger_count,
        CAST(trip_distance AS DOUBLE)               AS trip_distance,
        CAST(fare_amount AS DOUBLE)                 AS fare_amount,
        CAST(tip_amount AS DOUBLE)                  AS tip_amount,
        CAST(total_amount AS DOUBLE)                AS total_amount
    FROM read_parquet('{bronze_glob}', union_by_name = true)
),
filtered AS (
    SELECT
        vendor_id,
        pu_location_id,
        do_location_id,
        rate_code_id,
        payment_type,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        -- Treat 0 as "driver did not enter" (TLC convention) — null it.
        CASE WHEN passenger_count BETWEEN 1 AND 9
             THEN passenger_count ELSE NULL END     AS passenger_count,
        trip_distance,
        fare_amount,
        tip_amount,
        total_amount
    FROM src
    WHERE tpep_pickup_datetime IS NOT NULL
      AND tpep_dropoff_datetime IS NOT NULL
      AND tpep_dropoff_datetime > tpep_pickup_datetime
      AND trip_distance > 0
      AND trip_distance < 200
      AND fare_amount >= 0
      AND fare_amount < 2000
      AND total_amount >= 0
      AND total_amount < 3000
      AND pu_location_id BETWEEN 1 AND 265
      AND do_location_id BETWEEN 1 AND 265
      AND date_part('year', tpep_pickup_datetime) IN ({years})
),
enriched AS (
    SELECT
        *,
        EXTRACT(EPOCH FROM tpep_dropoff_datetime - tpep_pickup_datetime) / 60.0
            AS trip_duration_min,
        EXTRACT(HOUR FROM tpep_pickup_datetime)     AS pickup_hour,
        EXTRACT(DOW  FROM tpep_pickup_datetime)     AS pickup_dow
    FROM filtered
),
priced AS (
    SELECT
        *,
        CASE WHEN trip_duration_min > 0
             THEN trip_distance / (trip_duration_min / 60.0)
             ELSE 0 END                             AS avg_speed_mph,
        CAST(pickup_dow IN (0, 6) AS BOOLEAN)       AS is_weekend
    FROM enriched
)
SELECT *
FROM priced
WHERE trip_duration_min > 0
  AND trip_duration_min <= 720
  AND avg_speed_mph <= 100
"""


_WEATHER_SQL = """
SELECT
    CAST(time AS TIMESTAMP)                  AS timestamp,
    CAST(temperature_2m AS DOUBLE)           AS temperature_c,
    CAST(precipitation AS DOUBLE)            AS precipitation_mm,
    CAST(snowfall AS DOUBLE)                 AS snowfall_cm,
    CAST(wind_speed_10m AS DOUBLE)           AS wind_speed_kmh,
    CAST(visibility AS DOUBLE)               AS visibility_m,
    CAST(weather_code AS INTEGER)            AS weather_code,
    CAST(cloud_cover AS DOUBLE)              AS cloud_cover_pct,
    CAST(apparent_temperature AS DOUBLE)     AS apparent_temp_c,
    CAST(rain AS DOUBLE)                     AS rain_mm,
    CAST(wind_gusts_10m AS DOUBLE)           AS wind_gust_kmh
FROM read_parquet('{path}')
"""


def _years_clause(months: list[str]) -> str:
    years = sorted({m.split("-")[0] for m in months})
    return ", ".join(years)


def clean_trips() -> Path:
    bronze_glob = str(config.BRONZE_DIR / "yellow_tripdata" / "*.parquet")
    out = config.SILVER_DIR / "yellow_trips.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)

    sql = _TRIPS_SQL.format(bronze_glob=bronze_glob, years=_years_clause(config.MONTHS))
    log.info("clean.trips.start", glob=bronze_glob)

    conn = get_duckdb()
    rows = conn.execute(f"SELECT count(*) FROM ({sql})").fetchone()
    log.info("clean.trips.rows", count=rows[0] if rows else 0)
    conn.execute(f"COPY ({sql}) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    conn.close()

    log.info("clean.trips.done", path=str(out))
    return out


def clean_weather() -> Path:
    src = config.BRONZE_DIR / "weather" / "weather_hourly.parquet"
    out = config.SILVER_DIR / "weather_hourly.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    sql = _WEATHER_SQL.format(path=src)

    log.info("clean.weather.start", src=str(src))
    conn = get_duckdb()
    conn.execute(f"COPY ({sql}) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    conn.close()

    log.info("clean.weather.done", path=str(out))
    return out


def run_clean() -> None:
    trips = clean_trips()
    weather = clean_weather()
    log.info("clean.done", trips=str(trips), weather=str(weather))


if __name__ == "__main__":
    run_clean()
