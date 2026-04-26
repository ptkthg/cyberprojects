from __future__ import annotations

import streamlit as st

from utils.ui import render_banner, section_banner


def _status(value: str | None) -> str:
    return "✅ Configurada" if value else "❌ Ausente"


def render(secrets: dict) -> None:
    render_banner()
    section_banner("Configuração segura de integrações", "⚙️")

    st.write(f"**VirusTotal:** {_status(secrets.get('VIRUSTOTAL_API_KEY'))}")
    st.write(f"**AbuseIPDB:** {_status(secrets.get('ABUSEIPDB_API_KEY'))}")
    st.write(f"**URLhaus:** {_status(secrets.get('URLHAUS_API_KEY'))} (opcional)")
    st.write(f"**IPinfo:** {_status(secrets.get('IPINFO_API_KEY'))}")

    st.markdown("### Configure em `.streamlit/secrets.toml`")
    st.code(
        'VIRUSTOTAL_API_KEY = ""\nABUSEIPDB_API_KEY = ""\nURLHAUS_API_KEY = ""\nIPINFO_API_KEY = ""',
        language="toml",
    )
