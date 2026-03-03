from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

from laf.governance.models import EvaluateRequest
from laf.governance.policy_engine import evaluate as eval_policy
from laf.scenarios.loader import discover_scenarios, load_scenario_file


@dataclass
class ScenarioResult:
    file: str
    name: str
    passed: bool
    errors: List[str]
    actual: Dict[str, Any]


def _codes_from_violations(violations: List[Any]) -> List[str]:
    codes = []
    for v in violations or []:
        if isinstance(v, dict) and "code" in v:
            codes.append(v["code"])
        elif hasattr(v, "code"):
            codes.append(getattr(v, "code"))
    return codes


def _compare(expected: Dict[str, Any], actual: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if expected.get("allowed") is not None and expected["allowed"] != actual.get("allowed"):
        errors.append(f"allowed expected={expected['allowed']} actual={actual.get('allowed')}")

    exp_red = set(expected.get("redactions_applied") or [])
    act_red = set(actual.get("redactions_applied") or [])
    missing_red = sorted(exp_red - act_red)
    if missing_red:
        errors.append(f"missing redactions: {missing_red}")

    exp_v = set(expected.get("violations") or [])
    act_v = set(actual.get("violation_codes") or [])
    missing_v = sorted(exp_v - act_v)
    if missing_v:
        errors.append(f"missing violations: {missing_v}")

    return (len(errors) == 0), errors


def run_scenarios(path: Path, reports_dir: Path = Path("reports")) -> int:
    scenario_files = discover_scenarios(path)
    if not scenario_files:
        print(f"No scenario files found at: {path}")
        return 2

    reports_dir.mkdir(parents=True, exist_ok=True)

    results: List[ScenarioResult] = []
    for sf in scenario_files:
        scenario = load_scenario_file(sf)

        req = EvaluateRequest(
            input_text=scenario.input_text,
            data_classification=scenario.data_classification,
            policy_profile=scenario.policy_profile,
        )

        allowed, risk, violations, redactions, sanitized, audit = eval_policy(req)
        violation_codes = _codes_from_violations(violations)

        actual = {
            "allowed": allowed,
            "risk_score": risk,
            "redactions_applied": redactions,
            "sanitized_text": sanitized,
            "violation_codes": violation_codes,
            "audit_trail": audit,
        }

        expected = {
            "allowed": scenario.expected.allowed,
            "redactions_applied": scenario.expected.redactions_applied,
            "violations": scenario.expected.violations,
        }

        passed, errors = _compare(expected, actual)
        results.append(
            ScenarioResult(
                file=str(sf),
                name=scenario.name,
                passed=passed,
                errors=errors,
                actual=actual,
            )
        )

    # Write a single report file
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"scenario_report_{ts}.md"

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    lines = []
    lines.append(f"# LAF Scenario Report ({ts} UTC)")
    lines.append("")
    lines.append(f"- Total: **{total}**")
    lines.append(f"- Passed: **{passed}**")
    lines.append(f"- Failed: **{failed}**")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        lines.append(f"### {status} — {r.name}")
        lines.append(f"- File: `{r.file}`")
        if r.errors:
            lines.append(f"- Errors:")
            for e in r.errors:
                lines.append(f"  - {e}")
        lines.append(f"- Actual allowed: `{r.actual.get('allowed')}`")
        lines.append(f"- Actual redactions: `{r.actual.get('redactions_applied')}`")
        lines.append(f"- Actual violations: `{r.actual.get('violation_codes')}`")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote report: {report_path}")

    # Exit code: 0 if all pass else 1
    return 0 if failed == 0 else 1
