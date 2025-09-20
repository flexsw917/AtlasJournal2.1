"""Import page placeholder for Atlas Journal."""

from __future__ import annotations

import streamlit as st

from utils.ui import card, page_header, spaced_columns

page_header("Import", "Upload broker exports to seed your Atlas Journal workspace.")

uploaded_file = st.file_uploader(
    "Drop a CSV or Excel trade export",
    type=["csv", "xlsx"],
    help="Parsing comes next—today we're focused on layout.",
)

preview_col, errors_col = spaced_columns([1, 1])

with preview_col:
    with card("Preview", "Quick glance at detected trades.") as preview:
        if uploaded_file:
            preview.info("Preview rendering will appear here once parsing is implemented.")
        else:
            preview.markdown("No file uploaded.")

with errors_col:
    with card("Errors", "Validation notices during import.") as errors:
        if uploaded_file:
            errors.warning("Any parsing hiccups will be listed here.")
        else:
            errors.markdown("No file uploaded.")

# TODO: Parse the uploaded file and stage trades for review before committing to storage.

st.button("Commit to Database", type="primary", use_container_width=True, disabled=True)
