# app/viz/plots.py
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# -----------------------
# Price + peak line
# -----------------------
def price_with_drawdown(dd_df: pd.DataFrame, title: str = "") -> go.Figure:
    """
    Draw adjusted price + peak line (Peak).
    Expects a date-indexed DataFrame with columns:
      - 'Adj Close' (adjusted price)
      - 'Peak' (accumulated maximum, optional)
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
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


# -----------------------
# Drawdown area
# -----------------------
def drawdown_area(dd_df: pd.DataFrame, title: str = "Accumulated drawdown") -> go.Figure:
    """
    Draw accumulated drawdown (column 'dd') in % and axis [min..0].
    Expects date-indexed DataFrame with 'dd' column (negative proportion).
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
        xaxis_title="Date",
        yaxis_title="Drawdown",
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_yaxes(tickformat=".0%", range=[y_min, 0])
    return fig


# ----------------------------------------
# Monthly returns bars with threshold
# ----------------------------------------
def monthly_returns_bar(
    ret_df: pd.DataFrame,
    title: str = "Monthly returns",
    threshold: float | None = None,
    default_color: str = "lightslategray",
    hit_color: str = "crimson",
) -> go.Figure:
    """
    Period return bars (column 'ret').
    If threshold (proportion, e.g. -0.08) is defined:
      - colors bars <= threshold in red
      - draws a horizontal line at the threshold
    """
    df = ret_df.reset_index().rename(columns={ret_df.index.name or "index": "Date"})

    if threshold is not None:
        colors = [hit_color if v <= threshold else default_color for v in df["ret"]]
        subtitle = f"{title} · Threshold: {threshold:.0%}"
    else:
        colors = [default_color] * len(df)
        subtitle = title

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["ret"],
            marker=dict(color=colors),
            name="Monthly return",
            hovertemplate="%{x|%Y-%m}<br>Return: %{y:.2%}<extra></extra>",
        )
    )

    if threshold is not None:
        fig.add_hline(y=threshold, line_color=hit_color, line_dash="dash", opacity=0.85)

    fig.update_layout(
        title=subtitle,
        xaxis_title="Date",
        yaxis_title="Monthly return",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )
    fig.update_yaxes(tickformat=".0%")
    return fig


# ----------------------------------------
# Returns histogram with threshold line
# ----------------------------------------
def hist_returns(
    ret_df: pd.DataFrame,
    title: str = "Return distribution",
    threshold: float | None = None,
) -> go.Figure:
    fig = px.histogram(ret_df, x="ret", nbins=40)
    fig.update_traces(hovertemplate="Return: %{x:.2%}<br>Frequency: %{y}<extra></extra>")
    if threshold is not None:
        fig.add_vline(x=threshold, line_color="crimson", line_dash="dash", opacity=0.85)
        title = f"{title} · Threshold: {threshold:.0%}"
    fig.update_layout(
        title=title,
        xaxis_title="Return",
        yaxis_title="Frequency",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(tickformat=".0%")
    return fig


# ----------------------------------------
# Seasonality heatmap (Cloud robust)
# ----------------------------------------
def heatmap_calendar(pivot: pd.DataFrame, title: str = "Year × Month") -> go.Figure:
    """
    Robust seasonality heatmap with red (bad) to green (good) colorscale.
    - Red for negative returns (bad months)
    - Green for positive returns (good months)
    - White/yellow at zero
    - Month names displayed
    """
    if pivot is None or pivot.empty:
        return go.Figure()

    # Month name mapping
    MONTH_NAMES = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    df = pivot.copy()
    # ensure months as ints
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

    # Use month names instead of numbers
    x = [MONTH_NAMES.get(int(m), str(m)) for m in df.columns.tolist()]
    y = df.index.astype(int if df.index.inferred_type == "integer" else str).tolist()

    # Custom colorscale: Red (bad) -> White (neutral) -> Green (good)
    # Red shades for negative, green shades for positive
    colorscale = [
        [0.0, "rgb(220, 20, 60)"],      # Crimson red (very bad)
        [0.25, "rgb(255, 140, 140)"],  # Light red (bad)
        [0.5, "rgb(255, 255, 255)"],   # White (neutral/zero)
        [0.75, "rgb(144, 238, 144)"],  # Light green (good)
        [1.0, "rgb(34, 139, 34)"]      # Forest green (very good)
    ]

    fig = go.Figure(
        data=go.Heatmap(
            x=x,
            y=y,
            z=Z,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            colorbar=dict(
                title="Return",
                tickformat=".0%",
                tickmode="linear",
                tick0=zmin,
                dtick=(zmax - zmin) / 5
            ),
            text=[[f"{val:.1%}" if not pd.isna(val) else "" for val in row] for row in Z],
            texttemplate="%{text}",
            textfont={"size": 10, "color": "black"},
        )
    )

    fig.update_traces(hovertemplate="Year: %{y}<br>Month: %{x}<br>Return: %{z:.2%}<extra></extra>")
    fig.update_layout(
        title=title,
        margin=dict(l=40, r=20, t=60, b=40),
        xaxis=dict(title="Month", type="category"),
        yaxis=dict(title="Year", autorange="reversed"),
    )
    return fig


# ----------------------------------------
# Monthly average returns bar chart
# ----------------------------------------
def monthly_average_bars(ret_df: pd.DataFrame, title: str = "Average Monthly Returns") -> go.Figure:
    """
    Bar chart showing average return by month across all years.
    Green for positive, red for negative.
    """
    df = ret_df.copy()
    df['Month'] = df.index.month
    monthly_avg = df.groupby('Month')['ret'].mean().sort_index()
    
    # Month names
    MONTH_NAMES = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    colors = ["rgb(220, 20, 60)" if val < 0 else "rgb(34, 139, 34)" for val in monthly_avg.values]
    
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[MONTH_NAMES[i-1] for i in monthly_avg.index],
            y=monthly_avg.values,
            marker=dict(color=colors),
            hovertemplate="Month: %{x}<br>Avg Return: %{y:.2%}<extra></extra>",
        )
    )
    
    fig.add_hline(y=0, line_width=1, line_dash="dot", opacity=0.5, line_color="gray")
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Average Return",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )
    fig.update_yaxes(tickformat=".0%")
    return fig


# ----------------------------------------
# Bars: count of periods ≤ threshold by ticker
# ----------------------------------------
def bar_threshold_counts(counts: pd.Series, title: str = "Periods ≤ threshold") -> go.Figure:
    """
    Receives a Series with index = ticker and values = count of periods ≤ threshold.
    """
    df = counts.rename("Periods").reset_index().rename(columns={"index": "Ticker"})
    fig = px.bar(df, x="Ticker", y="Periods", title=title)
    fig.update_layout(
        xaxis_title="Ticker",
        yaxis_title="Periods",
        hovermode="x",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig
