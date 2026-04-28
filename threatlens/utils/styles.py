from __future__ import annotations

from textwrap import dedent

import streamlit as st


def apply_global_styles() -> None:
    css = dedent(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            :root {
                --background:#020617;
                --surface:#0b1220;
                --surface-alt:#111827;
                --surface-hover:#172033;
                --border:rgba(56,189,248,.20);
                --border-hover:rgba(56,189,248,.55);
                --text-primary:#f8fafc;
                --text-secondary:#cbd5e1;
                --text-muted:#94a3b8;
                --accent-blue:#2563eb;
                --accent-cyan:#38bdf8;
                --success:#22c55e;
                --warning:#f59e0b;
                --high:#f97316;
                --critical:#ef4444;
                --purple:#8b5cf6;
                --space-xs:4px;
                --space-sm:8px;
                --space-md:12px;
                --space-lg:16px;
                --space-xl:24px;
                --space-xxl:32px;
                --radius-sm:8px;
                --radius-md:12px;
                --radius-lg:16px;
                --radius-xl:20px;
            }
            html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
            .stApp {background:radial-gradient(1200px 560px at 12% -20%, rgba(37,99,235,.22), rgba(2,6,23,0)) , var(--background);color:var(--text-primary);}
            .block-container {padding-top:.35rem;padding-bottom:.55rem; max-width:1420px;}
            [data-testid="stSidebar"] {display:none;}
            #MainMenu, header[data-testid="stHeader"], footer {visibility:hidden;}
            [data-testid="stHorizontalBlock"] {gap:.45rem;}
            .tl-top-shell {background:linear-gradient(180deg, rgba(7,17,31,.96), rgba(2,6,23,.9));border:1px solid rgba(56,189,248,.16);border-radius:14px;padding:8px 10px;margin-bottom:7px;}
            .tl-banner {background:linear-gradient(120deg,rgba(11,18,32,.98),rgba(15,23,42,.9));border:1px solid rgba(56,189,248,.2);border-radius:14px;padding:.7rem .95rem;margin:.3rem 0 .45rem 0;position:relative;overflow:hidden;}
            .tl-banner:after {content:'';position:absolute;right:18%;top:-32%;width:280px;height:160px;background:radial-gradient(circle,rgba(56,189,248,.18),rgba(56,189,248,0) 70%);}
            .tl-banner h3 {font-size:1.55rem;margin:0 0 .12rem 0;position:relative;z-index:2;font-weight:700;}
            .tl-banner p {margin:0;color:var(--text-muted);font-size:.95rem;position:relative;z-index:2;}
            .tl-statusbar {display:flex;gap:.45rem;flex-wrap:wrap;background:linear-gradient(90deg,rgba(11,18,32,.95),rgba(7,17,31,.92));border:1px solid rgba(56,189,248,.2);border-radius:11px;padding:8px 10px;margin:.2rem 0 .5rem 0;}
            .tl-chip {display:inline-flex;align-items:center;padding:6px 11px;border:1px solid rgba(148,163,184,.28);border-radius:10px;font-size:.78rem;font-weight:500;color:#cbd5e1;background:rgba(15,23,42,.72);}
            .tl-chip-ok {color:#7dd3fc;border-color:rgba(56,189,248,.45);}
            .tl-card {background:linear-gradient(180deg,var(--surface-alt),var(--surface));border:1px solid var(--border);border-radius:var(--radius-lg);padding:12px;box-shadow:0 8px 26px rgba(0,0,0,.24);margin-bottom:4px;}
            .tl-metric {font-size:1.6rem;font-weight:700;color:#f8fafc;line-height:1.2;}
            .tl-label {font-size:.82rem;color:#cbd5e1;}
            .tl-mini {font-size:.76rem;color:#94a3b8;}
            .tl-badge {padding:4px 10px;border-radius:999px;font-size:.78rem;font-weight:700;display:inline-block;margin-right:6px;}
            [data-testid="stImage"] img {margin-top:2px;}
            [data-testid="stSegmentedControl"] {overflow-x:auto;padding-bottom:0;}
            [data-testid="stSegmentedControl"] [role="radiogroup"] {flex-wrap:nowrap !important;gap:3px;background:#07111f;border:1px solid rgba(56,189,248,.18);border-radius:12px;padding:3px;min-height:56px;}
            [data-testid="stSegmentedControl"] [role="radio"] {border-radius:9px !important;min-height:46px !important;padding:3px 11px !important;white-space:nowrap !important;font-size:.88rem !important;font-weight:600 !important;color:#cbd5e1 !important;background:transparent !important;border:1px solid transparent !important;line-height:1 !important;}
            [data-testid="stSegmentedControl"] [role="radio"] span {white-space:nowrap !important;}
            [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] {background:linear-gradient(180deg,rgba(37,99,235,.26),rgba(14,165,233,.16)) !important;border-color:rgba(56,189,248,.5) !important;color:#f8fafc !important;box-shadow:inset 0 -2px 0 #38bdf8;}
            .stButton>button {border-radius:11px;border:1px solid rgba(56,189,248,.24);background:#0b1220;color:#e2e8f0;font-weight:600;min-height:2.4rem;}
            .stButton>button[kind="primary"] {background:linear-gradient(90deg,#1d4ed8,#0891b2);color:white;}
            div[data-testid="stButton"] button[kind="secondary"] {background:#0f172a;}
            div[data-testid="stButton"] button p {line-height:1.12;}
            div[data-testid="stButton"] button[id*="card_"] {text-align:left;min-height:114px;max-height:124px;background:linear-gradient(100deg,var(--surface),#0a162b);border:1px solid var(--border);padding:.55rem .8rem;box-shadow:0 6px 22px rgba(0,0,0,.22);}
            div[data-testid="stButton"] button[id*="card_"]:hover {border-color:var(--border-hover);transform:translateY(-1px);}
            div[data-testid="stButton"] button[id*="card_"] p {white-space:pre-line;font-size:.95rem;line-height:1.18;}
            .stDownloadButton>button {border-radius:10px;border:1px solid rgba(56,189,248,.25);background:#0b1220;color:#e2e8f0;}
            .stDataFrame {border:1px solid rgba(56,189,248,.25);border-radius:12px;overflow:auto;}
            .stTextInput > div > div > input {background:#0b1220 !important;color:#f8fafc !important;border:1px solid rgba(56,189,248,.25) !important;}
            .stTextInput > div > div > input::placeholder {color:#94a3b8 !important;}
            .stTextInput > div > div:focus-within {box-shadow:0 0 0 1px #38bdf8 !important;border-radius:10px;}
            .stPlotlyChart {margin-top:-2px;}
            .tl-chart-card {background:linear-gradient(180deg,var(--surface-alt),var(--surface));border:1px solid var(--border);border-radius:var(--radius-lg);padding:10px 12px 6px 12px;min-height:348px;}
            .tl-chart-title {font-size:1.05rem;font-weight:600;color:#f8fafc;margin-bottom:4px;}
            .tl-chart-link {font-size:.94rem;color:#38bdf8;margin-top:-4px;}
            .tl-mini-card {background:linear-gradient(180deg,var(--surface-alt),var(--surface));border:1px solid var(--border);border-radius:var(--radius-lg);padding:14px;min-height:348px;}
            .tl-mini-card h4 {margin:0 0 .5rem 0;font-size:2rem;}
            .tl-mini-card p {color:#94a3b8;font-size:1.05rem;}
            .tl-sources-list {margin-top:8px;border-top:1px solid rgba(56,189,248,.14);}
            .tl-source-row {display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(56,189,248,.12);}
            .tl-source-ok {color:#22c55e;font-weight:600;}
            .tl-custom-table {width:100%;border-collapse:collapse;overflow:hidden;border-radius:12px;}
            .tl-custom-table th,.tl-custom-table td {padding:10px 10px;border-bottom:1px solid rgba(56,189,248,.12);text-align:left;}
            .tl-custom-table th {font-size:.87rem;color:#94a3b8;background:rgba(11,18,32,.7);}
            .tl-custom-table td {font-size:.94rem;color:#e2e8f0;}
            .tl-pill {display:inline-block;padding:3px 8px;border-radius:8px;border:1px solid rgba(56,189,248,.28);font-size:.8rem;}
            .tl-case-link {color:#38bdf8;text-decoration:none;font-weight:600;}
            .tl-footer {text-align:center;color:#94a3b8;padding:12px 0 4px 0;font-size:1.02rem;}
            .tl-footer b {color:#38bdf8;}
            @media (max-width:1200px) {
                .tl-banner h3 {font-size:1.7rem;}
                div[data-testid="stButton"] button[id*="card_"] {min-height:106px;}
            }
            @media (max-width:992px) {
                .block-container {max-width:100%;padding-left:.75rem;padding-right:.75rem;}
                [data-testid="stSegmentedControl"] [role="radiogroup"] {min-height:50px;}
                [data-testid="stSegmentedControl"] [role="radio"] {font-size:.8rem !important;min-height:40px !important;padding:2px 7px !important;}
                .tl-chart-card,.tl-mini-card {min-height:320px;}
            }
            @media (max-width:768px) {
                .tl-banner {padding:.6rem .7rem;}
                .tl-banner h3 {font-size:1.45rem;}
                .tl-statusbar {padding:6px 8px;}
                .tl-chip {padding:5px 8px;font-size:.73rem;}
                div[data-testid="stButton"] button[id*="card_"] {min-height:98px;}
                .tl-custom-table {display:block;overflow-x:auto;white-space:nowrap;}
            }
            a {color:#38bdf8;}
        </style>
        """
    ).strip()
    st.markdown(css, unsafe_allow_html=True)
