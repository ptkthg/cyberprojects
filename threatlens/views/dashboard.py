from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from database.db import get_all_analyses, get_dashboard_stats, get_latest_analysis
from services.openai_analysis import generate_ai_ioc_analysis
from utils.charts import risk_donut, status_donut, type_bar
from utils.ui import render_empty_state, render_metric_card


def _safe_source_name(row: dict) -> str:
    try:
        sources = json.loads(row.get("sources_json", "{}"))
        for src, status in sources.items():
            if status == "Consultado":
                return src
    except Exception:
        return "-"
    return "-"


def _table_badge(text: str, color: str) -> str:
    return f"<span class='tl-pill' style='border-color:{color};color:{color};background:rgba(15,23,42,.65)'>{text}</span>"


def _render_recent_table(rows: list[dict]) -> None:
    if not rows:
        return

    type_colors = {"ipv4": "#38bdf8", "domain": "#8b5cf6", "url": "#0ea5e9", "md5": "#14b8a6", "sha1": "#22c55e", "sha256": "#84cc16"}
    risk_colors = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#f59e0b", "Baixo": "#22c55e"}
    status_colors = {"Bloqueado": "#ef4444", "Em análise": "#f59e0b", "Falso positivo": "#fb923c", "Resolvido": "#3b82f6", "Novo": "#22c55e", "Monitorado": "#14b8a6", "Escalado": "#8b5cf6"}

    html = [
        "<div class='tl-card'>",
        "<div class='tl-chart-title'>Análises recentes</div>",
        "<table class='tl-custom-table'>",
        "<thead><tr><th>Data/Hora</th><th>IOC</th><th>Tipo</th><th>Risco</th><th>Status</th><th>Fonte principal</th><th>Caso</th></tr></thead><tbody>",
    ]

    for row in rows[:8]:
        ioc_type = row.get("ioc_type", "-")
        risk = row.get("risk_level", "-")
        status = row.get("case_status", "-")
        case_id = row.get("case_id", "-")
        html.append(
            "<tr>"
            f"<td>{row.get('updated_at', '-')}</td>"
            f"<td>{row.get('ioc', '-')}</td>"
            f"<td>{_table_badge(ioc_type.capitalize(), type_colors.get(ioc_type, '#94a3b8'))}</td>"
            f"<td>{_table_badge(risk, risk_colors.get(risk, '#94a3b8'))}</td>"
            f"<td>{_table_badge(status, status_colors.get(status, '#94a3b8'))}</td>"
            f"<td>{_safe_source_name(row)}</td>"
            f"<td><span class='tl-case-link'>{case_id}</span></td>"
            "</tr>"
        )

    html.append("</tbody></table><div class='tl-chart-link'>Ver todas as análises →</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_sources_panel() -> None:
    sources = ["VirusTotal", "AbuseIPDB", "URLHaus", "IPinfo", "OpenAI"]
    items = ["<div class='tl-mini-card'><div class='tl-chart-title'>Saúde das fontes</div><div class='tl-sources-list'>"]
    for source in sources:
        items.append(
            f"<div class='tl-source-row'><span>{source}</span><span class='tl-source-ok'>Operacional ●</span></div>"
        )
    items.append("</div><div class='tl-chart-link'>Ver todas as fontes →</div></div>")
    st.markdown("".join(items), unsafe_allow_html=True)


def render(secrets: dict) -> None:
    header_left, header_right = st.columns([4.5, 1.3], vertical_alignment="center")
    with header_left:
        st.markdown("<div class='tl-banner'><h3>ThreatLens</h3><p>IOC Enrichment & Triage Platform</p></div>", unsafe_allow_html=True)
    with header_right:
        if st.button("Analisar IOC", type="primary", use_container_width=True, key="dash_cta"):
            st.session_state["current_page"] = "Analisar IOC"
            st.rerun()

    search_col, button_col = st.columns([8, 1], vertical_alignment="center")
    query = search_col.text_input("", placeholder="🔎  Buscar IOC, domínio, IP, hash ou caso...", label_visibility="collapsed")
    button_col.button("Buscar", use_container_width=True, key="dash_search")

    rows = get_all_analyses()
    if query:
        rows = [r for r in rows if query.lower() in json.dumps(r, ensure_ascii=False).lower()]
    if not rows:
        render_empty_state("Nenhuma análise encontrada", "Execute uma análise de IOC para começar a popular o histórico.")
        return

    stats = get_dashboard_stats()
    latest = get_latest_analysis()
    latest_id = latest["id"] if latest else 0

    cards = st.columns(4)
    with cards[0]:
        render_metric_card("Total de IOCs", str(stats["total"]), "📄", "Ver lista completa →", on_click_key="card_total", target_page="Histórico")
    with cards[1]:
        render_metric_card("Casos abertos", str(stats["open_cases"]), "📁", "Ir para casos →", on_click_key="card_open", target_page="Casos", filter_type="case_status", filter_value="Novo")
    with cards[2]:
        render_metric_card("Risco crítico", str(stats["risk"].get("Crítico", 0)), "🚨", "Filtrar histórico →", on_click_key="card_crit", target_page="Histórico", filter_type="history_risk", filter_value="Crítico")
    with cards[3]:
        render_metric_card("Risco alto", str(stats["risk"].get("Alto", 0)), "⚠️", "Filtrar histórico →", on_click_key="card_high", target_page="Histórico", filter_type="history_risk", filter_value="Alto")

    cards2 = st.columns(4)
    with cards2[0]:
        render_metric_card("Risco médio", str(stats["risk"].get("Médio", 0)), "🟠", "Filtrar histórico →", on_click_key="card_med", target_page="Histórico", filter_type="history_risk", filter_value="Médio")
    with cards2[1]:
        render_metric_card("Risco baixo", str(stats["risk"].get("Baixo", 0)), "🟢", "Filtrar histórico →", on_click_key="card_low", target_page="Histórico", filter_type="history_risk", filter_value="Baixo")
    with cards2[2]:
        render_metric_card("Fontes ativas", str(stats["active_sources"]), "🛞", "Saúde das fontes →", on_click_key="card_sources", target_page="Configurações")
    with cards2[3]:
        render_metric_card("Última análise", stats["last_analysis"], "🕒", "Abrir detalhe →", on_click_key="card_latest", target_page="Detalhe da Análise", filter_type="analysis_id", filter_value=latest_id)

    risk_df = pd.DataFrame(list(stats["risk"].items()), columns=["Risco", "Quantidade"])
    type_df = pd.DataFrame(list(stats["types"].items()), columns=["Tipo", "Quantidade"])
    status_df = pd.DataFrame(list(stats["status"].items()), columns=["Status", "Quantidade"])

    ch1, ch2, ch3, ai_col = st.columns([2.1, 2.1, 2.1, 1.7], vertical_alignment="top")
    with ch1:
        st.markdown("<div class='tl-chart-card'><div class='tl-chart-title'>Distribuição por risco</div>", unsafe_allow_html=True)
        st.plotly_chart(risk_donut(risk_df), use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='tl-chart-link'>Ver detalhes →</div></div>", unsafe_allow_html=True)
    with ch2:
        st.markdown("<div class='tl-chart-card'><div class='tl-chart-title'>Distribuição por tipo de IOC</div>", unsafe_allow_html=True)
        st.plotly_chart(type_bar(type_df), use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='tl-chart-link'>Ver detalhes →</div></div>", unsafe_allow_html=True)
    with ch3:
        st.markdown("<div class='tl-chart-card'><div class='tl-chart-title'>Distribuição por status</div>", unsafe_allow_html=True)
        st.plotly_chart(status_donut(status_df), use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='tl-chart-link'>Ver detalhes →</div></div>", unsafe_allow_html=True)

    with ai_col:
        st.markdown("<div class='tl-mini-card'><div class='tl-chart-title'>Análise Inteligente</div><h4 style='text-align:center;color:#38bdf8'>AI</h4><p style='text-align:center'>Gere insights com IA a partir dos dados coletados.</p>", unsafe_allow_html=True)
        if st.button("Gerar análise IA", type="primary", use_container_width=True, key="dash_ai"):
            if not secrets.get("OPENAI_API_KEY"):
                st.warning("OPENAI_API_KEY não configurada. Configure em Configurações.")
            elif not latest:
                st.info("Sem análise recente para gerar insight.")
            else:
                ai = generate_ai_ioc_analysis(
                    latest.get("ioc", ""),
                    latest.get("ioc_type", ""),
                    {
                        "score": latest.get("score", 0),
                        "risk_level": latest.get("risk_level", "-"),
                        "confidence_level": latest.get("confidence_level", "Baixa"),
                        "sources": json.loads(latest.get("sources_json", "{}")),
                        "evidence": json.loads(latest.get("evidence_json", "{}")),
                        "score_breakdown": json.loads(latest.get("score_breakdown_json", "[]")),
                    },
                    "",
                    secrets.get("OPENAI_API_KEY"),
                )
                if ai.get("status") == "Consultado":
                    st.success("Insight de IA gerado com sucesso.")
                    st.json(ai, expanded=False)
                else:
                    st.warning("Não foi possível gerar insight IA nesta tentativa.")
        st.markdown("</div>", unsafe_allow_html=True)

    lower_left, lower_right = st.columns([3.2, 1.1], vertical_alignment="top")
    with lower_left:
        _render_recent_table(rows)
        sel = st.selectbox("Abrir análise recente", [r["id"] for r in rows[:15]])
        if st.button("Abrir detalhe da análise selecionada", key="open_recent"):
            st.session_state["selected_analysis_id"] = int(sel)
            st.session_state["current_page"] = "Detalhe da Análise"
            st.rerun()
    with lower_right:
        _render_sources_panel()
