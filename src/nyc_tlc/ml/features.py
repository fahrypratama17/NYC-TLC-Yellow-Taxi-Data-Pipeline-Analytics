"""Feature loading helpers — fetch marts as pandas frames for ML training."""

from __future__ import annotations

import pandas as pd

from nyc_tlc.utils import get_duckdb


def load_zone_features() -> pd.DataFrame:
    conn = get_duckdb(read_only=True)
    result = conn.execute("SELECT * FROM marts.fct_zone_features ORDER BY zone_id").df()
    conn.close()
    return result


def load_hourly_demand() -> pd.DataFrame:
    conn = get_duckdb(read_only=True)
    result = conn.execute("SELECT * FROM marts.fct_hourly_demand ORDER BY ts_hour").df()
    conn.close()
    return result
