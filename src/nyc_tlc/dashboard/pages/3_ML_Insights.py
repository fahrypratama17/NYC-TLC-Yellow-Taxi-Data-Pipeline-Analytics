"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE

ML insights — zone segments by behavioural clustering.
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
from nyc_tlc.dashboard.data import load_cluster_profiles
from nyc_tlc.dashboard.theme import SEGMENT_COLOURS, style
from nyc_tlc.ml.profiles import (
    _DEFAULT_ACTION,
    _DEFAULT_DESCRIPTION,
    ARCHETYPE_ACTIONS,
    ARCHETYPE_DESCRIPTIONS,
)

st.set_page_config(page_title="ML Insights · NYC TLC", page_icon="🧭", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "Zone Segments",
    "How the city's taxi zones group together by operational behaviour.",
)

PERIODS = {
    "mean_share_morning_rush": "Morning rush",
    "mean_share_midday": "Midday",
    "mean_share_evening_rush": "Evening rush",
    "mean_share_evening": "Evening",
    "mean_share_late_night": "Late night",
}

# ── Zone segments ───────────────────────────────────────
section(
    "Zone segments",
    "Taxi zones grouped by how their trips behave — each segment is a "
    "different kind of place to operate in.",
)

profiles = load_cluster_profiles()
if profiles.empty:
    st.warning("Run `make train` to produce the segments first.")
else:
    summary = pd.DataFrame(
        [
            {
                "Segment": r["cluster_name"],
                "Zones": int(r["n_zones"]),
                "Typical fare": f"${r['mean_avg_fare']:.2f}",
                "Typical trip": f"{r['mean_avg_distance']:.1f} mi",
                "Busiest period": PERIODS[max(PERIODS, key=lambda c: r.get(c, 0))],
            }
            for _, r in profiles.iterrows()
        ]
    )
    st.dataframe(summary, hide_index=True, width="stretch")

    for _, row in profiles.iterrows():
        name = row["cluster_name"]
        with st.container(border=True):
            st.markdown(f"**{name}** &nbsp;·&nbsp; {int(row['n_zones'])} zones")
            st.markdown(ARCHETYPE_DESCRIPTIONS.get(name, _DEFAULT_DESCRIPTION))
            st.markdown(f"**Recommended focus —** {ARCHETYPE_ACTIONS.get(name, _DEFAULT_ACTION)}")

    # Evidence — collapsed by default; the basis for the segment names.
    with st.expander("How these segments were defined — the evidence"):
        st.caption(
            "Zones were grouped by K-Means clustering on their trip behaviour. "
            "This chart compares each segment to the citywide average on the "
            "measures that most distinguish them — the basis for the names and "
            "recommendations above. Bars left of centre are below the city "
            "average; right of centre, above it."
        )
        key_traits = {
            "total_trips": "Trip volume",
            "avg_fare": "Fare",
            "avg_distance": "Trip distance",
            "share_evening_rush": "Evening-rush trips",
            "share_late_night": "Late-night trips",
            "share_weekend": "Weekend trips",
            "rain_demand_ratio": "Demand when raining",
        }
        comparison = pd.DataFrame(
            [
                {
                    "Trait": label,
                    "Segment": r["cluster_name"],
                    "Deviation": float(r.get(f"z_{col}", 0.0)),
                }
                for _, r in profiles.iterrows()
                for col, label in key_traits.items()
            ]
        )
        fig_cmp = px.bar(
            comparison,
            x="Deviation",
            y="Trait",
            color="Segment",
            orientation="h",
            barmode="group",
            color_discrete_map=SEGMENT_COLOURS,
        )
        fig_cmp.add_vline(x=0, line_color="#B0B6BD", line_width=1)
        fig_cmp.update_xaxes(showticklabels=False, title="", range=[-2, 2])
        fig_cmp.update_yaxes(title="")
        st.plotly_chart(style(fig_cmp, 440), width="stretch")
        st.caption(
            "Full per-zone profiles are stored in "
            "`data/marts/zone_cluster_profiles.parquet`. "
            "K-Means and GMM are compared; the winner is chosen by silhouette score."
        )

