from __future__ import annotations

import streamlit as st
import pandas as pd

from app.core.config import AppConfig
from app.core.services import DataService
from app.core.returns import seasonality_table, max_red_streak
from app.core.stats import pct_above_threshold
from app.viz.plots import (
    price_with_drawdown, drawdown_area, hist_returns, heatmap_calendar,
    monthly_returns_bar, bar_threshold_counts, monthly_average_bars
)
from app.ui.components import kpi_row, data_table
from app.ui.utils import format_percentage_colored
from app.ui.base import render_ticker_selector, render_chart


def render_overview_tab(
    raw_data: dict[str, pd.DataFrame],
    service: DataService,
    config: AppConfig
) -> None:
    """Render the Overview tab with KPIs and charts."""
    st.subheader("Overview")
    
    first_ticker = list(raw_data.keys())[0]
    
    # Get processed data from service
    ret0 = service.get_returns(first_ticker)
    dd0 = service.get_drawdown(first_ticker)

    # Calculate metrics
    counts = service.get_threshold_counts(config.threshold)
    pct_above = pct_above_threshold(ret0, config.threshold)
    
    # Additional metrics
    avg_return = ret0['ret'].mean()
    volatility = ret0['ret'].std()
    sharpe_approx = (avg_return / volatility) * (12 ** 0.5) if volatility > 0 else 0  # Annualized Sharpe

    # Build KPI dictionary
    kpi_common = {
        "Tickers": str(len(raw_data)),
        "Frequency": config.frequency,
        "Threshold": f"{config.threshold_pct}%"
    }
    
    kpis = {
        **kpi_common,
        "Periods analyzed": f"{ret0.shape[0]}",
        "Periods ≤ threshold": f"{counts[first_ticker]}",
        "% times ≥ threshold": format_percentage_colored(pct_above),
        "Avg monthly return": f"{avg_return:.2%}",
        "Volatility (σ)": f"{volatility:.2%}",
        "Worst period": f"{ret0['ret'].min():.2%}",
        "Max Drawdown": f"{dd0['dd'].min():.2%}",
        "Longest red-streak": f"{max_red_streak(ret0)} months",
    }
    kpi_row(kpis)

    # Charts row 1: Price/Drawdown
    c1, c2 = st.columns(2)
    with c1:
        render_chart(
            price_with_drawdown(dd0, title=f"{first_ticker} — Price and peak")
        )
    with c2:
        render_chart(
            drawdown_area(dd0, title=f"{first_ticker} — Accumulated drawdown")
        )

    # Charts row 2: Monthly returns
    r1, r2 = st.columns(2)
    with r1:
        render_chart(
            monthly_returns_bar(
                ret0, 
                title=f"Monthly returns — {first_ticker}", 
                threshold=config.threshold
            )
        )
    with r2:
        st.caption(
            "Drawdown is accumulated from the last peak. Bars show the return for each month; "
            "those falling below the threshold are colored in red."
        )

    # Multi-ticker comparison
    if len(raw_data) > 1:
        render_chart(
            bar_threshold_counts(
                pd.Series(counts), 
                title="Periods ≤ threshold by ticker"
            )
        )


def render_distribution_tab(
    raw_data: dict[str, pd.DataFrame],
    service: DataService,
    config: AppConfig
) -> None:
    """Render the Distribution tab with histogram."""
    st.subheader("Distribution")
    ticker = render_ticker_selector(list(raw_data.keys()), key="dist_t")
    ret = service.get_returns(ticker)
    
    # Show summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean", f"{ret['ret'].mean():.2%}")
    with col2:
        st.metric("Median", f"{ret['ret'].median():.2%}")
    with col3:
        st.metric("Std Dev", f"{ret['ret'].std():.2%}")
    with col4:
        st.metric("Skewness", f"{ret['ret'].skew():.2f}")
    
    st.caption("📊 Distribution of monthly returns. The red dashed line indicates your threshold.")
    render_chart(
        hist_returns(ret, title=f"Return distribution — {ticker}", threshold=config.threshold)
    )


