from __future__ import annotations

import json
from fastapi import APIRouter
from laf.storage.db import get_conn

router = APIRouter(tags=["audit"])


@router.get("/history")
def history(limit: int = 50):
    limit = max(1, min(int(limit), 500))

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, ts_utc, input_sha256, input_len, data_classification, allowed, risk_score, redactions_json, violations_json "
            "FROM evaluations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "ts_utc": r[1],
            "input_sha256": r[2],
            "input_len": r[3],
            "data_classification": r[4],
            "allowed": bool(r[5]),
            "risk_score": r[6],
            "redactions_applied": json.loads(r[7]),
            "violations": json.loads(r[8]),
        })
    return out
