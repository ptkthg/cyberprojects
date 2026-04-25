from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from database.db import init_db
from pages import about, analyze, batch, dashboard, history, settings

load_dotenv()


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
    }


def main() -> None:
    st.set_page_config(page_title="ThreatLens", page_icon="🛡️", layout="wide")
    init_db()
    secrets = load_secrets()

    st.sidebar.title("ThreatLens")
    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Analisar IOC", "Análise em lote", "Histórico", "Configurações", "Sobre"],
    )

    if page == "Dashboard":
        dashboard.render()
    elif page == "Analisar IOC":
        analyze.render(secrets)
    elif page == "Análise em lote":
        batch.render(secrets)
    elif page == "Histórico":
        history.render()
    elif page == "Configurações":
        settings.render(secrets)
    else:
        about.render()


if __name__ == "__main__":
    main()
