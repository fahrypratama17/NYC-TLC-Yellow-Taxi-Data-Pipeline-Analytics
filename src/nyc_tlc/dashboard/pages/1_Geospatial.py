"""


Geospatial analysis — 2D/3D zone maps + ranked trip corridors.
"""

from __future__ import annotations

import branca.colormap as cm
import folium
import numpy as np
import plotly.express as px
import pydeck as pdk
import streamlit as st
from streamlit_folium import st_folium

from nyc_tlc.dashboard.components import (
    inject_css,
    insight,
    page_header,
    section,
    sidebar_brand,
)
from nyc_tlc.dashboard.data import (
    load_cluster_profiles,
    load_flows,
    load_zone_clusters,
    load_zone_features,
    load_zones_geo,
)
from nyc_tlc.dashboard.theme import hex_to_rgb, segment_colour, style
from nyc_tlc.ml.profiles import ARCHETYPE_DESCRIPTIONS

st.set_page_config(page_title="Geospatial · NYC TLC", page_icon="🗺️", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "Geospatial Analysis",
    "Where demand concentrates across the 263 taxi zones, and how trips flow between them.",
)

gdf = load_zones_geo()
if gdf.empty:
    st.error("Taxi-zone shapefile not found. Run `make ingest` to download it.")
    st.stop()

clusters = load_zone_clusters()
features = load_zone_features()
profiles = load_cluster_profiles()

merged = gdf.merge(clusters, on="zone_id", how="left").merge(features, on="zone_id", how="left")
merged["cluster_name"] = merged["cluster_name"].fillna("Insufficient data")
merged["total_trips"] = merged["total_trips"].fillna(0).astype(int)
merged["avg_fare"] = merged["avg_fare"].fillna(0).round(2)

STROKE = {"color": "#5A6470", "weight": 0.7}


def _swatch(colour_hex: str, label: str) -> str:
    return (
        f"<span style='display:inline-block;width:12px;height:12px;"
        f"background:{colour_hex};border-radius:3px;margin:0 6px 0 14px;"
        f"vertical-align:middle'></span><span style='font-size:0.85rem'>{label}</span>"
    )


# ── Zone map ────────────────────────────────────────────
section("Zone map", "Two views of the same 263 zones — flat colour, or 3D height.")
tab_flat, tab_3d = st.tabs(["Colour-coded (2D)", "Demand height (3D)"])

with tab_flat:
    metric = st.radio(
        "Colour zones by",
        ["Cluster archetype", "Pickup volume", "Average fare"],
        horizontal=True,
        label_visibility="collapsed",
    )
    fmap = folium.Map(location=[40.73, -73.95], zoom_start=11, tiles="cartodbpositron")

    if metric == "Cluster archetype":
        ordered = sorted(n for n in merged["cluster_name"].unique() if n != "Insufficient data")
        if "Insufficient data" in merged["cluster_name"].values:
            ordered.append("Insufficient data")
        colour = {n: segment_colour(n, i) for i, n in enumerate(ordered)}
        folium.GeoJson(
            merged.__geo_interface__,
            style_function=lambda f: {
                "fillColor": colour.get(f["properties"]["cluster_name"], "#cccccc"),
                "fillOpacity": 0.82,
                **STROKE,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["zone", "borough", "cluster_name", "total_trips"],
                aliases=["Zone", "Borough", "Segment", "Total trips"],
            ),
        ).add_to(fmap)
    else:
        column = "total_trips" if metric == "Pickup volume" else "avg_fare"
        merged["_viz"] = (
            (merged["total_trips"] / 1000).round(1)
            if column == "total_trips"
            else merged["avg_fare"]
        )
        positive = merged.loc[merged["_viz"] > 0, "_viz"]
        breaks = sorted(set(np.quantile(positive, [0, 0.2, 0.4, 0.6, 0.8, 1.0]).round(1)))
        bin_colours = ["#EAF0F6", "#A9C5DD", "#6C9BC4", "#3D72A8", "#1F4E79"]
        used_colours = bin_colours[: len(breaks) - 1]
        scale = cm.StepColormap(used_colours, index=breaks, vmin=breaks[0], vmax=breaks[-1])
        folium.GeoJson(
            merged.__geo_interface__,
            style_function=lambda f: {
                "fillColor": (
                    scale(f["properties"]["_viz"]) if f["properties"]["_viz"] > 0 else "#EEEEEE"
                ),
                "fillOpacity": 0.86,
                **STROKE,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["zone", "borough", column],
                aliases=["Zone", "Borough", metric],
            ),
        ).add_to(fmap)

    st_folium(fmap, width=None, height=520, returned_objects=[])

    if metric == "Cluster archetype":
        st.markdown("".join(_swatch(colour[n], n) for n in ordered), unsafe_allow_html=True)
        insight(
            "The segments are geographically coherent — Manhattan's core is "
            "one dense high-volume cluster, the outer boroughs are mostly "
            "residential, and a band of inner Brooklyn and Queens stands out "
            "as weather-sensitive."
        )
    else:

        def _fmt(value: float) -> str:
            if metric == "Pickup volume":
                return f"{value / 1000:.1f}M" if value >= 1000 else f"{value:.0f}k"
            return f"&#36;{value:.0f}"  # escaped $ — avoids Streamlit LaTeX

        st.markdown(
            "".join(
                _swatch(used_colours[i], f"{_fmt(breaks[i])} – {_fmt(breaks[i + 1])}")
                for i in range(len(used_colours))
            ),
            unsafe_allow_html=True,
        )
        insight(
            "Demand and fares both rise away from a few dominant zones — most "
            "of the city's trips come from Manhattan and the airports."
        )

