import streamlit as st
import pandas as pd

def kpi_row(kpis: dict[str, str]) -> None:
    """
    Render KPIs in columns.
    - If the value comes with <span ...> (for coloring), display it with HTML
      but maintaining font size similar to st.metric (~2rem).
    """
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis.items()):
        if isinstance(value, str) and value.strip().startswith("<span"):
            # Large size + same look as a metric
            html = (
                f"<div style='font-weight:600; opacity:0.6'>{label}</div>"
                f"<div style='font-size:2rem; line-height:1.2; font-weight:700; margin-top:0.25rem'>{value}</div>"
            )
            col.markdown(html, unsafe_allow_html=True)
        else:
            col.metric(label=label, value=value)

def data_table(df: pd.DataFrame, caption: str = "") -> None:
    st.dataframe(df, use_container_width=True)
    if caption:
        st.caption(caption)
