from __future__ import annotations


def score_to_risk(score: int) -> str:
    if score <= 25:
        return "Baixo"
    if score <= 50:
        return "Médio"
    if score <= 75:
        return "Alto"
    return "Crítico"


def calculate_risk_score(results: dict) -> dict:
    score = 0
    breakdown: list[str] = []

    vt = results.get("virustotal", {}).get("data", {})
    vt_stats = vt.get("last_analysis_stats", {})
    malicious = int(vt_stats.get("malicious", 0) or 0)
    suspicious = int(vt_stats.get("suspicious", 0) or 0)

    if malicious > 0:
        points = min(malicious * 4, 40)
        score += points
        breakdown.append(f"+{points} VirusTotal retornou detecções maliciosas ({malicious})")

    if suspicious > 0:
        points = min(suspicious * 2, 15)
        score += points
        breakdown.append(f"+{points} VirusTotal retornou detecções suspeitas ({suspicious})")

    ioc_type = results.get("ioc_type")
    if ioc_type in {"md5", "sha1", "sha256"} and malicious >= 5:
        score += 20
        breakdown.append("+20 Hash com múltiplas detecções")

    abuse = results.get("abuseipdb", {}).get("data", {})
    conf = int(abuse.get("abuse_confidence_score", 0) or 0)
    if conf > 25:
        score += 15
        breakdown.append(f"+15 AbuseIPDB indicou reputação suspeita ({conf})")
    if conf > 75:
        score += 20
        breakdown.append(f"+20 AbuseIPDB com alta confiança de abuso ({conf})")

    urlhaus = results.get("urlhaus", {}).get("data", {})
    if urlhaus.get("found"):
        score += 25
        breakdown.append("+25 Indicador presente no URLhaus")
        if urlhaus.get("malware_family"):
            score += 10
            breakdown.append("+10 IOC associado a família de malware")

    if results.get("ioc_type") in {"domain", "url"} and vt.get("reputation", 0) < 0:
        score += 10
        breakdown.append("+10 Reputação negativa no VirusTotal")

    if not breakdown:
        breakdown.append("+0 Sem evidências externas relevantes no momento")

    final_score = min(100, max(0, score))
    return {
        "score": final_score,
        "risk_level": score_to_risk(final_score),
        "score_breakdown": breakdown,
    }
