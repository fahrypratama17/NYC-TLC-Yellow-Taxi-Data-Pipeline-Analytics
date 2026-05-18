# NYC TLC Yellow Taxi — Data Pipeline & Analytics

> End-to-end data pipeline and interactive dashboard for the NYC Taxi & Limousine
> Commission (TLC) Yellow Taxi dataset, enriched with Open-Meteo historical weather
> and zone clustering.
>
> **Course:** Rekayasa Data dan Visualisasi (RDV) — Final Project
> **Class:** TIF-A
> **Year:** 2026

---

## Team

```
245150201111042  ANINDHITA FAIZA AULIA
245150201111043  ANIZA HELWA MAHANANI
245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
245150201111002  MUHAMMAD ATHA TSAQIF
245150200111008  NAFIS NAUFAL RAHMAN
245150200111061  RICHARD SAMUEL HATANE
```

| Role | Member |
| --- | --- |
| Data Architect / Project Lead | NAFIS NAUFAL RAHMAN |
| Data Engineer (ingestion) | MUHAMAD FAHRY PRATAMA PUTRA |
| Data Engineer (cleaning + dbt) | MUHAMMAD ATHA TSAQIF |
| ML Engineer (clustering) | ANIZA HELWA MAHANANI |
| Data Analyst (dashboard + maps) | RICHARD SAMUEL HATANE |
| Data Analyst (analysis + report) | ANINDHITA FAIZA AULIA |

---

## Problem statement

> **Where, when, and under which weather conditions is NYC yellow-taxi demand
> highest — and what does that mean for zone-level operations?**

We answer three concrete questions:

1. **Where?** Cluster the 263 NYC taxi zones into operational profiles
   (commuter, nightlife, airport, weather-sensitive, …) based on trip behaviour.
2. **When?** Quantify how hour-of-day, day-of-week, and weather change demand.
3. **What patterns?** Surface actionable insights per zone segment via a multi-page dashboard.

---

## Architecture

```
External sources
  NYC TLC Yellow parquet  →  Bronze (raw parquet)
  Open-Meteo hourly weather →  Bronze (raw parquet)
  NYC taxi zones shapefile  →  Bronze (shapefile)

Bronze → Silver  (Python: clean/run.py)
  Filters bad trips, casts types, derives speed/duration columns

Silver → Marts  (dbt-duckdb)
  stg_yellow_trips + stg_weather_hourly
    → int_trips_with_weather → int_zone_hourly
    → fct_zone_features  (per-zone feature vector)
    → fct_hourly_demand  (citywide hourly panel)
    → fct_flow_od        (OD corridors)

Marts → ML  (Python: ml/clustering.py)
  K-Means vs GMM, winner by silhouette score
  → zone_clusters.parquet + zone_cluster_profiles.parquet

Marts + ML output → Dashboard  (Streamlit + Folium + Pydeck)
  Page 1: Geospatial   — choropleth + 3D demand map + corridors
  Page 2: Weather Impact — demand by condition and temperature
  Page 3: ML Insights   — zone segments with archetype descriptions

Orchestration: Prefect 3 (prefect_flows/main_flow.py)
```

---

## Tech stack

| Layer | Tool |
| --- | --- |
| Orchestration | **Prefect 3** |
| Storage | **DuckDB + Parquet (medallion)** |
| Transformation | **dbt-duckdb** |
| Geospatial | **GeoPandas · Folium · Pydeck** |
| ML | **scikit-learn** (K-Means, GMM) |
| Dashboard | **Streamlit + Plotly** |
| Packaging | **uv + pyproject.toml** |

---

## Prerequisites

| Tool | Version | Install |
| --- | --- | --- |
| **Python** | 3.11 | `uv python install 3.11` |
| **uv** | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **make** | any | preinstalled on macOS/Linux |

---

## Quickstart

```bash
# 1. Install dependencies
make install

# 2. Run the full pipeline
make ingest       # download TLC + weather + zones (~5–15 min, ~3 GB)
make clean        # bronze → silver
make dbt-run      # silver → marts
make train        # zone clustering (K-Means vs GMM)

# 3. Launch the dashboard
make dashboard    # opens http://localhost:8501

# Or run the entire pipeline in one step via Prefect:
make flow
```

---

## Repository layout

```
nyc-tlc-data-pipeline/
├── src/nyc_tlc/
│   ├── ingest/          # TLC parquet + Open-Meteo + zones shapefile
│   ├── clean/           # bronze → silver (SQL filters + type casts)
│   ├── ml/              # zone clustering (K-Means, GMM)
│   ├── dashboard/       # Streamlit multi-page app
│   ├── utils/           # logging, DuckDB connection helper
│   └── config.py        # paths and env vars
├── dbt_project/         # staging → intermediate → marts
├── prefect_flows/       # orchestration flow
├── data/                # bronze/ silver/ marts/ (gitignored)
├── docs/                # ARCHITECTURE.md, LAPORAN.md, slides.md
└── Makefile
```

---
