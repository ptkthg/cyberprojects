from __future__ import annotations


def generate_recommendation(score: int, ioc_type: str, results: dict) -> str:
    if score <= 25:
        return "Registrar e monitorar apenas se houver correlação interna."
    if score <= 50:
        return "Monitorar, validar em logs internos e acompanhar recorrência."
    if score <= 75:
        return "Investigar ocorrência no ambiente, validar conexões e avaliar bloqueio."
    return "Abrir incidente, caçar ocorrência no ambiente, avaliar bloqueio e documentar evidências."


def generate_summary(ioc: str, ioc_type: str, score: int, risk_level: str, results: dict) -> str:
    consulted = [k for k, v in results.items() if isinstance(v, dict) and v.get("status") == "Consultado"]
    return (
        f"IOC {ioc} ({ioc_type}) classificado como risco {risk_level} (score {score}). "
        f"Fontes consultadas com sucesso: {', '.join(consulted) if consulted else 'nenhuma'}"
    )
