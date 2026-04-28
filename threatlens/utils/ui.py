from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
from textwrap import dedent

import streamlit as st

from core.navigation import go_to_page, open_analysis_detail, set_case_filter, set_history_filter

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

RISK_STYLES = {"Baixo": ("#0b3b5c", "#7dd3fc"), "Médio": ("#78350f", "#fbbf24"), "Alto": ("#7c2d12", "#fb923c"), "Crítico": ("#7f1d1d", "#f87171")}
STATUS_COLORS = {"Novo": "#38bdf8", "Em análise": "#60a5fa", "Escalado": "#f59e0b", "Resolvido": "#22c55e", "Falso positivo": "#94a3b8", "Monitorado": "#a78bfa", "Bloqueado": "#ef4444"}


def render_logo(width: int = 190) -> None:
    p = ASSETS_DIR / "logo.svg"
    if p.exists():
        st.image(str(p), width=width)


def render_top_navigation(options: list[str], current: str) -> str:
    visible_options = options[:]
    selected_internal = current if current in visible_options else visible_options[0]
    icon_map = {
        "Painel": "◈",
        "Analisar IOC": "⌕",
        "Análise em Lote": "☰",
        "Histórico": "◷",
        "Casos": "◉",
        "Configurações": "⚙",
        "Sobre": "ⓘ",
    }
    clean_labels = [re.sub(r"^[^\wÀ-ÿ]+ ?", "", opt) for opt in visible_options]
    display_labels = [f"{icon_map.get(label, '•')}  {label}" for label in clean_labels]
    label_to_internal = dict(zip(display_labels, visible_options))
    selected_label = f"{icon_map.get(re.sub(r'^[^\\wÀ-ÿ]+ ?', '', selected_internal), '•')}  {re.sub(r'^[^\\wÀ-ÿ]+ ?', '', selected_internal)}"

    logo_col, nav_col = st.columns([1.3, 8.7], vertical_alignment="center")
    with logo_col:
        render_logo(138)
    with nav_col:
        selected = st.segmented_control(
            "Navegação",
            options=display_labels,
            default=selected_label,
            label_visibility="collapsed",
            key="top_nav_tabs",
        )
    next_page = label_to_internal.get(selected or selected_label, selected_internal)
    if next_page != selected_internal:
        go_to_page(next_page)
        st.rerun()
    return next_page


def render_status_bar(active_sources: int, mode: str, version: str = "v1.3.0", data_window: str = "Últimas 24h") -> None:
    updated = datetime.utcnow().strftime("%H:%M")
    status_html = dedent(
        f"""
        <div class='tl-statusbar'>
            <span class='tl-chip tl-chip-ok'>● Operacional</span>
            <span class='tl-chip'>Ambiente: {mode}</span>
            <span class='tl-chip'>{version}</span>
            <span class='tl-chip'>Atualizado: {updated}</span>
            <span class='tl-chip'>{data_window}</span>
            <span class='tl-chip'>Fontes: {active_sources}</span>
        </div>
        """
    ).strip()
    st.markdown(status_html, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str = "🛡️") -> None:
    st.markdown(f"<div class='tl-banner'><h3>{icon} {title}</h3><p>{subtitle}</p></div>", unsafe_allow_html=True)


def render_section_title(text: str) -> None:
    st.markdown(f"### {text}")


def render_metric_card(title: str, value: str, icon: str = "📌", subtitle: str = "", risk_level: str | None = None, on_click_key: str | None = None, target_page: str | None = None, filter_type: str | None = None, filter_value: str | int | None = None) -> None:
    label = f"{icon}  {value}\n{title}\n{subtitle or 'Ver detalhes →'}"
    if on_click_key and st.button(label, key=on_click_key, use_container_width=True):
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
    elif not on_click_key:
        st.markdown(
            f"<div class='tl-card'><div class='tl-metric'>{icon} {value}</div><div class='tl-label'>{title}</div><div class='tl-mini'>{subtitle or 'Ver detalhes →'}</div></div>",
            unsafe_allow_html=True,
        )


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
    c1, c2 = st.columns([1, 4])
    if icon.exists():
        c1.image(str(icon), width=90)
    c2.markdown(f"<div class='tl-card'><h4>{title}</h4><p>{message}</p></div>", unsafe_allow_html=True)


def render_social_links() -> None:
    st.markdown("<div class='tl-card'><b>Links profissionais</b><br><a href='[INSERIR_LINK_LINKEDIN]'>LinkedIn</a> • <a href='[INSERIR_LINK_GITHUB]'>GitHub</a> • <a href='[INSERIR_LINK_PORTFOLIO]'>Portfólio</a> • <a href='mailto:[INSERIR_EMAIL_PROFISSIONAL]'>E-mail</a></div>", unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown("<div class='tl-footer'>Desenvolvido por <b>Patrick Santos</b></div>", unsafe_allow_html=True)


metric_card = render_metric_card
triage_card = lambda result: st.markdown(f"<div class='tl-card'><b>{result.get('case_id','')}</b><br>{result.get('ioc')} • {result.get('ioc_type')} • {result.get('confidence_level','Baixa')}</div>", unsafe_allow_html=True)
section_banner = lambda text, icon="🛡️": render_header(text, "", icon)
render_banner = lambda: st.image(str(ASSETS_DIR / "dashboard_banner.svg"), use_container_width=True) if (ASSETS_DIR / "dashboard_banner.svg").exists() else None
