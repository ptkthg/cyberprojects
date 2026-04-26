from __future__ import annotations

import streamlit as st

from utils.ui import render_banner, render_logo, section_banner


def render() -> None:
    render_banner()
    render_logo(width=320)
    section_banner("ThreatLens - IOC Enrichment & Triage Platform", "ℹ️")

    st.markdown(
        """
        ### Desenvolvido por Patrick Santos

        O **ThreatLens** foi projetado para evoluir o SOC de um processo reativo para uma
        triagem operacional orientada a evidências, com foco em produtividade de analistas N1/N2.

        #### Objetivo
        - Priorizar IOCs com score explicável.
        - Consolidar sinais de múltiplas fontes OSINT.
        - Estruturar investigação com conceito de caso e auditoria.

        #### Fontes e tecnologias
        - VirusTotal, AbuseIPDB, URLhaus e IPinfo.
        - Python, Streamlit, SQLite, Pandas e Requests.

        #### Segurança e responsabilidade
        - O app **apoia** a decisão do analista.
        - O app **não executa bloqueio automático** em firewall, EDR ou qualquer ferramenta.
        - Nunca armazena API keys no banco e não exibe seus valores na UI.
        """
    )

    st.markdown("### Recursos")
    c1, c2, c3 = st.columns(3)
    c1.success("📁 Central de Casos")
    c2.info("📊 Score + Confiança")
    c3.warning("🧾 Trilha de Auditoria")
