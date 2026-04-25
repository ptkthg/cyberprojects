from __future__ import annotations

import streamlit as st


RISK_COLORS = {
    "Baixo": "#10B981",
    "Médio": "#F59E0B",
    "Alto": "#F97316",
    "Crítico": "#EF4444",
}


def risk_badge(risk_level: str, score: int) -> None:
    color = RISK_COLORS.get(risk_level, "#6B7280")
    st.markdown(
        f"""
        <div style='padding:14px;border-radius:12px;background:{color}22;border:1px solid {color};'>
            <h4 style='margin:0;color:{color};'>Risco {risk_level}</h4>
            <p style='margin:4px 0 0 0;'>Score: <b>{score}</b>/100</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_card(text: str) -> None:
    st.markdown(
        f"""
        <div style='padding:14px;border-radius:12px;background:#1F2937;border:1px solid #374151;'>
            <h4 style='margin:0;color:#93C5FD;'>Recomendação operacional</h4>
            <p style='margin:6px 0 0 0;'>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
