"""Data loaders used across all Streamlit pages."""

from __future__ import annotations

import geopandas as gpd
import pandas as pd
import streamlit as st

from nyc_tlc import config
from nyc_tlc.utils import get_duckdb


@st.cache_data
def load_zone_features() -> pd.DataFrame:
    conn = get_duckdb(read_only=True)
    result = conn.execute("SELECT * FROM marts.fct_zone_features").df()
    conn.close()
    return result


@st.cache_data
def load_zone_clusters() -> pd.DataFrame:
    path = config.MARTS_DIR / "zone_clusters.parquet"
    if not path.exists():
        return pd.DataFrame(columns=["zone_id", "cluster", "cluster_name"])
    return pd.read_parquet(path)


@st.cache_data
def load_cluster_profiles() -> pd.DataFrame:
    path = config.MARTS_DIR / "zone_cluster_profiles.parquet"
    if not path.exists():
        return pd.DataFrame(columns=["cluster", "cluster_name", "justification"])
    return pd.read_parquet(path)


@st.cache_data
def load_hourly_demand() -> pd.DataFrame:
    conn = get_duckdb(read_only=True)
    result = conn.execute("SELECT * FROM marts.fct_hourly_demand ORDER BY ts_hour").df()
    conn.close()
    return result


@st.cache_data
def load_flows(min_trips: int = 200) -> pd.DataFrame:
    conn = get_duckdb(read_only=True)
    result = conn.execute(f"SELECT * FROM marts.fct_flow_od WHERE trips >= {min_trips}").df()
    conn.close()
    return result


@st.cache_data
def load_zones_geo() -> gpd.GeoDataFrame:
    shp_dir = config.BRONZE_DIR / "taxi_zones"
    shp = next(shp_dir.rglob("*.shp"), None)
    if shp is None:
        return gpd.GeoDataFrame(columns=["LocationID", "zone", "borough", "geometry"])
    gdf = gpd.read_file(shp).to_crs(epsg=4326)
    gdf = gdf.rename(columns={"LocationID": "zone_id"})
    return gdf
