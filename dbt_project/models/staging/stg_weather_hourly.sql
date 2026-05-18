{{ config(materialized='view') }}

SELECT
    timestamp                                       AS weather_ts,
    temperature_c,
    apparent_temp_c,
    precipitation_mm,
    rain_mm,
    snowfall_cm,
    wind_speed_kmh,
    wind_gust_kmh,
    visibility_m,
    cloud_cover_pct,
    weather_code,
    -- Coarse weather category derived from WMO codes.
    CASE
        WHEN weather_code IN (0)                THEN 'clear'
        WHEN weather_code IN (1, 2, 3)          THEN 'cloudy'
        WHEN weather_code IN (45, 48)           THEN 'fog'
        WHEN weather_code BETWEEN 51 AND 67     THEN 'rain'
        WHEN weather_code BETWEEN 71 AND 77     THEN 'snow'
        WHEN weather_code BETWEEN 80 AND 82     THEN 'rain_showers'
        WHEN weather_code BETWEEN 85 AND 86     THEN 'snow_showers'
        WHEN weather_code BETWEEN 95 AND 99     THEN 'thunderstorm'
        ELSE 'other'
    END                                              AS weather_category
FROM read_parquet('{{ var("silver_dir") }}/weather_hourly.parquet')
