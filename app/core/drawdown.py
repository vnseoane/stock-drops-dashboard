from __future__ import annotations
import pandas as pd


def compute_drawdown(series: pd.Series) -> pd.DataFrame:
    s = series.dropna().astype(float)
    cum_max = s.cummax()
    dd = (s / cum_max) - 1.0
    return pd.DataFrame({'Adj Close': s, 'cum_max': cum_max, 'dd': dd})


def max_drawdown(df_dd: pd.DataFrame) -> float:
    return float(df_dd['dd'].min())


def drawdown_duration(df_dd: pd.DataFrame) -> int:
    below = df_dd['dd'] < 0
    groups = (below != below.shift()).cumsum()
    streaks = below.groupby(groups).cumsum() * below
    return int(streaks.iloc[-1])
