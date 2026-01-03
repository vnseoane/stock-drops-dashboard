from __future__ import annotations
from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class ReturnConfig:
    frequency: str = "M"  # "M" monthly, "W" weekly
    min_history_months: int = 12


def to_period_returns(df: pd.DataFrame, cfg: ReturnConfig) -> pd.DataFrame:
    if 'Adj Close' not in df.columns:
        raise ValueError("Missing 'Adj Close' column")
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'Date' in df.columns:
            df = df.set_index(pd.to_datetime(df['Date']))
        else:
            raise ValueError("Datetime index or 'Date' column required")
    px = df[['Adj Close']].resample(cfg.frequency).last().dropna()
    px['ret'] = px['Adj Close'].pct_change()
    return px.dropna()


def count_threshold_breaches(ret_df: pd.DataFrame, threshold: float) -> int:
    return int((ret_df['ret'] <= threshold).sum())


def max_red_streak(ret_df: pd.DataFrame) -> int:
    neg = (ret_df['ret'] < 0).astype(int)
    gaps = (neg != neg.shift()).cumsum()
    streaks = neg.groupby(gaps).cumsum() * neg
    return int(streaks.max() or 0)


def top_n_worst(ret_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return ret_df.sort_values('ret').head(n).copy()


def seasonality_table(ret_df: pd.DataFrame) -> pd.DataFrame:
    df = ret_df.copy()
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    return df.pivot_table(values='ret', index='Year', columns='Month', aggfunc='mean')


def monthly_stats(ret_df: pd.DataFrame) -> dict[str, float]:
    s = ret_df['ret'].dropna()
    return {
        'mean': float(s.mean()),
        'median': float(s.median()),
        'std': float(s.std(ddof=1)),
        'skew': float(s.skew()),
        'kurt': float(s.kurtosis()),
        'count': int(s.shape[0]),
    }
