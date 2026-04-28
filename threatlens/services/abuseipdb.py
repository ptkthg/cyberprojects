from __future__ import annotations

import requests

TIMEOUT = 12
BASE_URL = "https://api.abuseipdb.com/api/v2/check"


def query_abuseipdb(ioc: str, ioc_type: str, api_key: str | None) -> dict:
    if ioc_type != "ipv4":
        return {"status": "Não aplicável", "data": {}, "error": None}
    if not api_key:
        return {"status": "Sem API key", "data": {}, "error": None}

    headers = {"Key": api_key, "Accept": "application/json"}
    params = {"ipAddress": ioc, "maxAgeInDays": 90, "verbose": True}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=TIMEOUT)
        if response.status_code == 404:
            return {"status": "Sem resultado", "data": {}, "error": None}
        if response.status_code == 429:
            return {"status": "Erro", "data": {}, "error": "Rate limit excedido"}
        response.raise_for_status()
        payload = response.json().get("data", {})
        result = {
            "abuse_confidence_score": payload.get("abuseConfidenceScore", 0),
            "country_code": payload.get("countryCode"),
            "isp": payload.get("isp"),
            "domain": payload.get("domain"),
            "total_reports": payload.get("totalReports", 0),
            "categories": [r.get("categories") for r in payload.get("reports", []) if r.get("categories")],
        }
        return {"status": "Consultado", "data": result, "error": None}
    except requests.Timeout:
        return {"status": "Erro", "data": {}, "error": "Timeout na consulta"}
    except requests.RequestException as exc:
        return {"status": "Erro", "data": {}, "error": str(exc)}
    except Exception:
        return {"status": "Erro", "data": {}, "error": "Falha inesperada na consulta"}
