{{ config(materialized='table') }}

-- Join every trip with the weather observation matching its pickup hour.
SELECT
    t.*,
    w.temperature_c,
    w.apparent_temp_c,
    w.precipitation_mm,
    w.rain_mm,
    w.snowfall_cm,
    w.wind_speed_kmh,
    w.wind_gust_kmh,
    w.visibility_m,
    w.cloud_cover_pct,
    w.weather_code,
    w.weather_category
FROM {{ ref('stg_yellow_trips') }} t
LEFT JOIN {{ ref('stg_weather_hourly') }} w
       ON w.weather_ts = t.pickup_hour_ts
