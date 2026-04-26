from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

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


STATUS_OPTIONS = [
    "Novo",
    "Em triagem",
    "Em investigação",
    "Monitorado",
    "Bloqueado",
    "Falso positivo",
    "Encerrado",
    "Escalado para incidente",
]


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
            """
            INSERT INTO audit_logs (action, target_type, target_id, details, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (action, target_type, str(target_id), details, now_iso()),
        )


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


def get_all_analyses() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY datetime(updated_at) DESC").fetchall()
    return [dict(row) for row in rows]


def update_case(
    analysis_id: int,
    case_status: str,
    analyst_decision: str,
    analyst_notes: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE analyses
            SET case_status = ?, analyst_decision = ?, analyst_notes = ?, updated_at = ?
            WHERE id = ?
            """,
            (case_status, analyst_decision, analyst_notes, now_iso(), analysis_id),
        )
    create_audit_log("Caso atualizado", "analysis", str(analysis_id), f"Status={case_status}; decisão={analyst_decision}")
    create_audit_log("Decisão alterada", "analysis", str(analysis_id), f"Nova decisão={analyst_decision}")


def clear_history() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses")
    create_audit_log("Histórico limpo", "analysis", "all", "Todos os registros removidos")


def seed_demo_data() -> None:
    demo_rows = [
        {"ioc": "185.220.101.1", "ioc_type": "ipv4", "score": 82, "risk_level": "Crítico", "confidence_level": "Alta"},
        {"ioc": "malicious-example.com", "ioc_type": "domain", "score": 64, "risk_level": "Alto", "confidence_level": "Média"},
        {"ioc": "https://evil.test/dropper", "ioc_type": "url", "score": 71, "risk_level": "Alto", "confidence_level": "Alta"},
        {"ioc": "44d88612fea8a8f36de82e1278abb02f", "ioc_type": "md5", "score": 39, "risk_level": "Médio", "confidence_level": "Média"},
    ]

    for row in demo_rows:
        save_analysis(
            {
                **row,
                "recommendation": "Dado de demonstração para validação da UI.",
                "summary": "Registro fictício para modo demo.",
                "sources": {"VirusTotal": "Consultado", "AbuseIPDB": "Não aplicável", "URLhaus": "Consultado", "IPinfo": "Sem API key"},
                "evidence": {"demo": True},
                "score_breakdown": ["+20 detecções", "+19 correlação multi-fonte"],
                "case_status": "Em triagem",
                "analyst_decision": "Monitorar",
                "analyst_notes": "Inserido automaticamente no modo demo",
            },
            as_case=True,
        )

    create_audit_log("Demo carregado", "system", "demo", "Dados de demonstração inseridos")


def get_audit_logs(limit: int = 200) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_logs ORDER BY datetime(created_at) DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]
