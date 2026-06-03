from __future__ import annotations

from pathlib import Path

import yaml

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPER_SYSTEMS = ANALYSIS_ROOT / "config" / "paper_systems.yaml"


def load_paper_systems(path: Path = DEFAULT_PAPER_SYSTEMS) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    return dict(data)


def load_topology_grid(path: Path = DEFAULT_PAPER_SYSTEMS) -> dict[str, object]:
    data = load_paper_systems(path)
    grid = data.get("topology_grid")
    if not isinstance(grid, dict):
        raise ValueError(f"{path} must contain topology_grid.")
    return dict(grid)


def load_provider_property_cases(path: Path = DEFAULT_PAPER_SYSTEMS) -> dict[str, dict[str, object]]:
    data = load_paper_systems(path)
    cases = data.get("provider_property_cases")
    if not isinstance(cases, dict):
        raise ValueError(f"{path} must contain provider_property_cases.")
    normalized: dict[str, dict[str, object]] = {}
    for component, raw_case in cases.items():
        if not isinstance(raw_case, dict):
            raise ValueError(f"{component} provider case must be a mapping.")
        normalized[str(component).lower()] = dict(raw_case)
    return normalized
