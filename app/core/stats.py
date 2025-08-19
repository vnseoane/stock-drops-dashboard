from __future__ import annotations
import pandas as pd


def align_by_period(dfs: dict[str, pd.DataFrame], freq: str = "M") -> pd.DataFrame:
    """
    Alinea varios DataFrames de precios por período (M/W) y devuelve un panel
    con una columna por ticker. Usa 'Adj Close' y el último valor del período.
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
    Porcentaje de períodos con retorno >= umbral.
    - ret_df: DataFrame con columna 'ret' (retornos del período, p.ej. mensual)
    - threshold: umbral en proporción (ej: -0.08 para -8%)
    Devuelve un float entre 0.0 y 1.0
    """
    if ret_df is None or ret_df.empty or "ret" not in ret_df.columns:
        return 0.0
    return float((ret_df["ret"] >= threshold).mean())
