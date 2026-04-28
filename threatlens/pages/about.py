from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("ℹ️ Sobre o ThreatLens")
    st.markdown(
        """
        **ThreatLens - IOC Enrichment & Triage Platform** é uma ferramenta para Blue Team/SOC
        destinada a enriquecer IOCs com fontes públicas e apoiar triagem operacional.

        ### Fontes utilizadas
        - VirusTotal API v3
        - AbuseIPDB
        - URLhaus
        - IPinfo (opcional)

        ### Limitações
        - Dependência de APIs públicas e seus limites/rate limits.
        - Resultados podem variar por tempo, contexto e disponibilidade das fontes.
        - Não substitui validação em logs e telemetria interna.

        ### Aviso
        O app **não realiza bloqueio automático** em firewall/EDR.
        As recomendações apoiam a decisão do analista.
        """
    )
