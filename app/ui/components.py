import streamlit as st
import pandas as pd


def kpi_row(kpis: dict[str, str]) -> None:
    cols = st.columns(len(kpis))
    for col, (k, v) in zip(cols, kpis.items()):
        with col:
            st.metric(label=k, value=v)


def data_table(df: pd.DataFrame, caption: str = "") -> None:
    st.dataframe(df, use_container_width=True)
    if caption:
        st.caption(caption)
