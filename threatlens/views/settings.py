from __future__ import annotations

import pandas as pd
import streamlit as st

from database.db import clear_history, get_all_analyses
from utils.export import to_csv_bytes
from utils.ui import render_empty_state, render_header, render_metric_card


def _status(value: str | None) -> str:
    return "Configurada" if value else "Ausente"


def render(secrets: dict) -> None:
    render_header("Configurações", "Estado de integrações, demo e preferências locais", "⚙️")

    sources = [
        ("VirusTotal", _status(secrets.get("VIRUSTOTAL_API_KEY"))),
        ("AbuseIPDB", _status(secrets.get("ABUSEIPDB_API_KEY"))),
        ("URLhaus", _status(secrets.get("URLHAUS_API_KEY"))),
        ("IPinfo", _status(secrets.get("IPINFO_API_KEY"))),
        ("GreyNoise", "Não implementada"),
        ("Shodan", "Não implementada"),
        ("MISP", "Não implementada"),
        ("AlienVault OTX", "Não implementada"),
        ("ThreatFox", "Não implementada"),
    ]

    cols = st.columns(3)
    for idx, (name, status) in enumerate(sources):
        with cols[idx % 3]:
            render_metric_card(name, status, "🛰️")

    st.markdown("### Preferências")
    st.selectbox("Severidade mínima para alerta visual", ["Baixo", "Médio", "Alto", "Crítico"])
    st.selectbox("Formato padrão de exportação", ["CSV", "JSON", "HTML"])
    st.toggle("Modo demo", value=False)
    st.toggle("Tema escuro", value=True, disabled=True)

    st.markdown("### Segurança")
    st.code('VIRUSTOTAL_API_KEY = ""\nABUSEIPDB_API_KEY = ""\nURLHAUS_API_KEY = ""\nIPINFO_API_KEY = ""', language="toml")
    st.caption("As chaves devem ser configuradas localmente em .streamlit/secrets.toml")

    rows = get_all_analyses()
    if not rows:
        render_empty_state("Sem histórico para exportar", "Analise IOCs para habilitar exportações de histórico.")
    else:
        st.download_button("Exportar histórico", data=to_csv_bytes(pd.DataFrame(rows).to_dict(orient="records")), file_name="historico_total.csv", mime="text/csv")

    if st.button("Limpar histórico", type="secondary"):
        clear_history()
        st.success("Histórico limpo com sucesso.")
        st.rerun()
