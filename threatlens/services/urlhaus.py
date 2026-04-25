from __future__ import annotations

import requests

TIMEOUT = 12


def query_urlhaus(ioc: str, ioc_type: str) -> dict:
    if ioc_type not in {"url", "domain"}:
        return {"status": "Não aplicável", "data": {}, "error": None}

    endpoint = "https://urlhaus-api.abuse.ch/v1/url/" if ioc_type == "url" else "https://urlhaus-api.abuse.ch/v1/host/"
    key = "url" if ioc_type == "url" else "host"

    try:
        response = requests.post(endpoint, data={key: ioc}, timeout=TIMEOUT)
        if response.status_code == 429:
            return {"status": "Erro", "data": {}, "error": "Rate limit excedido"}
        response.raise_for_status()
        payload = response.json()
        if payload.get("query_status") in {"no_results", "invalid_url"}:
            return {"status": "Sem resultado", "data": {}, "error": None}

        urls = payload.get("urls", [])
        first = urls[0] if urls else payload
        data = {
            "found": True,
            "status": first.get("url_status") or first.get("query_status"),
            "threat": first.get("threat") or first.get("threat_type"),
            "malware_family": first.get("larted") or first.get("malware_family"),
            "tags": first.get("tags") or [],
            "date_added": first.get("date_added"),
        }
        return {"status": "Consultado", "data": data, "error": None}
    except requests.Timeout:
        return {"status": "Erro", "data": {}, "error": "Timeout na consulta"}
    except requests.RequestException as exc:
        return {"status": "Erro", "data": {}, "error": str(exc)}
    except Exception:
        return {"status": "Erro", "data": {}, "error": "Falha inesperada na consulta"}