def render_seasonality_tab(
    raw_data: dict[str, pd.DataFrame],
    service: DataService,
    config: AppConfig
) -> None:
    """Render the Seasonality tab with heatmap and statistics."""
    st.subheader("Seasonality")
    ticker = render_ticker_selector(list(raw_data.keys()), key="season_t")
    ret = service.get_returns(ticker)
    pivot = seasonality_table(ret)
    
    # Calculate monthly statistics
    ret_copy = ret.copy()
    ret_copy['Month'] = ret_copy.index.month
    monthly_stats = ret_copy.groupby('Month')['ret'].agg(['mean', 'std', 'count'])
    
    # Month names
    MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Find best and worst months
    best_month_idx = monthly_stats['mean'].idxmax()
    worst_month_idx = monthly_stats['mean'].idxmin()
    best_month_name = MONTH_NAMES[best_month_idx - 1]
    worst_month_name = MONTH_NAMES[worst_month_idx - 1]
    
    # Display key statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Best Month",
            best_month_name,
            f"{monthly_stats.loc[best_month_idx, 'mean']:.2%}"
        )
    with col2:
        st.metric(
            "Worst Month",
            worst_month_name,
            f"{monthly_stats.loc[worst_month_idx, 'mean']:.2%}"
        )
    with col3:
        st.metric(
            "Most Volatile",
            MONTH_NAMES[monthly_stats['std'].idxmax() - 1],
            f"σ={monthly_stats['std'].max():.2%}"
        )
    with col4:
        avg_return = ret['ret'].mean()
        st.metric(
            "Overall Avg",
            "Monthly Return",
            f"{avg_return:.2%}"
        )
    
    st.divider()
    
    # Heatmap
    st.markdown("#### Year × Month Heatmap")
    st.caption("🔴 Red = Negative returns (bad months) | 🟢 Green = Positive returns (good months)")
    render_chart(
        heatmap_calendar(pivot, title=f"Monthly Returns by Year — {ticker}")
    )
    
    # Monthly average chart
    st.markdown("#### Average Returns by Month")
    st.caption("Average return for each month across all years in the dataset")
    render_chart(
        monthly_average_bars(ret, title=f"Average Monthly Returns — {ticker}")
    )
    
    # Detailed statistics table
    with st.expander("📊 Detailed Monthly Statistics"):
        stats_df = pd.DataFrame({
            'Month': [MONTH_NAMES[i-1] for i in monthly_stats.index],
            'Avg Return': monthly_stats['mean'].apply(lambda x: f"{x:.2%}"),
            'Std Dev': monthly_stats['std'].apply(lambda x: f"{x:.2%}"),
            'Count': monthly_stats['count'].astype(int),
        })
        data_table(stats_df)


def render_events_tab(
    raw_data: dict[str, pd.DataFrame],
    service: DataService,
    config: AppConfig
) -> None:
    """Render the Events tab with threshold breach events."""
    st.subheader("Events (periods ≤ threshold)")
    ticker = render_ticker_selector(list(raw_data.keys()), key="events_t")
    ret = service.get_returns(ticker)
    events = ret[ret['ret'] <= config.threshold].copy()
    
    if events.empty:
        st.success(f"🎉 No events found! All periods are above the threshold of {config.threshold:.2%}.")
        st.info("Try lowering the threshold in the sidebar to see more events.")
        return
    
    events['ret_pct'] = (events['ret'] * 100).round(2)
    events['Date'] = events.index.strftime('%Y-%m')
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Events", len(events))
    with col2:
        st.metric("Worst Event", f"{events['ret'].min():.2%}")
    with col3:
        st.metric("Avg Event Return", f"{events['ret'].mean():.2%}")
    
    st.caption(f"📉 Showing {len(events)} period(s) where returns fell below {config.threshold:.2%}")
    
    # Display table with date and return
    display_df = events[['Date', 'ret_pct']].rename(columns={'ret_pct': 'Return (%)'})
    data_table(display_df)
    
    # Download button
    st.download_button(
        label="📥 Download events CSV",
        data=events[['ret_pct']].to_csv().encode('utf-8'),
        file_name=f"{ticker}_events_threshold_{config.threshold_pct}.csv",
        mime="text/csv",
    )

