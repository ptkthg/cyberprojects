from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_all_analyses, seed_demo_data
from utils.ui import metric_card, render_banner, section_banner


def _active_sources(df: pd.DataFrame) -> int:
    active = set()
    for raw in df["sources_json"].fillna("{}").tolist():
        try:
            data = json.loads(raw)
            for source, status in data.items():
                if status == "Consultado":
                    active.add(source)
        except Exception:
            continue
    return len(active)


def render() -> None:
    render_banner()
    section_banner("ThreatLens Dashboard - SOC Overview", "📊")

    top_l, top_r = st.columns([3, 1])
    with top_r:
        if st.button("Carregar modo demo"):
            seed_demo_data()
            st.success("Dados demo carregados com sucesso.")
            st.rerun()

    rows = get_all_analyses()
    if not rows:
        with top_l:
            st.markdown(
                """
                <div class='tl-card' style='text-align:center;padding:28px;'>
                    <h3>Sem análises ainda</h3>
                    <p>Use <b>Analisar IOC</b> ou carregue o <b>modo demo</b> para visualizar o painel.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    df = pd.DataFrame(rows)
    last_analysis = df.iloc[0]["updated_at"] if not df.empty else "-"
    open_cases = int(df[~df["case_status"].isin(["Encerrado", "Falso positivo"])].shape[0])

    r1 = st.columns(4)
    with r1[0]:
        metric_card("Total de IOCs", str(len(df)))
    with r1[1]:
        metric_card("Casos abertos", str(open_cases))
    with r1[2]:
        metric_card("Críticos", str((df["risk_level"] == "Crítico").sum()))
    with r1[3]:
        metric_card("Altos", str((df["risk_level"] == "Alto").sum()))

    r2 = st.columns(4)
    with r2[0]:
        metric_card("Médios", str((df["risk_level"] == "Médio").sum()))
    with r2[1]:
        metric_card("Baixos", str((df["risk_level"] == "Baixo").sum()))
    with r2[2]:
        metric_card("Última análise", str(last_analysis))
    with r2[3]:
        metric_card("Fontes ativas", str(_active_sources(df)))

    risk_counts = df["risk_level"].value_counts().reindex(["Baixo", "Médio", "Alto", "Crítico"], fill_value=0).reset_index()
    risk_counts.columns = ["Risco", "Quantidade"]

    type_counts = df["ioc_type"].replace({"ipv4": "IP", "domain": "Domínio", "url": "URL", "md5": "Hash", "sha1": "Hash", "sha256": "Hash"}).value_counts().reset_index()
    type_counts.columns = ["Tipo", "Quantidade"]

    status_counts = df["case_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Quantidade"]

    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(px.bar(risk_counts, x="Risco", y="Quantidade", color="Risco", title="Distribuição por risco"), use_container_width=True)
    c2.plotly_chart(px.bar(type_counts, x="Tipo", y="Quantidade", color="Tipo", title="Distribuição por tipo"), use_container_width=True)
    c3.plotly_chart(px.bar(status_counts, x="Status", y="Quantidade", color="Status", title="Distribuição por status"), use_container_width=True)

    st.markdown("### Últimos casos criados")
    st.dataframe(
        df[["case_id", "updated_at", "ioc", "ioc_type", "score", "risk_level", "confidence_level", "case_status"]]
        .rename(columns={"case_id": "Case ID", "updated_at": "Data", "ioc": "IOC", "ioc_type": "Tipo", "score": "Score", "risk_level": "Risco", "confidence_level": "Confiança", "case_status": "Status"})
        .head(10),
        use_container_width=True,
    )
