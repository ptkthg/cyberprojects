from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_all_analyses, get_dashboard_stats, get_latest_analysis, seed_demo_data
from utils.ui import render_empty_state, render_header, render_metric_card, render_section_title


def render(secrets: dict) -> None:
    render_header("ThreatLens SOC Console", "IOC enrichment and threat triage", "📊")

    t1, t2 = st.columns([4, 1])
    query = t1.text_input("", placeholder="Buscar IOC, domínio, IP, hash ou caso...", label_visibility="collapsed")
    if t2.button("Carregar demo"):
        seed_demo_data()
        st.success("Modo demo carregado.")
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
    api_ok = sum(1 for k in ["VIRUSTOTAL_API_KEY", "ABUSEIPDB_API_KEY", "URLHAUS_API_KEY", "IPINFO_API_KEY", "OPENAI_API_KEY"] if secrets.get(k))
    mode = "Demo" if any("TL-DEMO" in r.get("case_id", "") for r in rows) else "Produção local"
    st.caption(f"Fontes ativas: {stats['active_sources']} • Modo atual: {mode} • API status: {api_ok}/5 • Última atualização: {stats['last_analysis']}")

    c = st.columns(4)
    with c[0]: render_metric_card("Total de IOCs", str(stats["total"]), "📌", "Listar todos", on_click_key="card_total", target_page="🕒 Histórico")
    with c[1]: render_metric_card("Casos abertos", str(stats["open_cases"]), "📁", "Abrir casos ativos", on_click_key="card_open", target_page="📁 Casos", filter_type="case_status", filter_value="Novo")
    with c[2]: render_metric_card("Risco crítico", str(stats["risk"].get("Crítico", 0)), "🚨", "Abrir histórico", on_click_key="card_crit", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Crítico")
    with c[3]: render_metric_card("Risco alto", str(stats["risk"].get("Alto", 0)), "⚠️", "Abrir histórico", on_click_key="card_high", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Alto")

    c2 = st.columns(4)
    with c2[0]: render_metric_card("Risco médio", str(stats["risk"].get("Médio", 0)), "🟠", "Abrir histórico", on_click_key="card_med", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Médio")
    with c2[1]: render_metric_card("Risco baixo", str(stats["risk"].get("Baixo", 0)), "🟢", "Abrir histórico", on_click_key="card_low", target_page="🕒 Histórico", filter_type="history_risk", filter_value="Baixo")
    with c2[2]: render_metric_card("Fontes ativas", str(stats["active_sources"]), "🛰️", "Saúde das fontes", on_click_key="card_sources", target_page="⚙️ Configurações")
    with c2[3]: render_metric_card("Última análise", stats["last_analysis"], "🕒", "Abrir detalhe", on_click_key="card_latest", target_page="🧾 Detalhe da Análise", filter_type="analysis_id", filter_value=latest_id)

    df = pd.DataFrame(rows)
    risk_df = pd.DataFrame(list(stats["risk"].items()), columns=["Risco", "Quantidade"])
    type_df = pd.DataFrame(list(stats["types"].items()), columns=["Tipo", "Quantidade"])
    status_df = pd.DataFrame(list(stats["status"].items()), columns=["Status", "Quantidade"])

    st.markdown("Resumo visual de severidade, tipo e status dos casos.")
    g1, g2, g3 = st.columns(3)
    g1.plotly_chart(px.bar(risk_df, x="Risco", y="Quantidade", color="Risco", title="Distribuição por risco"), use_container_width=True)
    g2.plotly_chart(px.bar(type_df, x="Tipo", y="Quantidade", color="Tipo", title="Distribuição por tipo de IOC"), use_container_width=True)
    g3.plotly_chart(px.bar(status_df, x="Status", y="Quantidade", color="Status", title="Distribuição por status do caso"), use_container_width=True)

    evo = df.copy(); evo["data"] = evo["updated_at"].str.slice(0, 10)
    evo_df = evo.groupby("data", as_index=False).size().rename(columns={"size": "Quantidade"})
    st.plotly_chart(px.line(evo_df, x="data", y="Quantidade", markers=True, title="Evolução de análises por data"), use_container_width=True)

    render_section_title("Últimos IOCs analisados")
    preview = df[["id", "ioc", "ioc_type", "risk_level", "case_status", "updated_at"]].head(12)
    st.dataframe(preview.rename(columns={"ioc": "IOC", "ioc_type": "Tipo", "risk_level": "Risco", "case_status": "Status", "updated_at": "Última análise"}), use_container_width=True)
