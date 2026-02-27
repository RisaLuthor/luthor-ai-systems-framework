from pathlib import Path
import json
import subprocess
import sys

def test_cli_run_generates_reports(tmp_path, monkeypatch):
    # Run from repo root but write reports to tmp dir by chdir
    repo_root = Path(__file__).resolve().parents[1]
    work = tmp_path / "work"
    work.mkdir()
    (work / "scenarios").mkdir()

    # copy example scenarios
    src = repo_root / "scenarios" / "examples"
    dst = work / "scenarios" / "examples"
    dst.mkdir(parents=True)
    for f in src.glob("*.yaml"):
        dst.joinpath(f.name).write_text(f.read_text())

    # run CLI
    r = subprocess.run(
        [sys.executable, "-m", "laf", "run", str(dst)],
        cwd=work,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr

    summary = work / "reports" / "run.summary.json"
    assert summary.exists()
    data = json.loads(summary.read_text())
    assert data["scenario_count"] >= 1
