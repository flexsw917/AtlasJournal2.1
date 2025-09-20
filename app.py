"""Atlas Journal main entrypoint."""

import streamlit as st

from utils.ui import card, inject_global_css, page_header

st.set_page_config(
    page_title="Atlas Journal — Beginner MVP",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()
page_header(
    "Atlas Journal — Beginner MVP",
    "Monitor trading performance, capture insights, and grow a reflective practice.",
)

with card("Welcome aboard", "Use the sidebar to navigate between modules.") as welcome:
    welcome.write(
        "This starter focuses on layout and experience—data wiring comes next. "
        "Import your trades, review performance, and jot down thoughts as the "
        "core database layer solidifies."
    )
    welcome.caption(
        "Tip: Streamlit automatically saves widget state between reruns, so we can "
        "drop in persistence once the storage layer is ready."
    )

st.sidebar.header("Quick links")
st.sidebar.page_link("pages/01_🏠_Dashboard.py", label="Dashboard", icon="🏠")
st.sidebar.page_link("pages/02_📥_Import.py", label="Import", icon="📥")
st.sidebar.page_link("pages/03_📊_Trades.py", label="Trades", icon="📊")
st.sidebar.page_link("pages/04_📈_Reports.py", label="Reports", icon="📈")
st.sidebar.page_link("pages/05_📝_Journal.py", label="Journal", icon="📝")

# TODO: Populate sidebar summaries with live metrics once a data layer is in place.
