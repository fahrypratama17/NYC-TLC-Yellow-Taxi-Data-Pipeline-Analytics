{{ config(materialized='table') }}

-- Hourly aggregate per pickup zone, joined to weather.
SELECT
    pu_location_id                                   AS zone_id,
    pickup_hour_ts                                   AS ts_hour,
    pickup_hour,
    pickup_dow,
    is_weekend,
    COUNT(*)                                         AS trips,
    SUM(passenger_count)                             AS passengers,
    AVG(trip_distance)                               AS avg_distance,
    AVG(trip_duration_min)                           AS avg_duration_min,
    AVG(avg_speed_mph)                               AS avg_speed_mph,
    AVG(fare_amount)                                 AS avg_fare,
    AVG(tip_amount)                                  AS avg_tip,
    AVG(total_amount)                                AS avg_total,
    AVG(NULLIF(tip_amount, 0) / NULLIF(fare_amount, 0))
                                                     AS avg_tip_ratio,
    ANY_VALUE(temperature_c)                         AS temperature_c,
    ANY_VALUE(precipitation_mm)                      AS precipitation_mm,
    ANY_VALUE(snowfall_cm)                           AS snowfall_cm,
    ANY_VALUE(wind_speed_kmh)                        AS wind_speed_kmh,
    ANY_VALUE(weather_category)                      AS weather_category
FROM {{ ref('int_trips_with_weather') }}
GROUP BY 1, 2, 3, 4, 5
