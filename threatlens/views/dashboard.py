from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_all_analyses, get_dashboard_stats, get_latest_analysis, seed_demo_data
from utils.ui import render_empty_state, render_header, render_metric_card, render_section_title


def render(secrets: dict) -> None:
    render_header("ThreatLens", "IOC Enrichment & Triage Platform", "🛡️")

    t1, t2 = st.columns([4, 1])
    query = t1.text_input("", placeholder="Buscar IOC, domínio, IP, hash ou caso...", label_visibility="collapsed")
    if t2.button("Analisar IOC", type="primary"):
        st.session_state["current_page"] = "🔎 Analisar IOC"
        st.rerun()

    rows = get_all_analyses()
    if query:
        rows = [r for r in rows if query.lower() in json.dumps(r, ensure_ascii=False).lower()]
    if not rows:
        render_empty_state("Nenhuma análise encontrada", "Execute uma análise de IOC para começar a popular o histórico.")
        return

    stats = get_dashboard_stats()
    latest = get_latest_analysis()
    latest_id = latest["id"] if latest else 0

    c = st.columns(4)
    with c[0]: render_metric_card("Total de IOCs", str(stats["total"]), "🧾", "Ver lista completa", on_click_key="card_total", target_page="🕒 Histórico")
    with c[1]: render_metric_card("Casos abertos", str(stats["open_cases"]), "📂", "Ir para casos", on_click_key="card_open", target_page="📁 Casos", filter_type="case_status", filter_value="Novo")
    with c[2]: render_metric_card("Risco crítico", str(stats["risk"].get("Crítico", 0)), "🚨", "Filtrar histórico", on_click_key="card_crit", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Crítico")
    with c[3]: render_metric_card("Risco alto", str(stats["risk"].get("Alto", 0)), "⚠️", "Filtrar histórico", on_click_key="card_high", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Alto")

    c2 = st.columns(4)
    with c2[0]: render_metric_card("Risco médio", str(stats["risk"].get("Médio", 0)), "🟠", "Filtrar histórico", on_click_key="card_med", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Médio")
    with c2[1]: render_metric_card("Risco baixo", str(stats["risk"].get("Baixo", 0)), "🟢", "Filtrar histórico", on_click_key="card_low", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Baixo")
    with c2[2]: render_metric_card("Fontes ativas", str(stats["active_sources"]), "🛰️", "Saúde das fontes", on_click_key="card_sources", target_page="⚙️ Configurações")
    with c2[3]: render_metric_card("Última análise", stats["last_analysis"], "🕒", "Abrir detalhe", on_click_key="card_latest", target_page="🧾 Detalhe da Análise", filter_type="analysis_id", filter_value=latest_id)

    df = pd.DataFrame(rows)
    risk_df = pd.DataFrame(list(stats["risk"].items()), columns=["Risco", "Quantidade"])
    type_df = pd.DataFrame(list(stats["types"].items()), columns=["Tipo", "Quantidade"])
    status_df = pd.DataFrame(list(stats["status"].items()), columns=["Status", "Quantidade"])

    g1, g2, g3, g4 = st.columns([2, 2, 2, 1])
    g1.plotly_chart(px.bar(risk_df, x="Risco", y="Quantidade", color="Risco", title="Distribuição por risco"), use_container_width=True)
    g2.plotly_chart(px.bar(type_df, x="Tipo", y="Quantidade", color="Tipo", title="Distribuição por tipo"), use_container_width=True)
    g3.plotly_chart(px.bar(status_df, x="Status", y="Quantidade", color="Status", title="Distribuição por status"), use_container_width=True)
    with g4:
        st.markdown("<div class='tl-card'><h4>Saúde das Fontes</h4><p>VirusTotal • AbuseIPDB • URLHaus • IPinfo • OpenAI</p><p>Consulte Configurações para detalhes.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='tl-card'><h4>Análise Inteligente</h4><p>Gere insights com IA a partir dos dados coletados.</p></div>", unsafe_allow_html=True)

    render_section_title("Análises Recentes")
    recent = df[["id", "ioc", "ioc_type", "risk_level", "case_status", "updated_at"]].head(10)
    st.dataframe(recent.rename(columns={"ioc": "IOC", "ioc_type": "Tipo", "risk_level": "Risco", "case_status": "Status", "updated_at": "Analisado em"}), use_container_width=True)

    sel = st.selectbox("Abrir análise recente", recent["id"].tolist())
    if st.button("Ver detalhes da análise selecionada"):
        st.session_state["selected_analysis_id"] = int(sel)
        st.session_state["current_page"] = "🧾 Detalhe da Análise"
        st.rerun()
