from __future__ import annotations

from fastapi import APIRouter
from laf.storage.db import get_conn

router = APIRouter(tags=["audit"])


@router.get("/metrics")
def metrics():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
        allowed = conn.execute("SELECT COUNT(*) FROM evaluations WHERE allowed = 1").fetchone()[0]
        blocked = total - allowed
        avg_risk = conn.execute("SELECT COALESCE(AVG(risk_score), 0) FROM evaluations").fetchone()[0]

    pct_allowed = (allowed / total) * 100 if total else 0.0
    pct_blocked = (blocked / total) * 100 if total else 0.0

    return {
        "total": total,
        "allowed": allowed,
        "blocked": blocked,
        "pct_allowed": round(pct_allowed, 2),
        "pct_blocked": round(pct_blocked, 2),
        "avg_risk": round(float(avg_risk), 2),
    }
