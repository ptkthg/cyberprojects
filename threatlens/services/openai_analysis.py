from __future__ import annotations

import json
import os

from openai import OpenAI

MODEL = "gpt-4.1-mini"


def _sanitize(obj: dict, max_len: int = 7000) -> str:
    raw = json.dumps(obj, ensure_ascii=False)
    raw = " ".join(raw.split())
    return raw[:max_len]


def generate_ai_ioc_analysis(ioc: str, ioc_type: str, analysis_data: dict, kql: str | None = None, api_key: str | None = None) -> dict:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return {"status": "Sem API key"}

    payload = {
        "ioc": ioc,
        "ioc_type": ioc_type,
        "score": analysis_data.get("score"),
        "risk_level": analysis_data.get("risk_level"),
        "confidence_level": analysis_data.get("confidence_level"),
        "sources": analysis_data.get("sources", {}),
        "evidence": analysis_data.get("evidence", {}),
        "score_breakdown": analysis_data.get("score_breakdown", []),
        "kql": kql,
    }

    prompt = f"""
Você é um analista Blue Team/SOC auxiliando na triagem de um IOC.
Regras: use somente dados fornecidos; não invente evidências; declare insuficiência quando necessário; não recomendar bloqueio automático; responder em pt-BR.
Dados: {_sanitize(payload)}
Retorne JSON com chaves: executive_summary, technical_interpretation, risk_reasoning, confidence_assessment, recommended_actions(list), validation_points(list), hunting_suggestions(list), limitations(list).
"""

    try:
        client = OpenAI(api_key=key, timeout=30)
        response = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": "Você é assistente de análise SOC. Não invente dados e sempre recomende validação interna."},
                {"role": "user", "content": prompt},
            ],
        )
        text = getattr(response, "output_text", "") or "{}"
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = {
                "executive_summary": text,
                "technical_interpretation": "Formato não estruturado retornado pela IA.",
                "risk_reasoning": "Revisar manualmente.",
                "confidence_assessment": "Dados insuficientes para inferência estruturada.",
                "recommended_actions": ["Validar em logs internos antes de decisões"],
                "validation_points": ["Confirmar telemetria interna"],
                "hunting_suggestions": ["Executar KQL sugerida"],
                "limitations": ["Saída não estruturada"],
            }
        return {"status": "Consultado", **parsed}
    except Exception as exc:
        msg = str(exc).lower()
        if "rate" in msg:
            return {"status": "Rate limit", "error": str(exc)}
        if "timeout" in msg:
            return {"status": "Timeout", "error": str(exc)}
        return {"status": "Erro", "error": str(exc)}
