from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.navigation import go_to_page, open_analysis_detail, set_case_filter, set_history_filter

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

RISK_STYLES = {"Baixo": ("#0b3b5c", "#7dd3fc"), "Médio": ("#78350f", "#fbbf24"), "Alto": ("#7c2d12", "#fb923c"), "Crítico": ("#7f1d1d", "#f87171")}
STATUS_COLORS = {"Novo": "#38bdf8", "Em análise": "#60a5fa", "Escalado": "#f59e0b", "Resolvido": "#22c55e", "Falso positivo": "#94a3b8", "Monitorado": "#a78bfa", "Bloqueado": "#ef4444"}


def render_logo(width: int = 240) -> None:
    p = ASSETS_DIR / "logo.svg"
    if p.exists():
        st.image(str(p), width=width)


def render_header(title: str, subtitle: str, icon: str = "🛡️") -> None:
    st.markdown(f"<div class='tl-banner'><h3>{icon} {title}</h3><p style='margin:0;color:#94a3b8'>{subtitle}</p></div>", unsafe_allow_html=True)


def render_section_title(text: str) -> None:
    st.markdown(f"### {text}")


def render_metric_card(
    title: str,
    value: str,
    icon: str = "📌",
    subtitle: str = "",
    risk_level: str | None = None,
    on_click_key: str | None = None,
    target_page: str | None = None,
    filter_type: str | None = None,
    filter_value: str | int | None = None,
) -> None:
    badge = f"<div class='tl-label'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"<div class='tl-card'><div class='tl-metric'>{icon} {value}</div><div class='tl-label'>{title}</div>{badge}</div>", unsafe_allow_html=True)
    if on_click_key and st.button("Abrir", key=on_click_key):
        if target_page:
            go_to_page(target_page)
        if filter_type and filter_value is not None:
            if filter_type.startswith("history_"):
                set_history_filter(filter_type.replace("history_", ""), str(filter_value))
            elif filter_type.startswith("case_"):
                set_case_filter(filter_type.replace("case_", ""), str(filter_value))
            elif filter_type == "analysis_id":
                open_analysis_detail(int(filter_value))
        st.rerun()


def render_risk_badge(risk_level: str, score: int = 0) -> None:
    bg, fg = RISK_STYLES.get(risk_level, ("#334155", "#cbd5e1"))
    st.markdown(f"<span class='tl-badge' style='background:{bg};color:{fg};'>Risco {risk_level} • {score}/100</span>", unsafe_allow_html=True)


def risk_badge(risk_level: str, score: int) -> None:
    render_risk_badge(risk_level, score)


def render_status_badge(status: str) -> None:
    color = STATUS_COLORS.get(status, "#94a3b8")
    st.markdown(f"<span class='tl-badge' style='background:#0b1220;color:{color};border:1px solid {color};'>Status {status}</span>", unsafe_allow_html=True)


def recommendation_card(text: str) -> None:
    st.markdown(f"<div class='tl-card'><b>Ações recomendadas</b><p style='margin:.4rem 0'>{text}</p></div>", unsafe_allow_html=True)


def render_empty_state(title: str, message: str) -> None:
    icon = ASSETS_DIR / "empty_state.svg"
    c1, c2 = st.columns([1, 3])
    if icon.exists():
        c1.image(str(icon), width=90)
    c2.markdown(f"<div class='tl-card'><h4>{title}</h4><p>{message}</p></div>", unsafe_allow_html=True)


def render_social_links() -> None:
    st.markdown("<div class='tl-card'><b>Links profissionais</b><br><a href='[INSERIR_LINK_LINKEDIN]'>LinkedIn</a> • <a href='[INSERIR_LINK_GITHUB]'>GitHub</a> • <a href='[INSERIR_LINK_PORTFOLIO]'>Portfólio</a> • <a href='mailto:[INSERIR_EMAIL_PROFISSIONAL]'>E-mail</a></div>", unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown("<div class='tl-footer'>Desenvolvido por Patrick Santos • <a href='[INSERIR_LINK_LINKEDIN]'>LinkedIn</a> • <a href='[INSERIR_LINK_GITHUB]'>GitHub</a> • <a href='[INSERIR_LINK_PORTFOLIO]'>Portfólio</a> • <a href='mailto:[INSERIR_EMAIL_PROFISSIONAL]'>E-mail</a></div>", unsafe_allow_html=True)


metric_card = render_metric_card
triage_card = lambda result: st.markdown(f"<div class='tl-card'><b>{result.get('case_id','')}</b><br>{result.get('ioc')} • {result.get('ioc_type')} • {result.get('confidence_level','Baixa')}</div>", unsafe_allow_html=True)
section_banner = lambda text, icon="🛡️": render_header(text, "", icon)
render_banner = lambda: st.image(str(ASSETS_DIR / "dashboard_banner.svg"), use_container_width=True) if (ASSETS_DIR / "dashboard_banner.svg").exists() else None
