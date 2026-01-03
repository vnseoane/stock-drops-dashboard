from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class LoadConfig:
    period_years: int = 20


def load_from_yf(tickers: List[str], cfg: LoadConfig) -> Dict[str, pd.DataFrame]:
    """Download adjusted prices by ticker from yfinance."""
    out: Dict[str, pd.DataFrame] = {}
    period = f"{cfg.period_years}y"
    for t in tickers:
        t = t.strip().upper()
        if not t:
            continue
        hist = yf.Ticker(t).history(period=period, auto_adjust=False)
        if hist.empty:
            continue
        hist = hist.rename_axis("Date").reset_index().set_index("Date")
        out[t] = hist
    return out


def load_from_csv(file: bytes) -> pd.DataFrame:
    """Read a CSV uploaded by the user and return DataFrame with datetime index."""
    import io
    df = pd.read_csv(io.BytesIO(file))
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    return df
