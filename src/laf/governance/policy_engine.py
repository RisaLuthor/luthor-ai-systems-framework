from __future__ import annotations

from laf.models import EvaluateRequest, Violation
from laf.safety.redaction import redact_pii


def evaluate(req: EvaluateRequest):
    """
    MVP policy evaluation:
    - Redact common PII patterns
    - If classification is RESTRICTED and PII found => block
    - Score risk based on classification + findings
    """
    audit: list[str] = []
    violations: list[Violation] = []

    audit.append(f"classification={req.data_classification}")
    audit.append(f"policy_profile={req.policy_profile}")

    redaction = redact_pii(req.input_text)
    if redaction.redactions:
        audit.append(f"pii_detected={','.join(redaction.redactions)}")
        violations.append(
            Violation(
                code="PII_DETECTED",
                message=f"Detected PII types: {', '.join(redaction.redactions)}",
                severity="MEDIUM" if req.data_classification in ("PUBLIC", "INTERNAL") else "HIGH",
            )
        )

    # Base risk by classification
    base = {"PUBLIC": 5, "INTERNAL": 15, "CONFIDENTIAL": 35, "RESTRICTED": 55}[req.data_classification]
    risk = base + (20 * len(redaction.redactions))

    allowed = True
    if req.data_classification == "RESTRICTED" and redaction.redactions:
        allowed = False
        audit.append("decision=blocked (restricted+pii)")
        violations.append(
            Violation(
                code="RESTRICTED_PII_BLOCK",
                message="Restricted data cannot include PII in output/input.",
                severity="HIGH",
            )
        )
    else:
        audit.append("decision=allowed")

    risk = max(0, min(100, risk))
    return allowed, risk, violations, redaction.redactions, redaction.text, audit
