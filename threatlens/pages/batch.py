from __future__ import annotations

import pandas as pd
import streamlit as st

from core.analyzer import analyze_ioc
from database.db import insert_analysis
from utils.export import to_csv_bytes


def _read_iocs(uploaded_file) -> list[str]:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        if "ioc" not in df.columns:
            raise ValueError("CSV deve conter uma coluna chamada 'ioc'.")
        return [str(v) for v in df["ioc"].dropna().tolist()]
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    return [line.strip() for line in content.splitlines() if line.strip()]


def render(secrets: dict) -> None:
    st.title("🧪 Análise em lote")
    file = st.file_uploader("Upload CSV/TXT com IOCs", type=["csv", "txt"])
    if file and st.button("Analisar lote", type="primary"):
        try:
            iocs = _read_iocs(file)
        except Exception as exc:
            st.error(str(exc))
            return

        results = []
        progress = st.progress(0)
        for idx, ioc in enumerate(iocs, start=1):
            result = analyze_ioc(ioc, secrets)
            results.append(
                {
                    "ioc": result["ioc"],
                    "ioc_type": result["ioc_type"],
                    "score": result["score"],
                    "risk_level": result["risk_level"],
                    "recommendation": result["recommendation"],
                    "sources": ", ".join([f"{k}:{v}" for k, v in result["sources"].items()]),
                }
            )
            if result["ioc_type"] != "unknown":
                insert_analysis(result)
            progress.progress(idx / len(iocs))

        st.success(f"{len(results)} IOCs analisados.")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        st.download_button(
            "Exportar consolidado em CSV",
            data=to_csv_bytes(results),
            file_name="threatlens_batch_results.csv",
            mime="text/csv",
        )
