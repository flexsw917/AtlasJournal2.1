"""Trades table placeholder."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.ui import card, page_header, spaced_columns

page_header("Trades", "Filter, inspect, and tag executions once data is live.")

filters = spaced_columns([1, 1, 1])

with filters[0]:
    date_range = st.date_input(
        "Date range",
        value=(
            pd.to_datetime("2024-01-02").date(),
            pd.to_datetime("2024-01-31").date(),
        ),
    )
with filters[1]:
    selected_symbols = st.multiselect(
        "Symbols",
        options=["AAPL", "MSFT", "TSLA", "NVDA", "SPY"],
        default=["AAPL", "MSFT"],
    )
with filters[2]:
    trade_types = st.multiselect(
        "Trade type",
        options=["Long", "Short", "Options"],
        default=["Long"],
    )

# TODO: Wire filters into the eventual trades dataset.

trades = pd.DataFrame(
    [
        ("2024-01-02", "AAPL", "Long", 100, 192.34, 145.00),
        ("2024-01-05", "MSFT", "Long", 50, 376.11, 210.00),
        ("2024-01-09", "TSLA", "Short", 20, 248.03, -85.00),
        ("2024-01-15", "NVDA", "Long", 15, 506.47, 364.00),
        ("2024-01-22", "SPY", "Long", 25, 475.62, 42.00),
    ],
    columns=["Date", "Symbol", "Side", "Quantity", "Price", "P/L"],
)

with card("Recent trades", "Static snapshot until live data arrives.") as trades_card:
    trades_card.dataframe(trades, use_container_width=True, hide_index=True)
    trades_card.caption("Visual refinements and tagging hooks will connect once the dataset is persisted.")
