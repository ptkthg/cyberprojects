from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from core.analyzer import analyze_ioc
from database.db import insert_analysis
from utils.export import to_csv_bytes
from utils.ui import recommendation_card, risk_badge


def render(secrets: dict) -> None:
    st.title("🔎 Analisar IOC")
    ioc_input = st.text_input("Cole um IOC (IP, domínio, URL, MD5, SHA1, SHA256)")

    if st.button("Analisar IOC", type="primary"):
        with st.spinner("Enriquecendo IOC em fontes públicas..."):
            result = analyze_ioc(ioc_input, secrets)

        st.subheader("Resultado da análise")
        cols = st.columns([1, 1])
        with cols[0]:
            risk_badge(result["risk_level"], result["score"])
        with cols[1]:
            recommendation_card(result["recommendation"])

        st.markdown(f"**Indicador:** `{result['ioc']}`")
        st.markdown(f"**Tipo detectado:** `{result['ioc_type']}`")
        st.markdown(f"**Resumo executivo:** {result['summary']}")
        st.markdown(f"**Data/Hora:** {result['created_at']}")

        sources_df = pd.DataFrame(
            [{"fonte": name, "status": status} for name, status in result["sources"].items()]
        )
        st.markdown("#### Resultado por fonte")
        st.dataframe(sources_df, use_container_width=True)

        st.markdown("#### Evidências técnicas")
        st.json(result["evidence"], expanded=False)

        csv_data = to_csv_bytes(
            [
                {
                    "ioc": result["ioc"],
                    "ioc_type": result["ioc_type"],
                    "score": result["score"],
                    "risk_level": result["risk_level"],
                    "recommendation": result["recommendation"],
                    "summary": result["summary"],
                    "sources": json.dumps(result["sources"], ensure_ascii=False),
                    "evidence": json.dumps(result["evidence"], ensure_ascii=False),
                    "created_at": result["created_at"],
                }
            ]
        )
        st.download_button(
            "Exportar resultado em CSV",
            data=csv_data,
            file_name=f"threatlens_{result['ioc']}.csv",
            mime="text/csv",
        )

        st.code(result["kql"], language="kql")
        st.caption("Copie a query KQL acima para Microsoft Defender Advanced Hunting.")

        if result["ioc_type"] != "unknown":
            insert_analysis(result)
            st.success("Análise salva no histórico local (SQLite).")
