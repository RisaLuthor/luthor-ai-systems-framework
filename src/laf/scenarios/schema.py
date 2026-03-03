from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ScenarioExpected(BaseModel):
    allowed: Optional[bool] = None
    # Examples: ["EMAIL", "PHONE"]
    redactions_applied: List[str] = Field(default_factory=list)
    # Examples: ["FINDINGS_DETECTED", "POLICY_BLOCK"]
    violations: List[str] = Field(default_factory=list)


class Scenario(BaseModel):
    name: str = Field(default="unnamed_scenario")
    input_text: str = Field(default="")
    data_classification: str = Field(default="INTERNAL")
    policy_profile: str = Field(default="default")
    expected: ScenarioExpected = Field(default_factory=ScenarioExpected)
