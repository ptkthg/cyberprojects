from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import dedent

import streamlit as st

from core.navigation import VALID_PAGES, go_to_page, normalize_page_name, open_analysis_detail, set_case_filter, set_history_filter

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

RISK_STYLES = {"Baixo": ("#0b3b5c", "#7dd3fc"), "Médio": ("#78350f", "#fbbf24"), "Alto": ("#7c2d12", "#fb923c"), "Crítico": ("#7f1d1d", "#f87171")}
STATUS_COLORS = {"Novo": "#38bdf8", "Em análise": "#60a5fa", "Escalado": "#f59e0b", "Resolvido": "#22c55e", "Falso positivo": "#94a3b8", "Monitorado": "#a78bfa", "Bloqueado": "#ef4444"}


def render_logo(width: int = 190) -> None:
    p = ASSETS_DIR / "logo.svg"
    if p.exists():
        st.image(str(p), width=width)


def render_top_navigation(options: list[str], current: str) -> str:
    visible_options = []
    for option in options:
        normalized = normalize_page_name(option, fallback="")
        if normalized in VALID_PAGES and normalized not in visible_options:
            visible_options.append(normalized)
    if not visible_options:
        visible_options = VALID_PAGES.copy()

    selected_internal = normalize_page_name(current, fallback="Painel")
    if selected_internal not in visible_options:
        selected_internal = "Painel"
        st.session_state["current_page"] = "Painel"

    logo_col, nav_col = st.columns([1.1, 8.9], vertical_alignment="center")
    with logo_col:
        render_logo(142)
    with nav_col:
        selected = st.segmented_control(
            "Navegação",
            options=visible_options,
            default=selected_internal,
            label_visibility="collapsed",
            key="top_nav_tabs",
        )
    next_page = normalize_page_name(selected, fallback="Painel")
    if next_page != selected_internal:
        go_to_page(next_page)
        st.rerun()
    return next_page


def render_topbar(options: list[str], current: str) -> str:
    return render_top_navigation(options, current)


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


def render_statusbar(active_sources: int, mode: str, version: str = "v1.3.0", data_window: str = "Últimas 24h") -> None:
    render_status_bar(active_sources, mode, version, data_window)


def render_header(title: str, subtitle: str, icon: str = "🛡️") -> None:
    st.markdown(f"<div class='tl-banner'><h3>{icon} {title}</h3><p>{subtitle}</p></div>", unsafe_allow_html=True)


def render_section_title(text: str) -> None:
    st.markdown(f"### {text}")


def render_page_header(title: str, subtitle: str, button_label: str = "Analisar IOC") -> bool:
    c1, c2 = st.columns([4.5, 1.3], vertical_alignment="center")
    c1.markdown(f"<div class='tl-banner'><h3>{title}</h3><p>{subtitle}</p></div>", unsafe_allow_html=True)
    return c2.button(button_label, type="primary", use_container_width=True, key=f"hdr_{button_label}")


def render_search_bar(placeholder: str = "🔎  Buscar IOC, domínio, IP, hash ou caso...", button_label: str = "Buscar", key_prefix: str = "main") -> tuple[str, bool]:
    c1, c2 = st.columns([8, 1], vertical_alignment="center")
    query = c1.text_input("", placeholder=placeholder, label_visibility="collapsed", key=f"{key_prefix}_search")
    clicked = c2.button(button_label, use_container_width=True, key=f"{key_prefix}_search_btn")
    return query, clicked


def render_metric_card(title: str, value: str, icon: str = "📌", subtitle: str = "", risk_level: str | None = None, on_click_key: str | None = None, target_page: str | None = None, filter_type: str | None = None, filter_value: str | int | None = None) -> None:
    action = subtitle or "Ver detalhes →"
    label = f"{icon}  {value}\n{title}\n{action}"
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
            f"<div class='tl-card'><div class='tl-metric'>{icon} {value}</div><div class='tl-label'>{title}</div><div class='tl-mini'>{action}</div></div>",
            unsafe_allow_html=True,
        )


