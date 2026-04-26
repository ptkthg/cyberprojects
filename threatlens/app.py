from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from database.db import init_db
from utils.styles import apply_global_styles
from utils.ui import render_footer, render_logo
from views import about, analysis_detail, analyze, batch, cases, dashboard, history, settings

load_dotenv()

PAGE_MAP = {
    "📊 Painel": "painel",
    "🔎 Analisar IOC": "analisar",
    "📥 Análise em Lote": "lote",
    "🕒 Histórico": "historico",
    "📁 Casos": "casos",
    "⚙️ Configurações": "config",
    "ℹ️ Sobre": "sobre",
}


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
    apply_global_styles()
    init_db()
    secrets = load_secrets()

    with st.sidebar:
        render_logo(width=220)
        st.markdown("**ThreatLens**")
        st.caption("IOC Enrichment & Triage Platform")
        st.divider()
        options = list(PAGE_MAP.keys())
        if st.session_state.get("selected_analysis_id"):
            options.append("🧾 Detalhe da Análise")
        current = st.session_state.get("current_page")
        default_idx = options.index(current) if current in options else 0
        selected = st.radio("Navegação", options, index=default_idx)
        st.session_state["current_page"] = selected
        st.caption("Desenvolvido por Patrick Santos")

    page = PAGE_MAP.get(selected)
    if selected == "🧾 Detalhe da Análise":
        analysis_detail.render(secrets)
    elif page == "painel":
        dashboard.render(secrets)
    elif page == "analisar":
        analyze.render(secrets)
    elif page == "lote":
        batch.render(secrets)
    elif page == "historico":
        history.render(secrets)
    elif page == "casos":
        cases.render(secrets)
    elif page == "config":
        settings.render(secrets)
    else:
        about.render(secrets)

    render_footer()


if __name__ == "__main__":
    main()
