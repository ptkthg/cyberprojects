from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "threatlens.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
                created_at TEXT NOT NULL
            )
            """
        )


def insert_analysis(record: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analyses (
                ioc, ioc_type, score, risk_level, recommendation, summary,
                sources_json, evidence_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                record.get("created_at") or datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )


def list_analyses() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY datetime(created_at) DESC").fetchall()
    return [dict(row) for row in rows]


def clear_analyses() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses")
