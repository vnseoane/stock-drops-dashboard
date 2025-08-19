import streamlit as st
import pandas as pd

def kpi_row(kpis: dict[str, str]) -> None:
    """
    Renderiza KPIs en columnas.
    - Si el valor viene con <span ...> (para colorear), lo mostramos con HTML
      pero manteniendo el tamaño de fuente similar a st.metric (~2rem).
    """
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis.items()):
        if isinstance(value, str) and value.strip().startswith("<span"):
            # Tamaño grande + mismo look que un metric
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
