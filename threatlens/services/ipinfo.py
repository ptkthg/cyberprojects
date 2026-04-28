from __future__ import annotations

import requests

TIMEOUT = 12


def query_ipinfo(ioc: str, ioc_type: str, api_key: str | None) -> dict:
    if ioc_type != "ipv4":
        return {"status": "Não aplicável", "data": {}, "error": None}
    if not api_key:
        return {"status": "Sem API key", "data": {}, "error": None}

    url = f"https://ipinfo.io/{ioc}/json"
    params = {"token": api_key}

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code == 404:
            return {"status": "Sem resultado", "data": {}, "error": None}
        if response.status_code == 429:
            return {"status": "Erro", "data": {}, "error": "Rate limit excedido"}
        response.raise_for_status()
        payload = response.json()
        data = {
            "country": payload.get("country"),
            "region": payload.get("region"),
            "city": payload.get("city"),
            "asn": payload.get("org"),
            "organization": payload.get("org"),
        }
        return {"status": "Consultado", "data": data, "error": None}
    except requests.Timeout:
        return {"status": "Erro", "data": {}, "error": "Timeout na consulta"}
    except requests.RequestException as exc:
        return {"status": "Erro", "data": {}, "error": str(exc)}
    except Exception:
        return {"status": "Erro", "data": {}, "error": "Falha inesperada na consulta"}
