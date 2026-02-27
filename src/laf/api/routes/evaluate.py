from fastapi import APIRouter
from laf.models import EvaluateRequest, EvaluateResponse
from laf.governance.policy_engine import evaluate as eval_policy

router = APIRouter()

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    allowed, risk, violations, redactions, sanitized, audit = eval_policy(req)
    return EvaluateResponse(
        allowed=allowed,
        risk_score=risk,
        violations=violations,
        redactions_applied=redactions,
        sanitized_text=sanitized,
        audit_trail=audit,
    )
