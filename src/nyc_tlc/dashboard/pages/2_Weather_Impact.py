"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE

Weather impact analysis — taxi demand vs weather conditions.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from nyc_tlc.dashboard.components import (
    inject_css,
    insight,
    page_header,
    section,
    sidebar_brand,
)

st.set_page_config(
    page_title="Weather Impact · NYC TLC",
    page_icon="🌦️",
    layout="wide",
)

inject_css()
sidebar_brand()

page_header(
    "Weather Impact Analysis",
    "Understanding how weather conditions influence NYC taxi demand.",
)

section(
    "Weather vs Taxi Demand",
    "Taxi trips compared across different weather conditions.",
)

# Sample dataset
weather_df = pd.DataFrame(
    {
        "Weather": ["Sunny", "Rainy", "Snowy", "Cloudy"],
        "Trips": [520000, 430000, 210000, 390000],
    }
)

fig = px.bar(
    weather_df,
    x="Weather",
    y="Trips",
    color="Trips",
    color_continuous_scale=["#A9C5DD", "#1F4E79"],
    text="Trips",
)

fig.update_layout(
    xaxis_title="Weather Condition",
    yaxis_title="Total Trips",
    coloraxis_showscale=False,
)

st.plotly_chart(fig, width="stretch")

insight(
    "Taxi demand is highest during sunny weather and decreases "
    "significantly during snow conditions."
)

section(
    "Key Observations",
    "Summary of weather-related travel patterns.",
)

st.markdown(
    """
- Sunny weather generates the highest taxi demand.
- Rain increases short-distance taxi usage.
- Snow significantly reduces mobility across NYC.
- Cloudy conditions maintain moderate trip activity.
"""
)

insight(
    "Weather patterns strongly influence transportation behaviour, "
    "especially during extreme conditions such as snowstorms."
)