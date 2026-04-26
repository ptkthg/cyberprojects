from __future__ import annotations

import pandas as pd
import streamlit as st

from database.db import STATUS_OPTIONS, clear_history, get_all_analyses, get_audit_logs, update_case
from utils.export import to_csv_bytes
from utils.ui import render_banner, section_banner

DECISIONS = ["Pendente", "Monitorar", "Investigar", "Bloquear", "Falso positivo", "Escalado para incidente"]


def render() -> None:
    render_banner()
    section_banner("Histórico de análises e trilha de auditoria", "🗂️")
    rows = get_all_analyses()
    if not rows:
        st.info("Sem histórico no momento.")
        return

    df = pd.DataFrame(rows)

    c1, c2, c3, c4 = st.columns(4)
    search = c1.text_input("Buscar IOC")
    risk = c2.selectbox("Risco", ["Todos"] + sorted(df["risk_level"].dropna().unique().tolist()))
    ioc_type = c3.selectbox("Tipo", ["Todos"] + sorted(df["ioc_type"].dropna().unique().tolist()))
    date_filter = c4.date_input("Data", value=None)

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["ioc"].str.contains(search, case=False, na=False)]
    if risk != "Todos":
        filtered = filtered[filtered["risk_level"] == risk]
    if ioc_type != "Todos":
        filtered = filtered[filtered["ioc_type"] == ioc_type]
    if date_filter:
        filtered = filtered[filtered["updated_at"].str.startswith(str(date_filter))]

    st.dataframe(filtered, use_container_width=True)

    st.markdown("### Atualizar caso")
    options = filtered["id"].tolist()
    if options:
        analysis_id = st.selectbox("Selecione ID", options)
        current = filtered[filtered["id"] == analysis_id].iloc[0]
        status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current.get("case_status", "Novo")))
        decision = st.selectbox("Decisão", DECISIONS, index=DECISIONS.index(current.get("analyst_decision", "Pendente")))
        notes = st.text_area("Notas", value=current.get("analyst_notes", ""))
        if st.button("Salvar atualização"):
            update_case(int(analysis_id), status, decision, notes)
            st.success("Caso atualizado.")
            st.rerun()

    st.download_button(
        "Exportar histórico CSV",
        data=to_csv_bytes(filtered.to_dict(orient="records")),
        file_name="threatlens_history.csv",
        mime="text/csv",
    )

    st.markdown("### Auditoria")
    audit_df = pd.DataFrame(get_audit_logs(100))
    if not audit_df.empty:
        st.dataframe(audit_df, use_container_width=True)

    st.divider()
    if st.checkbox("Confirmo limpeza total do histórico"):
        if st.button("Limpar histórico"):
            clear_history()
            st.success("Histórico limpo com sucesso.")
            st.rerun()
