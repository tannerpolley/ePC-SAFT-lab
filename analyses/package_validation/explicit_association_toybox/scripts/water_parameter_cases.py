from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path

import yaml

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ANALYSIS_ROOT / "config" / "water_parameter_cases.yaml"
DEFAULT_PUBLIC_SOURCES = ANALYSIS_ROOT / "config" / "public_property_sources.yaml"

REQUIRED_FIELDS = {
    "case_id",
    "topology_id",
    "parameter_source",
    "sigma_policy",
    "temperature_range_k",
    "property_source",
    "comparison_role",
}


def load_water_parameter_cases(path: Path = DEFAULT_CONFIG) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("cases"), list):
        raise ValueError(f"{path} must define a cases list.")
    return [_validate_case(row) for row in data["cases"]]


def link_water_cases_to_public_sources(
    cases: Iterable[Mapping[str, object]],
    *,
    sources_path: Path = DEFAULT_PUBLIC_SOURCES,
) -> list[dict[str, object]]:
    with sources_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("sources"), list):
        raise ValueError(f"{sources_path} must define a sources list.")
    water_source = next(
        (source for source in data["sources"] if str(source.get("component", "")).lower() == "water"),
        None,
    )
    if water_source is None:
        raise ValueError("public property sources must include water.")
    rows: list[dict[str, object]] = []
    for case in cases:
        row = _validate_case(case)
        row["property_source_component"] = str(water_source["component"]).lower()
        row["property_source_name"] = str(water_source["source_name"])
        row["property_source_nist_id"] = str(water_source["nist_id"])
        rows.append(row)
    return rows


def _validate_case(raw: Mapping[str, object]) -> dict[str, object]:
    missing = REQUIRED_FIELDS - set(raw)
    if missing:
        raise ValueError(f"water parameter case is missing required fields: {sorted(missing)}")
    row = dict(raw)
    topology_id = str(row["topology_id"])
    if not topology_id.startswith("hr_"):
        raise ValueError(f"water topology_id must use the hr_ prefix: {topology_id}")
    temperature_range = row["temperature_range_k"]
    if (
        not isinstance(temperature_range, list)
        or len(temperature_range) != 2
        or float(temperature_range[0]) >= float(temperature_range[1])
    ):
        raise ValueError("water temperature_range_k must be an increasing two-value list.")
    row["temperature_range_k"] = [float(temperature_range[0]), float(temperature_range[1])]
    return row


def main() -> None:
    print(json.dumps(link_water_cases_to_public_sources(load_water_parameter_cases()), indent=2))


if __name__ == "__main__":
    main()
