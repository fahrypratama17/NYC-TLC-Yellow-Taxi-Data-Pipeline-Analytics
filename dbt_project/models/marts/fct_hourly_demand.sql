{{ config(materialized='table') }}

-- Citywide hourly demand panel used by the forecasting model.
SELECT
    ts_hour,
    SUM(trips)                              AS trips,
    SUM(passengers)                         AS passengers,
    AVG(temperature_c)                      AS temperature_c,
    SUM(precipitation_mm)                   AS precipitation_mm,
    SUM(snowfall_cm)                        AS snowfall_cm,
    AVG(wind_speed_kmh)                     AS wind_speed_kmh,
    ANY_VALUE(weather_category)             AS weather_category,
    ANY_VALUE(pickup_hour)                  AS pickup_hour,
    ANY_VALUE(pickup_dow)                   AS pickup_dow,
    ANY_VALUE(is_weekend)                   AS is_weekend
FROM {{ ref('int_zone_hourly') }}
GROUP BY ts_hour
ORDER BY ts_hour
