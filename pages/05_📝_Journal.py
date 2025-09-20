"""Journal page placeholder."""

from __future__ import annotations

import streamlit as st

from utils.ui import card, page_header

page_header("Journal", "Capture lessons learned so you can refine your playbook.")

with card("Write a new note", "Markdown supported once entries persist.") as compose:
    note_value = compose.text_area(
        "Journal entry",
        value="",
        height=220,
        placeholder="Log your trade review, mindset check, or process tweak...",
    )
    compose.button("Save note", type="primary", disabled=True)

# TODO: Persist journal entries and surface the latest notes below.

with card("History", "Your most recent reflections will appear here.") as history:
    history.info("No journal entries yet.")
