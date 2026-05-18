"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE

Streamlit entrypoint — guided executive summary.
Run: streamlit run src/nyc_tlc/dashboard/Home.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from nyc_tlc.dashboard.components import (
    cards,
    inject_css,
    insight,
    page_header,
    section,
    sidebar_brand,
)
from nyc_tlc.dashboard.data import (
    load_cluster_profiles,
    load_hourly_demand,
    load_zone_features,
)
from nyc_tlc.dashboard.theme import ACCENT, HEATMAP_SCALE, style

st.set_page_config(page_title="NYC TLC Analytics", page_icon="🚕", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "NYC Yellow Taxi — Operational Analytics",
    "An end-to-end view of taxi demand across New York City, "
    "January–June 2025, integrated with hourly weather.",
)

demand = load_hourly_demand()
demand["ts_hour"] = pd.to_datetime(demand["ts_hour"])
features = load_zone_features()
profiles = load_cluster_profiles()

# ── Headline figures ────────────────────────────────────
total_trips = int(features["total_trips"].sum())
weights = features["total_trips"]
avg_fare = float((features["avg_fare"] * weights).sum() / weights.sum())
avg_distance = float((features["avg_distance"] * weights).sum() / weights.sum())
n_days = demand["ts_hour"].dt.date.nunique()

cards(
    [
        ("Total trips", f"{total_trips / 1e6:.1f}M", "Jan–Jun 2025"),
        ("Average fare", f"${avg_fare:.2f}", "Per trip, citywide"),
        ("Average distance", f"{avg_distance:.1f} mi", "Per trip, citywide"),
        ("Days covered", f"{n_days}", "Six full months"),
    ]
)

# ── What the dashboard answers ──────────────────────────
section(
    "What this dashboard answers",
    "Three questions about where, when, and how taxi demand moves.",
)

by_hour = demand.groupby("pickup_hour", as_index=False)["trips"].mean()
peak_hour = int(by_hour.loc[by_hour["trips"].idxmax(), "pickup_hour"])
low = by_hour["trips"].min()
ratio = by_hour["trips"].max() / low if low else 0

n_segments = len(profiles) if not profiles.empty else 0

cards(
    [
        ("Where", f"{n_segments} zone segments", "Distinct operating profiles — see Geospatial"),
        (
            "When",
            f"Peak at {peak_hour}:00",
            f"About {ratio:.0f}x the pre-dawn low — see Weather Impact",
        ),
        ("ML Clusters", f"{n_segments} archetypes", "Behavioural segments — see ML Insights"),
    ],
    accent=True,
)

# ── Daily demand ────────────────────────────────────────
section("Demand across the six months", "Total trips per day, with a 7-day trend.")
daily = demand.set_index("ts_hour")["trips"].resample("D").sum().reset_index()
daily["trend"] = daily["trips"].rolling(7, center=True, min_periods=1).mean()
fig_daily = px.area(daily, x="ts_hour", y="trips")
fig_daily.update_traces(
    line_color="rgba(44,107,170,0.55)",
    fillcolor="rgba(44,107,170,0.10)",
    name="Daily",
    hovertemplate="%{y:,.0f} trips<extra></extra>",
)
fig_daily.add_scatter(
    x=daily["ts_hour"],
    y=daily["trend"],
    mode="lines",
    line={"color": ACCENT, "width": 3},
    name="7-day trend",
)
fig_daily.update_layout(xaxis_title=None, yaxis_title="Trips per day")
st.plotly_chart(style(fig_daily, 320), width="stretch")
insight(
    "Daily volume trends gently upward from winter into summer. The sawtooth "
    "is the weekly rhythm — weekday highs and lighter weekends."
)

# ── Weekly rhythm heatmap ───────────────────────────────
section(
    "The weekly rhythm",
    "Average trips for every hour of every weekday — the whole week at a glance.",
)
_days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 0: "Sun"}
_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
grid = demand.groupby(["pickup_dow", "pickup_hour"], as_index=False)["trips"].mean()
grid["day"] = grid["pickup_dow"].map(_days)
pivot = grid.pivot(index="day", columns="pickup_hour", values="trips").reindex(_order)
fig_heat = px.imshow(
    pivot,
    color_continuous_scale=HEATMAP_SCALE,
    aspect="auto",
    labels={"x": "Hour of day", "y": "", "color": "Trips/hour"},
)
fig_heat.update_xaxes(dtick=2, title="Hour of day")
fig_heat.update_yaxes(title="")
fig_heat.update_traces(hovertemplate="%{y} %{x}:00 — %{z:,.0f} trips/hr<extra></extra>")
st.plotly_chart(style(fig_heat, 320), width="stretch")
insight(
    f"Two demand worlds: weekdays spike at the {peak_hour}:00 evening commute, "
    "while Friday and Saturday stay bright late into the night. The pre-dawn "
    f"hours are nearly empty — a roughly {ratio:.0f}-fold swing across the week."
)
