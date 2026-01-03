from __future__ import annotations

import streamlit as st

from app.core.config import AppConfig


def render_sidebar() -> AppConfig:
    """
    Render sidebar and return application configuration.
    
    Returns:
        AppConfig with all user-selected parameters
    """
    with st.sidebar:
        st.header("Parameters")
        tickers_raw = st.text_input("Tickers (comma-separated)", value="SPY")
        tickers: list[str] = [t.strip().upper() for t in tickers_raw.split(',') if t.strip()]
        years = st.slider("Years of history", 5, 30, 20)

        # Fixed monthly frequency
        freq = "M"
        st.caption("Fixed frequency: Monthly")

        threshold_pct = st.slider("Drop threshold (%)", -30, 0, -5)
        threshold = threshold_pct / 100.0

        st.divider()
        st.subheader("Data source")
        src = st.radio("Source", options=["yfinance", "CSV"], horizontal=True)
        uploaded = st.file_uploader("Upload a CSV with OHLCV", type=["csv"]) if src == "CSV" else None

    return AppConfig(
        tickers=tickers,
        years=years,
        frequency=freq,
        threshold=threshold,
        data_source=src,
        uploaded_file=uploaded
    )

