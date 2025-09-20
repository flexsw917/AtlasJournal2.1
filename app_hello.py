"""Streamlit starter app for Atlas Journal."""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Atlas Journal — Hello", page_icon="📓")
st.title("Atlas Journal — Hello")

entries = pd.DataFrame(
    {
        "Day": pd.date_range("2024-01-01", periods=7, freq="D"),
        "Entries": [1, 2, 3, 5, 8, 13, 21],
    }
)

chart = px.line(
    entries,
    x="Day",
    y="Entries",
    markers=True,
    title="Momentum of journal entries",
)
chart.update_layout(margin=dict(l=0, r=0, t=60, b=0))

st.plotly_chart(chart, use_container_width=True)

st.info("Next steps: scaffold pages.")
