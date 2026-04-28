from __future__ import annotations

import pandas as pd
import streamlit as st

from database.db import clear_analyses, list_analyses
from utils.export import to_csv_bytes


def render() -> None:
    st.title("🗂️ Histórico")
    rows = list_analyses()
    if not rows:
        st.info("Sem histórico no momento.")
        return

    df = pd.DataFrame(rows)
    c1, c2, c3 = st.columns(3)
    selected_type = c1.selectbox("Tipo", ["Todos"] + sorted(df["ioc_type"].dropna().unique().tolist()))
    selected_risk = c2.selectbox("Risco", ["Todos"] + sorted(df["risk_level"].dropna().unique().tolist()))
    search = c3.text_input("Buscar IOC")

    filtered = df.copy()
    if selected_type != "Todos":
        filtered = filtered[filtered["ioc_type"] == selected_type]
    if selected_risk != "Todos":
        filtered = filtered[filtered["risk_level"] == selected_risk]
    if search:
        filtered = filtered[filtered["ioc"].str.contains(search, case=False, na=False)]

    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "Exportar histórico CSV",
        data=to_csv_bytes(filtered.to_dict(orient="records")),
        file_name="threatlens_history.csv",
        mime="text/csv",
    )

    st.divider()
    st.warning("Ação destrutiva")
    if st.checkbox("Confirmo que desejo limpar todo o histórico"):
        if st.button("Limpar histórico", type="secondary"):
            clear_analyses()
            st.success("Histórico limpo com sucesso.")
            st.rerun()
