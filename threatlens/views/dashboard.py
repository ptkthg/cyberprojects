from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_all_analyses, get_dashboard_stats, seed_demo_data
from utils.ui import render_empty_state, render_header, render_metric_card, render_section_title


def render(secrets: dict) -> None:
    render_header("ThreatLens SOC Console", "IOC enrichment and threat triage", "📊")

    toolbar1, toolbar2 = st.columns([4, 1])
    with toolbar1:
        query = st.text_input("", placeholder="Buscar IOC, domínio, IP, hash ou caso...", label_visibility="collapsed")
    with toolbar2:
        if st.button("Carregar demo"):
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
    api_ok = sum(1 for k in ["VIRUSTOTAL_API_KEY", "ABUSEIPDB_API_KEY", "URLHAUS_API_KEY", "IPINFO_API_KEY"] if secrets.get(k))
    mode = "Demo" if any("TL-DEMO" in r.get("case_id", "") for r in rows) else "Produção local"
    st.caption(f"Fontes ativas: {stats['active_sources']} • Modo: {mode} • API status: {api_ok}/4 • Última atualização: {stats['last_analysis']}")

    cols = st.columns(4)
    with cols[0]: render_metric_card("Total de IOCs", str(stats["total"]), "📌")
    with cols[1]: render_metric_card("Casos abertos", str(stats["open_cases"]), "📁")
    with cols[2]: render_metric_card("Risco crítico", str(stats["risk"].get("Crítico", 0)), "🚨")
    with cols[3]: render_metric_card("Risco alto", str(stats["risk"].get("Alto", 0)), "⚠️")

    cols2 = st.columns(4)
    with cols2[0]: render_metric_card("Risco médio", str(stats["risk"].get("Médio", 0)), "🟠")
    with cols2[1]: render_metric_card("Risco baixo", str(stats["risk"].get("Baixo", 0)), "🟢")
    with cols2[2]: render_metric_card("Fontes ativas", str(stats["active_sources"]), "🛰️")
    with cols2[3]: render_metric_card("Última análise", stats["last_analysis"], "🕒")

    df = pd.DataFrame(rows)
    risk_df = pd.DataFrame(list(stats["risk"].items()), columns=["Risco", "Quantidade"])
    type_df = pd.DataFrame(list(stats["types"].items()), columns=["Tipo", "Quantidade"])
    status_df = pd.DataFrame(list(stats["status"].items()), columns=["Status", "Quantidade"])

    st.markdown("Resumo visual de severidade, tipo e status dos casos.")
    g1, g2, g3 = st.columns(3)
    g1.plotly_chart(px.bar(risk_df, x="Risco", y="Quantidade", color="Risco", title="Distribuição por risco"), use_container_width=True)
    g2.plotly_chart(px.bar(type_df, x="Tipo", y="Quantidade", color="Tipo", title="Distribuição por tipo de IOC"), use_container_width=True)
    g3.plotly_chart(px.bar(status_df, x="Status", y="Quantidade", color="Status", title="Distribuição por status"), use_container_width=True)

    evo = df.copy()
    evo["data"] = evo["updated_at"].str.slice(0, 10)
    evo_df = evo.groupby("data", as_index=False).size().rename(columns={"size": "Quantidade"})
    st.plotly_chart(px.line(evo_df, x="data", y="Quantidade", markers=True, title="Evolução de análises por data"), use_container_width=True)

    render_section_title("Últimos IOCs analisados")
    preview = df[["id", "ioc", "ioc_type", "risk_level", "case_status", "sources_json", "updated_at"]].head(12)
    preview = preview.rename(columns={"ioc": "IOC", "ioc_type": "Tipo", "risk_level": "Risco", "case_status": "Status", "updated_at": "Última análise", "sources_json": "Fontes"})
    st.dataframe(preview, use_container_width=True)

    actions = st.columns(3)
    ids = df["id"].head(20).tolist()
    sel = actions[0].selectbox("Selecionar análise", ids)
    if actions[1].button("Ver análise"):
        st.session_state["selected_analysis_id"] = int(sel)
        st.rerun()
    if actions[2].button("Reanalisar"):
        row = df[df["id"] == sel].iloc[0]
        st.session_state["reanalyze_ioc"] = row["ioc"]
        st.success("IOC enviado para tela de análise.")
