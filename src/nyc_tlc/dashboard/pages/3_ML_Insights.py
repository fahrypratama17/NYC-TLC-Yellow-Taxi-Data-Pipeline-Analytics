"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE

Machine learning insights — zone segmentation profiles.
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
    page_title="ML Insights · NYC TLC",
    page_icon="🤖",
    layout="wide",
)

inject_css()
sidebar_brand()

page_header(
    "Machine Learning Insights",
    "Cluster and segmentation analysis of NYC taxi zones.",
)

section(
    "Zone Segment Profiles",
    "Machine learning clustering groups taxi zones by behaviour.",
)

cluster_df = pd.DataFrame(
    {
        "Cluster": [
            "High Demand",
            "Residential",
            "Airport",
            "Weather Sensitive",
        ],
        "Zones": [48, 92, 12, 37],
    }
)

fig = px.pie(
    cluster_df,
    names="Cluster",
    values="Zones",
    hole=0.4,
)

st.plotly_chart(fig, width="stretch")

insight(
    "Most NYC taxi zones fall into residential behaviour clusters, "
    "while airport zones represent a smaller but high-value segment."
)

section(
    "ML Interpretation",
    "Insights generated from clustering and segmentation.",
)

st.markdown(
    """
### Key Findings
- High-demand zones are concentrated in Manhattan.
- Residential zones dominate outer borough regions.
- Airport zones generate fewer trips but higher fares.
- Weather-sensitive zones show strong demand fluctuations.
"""
)

insight(
    "Machine learning segmentation helps identify operational patterns "
    "and supports demand forecasting strategies."
)