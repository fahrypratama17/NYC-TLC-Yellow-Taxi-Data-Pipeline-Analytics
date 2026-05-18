---
marp: true
theme: default
paginate: true
header: "RDV Final Project · NYC TLC Data Pipeline"
footer: "TIF-A 2026"
---

<style>
section.lead h1 { font-size: 2.0em; }
.placeholder {
  border: 2px dashed #9aa0a6;
  border-radius: 8px;
  padding: 1.6em;
  text-align: center;
  color: #5f6368;
  font-style: italic;
  background: #f6f7f9;
}
.small { font-size: 0.8em; }
table { font-size: 0.85em; }
</style>

<!--
============================================================
PRESENTATION DECK — render with Marp (https://marp.app):
    npx @marp-team/marp-cli docs/slides.md --pdf
    npx @marp-team/marp-cli docs/slides.md --pptx
or use the "Marp for VS Code" extension.

SCREENSHOT PLACEHOLDERS:
Every dashed box is a placeholder. Capture the screenshot, save it under
docs/screenshots/, and replace the <div class="placeholder">...</div> with:
    ![w:1000](screenshots/your-file.png)

Presenter for each slide is noted in these speaker-note comments.
Target: a relaxed, well-paced technical talk — every stage gets its own slides.
============================================================
-->

<!-- _class: lead -->

# NYC Yellow Taxi
## A Data Engineering Pipeline & Analytics Dashboard

**Rekayasa Data dan Visualisasi — Final Project**
TIF-A · 2026

<!--
Presenter: Nafis (Project Lead).
One line: "We built an end-to-end data engineering pipeline on the NYC Taxi
trip dataset, plus a dashboard and two bonus extensions." ~20 seconds.
-->

---

# The Team

| NIM | Name | Role |
|---|---|---|
| 245150201111042 | Anindhita Faiza Aulia | Data Analyst — Analysis & Report |
| 245150201111043 | Aniza Helwa Mahanani | ML Engineer |
| 245150207111046 | Muhamad Fahry Pratama Putra | Data Engineer — Ingestion |
| 245150201111002 | Muhammad Atha Tsaqif | Data Engineer — Cleaning & Transformation |
| 245150200111008 | Nafis Naufal Rahman | Data Architect / Lead |
| 245150200111061 | Richard Samuel Hatane | Data Analyst — Dashboard |

<!--
Presenter: Nafis. Quick — 10 seconds. Names are listed alphabetically.
-->

---

# Agenda

```
  1  The Problem        — what we set out to answer
  2  Architecture       — how the system is shaped
  3  The Pipeline       — 5 stages, ingestion to orchestration
  4  Visualization      — the interactive dashboard
  5  Findings           — what the data told us
  6  Bonuses            — external data + machine learning
```

> This is a **data engineering** course — most of today is the pipeline.

<!--
Presenter: Nafis. Set expectations: the pipeline is the main act; ML is a
bonus near the end. ~20 seconds.
-->

---

<!-- _class: lead -->

# Part 1
## The Problem

<!-- Presenter: Nafis. Section divider — just read the title. -->

---

# Motivation

Taxi demand in a big city is **uneven** — across place, time, and weather.

A fleet that anticipates demand can:
- position cars where riders will be
- staff shifts for the busy hours
- react to rain and snow before demand spikes

**The NYC TLC publishes every trip as open data** — a realistic dataset to
build a pipeline on.

<!--
Presenter: Nafis. Frame the real-world "why". ~30 seconds.
-->

---

# Three Objectives

```
   WHERE      ──▶  Segment the 263 taxi zones by trip behaviour
   WHEN       ──▶  Quantify how hour, day & weather move demand
   WHAT NEXT  ──▶  Forecast hourly demand for the city
```

Every pipeline stage exists to answer these three questions.

<!--
Presenter: Nafis. These three come back on the Findings slides — the talk
closes the loop. ~25 seconds.
-->

---

# Scope & Boundaries

| | |
|---|---|
| Dataset | NYC TLC **Yellow Taxi** |
| Period | **January – June 2025** (6 months) |
| Volume | 24.08M raw trips |
| Spatial unit | 263 official taxi zones |
| External data | Open-Meteo hourly weather |

A bounded scope keeps the analysis **realistic** — as the brief requires.

<!--
Presenter: Nafis. Why 6 months: enough seasonal/weather variety, still
laptop-scale. ~25 seconds.
-->

---

<!-- _class: lead -->

# Part 2
## Architecture

<!-- Presenter: Nafis. Section divider. -->

---

# Pipeline Architecture

```
 ┌───────────┐
 │ NYC TLC   │─┐
 ├───────────┤ │   ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────────┐
 │ Open-Meteo│─┼──▶│ INGEST │─▶│ CLEAN  │─▶│ STORE  │─▶│ TRANSFORM│─▶│ VISUALIZE  │
 ├───────────┤ │   │ Bronze │  │ Silver │  │ DuckDB │  │   dbt    │  │ Streamlit  │
 │ Taxi Zones│─┘   └────────┘  └────────┘  └────────┘  └──────────┘  └────────────┘
 └───────────┘         └──────────────  Prefect orchestration  ──────────────┘
```

Five stages. One automated flow.

<!--
Presenter: Nafis. Walk left to right once. This diagram is the map of Part 3 —
each box becomes its own set of slides. ~40 seconds.
-->

---

# The Medallion Lakehouse

```
   BRONZE  ──  raw, untouched          ┐
   SILVER  ──  cleaned, validated      ┘  Parquet files  (data lake)

   GOLD    ──  joins & aggregates      ┐
   MARTS   ──  analysis-ready tables   ┘  DuckDB warehouse
```

- **Lake** holds portable raw/clean Parquet
- **Warehouse** holds modelled tables for fast queries

<!--
Presenter: Nafis. The deliberate split: files for raw/clean, warehouse for
modelled. Each layer has one job → bugs stay local, any stage rebuilds alone.
~35 seconds.
-->

---

# Technology Stack

| Stage | Tool | Why |
|---|---|---|
| Orchestration | **Prefect 3** | Python-native, built-in scheduler |
| Storage / query | **DuckDB + Parquet** | No server, fast on a laptop |
| Transformation | **dbt** | SQL models, tests, lineage |
| Visualization | **Streamlit + Folium** | Interactive maps, pure Python |
| ML | **scikit-learn** | K-Means · GMM, silhouette-score selection |

<!--
Presenter: Nafis. Don't read every row — say "all open-source, all chosen for
a reason; the reasoning is in our decision log." ~30 seconds.
-->

---

<!-- _class: lead -->

# Part 3
## The Pipeline

<!-- Presenter: Nafis hands over to Fahry. Section divider. -->

---

# Stage 1 · Data Ingestion

```
   NYC TLC     ─┐
   Open-Meteo  ─┼──▶  download  ──▶  data/bronze/
   Taxi Zones  ─┘                    (raw, untouched)
```

**Goal:** pull every source into the Bronze layer, exactly as published.

<!--
Presenter: Fahry (Data Engineer). Ingestion = get raw data in, change
nothing. ~20 seconds.
-->

---

# Ingestion · The Three Sources

| Source | What | Format |
|---|---|---|
| NYC TLC | 6 monthly Yellow Taxi files | Parquet |
| Open-Meteo | Hourly NYC weather *(bonus)* | JSON → Parquet |
| NYC TLC | Taxi-zone boundaries | Shapefile |

Three sources, one Bronze layer.

<!--
Presenter: Fahry. Note the weather source is the external-data bonus,
introduced here at ingestion. ~25 seconds.
-->

---

# Ingestion · Built to be Reliable

- **Streaming download** — large files never fill memory
- **Idempotent** — re-runs skip files already downloaded
- **Date-bounds automatic** — no hardcoded date ranges

> Reliable + idempotent ingestion is what makes the **scheduled** run safe.

<!--
Presenter: Fahry. This is the engineering point: not just "download", but
download that can run unattended every month. ~30 seconds.
-->

---

# Ingestion · Result

<div class="placeholder">
SCREENSHOT — terminal output of <code>make ingest</code><br>
showing the download log lines and the populated<br>
<code>data/bronze/</code> folder tree
</div>

<!--
Presenter: Fahry. Capture: the ingest log + a file tree of data/bronze/.
~15 seconds to show.
-->

---

# Stage 2 · Preprocessing & Cleaning

```
   data/bronze/  ──▶  clean + validate  ──▶  data/silver/
   (raw)                                     (analysis-ready)
```

Raw taxi data is messy. Silver is the **trusted** layer.

<!--
Presenter: Atha (Data Engineer). ~15 seconds.
-->

---

# Cleaning · Anomalies Removed

| Anomaly | Action |
|---|---|
| NULL / reversed timestamps | drop |
| Distance ≤ 0 or > 200 mi | drop |
| Negative fare / total | drop |
| Zone ID outside 1–265 | drop |
| Avg speed > 100 mph (GPS error) | drop |
| `passenger_count = 0` | set to missing |

<!--
Presenter: Atha. Each rule has a reason: reversed timestamps are data entry
errors, speed >100 mph is GPS/clock anomaly, passenger_count=0 is "driver
didn't enter" per TLC convention (nulled, not dropped). Modern TLC data uses
zone IDs, not GPS coordinates. ~40 seconds.
-->

---

# Cleaning · Result

```
   24.08M  raw trips
   ─ 2.07M  anomalies removed  (8.6%)
   ─────────
   22.01M  clean trips  ──▶  Silver
```

Derived columns added: **trip duration · speed · hour · day-of-week · weekend**

<!--
Presenter: Atha. The derived columns (e.g. duration from two timestamps) are
the rubric's "transformation" requirement. ~30 seconds.
-->

---

# Cleaning · Result Output

<div class="placeholder">
SCREENSHOT — <code>make clean</code> terminal output<br>
showing the row counts (24M → 22M)
</div>

<!--
Presenter: Atha. Capture the clean log with the row-count drop. ~15 seconds.
-->

---

# Stage 3 · Storage & Data Modelling

```
   BRONZE / SILVER   ──  Parquet files
   GOLD / MARTS      ──  tables in  data/warehouse.duckdb
```

The DuckDB warehouse: an analytical database in a **single file** — no server.

<!--
Presenter: Atha. ~25 seconds.
-->

---

# Schema Design · Fact Tables by Grain

```
                ┌──────────────┐
                │   dim_zone   │  zone dimension
                └──────┬───────┘
        ┌──────────────┼──────────────┐
 ┌──────┴──────┐ ┌─────┴──────┐ ┌─────┴──────┐
 │ fct_zone_   │ │ fct_hourly_│ │ fct_flow_  │
 │ features    │ │ demand     │ │ od         │
 │ 1 row/zone  │ │ 1 row/hour │ │ O→D pairs  │
 └─────────────┘ └────────────┘ └────────────┘
```

Relevant, normalised tables — **not** one wide un-normalised dump.

<!--
Presenter: Atha. Each fact table has its own grain matched to a consumer:
features→clustering, demand→time analysis, flows→map. ~35 seconds.
-->

---

# Stage 4 · Transformation with dbt

```
   staging          intermediate            marts
   ────────         ──────────────          ─────────────
   stg_*       ──▶  int_trips_with_weather  ──▶  fct_zone_features
   (views)          int_zone_hourly              fct_hourly_demand
                                                 fct_flow_od
```

Every table is a **version-controlled SQL model**.

<!--
Presenter: Atha. dbt gives staging→intermediate→marts discipline, plus tests
and lineage for free. The weather join happens here. ~35 seconds.
-->

---

# Transformation · dbt Lineage

<div class="placeholder">
SCREENSHOT — dbt lineage graph<br>
generated by <code>make dbt-docs</code><br>
(sources → staging → intermediate → marts)
</div>

<!--
Presenter: Atha. The auto-generated lineage graph is strong visual proof of
the modelling discipline. ~20 seconds.
-->

---

# Stage 5 · Orchestration with Prefect

```
   ingest ──▶ clean ──▶ dbt run ──▶ ml train
   └──────────────  one Prefect flow  ──────────┘
```

- Each stage is a **retryable task**
- The whole pipeline runs with one command: `make flow`

<!--
Presenter: Nafis (Data Architect). The five stages become one system here.
~30 seconds.
-->

---

# Orchestration · Scheduled Automation

```
   Prefect deployment   cron:  0 5 5 * *
   ──▶ runs the full pipeline at 05:00 on the 5th of every month
```

New TLC data is ingested, cleaned, modelled, and the ML retrained —
**with no manual work**.

<div class="placeholder">SCREENSHOT — Prefect UI showing a completed flow run</div>

<!--
Presenter: Nafis. This satisfies the rubric's Automation / Scheduling
criterion. ~30 seconds.
-->

---

# Engineering Practices

Built like a production system:

- **Data tests** — dbt `not_null` + `unique` tests on all mart keys
- **Idempotency** — every stage is safe to re-run
- **Medallion separation** — bronze/silver/marts each have one job
- **Reproducibility** — `uv.lock` pins every dependency

<!--
Presenter: Nafis. ~35 seconds. This is the "engineered, not improvised"
slide — keep it brisk.
-->

---

<!-- _class: lead -->

# Part 4
## Visualization

<!-- Presenter: Nafis hands to Richard. Section divider. -->

---

# The Dashboard

A **Streamlit** app — four pages, every chart answers a question.

```
   Overview   │  Geospatial   │  Weather Impact  │  ML Insights
   KPIs &     │  zone maps &  │  demand vs       │  segments &
   trends     │  flow         │  conditions      │  forecast
```

<!--
Presenter: Richard (Data Analyst). Visualization is core, not a bonus.
~25 seconds.
-->

---

# Dashboard · Overview Page

<div class="placeholder">
SCREENSHOT — dashboard Home / Overview page<br>
(KPI row · daily trip volume · demand-by-hour bar chart)
</div>

<!--
Presenter: Richard. Point out the demand-by-hour shape — sets up the
Findings later. ~20 seconds.
-->

---

# Dashboard · Geospatial Page

<div class="placeholder">
SCREENSHOT — Geospatial page, zone map coloured by cluster archetype<br>
(show the colour-by selector and the legend)
</div>

The map satisfies the rubric's **geospatial** requirement.

<!--
Presenter: Richard. Mention the 3 colour modes + the busiest-corridors chart.
If the room allows, do this one live. ~30 seconds.
-->

---

# Dashboard · Weather Impact Page

<div class="placeholder">
SCREENSHOT — Weather Impact page<br>
(demand by weather condition · demand by temperature band)
</div>

<!--
Presenter: Richard. This page is where the external-data bonus becomes
visible. ~20 seconds.
-->

---

# Dashboard · Interactivity

The dashboard is **interactive**, as the rubric requires:

- Colour-by selector on the map (cluster / volume / fare)
- Day-type filter on Weather Impact (all / weekday / weekend)
- Corridor count slider
- Hover tooltips on every zone

<!--
Presenter: Richard. Interactivity is a scored criterion — call it out
explicitly. ~25 seconds.
-->

---

<!-- _class: lead -->

# Part 5
## Findings

<!-- Presenter: Richard hands to Ninda. Section divider. -->

---

# Finding 1 · When is Demand Highest?

```
   Peak     18:00   ──  8,388 trips/hour
   Trough   04:00   ──    849 trips/hour
                        ≈ 10× swing
```

Demand follows a strong, predictable daily rhythm.

<!--
Presenter: Ninda (Data Analyst). Answers objective WHEN. ~25 seconds.
-->

---

# Finding 2 · Weather Drives Demand

```
   Rain     ████████████████████  5,880 /hr   +22%
   Snow     ██████████████████    5,312 /hr
   Cloudy   █████████████████     4,990 /hr
   Clear    ████████████████      4,803 /hr   baseline
```

Demand is **highest in the rain** — riders avoid walking.

<!--
Presenter: Ninda. The headline weather result — rain correlates with a +22%
demand uplift. ~30 seconds.
-->

---

# Finding 3 · Zone Segments

| Segment | Zones | Avg fare | Avg trip |
|---|---|---|---|
| High-Volume Urban Core | 51 | $17.98 | 3.2 mi |
| Low-Activity Residential | 148 | $31.66 | 7.1 mi |
| Weather-Sensitive Demand | 48 | $24.85 | 4.8 mi |

Manhattan core = **cheap short hops**; outer zones = **long rides in**.

<!--
Presenter: Ninda. Answers objective WHERE. The fare/distance contrast is the
intuitive story. ~30 seconds.
-->

---

# Finding 4 · Busiest Corridor

```
   Upper East Side South  ⇄  Upper East Side North
   ───────────────────────────────────────────────
   South → North   148,067 trips
   North → South   126,550 trips
```

The densest origin-destination pair in the whole city.

<!--
Presenter: Ninda. ~20 seconds.
-->

---

<!-- _class: lead -->

# Part 6
## Bonus Extensions

<!-- Presenter: Ninda hands to Helwa. Section divider. -->

---

# Bonus 1 · External Data Integration

**Open-Meteo Historical Weather API** — *+10 points*

```
   weather  ──▶  ingested to Bronze  ──▶  joined per pickup-hour in dbt
                                          ──▶  Weather Impact dashboard
```

External data is merged **inside the pipeline**, not bolted on.

<!--
Presenter: Helwa (ML Engineer). Keep brief — the integration point is the key.
~25 seconds.
-->

---

# Bonus 2 · Machine Learning — Clustering

**Group the zones by behaviour** — *+10 points*

```
   zone features  ──▶  K-Means (k=3–10)  ──▶  best by silhouette
                   ──▶  GMM    (k=3–10)  ──▶  winner → 3 segments
```

The three segments shown in Finding 3 come from this model.
Cluster names are derived automatically from each segment's dominant feature.

<!--
Presenter: Helwa. We compared two algorithm families and let the silhouette score
pick the winner. Cluster names come from z-score analysis, not manual labelling.
~35 seconds.
-->

---

# ML · Insights Page

<div class="placeholder">
SCREENSHOT — ML Insights dashboard page<br>
(zone-segment summary table · archetype descriptions · σ-deviation chart)
</div>

<!--
Presenter: Helwa. ML output flows back into the dashboard — part of the data
flow, not separate. ~20 seconds.
-->

---

# Challenges & Lessons Learned

| Challenge | Fix |
|---|---|
| One airport zone dominated the map | quantile colour bins |
| Clustering split only by volume | log-transform the volume feature |
| Cluster names looked arbitrary | derive names from σ-profiles |
| Brief assumed GPS coordinates | modern TLC data uses zone IDs |

**Lesson:** most of the effort is data engineering, not modelling.

<!--
Presenter: Ninda. The rubric asks for "problems faced" — these are real ones.
The closing line reinforces the course framing. ~40 seconds.
-->

---

# Division of Labor

| Member | Responsibility |
|---|---|
| Nafis Naufal Rahman | Architecture, lead, documentation |
| Muhamad Fahry Pratama Putra | Ingestion, Prefect orchestration |
| Muhammad Atha Tsaqif | Cleaning, dbt modelling |
| Aniza Helwa Mahanani | Zone clustering (K-Means, GMM), archetype naming |
| Richard Samuel Hatane | Streamlit dashboard, maps |
| Anindhita Faiza Aulia | Analysis, report |

<!--
Presenter: Nafis (back to lead). Confirm each contribution briefly.
~25 seconds.
-->

---

<!-- _class: lead -->

# Thank You
## Questions?

**Ingest → Clean → Store → Transform → Visualize**
Orchestrated by Prefect · Validated end to end · +20 bonus delivered

`github.com/<your-org>/nyc-tlc-data-pipeline`

<!--
Presenter: Nafis. For Q&A: why k=3 (highest silhouette score among k=3–10),
why DuckDB (no server, fast on a laptop), why Prefect (Python-native flow,
easy local scheduler), why K-Means vs GMM (both tried, winner chosen by data).
Fill in the real GitHub URL before presenting.
-->
