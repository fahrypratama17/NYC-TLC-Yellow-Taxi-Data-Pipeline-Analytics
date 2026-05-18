from __future__ import annotations

import duckdb

from nyc_tlc import config


def get_duckdb(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    config.DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(config.DUCKDB_PATH), read_only=read_only)
    conn.execute("INSTALL spatial; LOAD spatial;")
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    return conn
