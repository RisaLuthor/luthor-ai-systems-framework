from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal


class EvaluateRequest(BaseModel):
    input_text: str = Field(..., min_length=1, description="User-provided text to evaluate.")
    data_classification: Literal["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"] = "INTERNAL"
    policy_profile: Literal["default"] = "default"


class Violation(BaseModel):
    code: str
    message: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]


class EvaluateResponse(BaseModel):
    allowed: bool
    risk_score: int = Field(..., ge=0, le=100)
    violations: list[Violation] = Field(default_factory=list)
    redactions_applied: list[str] = Field(default_factory=list)
    sanitized_text: str
    audit_trail: list[str] = Field(default_factory=list)
