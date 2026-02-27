from __future__ import annotations

from pathlib import Path
from typing import Any
import importlib.resources as ir

import yaml


def _package_policies_dir() -> Path | None:
    """
    When installed (editable or wheel), policies can be packaged under laf/policies.
    This returns a real filesystem path when available.
    """
    try:
        pkg = ir.files("laf").joinpath("policies")
        # as_file gives a context manager; but in editable installs this is already a Path-like
        # We'll try to materialize a path safely.
        with ir.as_file(pkg) as p:
            return Path(p)
    except Exception:
        return None


def _repo_policies_dir() -> Path:
    # src/laf/governance/profiles.py -> src/laf/governance -> src/laf -> src -> repo
    return Path(__file__).resolve().parents[3] / "policies"


def load_profile(profile_name: str) -> dict[str, Any]:
    candidates: list[Path] = []

    pkg_dir = _package_policies_dir()
    if pkg_dir:
        candidates.append(pkg_dir / f"{profile_name}.yaml")

    candidates.append(_repo_policies_dir() / f"{profile_name}.yaml")
    candidates.append(Path.cwd() / "policies" / f"{profile_name}.yaml")

    for path in candidates:
        if path.exists():
            data = yaml.safe_load(path.read_text())
            if not isinstance(data, dict) or "name" not in data:
                raise ValueError(f"Invalid policy profile: {path}")
            return data

    raise FileNotFoundError(f"Policy profile not found. Tried: {', '.join(str(p) for p in candidates)}")
