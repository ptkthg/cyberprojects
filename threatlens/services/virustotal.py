from __future__ import annotations

import base64

import requests

TIMEOUT = 12
BASE_URL = "https://www.virustotal.com/api/v3"


def _not_applicable() -> dict:
    return {"status": "Não aplicável", "data": {}, "error": None}


def query_virustotal(ioc: str, ioc_type: str, api_key: str | None) -> dict:
    if ioc_type not in {"ipv4", "domain", "url", "md5", "sha1", "sha256"}:
        return _not_applicable()
    if not api_key:
        return {"status": "Sem API key", "data": {}, "error": None}

    headers = {"x-apikey": api_key}

    if ioc_type == "ipv4":
        endpoint = f"/ip_addresses/{ioc}"
    elif ioc_type == "domain":
        endpoint = f"/domains/{ioc}"
    elif ioc_type == "url":
        url_id = base64.urlsafe_b64encode(ioc.encode()).decode().strip("=")
        endpoint = f"/urls/{url_id}"
    else:
        endpoint = f"/files/{ioc}"

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=TIMEOUT)
        if response.status_code == 404:
            return {"status": "Sem resultado", "data": {}, "error": None}
        if response.status_code == 429:
            return {"status": "Erro", "data": {}, "error": "Rate limit excedido"}
        response.raise_for_status()
        raw = response.json().get("data", {})
        attributes = raw.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        result = {
            "last_analysis_stats": {
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
            },
            "reputation": attributes.get("reputation", 0),
            "last_analysis_date": attributes.get("last_analysis_date"),
            "tags": attributes.get("tags", []),
            "related_links": raw.get("links", {}),
        }
        return {"status": "Consultado", "data": result, "error": None}
    except requests.Timeout:
        return {"status": "Erro", "data": {}, "error": "Timeout na consulta"}
    except requests.RequestException as exc:
        return {"status": "Erro", "data": {}, "error": str(exc)}
    except Exception:
        return {"status": "Erro", "data": {}, "error": "Falha inesperada na consulta"}
