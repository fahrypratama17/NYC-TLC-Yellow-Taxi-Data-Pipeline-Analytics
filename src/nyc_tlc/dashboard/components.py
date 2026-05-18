"""Reusable UI components — header, KPI cards, section titles, insight callouts.

Every page calls `inject_css()` once, then composes the page from these
helpers so the whole dashboard shares one visual language.
"""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
  /* ── Layout ─────────────────────────────────────── */
  .block-container { padding-top: 2.2rem; max-width: 1200px; }
  #MainMenu, footer { visibility: hidden; }

  /* ── Page header ────────────────────────────────── */
  .page-header {
    border-left: 5px solid #2C6BAA;
    padding: 0.2rem 0 0.2rem 1rem;
    margin-bottom: 1.4rem;
  }
  .page-header .title {
    font-size: 1.7rem; font-weight: 700; color: #1A2A3A; line-height: 1.2;
  }
  .page-header .subtitle {
    font-size: 0.98rem; color: #5B6B7B; margin-top: 0.25rem;
  }

  /* ── Section header ─────────────────────────────── */
  .section { margin: 1.9rem 0 0.7rem 0; }
  .section .s-title {
    font-size: 1.15rem; font-weight: 700; color: #1A2A3A;
  }
  .section .s-desc {
    font-size: 0.9rem; color: #5B6B7B; margin-top: 0.15rem;
  }
  .section-rule {
    border: 0; border-top: 1px solid #E3E7EC; margin: 0.45rem 0 0 0;
  }

  /* ── KPI / answer cards ─────────────────────────── */
  .card-row { display: flex; gap: 0.85rem; flex-wrap: wrap; margin: 0.4rem 0; }
  .card {
    flex: 1 1 0; min-width: 170px;
    background: #FFFFFF; border: 1px solid #E3E7EC; border-radius: 10px;
    padding: 0.95rem 1.05rem;
    box-shadow: 0 1px 2px rgba(16,24,40,0.04);
  }
  .card .c-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase; color: #8A97A4;
  }
  .card .c-value {
    font-size: 1.55rem; font-weight: 700; color: #1A2A3A;
    margin-top: 0.2rem; line-height: 1.15;
  }
  .card .c-sub { font-size: 0.82rem; color: #5B6B7B; margin-top: 0.18rem; }
  .card.accent { border-top: 3px solid #2C6BAA; }

  /* ── Insight callout ────────────────────────────── */
  .insight {
    background: #EEF4FA; border-left: 4px solid #2C6BAA;
    border-radius: 6px; padding: 0.7rem 0.95rem; margin: 0.7rem 0 0.2rem 0;
    font-size: 0.92rem; color: #243B52;
  }
  .insight b { color: #1A2A3A; }

  /* ── Sidebar brand ──────────────────────────────── */
  .sb-brand {
    padding: 0.2rem 0 0.6rem 0; border-bottom: 1px solid #E3E7EC;
    margin-bottom: 0.6rem;
  }
  .sb-brand .b-name { font-weight: 700; color: #1A2A3A; font-size: 1.0rem; }
  .sb-brand .b-meta { font-size: 0.78rem; color: #8A97A4; margin-top: 0.1rem; }
</style>
"""


def _esc(text: str) -> str:
    """Escape '$' so Streamlit does not render it as LaTeX math."""
    return str(text).replace("$", "&#36;")


def inject_css() -> None:
    """Inject the shared stylesheet. Safe to call once per page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='page-header'>"
        f"<div class='title'>{_esc(title)}</div>"
        f"<div class='subtitle'>{_esc(subtitle)}</div></div>",
        unsafe_allow_html=True,
    )


def section(title: str, description: str = "") -> None:
    desc = f"<div class='s-desc'>{_esc(description)}</div>" if description else ""
    st.markdown(
        f"<div class='section'><div class='s-title'>{_esc(title)}</div>{desc}</div>"
        f"<hr class='section-rule'/>",
        unsafe_allow_html=True,
    )


def cards(items: list[tuple[str, str, str]], accent: bool = False) -> None:
    """Render a row of cards. Each item is (label, value, sub)."""
    cls = "card accent" if accent else "card"
    blocks = "".join(
        f"<div class='{cls}'><div class='c-label'>{_esc(label)}</div>"
        f"<div class='c-value'>{_esc(value)}</div>"
        f"<div class='c-sub'>{_esc(sub)}</div></div>"
        for label, value, sub in items
    )
    st.markdown(f"<div class='card-row'>{blocks}</div>", unsafe_allow_html=True)


def insight(text: str) -> None:
    """A plain-language 'what this means' callout under a chart."""
    st.markdown(
        f"<div class='insight'><b>What this means.</b> {_esc(text)}</div>",
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    with st.sidebar:
        st.markdown(
            "<div class='sb-brand'>"
            "<div class='b-name'>NYC Yellow Taxi Analytics</div>"
            "<div class='b-meta'>Yellow Taxi · Jan–Jun 2025</div></div>",
            unsafe_allow_html=True,
        )
