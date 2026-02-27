from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICIES_DIR = Path("policies")


def load_profile(profile_name: str, policies_dir: Path = DEFAULT_POLICIES_DIR) -> dict[str, Any]:
    path = policies_dir / f"{profile_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Policy profile not found: {path}")
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or "name" not in data:
        raise ValueError(f"Invalid policy profile: {path}")
    return data
