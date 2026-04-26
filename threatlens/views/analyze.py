from __future__ import annotations

import json
from html import escape

import pandas as pd
import streamlit as st

from core.analyzer import analyze_ioc
from database.db import save_analysis
from utils.export import to_csv_bytes
from utils.ui import recommendation_card, render_banner, risk_badge, section_banner


def _build_html_report(result: dict) -> str:
    sources = "".join([f"<li><b>{k}</b>: {v}</li>" for k, v in result["sources"].items()])
    breakdown = "".join([f"<li>{escape(item)}</li>" for item in result.get("score_breakdown", [])])
    return f"""
    <html><head><meta charset='utf-8'><title>ThreatLens Report</title></head>
    <body style='font-family:Arial;background:#0b1220;color:#e2e8f0;padding:20px;'>
    <h1>ThreatLens - IOC Report</h1>
    <p><b>IOC:</b> {escape(result['ioc'])}</p>
    <p><b>Tipo:</b> {escape(result['ioc_type'])}</p>
    <p><b>Score:</b> {result['score']}/100</p>
    <p><b>Risco:</b> {escape(result['risk_level'])}</p>
    <p><b>Recomendação:</b> {escape(result['recommendation'])}</p>
    <h3>Resumo</h3><p>{escape(result['summary'])}</p>
    <h3>Composição do score</h3><ul>{breakdown}</ul>
    <h3>Fontes consultadas</h3><ul>{sources}</ul>
    <h3>KQL</h3><pre>{escape(result['kql'])}</pre>
    <p>Desenvolvido por Patrick Santos</p>
    </body></html>
    """


def render(secrets: dict) -> None:
    render_banner()
    section_banner("Painel de triagem de IOC", "🔎")
    ioc_input = st.text_input("Cole um IOC (IP, domínio, URL, MD5, SHA1, SHA256)")

    if st.button("Analisar IOC", type="primary"):
        with st.spinner("Executando enriquecimento em fontes OSINT..."):
            result = analyze_ioc(ioc_input, secrets)

        a, b = st.columns(2)
        with a:
            risk_badge(result["risk_level"], result["score"])
        with b:
            recommendation_card(result["recommendation"])

        st.markdown("### Resultado da análise")
        st.write(f"**IOC analisado:** `{result['ioc']}`")
        st.write(f"**Tipo detectado:** `{result['ioc_type']}`")
        st.write(f"**Resumo executivo:** {result['summary']}")

        st.markdown("### Composição do score")
        st.write(f"**Score final:** {result['score']}/100")
        for line in result.get("score_breakdown", []):
            st.markdown(f"- {line}")

        st.markdown("### Fontes consultadas")
        sources_df = pd.DataFrame([{"Fonte": k, "Status": v} for k, v in result["sources"].items()])
        st.dataframe(sources_df, use_container_width=True)

        st.markdown("### Evidências técnicas")
        st.json(result["evidence"], expanded=False)

        st.markdown("### Query KQL (Microsoft Defender)")
        st.code(result["kql"], language="kql")
        st.text_area("Copiar query KQL", value=result["kql"], height=140)

        csv_data = to_csv_bytes(
            [
                {
                    "ioc": result["ioc"],
                    "ioc_type": result["ioc_type"],
                    "score": result["score"],
                    "risk_level": result["risk_level"],
                    "recommendation": result["recommendation"],
                    "summary": result["summary"],
                    "score_breakdown": json.dumps(result.get("score_breakdown", []), ensure_ascii=False),
                    "sources": json.dumps(result["sources"], ensure_ascii=False),
                    "evidence": json.dumps(result["evidence"], ensure_ascii=False),
                    "created_at": result["created_at"],
                }
            ]
        )
        html_report = _build_html_report(result).encode("utf-8")
        c1, c2 = st.columns(2)
        c1.download_button("Exportar CSV", data=csv_data, file_name=f"threatlens_{result['ioc']}.csv", mime="text/csv")
        c2.download_button(
            "Gerar relatório HTML",
            data=html_report,
            file_name=f"threatlens_report_{result['ioc']}.html",
            mime="text/html",
        )

        if result["ioc_type"] != "unknown":
            save_analysis(result)
            st.success("Análise salva no histórico SQLite.")