def render_kpi_card(title: str, value: str, icon: str = "📌", subtitle: str = "", on_click_key: str | None = None, target_page: str | None = None, filter_type: str | None = None, filter_value: str | int | None = None) -> None:
    render_metric_card(title, value, icon, subtitle, on_click_key=on_click_key, target_page=target_page, filter_type=filter_type, filter_value=filter_value)


def render_risk_badge(risk_level: str, score: int = 0) -> None:
    bg, fg = RISK_STYLES.get(risk_level, ("#334155", "#cbd5e1"))
    st.markdown(f"<span class='tl-badge' style='background:{bg};color:{fg};'>Risco {risk_level} • {score}/100</span>", unsafe_allow_html=True)


def risk_badge(risk_level: str, score: int) -> None:
    render_risk_badge(risk_level, score)


def render_status_badge(status: str) -> None:
    color = STATUS_COLORS.get(status, "#94a3b8")
    st.markdown(f"<span class='tl-badge' style='background:#0b1220;color:{color};border:1px solid {color};'>Status {status}</span>", unsafe_allow_html=True)


def render_badge(text: str, color: str = "#38bdf8") -> str:
    return f"<span class='tl-pill' style='border-color:{color};color:{color};background:rgba(15,23,42,.65)'>{text}</span>"


def recommendation_card(text: str) -> None:
    st.markdown(f"<div class='tl-card'><b>Ações recomendadas</b><p style='margin:.4rem 0'>{text}</p></div>", unsafe_allow_html=True)


def render_empty_state(title: str, message: str) -> None:
    icon = ASSETS_DIR / "empty_state.svg"
    c1, c2 = st.columns([1, 4])
    if icon.exists():
        c1.image(str(icon), width=90)
    c2.markdown(f"<div class='tl-card'><h4>{title}</h4><p>{message}</p></div>", unsafe_allow_html=True)


def render_chart_panel(title: str, detail_link: str = "Ver detalhes →") -> None:
    st.markdown(f"<div class='tl-chart-card'><div class='tl-chart-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='tl-chart-link'>{detail_link}</div></div>", unsafe_allow_html=True)


def render_ai_panel() -> None:
    st.markdown("<div class='tl-mini-card'><div class='tl-chart-title'>Análise Inteligente</div><h4 style='text-align:center;color:#38bdf8'>AI</h4><p style='text-align:center'>Gere insights com IA a partir dos dados coletados.</p></div>", unsafe_allow_html=True)


def render_source_health_panel(sources: list[tuple[str, str]]) -> None:
    rows = ["<div class='tl-mini-card'><div class='tl-chart-title'>Saúde das fontes</div><div class='tl-sources-list'>"]
    for source, status in sources:
        status_class = "tl-source-ok" if status == "Operacional" else "tl-mini"
        indicator = "●" if status == "Operacional" else "○"
        rows.append(f"<div class='tl-source-row'><span>{source}</span><span class='{status_class}'>{status} {indicator}</span></div>")
    rows.append("</div><div class='tl-chart-link'>Ver todas as fontes →</div></div>")
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_recent_analysis_table(html_table: str) -> None:
    st.markdown(html_table, unsafe_allow_html=True)


def render_social_links() -> None:
    st.markdown("<div class='tl-card'><b>Links profissionais</b><br><a href='[INSERIR_LINK_LINKEDIN]'>LinkedIn</a> • <a href='[INSERIR_LINK_GITHUB]'>GitHub</a> • <a href='[INSERIR_LINK_PORTFOLIO]'>Portfólio</a> • <a href='mailto:[INSERIR_EMAIL_PROFISSIONAL]'>E-mail</a></div>", unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown("<div class='tl-footer'>Desenvolvido por <b>Patrick Santos</b></div>", unsafe_allow_html=True)


metric_card = render_metric_card
triage_card = lambda result: st.markdown(f"<div class='tl-card'><b>{result.get('case_id','')}</b><br>{result.get('ioc')} • {result.get('ioc_type')} • {result.get('confidence_level','Baixa')}</div>", unsafe_allow_html=True)
section_banner = lambda text, icon="🛡️": render_header(text, "", icon)
render_banner = lambda: st.image(str(ASSETS_DIR / "dashboard_banner.svg"), use_container_width=True) if (ASSETS_DIR / "dashboard_banner.svg").exists() else None
