from __future__ import annotations

import pandas as pd
import streamlit as st

from database.db import STATUS_OPTIONS, get_all_analyses, update_case
from utils.export import to_csv_bytes
from utils.ui import render_banner, section_banner

DECISIONS = ["Pendente", "Monitorar", "Investigar", "Bloquear", "Falso positivo", "Escalado para incidente"]


def render() -> None:
    render_banner()
    section_banner("Central de Casos", "📁")

    df = pd.DataFrame(get_all_analyses())
    if df.empty:
        st.info("Nenhum caso disponível.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    q = c1.text_input("Buscar IOC")
    risk = c2.selectbox("Risco", ["Todos"] + sorted(df["risk_level"].dropna().unique().tolist()))
    status = c3.selectbox("Status", ["Todos"] + STATUS_OPTIONS)
    ioc_type = c4.selectbox("Tipo", ["Todos"] + sorted(df["ioc_type"].dropna().unique().tolist()))
    date_filter = c5.date_input("Data", value=None)

    filtered = df.copy()
    if q:
        filtered = filtered[filtered["ioc"].str.contains(q, case=False, na=False)]
    if risk != "Todos":
        filtered = filtered[filtered["risk_level"] == risk]
    if status != "Todos":
        filtered = filtered[filtered["case_status"] == status]
    if ioc_type != "Todos":
        filtered = filtered[filtered["ioc_type"] == ioc_type]
    if date_filter:
        filtered = filtered[filtered["updated_at"].str.startswith(str(date_filter))]

    st.dataframe(
        filtered[["id", "case_id", "ioc", "ioc_type", "risk_level", "confidence_level", "case_status", "analyst_decision", "updated_at"]],
        use_container_width=True,
    )

    st.markdown("### Editar caso")
    if not filtered.empty:
        selected = st.selectbox("ID da análise", filtered["id"].tolist())
        row = filtered[filtered["id"] == selected].iloc[0]
        new_status = st.selectbox("Novo status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["case_status"]))
        new_decision = st.selectbox("Nova decisão", DECISIONS, index=DECISIONS.index(row["analyst_decision"]))
        notes = st.text_area("Notas do analista", value=row.get("analyst_notes", ""))
        if st.button("Atualizar caso", type="primary"):
            update_case(int(selected), new_status, new_decision, notes)
            st.success("Caso atualizado com sucesso.")
            st.rerun()

    st.download_button(
        "Exportar casos CSV",
        data=to_csv_bytes(filtered.to_dict(orient="records")),
        file_name="threatlens_cases.csv",
        mime="text/csv",
    )
