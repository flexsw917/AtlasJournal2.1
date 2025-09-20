"""Dashboard overview for Atlas Journal."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ui import card, page_header, spaced_columns

page_header("Dashboard", "High-level metrics to keep your finger on the pulse.")

kpis = [
    ("Total P/L", "$0.00", "Awaiting imported trades."),
    ("Win Rate", "0%", "Need completed trades."),
    ("Avg Win / Loss", "$0.00", "Averages will populate soon."),
    ("Trades Count", "0", "Import executions to unlock."),
]

for column, (title, value, subtitle) in zip(spaced_columns([1, 1, 1, 1]), kpis):
    with column:
        with card(title, subtitle) as card_body:
            card_body.markdown(f"<p class='aj-metric'>{value}</p>", unsafe_allow_html=True)

# TODO: Replace mocked metrics with calculations fed by the import pipeline.

performance = pd.DataFrame(
    {
        "Date": pd.date_range("2024-01-01", periods=14, freq="D"),
        "Equity": [10000, 10080, 10010, 10120, 10180, 10260, 10190, 10230, 10290, 10360, 10310, 10470, 10510, 10580],
    }
)

chart = px.line(
    performance,
    x="Date",
    y="Equity",
    markers=True,
    title="Stub equity curve",
)
chart.update_layout(margin=dict(l=0, r=0, t=46, b=8), height=280, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
chart.update_traces(line_color="#38bdf8")

with card("Equity curve", "Placeholder data until the journal is connected.") as chart_card:
    chart_card.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

with card("Bring in your history", "Import trades to unlock analytics across the app.") as cta:
    cta.write("Once we accept trade files, this module will summarize what changed during the import.")
    if cta.button("Import your first trades", type="primary"):
        st.switch_page("pages/02_📥_Import.py")
    cta.caption("We will wire the button into the import workflow when the parser is ready.")
