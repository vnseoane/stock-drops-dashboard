import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def price_with_drawdown(dd_df: pd.DataFrame, title: str = "") -> go.Figure:
    """Serie de precio ajustado + línea del pico (Peak)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd_df.index, y=dd_df["Adj Close"], name="Adj Close", mode="lines"))
    if "Peak" in dd_df.columns:
        fig.add_trace(go.Scatter(x=dd_df.index, y=dd_df["Peak"], name="Peak", mode="lines"))
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Precio",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def drawdown_area(dd_df: pd.DataFrame, title: str = "Drawdown acumulado") -> go.Figure:
    """Drawdown (proporción negativa) con eje en % y rango [min..0]."""
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


def monthly_returns_bar(
    ret_df: pd.DataFrame,
    title: str = "Retornos mensuales",
    threshold: float | None = None,
    default_color: str = "lightslategray",
    hit_color: str = "crimson",
) -> go.Figure:
    """Barras de retorno mensual. Si hay 'threshold' (proporción, ej. -0.08),
    pinta en rojo (hit_color) las barras <= umbral y dibuja línea horizontal."""
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



def hist_returns(
    ret_df: pd.DataFrame,
    title: str = "Distribución de retornos",
    threshold: float | None = None,
) -> go.Figure:
    """Histograma de retornos; si hay umbral, dibuja línea vertical."""
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


def heatmap_calendar(pivot: pd.DataFrame, title: str = "Año × Mes") -> go.Figure:
    # columnas = meses (1..12), index = años
    pivot = pivot.copy().reindex(sorted(pivot.columns), axis=1)

    fig = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(x="Mes", y="Año", color="Retorno"),
        zmin=pivot.min().min(),
        zmax=pivot.max().max(),
        color_continuous_midpoint=0,
    )

    # ✅ hover en porcentaje y con etiquetas claras
    fig.update_traces(
        hovertemplate="Mes: %{x}<br>Año: %{y}<br>Retorno: %{z:.2%}<extra></extra>"
    )

    # Eje, colorbar y layout
    fig.update_layout(title=title, margin=dict(l=40, r=20, t=60, b=40))
    fig.update_coloraxes(colorbar_title="Retorno", colorbar_tickformat=".0%")
    fig.update_xaxes(type="category")  # mostrar meses como 1..12, no como continuo

    return fig
