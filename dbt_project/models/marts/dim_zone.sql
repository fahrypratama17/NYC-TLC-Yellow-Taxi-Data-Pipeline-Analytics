{{ config(materialized='table') }}

-- Zone dimension. The shapefile lookup is handled in Python ML stage (geopandas);
-- here we just produce the canonical 1..265 list seen in trip data.
SELECT DISTINCT
    pu_location_id AS zone_id
FROM {{ ref('stg_yellow_trips') }}
UNION
SELECT DISTINCT do_location_id AS zone_id
FROM {{ ref('stg_yellow_trips') }}
