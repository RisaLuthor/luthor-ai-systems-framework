from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Severity = Literal["LOW", "MEDIUM", "HIGH"]


class EvaluateRequest(BaseModel):
    input_text: str = Field(default="")
    data_classification: str = Field(default="INTERNAL")
    policy_profile: str = Field(default="default")


class Violation(BaseModel):
    code: str
    message: str
    severity: Severity = "MEDIUM"
    rule: Optional[str] = None


class EvaluateResponse(BaseModel):
    allowed: bool
    risk_score: int
    violations: List[Violation]
    redactions_applied: List[str]
    sanitized_text: str
    audit_trail: List[str]
