from __future__ import annotations

import pandas as pd
from typing import Dict
from functools import lru_cache

from app.core.returns import ReturnConfig, to_period_returns, count_threshold_breaches
from app.core.drawdown import compute_drawdown


class DataService:
    """Service class for data processing operations with caching."""
    
    def __init__(self, raw_data: Dict[str, pd.DataFrame], config: ReturnConfig):
        self.raw_data = raw_data
        self.config = config
        self._returns_cache: Dict[str, pd.DataFrame] = {}
        self._drawdown_cache: Dict[str, pd.DataFrame] = {}
    
    def get_returns(self, ticker: str) -> pd.DataFrame:
        """Get period returns for a ticker, with caching."""
        if ticker not in self._returns_cache:
            df = self.raw_data[ticker]
            self._returns_cache[ticker] = to_period_returns(df, self.config)
        return self._returns_cache[ticker]
    
    def get_drawdown(self, ticker: str) -> pd.DataFrame:
        """Get drawdown data for a ticker, with caching."""
        if ticker not in self._drawdown_cache:
            df = self.raw_data[ticker]
            price_m = df['Adj Close'].resample(self.config.frequency).last()
            dd = compute_drawdown(price_m).rename(columns={"cum_max": "Peak"})
            self._drawdown_cache[ticker] = dd
        return self._drawdown_cache[ticker]
    
    def get_threshold_counts(self, threshold: float) -> Dict[str, int]:
        """Get threshold breach counts for all tickers."""
        counts = {}
        for ticker in self.raw_data.keys():
            ret = self.get_returns(ticker)
            counts[ticker] = count_threshold_breaches(ret, threshold)
        return counts
    
    def get_all_returns(self) -> Dict[str, pd.DataFrame]:
        """Get returns for all tickers."""
        return {ticker: self.get_returns(ticker) for ticker in self.raw_data.keys()}

