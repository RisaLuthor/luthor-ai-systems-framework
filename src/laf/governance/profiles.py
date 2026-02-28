from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class PolicyProfile:
    name: str
    version: str
    description: str
    rules: Dict[str, Any]
    source_path: str


def _repo_root() -> Path:
    # repo root is 3 up from src/laf/governance/
    return Path(__file__).resolve().parents[3]


def resolve_profile_path(profile: str | None) -> Path:
    """
    profile can be:
      - None => policies/default.yaml
      - "default" => policies/default.yaml
      - "restricted" => policies/restricted.yaml
      - "policies/custom.yaml" or absolute path
    """
    root = _repo_root()
    if not profile or profile.strip() == "":
        return root / "policies" / "default.yaml"

    p = profile.strip()
    if p.endswith(".yml") or p.endswith(".yaml"):
        path = Path(p)
        return path if path.is_absolute() else (root / path)

    # named profile
    return root / "policies" / f"{p}.yaml"


def load_profile(profile: str | None = None) -> PolicyProfile:
    path = resolve_profile_path(profile)
    if not path.exists():
        raise FileNotFoundError(f"Policy profile not found: {path.as_posix()}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return PolicyProfile(
        name=str(data.get("name", path.stem)),
        version=str(data.get("version", "0.0")),
        description=str(data.get("description", "")),
        rules=dict(data.get("rules", {})),
        source_path=path.as_posix(),
    )
