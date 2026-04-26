from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from random import choice, randint

DB_PATH = Path(__file__).resolve().parents[1] / "threatlens.db"

REQUIRED_COLUMNS = {
    "case_id": "TEXT NOT NULL DEFAULT ''",
    "confidence_level": "TEXT NOT NULL DEFAULT 'Baixa'",
    "score_breakdown_json": "TEXT NOT NULL DEFAULT '[]'",
    "analyst_decision": "TEXT NOT NULL DEFAULT 'Pendente'",
    "analyst_notes": "TEXT NOT NULL DEFAULT ''",
    "case_status": "TEXT NOT NULL DEFAULT 'Novo'",
    "updated_at": "TEXT NOT NULL DEFAULT ''",
}

STATUS_OPTIONS = ["Novo", "Em análise", "Escalado", "Resolvido", "Falso positivo", "Monitorado", "Bloqueado"]
DECISION_OPTIONS = ["Pendente", "Monitorar", "Investigar", "Bloquear", "Falso positivo", "Escalar incidente"]


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_audit_table() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_audit_log(action: str, target_type: str, target_id: str, details: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO audit_logs (action, target_type, target_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (action, target_type, str(target_id), details, now_iso()),
        )


def get_audit_logs(limit: int = 200) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY datetime(created_at) DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def migrate_db() -> None:
    with get_connection() as conn:
        existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(analyses)").fetchall()}
        for col, col_type in REQUIRED_COLUMNS.items():
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE analyses ADD COLUMN {col} {col_type}")


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL DEFAULT '',
                ioc TEXT NOT NULL,
                ioc_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                confidence_level TEXT NOT NULL DEFAULT 'Baixa',
                recommendation TEXT NOT NULL,
                summary TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                score_breakdown_json TEXT NOT NULL DEFAULT '[]',
                analyst_decision TEXT NOT NULL DEFAULT 'Pendente',
                analyst_notes TEXT NOT NULL DEFAULT '',
                case_status TEXT NOT NULL DEFAULT 'Novo',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    migrate_db()
    create_audit_table()


def generate_case_id() -> str:
    return f"TL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"


def save_analysis(record: dict, as_case: bool = True) -> int:
    created = record.get("created_at") or now_iso()
    updated = now_iso()
    case_id = record.get("case_id") or (generate_case_id() if as_case else "")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (
                case_id, ioc, ioc_type, score, risk_level, confidence_level,
                recommendation, summary, sources_json, evidence_json,
                score_breakdown_json, analyst_decision, analyst_notes,
                case_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                record["ioc"],
                record["ioc_type"],
                int(record["score"]),
                record["risk_level"],
                record.get("confidence_level", "Baixa"),
                record["recommendation"],
                record["summary"],
                json.dumps(record["sources"], ensure_ascii=False),
                json.dumps(record["evidence"], ensure_ascii=False),
                json.dumps(record.get("score_breakdown", []), ensure_ascii=False),
                record.get("analyst_decision", "Pendente"),
                record.get("analyst_notes", ""),
                record.get("case_status", "Novo"),
                created,
                updated,
            ),
        )
        analysis_id = int(cursor.lastrowid)

    create_audit_log("Análise criada", "analysis", str(analysis_id), f"IOC {record['ioc']} salvo")
    return analysis_id


def insert_analysis(record: dict) -> int:
    return save_analysis(record, as_case=True)


def get_all_analyses() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY datetime(updated_at) DESC").fetchall()
    return [dict(row) for row in rows]


def list_analyses() -> list[dict]:
    return get_all_analyses()


def get_analyses() -> list[dict]:
    return get_all_analyses()


