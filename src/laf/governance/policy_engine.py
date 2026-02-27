from __future__ import annotations

from laf.models import EvaluateRequest, Violation
from laf.safety.redaction import redact_pii
from laf.governance.profiles import load_profile


def _score(profile: dict, classification: str, findings: list[str]) -> int:
    weights = profile.get("weights", {})
    base_map = weights.get("base_by_classification", {})
    per = weights.get("per_finding", {})
    base = int(base_map.get(classification, 15))

    risk = base
    for f in findings:
        risk += int(per.get(f, 10))

    return max(0, min(100, risk))


def _blocked(profile: dict, classification: str, findings: list[str]) -> tuple[bool, str | None]:
    rules = profile.get("rules", {})
    block_if = rules.get("block_if", [])
    finding_set = set(findings)

    for rule in block_if:
        when = rule.get("when", {})
        if when.get("data_classification") and when["data_classification"] != classification:
            continue
        any_needed = set(when.get("findings_any", []))
        if any_needed and not (any_needed & finding_set):
            continue
        return True, rule.get("reason")
    return False, None


def evaluate(req: EvaluateRequest):
    audit: list[str] = []
    violations: list[Violation] = []

    profile = load_profile(req.policy_profile)
    audit.append(f"policy={profile.get('name')}@{profile.get('version')}")
    audit.append(f"classification={req.data_classification}")

    redaction = redact_pii(req.input_text)
    findings = redaction.findings

    if findings:
        audit.append(f"findings={','.join(findings)}")
        violations.append(
            Violation(
                code="FINDINGS_DETECTED",
                message=f"Detected findings: {', '.join(findings)}",
                severity="MEDIUM" if req.data_classification in ("PUBLIC", "INTERNAL") else "HIGH",
            )
        )

    risk = _score(profile, req.data_classification, findings)

    blocked, reason = _blocked(profile, req.data_classification, findings)
    allowed = not blocked

    if blocked:
        audit.append("decision=blocked")
        violations.append(
            Violation(
                code="POLICY_BLOCK",
                message=reason or "Blocked by policy.",
                severity="HIGH",
            )
        )
    else:
        audit.append("decision=allowed")

    return allowed, risk, violations, redaction.redactions_applied, redaction.text, audit
