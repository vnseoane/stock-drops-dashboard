from __future__ import annotations

from typing import Protocol
import streamlit as st

from app.core.config import AppConfig
from app.core.services import DataService


class TabRenderer(Protocol):
    """Protocol for tab rendering functions."""
    
    def __call__(
        self,
        raw_data: dict[str, pd.DataFrame],
        service: DataService,
        config: AppConfig
    ) -> None:
        """Render a tab with the given data and configuration."""
        ...


def render_ticker_selector(
    tickers: list[str],
    key: str,
    label: str = "Ticker"
) -> str:
    """Render a ticker selector and return the selected ticker."""
    return st.selectbox(label, options=tickers, index=0, key=key)


def render_chart(fig, use_container_width: bool = True) -> None:
    """Render a Plotly chart with consistent settings."""
    st.plotly_chart(fig, use_container_width=use_container_width)

