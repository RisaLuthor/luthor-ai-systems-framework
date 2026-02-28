from __future__ import annotations

from fastapi import APIRouter

from laf.governance.models import EvaluateRequest, EvaluateResponse
from laf.governance.policy_engine import evaluate as eval_policy

# If your project has an audit logger, keep it. If not, this import can be removed.
try:
    from laf.storage.audit import log_evaluation  # type: ignore
except Exception:  # pragma: no cover
    log_evaluation = None  # type: ignore


router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    """
    Evaluate an input against governance policies and return:
      - allowed (bool)
      - risk_score (0-100)
      - violations (list of structured violations)
      - redactions_applied (list of redaction categories applied)
      - sanitized_text (string with redactions applied)
      - audit_trail (list of decision/audit breadcrumbs)
    """
    allowed, risk, violations, redactions, sanitized, audit = eval_policy(req)

    # Make violations JSON-safe
    violations_out = []
    for v in violations or []:
        if hasattr(v, "model_dump"):
            violations_out.append(v.model_dump())
        elif isinstance(v, dict):
            violations_out.append(v)
        else:
            violations_out.append({"message": str(v)})

    # Persist audit record (logging should NEVER break the API)
    if log_evaluation is not None:
        try:
            # Prefer kwargs (most likely signature)
            log_evaluation(
                input_text=req.input_text,
                data_classification=req.data_classification,
                allowed=allowed,
                risk_score=risk,
                redactions_applied=redactions,
                violations=violations_out,
                sanitized_text=sanitized,
                audit_trail=audit,
            )
        except TypeError:
            # Fallback: some implementations may accept a single keyword like "record"
            try:
                log_evaluation(record={
                    "input_text": req.input_text,
                    "data_classification": req.data_classification,
                    "allowed": allowed,
                    "risk_score": risk,
                    "violations": violations_out,
                    "redactions_applied": redactions,
                    "sanitized_text": sanitized,
                    "audit_trail": audit,
                })
            except Exception:
                pass
        except Exception:
            pass

    return EvaluateResponse(
        allowed=allowed,
        risk_score=risk,
        violations=violations_out,
        redactions_applied=redactions,
        sanitized_text=sanitized,
        audit_trail=audit,
    )
