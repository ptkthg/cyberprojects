from __future__ import annotations

import streamlit as st

from utils.ui import render_banner, render_logo, section_banner


def render() -> None:
    render_banner()
    render_logo(width=300)
    section_banner("ThreatLens - IOC Enrichment & Triage Platform", "ℹ️")

    st.markdown(
        """
        ### Desenvolvido por Patrick Santos

        **ThreatLens** é uma plataforma de enriquecimento e triagem de IOCs para Blue Team/SOC.

        **Objetivo do projeto**
        - Acelerar triagem de IOC para SOC N1/N2.
        - Consolidar sinais de múltiplas fontes OSINT.
        - Apoiar decisão operacional sem bloqueio automático.

        **Fontes utilizadas**
        - VirusTotal API v3
        - AbuseIPDB
        - URLhaus
        - IPinfo

        **Tecnologias**
        - Python, Streamlit, SQLite, Pandas, Requests e APIs OSINT.

        **Limitações**
        - Dependência de disponibilidade/rate limit das APIs públicas.
        - Resultado precisa de validação em telemetria interna.

        **Aviso de segurança**
        O app apoia a decisão do analista, mas não faz bloqueio automático.
        """
    )


    st.markdown("### Identidade visual Blue Team")
    cols = st.columns(4)
    cols[0].image("assets/shield.svg", width=64)
    cols[1].image("assets/radar.svg", width=64)
    cols[2].image("assets/network.svg", width=64)
    cols[3].image("assets/threat.svg", width=64)

    c1, c2, c3 = st.columns(3)
    c1.success("🔎 Enriquecimento multi-fonte")
    c2.info("📊 Score + priorização")
    c3.warning("🛡️ Uso responsável em SOC")
