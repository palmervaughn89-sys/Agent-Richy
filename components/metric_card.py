"""Metric card component — professional stat display."""

import streamlit as st
from config import COLORS


def render_metric_card(label: str, value: str, delta: str = "",
                       delta_positive: bool = True, icon: str = "") -> None:
    """Render a premium styled metric card.

    Args:
        label: Metric label text.
        value: Main value to display.
        delta: Optional delta/change text.
        delta_positive: Whether delta is positive (green) or negative (red).
        icon: Optional emoji icon.
    """
    delta_class = "positive" if delta_positive else "negative"
    delta_html = f'<div class="stat-delta {delta_class}">{delta}</div>' if delta else ""
    icon_html = f'<span style="font-size: 1.5rem;">{icon}</span> ' if icon else ""

    st.markdown(f"""
    <div class="stat-card">
        {icon_html}
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards using st.columns.

    Args:
        metrics: List of dicts with keys: label, value, delta (optional),
                 delta_positive (optional), icon (optional).
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            render_metric_card(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta", ""),
                delta_positive=m.get("delta_positive", True),
                icon=m.get("icon", ""),
            )
