from __future__ import annotations

from typing import Any, Dict, List, Tuple

from laf.governance.models import EvaluateRequest, Violation
from laf.governance.profiles import load_profile
from laf.governance.pii_detect import detect_pii, redact_pii


def _as_dict(profile: Any) -> Dict[str, Any]:
    """Normalize PolicyProfile (or dict) into a plain dict."""
    if profile is None:
        return {}
    if isinstance(profile, dict):
        return profile
    # Pydantic v2
    if hasattr(profile, "model_dump"):
        return profile.model_dump()
    # Dataclass / object with __dict__
    if hasattr(profile, "__dict__"):
        return dict(profile.__dict__)
    return {}


def _get(profile: Any, key: str, default: Any = None) -> Any:
    d = _as_dict(profile)
    return d.get(key, default)


def _score(profile: Any, classification: str, findings: List[str]) -> int:
    # weights can be defined at top-level or under a "weights" key; default to empty.
    weights = _get(profile, "weights", {}) or {}
    # if your profile stores weights differently, this still won't crash.
    base = int(weights.get("base", 0) or 0)

    # simple deterministic scoring:
    score = base
    if "PII_EMAIL" in findings:
        score += int(weights.get("pii_email", 20) or 20)
    if "PII_PHONE" in findings:
        score += int(weights.get("pii_phone", 20) or 20)

    # classification multiplier
    if classification.upper() == "RESTRICTED":
        score += int(weights.get("restricted_bonus", 40) or 40)
    elif classification.upper() == "CONFIDENTIAL":
        score += int(weights.get("confidential_bonus", 20) or 20)

    return max(0, min(100, score))


def evaluate(req: EvaluateRequest) -> Tuple[bool, int, List[Violation], List[str], str, List[str]]:
    audit: List[str] = []
    violations: List[Violation] = []
    redactions: List[str] = []

    profile = load_profile(req.policy_profile)

    name = _get(profile, "name", req.policy_profile)
    version = _get(profile, "version", "unknown")
    audit.append(f"policy={name}@{version}")

    rules = _get(profile, "rules", {}) or {}
    pii_cfg = (rules.get("pii") or {})
    pii_enabled = bool(pii_cfg.get("enabled", True))

    text = req.input_text or ""
    findings: List[str] = []

    if pii_enabled and text:
        findings = detect_pii(text)
        if findings:
            violations.append(
                Violation(
                    code="FINDINGS_DETECTED",
                    message=f"Detected: {', '.join(findings)}",
                    severity="MEDIUM",
                    rule="pii",
                )
            )
            # apply redactions
            redactions, text = redact_pii(text, findings)
            audit.append(f"redactions={redactions}")

    risk = _score(profile, req.data_classification, findings)

    # Block policy: if RESTRICTED and any PII present -> block
    allowed = True
    if req.data_classification.upper() == "RESTRICTED" and findings:
        allowed = False
        violations.append(
            Violation(
                code="POLICY_BLOCK",
                message="RESTRICTED data cannot contain PII",
                severity="HIGH",
                rule="classification",
            )
        )

    audit.append(f"allowed={allowed}")
    audit.append(f"risk_score={risk}")
    return allowed, risk, violations, redactions, text, audit
