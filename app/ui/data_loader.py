from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Dict

from app.core.config import AppConfig
from app.data.loader import load_from_yf, load_from_csv, LoadConfig


@st.cache_data(show_spinner=True)
def load_data(config: AppConfig) -> Dict[str, pd.DataFrame]:
    """Load stock data from yfinance or CSV file."""
    if config.data_source == "yfinance":
        return load_from_yf(config.tickers, LoadConfig(period_years=config.years))
    else:
        if config.uploaded_file is None:
            return {}
        df = load_from_csv(config.uploaded_file.read())
        t = config.tickers[0] if config.tickers else "CSV"
        return {t: df}

