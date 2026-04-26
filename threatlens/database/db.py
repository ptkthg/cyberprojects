from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "threatlens.db"

REQUIRED_COLUMNS = {
    "score_breakdown_json": "TEXT NOT NULL DEFAULT '[]'",
    "analyst_decision": "TEXT NOT NULL DEFAULT 'Pendente'",
    "analyst_notes": "TEXT NOT NULL DEFAULT ''",
    "case_id": "TEXT NOT NULL DEFAULT ''",
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def migrate_db() -> None:
    with get_connection() as conn:
        existing_cols = {
            row["name"] for row in conn.execute("PRAGMA table_info(analyses)").fetchall()
        }
        for col, col_type in REQUIRED_COLUMNS.items():
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE analyses ADD COLUMN {col} {col_type}")


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ioc TEXT NOT NULL,
                ioc_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                summary TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                score_breakdown_json TEXT NOT NULL DEFAULT '[]',
                analyst_decision TEXT NOT NULL DEFAULT 'Pendente',
                analyst_notes TEXT NOT NULL DEFAULT '',
                case_id TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
    migrate_db()


def save_analysis(record: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analyses (
                ioc, ioc_type, score, risk_level, recommendation, summary,
                sources_json, evidence_json, score_breakdown_json,
                analyst_decision, analyst_notes, case_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["ioc"],
                record["ioc_type"],
                int(record["score"]),
                record["risk_level"],
                record["recommendation"],
                record["summary"],
                json.dumps(record["sources"], ensure_ascii=False),
                json.dumps(record["evidence"], ensure_ascii=False),
                json.dumps(record.get("score_breakdown", []), ensure_ascii=False),
                record.get("analyst_decision", "Pendente"),
                record.get("analyst_notes", ""),
                record.get("case_id", ""),
                record.get("created_at") or datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )


def get_all_analyses() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY datetime(created_at) DESC").fetchall()
    return [dict(row) for row in rows]


def update_analysis_decision(analysis_id: int, decision: str, notes: str, case_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE analyses
            SET analyst_decision = ?, analyst_notes = ?, case_id = ?
            WHERE id = ?
            """,
            (decision, notes, case_id, analysis_id),
        )


def clear_history() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses")
