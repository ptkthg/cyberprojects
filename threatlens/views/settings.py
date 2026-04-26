from __future__ import annotations

import pandas as pd
import streamlit as st

from database.db import clear_history, get_all_analyses
from utils.export import to_csv_bytes
from utils.ui import render_empty_state, render_header, render_metric_card


def _status(value: str | None) -> str:
    return "Configurada" if value else "Ausente"


def render(secrets: dict) -> None:
    render_header("Configurações", "Saúde das Fontes e Análise IA", "⚙️")

    sources = [
        ("VirusTotal", _status(secrets.get("VIRUSTOTAL_API_KEY"))),
        ("AbuseIPDB", _status(secrets.get("ABUSEIPDB_API_KEY"))),
        ("URLhaus", _status(secrets.get("URLHAUS_API_KEY"))),
        ("IPinfo", _status(secrets.get("IPINFO_API_KEY"))),
        ("OpenAI", _status(secrets.get("OPENAI_API_KEY"))),
        ("GreyNoise", "Não implementada"),
        ("Shodan", "Não implementada"),
        ("MISP", "Não implementada"),
    ]
    st.markdown("### Saúde das Fontes")
    cols = st.columns(4)
    for i, (name, status) in enumerate(sources):
        with cols[i % 4]:
            render_metric_card(name, status, "🛰️")

    st.markdown("### Análise IA")
    st.write(f"**OpenAI API:** {_status(secrets.get('OPENAI_API_KEY'))}")
    st.write("**Modelo usado:** gpt-4.1-mini")
    st.write(f"**Status:** {'Disponível' if secrets.get('OPENAI_API_KEY') else 'Indisponível'}")
    st.warning("A análise IA é opcional, auxiliar e deve ser validada pelo analista. Não enviar dados sensíveis.")
    st.code('OPENAI_API_KEY = ""', language="toml")

    st.markdown("### Preferências")
    st.selectbox("Severidade mínima para alerta visual", ["Baixo", "Médio", "Alto", "Crítico"])
    st.selectbox("Formato padrão de exportação", ["CSV", "JSON", "HTML"])

    rows = get_all_analyses()
    if not rows:
        render_empty_state("Sem histórico para exportar", "Analise IOCs para habilitar exportações de histórico.")
    else:
        st.download_button("Exportar histórico", data=to_csv_bytes(pd.DataFrame(rows).to_dict(orient="records")), file_name="historico_total.csv", mime="text/csv")

    if st.button("Limpar histórico", type="secondary"):
        clear_history(); st.success("Histórico limpo com sucesso."); st.rerun()
