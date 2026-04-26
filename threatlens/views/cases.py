from __future__ import annotations

import pandas as pd
import streamlit as st

from database.db import DECISION_OPTIONS, STATUS_OPTIONS, get_all_analyses, update_case
from utils.export import to_csv_bytes
from utils.ui import render_empty_state, render_header


def render(secrets: dict) -> None:
    render_header("Casos", "Central operacional de triagem e acompanhamento", "📁")
    df = pd.DataFrame(get_all_analyses())
    if df.empty:
        render_empty_state("Nenhum caso aberto no momento", "Use Analisar IOC para criar o primeiro caso.")
        return

    c1, c2, c3 = st.columns(3)
    q = c1.text_input("Buscar IOC/Case ID")
    risk = c2.selectbox("Risco", ["Todos", "Crítico", "Alto", "Médio", "Baixo"])
    status = c3.selectbox("Status", ["Todos"] + STATUS_OPTIONS)

    flt = df.copy()
    if q:
        flt = flt[flt["ioc"].str.contains(q, case=False, na=False) | flt["case_id"].str.contains(q, case=False, na=False)]
    if risk != "Todos":
        flt = flt[flt["risk_level"] == risk]
    if status != "Todos":
        flt = flt[flt["case_status"] == status]

    st.dataframe(
        flt[["id", "case_id", "ioc", "ioc_type", "risk_level", "confidence_level", "case_status", "analyst_decision", "analyst_notes", "created_at", "updated_at"]],
        use_container_width=True,
    )

    if flt.empty:
        render_empty_state("Sem casos para os filtros", "Ajuste filtros para visualizar casos.")
        return

    selected = st.selectbox("Selecionar ID para atualizar", flt["id"].tolist())
    row = flt[flt["id"] == selected].iloc[0]
    s1, s2 = st.columns(2)
    new_status = s1.selectbox("Status do caso", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["case_status"]))
    new_decision = s2.selectbox("Decisão", DECISION_OPTIONS, index=DECISION_OPTIONS.index(row["analyst_decision"]))
    notes = st.text_area("Notas", value=row.get("analyst_notes", ""))
    a1, a2 = st.columns(2)
    if a1.button("Atualizar caso", type="primary"):
        update_case(int(selected), new_status, new_decision, notes)
        st.success("Caso atualizado com sucesso.")
        st.rerun()
    if a2.button("Abrir detalhe"):
        st.session_state["selected_analysis_id"] = int(selected)
        st.rerun()

    st.download_button("Exportar casos CSV", data=to_csv_bytes(flt.to_dict(orient="records")), file_name="casos.csv", mime="text/csv")
