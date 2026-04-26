from __future__ import annotations

import json
from html import escape

import pandas as pd
import streamlit as st

from core.analyzer import analyze_ioc
from database.db import create_audit_log, save_analysis
from services.openai_analysis import generate_ai_ioc_analysis
from utils.export import to_csv_bytes
from utils.ui import recommendation_card, render_header, render_risk_badge, render_section_title, render_status_badge


def _build_html_report(result: dict) -> str:
    return f"""
    <html><head><meta charset='utf-8'><title>ThreatLens Report</title></head>
    <body style='font-family:Inter,Arial;background:#020617;color:#f8fafc;padding:20px;'>
    <h1>ThreatLens - IOC Enrichment & Triage Platform</h1>
    <h3>Desenvolvido por Patrick Santos</h3>
    <p><b>Case ID:</b> {escape(result['case_id'])}</p><p><b>IOC:</b> {escape(result['ioc'])}</p>
    <p><b>Tipo:</b> {escape(result['ioc_type'])}</p><p><b>Score:</b> {result['score']}/100</p>
    <p><b>Risco:</b> {escape(result['risk_level'])}</p><p><b>Confiança:</b> {escape(result['confidence_level'])}</p>
    <p><b>Resumo:</b> {escape(result['summary'])}</p>
    <h3>Score breakdown</h3><pre>{escape('\n'.join(result.get('score_breakdown', [])))}</pre>
    <h3>Fontes</h3><pre>{escape(json.dumps(result['sources'], ensure_ascii=False, indent=2))}</pre>
    <h3>Evidências</h3><pre>{escape(json.dumps(result['evidence'], ensure_ascii=False, indent=2))}</pre>
    <h3>KQL</h3><pre>{escape(result['kql'])}</pre>
    </body></html>
    """


def render(secrets: dict) -> None:
    render_header("Painel / Analisar IOC", "Tipos suportados: IP, domínio, URL, MD5, SHA1, SHA256", "🔎")
    ioc_default = st.session_state.pop("reanalyze_ioc", "")
    ioc_input = st.text_input("IOC", value=ioc_default, placeholder="Ex: 8.8.8.8 ou exemplo[.]com")

    if st.button("Analisar IOC", type="primary", use_container_width=True):
        phases = ["Validando IOC", "Identificando tipo", "Consultando fontes externas", "Calculando score", "Gerando recomendação", "Salvando histórico local"]
        bar = st.progress(0)
        for i, p in enumerate(phases, start=1):
            st.caption(f"{i}. {p}")
            bar.progress(int(i / len(phases) * 100))
        with st.spinner("Finalizando análise..."):
            st.session_state["latest_analysis"] = analyze_ioc(ioc_input, secrets)

    result = st.session_state.get("latest_analysis")
    if not result:
        st.info("Insira um IOC e clique em Analisar IOC para iniciar a triagem.")
        return

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(f"**IOC:** `{result['ioc']}`")
        st.markdown(f"**Tipo:** `{result['ioc_type']}`")
    with c2:
        render_risk_badge(result["risk_level"], result["score"])
        render_status_badge(result.get("case_status", "Novo"))
    with c3:
        st.markdown(f"**Confiança:** `{result['confidence_level']}`")
        st.markdown(f"**Case ID:** `{result['case_id']}`")

    render_section_title("Resumo executivo")
    st.write(result["summary"])

    recommendation_card(result["recommendation"])
    st.markdown("- Investigar endpoints que acessaram o IOC.\n- Consultar logs de proxy e DNS.\n- Validar conexões no Microsoft Defender.\n- Avaliar bloqueio apenas após validação interna.")

    render_section_title("Composição do score")
    for line in result.get("score_breakdown", []):
        st.markdown(f"- {line}")

    render_section_title("Veredito por fonte")
    source_table = []
    for source, status in result["sources"].items():
        evidence = result["evidence"].get("urlhaus" if source == "URLhaus" else "vt_stats" if source == "VirusTotal" else "abuse_confidence" if source == "AbuseIPDB" else "ipinfo")
        source_table.append({"Fonte": source, "Status": status, "Resultado": "Sinal relevante" if status == "Consultado" else "Sem sinal", "Evidência": str(evidence)[:120], "Observação": "Baseado em resposta da API"})
    st.dataframe(pd.DataFrame(source_table), use_container_width=True)

    render_section_title("Query KQL")
    st.code(result["kql"], language="kql")
    k1, k2 = st.columns(2)
    k1.download_button("Exportar .kql", data=result["kql"].encode("utf-8"), file_name=f"{result['case_id']}.kql", mime="text/plain")
    k2.text_area("Copiar KQL", value=result["kql"], height=100)


    render_section_title("Análise assistida por IA")
    st.caption("Esta análise é auxiliar e deve ser validada pelo analista.")
    if st.button("Gerar análise IA (sessão atual)"):
        ai = generate_ai_ioc_analysis(result["ioc"], result["ioc_type"], result, result["kql"], secrets.get("OPENAI_API_KEY"))
        if ai.get("status") == "Consultado":
            st.session_state["latest_ai_analysis"] = ai
            st.success("Análise IA gerada para esta sessão.")
        elif ai.get("status") == "Sem API key":
            st.warning("OPENAI_API_KEY ausente. Configure em Configurações.")
        else:
            st.error(f"Falha na análise IA: {ai.get('error', ai.get('status'))}")

    if st.session_state.get("latest_ai_analysis"):
        st.json(st.session_state["latest_ai_analysis"], expanded=False)
    render_section_title("Evidências técnicas")
    st.json(result["evidence"], expanded=False)

    csv_data = to_csv_bytes([result])
    html_report = _build_html_report(result).encode("utf-8")
    a1, a2, a3 = st.columns(3)
    a1.download_button("Exportar CSV", data=csv_data, file_name=f"threatlens_{result['ioc']}.csv", mime="text/csv")
    if a2.download_button("Exportar relatório HTML", data=html_report, file_name=f"report_{result['case_id']}.html", mime="text/html"):
        create_audit_log("Relatório exportado", "analysis", result["case_id"], "Relatório HTML exportado")
    if a3.button("Salvar como caso"):
        save_analysis(result, as_case=True)
        st.success("Caso salvo com sucesso.")

    if st.button("Abrir detalhe da análise"):
        analysis_id = save_analysis(result, as_case=True)
        st.session_state["selected_analysis_id"] = analysis_id
        st.rerun()
