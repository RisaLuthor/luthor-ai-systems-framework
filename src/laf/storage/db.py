from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path("laf.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_utc TEXT NOT NULL,
            data_classification TEXT NOT NULL,
            allowed INTEGER NOT NULL,
            risk_score INTEGER NOT NULL,
            redactions_json TEXT NOT NULL,
            violations_json TEXT NOT NULL,
            sanitized_text TEXT NOT NULL
        )
        """)
        conn.commit()


def log_evaluation(*, data_classification: str, allowed: bool, risk_score: int,
                   redactions: list[str], violations: list[dict], sanitized_text: str):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO evaluations (
            ts_utc, data_classification, allowed, risk_score,
            redactions_json, violations_json, sanitized_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            data_classification,
            1 if allowed else 0,
            int(risk_score),
            json.dumps(redactions, ensure_ascii=False),
            json.dumps(violations, ensure_ascii=False),
            sanitized_text,
        ))
        conn.commit()
