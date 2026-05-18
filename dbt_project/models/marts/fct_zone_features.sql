{{ config(materialized='table') }}

-- Per-zone feature vector used as input to clustering.
-- Each zone gets a single row summarising its overall behaviour
-- and time-of-day / weather sensitivities.
WITH base AS (
    SELECT
        zone_id,
        SUM(trips)                              AS total_trips,
        SUM(passengers)                         AS total_passengers,
        AVG(avg_distance)                       AS avg_distance,
        AVG(avg_duration_min)                   AS avg_duration_min,
        AVG(avg_speed_mph)                      AS avg_speed_mph,
        AVG(avg_fare)                           AS avg_fare,
        AVG(avg_tip)                            AS avg_tip,
        AVG(avg_tip_ratio)                      AS avg_tip_ratio,
        AVG(avg_total)                          AS avg_total
    FROM {{ ref('int_zone_hourly') }}
    GROUP BY 1
),
time_profile AS (
    SELECT
        zone_id,
        SUM(CASE WHEN pickup_hour BETWEEN 0  AND 5  THEN trips ELSE 0 END) * 1.0
            / NULLIF(SUM(trips), 0)               AS share_late_night,
        SUM(CASE WHEN pickup_hour BETWEEN 6  AND 9  THEN trips ELSE 0 END) * 1.0
            / NULLIF(SUM(trips), 0)               AS share_morning_rush,
        SUM(CASE WHEN pickup_hour BETWEEN 10 AND 15 THEN trips ELSE 0 END) * 1.0
            / NULLIF(SUM(trips), 0)               AS share_midday,
        SUM(CASE WHEN pickup_hour BETWEEN 16 AND 19 THEN trips ELSE 0 END) * 1.0
            / NULLIF(SUM(trips), 0)               AS share_evening_rush,
        SUM(CASE WHEN pickup_hour BETWEEN 20 AND 23 THEN trips ELSE 0 END) * 1.0
            / NULLIF(SUM(trips), 0)               AS share_evening,
        SUM(CASE WHEN is_weekend THEN trips ELSE 0 END) * 1.0
            / NULLIF(SUM(trips), 0)               AS share_weekend
    FROM {{ ref('int_zone_hourly') }}
    GROUP BY 1
),
weather_sensitivity AS (
    SELECT
        zone_id,
        AVG(CASE WHEN precipitation_mm > 1 THEN trips END) /
            NULLIF(AVG(CASE WHEN precipitation_mm <= 1 THEN trips END), 0)
                                                  AS rain_demand_ratio,
        AVG(CASE WHEN snowfall_cm > 0.1 THEN trips END) /
            NULLIF(AVG(CASE WHEN snowfall_cm <= 0.1 THEN trips END), 0)
                                                  AS snow_demand_ratio
    FROM {{ ref('int_zone_hourly') }}
    GROUP BY 1
)
SELECT
    b.*,
    t.share_late_night,
    t.share_morning_rush,
    t.share_midday,
    t.share_evening_rush,
    t.share_evening,
    t.share_weekend,
    w.rain_demand_ratio,
    w.snow_demand_ratio
FROM base b
LEFT JOIN time_profile        t USING (zone_id)
LEFT JOIN weather_sensitivity w USING (zone_id)
