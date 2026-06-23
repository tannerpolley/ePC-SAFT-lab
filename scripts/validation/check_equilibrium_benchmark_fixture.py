from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASE_DIR = (
    REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_tp_flash" / "ethane_carbon_dioxide"
)
ACCEPTED_NEUTRAL_FLASH_MODEL_FAMILIES = {"PC-SAFT", "ePC-SAFT"}
PHASE_DISCOVERY_REQUIREMENTS = (
    "deterministic_screening",
    "continuous_tpd_minimization",
    "held_stage_i_stability",
    "held_stage_ii_dual_phase_discovery",
    "held_stage_iii_ipopt_refinement",
)
EXECUTABLE_FIXTURE_REQUIRED_FIELDS = (
    "species",
    "pure_component_parameters",
    "binary_interactions",
    "temperature",
    "pressure",
    "feed_composition",
    "expected_phase_count",
    "expected_phase_compositions",
    "expected_phase_fractions",
    "source_model_family",
    "source_path",
    "acceptance_tolerances",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _read_optional_phase_discovery_payload(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return _read_json(path)


def _float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped == "not_evaluated":
        return None
    return float(stripped)


def _phase_rows_by_case(phase_rows: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    by_case: dict[str, dict[str, dict[str, str]]] = {}
    for row in phase_rows:
        by_case.setdefault(row["case_key"], {})[row["phase"]] = row
    return by_case


def _indexed_columns(row: dict[str, str], prefix: str) -> list[str]:
    columns = []
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    for key in row:
        match = pattern.match(key)
        if match is not None:
            columns.append(key)
    return sorted(columns, key=lambda item: int(pattern.match(item).group(1)))  # type: ignore[union-attr]


def _source_path_present(metadata: dict[str, Any]) -> bool:
    source_path = metadata.get("source_path")
    source_paths = metadata.get("source_paths")
    return bool(source_path) or (isinstance(source_paths, dict) and any(source_paths.values()))


def _species_present(phase_rows: list[dict[str, str]], metadata: dict[str, Any]) -> bool:
    species = metadata.get("species")
    if isinstance(species, list) and species:
        return True
    component_columns = _indexed_columns(phase_rows[0], "component_") if phase_rows else []
    return bool(component_columns) and all(row.get(column, "").strip() for row in phase_rows for column in component_columns)


def _all_rows_have_finite(phase_rows: list[dict[str, str]], column: str) -> bool:
    try:
        return bool(phase_rows) and all(math.isfinite(float(row[column])) for row in phase_rows)
    except (KeyError, ValueError):
        return False


def _all_phase_compositions_present(phase_rows: list[dict[str, str]]) -> bool:
    phase_rows_only = [row for row in phase_rows if row.get("phase") != "feed"]
    if not phase_rows_only:
        return False
    try:
        return all(
            math.isclose(float(row["composition_sum"]), 1.0, rel_tol=0.0, abs_tol=1.0e-12)
            for row in phase_rows_only
        )
    except (KeyError, ValueError):
        return False


def _expected_phase_count_present(phase_rows: list[dict[str, str]], metadata: dict[str, Any]) -> bool:
    if metadata.get("expected_phase_count"):
        return True
    by_case = _phase_rows_by_case(phase_rows)
    return bool(by_case) and all({"vapor", "liquid"} <= set(phases) for phases in by_case.values())


def _has_pc_saft_parameter_fixture(metadata: dict[str, Any], case_dir: Path) -> bool:
    if metadata.get("pure_component_parameters"):
        return True
    return (case_dir / "pc_saft_parameters.csv").exists() or (case_dir / "epcsaft_parameters.csv").exists()


def _has_binary_interaction_fixture(metadata: dict[str, Any], case_dir: Path) -> bool:
    if metadata.get("binary_interactions"):
        return True
    return (case_dir / "binary_interactions.csv").exists()


def _fixture_field_status(
    metadata: dict[str, Any],
    case_dir: Path,
    phase_rows: list[dict[str, str]],
    computed_rows: list[dict[str, Any]],
) -> dict[str, str]:
    source_model_family = str(metadata.get("source_model_family", ""))
    accepted_model = source_model_family in ACCEPTED_NEUTRAL_FLASH_MODEL_FAMILIES
    feed_statuses = {str(row["reported_feed_status"]) for row in computed_rows}
    all_feeds_normalized = bool(computed_rows) and feed_statuses == {"normalized"}
    all_phase_fractions_present = bool(computed_rows) and all(
        row["material_balance_eligible"] and row["vapor_fraction"] is not None and row["liquid_fraction"] is not None
        for row in computed_rows
    )
    saft_vr_parameters_present = (case_dir / "saft_vr_parameters.csv").exists()

    return {
        "species": "present" if _species_present(phase_rows, metadata) else "missing",
        "pure_component_parameters": (
            "present"
            if accepted_model and _has_pc_saft_parameter_fixture(metadata, case_dir)
            else "rejected_saft_vr_parameters"
            if saft_vr_parameters_present and not accepted_model
            else "missing_pc_saft_parameters"
        ),
        "binary_interactions": (
            "present"
            if accepted_model and _has_binary_interaction_fixture(metadata, case_dir)
            else "rejected_saft_vr_binary_factors"
            if saft_vr_parameters_present and not accepted_model
            else "missing_binary_interactions"
        ),
        "temperature": "present" if _all_rows_have_finite(phase_rows, "temperature_K") else "missing",
        "pressure": "present" if _all_rows_have_finite(phase_rows, "pressure_MPa") else "missing",
        "feed_composition": "present" if all_feeds_normalized else "incomplete_reported_feed_not_normalized",
        "expected_phase_count": "present" if _expected_phase_count_present(phase_rows, metadata) else "missing",
        "expected_phase_compositions": "present" if _all_phase_compositions_present(phase_rows) else "missing",
        "expected_phase_fractions": (
            "present" if all_phase_fractions_present else "incomplete_material_balance_or_phase_fraction"
        ),
        "source_model_family": "present" if accepted_model else "rejected_model_family_mismatch",
        "source_path": "present" if _source_path_present(metadata) else "missing",
        "acceptance_tolerances": "present" if bool(metadata.get("acceptance_tolerances")) else "missing",
    }


def _composition(row: dict[str, str]) -> tuple[float, ...]:
    composition_columns = _indexed_columns(row, "x")
    if not composition_columns:
        raise ValueError("phase split row does not define x1, x2, ... composition columns")
    return tuple(float(row[column]) for column in composition_columns)


def _composition_sum(row: dict[str, str]) -> float:
    return float(row["composition_sum"])


def _lever_fraction(feed: tuple[float, ...], vapor: tuple[float, ...], liquid: tuple[float, ...]) -> float:
    candidates = [
        (feed[index] - liquid[index]) / (vapor[index] - liquid[index])
        for index in range(len(feed))
        if abs(vapor[index] - liquid[index]) > 1.0e-15
    ]
    if not candidates:
        raise ValueError("phase split cannot determine a lever-rule vapor fraction")
    vapor_fraction = sum(candidates) / len(candidates)
    if any(abs(candidate - vapor_fraction) > 1.0e-8 for candidate in candidates):
        raise ValueError("phase split gives inconsistent lever-rule vapor fractions")
    return vapor_fraction


def _material_balance_residual(
    feed: tuple[float, ...],
    vapor: tuple[float, ...],
    liquid: tuple[float, ...],
    vapor_fraction: float,
) -> float:
    liquid_fraction = 1.0 - vapor_fraction
    return max(
        abs(feed[index] - (vapor_fraction * vapor[index] + liquid_fraction * liquid[index]))
        for index in range(2)
    )


def _case_blockers(metadata: dict[str, Any], row: dict[str, Any]) -> list[str]:
    blockers = []
    source_model_family = str(metadata.get("source_model_family", ""))
    if source_model_family not in ACCEPTED_NEUTRAL_FLASH_MODEL_FAMILIES:
        blockers.append("model_family_mismatch")
    if str(metadata.get("runtime_model_support", "")) == "absent_from_epcsaft":
        blockers.append("saft_vr_runtime_absent")
    if row["reported_feed_status"] != "normalized":
        blockers.append("published_second_feed_composition_not_normalized")
    return list(dict.fromkeys(blockers))


def _computed_material_balance_rows(metadata: dict[str, Any], case_dir: Path) -> list[dict[str, Any]]:
    by_case = _phase_rows_by_case(_read_csv(case_dir / "phase_splits.csv"))
    rows: list[dict[str, Any]] = []
    for case_key in sorted(by_case):
        phases = by_case[case_key]
        feed_row = phases["feed"]
        vapor = _composition(phases["vapor"])
        liquid = _composition(phases["liquid"])
        feed = _composition(feed_row)
        feed_sum = _composition_sum(feed_row)
        normalized = math.isclose(feed_sum, 1.0, rel_tol=0.0, abs_tol=1.0e-12)
        row: dict[str, Any] = {
            "case_key": case_key,
            "reported_feed_status": "normalized" if normalized else "not_normalized",
            "material_balance_status": "blocked_by_published_feed",
            "vapor_fraction": None,
            "liquid_fraction": None,
            "max_abs_material_balance_residual": None,
            "material_balance_eligible": False,
            "blockers": [],
        }
        if normalized:
            vapor_fraction = _lever_fraction(feed, vapor, liquid)
            residual = _material_balance_residual(feed, vapor, liquid, vapor_fraction)
            row.update(
                {
                    "material_balance_status": "feasible_from_reported_feed",
                    "vapor_fraction": vapor_fraction,
                    "liquid_fraction": 1.0 - vapor_fraction,
                    "max_abs_material_balance_residual": residual,
                    "material_balance_eligible": residual <= 1.0e-10 and 0.0 < vapor_fraction < 1.0,
                }
            )
        row["blockers"] = _case_blockers(metadata, row)
        row["fixture_eligible"] = row["material_balance_eligible"] and not row["blockers"]
        rows.append(row)
    return rows


def _stored_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _stored_blockers(value: str) -> list[str]:
    return [] if not value.strip() else value.split(";")


def _compare_stored_material_balance(
    computed_rows: list[dict[str, Any]],
    stored_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    stored_by_case = {row["case_key"]: row for row in stored_rows}
    mismatches: list[dict[str, Any]] = []
    for computed in computed_rows:
        case_key = str(computed["case_key"])
        stored = stored_by_case.get(case_key)
        if stored is None:
            mismatches.append({"case_key": case_key, "field": "case_key", "stored": None, "computed": case_key})
            continue
        checks: tuple[tuple[str, Any, Any], ...] = (
            ("reported_feed_status", stored["reported_feed_status"], computed["reported_feed_status"]),
            ("material_balance_status", stored["material_balance_status"], computed["material_balance_status"]),
            ("vapor_fraction", _float_or_none(stored["vapor_fraction"]), computed["vapor_fraction"]),
            ("liquid_fraction", _float_or_none(stored["liquid_fraction"]), computed["liquid_fraction"]),
            (
                "max_abs_material_balance_residual",
                _float_or_none(stored["max_abs_material_balance_residual"]),
                computed["max_abs_material_balance_residual"],
            ),
            (
                "material_balance_eligible",
                _stored_bool(stored["material_balance_eligible"]),
                computed["material_balance_eligible"],
            ),
            ("fixture_eligible", _stored_bool(stored["fixture_eligible"]), computed["fixture_eligible"]),
            ("blockers", _stored_blockers(stored["blockers"]), computed["blockers"]),
        )
        for field, stored_value, computed_value in checks:
            if _values_match(stored_value, computed_value):
                continue
            mismatches.append(
                {
                    "case_key": case_key,
                    "field": field,
                    "stored": stored_value,
                    "computed": computed_value,
                }
            )
    return mismatches


def _values_match(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=1.0e-10, abs_tol=1.0e-12)
    return left == right


def _computed_feed_correction_rows(case_dir: Path) -> list[dict[str, Any]]:
    by_case = _phase_rows_by_case(_read_csv(case_dir / "phase_splits.csv"))
    rows: list[dict[str, Any]] = []
    for case_key, phases in sorted(by_case.items()):
        feed = phases["feed"]
        if math.isclose(_composition_sum(feed), 1.0, rel_tol=0.0, abs_tol=1.0e-12):
            continue
        vapor = _composition(phases["vapor"])
        liquid = _composition(phases["liquid"])
        candidate_feed = (float(feed["x1"]), 1.0 - float(feed["x1"]))
        vapor_fraction = _lever_fraction(candidate_feed, vapor, liquid)
        rows.append(
            {
                "case_key": case_key,
                "candidate_x1": candidate_feed[0],
                "candidate_x2": candidate_feed[1],
                "candidate_source": "material_balance_from_reported_phase_splits",
                "correction_status": "inferred_not_source_confirmed",
                "candidate_vapor_fraction": vapor_fraction,
                "candidate_liquid_fraction": 1.0 - vapor_fraction,
                "max_abs_material_balance_residual": _material_balance_residual(
                    candidate_feed,
                    vapor,
                    liquid,
                    vapor_fraction,
                ),
            }
        )
    return rows


def _phase_discovery_status_from_payload(payload: dict[str, Any] | None) -> dict[str, str]:
    if payload is None:
        return {key: "required_not_verified" for key in PHASE_DISCOVERY_REQUIREMENTS}
    raw_statuses = payload.get("requirement_status", {})
    if not isinstance(raw_statuses, dict):
        raw_statuses = {}
    return {
        key: str(raw_statuses.get(key, "required_not_verified"))
        for key in PHASE_DISCOVERY_REQUIREMENTS
    }


def _phase_discovery_complete(payload: dict[str, Any] | None) -> bool:
    if payload is None:
        return False
    statuses = _phase_discovery_status_from_payload(payload)
    return bool(payload.get("complete", False)) and all(
        value.startswith("verified") for value in statuses.values()
    )


def _phase_discovery_incomplete_requirements(payload: dict[str, Any] | None) -> list[str]:
    statuses = _phase_discovery_status_from_payload(payload)
    return [
        key
        for key in PHASE_DISCOVERY_REQUIREMENTS
        if not statuses[key].startswith("verified")
    ]


def evaluate_case_dir(case_dir: Path, phase_discovery_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = _read_json(case_dir / "metadata.json")
    phase_rows = _read_csv(case_dir / "phase_splits.csv")
    computed_rows = _computed_material_balance_rows(metadata, case_dir)
    fixture_field_status = _fixture_field_status(metadata, case_dir, phase_rows, computed_rows)
    unmet_fixture_fields = [
        field
        for field in EXECUTABLE_FIXTURE_REQUIRED_FIELDS
        if fixture_field_status[field] != "present"
    ]
    stored_material_balance = _read_csv(case_dir / "material_balance_check.csv")
    mismatches = _compare_stored_material_balance(computed_rows, stored_material_balance)
    blockers = list(dict.fromkeys(reason for row in computed_rows for reason in row["blockers"]))
    fixture_requirements = metadata.get("fixture_requirements", {})
    phase_discovery_required = bool(fixture_requirements.get("phase_discovery_required", False))
    phase_discovery_status = _phase_discovery_status_from_payload(phase_discovery_payload)
    phase_discovery_incomplete = _phase_discovery_incomplete_requirements(phase_discovery_payload)
    phase_discovery_verified = (
        _phase_discovery_complete(phase_discovery_payload)
        if phase_discovery_payload is not None
        else bool(fixture_requirements.get("phase_discovery_verified", False))
    )
    if phase_discovery_required and not phase_discovery_verified:
        blockers.append("phase_discovery_not_verified")
    if bool(fixture_requirements.get("source_confirmed_feed_correction_required", False)):
        blockers.append("source_confirmed_feed_correction_required")
    if unmet_fixture_fields:
        blockers.append("executable_fixture_contract_incomplete")
    if mismatches:
        blockers.append("stored_material_balance_check_mismatch")
    executable = (
        str(metadata.get("source_model_family", "")) in ACCEPTED_NEUTRAL_FLASH_MODEL_FAMILIES
        and all(bool(row["fixture_eligible"]) for row in computed_rows)
        and not unmet_fixture_fields
        and not mismatches
        and (not phase_discovery_required or phase_discovery_verified)
        and not bool(fixture_requirements.get("source_confirmed_feed_correction_required", False))
    )
    return {
        "name": metadata.get("name", ""),
        "case_label": metadata.get("case_label", ""),
        "family_label": metadata.get("family_label", ""),
        "source_model_family": metadata.get("source_model_family", ""),
        "fixture_status": "executable" if executable else "blocked",
        "executable": executable,
        "phase_discovery_required": phase_discovery_required,
        "phase_discovery_verified": phase_discovery_verified,
        "phase_discovery_status": phase_discovery_status,
        "phase_discovery_incomplete_requirements": phase_discovery_incomplete,
        "executable_fixture_required_fields": list(EXECUTABLE_FIXTURE_REQUIRED_FIELDS),
        "executable_fixture_field_status": fixture_field_status,
        "unmet_executable_fixture_fields": unmet_fixture_fields,
        "blockers": list(dict.fromkeys(blockers)),
        "cases": computed_rows,
        "feed_correction_candidates": _computed_feed_correction_rows(case_dir),
        "stored_material_balance_consistent": not mismatches,
        "stored_material_balance_mismatches": mismatches,
    }


def _print_human(payload: dict[str, Any]) -> None:
    print(f"{payload['case_label']}: {payload['fixture_status']}")
    print(f"  executable: {str(payload['executable']).lower()}")
    print(f"  source model: {payload['source_model_family']}")
    if payload["blockers"]:
        print("  blockers: " + ", ".join(str(item) for item in payload["blockers"]))
    if payload["unmet_executable_fixture_fields"]:
        print(
            "  unmet fixture fields: "
            + ", ".join(str(item) for item in payload["unmet_executable_fixture_fields"])
        )
    for case in payload["cases"]:
        print(
            "  "
            + str(case["case_key"])
            + f": {case['material_balance_status']}, fixture_eligible={str(case['fixture_eligible']).lower()}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check whether an equilibrium benchmark fixture can run.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument(
        "--phase-discovery-json",
        dest="phase_discovery_json",
        type=Path,
        default=None,
        help="Machine-readable phase-discovery payload from check_phase_discovery.py.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--require-executable",
        action="store_true",
        help="Return a failing exit code when the fixture is not executable.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    phase_discovery_payload = _read_optional_phase_discovery_payload(args.phase_discovery_json)
    payload = evaluate_case_dir(args.case_dir, phase_discovery_payload=phase_discovery_payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(payload)
    if not payload["stored_material_balance_consistent"]:
        return 1
    if args.require_executable and not payload["executable"]:
        print(
            f"{payload['case_label']} is not an executable equilibrium fixture.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
