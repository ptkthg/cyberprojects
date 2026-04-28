from __future__ import annotations

import streamlit as st


def _status(value: str | None) -> str:
    return "✅ Configurada" if value else "❌ Ausente"


def render(secrets: dict) -> None:
    st.title("⚙️ Configurações")
    st.markdown("### Status das API keys")
    st.write(f"**VirusTotal:** {_status(secrets.get('VIRUSTOTAL_API_KEY'))}")
    st.write(f"**AbuseIPDB:** {_status(secrets.get('ABUSEIPDB_API_KEY'))}")
    st.write("**URLhaus:** ✅ Não requer API key para endpoint público")
    st.write(f"**IPinfo:** {_status(secrets.get('IPINFO_API_KEY'))}")

    st.markdown("### Como configurar")
    st.code(
        """Crie o arquivo .streamlit/secrets.toml com o conteúdo:

VIRUSTOTAL_API_KEY = "..."
ABUSEIPDB_API_KEY = "..."
IPINFO_API_KEY = "..."""  # noqa: S105
    )
    st.caption("As chaves nunca são exibidas em tela e não são armazenadas no banco.")
