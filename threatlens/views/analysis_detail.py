from __future__ import annotations

import json

import streamlit as st

from core.analyzer import analyze_ioc
from database.db import get_ai_analysis, get_analysis_by_id, save_ai_analysis, save_analysis
from services.openai_analysis import generate_ai_ioc_analysis
from utils.ui import recommendation_card, render_empty_state, render_header, render_risk_badge, render_status_badge


def render(secrets: dict) -> None:
    render_header("Detalhe da Análise", "Fluxo: Histórico → Reabrir análise → Abrir caso", "🧾")
    analysis_id = st.session_state.get("selected_analysis_id")
    if not analysis_id:
        render_empty_state("Nenhuma análise selecionada", "Abra Histórico, Painel ou Casos e clique em Ver análise.")
        return

    row = get_analysis_by_id(int(analysis_id))
    if not row:
        render_empty_state("Análise não encontrada", "O registro selecionado não existe mais.")
        return

    st.markdown(f"**Case ID:** `{row['case_id']}` • **IOC:** `{row['ioc']}` • **Tipo:** `{row['ioc_type']}`")
    render_risk_badge(row["risk_level"], int(row["score"])); render_status_badge(row["case_status"])
    st.caption(f"Confiança: {row['confidence_level']} • Data: {row['updated_at']}")
    st.markdown("### Resumo executivo"); st.write(row["summary"])
    recommendation_card(row["recommendation"])

    st.markdown("### Fontes consultadas"); st.json(json.loads(row["sources_json"]), expanded=False)
    st.markdown("### Evidências"); st.json(json.loads(row["evidence_json"]), expanded=False)
    st.markdown("### Score breakdown")
    for line in json.loads(row.get("score_breakdown_json", "[]")):
        st.markdown(f"- {line}")

    rerun = analyze_ioc(row["ioc"], secrets)
    st.markdown("### KQL"); st.code(rerun["kql"], language="kql")

    st.markdown("### Análise assistida por IA")
    st.caption("Esta análise é auxiliar e deve ser validada pelo analista.")
    saved_ai = get_ai_analysis(int(analysis_id))
    if saved_ai.get("analysis"):
        st.success(f"Análise IA salva em {saved_ai.get('created_at','-')}")
        st.json(saved_ai["analysis"], expanded=False)

    if st.button("Gerar análise IA"):
        ai = generate_ai_ioc_analysis(row["ioc"], row["ioc_type"], {"score": row["score"], "risk_level": row["risk_level"], "confidence_level": row["confidence_level"], "sources": json.loads(row["sources_json"]), "evidence": json.loads(row["evidence_json"]), "score_breakdown": json.loads(row.get("score_breakdown_json", "[]"))}, rerun["kql"], secrets.get("OPENAI_API_KEY"))
        if ai.get("status") == "Consultado":
            save_ai_analysis(int(analysis_id), ai)
            st.success("Análise IA gerada e salva.")
            st.rerun()
        elif ai.get("status") == "Sem API key":
            st.warning("OPENAI_API_KEY ausente. Configure nas Configurações.")
        else:
            st.error(f"Falha ao gerar análise IA: {ai.get('error', ai.get('status'))}")

    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("Voltar"):
        st.session_state.pop("selected_analysis_id", None); st.rerun()
    c2.download_button("Exportar relatório", data=json.dumps(row, ensure_ascii=False, indent=2).encode("utf-8"), file_name=f"detail_{row['case_id']}.json", mime="application/json")
    c3.text_area("Copiar KQL", rerun["kql"], height=100)
    if c4.button("Abrir caso"):
        st.session_state["current_page"] = "📁 Casos"; st.rerun()
    if c5.button("Reanalisar"):
        new = analyze_ioc(row["ioc"], secrets); new_id = save_analysis(new, as_case=True); st.session_state["selected_analysis_id"] = new_id; st.success("Reanálise concluída e salva."); st.rerun()
