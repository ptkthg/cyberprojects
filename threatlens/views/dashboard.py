from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_all_analyses
from utils.ui import metric_card, render_banner, section_banner


def render() -> None:
    render_banner()
    section_banner("Painel SOC - Visão Geral de IOC", "📊")

    rows = get_all_analyses()
    if not rows:
        st.markdown(
            """
            <div class='tl-card' style='text-align:center;padding:28px;'>
                <h3>Sem análises ainda</h3>
                <p>Inicie pela tela <b>Analisar IOC</b> para popular o dashboard.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(rows)
    last_analysis = df.iloc[0]["created_at"] if not df.empty else "-"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Total de IOCs analisados", str(len(df)))
    with m2:
        metric_card("Críticos", str((df["risk_level"] == "Crítico").sum()))
    with m3:
        metric_card("Altos", str((df["risk_level"] == "Alto").sum()))
    with m4:
        metric_card("Médios", str((df["risk_level"] == "Médio").sum()))

    m5, m6, m7 = st.columns(3)
    with m5:
        metric_card("Baixos", str((df["risk_level"] == "Baixo").sum()))
    with m6:
        metric_card("Última análise", str(last_analysis))
    with m7:
        metric_card("Tipos únicos", str(df["ioc_type"].nunique()))

    risk_counts = (
        df["risk_level"]
        .value_counts()
        .reindex(["Baixo", "Médio", "Alto", "Crítico"], fill_value=0)
        .reset_index()
    )
    risk_counts.columns = ["Risco", "Quantidade"]

    type_map = df["ioc_type"].replace(
        {"ipv4": "IP", "domain": "Domínio", "url": "URL", "md5": "Hash", "sha1": "Hash", "sha256": "Hash"}
    )
    type_counts = type_map.value_counts().reset_index()
    type_counts.columns = ["Tipo", "Quantidade"]

    c1, c2 = st.columns(2)
    with c1:
        fig_risk = px.bar(risk_counts, x="Risco", y="Quantidade", color="Risco", title="Distribuição por risco")
        st.plotly_chart(fig_risk, use_container_width=True)
    with c2:
        fig_type = px.bar(type_counts, x="Tipo", y="Quantidade", color="Tipo", title="Distribuição por tipo")
        st.plotly_chart(fig_type, use_container_width=True)

    st.markdown("### Últimos registros")
    friendly = df[["created_at", "ioc", "ioc_type", "score", "risk_level", "recommendation"]].rename(
        columns={
            "created_at": "Data",
            "ioc": "IOC",
            "ioc_type": "Tipo",
            "score": "Score",
            "risk_level": "Risco",
            "recommendation": "Recomendação",
        }
    )
    st.dataframe(friendly.head(10), use_container_width=True)
