from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from core.navigation import DETAIL_PAGE, VALID_PAGES, normalize_page_name
from database.db import get_dashboard_stats, init_db
from utils.styles import apply_global_styles
from utils.ui import render_footer, render_status_bar, render_top_navigation
from views import about, analysis_detail, analyze, batch, cases, dashboard, history, settings

load_dotenv()

PAGES = VALID_PAGES


def load_secrets() -> dict:
    def pick(name: str) -> str | None:
        if name in st.secrets:
            return st.secrets.get(name)
        return os.getenv(name)

    return {
        "VIRUSTOTAL_API_KEY": pick("VIRUSTOTAL_API_KEY"),
        "ABUSEIPDB_API_KEY": pick("ABUSEIPDB_API_KEY"),
        "URLHAUS_API_KEY": pick("URLHAUS_API_KEY"),
        "IPINFO_API_KEY": pick("IPINFO_API_KEY"),
        "OPENAI_API_KEY": pick("OPENAI_API_KEY"),
    }


def main() -> None:
    st.set_page_config(page_title="ThreatLens", page_icon="🛡️", layout="wide")
    st.set_option("client.showSidebarNavigation", False)
    apply_global_styles()
    init_db()
    secrets = load_secrets()

    current = normalize_page_name(st.session_state.get("current_page"), fallback="Painel")
    st.session_state["current_page"] = current
    if current == DETAIL_PAGE and st.session_state.get("selected_analysis_id"):
        nav_options = PAGES + [DETAIL_PAGE]
    else:
        nav_options = PAGES

    selected = render_top_navigation(nav_options, current)
    st.session_state["current_page"] = selected

    stats = get_dashboard_stats()
    mode = "Demo" if stats.get("total", 0) and "TL-DEMO" in (str(st.session_state.get("selected_analysis_id", ""))) else "Produção"
    render_status_bar(stats.get("active_sources", 0), mode)

    if selected == "Painel":
        dashboard.render(secrets)
    elif selected == "Analisar IOC":
        analyze.render(secrets)
    elif selected == "Análise em Lote":
        batch.render(secrets)
    elif selected == "Histórico":
        history.render(secrets)
    elif selected == "Casos":
        cases.render(secrets)
    elif selected == "Configurações":
        settings.render(secrets)
    elif selected == DETAIL_PAGE:
        analysis_detail.render(secrets)
    else:
        about.render(secrets)

    render_footer()


if __name__ == "__main__":
    main()
