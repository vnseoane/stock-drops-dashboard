from __future__ import annotations

# --- bootstrap del sys.path para poder importar app.* ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --------------------------------------------------------

import streamlit as st
import pandas as pd
from typing import List, Dict

# Imports del proyecto
from app.data.loader import load_from_yf, load_from_csv, LoadConfig
from app.core.returns import (
    to_period_returns, ReturnConfig, count_threshold_breaches, max_red_streak,
    top_n_worst, seasonality_table, monthly_stats
)
from app.core.drawdown import compute_drawdown
from app.core.stats import align_by_period, pct_above_threshold
from app.viz.plots import (
    price_with_drawdown, drawdown_area, hist_returns, heatmap_calendar,
    monthly_returns_bar
)
from app.ui.components import kpi_row, data_table

# Config
st.set_page_config(page_title="Stock Drops Dashboard", layout="wide")
st.title("📉 Analizador de caídas mensuales de acciones")
st.caption("Usa precios ajustados y fin de período para retornos. Maneja múltiples tickers y permite subir CSV.")

# -------- Sidebar --------
with st.sidebar:
    st.header("Parámetros")
    tickers_raw = st.text_input("Tickers (separados por coma)", value="SPY")
    tickers: List[str] = [t.strip().upper() for t in tickers_raw.split(',') if t.strip()]
    years = st.slider("Años de historia", 5, 30, 20)

    # Frecuencia fija mensual
    freq = "M"
    st.caption("Frecuencia fija: Mensual")

    threshold_pct = st.slider("Umbral de caída (%)", -30, 0, -5)
    threshold = threshold_pct / 100.0

    st.divider()
    st.subheader("Fuente de datos")
    src = st.radio("Fuente", options=["yfinance", "CSV"], horizontal=True)
    uploaded = st.file_uploader("Subí un CSV con OHLCV", type=["csv"]) if src == "CSV" else None

# -------- Carga de datos --------
@st.cache_data(show_spinner=True)
def _load_data(tickers: List[str], years: int, src: str, uploaded) -> Dict[str, pd.DataFrame]:
    if src == "yfinance":
        return load_from_yf(tickers, LoadConfig(period_years=years))
    else:
        if uploaded is None:
            return {}
        df = load_from_csv(uploaded.read())
        t = tickers[0] if tickers else "CSV"
        return {t: df}

raw: Dict[str, pd.DataFrame] = _load_data(tickers, years, src, uploaded)
if not raw:
    st.warning("Cargá datos desde yfinance o subí un CSV para continuar.")
    st.stop()

cfg = ReturnConfig(frequency=freq)
tabs = st.tabs(["Overview", "Distribución", "Estacionalidad", "Eventos"])

# -------- Overview --------
with tabs[0]:
    st.subheader("Overview")
    counts = {}
    kpi_common = {"Tickers": str(len(raw)), "Frecuencia": cfg.frequency, "Umbral": f"{threshold_pct}%"}

    first_ticker = list(raw.keys())[0]
    df0 = raw[first_ticker]

    # Retornos del período (mensual) y drawdown acumulado sobre precio ajustado
    ret0 = to_period_returns(df0, cfg)
    price_m = df0['Adj Close'].resample(cfg.frequency).last()
    dd0 = compute_drawdown(price_m).rename(columns={"cum_max": "Peak"})

    counts[first_ticker] = count_threshold_breaches(ret0, threshold)
    pct_above = pct_above_threshold(ret0, threshold)  # % de meses con retorno >= umbral

    # --- Texto coloreado si ≥90% ---
    pct_text = f"{pct_above:.0%}"
    if pct_above >= 0.90:
        pct_colored = f"<span style='color:limegreen; font-weight:700'>{pct_text}</span>"
    else:
        pct_colored = pct_text

    kpis = {
        **kpi_common,
        "Meses analizados": f"{ret0.shape[0]}",
        "Meses ≤ umbral": f"{counts[first_ticker]}",
        "% veces ≥ umbral": pct_colored,                       # ← renderiza color si ≥90%
        "Peor período (mes)": f"{ret0['ret'].min():.2%}",
        "Max Drawdown (acum.)": f"{dd0['dd'].min():.2%}",
        "Longest red-streak": f"{max_red_streak(ret0)}",
    }
    kpi_row(kpis)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(price_with_drawdown(dd0, title=f"{first_ticker} — Precio y pico"),
                        use_container_width=True)
    with c2:
        st.plotly_chart(drawdown_area(dd0, title=f"{first_ticker} — Drawdown acumulado"),
                        use_container_width=True)

    r1, r2 = st.columns(2)
    with r1:
        st.plotly_chart(
            monthly_returns_bar(ret0, title=f"Retornos mensuales — {first_ticker}", threshold=threshold),
            use_container_width=True
        )
    with r2:
        st.caption("El drawdown es acumulado desde el último pico. Las barras muestran el retorno de cada mes; "
                   "las que caen por debajo del umbral se pintan en rojo.")

    # Comparación multi-ticker (conteo ≤ umbral)
    if len(raw) > 1:
        for t, df in raw.items():
            if t == first_ticker:
                continue
            ret = to_period_returns(df, cfg)
            counts[t] = count_threshold_breaches(ret, threshold)
        st.plotly_chart(
            bar_threshold_counts(pd.Series(counts), title="Períodos ≤ umbral por ticker"),
            use_container_width=True
        )

# -------- Distribución --------
with tabs[1]:
    st.subheader("Distribución")
    t = st.selectbox("Ticker", options=list(raw.keys()), index=0, key="dist_t")
    ret = to_period_returns(raw[t], cfg)
    st.plotly_chart(
        hist_returns(ret, title=f"Distribución retornos — {t}", threshold=threshold),
        use_container_width=True
    )

# -------- Estacionalidad --------
with tabs[2]:
    st.subheader("Estacionalidad")
    t = st.selectbox("Ticker", options=list(raw.keys()), index=0, key="season_t")
    ret = to_period_returns(raw[t], cfg)
    pivot = seasonality_table(ret)
    st.plotly_chart(heatmap_calendar(pivot, title=f"Año×Mes — {t}"), use_container_width=True)

# -------- Eventos --------
with tabs[3]:
    st.subheader("Eventos (períodos ≤ umbral)")
    t = st.selectbox("Ticker", options=list(raw.keys()), index=0, key="events_t")
    ret = to_period_returns(raw[t], cfg)
    events = ret[ret['ret'] <= threshold].copy()
    events['ret_pct'] = (events['ret'] * 100).round(2)
    data_table(events[['ret_pct']].rename(columns={'ret_pct': 'Retorno (%)'}))
    st.download_button(
        label="Descargar eventos CSV",
        data=events.to_csv().encode('utf-8'),
        file_name=f"{t}_eventos_threshold_{int(threshold_pct)}.csv",
        mime="text/csv",
    )
