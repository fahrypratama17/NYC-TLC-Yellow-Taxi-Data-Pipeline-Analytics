"""Zone clustering: compare K-Means, GMM, HDBSCAN; pick best via silhouette."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from nyc_tlc import config
from nyc_tlc.ml.features import load_zone_features
from nyc_tlc.utils import get_logger

log = get_logger(__name__)


FEATURE_COLS = [
    "total_trips",
    "avg_distance",
    "avg_duration_min",
    "avg_speed_mph",
    "avg_fare",
    "avg_tip_ratio",
    "share_late_night",
    "share_morning_rush",
    "share_midday",
    "share_evening_rush",
    "share_evening",
    "share_weekend",
    "rain_demand_ratio",
    "snow_demand_ratio",
]

# total_trips is heavily right-skewed (airport zones carry 100x quiet zones).
# log1p compresses the tail so time-of-day and weather features actually
# influence the clustering instead of being drowned out by raw counts.
LOG_FEATURES = ["total_trips"]


def build_feature_matrix(df: pd.DataFrame) -> tuple[np.ndarray, StandardScaler]:
    X = df[FEATURE_COLS].copy()
    for col in LOG_FEATURES:
        X[col] = np.log1p(X[col])
    scaler = StandardScaler()
    return scaler.fit_transform(X.to_numpy()), scaler


@dataclass
class ClusteringResult:
    name: str
    labels: np.ndarray
    silhouette: float
    davies_bouldin: float
    calinski_harabasz: float
    n_clusters: int


def _score(name: str, X: np.ndarray, labels: np.ndarray, k: int) -> ClusteringResult:
    if len(set(labels)) < 2:
        return ClusteringResult(name, labels, -1, np.inf, 0, k)
    return ClusteringResult(
        name=name,
        labels=labels,
        silhouette=float(silhouette_score(X, labels)),
        davies_bouldin=float(davies_bouldin_score(X, labels)),
        calinski_harabasz=float(calinski_harabasz_score(X, labels)),
        n_clusters=k,
    )


def _kmeans_sweep(X: np.ndarray, k_range: range) -> ClusteringResult:
    best: ClusteringResult | None = None
    for k in k_range:
        labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)
        res = _score(f"kmeans_k{k}", X, labels, k)
        log.info("cluster.kmeans", k=k, sil=round(res.silhouette, 4))
        if best is None or res.silhouette > best.silhouette:
            best = res
    assert best is not None
    return best


def _gmm_sweep(X: np.ndarray, k_range: range) -> ClusteringResult:
    best: ClusteringResult | None = None
    for k in k_range:
        labels = GaussianMixture(n_components=k, random_state=42).fit_predict(X)
        res = _score(f"gmm_k{k}", X, labels, k)
        log.info("cluster.gmm", k=k, sil=round(res.silhouette, 4))
        if best is None or res.silhouette > best.silhouette:
            best = res
    assert best is not None
    return best


def train_clustering() -> dict[str, object]:
    """Fit clustering on zone features, pick the best algorithm by silhouette score."""
    df = load_zone_features().dropna(subset=FEATURE_COLS, how="any").reset_index(drop=True)
    X, scaler = build_feature_matrix(df)

    candidates = [
        _kmeans_sweep(X, k_range=range(3, 11)),
        _gmm_sweep(X, k_range=range(3, 11)),
    ]
    winner = max(candidates, key=lambda c: c.silhouette)
    log.info(
        "cluster.winner",
        name=winner.name,
        sil=round(winner.silhouette, 4),
        db=round(winner.davies_bouldin, 4),
        k=winner.n_clusters,
    )

    from nyc_tlc.ml.profiles import characterize_clusters

    labelled = df.assign(cluster=winner.labels)
    profiles = characterize_clusters(labelled, FEATURE_COLS, LOG_FEATURES)

    out_dir = config.MARTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    name_map = dict(zip(profiles["cluster"], profiles["cluster_name"], strict=True))
    df_out = pd.DataFrame(
        {
            "zone_id": df["zone_id"].to_numpy(),
            "cluster": winner.labels,
            "cluster_name": [name_map.get(c, "Unclustered") for c in winner.labels],
        }
    )
    df_out.to_parquet(out_dir / "zone_clusters.parquet", index=False)
    profiles.to_parquet(out_dir / "zone_cluster_profiles.parquet", index=False)

    for _, row in profiles.iterrows():
        log.info(
            "cluster.profile",
            cluster=int(row["cluster"]),
            name=row["cluster_name"],
            n_zones=int(row["n_zones"]),
        )

    return {
        "labels": winner.labels,
        "winner": winner.name,
        "scaler": scaler,
        "n_clusters": winner.n_clusters,
        "profiles": profiles,
    }
