from __future__ import annotations

import streamlit as st

VALID_PAGES = ["Painel", "Analisar IOC", "Análise em Lote", "Histórico", "Casos", "Configurações", "Sobre"]
DETAIL_PAGE = "Detalhe da Análise"
LEGACY_PAGE_MAP = {
    "📊 Painel": "Painel",
    "🔎 Analisar IOC": "Analisar IOC",
    "📥 Análise em Lote": "Análise em Lote",
    "🕒 Histórico": "Histórico",
    "📁 Casos": "Casos",
    "⚙️ Configurações": "Configurações",
    "ℹ️ Sobre": "Sobre",
    "🧾 Detalhe da Análise": DETAIL_PAGE,
}


def normalize_page_name(page_name: str | None, fallback: str = "Painel") -> str:
    raw = (page_name or "").strip()
    mapped = LEGACY_PAGE_MAP.get(raw, raw)
    if mapped in VALID_PAGES or mapped == DETAIL_PAGE:
        return mapped
    return fallback


def go_to_page(page_name: str) -> None:
    st.session_state["current_page"] = normalize_page_name(page_name)


def set_history_filter(field: str, value: str) -> None:
    st.session_state[f"history_filter_{field}"] = value


def set_case_filter(field: str, value: str) -> None:
    st.session_state[f"case_filter_{field}"] = value


def open_analysis_detail(analysis_id: int) -> None:
    st.session_state["selected_analysis_id"] = analysis_id
    st.session_state["current_page"] = DETAIL_PAGE


def clear_navigation_filters() -> None:
    for k in list(st.session_state.keys()):
        if k.startswith("history_filter_") or k.startswith("case_filter_"):
            del st.session_state[k]
