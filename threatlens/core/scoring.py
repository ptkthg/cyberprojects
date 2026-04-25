from __future__ import annotations


def score_to_risk(score: int) -> str:
    if score <= 25:
        return "Baixo"
    if score <= 50:
        return "Médio"
    if score <= 75:
        return "Alto"
    return "Crítico"


def calculate_risk_score(results: dict) -> int:
    score = 0

    vt = results.get("virustotal", {}).get("data", {})
    vt_stats = vt.get("last_analysis_stats", {})
    malicious = int(vt_stats.get("malicious", 0) or 0)
    suspicious = int(vt_stats.get("suspicious", 0) or 0)

    score += min(malicious * 4, 40)
    score += min(suspicious * 2, 15)

    ioc_type = results.get("ioc_type")
    if ioc_type in {"md5", "sha1", "sha256"} and malicious >= 5:
        score += 20

    abuse = results.get("abuseipdb", {}).get("data", {})
    conf = int(abuse.get("abuse_confidence_score", 0) or 0)
    if conf > 25:
        score += 15
    if conf > 75:
        score += 20

    urlhaus = results.get("urlhaus", {}).get("data", {})
    if urlhaus.get("found"):
        score += 30
        if urlhaus.get("malware_family"):
            score += 10

    if results.get("ioc_type") in {"domain", "url"} and vt.get("reputation", 0) < 0:
        score += 10

    return min(100, max(0, score))
