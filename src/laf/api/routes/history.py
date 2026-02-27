from __future__ import annotations

import json
from fastapi import APIRouter
from laf.storage.db import get_conn

router = APIRouter()

@router.get("/history")
def history(limit: int = 50):
    limit = max(1, min(int(limit), 500))
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, ts_utc, data_classification, allowed, risk_score, redactions_json, violations_json "
            "FROM evaluations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "ts_utc": r[1],
            "data_classification": r[2],
            "allowed": bool(r[3]),
            "risk_score": r[4],
            "redactions_applied": json.loads(r[5]),
            "violations": json.loads(r[6]),
        })
    return out
