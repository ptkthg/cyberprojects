from __future__ import annotations

from textwrap import dedent

import streamlit as st


def apply_global_styles() -> None:
    css = dedent(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
            .stApp {background:#020617;color:#f8fafc;}
            .block-container {padding-top:.45rem;padding-bottom:.8rem; max-width:1380px;}
            [data-testid="stSidebar"] {display:none;}
            #MainMenu, header[data-testid="stHeader"], footer {visibility:hidden;}
            [data-testid="stHorizontalBlock"] {gap:.5rem;}
            .tl-banner {background:linear-gradient(120deg,#0b1220,#111827);border:1px solid rgba(56,189,248,.2);border-radius:12px;padding:.55rem .85rem;margin-bottom:.5rem;}
            .tl-banner h3 {font-size:1.05rem;margin:0 0 .15rem 0;}
            .tl-banner p {margin:0;color:#94a3b8;font-size:.82rem;}
            .tl-statusbar {display:flex;gap:.4rem;flex-wrap:wrap;background:#0b1220;border:1px solid rgba(56,189,248,.18);border-radius:10px;padding:6px 8px;margin:.35rem 0 .55rem 0;}
            .tl-chip {display:inline-flex;align-items:center;padding:4px 8px;border:1px solid rgba(148,163,184,.3);border-radius:999px;font-size:.74rem;color:#cbd5e1;background:rgba(15,23,42,.55);}
            .tl-chip-ok {color:#7dd3fc;border-color:rgba(56,189,248,.45);}
            .tl-card {background:#111827;border:1px solid rgba(56,189,248,.2);border-radius:10px;padding:10px;box-shadow:0 4px 12px rgba(0,0,0,.2);margin-bottom:4px;}
            .tl-metric {font-size:1.6rem;font-weight:700;color:#f8fafc;line-height:1.2;}
            .tl-label {font-size:.82rem;color:#cbd5e1;}
            .tl-mini {font-size:.76rem;color:#94a3b8;}
            .tl-badge {padding:4px 10px;border-radius:999px;font-size:.78rem;font-weight:700;display:inline-block;margin-right:6px;}
            [data-testid="stImage"] img {margin-top:2px;}
            [data-testid="stSegmentedControl"] {overflow-x:auto;padding-bottom:2px;}
            [data-testid="stSegmentedControl"] [role="radiogroup"] {flex-wrap:nowrap !important;gap:6px;background:#0b1220;border:1px solid rgba(56,189,248,.2);border-radius:12px;padding:5px;min-height:44px;}
            [data-testid="stSegmentedControl"] [role="radio"] {border-radius:9px !important;min-height:32px !important;padding:2px 10px !important;white-space:nowrap !important;font-size:.8rem !important;color:#cbd5e1 !important;background:transparent !important;border:1px solid transparent !important;}
            [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] {background:rgba(56,189,248,.16) !important;border-color:rgba(56,189,248,.45) !important;color:#e0f2fe !important;}
            .stButton>button {border-radius:10px;border:1px solid rgba(56,189,248,.24);background:#0b1220;color:#e2e8f0;font-weight:600;min-height:2.15rem;}
            .stButton>button[kind="primary"] {background:linear-gradient(90deg,#1d4ed8,#0891b2);color:white;}
            div[data-testid="stButton"] button[kind="secondary"] {background:#0f172a;}
            div[data-testid="stButton"] button p {line-height:1.15;}
            div[data-testid="stButton"] button[id*="card_"] {text-align:left;min-height:92px;background:#111827;border:1px solid rgba(56,189,248,.2);}
            div[data-testid="stButton"] button[id*="card_"]:hover {border-color:#38bdf8;transform:translateY(-1px);}
            .stDownloadButton>button {border-radius:10px;border:1px solid rgba(56,189,248,.25);background:#0b1220;color:#e2e8f0;}
            .stDataFrame {border:1px solid rgba(56,189,248,.25);border-radius:12px;overflow:auto;}
            .stTextInput > div > div > input {background:#0b1220 !important;color:#f8fafc !important;border:1px solid rgba(56,189,248,.25) !important;}
            .stTextInput > div > div > input::placeholder {color:#94a3b8 !important;}
            .stTextInput > div > div:focus-within {box-shadow:0 0 0 1px #38bdf8 !important;border-radius:10px;}
            .stPlotlyChart {margin-top:-4px;}
            .tl-footer {text-align:center;color:#94a3b8;padding:16px 0;font-size:.9rem;}
            a {color:#38bdf8;}
        </style>
        """
    ).strip()
    st.markdown(css, unsafe_allow_html=True)