with tab_3d:
    geo3d = merged[["zone_id", "zone", "borough", "total_trips", "cluster_name", "geometry"]].copy()
    geo3d["fill"] = geo3d["cluster_name"].apply(lambda n: [*hex_to_rgb(segment_colour(n)), 215])
    max_trips = max(int(geo3d["total_trips"].max()), 1)
    layer = pdk.Layer(
        "GeoJsonLayer",
        geo3d.__geo_interface__,
        extruded=True,
        get_elevation="properties.total_trips",
        elevation_scale=9000 / max_trips,
        get_fill_color="properties.fill",
        get_line_color=[255, 255, 255, 50],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=40.72, longitude=-73.95, zoom=9.5, pitch=52, bearing=12
            ),
            map_style="light",
            tooltip={"text": "{zone}\n{total_trips} trips"},
        ),
        width="stretch",
    )
    insight(
        "Each zone's height is its trip volume; colour is its segment. The "
        "Manhattan core rises far above everything else — demand in NYC is "
        "extraordinarily concentrated in a small part of the city."
    )

# ── Archetype reference ─────────────────────────────────
if not profiles.empty:
    with st.expander("Reference — what each segment means"):
        for _, row in profiles.iterrows():
            desc = ARCHETYPE_DESCRIPTIONS.get(
                row["cluster_name"], "A mix of behaviours with no single pattern."
            )
            st.markdown(f"**{row['cluster_name']}** ({int(row['n_zones'])} zones) — {desc}")
        st.markdown(
            "_**Insufficient data** — zones with too few trips to profile "
            "reliably; excluded from the segmentation and shown in grey._"
        )

# ── Trip corridors ──────────────────────────────────────
section(
    "Busiest trip corridors",
    "The most-travelled one-way routes, origin → destination, ranked by total "
    "trips. Darker bars carry more trips.",
)
n_show = st.slider("Number of corridors to show", 6, 24, 12)

flows = load_flows(min_trips=200)
zone_name = gdf.set_index("zone_id")["zone"].to_dict()
flows = flows[flows["origin_zone_id"] != flows["destination_zone_id"]].copy()
top = flows.nlargest(n_show, "trips").sort_values("trips").copy()
top["route"] = (
    top["origin_zone_id"].map(zone_name).fillna("Unknown")
    + "  →  "
    + top["destination_zone_id"].map(zone_name).fillna("Unknown")
)
top["label"] = top["trips"].map(lambda v: f"{v / 1000:.0f}k")

fig = px.bar(
    top,
    x="trips",
    y="route",
    orientation="h",
    color="trips",
    color_continuous_scale=["#A9C5DD", "#1F4E79"],
    text="label",
)
fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}<br>%{x:,} trips<extra></extra>",
)
fig.update_layout(xaxis_title="Total trips", yaxis_title=None, coloraxis_showscale=False)
st.plotly_chart(style(fig, 90 + 30 * n_show), width="stretch")
insight(
    "The busiest corridors are short hops within Manhattan's Upper East Side. "
    "Routes appear in both directions with similar volumes — demand there is "
    "balanced, not one-way."
)
