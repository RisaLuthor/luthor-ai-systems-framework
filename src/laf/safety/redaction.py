from __future__ import annotations

import re
from dataclasses import dataclass

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


@dataclass
class RedactionResult:
    text: str
    findings: list[str]          # e.g., ["PII_EMAIL"]
    redactions_applied: list[str]  # e.g., ["EMAIL"]


def redact_pii(text: str) -> RedactionResult:
    findings: list[str] = []
    redactions: list[str] = []
    out = text

    if EMAIL_RE.search(out):
        out = EMAIL_RE.sub("[REDACTED:EMAIL]", out)
        findings.append("PII_EMAIL")
        redactions.append("EMAIL")

    if PHONE_RE.search(out):
        out = PHONE_RE.sub("[REDACTED:PHONE]", out)
        findings.append("PII_PHONE")
        redactions.append("PHONE")

    if SSN_RE.search(out):
        out = SSN_RE.sub("[REDACTED:SSN]", out)
        findings.append("PII_SSN")
        redactions.append("SSN")

    return RedactionResult(text=out, findings=findings, redactions_applied=redactions)
