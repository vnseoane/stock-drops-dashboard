# app/viz/plots.py
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# -----------------------
# Precio + línea de pico
# -----------------------
def price_with_drawdown(dd_df: pd.DataFrame, title: str = "") -> go.Figure:
    """
    Dibuja precio ajustado + línea de pico (Peak).
    Espera un DataFrame indexado por fecha con columnas:
      - 'Adj Close' (precio ajustado)
      - 'Peak' (máximo acumulado, opcional)
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dd_df.index,
            y=dd_df["Adj Close"],
            name="Adj Close",
            mode="lines",
        )
    )
    if "Peak" in dd_df.columns:
        fig.add_trace(
            go.Scatter(
                x=dd_df.index,
                y=dd_df["Peak"],
                name="Peak",
                mode="lines",
            )
        )
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Precio",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


# -----------------------
# Área de drawdown
# -----------------------
def drawdown_area(dd_df: pd.DataFrame, title: str = "Drawdown acumulado") -> go.Figure:
    """
    Dibuja el drawdown acumulado (columna 'dd') en % y eje [min..0].
    Espera DataFrame indexado por fecha con columna 'dd' (proporción negativa).
    """
    min_dd = float(dd_df["dd"].min()) if not dd_df["dd"].empty else -0.01
    y_min = min(min_dd * 1.10, -0.05)

    fig = go.Figure()
    fig.add_hline(y=0, line_width=1, line_dash="dot", opacity=0.6)
    fig.add_trace(
        go.Scatter(
            x=dd_df.index,
            y=dd_df["dd"],
            name="Drawdown",
            fill="tozeroy",
            mode="lines",
            hovertemplate="%{x|%Y-%m}<br>DD: %{y:.2%}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Drawdown",
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_yaxes(tickformat=".0%", range=[y_min, 0])
    return fig


# ----------------------------------------
# Barras de retornos mensuales con umbral
# ----------------------------------------
def monthly_returns_bar(
    ret_df: pd.DataFrame,
    title: str = "Retornos mensuales",
    threshold: float | None = None,
    default_color: str = "lightslategray",
    hit_color: str = "crimson",
) -> go.Figure:
    """
    Barras de retorno del período (columna 'ret').
    Si threshold (proporción, ej. -0.08) está definido:
      - pinta en rojo las barras <= threshold
      - dibuja una línea horizontal en el umbral
    """
    df = ret_df.reset_index().rename(columns={ret_df.index.name or "index": "Date"})

    if threshold is not None:
        colors = [hit_color if v <= threshold else default_color for v in df["ret"]]
        subtitle = f"{title} · Umbral: {threshold:.0%}"
    else:
        colors = [default_color] * len(df)
        subtitle = title

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["ret"],
            marker=dict(color=colors),
            name="Retorno mensual",
            hovertemplate="%{x|%Y-%m}<br>Retorno: %{y:.2%}<extra></extra>",
        )
    )

    if threshold is not None:
        fig.add_hline(y=threshold, line_color=hit_color, line_dash="dash", opacity=0.85)

    fig.update_layout(
        title=subtitle,
        xaxis_title="Fecha",
        yaxis_title="Retorno mensual",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )
    fig.update_yaxes(tickformat=".0%")
    return fig


# ----------------------------------------
# Histograma de retornos con línea umbral
# ----------------------------------------
def hist_returns(
    ret_df: pd.DataFrame,
    title: str = "Distribución de retornos",
    threshold: float | None = None,
) -> go.Figure:
    fig = px.histogram(ret_df, x="ret", nbins=40)
    fig.update_traces(hovertemplate="Retorno: %{x:.2%}<br>Frecuencia: %{y}<extra></extra>")
    if threshold is not None:
        fig.add_vline(x=threshold, line_color="crimson", line_dash="dash", opacity=0.85)
        title = f"{title} · Umbral: {threshold:.0%}"
    fig.update_layout(
        title=title,
        xaxis_title="Retorno",
        yaxis_title="Frecuencia",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(tickformat=".0%")
    return fig


# ----------------------------------------
# Heatmap de estacionalidad (robusto Cloud)
# ----------------------------------------
def heatmap_calendar(pivot: pd.DataFrame, title: str = "Año × Mes") -> go.Figure:
    """
    Heatmap de estacionalidad robusto para Streamlit Cloud.
    - Hover en porcentaje
    - Colorbar en %
    - Rango simétrico [-max_abs, +max_abs] centrado en 0
    - Meses como categorías '1'..'12'
    """
    if pivot is None or pivot.empty:
        return go.Figure()

    df = pivot.copy()
    # asegurar meses como ints
    try:
        df.columns = [int(c) for c in df.columns]
    except Exception:
        df.columns = pd.to_numeric(df.columns, errors="coerce").astype("Int64")

    df = df.reindex(sorted([c for c in df.columns if pd.notna(c)]), axis=1)
    df = df.replace([np.inf, -np.inf], np.nan)

    Z = df.values.astype(float)
    finite = np.isfinite(Z)
    max_abs = np.nanmax(np.abs(Z[finite])) if finite.any() else 0.01
    zmin, zmax = -max_abs, +max_abs

    x = [str(m) for m in df.columns.tolist()]  # meses 1..12 como categorías
    y = df.index.astype(int if df.index.inferred_type == "integer" else str).tolist()

    fig = go.Figure(
        data=go.Heatmap(
            x=x,
            y=y,
            z=Z,
            colorscale="RdBu",
            reversescale=True,
            zmin=zmin,
            zmax=zmax,
            colorbar=dict(title="Retorno", tickformat=".0%"),
        )
    )

    fig.update_traces(hovertemplate="Año: %{y}<br>Mes: %{x}<br>Retorno: %{z:.2%}<extra></extra>")
    fig.update_layout(
        title=title,
        margin=dict(l=40, r=20, t=60, b=40),
        xaxis=dict(title="Mes", type="category"),
        yaxis=dict(title="Año", autorange="reversed"),
    )
    return fig


# ----------------------------------------
# Barras: conteo de períodos ≤ umbral por ticker
# ----------------------------------------
def bar_threshold_counts(counts: pd.Series, title: str = "Meses ≤ umbral") -> go.Figure:
    """
    Recibe una Series con índice = ticker y valores = conteo de períodos ≤ umbral.
    """
    df = counts.rename("Meses").reset_index().rename(columns={"index": "Ticker"})
    fig = px.bar(df, x="Ticker", y="Meses", title=title)
    fig.update_layout(
        xaxis_title="Ticker",
        yaxis_title="Meses",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig
