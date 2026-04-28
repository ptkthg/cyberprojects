from __future__ import annotations

import streamlit as st


def go_to_page(page_name: str) -> None:
    st.session_state["current_page"] = page_name


def set_history_filter(field: str, value: str) -> None:
    st.session_state[f"history_filter_{field}"] = value


def set_case_filter(field: str, value: str) -> None:
    st.session_state[f"case_filter_{field}"] = value


def open_analysis_detail(analysis_id: int) -> None:
    st.session_state["selected_analysis_id"] = analysis_id
    st.session_state["current_page"] = "🧾 Detalhe da Análise"


def clear_navigation_filters() -> None:
    for k in list(st.session_state.keys()):
        if k.startswith("history_filter_") or k.startswith("case_filter_"):
            del st.session_state[k]
