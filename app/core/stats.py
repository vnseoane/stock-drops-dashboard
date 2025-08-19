from __future__ import annotations
import pandas as pd


def align_by_period(dfs: dict[str, pd.DataFrame], freq: str = "M") -> pd.DataFrame:
    out = []
    for tkr, df in dfs.items():
        if not isinstance(df.index, pd.DatetimeIndex) and 'Date' in df.columns:
            df = df.set_index(pd.to_datetime(df['Date']))
        s = df['Adj Close'].resample(freq).last().rename(tkr)
        out.append(s)
    return pd.concat(out, axis=1).dropna(how='all')
