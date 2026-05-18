from __future__ import annotations

import numpy as np
import pandas as pd

ARCHETYPE_DESCRIPTIONS = {
    "High-Volume Urban Core": "The city's busiest zones — very high trip count with short, fast rides.",
    "Airport & Long-Haul Gateway": "Airport and long-distance zones — fewer trips but much longer and more expensive.",
    "Commuter Corridor": "Weekday commuter zones — demand spikes at morning and evening rush hours.",
    "Nightlife & Weekend Hotspot": "Leisure zones — busiest late at night and on weekends.",
    "Midday Business District": "Business zones — trips concentrate in the midday working hours.",
    "Weather-Sensitive Demand": "Zones where demand rises the most when it rains or snows.",
    "Low-Activity Residential": "Outer-borough zones — fewer trips overall but rides tend to be longer.",
}

ARCHETYPE_ACTIONS = {
    "High-Volume Urban Core": "Concentrate the largest share of the fleet here — demand is consistently high.",
    "Airport & Long-Haul Gateway": "Ensure steady driver availability for airport runs.",
    "Commuter Corridor": "Stage vehicles for morning and evening rush; scale back midday and weekends.",
    "Nightlife & Weekend Hotspot": "Increase late-night and weekend coverage.",
    "Midday Business District": "Focus coverage on the midday working hours.",
    "Weather-Sensitive Demand": "Add vehicles when rain or snow is forecast.",
    "Low-Activity Residential": "Keep lighter coverage; expect longer rides toward the city core.",
}

_DEFAULT_DESCRIPTION = "A mix of behaviours with no single dominant pattern."
_DEFAULT_ACTION = "Monitor demand patterns before committing fleet resources."

_FEATURE_TO_NAME = {
    "total_trips":         "High-Volume Urban Core",
    "avg_distance":        "Airport & Long-Haul Gateway",
    "avg_fare":            "Airport & Long-Haul Gateway",
    "share_morning_rush":  "Commuter Corridor",
    "share_evening_rush":  "Commuter Corridor",
    "share_late_night":    "Nightlife & Weekend Hotspot",
    "share_weekend":       "Nightlife & Weekend Hotspot",
    "share_midday":        "Midday Business District",
    "rain_demand_ratio":   "Weather-Sensitive Demand",
    "snow_demand_ratio":   "Weather-Sensitive Demand",
}


def characterize_clusters(
    labelled: pd.DataFrame,
    feature_cols: list[str],
    log_features: list[str],
) -> pd.DataFrame:
    """Name each cluster by its most distinctive feature vs the citywide average."""
    means = labelled.groupby("cluster")[feature_cols].mean()
    sizes = labelled.groupby("cluster").size()
    city_mean = labelled[feature_cols].mean()
    city_std = labelled[feature_cols].std().replace(0, 1)

    assigned: dict[int, str] = {}
    for cluster in means.index:
        if cluster == -1:
            assigned[cluster] = "Noise / Outlier Zones"
            continue
        # Find the feature with the largest positive z-score deviation
        z = (means.loc[cluster] - city_mean) / city_std
        ranked = z.sort_values(ascending=False)
        name = "Low-Activity Residential"
        for feat in ranked.index:
            if feat in _FEATURE_TO_NAME and ranked[feat] > 0.2:
                name = _FEATURE_TO_NAME[feat]
                break
        assigned[cluster] = name

    rows = []
    for cluster in means.index:
        row: dict = {
            "cluster": int(cluster),
            "cluster_name": assigned[cluster],
            "n_zones": int(sizes[cluster]),
        }
        for feat in feature_cols:
            row[f"mean_{feat}"] = float(means.loc[cluster, feat])
            row[f"z_{feat}"] = round(float((means.loc[cluster, feat] - city_mean[feat]) / city_std[feat]), 3)
        rows.append(row)

    return pd.DataFrame(rows).sort_values("cluster").reset_index(drop=True)
