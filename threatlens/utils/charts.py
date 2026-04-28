from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

RISK_COLORS = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#3b82f6", "Baixo": "#22c55e"}
STATUS_COLORS = {
    "Bloqueado": "#ef4444",
    "Em análise": "#f59e0b",
    "Falso positivo": "#fb923c",
    "Resolvido": "#3b82f6",
    "Novo": "#22c55e",
    "Monitorado": "#14b8a6",
    "Escalado": "#8b5cf6",
}


def apply_dark_chart_layout(fig: go.Figure, title: str | None = None) -> go.Figure:
    if title:
        fig.update_layout(title={"text": title, "x": 0, "font": {"size": 18}})
    fig.update_layout(
        paper_bgcolor="rgba(11,18,32,0)",
        plot_bgcolor="rgba(11,18,32,0)",
        font={"color": "#cbd5e1", "family": "Inter, sans-serif"},
        margin={"l": 18, "r": 18, "t": 42, "b": 26},
        legend={"bgcolor": "rgba(11,18,32,0.25)", "borderwidth": 0, "orientation": "v"},
        hoverlabel={"bgcolor": "#0b1220", "font_color": "#e2e8f0", "bordercolor": "#334155"},
    )
    fig.update_xaxes(showgrid=False, color="#94a3b8")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)", color="#94a3b8")
    return fig


def risk_distribution_chart(risk_df: pd.DataFrame) -> go.Figure:
    fig = px.pie(risk_df, names="Risco", values="Quantidade", hole=0.55, color="Risco", color_discrete_map=RISK_COLORS)
    fig.update_traces(textposition="none", sort=False)
    return apply_dark_chart_layout(fig)


def ioc_type_distribution_chart(type_df: pd.DataFrame) -> go.Figure:
    palette = ["#2563eb", "#6366f1", "#8b5cf6", "#0ea5e9", "#14b8a6", "#22c55e"]
    fig = px.bar(type_df, x="Tipo", y="Quantidade", color="Tipo", color_discrete_sequence=palette)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    return apply_dark_chart_layout(fig)


def status_distribution_chart(status_df: pd.DataFrame) -> go.Figure:
    fig = px.pie(status_df, names="Status", values="Quantidade", hole=0.55, color="Status", color_discrete_map=STATUS_COLORS)
    fig.update_traces(textposition="none", sort=False)
    return apply_dark_chart_layout(fig)


# Backward-compatible aliases.
risk_donut = risk_distribution_chart
type_bar = ioc_type_distribution_chart
status_donut = status_distribution_chart
