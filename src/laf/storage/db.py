from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("laf.db")

REQUIRED_COLUMNS: dict[str, str] = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "ts_utc": "TEXT NOT NULL",
    "input_sha256": "TEXT NOT NULL",
    "input_len": "INTEGER NOT NULL",
    "data_classification": "TEXT NOT NULL",
    "allowed": "INTEGER NOT NULL",
    "risk_score": "INTEGER NOT NULL",
    "redactions_json": "TEXT NOT NULL",
    "violations_json": "TEXT NOT NULL",
    "sanitized_text": "TEXT NOT NULL",
}


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _existing_columns(conn: sqlite3.Connection, table: str) -> dict[str, dict[str, Any]]:
    """
    Returns mapping of column name -> info dict from PRAGMA table_info.
    """
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    info: dict[str, dict[str, Any]] = {}
    for cid, name, coltype, notnull, dflt_value, pk in rows:
        info[name] = {
            "cid": cid,
            "type": coltype,
            "notnull": bool(notnull),
            "default": dflt_value,
            "pk": bool(pk),
        }
    return info


def init_db() -> None:
    with get_conn() as conn:
        if not _table_exists(conn, "evaluations"):
            cols_sql = ",\n            ".join(
                f"{name} {decl}" for name, decl in REQUIRED_COLUMNS.items()
            )
            conn.execute(f"""
            CREATE TABLE evaluations (
            {cols_sql}
            )
            """)
            conn.commit()
            return

        # Migration: add missing columns that our app expects.
        existing = _existing_columns(conn, "evaluations")
        for name, decl in REQUIRED_COLUMNS.items():
            if name in existing:
                continue
            if name == "id":
                # If id missing, we'd need a rebuild. Assume legacy already has it.
                continue
            conn.execute(f"ALTER TABLE evaluations ADD COLUMN {name} {decl}")
        conn.commit()


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def log_evaluation(
    *,
    input_text: str,
    data_classification: str,
    allowed: bool,
    risk_score: int,
    redactions: list[str],
    violations: list[dict[str, Any]],
    sanitized_text: str,
) -> None:
    with get_conn() as conn:
        init_db()
        cols = _existing_columns(conn, "evaluations")

        ts = datetime.now(timezone.utc).isoformat()

        # Legacy schemas sometimes use `timestamp` (NOT NULL) instead of `ts_utc`.
        # We'll populate whichever exists to satisfy constraints.
        insert_cols: list[str] = []
        values: list[Any] = []

        if "ts_utc" in cols:
            insert_cols.append("ts_utc")
            values.append(ts)

        if "timestamp" in cols:
            insert_cols.append("timestamp")
            values.append(ts)

        # Standard fields (support older column names if they differ)
        # Our project standard names:
        insert_cols += [
            "input_sha256",
            "input_len",
            "data_classification",
            "allowed",
            "risk_score",
            "redactions_json",
            "violations_json",
            "sanitized_text",
        ]
        values += [
            sha256_text(input_text),
            len(input_text or ""),
            data_classification,
            1 if allowed else 0,
            int(risk_score),
            json.dumps(redactions or [], ensure_ascii=False),
            json.dumps(violations or [], ensure_ascii=False),
            sanitized_text or "",
        ]

        placeholders = ", ".join(["?"] * len(values))
        col_sql = ", ".join(insert_cols)

        conn.execute(
            f"""
            INSERT INTO evaluations ({col_sql})
            VALUES ({placeholders})
            """,
            tuple(values),
        )
        conn.commit()
