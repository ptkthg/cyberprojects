from __future__ import annotations

from datetime import datetime

from core.ioc_detector import detect_ioc_type
from core.kql_generator import generate_kql
from core.recommendations import generate_recommendation, generate_summary
from core.scoring import calculate_risk_score, score_to_risk
from services.abuseipdb import query_abuseipdb
from services.ipinfo import query_ipinfo
from services.urlhaus import query_urlhaus
from services.virustotal import query_virustotal


def analyze_ioc(ioc_raw: str, secrets: dict) -> dict:
    ioc, ioc_type = detect_ioc_type(ioc_raw)
    if ioc_type == "unknown":
        return {
            "ioc": ioc,
            "ioc_type": ioc_type,
            "score": 0,
            "risk_level": "Baixo",
            "recommendation": "IOC inválido. Ajuste o indicador e tente novamente.",
            "summary": "Não foi possível identificar o tipo do IOC.",
            "sources": {},
            "evidence": {"errors": ["Tipo de IOC não reconhecido"]},
            "kql": "// IOC inválido",
            "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        }

    vt = query_virustotal(ioc, ioc_type, secrets.get("VIRUSTOTAL_API_KEY"))
    abuse = query_abuseipdb(ioc, ioc_type, secrets.get("ABUSEIPDB_API_KEY"))
    urlhaus = query_urlhaus(ioc, ioc_type)
    ipinfo = query_ipinfo(ioc, ioc_type, secrets.get("IPINFO_API_KEY"))

    results = {
        "ioc_type": ioc_type,
        "virustotal": vt,
        "abuseipdb": abuse,
        "urlhaus": urlhaus,
        "ipinfo": ipinfo,
    }
    score = calculate_risk_score(results)
    risk_level = score_to_risk(score)
    recommendation = generate_recommendation(score, ioc_type, results)
    summary = generate_summary(ioc, ioc_type, score, risk_level, results)

    evidence = {
        "vt_stats": vt.get("data", {}).get("last_analysis_stats", {}),
        "abuse_confidence": abuse.get("data", {}).get("abuse_confidence_score"),
        "urlhaus": urlhaus.get("data", {}),
        "ipinfo": ipinfo.get("data", {}),
        "errors": {
            name: data.get("error")
            for name, data in {
                "virustotal": vt,
                "abuseipdb": abuse,
                "urlhaus": urlhaus,
                "ipinfo": ipinfo,
            }.items()
            if data.get("error")
        },
    }

    return {
        "ioc": ioc,
        "ioc_type": ioc_type,
        "score": score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "summary": summary,
        "sources": {
            "virustotal": vt["status"],
            "abuseipdb": abuse["status"],
            "urlhaus": urlhaus["status"],
            "ipinfo": ipinfo["status"],
        },
        "evidence": evidence,
        "kql": generate_kql(ioc, ioc_type),
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    }
