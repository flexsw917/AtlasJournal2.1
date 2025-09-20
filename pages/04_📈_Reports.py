"""Reports tab placeholders for Atlas Journal."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ui import card, page_header

page_header("Reports", "Dive deeper into performance once analytics are wired up.")

performance_tab, tags_tab = st.tabs(["Performance", "Tags"])

with performance_tab:
    with card("Performance overview", "Equity and drawdown trends will render here.") as perf_card:
        perf_data = pd.DataFrame(
            {
                "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "Net P/L": [320, 540, -120, 680, 420, 890],
            }
        )
        perf_fig = px.line(perf_data, x="Month", y="Net P/L", markers=True)
        perf_fig.update_layout(margin=dict(l=0, r=0, t=40, b=10), height=280, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        perf_fig.update_traces(line_color="#38bdf8")
        perf_card.plotly_chart(perf_fig, use_container_width=True, config={"displayModeBar": False})
        perf_card.caption("Detailed analytics will layer in once the reporting queries hook into stored trades.")

with tags_tab:
    with card("Tag insights", "Monitor themes and notes once tagging is available.") as tags_card:
        tag_data = pd.DataFrame(
            {
                "Tag": ["Breakout", "Pullback", "Earnings", "Swing", "Scalp"],
                "Count": [5, 3, 2, 4, 1],
            }
        )
        tag_fig = px.bar(tag_data, x="Tag", y="Count", text="Count")
        tag_fig.update_traces(marker_color="#22d3ee", textposition="outside")
        tag_fig.update_layout(margin=dict(l=0, r=0, t=40, b=10), height=280, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        tags_card.plotly_chart(tag_fig, use_container_width=True, config={"displayModeBar": False})
        tags_card.caption("As tagging data rolls in, we can branch into per-tag P/L and habit metrics.")

# TODO: Replace placeholder aggregates with analytics backed by the stored trade history.
