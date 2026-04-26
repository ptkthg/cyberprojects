from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import list_analyses


def render() -> None:
    st.title("📊 Dashboard")
    rows = list_analyses()
    if not rows:
        st.info("Ainda não há análises salvas.")
        return

    df = pd.DataFrame(rows)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de IOCs", len(df))
    col2.metric("Risco crítico", int((df["risk_level"] == "Crítico").sum()))
    col3.metric("Tipos únicos", int(df["ioc_type"].nunique()))

    risk_counts = df["risk_level"].value_counts().reset_index()
    risk_counts.columns = ["risk", "count"]

    type_map = df["ioc_type"].replace({"ipv4": "IP", "domain": "Domínio", "url": "URL", "md5": "Hash", "sha1": "Hash", "sha256": "Hash"})
    type_counts = type_map.value_counts().reset_index()
    type_counts.columns = ["type", "count"]

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.pie(risk_counts, names="risk", values="count", title="Distribuição por risco"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(type_counts, x="type", y="count", title="Distribuição por tipo"), use_container_width=True)

    st.markdown("#### Últimas 10 análises")
    st.dataframe(df.head(10)[["created_at", "ioc", "ioc_type", "score", "risk_level"]], use_container_width=True)
