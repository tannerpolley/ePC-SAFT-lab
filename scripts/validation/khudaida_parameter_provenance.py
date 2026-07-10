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


def _normalized_pair(left: str, right: str) -> tuple[str, str] | None:
    if left == right or left not in KHUDAIDA_COMPONENTS or right not in KHUDAIDA_COMPONENTS:
        return None
    left_index = KHUDAIDA_COMPONENTS.index(left)
    right_index = KHUDAIDA_COMPONENTS.index(right)
    return (left, right) if left_index < right_index else (right, left)


def _finite_value(raw: object, *, label: str) -> float:
    text = str(raw if raw is not None else "").strip()
    if not text:
        raise ValueError(f"missing numeric value for {label}")
    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError(f"non-numeric value for {label}: {text!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite value for {label}")
    return value


def _pair_rows(
    rows: list[dict[str, str]],
    *,
    owner: str,
) -> tuple[dict[tuple[str, str], dict[str, str]], list[str]]:
    by_pair: dict[tuple[str, str], dict[str, str]] = {}
    blockers: list[str] = []
    for row in rows:
        left = str(row.get("component_i", "")).strip()
        right = str(row.get("component_j", "")).strip()
        pair = _normalized_pair(left, right)
        if pair is None:
            blockers.append(f"parameter_provenance:invalid_{owner}_pair:{left}/{right}")
            continue
        label = f"{pair[0]}/{pair[1]}"
        if pair in by_pair:
            blockers.append(f"parameter_provenance:duplicate_{owner}_pair:{label}")
            continue
        by_pair[pair] = row
    return by_pair, blockers


def _matrix_value_receipt(path: Path) -> tuple[dict[str, Any], dict[tuple[str, str], float], list[str]]:
    if not path.is_file():
        return (
            {"path": path.as_posix(), "executable_values_present": False, "value_count": 0},
            {},
            [f"parameter_provenance:missing_executable_matrix:{path.stem}"],
        )
    rows = _read_csv(path)
    rows_by_component: dict[str, dict[str, str]] = {}
    blockers: list[str] = []
    value_count = 0
    for row in rows:
        row_component = str(row.get("component", "")).strip()
        if row_component not in KHUDAIDA_COMPONENTS:
            blockers.append(f"parameter_provenance:invalid_matrix_row:{path.stem}:{row_component}")
            continue
        if row_component in rows_by_component:
            blockers.append(f"parameter_provenance:duplicate_matrix_row:{path.stem}:{row_component}")
            continue
        rows_by_component[row_component] = row
        for component in KHUDAIDA_COMPONENTS:
            raw = str(row.get(component, "")).strip()
            if not raw:
                continue
            _finite_value(raw, label=f"{path.stem}:{row_component}/{component}")
            value_count += 1
    pair_values: dict[tuple[str, str], float] = {}
    for left, right in combinations(KHUDAIDA_COMPONENTS, 2):
        label = f"{left}/{right}"
        left_row = rows_by_component.get(left)
        right_row = rows_by_component.get(right)
        if left_row is None or right_row is None:
            blockers.append(f"parameter_provenance:missing_executable_matrix_pair:{label}")
            continue
        forward = _finite_value(left_row.get(right), label=f"{path.stem}:{label}")
        reverse = _finite_value(right_row.get(left), label=f"{path.stem}:{right}/{left}")
        if forward != reverse:
            blockers.append(f"parameter_provenance:asymmetric_executable_matrix:{label}")
        pair_values[(left, right)] = forward
    for component in KHUDAIDA_COMPONENTS:
        row = rows_by_component.get(component)
        if row is None:
            continue
        diagonal = _finite_value(row.get(component), label=f"{path.stem}:{component}/{component}")
        if diagonal != 0.0:
            blockers.append(f"parameter_provenance:nonzero_executable_matrix_diagonal:{component}")
    return (
        {
            "path": path.as_posix(),
            "executable_values_present": value_count > 0,
            "value_count": value_count,
        },
        pair_values,
        blockers,
    )


