{{ config(materialized='view') }}

WITH src AS (
    SELECT *
    FROM read_parquet('{{ var("silver_dir") }}/yellow_trips.parquet')
)
SELECT
    vendor_id,
    pu_location_id,
    do_location_id,
    rate_code_id,
    payment_type,
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    tip_amount,
    total_amount,
    trip_duration_min,
    avg_speed_mph,
    pickup_hour,
    pickup_dow,
    is_weekend,
    date_trunc('hour', tpep_pickup_datetime) AS pickup_hour_ts,
    date_trunc('day',  tpep_pickup_datetime) AS pickup_date
FROM src
