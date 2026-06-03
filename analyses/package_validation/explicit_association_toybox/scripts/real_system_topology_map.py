from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path

import yaml

from .topology_reductions import HUANG_RADOSZ_TOPOLOGIES

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ANALYSIS_ROOT / "config" / "real_system_topology_map.yaml"

REQUIRED_FIELDS = {
    "system_id",
    "source_paper",
    "component_family",
    "assigned_topology",
    "rigorous_topology",
    "parameter_source_status",
    "validation_role",
}


def load_real_system_topology_map(path: Path = DEFAULT_CONFIG) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("systems"), list):
        raise ValueError(f"{path} must define a systems list.")
    return expand_real_system_rows(data["systems"])


def expand_real_system_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    expanded: list[dict[str, object]] = []
    for raw in rows:
        missing = REQUIRED_FIELDS - set(raw)
        if missing:
            raise ValueError(f"real-system topology row is missing required fields: {sorted(missing)}")
        row = dict(raw)
        assigned_key = _topology_key(str(row["assigned_topology"]), field_name="assigned_topology")
        rigorous_key = _topology_key(str(row["rigorous_topology"]), field_name="rigorous_topology")
        if not str(row["source_paper"]).strip():
            raise ValueError("real-system topology row must include source_paper metadata.")
        row["assigned_topology_key"] = assigned_key
        row["rigorous_topology_key"] = rigorous_key
        row["assigned_source_formula_id"] = f"huang_radosz_table_vii_{assigned_key.lower()}"
        row["rigorous_source_formula_id"] = f"huang_radosz_table_vii_{rigorous_key.lower()}"
        expanded.append(row)
    if not expanded:
        raise ValueError("real-system topology map must contain at least one row.")
    return expanded


def _topology_key(value: str, *, field_name: str) -> str:
    token = value.strip().lower()
    if token.startswith("hr_"):
        token = token[3:]
    key = token.upper()
    if key not in HUANG_RADOSZ_TOPOLOGIES:
        raise ValueError(f"{field_name} does not match a Huang/Radosz topology: {value}")
    return key


def main() -> None:
    print(json.dumps(load_real_system_topology_map(), indent=2))


if __name__ == "__main__":
    main()
