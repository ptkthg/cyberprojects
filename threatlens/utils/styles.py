from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
            .stApp {background:#020617;color:#f8fafc;}
            .block-container {padding-top:.8rem; max-width:1360px;}
            [data-testid="stSidebar"] {display:none;}
            #MainMenu, header[data-testid="stHeader"], footer {visibility:hidden;}
            .tl-banner {background:linear-gradient(90deg,#0b1220,#111827);border:1px solid rgba(56,189,248,.2);border-radius:12px;padding:.8rem 1rem;margin-bottom:.8rem;}
            .tl-statusbar {display:flex;gap:18px;flex-wrap:wrap;background:#0b1220;border:1px solid rgba(56,189,248,.25);border-radius:10px;padding:10px 12px;margin-bottom:10px;color:#cbd5e1;font-size:.86rem;}
            .tl-card {background:#111827;border:1px solid rgba(56,189,248,.23);border-radius:12px;padding:12px;box-shadow:0 8px 20px rgba(0,0,0,.22);margin-bottom:6px;}
            .tl-clickable:hover {border-color:#38bdf8;transform:translateY(-1px);transition:.2s;}
            .tl-metric {font-size:1.6rem;font-weight:700;color:#f8fafc;line-height:1.2;}
            .tl-label {font-size:.86rem;color:#cbd5e1;}
            .tl-mini {font-size:.78rem;color:#64748b;}
            .tl-badge {padding:4px 10px;border-radius:999px;font-size:.78rem;font-weight:700;display:inline-block;margin-right:6px;}
            .stButton>button {border-radius:10px;border:1px solid rgba(56,189,248,.3);background:#0b1220;color:#e2e8f0;font-weight:600;}
            .stButton>button[kind="primary"] {background:linear-gradient(90deg,#2563eb,#38bdf8);color:white;}
            .stDownloadButton>button {border-radius:10px;border:1px solid rgba(56,189,248,.25);background:#0b1220;color:#e2e8f0;}
            .stDataFrame {border:1px solid rgba(56,189,248,.25);border-radius:12px;overflow:auto;}
            .tl-footer {text-align:center;color:#94a3b8;padding:16px 0;font-size:.9rem;}
            a {color:#38bdf8;}
        </style>
        """,
        unsafe_allow_html=True,
    )
