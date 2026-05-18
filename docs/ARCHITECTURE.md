# Architecture deep-dive

## Medallion lakehouse

The Bronze and Silver layers are **files on disk** (a data lake); the Gold and
Marts layers are **tables inside the DuckDB warehouse** (`data/warehouse.duckdb`).
Raw and cleaned data stays as portable Parquet; modelled data lives in the query
engine.

```
data/
├── bronze/                         # raw, append-only (data lake)
│   ├── yellow_tripdata/*.parquet   # one file per month, untouched
│   ├── weather/weather_hourly.parquet
│   └── taxi_zones/                 # NYC OpenData shapefile
├── silver/                         # cleaned, derived columns
│   ├── yellow_trips.parquet
│   └── weather_hourly.parquet
├── marts/                          # ML outputs (parquet)
│   ├── zone_clusters.parquet
│   └── zone_cluster_profiles.parquet
└── warehouse.duckdb                # DuckDB warehouse — holds intermediate
                                    # and mart tables (dim_/fct_)
```

The dbt models — `dim_zone`, `fct_zone_features`, `fct_hourly_demand`,
`fct_flow_od`, and the intermediate joins — are materialised as tables inside
`warehouse.duckdb`. The ML stage additionally writes its outputs to
`data/marts/` as Parquet so the dashboard can read them without the warehouse.

## Stage-by-stage detail

### 1. Ingestion (`src/nyc_tlc/ingest/`)

- `tlc.py` — streams Yellow Taxi parquet from CloudFront, one file per
  YYYY-MM. Skips files that already exist on disk (idempotent).
- `weather.py` — fetches Open-Meteo Historical Weather API for NYC midtown
  (latitude 40.758, longitude −73.986) covering the full date range. Hourly
  variables: temperature, apparent temperature, precipitation, rain, snowfall,
  cloud cover, wind speed/gusts, visibility, weather_code. Free, no API key.
- `zones.py` — pulls the NYC TLC taxi-zone shapefile.

### 2. Cleaning (`src/nyc_tlc/clean/`)

DuckDB SQL does the heavy lifting (column casting + filtering) and writes the
result back to Parquet.

Anomalies handled:
- NULL pickup or dropoff timestamps.
- Dropoff at or before pickup.
- Zero or negative trip distance.
- Trip distance > 200 miles (impossible inside NYC).
- Negative fare or total amount.
- Out-of-range LocationID (must be 1–265).
- Trip duration ≤ 0 or > 12 hours.
- Average speed > 100 mph (GPS/clock anomaly).

Derived columns: `trip_duration_min`, `avg_speed_mph`, `pickup_hour`,
`pickup_dow`, `is_weekend`, plus `pickup_hour_ts` and `pickup_date`
truncations added in the staging layer.

### 3. Transformation (`dbt_project/`)

Layered dbt models with on-disk Parquet sources:

- `stg_*` — light SQL views over silver Parquet.
- `int_trips_with_weather` — every trip joined to the matching weather hour.
- `int_zone_hourly` — pickup-zone × hour aggregate.
- `marts/dim_zone` — canonical 1–265 zone list.
- `marts/fct_zone_features` — per-zone vector used as clustering input,
  including time-of-day shares and rain/snow demand ratios.
- `marts/fct_hourly_demand` — citywide hourly panel.
- `marts/fct_flow_od` — origin→destination flow aggregates for the Pydeck arc
  layer.

### 4. Machine learning (`src/nyc_tlc/ml/`)

**Clustering**

- Input: `fct_zone_features` (one row per zone).
- `total_trips` log1p-transformed before standardisation — raw counts are
  heavily right-skewed and would dominate Euclidean distance.
- Standard-scaled, then evaluated under two algorithm families:
  - **K-Means** sweep over k ∈ [3, 10].
  - **Gaussian Mixture** sweep over k ∈ [3, 10].
- Winner picked by **silhouette score**; Davies–Bouldin and
  Calinski–Harabasz also computed for cross-checking.
- Cluster names derived automatically: for each cluster, the feature with the
  highest positive z-score deviation from the citywide mean is mapped to a
  fixed archetype name (e.g. high `avg_distance` → "Airport & Long-Haul
  Gateway"). See `src/nyc_tlc/ml/profiles.py`.
- Results persisted to `data/marts/zone_clusters.parquet` and
  `data/marts/zone_cluster_profiles.parquet`.

### 5. Orchestration (`prefect_flows/`)

Prefect 3 flow `nyc_tlc_pipeline` chains:
ingest → clean → dbt run → ml train.

Run it with `make flow`.

### 6. Dashboard (`src/nyc_tlc/dashboard/`)

Streamlit multi-page app:

- **Home** — KPIs + daily demand timeline + weekly rhythm heatmap.
- **Geospatial** — Folium choropleth (zones coloured by cluster archetype,
  pickup volume, or fare) + Pydeck 3D extruded GeoJSON layer + top OD
  corridors bar chart.
- **Weather Impact** — average demand by weather category and temperature band.
- **ML Insights** — zone segment summary table + per-archetype descriptions
  and fleet recommendations + σ-deviation evidence chart.

## Operational notes

- **Idempotency** — every stage skips work if outputs already exist, so
  re-runs are safe.
- **Backfill** — change `TLC_MONTHS` in `.env` and re-run `make ingest` to
  add or replace months.
- **Reproducibility** — `uv.lock` pins every dependency.