def get_analysis_by_id(analysis_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    return dict(row) if row else None


def get_analyses_by_ioc(ioc_query: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM analyses WHERE ioc LIKE ? ORDER BY datetime(updated_at) DESC", (f"%{ioc_query}%",)).fetchall()
    return [dict(row) for row in rows]


def update_case(analysis_id: int, case_status: str, analyst_decision: str, analyst_notes: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE analyses SET case_status = ?, analyst_decision = ?, analyst_notes = ?, updated_at = ? WHERE id = ?",
            (case_status, analyst_decision, analyst_notes, now_iso(), analysis_id),
        )
    create_audit_log("Caso atualizado", "analysis", str(analysis_id), f"status={case_status}")


def update_analysis_decision(analysis_id: int, decision: str, notes: str = "", case_id: str = "") -> None:
    row = get_analysis_by_id(analysis_id)
    if not row:
        return
    update_case(analysis_id, row.get("case_status", "Novo"), decision, notes or row.get("analyst_notes", ""))
    if case_id:
        with get_connection() as conn:
            conn.execute("UPDATE analyses SET case_id = ? WHERE id = ?", (case_id, analysis_id))
    create_audit_log("Decisão alterada", "analysis", str(analysis_id), decision)


def update_analysis_notes(analysis_id: int, notes: str) -> None:
    row = get_analysis_by_id(analysis_id)
    if not row:
        return
    update_case(analysis_id, row.get("case_status", "Novo"), row.get("analyst_decision", "Pendente"), notes)


def update_case_status(analysis_id: int, case_status: str) -> None:
    row = get_analysis_by_id(analysis_id)
    if not row:
        return
    update_case(analysis_id, case_status, row.get("analyst_decision", "Pendente"), row.get("analyst_notes", ""))


def clear_history() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses")
    create_audit_log("Histórico limpo", "analysis", "all", "Registros removidos")


def clear_analyses() -> None:
    clear_history()


def get_dashboard_stats() -> dict:
    rows = get_all_analyses()
    total = len(rows)
    if not rows:
        return {"total": 0, "open_cases": 0, "last_analysis": "-", "risk": {}, "types": {}, "status": {}, "active_sources": 0}

    risk: dict[str, int] = {}
    types: dict[str, int] = {}
    status: dict[str, int] = {}
    active_sources = set()
    for row in rows:
        risk[row["risk_level"]] = risk.get(row["risk_level"], 0) + 1
        types[row["ioc_type"]] = types.get(row["ioc_type"], 0) + 1
        status[row["case_status"]] = status.get(row["case_status"], 0) + 1
        try:
            src = json.loads(row.get("sources_json", "{}"))
            for name, st in src.items():
                if st == "Consultado":
                    active_sources.add(name)
        except Exception:
            pass

    open_cases = sum(1 for row in rows if row["case_status"] not in {"Resolvido", "Falso positivo"})
    return {
        "total": total,
        "open_cases": open_cases,
        "last_analysis": rows[0].get("updated_at", "-"),
        "risk": risk,
        "types": types,
        "status": status,
        "active_sources": len(active_sources),
    }


def seed_demo_data() -> None:
    iocs = [
        ("185.220.101.1", "ipv4"), ("198.51.100.2", "ipv4"), ("203.0.113.77", "ipv4"),
        ("evil-cdn-check.com", "domain"), ("pay-secure-login.net", "domain"),
        ("https://malicious-c2.site/payload", "url"), ("https://dropper.test/update", "url"),
        ("44d88612fea8a8f36de82e1278abb02f", "md5"), ("da39a3ee5e6b4b0d3255bfef95601890afd80709", "sha1"),
        ("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "sha256"),
        ("45.146.164.95", "ipv4"), ("phishing-portal.biz", "domain"),
    ]
    risk_opts = [("Baixo", "Baixa", 18), ("Médio", "Média", 44), ("Alto", "Média", 67), ("Crítico", "Alta", 89)]

    for idx, (ioc, ioc_type) in enumerate(iocs, start=1):
        risk, conf, score = choice(risk_opts)
        created = datetime.utcnow() - timedelta(days=randint(0, 40), hours=randint(0, 23))
        save_analysis(
            {
                "case_id": f"TL-DEMO-{idx:04d}",
                "ioc": ioc,
                "ioc_type": ioc_type,
                "score": score,
                "risk_level": risk,
                "confidence_level": conf,
                "recommendation": "Recomendação demo: validar em telemetria interna antes de qualquer contenção.",
                "summary": "Registro fictício do modo demo para visualização de fluxo SOC.",
                "sources": {"VirusTotal": "Consultado", "AbuseIPDB": "Consultado" if ioc_type == "ipv4" else "Não aplicável", "URLhaus": "Consultado" if ioc_type in {"url", "domain"} else "Não aplicável", "IPinfo": "Sem API key"},
                "evidence": {"demo": True, "reports": randint(0, 120)},
                "score_breakdown": [f"+{score//2} Indicadores externos", f"+{score-score//2} Correlação de contexto"],
                "case_status": choice(STATUS_OPTIONS),
                "analyst_decision": choice(DECISION_OPTIONS),
                "analyst_notes": "Amostra gerada para demonstração do ThreatLens.",
                "created_at": created.isoformat(timespec="seconds"),
                "updated_at": created.isoformat(timespec="seconds"),
            },
            as_case=True,
        )

    create_audit_log("Demo carregado", "system", "demo", "Base demo populada")
