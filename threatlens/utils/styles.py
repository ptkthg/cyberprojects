from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
            .stApp {background: #020617; color:#f8fafc;}
            .block-container {padding-top: 1rem; padding-bottom: 1.4rem; max-width: 1280px;}
            [data-testid="stSidebar"] {background:#0f172a;border-right:1px solid rgba(56,189,248,.25);}            
            #MainMenu, header[data-testid="stHeader"], footer {visibility:hidden;}
            .tl-banner {background:linear-gradient(90deg,#0b1220,#111827);border:1px solid rgba(56,189,248,.25);border-radius:12px;padding:.9rem 1rem;margin-bottom:.9rem;}
            .tl-card {background:#111827;border:1px solid rgba(56,189,248,.25);border-radius:12px;padding:12px;box-shadow:0 8px 20px rgba(0,0,0,.2);transition:all .2s ease;}
            .tl-card:hover {transform:translateY(-2px); border-color:#38bdf8;}
            .tl-metric {font-size:1.65rem;font-weight:700;color:#f8fafc;line-height:1.2;}
            .tl-label {font-size:.83rem;color:#cbd5e1;}
            .tl-badge {padding:4px 10px;border-radius:999px;font-size:.78rem;font-weight:700;display:inline-block;}
            .stButton>button {border-radius:10px;border:1px solid #2563eb;background:linear-gradient(90deg,#2563eb,#38bdf8);color:white;font-weight:600;}
            .stDownloadButton>button {border-radius:10px;border:1px solid rgba(56,189,248,.25);background:#0b1220;color:#e2e8f0;}
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
                background:#0b1220 !important;border:1px solid rgba(56,189,248,.25) !important;color:#f8fafc !important;
            }
            .stDataFrame {border:1px solid rgba(56,189,248,.25);border-radius:12px;overflow:auto;}
            [data-testid="stFileUploader"] {border:1px dashed rgba(56,189,248,.35);border-radius:12px;background:#0b1220;}
            .tl-footer {text-align:center;color:#94a3b8;padding-top:20px;font-size:.88rem;}
            .tl-footer a {color:#38bdf8;text-decoration:none;}
        </style>
        """,
        unsafe_allow_html=True,
    )
