"""Colour system and Plotly styling — the single source of visual consistency."""

from __future__ import annotations

import plotly.graph_objects as go

# ── Brand / UI ──────────────────────────────────────────
PRIMARY = "#2C6BAA"
INK = "#1A2A3A"
MUTED = "#5B6B7B"
BG = "#F7F8FA"
BORDER = "#E3E7EC"
GRID = "#E8EBEF"

# ── Data palette (seaborn "deep") ───────────────────────
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]
ACCENT = PRIMARY

# Diverging — below vs above the citywide average.
BELOW = "#5B8FC0"  # cool blue
ABOVE = "#C4634E"  # warm terracotta

# Stable colour per zone segment — covers all 7 possible archetypes from profiles.py
# plus the two special labels. Used identically on every dashboard page.
SEGMENT_COLOURS = {
    "High-Volume Urban Core":      "#4C72B0",
    "Airport & Long-Haul Gateway": "#C44E52",
    "Commuter Corridor":           "#55A868",
    "Nightlife & Weekend Hotspot": "#8172B3",
    "Midday Business District":    "#E0A82E",
    "Weather-Sensitive Demand":    "#937860",
    "Low-Activity Residential":    "#DD8452",
    "Noise / Outlier Zones":       "#B0B6BD",
    "Insufficient data":           "#C9CDD2",
}


def segment_colour(name: str, fallback_index: int = 0) -> str:
    """Return the stable colour for a segment name."""
    return SEGMENT_COLOURS.get(name, PALETTE[fallback_index % len(PALETTE)])


def hex_to_rgb(hex_colour: str) -> list[int]:
    """'#RRGGBB' -> [r, g, b]."""
    h = hex_colour.lstrip("#")
    return [int(h[i : i + 2], 16) for i in (0, 2, 4)]


# Sequential scale for demand heatmaps.
HEATMAP_SCALE = "Plasma"

# Intuitive colour per weather condition.
WEATHER_COLOURS = {
    "clear": "#E0A82E",
    "cloudy": "#94A3B2",
    "fog": "#C2C8CF",
    "rain": "#3D72A8",
    "rain_showers": "#5B8FC0",
    "snow": "#9CC3DE",
    "snow_showers": "#B9D4E6",
    "thunderstorm": "#6C5DAE",
    "other": "#B0B6BD",
}


def style(fig: go.Figure, height: int | None = None) -> go.Figure:
    """Apply the shared layout to a Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        font={"family": "-apple-system, Segoe UI, Roboto, sans-serif", "size": 13, "color": INK},
        colorway=PALETTE,
        margin={"l": 60, "r": 24, "t": 16, "b": 44},
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        title_text="",
        hoverlabel={"font_size": 13},
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=BORDER)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=BORDER)
    if height:
        fig.update_layout(height=height)
    return fig
