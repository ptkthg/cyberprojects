from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from core.analyzer import analyze_ioc
from core.ioc_detector import detect_ioc_type
from database.db import save_analysis
from utils.export import to_csv_bytes
from utils.ui import render_empty_state, render_header


def _read_iocs(uploaded_file) -> list[str]:
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        if "ioc" not in df.columns:
            raise ValueError("CSV precisa da coluna 'ioc'.")
        return [str(v).strip() for v in df["ioc"].dropna().tolist() if str(v).strip()]
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    return [line.strip() for line in content.splitlines() if line.strip()]


def render(secrets: dict) -> None:
    render_header("Análise em Lote", "Upload CSV/TXT e análise robusta com progresso", "📥")
    file = st.file_uploader("Arquivo de IOC", type=["csv", "txt"])
    if not file:
        render_empty_state("Sem arquivo", "Faça upload de um CSV com coluna ioc ou TXT com um IOC por linha.")
        return

    try:
        iocs = _read_iocs(file)
    except Exception as exc:
        st.error(str(exc))
        return

    preview = []
    for ioc in iocs[:50]:
        norm, ioc_type = detect_ioc_type(ioc)
        preview.append({"ioc": norm, "tipo_detectado": ioc_type})
    st.dataframe(pd.DataFrame(preview), use_container_width=True)

    if st.button("Analisar todos", type="primary"):
        results = []
        progress = st.progress(0)
        for idx, ioc in enumerate(iocs, start=1):
            try:
                result = analyze_ioc(ioc, secrets)
                if result["ioc_type"] != "unknown":
                    analysis_id = save_analysis(result, as_case=True)
                    result["analysis_id"] = analysis_id
                results.append(result)
            except Exception as exc:
                results.append({"ioc": ioc, "ioc_type": "unknown", "risk_level": "Baixo", "score": 0, "confidence_level": "Baixa", "error": str(exc)})
            progress.progress(int(idx / len(iocs) * 100))

        df = pd.DataFrame(results)
        risk_filter = st.selectbox("Filtrar severidade", ["Todos", "Crítico", "Alto", "Médio", "Baixo"])
        if risk_filter != "Todos":
            df = df[df["risk_level"] == risk_filter]
        st.dataframe(df[[c for c in ["analysis_id", "case_id", "ioc", "ioc_type", "score", "risk_level", "confidence_level"] if c in df.columns]], use_container_width=True)

        c1, c2 = st.columns(2)
        c1.download_button("Exportar CSV", data=to_csv_bytes(df.to_dict(orient="records")), file_name="batch_results.csv", mime="text/csv")
        c2.download_button("Exportar JSON", data=json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2).encode("utf-8"), file_name="batch_results.json", mime="application/json")

        if "analysis_id" in df.columns and not df["analysis_id"].dropna().empty:
            aid = st.selectbox("Abrir detalhe de IOC", [int(v) for v in df["analysis_id"].dropna().tolist()])
            if st.button("Abrir detalhe"):
                st.session_state["selected_analysis_id"] = int(aid)
                st.rerun()
