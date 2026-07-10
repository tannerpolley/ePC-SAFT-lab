from __future__ import annotations

import csv
import math
from itertools import combinations
from pathlib import Path
from typing import Any

KHUDAIDA_COMPONENTS = ("H2O", "Ethanol", "Butanol", "Na+", "Cl-")
REQUIRED_INTERACTION_FAMILIES = ("k_ij", "l_ij", "k_hb_ij")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _matrix_value_receipt(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": path.as_posix(), "executable_values_present": False, "value_count": 0}
    rows = _read_csv(path)
    value_count = 0
    for row in rows:
        for component in KHUDAIDA_COMPONENTS:
            raw = str(row.get(component, "")).strip()
            if not raw:
                continue
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError(f"non-finite {path.stem} value for {row.get('component', '')}/{component}")
            value_count += 1
    return {
        "path": path.as_posix(),
        "executable_values_present": value_count > 0,
        "value_count": value_count,
    }


def evaluate_khudaida_parameter_provenance(analysis_root: Path) -> dict[str, Any]:
    interaction_root = analysis_root / "parameters" / "mixed" / "binary_interaction"
    manifest_path = interaction_root / "source_manifest.csv"
    source_path = analysis_root / "shared" / "source" / "table_7_epcsaft_kij.csv"
    source_rows = _read_csv(source_path) if source_path.is_file() else []
    manifest_rows = _read_csv(manifest_path) if manifest_path.is_file() else []
    expected_pairs = list(combinations(KHUDAIDA_COMPONENTS, 2))
    source_map = {(row.get("component_i", ""), row.get("component_j", "")): row for row in source_rows}
    manifest_by_family = {
        family: [row for row in manifest_rows if row.get("parameter") == family]
        for family in REQUIRED_INTERACTION_FAMILIES
    }

    k_manifest_map = {
        (row.get("component_i", ""), row.get("component_j", "")): row for row in manifest_by_family["k_ij"]
    }
    k_blockers: list[str] = []
    unresolved_pairs: list[str] = []
    source_backed_pair_count = 0
    for left, right in expected_pairs:
        label = f"{left}/{right}"
        source_row = source_map.get((left, right)) or source_map.get((right, left))
        manifest_row = k_manifest_map.get((left, right)) or k_manifest_map.get((right, left))
        source_reference = str(source_row.get("source_reference", "")).strip() if source_row else ""
        manifest_status = str(manifest_row.get("provenance_status", "")).strip() if manifest_row else ""
        if not source_reference:
            unresolved_pairs.append(label)
            k_blockers.append(f"parameter_provenance:unresolved_source_reference:{label}")
        elif manifest_status != "source_backed":
            k_blockers.append(f"parameter_provenance:manifest_status_not_source_backed:{label}")
        else:
            source_backed_pair_count += 1
    if not source_rows:
        k_blockers.append("parameter_provenance:missing_table_7_source_rows")
    if not manifest_by_family["k_ij"]:
        k_blockers.append("parameter_provenance:missing_manifest_family:k_ij")

    families: dict[str, dict[str, Any]] = {
        "k_ij": {
            "status": "source_backed" if not k_blockers else "partial_source_coverage",
            "source_backed_pair_count": source_backed_pair_count,
            "total_pair_count": len(expected_pairs),
            "unresolved_pairs": unresolved_pairs,
            "blockers": sorted(set(k_blockers)),
            **_matrix_value_receipt(interaction_root / "k_ij.csv"),
        }
    }
    blockers = list(k_blockers)
    unresolved_families: list[str] = []
    for family in ("l_ij", "k_hb_ij"):
        rows = manifest_by_family[family]
        statuses = sorted({str(row.get("provenance_status", "")).strip() for row in rows if row})
        matrix = _matrix_value_receipt(interaction_root / f"{family}.csv")
        family_blockers = [f"parameter_provenance:unresolved_parameter_family:{family}"]
        if matrix["executable_values_present"]:
            family_blockers.append(f"parameter_provenance:unsourced_matrix_values_present:{family}")
        if not rows:
            family_blockers.append(f"parameter_provenance:missing_manifest_family:{family}")
        families[family] = {
            "status": "unresolved_parameter_family",
            "manifest_statuses": statuses,
            "blockers": family_blockers,
            **matrix,
        }
        unresolved_families.append(family)
        blockers.extend(family_blockers)

    blockers = sorted(set(blockers))
    return {
        "status": "source_backed" if not blockers else "partial_source_coverage",
        "parameter_family": "k_ij",
        "source_backed_pair_count": source_backed_pair_count,
        "total_pair_count": len(expected_pairs),
        "source_coverage": source_backed_pair_count / len(expected_pairs) if expected_pairs else 0.0,
        "unresolved_pairs": unresolved_pairs,
        "unresolved_families": sorted(unresolved_families),
        "families": families,
        "blocking": bool(blockers),
        "blockers": blockers,
    }
