from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

from laf.models import EvaluateRequest
from laf.governance.policy_engine import evaluate as eval_policy


def run_scenarios(path: str) -> int:
    base = Path(path)
    files: list[Path] = []
    if base.is_dir():
        files = sorted([p for p in base.rglob("*.yml")] + [p for p in base.rglob("*.yaml")])
    elif base.is_file():
        files = [base]
    else:
        print(f"Path not found: {path}")
        return 2

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "scenario_count": len(files),
        "results": [],
    }

    import yaml  # noqa: PLC0415

    for f in files:
        scenario = yaml.safe_load(f.read_text())
        req = EvaluateRequest(
            input_text=scenario["input_text"],
            data_classification=scenario.get("data_classification", "INTERNAL"),
            policy_profile=scenario.get("policy_profile", "default"),
        )

        allowed, risk, violations, redactions, sanitized, audit = eval_policy(req)

        expected = scenario.get("expected", {})
        expected_allowed = expected.get("allowed")
        expected_violation_codes = set(expected.get("violation_codes", []))

        actual_violation_codes = {v.code for v in violations}
        checks = []
        if expected_allowed is not None:
            checks.append(("allowed", expected_allowed == allowed))
        if expected_violation_codes:
            checks.append(("violation_codes", expected_violation_codes.issubset(actual_violation_codes)))

        passed = all(ok for _, ok in checks) if checks else True

        report = {
            "scenario_file": str(f),
            "pass": passed,
            "allowed": allowed,
            "risk_score": risk,
            "violations": [v.model_dump() for v in violations],
            "redactions_applied": redactions,
            "sanitized_text": sanitized,
            "audit_trail": audit,
            "checks": [{"name": n, "ok": ok} for n, ok in checks],
        }

        summary["results"].append(report)

        out_file = out_dir / (f.stem + ".report.json")
        out_file.write_text(json.dumps(report, indent=2))

    (out_dir / "run.summary.json").write_text(json.dumps(summary, indent=2))
    print(f"Wrote {len(files)} report(s) to {out_dir}/")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="laf")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run YAML scenarios and generate JSON reports")
    run.add_argument("path", help="Scenario file or directory")

    args = parser.parse_args()
    if args.cmd == "run":
        return run_scenarios(args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
