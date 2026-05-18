{{ config(materialized='table') }}

-- Origin → Destination flow aggregates. Used by the Pydeck arc layer.
SELECT
    pu_location_id   AS origin_zone_id,
    do_location_id   AS destination_zone_id,
    COUNT(*)         AS trips,
    AVG(trip_distance)     AS avg_distance,
    AVG(trip_duration_min) AS avg_duration_min,
    AVG(total_amount)      AS avg_total
FROM {{ ref('stg_yellow_trips') }}
GROUP BY 1, 2
HAVING COUNT(*) >= 50
