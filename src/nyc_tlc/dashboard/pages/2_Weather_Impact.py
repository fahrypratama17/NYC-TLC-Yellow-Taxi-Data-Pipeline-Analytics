"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE

Weather impact — how conditions and temperature relate to demand.
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
from nyc_tlc.dashboard.data import load_hourly_demand
from nyc_tlc.dashboard.theme import WEATHER_COLOURS, style

st.set_page_config(page_title="Weather Impact · NYC TLC", page_icon="🌧️", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "Weather Impact on Demand",
    "How rain, snow, and temperature relate to how many taxis New Yorkers hail.",
)

df = load_hourly_demand()

day_type = st.radio("Day type", ["All days", "Weekdays", "Weekends"], horizontal=True)
if day_type == "Weekdays":
    df = df[~df["is_weekend"]]
elif day_type == "Weekends":
    df = df[df["is_weekend"]]

# ── Headline weather effects ────────────────────────────
by_cat = df.groupby("weather_category", as_index=False)["trips"].mean()
cat_lookup = dict(zip(by_cat["weather_category"], by_cat["trips"], strict=True))
clear = cat_lookup.get("clear")


def _delta(condition: str) -> str:
    value = cat_lookup.get(condition)
    if value is None or not clear:
        return "—"
    return f"{(value / clear - 1) * 100:+.0f}%"


bands = pd.cut(
    df["temperature_c"],
    bins=[-100, 0, 10, 20, 30, 100],
    labels=["< 0°C", "0–10°C", "10–20°C", "20–30°C", "30°C +"],
)
by_temp = (
    df.assign(temp_band=bands).groupby("temp_band", as_index=False, observed=True)["trips"].mean()
)
busiest_band = by_temp.loc[by_temp["trips"].idxmax(), "temp_band"]

cards(
    [
        ("Rain vs clear", _delta("rain"), "Change in average hourly demand"),
        ("Snow vs clear", _delta("snow"), "Change in average hourly demand"),
        ("Busiest temperature", str(busiest_band), "Highest average demand"),
    ],
    accent=True,
)

# ── Demand by weather condition ─────────────────────────
section(
    "Demand by weather condition",
    "Average trips per hour under each sky condition.",
)
order = by_cat.sort_values("trips", ascending=False)
fig_cat = px.bar(
    order,
    x="weather_category",
    y="trips",
    color="weather_category",
    color_discrete_map=WEATHER_COLOURS,
)
fig_cat.update_layout(xaxis_title=None, yaxis_title="Average trips per hour", showlegend=False)
st.plotly_chart(style(fig_cat, 320), width="stretch")
insight(
    f"Demand is highest in the rain ({_delta('rain')} vs clear weather) — when "
    "it pours, New Yorkers swap walking and transit for a taxi. These are raw "
    "averages; the weather integration also shows up in the zone clustering "
    "features — zones with high rain/snow demand ratios form their own segment."
)

# ── Demand by temperature ───────────────────────────────
section(
    "Demand by temperature",
    "Average trips per hour across temperature bands.",
)
_temp_colours = {
    "< 0°C": "#2C5F8A",
    "0–10°C": "#6C9BC4",
    "10–20°C": "#A9C5DD",
    "20–30°C": "#E8B97A",
    "30°C +": "#C4634E",
}
fig_temp = px.bar(
    by_temp,
    x="temp_band",
    y="trips",
    color="temp_band",
    color_discrete_map=_temp_colours,
)
fig_temp.update_layout(xaxis_title=None, yaxis_title="Average trips per hour", showlegend=False)
st.plotly_chart(style(fig_temp, 320), width="stretch")
insight(
    f"Demand is strongest in the {busiest_band} band — comfortable, mild "
    "weather coincides with the busiest periods of city activity."
)
