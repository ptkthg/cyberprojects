from __future__ import annotations

import streamlit as st

from utils.ui import render_header, render_logo, render_social_links


def render(secrets: dict) -> None:
    render_logo(260)
    render_header("ThreatLens", "IOC Enrichment & Triage Platform", "ℹ️")
    st.markdown(
        """
        ThreatLens é uma plataforma de enriquecimento, triagem e documentação de indicadores de ameaça criada para apoiar equipes Blue Team, SOC e profissionais de segurança da informação na análise rápida, padronizada e rastreável de IOCs.

        **Como funciona:**
        1. Detecta automaticamente o tipo do IOC.
        2. Consulta múltiplas fontes OSINT.
        3. Gera score, risco, confiança e recomendação.
        4. Armazena histórico e casos com trilha de auditoria.

        **Tipos suportados:** IPv4, domínio, URL, MD5, SHA1 e SHA256.

        **Fontes atuais:** VirusTotal, AbuseIPDB, URLhaus e IPinfo.

        **Limitações:** depende da disponibilidade das APIs externas e não substitui telemetria interna.

        **Uso responsável:** O ThreatLens apoia a decisão do analista, mas não executa bloqueios automáticos.

        **Desenvolvido por Patrick Santos**.
        """
    )
    render_social_links()
