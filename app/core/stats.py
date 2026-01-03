from __future__ import annotations
import pandas as pd


def align_by_period(dfs: dict[str, pd.DataFrame], freq: str = "M") -> pd.DataFrame:
    """
    Align multiple price DataFrames by period (M/W) and return a panel
    with one column per ticker. Uses 'Adj Close' and the last value of the period.
    """
    out = []
    for tkr, df in dfs.items():
        if not isinstance(df.index, pd.DatetimeIndex) and "Date" in df.columns:
            df = df.set_index(pd.to_datetime(df["Date"]))
        s = df["Adj Close"].resample(freq).last().rename(tkr)
        out.append(s)
    if not out:
        return pd.DataFrame()
    return pd.concat(out, axis=1).dropna(how="all")


def pct_above_threshold(ret_df: pd.DataFrame, threshold: float) -> float:
    """
    Percentage of periods with return >= threshold.
    - ret_df: DataFrame with 'ret' column (period returns, e.g. monthly)
    - threshold: threshold as proportion (e.g.: -0.08 for -8%)
    Returns a float between 0.0 and 1.0
    """
    if ret_df is None or ret_df.empty or "ret" not in ret_df.columns:
        return 0.0
    return float((ret_df["ret"] >= threshold).mean())