def evaluate_khudaida_parameter_provenance(analysis_root: Path) -> dict[str, Any]:
    interaction_root = analysis_root / "parameters" / "mixed" / "binary_interaction"
    manifest_path = interaction_root / "source_manifest.csv"
    source_path = analysis_root / "shared" / "source" / "table_7_epcsaft_kij.csv"
    source_rows = _read_csv(source_path) if source_path.is_file() else []
    manifest_rows = _read_csv(manifest_path) if manifest_path.is_file() else []
    expected_pairs = list(combinations(KHUDAIDA_COMPONENTS, 2))
    source_map, source_pair_blockers = _pair_rows(source_rows, owner="source")
    manifest_by_family = {
        family: [row for row in manifest_rows if row.get("parameter") == family]
        for family in REQUIRED_INTERACTION_FAMILIES
    }

    k_manifest_map, manifest_pair_blockers = _pair_rows(manifest_by_family["k_ij"], owner="manifest")
    matrix_receipt, matrix_values, matrix_blockers = _matrix_value_receipt(interaction_root / "k_ij.csv")
    k_blockers: list[str] = [*source_pair_blockers, *manifest_pair_blockers, *matrix_blockers]
    unresolved_pairs: list[str] = []
    source_backed_pair_count = 0
    value_joined_pair_count = 0
    for left, right in expected_pairs:
        label = f"{left}/{right}"
        pair = (left, right)
        source_row = source_map.get(pair)
        manifest_row = k_manifest_map.get(pair)
        source_reference = str(source_row.get("source_reference", "")).strip() if source_row else ""
        manifest_status = str(manifest_row.get("provenance_status", "")).strip() if manifest_row else ""
        pair_blockers: list[str] = []
        source_value = (
            _finite_value(source_row.get("k_ij"), label=f"source:{label}")
            if source_row is not None
            else None
        )
        manifest_value = (
            _finite_value(manifest_row.get("value"), label=f"manifest:{label}")
            if manifest_row is not None
            else None
        )
        matrix_value = matrix_values.get(pair)
        if source_value is not None and manifest_value is not None and source_value != manifest_value:
            pair_blockers.append(f"parameter_provenance:source_manifest_value_mismatch:{label}")
        if manifest_value is not None and matrix_value is not None and manifest_value != matrix_value:
            pair_blockers.append(f"parameter_provenance:matrix_manifest_value_mismatch:{label}")
        if source_value is not None and matrix_value is not None and source_value != matrix_value:
            pair_blockers.append(f"parameter_provenance:matrix_source_value_mismatch:{label}")
        if source_value is not None and manifest_value is not None and matrix_value is not None and not pair_blockers:
            value_joined_pair_count += 1
        if not source_reference:
            unresolved_pairs.append(label)
            pair_blockers.append(f"parameter_provenance:unresolved_source_reference:{label}")
        elif manifest_status != "source_backed":
            pair_blockers.append(f"parameter_provenance:manifest_status_not_source_backed:{label}")
        if not pair_blockers:
            source_backed_pair_count += 1
        k_blockers.extend(pair_blockers)
    if not source_rows:
        k_blockers.append("parameter_provenance:missing_table_7_source_rows")
    if not manifest_by_family["k_ij"]:
        k_blockers.append("parameter_provenance:missing_manifest_family:k_ij")

    families: dict[str, dict[str, Any]] = {
        "k_ij": {
            "status": "source_backed" if not k_blockers else "partial_source_coverage",
            "source_backed_pair_count": source_backed_pair_count,
            "value_joined_pair_count": value_joined_pair_count,
            "total_pair_count": len(expected_pairs),
            "unresolved_pairs": unresolved_pairs,
            "blockers": sorted(set(k_blockers)),
            **matrix_receipt,
        }
    }
    blockers = list(k_blockers)
    unresolved_families: list[str] = []
    for family in ("l_ij", "k_hb_ij"):
        rows = manifest_by_family[family]
        statuses = sorted({str(row.get("provenance_status", "")).strip() for row in rows if row})
        matrix, _matrix_values, matrix_family_blockers = _matrix_value_receipt(interaction_root / f"{family}.csv")
        family_blockers = [f"parameter_provenance:unresolved_parameter_family:{family}"]
        if matrix["executable_values_present"]:
            family_blockers.append(f"parameter_provenance:unsourced_matrix_values_present:{family}")
        family_blockers.extend(matrix_family_blockers)
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
