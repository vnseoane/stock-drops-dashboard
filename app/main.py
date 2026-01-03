from __future__ import annotations

# --- bootstrap sys.path to import app.* ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --------------------------------------------------------

import streamlit as st

from app.ui.sidebar import render_sidebar
from app.ui.data_loader import load_data
from app.core.services import DataService
from app.ui.tabs import (
    render_overview_tab,
    render_distribution_tab,
    render_seasonality_tab,
    render_events_tab
)


def setup_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(page_title="Stock Drops Dashboard", layout="wide")
    st.title("📉 Monthly Stock Drops Analyzer")
    st.caption("Uses adjusted prices and end-of-period for returns. Handles multiple tickers and allows CSV upload.")


def main() -> None:
    """Main application entry point."""
    setup_page()
    
    # Get configuration from sidebar
    config = render_sidebar()
    
    # Load data
    raw_data = load_data(config)
    if not raw_data:
        st.warning("Load data from yfinance or upload a CSV to continue.")
        st.stop()
    
    # Initialize data service
    service = DataService(raw_data, config.return_config)
    
    # Create tabs
    tabs = st.tabs(["Overview", "Distribution", "Seasonality", "Events"])
    
    # Render tabs
    with tabs[0]:
        render_overview_tab(raw_data, service, config)
    
    with tabs[1]:
        render_distribution_tab(raw_data, service, config)
    
    with tabs[2]:
        render_seasonality_tab(raw_data, service, config)
    
    with tabs[3]:
        render_events_tab(raw_data, service, config)


if __name__ == "__main__":
    main()
