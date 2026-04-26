from __future__ import annotations

from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

RISK_STYLES = {
    "Baixo": ("#065f46", "#34d399"),
    "Médio": ("#78350f", "#fbbf24"),
    "Alto": ("#7c2d12", "#fb923c"),
    "Crítico": ("#7f1d1d", "#f87171"),
}


def render_logo(width: int = 260) -> None:
    path = ASSETS_DIR / "logo.svg"
    if path.exists():
        st.image(str(path), width=width)


def render_banner() -> None:
    path = ASSETS_DIR / "blue_team_banner.svg"
    if path.exists():
        st.image(str(path), use_container_width=True)


def section_banner(text: str, icon: str = "🛡️") -> None:
    st.markdown(f"<div class='tl-banner'><b>{icon} {text}</b></div>", unsafe_allow_html=True)


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"<div class='tl-card'><div class='tl-metric'>{value}</div><div class='tl-label'>{label}</div></div>",
        unsafe_allow_html=True,
    )


def risk_badge(risk_level: str, score: int) -> None:
    bg, fg = RISK_STYLES.get(risk_level, ("#374151", "#d1d5db"))
    st.markdown(
        f"""
        <div class='tl-card'>
          <span class='tl-badge' style='background:{bg};color:{fg};'>Risco {risk_level}</span>
          <h3 style='margin:.6rem 0 .2rem 0;'>Score {score}/100</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_card(text: str) -> None:
    st.markdown(
        f"<div class='tl-card'><h4>🎯 Recomendação operacional</h4><p>{text}</p></div>",
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown("<div class='tl-footer'>Desenvolvido por Patrick Santos</div>", unsafe_allow_html=True)
