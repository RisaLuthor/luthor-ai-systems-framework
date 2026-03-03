from __future__ import annotations

from pathlib import Path
from typing import List

import yaml

from laf.scenarios.schema import Scenario


def load_scenario_file(path: Path) -> Scenario:
    data = yaml.safe_load(path.read_text()) or {}
    if "name" not in data:
        data["name"] = path.stem
    return Scenario.model_validate(data)


def discover_scenarios(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    # directory: load all *.yaml / *.yml files
    files = sorted(list(path.glob("*.yaml")) + list(path.glob("*.yml")))
    return files
