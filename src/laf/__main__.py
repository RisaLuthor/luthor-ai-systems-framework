from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

from laf.governance.models import EvaluateRequest
from laf.governance.policy_engine import evaluate as eval_policy


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _write_markdown_report(reports_dir: Path, rows: List[Dict[str, Any]]) -> Path:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = reports_dir / f"scenario_report_{ts}.md"

    lines: List[str] = []
    lines.append(f"# LAF Scenario Run Report ({ts} UTC)")
    lines.append("")
    lines.append("| scenario | allowed | risk_score | redactions | violations |")
    lines.append("|---|---:|---:|---|---|")

    for r in rows:
        scen = r.get("scenario", "")
        allowed = r.get("allowed", "")
        risk = r.get("risk_score", "")
        redactions = ", ".join(r.get("redactions_applied", []) or [])
        violations = ", ".join([v.get("code", "") for v in (r.get("violations") or [])])
        lines.append(f"| {scen} | {allowed} | {risk} | {redactions} | {violations} |")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def run_scenarios(path_str: str) -> int:
    scenarios_path = Path(path_str)
    if not scenarios_path.exists():
        raise SystemExit(f"Path not found: {scenarios_path}")

    # Always write to ./reports relative to current working dir (matches tests)
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    scenario_files = sorted(scenarios_path.glob("*.yaml"))
    rows: List[Dict[str, Any]] = []

    for sf in scenario_files:
        spec = _load_yaml(sf)
        req = EvaluateRequest(
            input_text=spec.get("input_text", ""),
            data_classification=spec.get("data_classification", "INTERNAL"),
            policy_profile=spec.get("policy_profile", "default"),
        )

        allowed, risk, violations, redactions, sanitized, audit = eval_policy(req)

        # Ensure violations is list[dict] for JSON
        vio_out: List[dict] = []
        for v in violations or []:
            if hasattr(v, "model_dump"):
                vio_out.append(v.model_dump())
            elif isinstance(v, dict):
                vio_out.append(v)
            else:
                vio_out.append({"code": "UNKNOWN", "message": str(v)})

        rows.append(
            {
                "scenario": spec.get("name", sf.stem),
                "file": str(sf),
                "allowed": bool(allowed),
                "risk_score": int(risk),
                "redactions_applied": list(redactions or []),
                "sanitized_text": sanitized,
                "violations": vio_out,
                "audit_trail": list(audit or []),
            }
        )

    # 1) markdown report (you already had this behavior)
    md_path = _write_markdown_report(reports_dir, rows)
    print(f"Wrote report: {md_path}")

    # 2) REQUIRED by tests: reports/run.summary.json
    summary_path = reports_dir / "run.summary.json"
    summary_payload = {
        "scenario_count": len(rows),
        "allowed": sum(1 for r in rows if r["allowed"]),
        "blocked": sum(1 for r in rows if not r["allowed"]),
        "scenarios": [
            {
                "name": r["scenario"],
                "allowed": r["allowed"],
                "risk_score": r["risk_score"],
                "redactions_applied": r["redactions_applied"],
                "violations": [v.get("code") for v in (r.get("violations") or [])],
            }
            for r in rows
        ],
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="laf")
    sub = parser.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run", help="Run scenario files (YAML) and write reports/")
    runp.add_argument("path", help="Path to directory of scenario YAML files")

    args = parser.parse_args()
    if args.cmd == "run":
        return run_scenarios(args.path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
