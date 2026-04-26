from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {background: radial-gradient(circle at top right, #0b3a5a 0%, #0b1220 35%, #070d18 100%);}            
            .block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1240px;}
            [data-testid="stSidebar"] {background: #0a1120; border-right: 1px solid #1e293b;}
            #MainMenu, header[data-testid="stHeader"] {visibility: hidden;}
            h1, h2, h3 {color: #e2e8f0 !important; letter-spacing: .2px;}
            .tl-banner {background: linear-gradient(100deg,#0b1220,#0f2942); border: 1px solid #1e3a5f; border-radius: 14px; padding: .8rem 1rem; margin-bottom: .8rem; color: #cbd5e1;}
            .tl-card {background: #0f172a; border: 1px solid #1f2a44; border-radius: 14px; padding: 14px; box-shadow: 0 4px 14px rgba(0,0,0,.25);}            
            .tl-metric {font-size: 1.4rem; font-weight: 700; color: #bae6fd;}
            .tl-label {font-size: .85rem; color: #94a3b8; margin-top: 4px;}
            .stButton>button, .stDownloadButton>button {border-radius: 10px; border: 1px solid #1d4ed8; background: linear-gradient(90deg, #1d4ed8, #0ea5e9); color: white; font-weight: 600;}
            .stDataFrame {border: 1px solid #1f2a44; border-radius: 12px;}
            .tl-footer {text-align:center;color:#7c93b5;margin-top:24px;font-size:.9rem;}
            .tl-badge {padding:4px 10px;border-radius:999px;font-size:.78rem;font-weight:700;display:inline-block;}
        </style>
        """,
        unsafe_allow_html=True,
    )
