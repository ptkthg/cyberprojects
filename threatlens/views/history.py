from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from core.navigation import clear_navigation_filters, open_analysis_detail
from database.db import STATUS_OPTIONS, clear_history, get_all_analyses, get_audit_logs
from utils.export import to_csv_bytes
from utils.ui import render_empty_state, render_page_header, render_risk_badge, render_status_badge


def render(secrets: dict) -> None:
    render_page_header("Histórico investigativo", "Case Management Timeline • filtros operacionais • acesso ao detalhe", None)
    rows = get_all_analyses()
    if not rows:
        render_empty_state("Nenhuma análise encontrada", "Execute uma análise de IOC para começar a popular o histórico.")
        return

    df = pd.DataFrame(rows)
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        q = c1.text_input("Buscar IOC", value=st.session_state.get("history_filter_search_ioc", ""))
        risk = c2.selectbox("Risco", ["Todos", "Crítico", "Alto", "Médio", "Baixo"], index=["Todos", "Crítico", "Alto", "Médio", "Baixo"].index(st.session_state.get("history_filter_risk", "Todos")))
        ioc_type = c3.selectbox("Tipo", ["Todos"] + sorted(df["ioc_type"].unique().tolist()), index=0)
        status_opts = ["Todos"] + STATUS_OPTIONS
        status_default = st.session_state.get("history_filter_status", "Todos")
        status_idx = status_opts.index(status_default) if status_default in status_opts else 0
        status = c4.selectbox("Status", status_opts, index=status_idx)
        period = c5.selectbox("Período", ["Todos", "7 dias", "30 dias", "90 dias"])

    flt = df.copy()
    if q:
        flt = flt[flt["ioc"].str.contains(q, case=False, na=False) | flt["case_id"].str.contains(q, case=False, na=False)]
    if risk != "Todos":
        flt = flt[flt["risk_level"] == risk]
    if ioc_type != "Todos":
        flt = flt[flt["ioc_type"] == ioc_type]
    if status != "Todos":
        flt = flt[flt["case_status"] == status]
    if period != "Todos":
        days = int(period.split()[0]); cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
        flt = flt[pd.to_datetime(flt["updated_at"], errors="coerce") >= cutoff]

    if any(k in st.session_state for k in ["history_filter_risk", "history_filter_status", "history_filter_type", "history_filter_search_ioc"]):
        st.info(f"Filtro ativo: Risco {st.session_state.get('history_filter_risk','Todos')}")
        if st.button("Limpar filtros"):
            clear_navigation_filters(); st.rerun()

    if flt.empty:
        render_empty_state("Sem resultado", "Nenhum resultado para os filtros selecionados.")
    else:
        st.markdown("### Timeline")
        for _, row in flt.head(25).iterrows():
            with st.container(border=True):
                l, r = st.columns([4, 1])
                l.write(f"**{row['ioc']}** ({row['ioc_type']}) • Case `{row['case_id']}`")
                render_risk_badge(row["risk_level"], int(row["score"])); render_status_badge(row["case_status"])
                l.caption(f"Confiança: {row['confidence_level']} • Data: {row['updated_at']}")
                try:
                    src = json.loads(row.get("sources_json", "{}")); l.caption(f"Fontes: {', '.join([f'{k}:{v}' for k,v in src.items()])}")
                except Exception:
                    pass
                if r.button("Ver análise", key=f"hist_{row['id']}"):
                    open_analysis_detail(int(row["id"])); st.rerun()
                if r.button("Reanalisar", key=f"rean_{row['id']}"):
                    st.session_state["reanalyze_ioc"] = row["ioc"]; st.session_state["current_page"] = "Analisar IOC"; st.rerun()
                if r.button("Abrir caso", key=f"case_{row['id']}"):
                    st.session_state["current_page"] = "Casos"; st.session_state["case_filter_search"] = row["case_id"]; st.rerun()

        st.download_button("Exportar histórico CSV", data=to_csv_bytes(flt.to_dict(orient="records")), file_name="historico.csv", mime="text/csv")

    st.markdown("### Auditoria recente")
    st.dataframe(pd.DataFrame(get_audit_logs(50)), use_container_width=True)

    if st.button("Limpar histórico", type="secondary"):
        clear_history(); st.success("Histórico limpo."); st.rerun()
