"""Shared UI helpers for the Atlas Journal Streamlit app."""

from __future__ import annotations

from contextlib import contextmanager

import streamlit as st

_CSS = """
<style>
:root {
  --aj-bg: #0f172a;
  --aj-surface: rgba(30, 41, 59, 0.92);
  --aj-surface-strong: rgba(15, 23, 42, 0.96);
  --aj-border: rgba(148, 163, 184, 0.16);
  --aj-primary: #38bdf8;
  --aj-text: #e2e8f0;
  --aj-muted: #94a3b8;
  --aj-shadow: 0 24px 60px -35px rgba(56, 189, 248, 0.55);
  --aj-radius: 1.5rem;
  --aj-spacing: 1.25rem;
}
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at top, rgba(56, 189, 248, 0.12), transparent 46%), var(--aj-bg);
  color: var(--aj-text);
}
[data-testid="stHeader"] {
  background: transparent;
}
[data-testid="stSidebar"] > div:first-child {
  background: var(--aj-surface-strong);
  border-right: 1px solid var(--aj-border);
}
.aj-card {
  background: linear-gradient(155deg, var(--aj-surface), var(--aj-surface-strong));
  border-radius: var(--aj-radius);
  padding: var(--aj-spacing);
  border: 1px solid var(--aj-border);
  box-shadow: var(--aj-shadow);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.aj-card h2 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: var(--aj-text);
}
.aj-card p {
  color: var(--aj-muted);
  font-size: 0.95rem;
  margin: 0;
}
.aj-metric {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  color: var(--aj-primary);
}
.aj-page-header {
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px dashed var(--aj-border);
}
.aj-page-header h1 {
  font-size: 2rem;
  margin: 0 0 0.35rem;
  font-weight: 700;
}
.aj-page-header p {
  margin: 0;
  color: var(--aj-muted);
  max-width: 720px;
}
</style>
"""


def inject_global_css() -> None:
    """Apply once-per-session CSS overrides for the dark Atlas aesthetic."""
    if st.session_state.get("_aj_css_injected"):
        return
    st.markdown(_CSS, unsafe_allow_html=True)
    st.session_state["_aj_css_injected"] = True


def page_header(title: str, subtitle: str | None = None) -> None:
    """Renders a consistent page header."""
    inject_global_css()
    st.markdown(
        f"""
        <div class=\"aj-page-header\">
            <h1>{title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def card(title: str, subtitle: str | None = None):
    """Reusable card wrapper with consistent styling."""
    inject_global_css()
    container = st.container()
    container.markdown(
        f"""
        <div class=\"aj-card\">
            <div>
                <h2>{title}</h2>
                {f'<p>{subtitle}</p>' if subtitle else ''}
            </div>
        """,
        unsafe_allow_html=True,
    )
    body = container.container()
    try:
        yield body
    finally:
        container.markdown("</div>", unsafe_allow_html=True)


def spaced_columns(weights: tuple[int, ...] | list[int], gap: str = "large"):
    """Convenience helper to create evenly spaced columns."""
    inject_global_css()
    return st.columns(weights, gap=gap)
