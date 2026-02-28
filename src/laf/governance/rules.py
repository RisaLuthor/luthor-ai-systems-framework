from __future__ import annotations

import re
from typing import List, Tuple

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)

_PHONE_RE = re.compile(
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"
)

_SSN_RE = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")

_SECRET_RE_LIST = [
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
]


def detect_pii(text: str) -> List[str]:
    findings: List[str] = []
    if not text:
        return findings

    if _EMAIL_RE.search(text):
        findings.append("PII_EMAIL")
    if _PHONE_RE.search(text):
        findings.append("PII_PHONE")
    if _SSN_RE.search(text):
        findings.append("PII_SSN")

    return findings


def redact_pii(text: str) -> Tuple[str, List[str]]:
    if not text:
        return "", []

    redactions: List[str] = []
    sanitized = text

    if _EMAIL_RE.search(sanitized):
        sanitized = _EMAIL_RE.sub("[REDACTED:EMAIL]", sanitized)
        redactions.append("EMAIL")

    if _PHONE_RE.search(sanitized):
        sanitized = _PHONE_RE.sub("[REDACTED:PHONE]", sanitized)
        redactions.append("PHONE")

    if _SSN_RE.search(sanitized):
        sanitized = _SSN_RE.sub("[REDACTED_SSN]", sanitized)
        redactions.append("SSN")

    return sanitized, redactions


def detect_secrets(text: str) -> bool:
    if not text:
        return False
    return any(rx.search(text) for rx in _SECRET_RE_LIST)
