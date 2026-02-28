from __future__ import annotations

import re
from typing import List, Tuple


# Very small, deterministic PII patterns for MVP tests
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(
    r"\b(?:\+?1[\s\-\.]?)?(?:\(?\d{3}\)?[\s\-\.]?)\d{3}[\s\-\.]?\d{4}\b"
)


def detect_pii(text: str) -> List[str]:
    findings: List[str] = []
    if not text:
        return findings

    if _EMAIL_RE.search(text):
        findings.append("PII_EMAIL")
    if _PHONE_RE.search(text):
        findings.append("PII_PHONE")

    return findings


def redact_pii(text: str, findings: List[str]) -> Tuple[List[str], str]:
    """
    Returns: (redactions_applied, sanitized_text)

    Tests expect:
      - redactions_applied contains "EMAIL" (and/or "PHONE")
      - sanitized_text contains "[REDACTED:EMAIL]" or "[REDACTED:PHONE]"
    """
    redactions: List[str] = []
    sanitized = text or ""

    if "PII_EMAIL" in findings:
        sanitized = _EMAIL_RE.sub("[REDACTED:EMAIL]", sanitized)
        redactions.append("EMAIL")

    if "PII_PHONE" in findings:
        sanitized = _PHONE_RE.sub("[REDACTED:PHONE]", sanitized)
        redactions.append("PHONE")

    return redactions, sanitized
