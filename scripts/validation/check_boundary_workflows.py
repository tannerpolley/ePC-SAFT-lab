from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.core.native_results import native_route_solved_pressure, native_route_solved_temperature
from scripts.validation import equilibrium_validation_runtime as runtime

_core = extension_native_core()

DEFAULT_CASE_DIR = runtime.DEFAULT_NEUTRAL_TP_FLASH_CASE_DIR
DEFAULT_CLOUD_SHADOW_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "matsuda_2011_pfhexane_hexane"
)
EXPECTED_CLOUD_SHADOW_SPECIES = ["perfluorohexane", "hexane"]
EXPECTED_CLOUD_SHADOW_BINODAL_ROWS = 14
EXPECTED_CLOUD_SHADOW_PRESSURE_KPA = 101.3
EXPECTED_CLOUD_SHADOW_PRESSURE_PA = 101300.0
ROUTE_ADMISSION_BLOCKERS = [
    "native_cloud_point_route_absent",
    "native_shadow_point_route_absent",
]
REQUIRED_CLOUD_SHADOW_FILES = (
    "metadata.json",
    "thresholds.json",
    "source_binodal_points.csv",
    "experimental_tielines.csv",
)

BOUNDARY_ROUTES: dict[str, dict[str, Any]] = {
    "bubble_pressure": {
        "workflow_label": "Bubble point",
        "selector_family": "bubble_dew_derived_routes",
        "problem_name": "neutral_bubble_p_eos",
        "diagram_target": "P-x",
        "source_phase": "liquid",
        "composition_role": "liquid",
        "boundary_variable": "P",
        "fixed_variables": ("T", "x"),
        "free_variables": ("P", "y", "phase_volumes"),
    },
    "bubble_temperature": {
        "workflow_label": "Bubble point",
        "selector_family": "bubble_dew_derived_routes",
        "problem_name": "neutral_bubble_t_eos",
        "diagram_target": "T-x",
        "source_phase": "liquid",
        "composition_role": "liquid",
        "boundary_variable": "T",
        "fixed_variables": ("P", "x"),
        "free_variables": ("T", "y", "phase_volumes"),
    },
    "dew_pressure": {
        "workflow_label": "Dew point",
        "selector_family": "bubble_dew_derived_routes",
        "problem_name": "neutral_dew_p_eos",
        "diagram_target": "P-x",
        "source_phase": "vapor",
        "composition_role": "vapor",
        "boundary_variable": "P",
        "fixed_variables": ("T", "y"),
        "free_variables": ("P", "x", "phase_volumes"),
    },
    "dew_temperature": {
        "workflow_label": "Dew point",
        "selector_family": "bubble_dew_derived_routes",
        "problem_name": "neutral_dew_t_eos",
        "diagram_target": "T-x",
        "source_phase": "vapor",
        "composition_role": "vapor",
        "boundary_variable": "T",
        "fixed_variables": ("P", "y"),
        "free_variables": ("T", "x", "phase_volumes"),
    },
}

BOUNDARY_TRACE_SCHEMA_VERSION = 1
REQUIRED_BOUNDARY_TRACE_FIELDS = {
    "schema_version",
    "route",
    "workflow_label",
    "workflow_kind",
    "diagram_target",
    "known_variables",
    "free_variables",
    "solved_boundary_variable",
    "fixed_composition_role",
    "phase_roles",
    "source_fixture",
    "selector_family",
    "problem_name",
    "variable_model",
    "density_backend",
    "residual_families",
    "constraint_families",
    "strict_convergence",
    "solver_status",
    "application_status",
    "seed_attempts",
    "iteration_limit_seed_attempts",
    "residuals",
}
REQUIRED_BOUNDARY_RESIDUALS = (
    "material_balance_norm",
    "pressure_consistency_norm",
    "ln_fugacity_consistency_norm",
    "scaled_constraint_violation_inf_norm",
)
REQUIRED_BOUNDARY_RESIDUAL_FAMILY_GROUPS = {
    "material_closure": {"material_balance", "phase_amount_total"},
    "pressure_consistency": {"phase_pressure_consistency"},
    "phase_equilibrium": {"phase_equilibrium"},
    "phase_distance": {"phase_distance"},
}
REQUIRED_BOUNDARY_CONSTRAINT_FAMILY_GROUPS = {
    "material_closure": {"material_balance", "phase_amount_total"},
    "pressure_consistency": {"phase_pressure_consistency"},
}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _finite_float(value: Any) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(numeric)


def _positive_finite_float(value: Any) -> bool:
    return _finite_float(value) and float(value) > 0.0


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _repo_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _range(values: list[float]) -> list[float]:
    if not values:
        return []
    return [min(values), max(values)]


def _composition_valid(values: list[float]) -> bool:
    return all(0.0 <= value <= 1.0 for value in values) and math.isclose(
        sum(values), 1.0, rel_tol=0.0, abs_tol=1.0e-10
    )


def _cloud_shadow_metadata_blockers(metadata: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if metadata.get("source_status") != "source_backed":
        blockers.append("cloud_shadow_source_status_not_source_backed")
    if metadata.get("species") != EXPECTED_CLOUD_SHADOW_SPECIES:
        blockers.append("cloud_shadow_metadata_species_order_mismatch")
    if metadata.get("route") != "lle":
        blockers.append("cloud_shadow_metadata_route_mismatch")
    if metadata.get("selector_route") != "neutral_lle":
        blockers.append("cloud_shadow_metadata_selector_route_mismatch")
    if metadata.get("expected_phase_count") != 2:
        blockers.append("cloud_shadow_expected_phase_count_mismatch")
    for field in ("association_active", "electrolyte_active", "reaction_active"):
        if metadata.get(field) is not False:
            blockers.append(f"cloud_shadow_forbidden_physics_active:{field}")
    return blockers


def _cloud_shadow_binodal_payload(
    rows: list[dict[str, str]],
) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    temperatures: list[float] = []
    pressures: list[float] = []
    compositions: list[float] = []
    method_set: set[str] = set()
    source_datasets: set[str] = set()

    if len(rows) != EXPECTED_CLOUD_SHADOW_BINODAL_ROWS:
        blockers.append("cloud_shadow_source_binodal_rows_count_mismatch")

    for row in rows:
        if row.get("component_1") != EXPECTED_CLOUD_SHADOW_SPECIES[0] or row.get(
            "component_2"
        ) != EXPECTED_CLOUD_SHADOW_SPECIES[1]:
            blockers.append("cloud_shadow_binodal_species_order_mismatch")
        method = str(row.get("method", "")).strip()
        method_set.add(method)
        if method != "cloud_point":
            blockers.append("cloud_shadow_binodal_method_rejected")
        source_dataset = str(row.get("source_dataset", "")).strip()
        if source_dataset:
            source_datasets.add(source_dataset)
        if not _positive_finite_float(row.get("temperature_K")):
            blockers.append("cloud_shadow_binodal_temperature_invalid")
        else:
            temperatures.append(float(row["temperature_K"]))
        if not _positive_finite_float(row.get("pressure_kPa")):
            blockers.append("cloud_shadow_binodal_pressure_invalid")
        else:
            pressure = float(row["pressure_kPa"])
            pressures.append(pressure)
            if not math.isclose(pressure, EXPECTED_CLOUD_SHADOW_PRESSURE_KPA, rel_tol=0.0, abs_tol=1.0e-9):
                blockers.append("cloud_shadow_binodal_pressure_mismatch")
        if not _finite_float(row.get("x_perfluorohexane")):
            blockers.append("cloud_shadow_binodal_composition_invalid")
        else:
            composition = float(row["x_perfluorohexane"])
            compositions.append(composition)
            if composition < 0.0 or composition > 1.0:
                blockers.append("cloud_shadow_binodal_composition_invalid")

    pressure_kpa = pressures[0] if pressures and all(math.isclose(value, pressures[0]) for value in pressures) else None
    return (
        {
            "binodal_point_count": len(rows),
            "pressure_kPa": pressure_kpa,
            "temperature_range_K": _range(temperatures),
            "composition_range_x1": _range(compositions),
            "method_set": sorted(method_set),
            "source_datasets": sorted(source_datasets),
        },
        blockers,
    )


def _cloud_shadow_pair_payload(
    rows: list[dict[str, str]],
    thresholds: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    if len(rows) != 1:
        return (
            {
                "paired_cloud_shadow_count": len(rows),
                "paired_branch_compositions": [],
                "paired_pressure_Pa": None,
                "branch_temperature_gap_K": None,
                "branch_temperature_gap_threshold_K": thresholds.get("source_temperature_pair_abs_K"),
                "source_row_pair": None,
                "phase_distance_x1": None,
            },
            ["cloud_shadow_paired_branch_rows_missing"],
        )

    row = rows[0]
    if row.get("component_1") != EXPECTED_CLOUD_SHADOW_SPECIES[0] or row.get(
        "component_2"
    ) != EXPECTED_CLOUD_SHADOW_SPECIES[1]:
        blockers.append("cloud_shadow_pair_species_order_mismatch")
    if row.get("source_status") != "source_backed":
        blockers.append("cloud_shadow_pair_source_status_rejected")
    if row.get("source_basis") != "paired_binodal_branch_rows":
        blockers.append("cloud_shadow_pair_source_basis_rejected")

    numeric_fields = (
        "temperature_K",
        "pressure_kPa",
        "pressure_Pa",
        "liquid1_x1",
        "liquid1_x2",
        "liquid2_x1",
        "liquid2_x2",
        "temperature_difference_K",
    )
    for field in numeric_fields:
        if not _finite_float(row.get(field)):
            blockers.append(f"cloud_shadow_pair_field_invalid:{field}")

    liquid1: list[float] = []
    liquid2: list[float] = []
    if all(_finite_float(row.get(field)) for field in ("liquid1_x1", "liquid1_x2", "liquid2_x1", "liquid2_x2")):
        liquid1 = [float(row["liquid1_x1"]), float(row["liquid1_x2"])]
        liquid2 = [float(row["liquid2_x1"]), float(row["liquid2_x2"])]
        if not _composition_valid(liquid1) or not _composition_valid(liquid2):
            blockers.append("cloud_shadow_pair_composition_invalid")

    pressure_pa = float(row["pressure_Pa"]) if _finite_float(row.get("pressure_Pa")) else None
    if pressure_pa is not None and not math.isclose(
        pressure_pa, EXPECTED_CLOUD_SHADOW_PRESSURE_PA, rel_tol=0.0, abs_tol=1.0e-6
    ):
        blockers.append("cloud_shadow_pair_pressure_mismatch")

    threshold = thresholds.get("source_temperature_pair_abs_K")
    if not _positive_finite_float(threshold):
        blockers.append("cloud_shadow_source_temperature_threshold_invalid")
        threshold_value = None
    else:
        threshold_value = float(threshold)
    gap = float(row["temperature_difference_K"]) if _finite_float(row.get("temperature_difference_K")) else None
    if gap is not None and threshold_value is not None and abs(gap) > threshold_value:
        blockers.append("cloud_shadow_pair_temperature_gap_exceeds_threshold")

    phase_distance_min = thresholds.get("phase_distance_min")
    phase_distance = abs(liquid2[0] - liquid1[0]) if liquid1 and liquid2 else None
    if phase_distance is not None and _positive_finite_float(phase_distance_min):
        if phase_distance <= float(phase_distance_min):
            blockers.append("cloud_shadow_pair_phase_distance_below_threshold")

    return (
        {
            "paired_cloud_shadow_count": 1,
            "paired_branch_compositions": [liquid1, liquid2] if liquid1 and liquid2 else [],
            "paired_pressure_Pa": pressure_pa,
            "branch_temperature_gap_K": gap,
            "branch_temperature_gap_threshold_K": threshold_value,
            "source_row_pair": row.get("source_row_pair"),
            "phase_distance_x1": phase_distance,
        },
        blockers,
    )


def evaluate_cloud_shadow_gate(
    case_dir: Path = DEFAULT_CLOUD_SHADOW_CASE_DIR,
    *,
    workflows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    source_data_blockers = [
        f"missing_required_file:{name}" for name in REQUIRED_CLOUD_SHADOW_FILES if not (case_dir / name).exists()
    ]
    metadata: dict[str, Any] = {}
    thresholds: dict[str, Any] = {}
    binodal_payload: dict[str, Any] = {
        "binodal_point_count": 0,
        "pressure_kPa": None,
        "temperature_range_K": [],
        "composition_range_x1": [],
        "method_set": [],
        "source_datasets": [],
    }
    pair_payload: dict[str, Any] = {
        "paired_cloud_shadow_count": 0,
        "paired_branch_compositions": [],
        "paired_pressure_Pa": None,
        "branch_temperature_gap_K": None,
        "branch_temperature_gap_threshold_K": None,
        "source_row_pair": None,
        "phase_distance_x1": None,
    }

    if (case_dir / "metadata.json").exists():
        metadata = _read_json(case_dir / "metadata.json")
        source_data_blockers.extend(_cloud_shadow_metadata_blockers(metadata))
    if (case_dir / "thresholds.json").exists():
        thresholds = _read_json(case_dir / "thresholds.json")
    if (case_dir / "source_binodal_points.csv").exists():
        binodal_payload, blockers = _cloud_shadow_binodal_payload(_read_csv(case_dir / "source_binodal_points.csv"))
        source_data_blockers.extend(blockers)
    if (case_dir / "experimental_tielines.csv").exists():
        pair_payload, blockers = _cloud_shadow_pair_payload(_read_csv(case_dir / "experimental_tielines.csv"), thresholds)
        source_data_blockers.extend(blockers)

    for workflow in workflows if workflows is not None else _workflow_contracts():
        if workflow.get("label") in {"Cloud point", "Shadow point"} and workflow.get("routes"):
            source_data_blockers.append(f"cloud_shadow_unproven_runtime_route_claim:{workflow['label']}")

    source_data_blockers = sorted(set(source_data_blockers))
    payload = {
        "complete": not source_data_blockers,
        "status": "source_data_gate_complete" if not source_data_blockers else "source_data_gate_blocked",
        "source_fixture": _repo_relative_path(case_dir),
        "species": metadata.get("species", EXPECTED_CLOUD_SHADOW_SPECIES),
        "source_data_blockers": source_data_blockers,
        "route_admission_blockers": ROUTE_ADMISSION_BLOCKERS,
        **binodal_payload,
        **pair_payload,
    }
    return payload


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value]


def _workflow_contracts(route_points_by_label: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    route_points_by_label = route_points_by_label or {}
    workflows = [
        {
            "label": "Bubble point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "executable_current_routes",
            "routes": ["bubble_pressure", "bubble_temperature"],
            "fixed_variables": ["temperature_or_pressure", "liquid_or_feed_composition"],
            "free_variables": ["incipient_vapor_composition", "phase_volumes", "boundary_pressure_or_temperature"],
            "diagram_targets": ["P-x", "T-x"],
        },
        {
            "label": "Dew point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "executable_current_routes",
            "routes": ["dew_pressure", "dew_temperature"],
            "fixed_variables": ["temperature_or_pressure", "vapor_composition"],
            "free_variables": ["incipient_liquid_composition", "phase_volumes", "boundary_pressure_or_temperature"],
            "diagram_targets": ["P-x", "T-x"],
        },
        {
            "label": "Cloud point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "planned_not_executable",
            "routes": [],
            "fixed_variables": ["temperature_or_pressure", "parent_liquid_composition"],
            "free_variables": [
                "incipient_second_liquid_composition",
                "phase_volumes",
                "boundary_pressure_or_temperature",
            ],
            "diagram_targets": ["P-x", "T-x"],
        },
        {
            "label": "Shadow point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "planned_not_executable",
            "routes": [],
            "fixed_variables": ["cloud_state"],
            "free_variables": ["incipient_phase_composition", "incipient_phase_volume"],
            "diagram_targets": ["P-x", "T-x"],
        },
    ]
    for workflow in workflows:
        route_points = list(route_points_by_label.get(workflow["label"], []))
        workflow["route_points"] = route_points
        if workflow["runtime_status"] == "planned_not_executable":
            workflow["route_point_status"] = "planned_not_executable"
        elif not route_points:
            workflow["route_point_status"] = "not_requested"
        elif all(point["status"] == "accepted" for point in route_points):
            workflow["route_point_status"] = "complete"
        else:
            workflow["route_point_status"] = "blocked"
    return workflows


def _native_ipopt_compiled() -> bool:
    try:
        with runtime.suppress_native_stdout():
            return bool(_core._native_ipopt_smoke()["compiled"])
    except Exception:
        return False


def _composition_samples(base: list[float], count: int) -> list[list[float]]:
    if count < 1:
        raise ValueError("--route-point-count must be greater than zero")
    if count == 1:
        return [base]
    if len(base) < 2:
        return [base for _ in range(count)]
    span = min(0.02, 0.25 * base[0], 0.25 * base[-1])
    offsets = [-span + 2.0 * span * index / (count - 1) for index in range(count)]
    samples: list[list[float]] = []
    for offset in offsets:
        sample = list(base)
        sample[0] += offset
        sample[-1] -= offset
        total = sum(sample)
        if total <= 0.0 or any(value <= 0.0 for value in sample):
            raise ValueError("Generated boundary route-point composition left the positive simplex")
        samples.append([value / total for value in sample])
    return samples


def _route_request(
    route: str,
    spec: dict[str, Any],
    row: dict[str, str],
    composition: list[float],
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "route": route,
        "composition": composition,
        "composition_role": spec["composition_role"],
    }
    if spec["boundary_variable"] == "P":
        request["temperature"] = float(row["temperature_K"])
    else:
        request["pressure"] = float(row["pressure_MPa"]) * 1.0e6
    return request


def _run_native_route(
    mix: Any,
    request: dict[str, Any],
    *,
    debug: bool,
    max_iterations: int,
) -> dict[str, Any]:
    def run() -> dict[str, Any]:
        return dict(
            _core._native_equilibrium_selector_route_result(
                mix._native,
                request,
                max_iterations,
                1.0e-8,
                0.0,
                "auto",
                50 if debug else 8,
                1.0e-8,
                1.0e-3,
                1.0e-8,
                1.0e-8,
                {},
                linear_solver="auto",
                option_profile="continuation_trace",
                print_level=5 if debug else 0,
                acceptable_tolerance=1.0e-7,
                constraint_violation_tolerance=1.0e-7,
                dual_infeasibility_tolerance=1.0e-8,
                complementarity_tolerance=1.0e-8,
            )
        )

    if debug:
        with runtime.redirect_native_stdout_to_stderr():
            return run()
    with runtime.suppress_native_stdout():
        return run()


def _strict_convergence(route_payload: dict[str, Any], iteration_limit_seed_attempts: list[str]) -> bool:
    return (
        route_payload.get("solver_status") == "success"
        and route_payload.get("application_status") == "solve_succeeded"
        and not iteration_limit_seed_attempts
    )


def _residuals(route_payload: dict[str, Any]) -> dict[str, float | None]:
    postsolve = route_payload.get("postsolve")
    postsolve = postsolve if isinstance(postsolve, dict) else {}
    keys = (
        "material_balance_norm",
        "pressure_consistency_norm",
        "ln_fugacity_consistency_norm",
        "phase_equilibrium_norm",
        "scaled_constraint_violation_inf_norm",
    )
    residuals: dict[str, float | None] = {}
    for key in keys:
        value = postsolve.get(key, route_payload.get(key))
        residuals[key] = float(value) if isinstance(value, (int, float)) and math.isfinite(float(value)) else None
    return residuals


def _seed_attempt_summary(route_payload: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = []
    for attempt in route_payload.get("seed_attempts") or ():
        attempt = dict(attempt)
        attempts.append(
            {
                "seed_name": attempt.get("seed_name"),
                "status": attempt.get("status"),
                "solver_status": attempt.get("solver_status"),
                "application_status": attempt.get("application_status"),
                "accepted": attempt.get("accepted"),
                "iteration_count": attempt.get("iteration_count"),
                "max_iterations": attempt.get("max_iterations"),
            }
        )
    return attempts


def _iteration_limit_seed_attempts(route_payload: dict[str, Any]) -> list[str]:
    blocked = []
    for attempt in route_payload.get("seed_attempts") or ():
        attempt = dict(attempt)
        if (
            attempt.get("solver_status") == "max_iterations_exceeded"
            or attempt.get("application_status") == "maximum_iterations_exceeded"
        ):
            blocked.append(str(attempt.get("seed_name", "unnamed_seed_attempt")))
    return blocked


def _solved_boundary_value(route: str, spec: dict[str, Any], route_payload: dict[str, Any]) -> float:
    if spec["boundary_variable"] == "P":
        return native_route_solved_pressure(route_payload, route)
    return native_route_solved_temperature(route_payload, route)


def _boundary_trace(
    route: str,
    spec: dict[str, Any],
    source_fixture: str,
    composition: list[float],
    route_payload: dict[str, Any],
    seed_attempts: list[dict[str, Any]],
    iteration_limit_attempts: list[str],
    strict: bool,
    residuals: dict[str, float | None],
) -> dict[str, Any]:
    physical_evidence = route_payload.get("physical_evidence")
    physical_evidence = physical_evidence if isinstance(physical_evidence, dict) else {}
    return {
        "schema_version": BOUNDARY_TRACE_SCHEMA_VERSION,
        "route": route,
        "workflow_label": spec["workflow_label"],
        "workflow_kind": "derived_boundary",
        "diagram_target": spec["diagram_target"],
        "known_variables": list(spec["fixed_variables"]),
        "free_variables": list(spec["free_variables"]),
        "solved_boundary_variable": spec["boundary_variable"],
        "fixed_composition_role": spec["composition_role"],
        "fixed_composition": composition,
        "phase_labels": route_payload.get("phase_labels", physical_evidence.get("phase_labels", [])),
        "phase_roles": route_payload.get("phase_roles", physical_evidence.get("phase_roles", [])),
        "phase_amounts": route_payload.get("phase_amounts", []),
        "phase_volumes": route_payload.get("phase_volumes", []),
        "source_fixture": source_fixture,
        "selector_family": route_payload.get("selector_family", spec["selector_family"]),
        "problem_name": route_payload.get("problem_name", spec["problem_name"]),
        "variable_model": route_payload.get("variable_model"),
        "density_backend": route_payload.get("density_backend"),
        "residual_families": route_payload.get("residual_families", []),
        "constraint_families": route_payload.get("constraint_families", []),
        "shared_nlp_contract": "neutral_amount_volume_phase_nlp",
        "derivation": "degree_of_freedom_swap",
        "strict_convergence": strict,
        "solver_status": route_payload.get("solver_status"),
        "application_status": route_payload.get("application_status"),
        "seed_attempts": seed_attempts,
        "iteration_limit_seed_attempts": iteration_limit_attempts,
        "residuals": residuals,
    }


def _route_point_result(
    route: str,
    sample_index: int,
    composition: list[float],
    route_payload: dict[str, Any],
    source_fixture: str,
) -> dict[str, Any]:
    spec = BOUNDARY_ROUTES[route]
    seed_attempts = _seed_attempt_summary(route_payload)
    iteration_limit_attempts = _iteration_limit_seed_attempts(route_payload)
    strict = _strict_convergence(route_payload, iteration_limit_attempts)
    residuals = _residuals(route_payload)
    selected_seed = route_payload.get("seed_name") or next(
        (attempt["seed_name"] for attempt in seed_attempts if attempt.get("accepted")),
        None,
    )
    return {
        "route": route,
        "diagram_target": spec["diagram_target"],
        "sample_index": sample_index,
        "status": "accepted" if strict else "blocked_nonconverged",
        "fixed_composition_role": spec["composition_role"],
        "fixed_composition": composition,
        "boundary_variable": spec["boundary_variable"],
        "solved_boundary_value": _solved_boundary_value(route, spec, route_payload),
        "route_status": route_payload.get("status"),
        "solver_status": route_payload.get("solver_status"),
        "application_status": route_payload.get("application_status"),
        "strict_convergence": strict,
        "iteration_limit_seed_attempts": iteration_limit_attempts,
        "seed_source": selected_seed,
        "seed_attempts": seed_attempts,
        "max_iterations": route_payload.get("max_iterations"),
        "iteration_count": route_payload.get("iteration_count"),
        "iteration_history_limit": route_payload.get("iteration_history_limit"),
        "iteration_history_size": route_payload.get("iteration_history_size"),
        "iteration_history": route_payload.get("iteration_history", []),
        "ipopt_print_level": route_payload.get("ipopt_print_level"),
        "option_profile": route_payload.get("option_profile"),
        "residuals": residuals,
        "boundary_trace": _boundary_trace(
            route,
            spec,
            source_fixture,
            composition,
            route_payload,
            seed_attempts,
            iteration_limit_attempts,
            strict,
            residuals,
        ),
    }


def _selected_routes(route: str | None) -> list[str]:
    if route is None:
        return list(BOUNDARY_ROUTES)
    return [route]


def _run_route_points(args: argparse.Namespace) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    metadata = json.loads(args.case_dir.joinpath("metadata.json").read_text(encoding="utf-8"))
    rows = runtime.case_rows(args.case_dir)
    species = runtime.species(rows, metadata)
    mix = runtime.mixture(args.case_dir, species)
    blockers: list[str] = []
    route_points_by_label: dict[str, list[dict[str, Any]]] = {}
    source_fixture = _source_fixture(args.case_dir)
    for route in _selected_routes(args.route):
        spec = BOUNDARY_ROUTES[route]
        row = rows[str(spec["source_phase"])]
        samples = _composition_samples(runtime.composition(row), int(args.route_point_count))
        for sample_index, composition in enumerate(samples):
            request = _route_request(route, spec, row, composition)
            payload = _run_native_route(
                mix,
                request,
                debug=bool(args.debug),
                max_iterations=int(args.max_iterations),
            )
            point = _route_point_result(route, sample_index, composition, payload, source_fixture)
            route_points_by_label.setdefault(str(spec["workflow_label"]), []).append(point)
            if point["status"] != "accepted":
                blockers.append(f"{route}_strict_convergence_missing")
    return route_points_by_label, list(dict.fromkeys(blockers))


def _route_point_summary(workflows: list[dict[str, Any]]) -> dict[str, int]:
    points = [point for workflow in workflows for point in workflow["route_points"]]
    accepted = [point for point in points if point["status"] == "accepted"]
    return {
        "requested_route_point_count": len(points),
        "accepted_route_point_count": len(accepted),
        "failed_route_point_count": len(points) - len(accepted),
    }


def _source_fixture(case_dir: Path) -> str:
    try:
        return str(case_dir.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(case_dir.resolve())


def _trace_points(payload: dict[str, Any]) -> list[dict[str, Any]]:
    points = []
    workflows = payload.get("workflows")
    if not isinstance(workflows, list):
        return points
    for workflow in workflows:
        if not isinstance(workflow, dict):
            continue
        route_points = workflow.get("route_points")
        if not isinstance(route_points, list):
            continue
        for point in route_points:
            if isinstance(point, dict):
                points.append(point)
    return points


def _validate_boundary_trace(point: dict[str, Any]) -> list[str]:
    route = str(point.get("route", ""))
    sample_index = point.get("sample_index", 0)
    route_label = route if route else "unknown_route"
    if route not in BOUNDARY_ROUTES:
        return [f"unknown_boundary_route:{route_label}:{sample_index}"]
    spec = BOUNDARY_ROUTES[route]
    trace = point.get("boundary_trace")
    if not isinstance(trace, dict):
        return [f"missing_boundary_trace:{route}:{sample_index}"]

    blockers: list[str] = []
    for field in sorted(REQUIRED_BOUNDARY_TRACE_FIELDS):
        if field not in trace:
            blockers.append(f"malformed_boundary_trace:{route}:{field}")

    if trace.get("schema_version") != BOUNDARY_TRACE_SCHEMA_VERSION:
        blockers.append(f"boundary_trace_schema_version_mismatch:{route}")
    if trace.get("route") != route:
        blockers.append(f"boundary_trace_route_mismatch:{route}")
    if trace.get("workflow_label") != spec["workflow_label"]:
        blockers.append(f"boundary_trace_workflow_label_mismatch:{route}")
    if trace.get("workflow_kind") != "derived_boundary":
        blockers.append(f"boundary_trace_workflow_kind_mismatch:{route}")
    if trace.get("diagram_target") != spec["diagram_target"]:
        blockers.append(f"boundary_trace_diagram_target_mismatch:{route}")
    if _string_list(trace.get("known_variables")) != list(spec["fixed_variables"]):
        blockers.append(f"boundary_trace_known_variables_mismatch:{route}")
    if _string_list(trace.get("free_variables")) != list(spec["free_variables"]):
        blockers.append(f"boundary_trace_free_variables_mismatch:{route}")
    if trace.get("solved_boundary_variable") != spec["boundary_variable"]:
        blockers.append(f"boundary_trace_solved_variable_mismatch:{route}")
    if trace.get("fixed_composition_role") != spec["composition_role"]:
        blockers.append(f"boundary_trace_composition_role_mismatch:{route}")
    if trace.get("selector_family") != spec["selector_family"]:
        blockers.append(f"boundary_trace_selector_family_mismatch:{route}")
    if trace.get("problem_name") != spec["problem_name"]:
        blockers.append(f"boundary_trace_problem_name_mismatch:{route}")

    if not _string_list(trace.get("phase_roles")):
        blockers.append(f"boundary_trace_missing_phase_roles:{route}")

    residual_families = set(_string_list(trace.get("residual_families")))
    for group_name, aliases in REQUIRED_BOUNDARY_RESIDUAL_FAMILY_GROUPS.items():
        if not residual_families.intersection(aliases):
            blockers.append(f"boundary_trace_missing_residual_family:{route}:{group_name}")

    constraint_families = set(_string_list(trace.get("constraint_families")))
    for group_name, aliases in REQUIRED_BOUNDARY_CONSTRAINT_FAMILY_GROUPS.items():
        if not constraint_families.intersection(aliases):
            blockers.append(f"boundary_trace_missing_constraint_family:{route}:{group_name}")

    if trace.get("strict_convergence") is not True or point.get("strict_convergence") is not True:
        blockers.append(f"boundary_trace_strict_convergence_missing:{route}")
    if trace.get("solver_status") != "success" or point.get("solver_status") != "success":
        blockers.append(f"boundary_trace_solver_status_not_success:{route}")
    if trace.get("application_status") != "solve_succeeded" or point.get("application_status") != "solve_succeeded":
        blockers.append(f"boundary_trace_application_status_not_succeeded:{route}")
    if trace.get("iteration_limit_seed_attempts") or point.get("iteration_limit_seed_attempts"):
        blockers.append(f"boundary_trace_iteration_limit_seed_attempt:{route}")

    solved_boundary_value = point.get("solved_boundary_value")
    if not _finite_number(solved_boundary_value) or float(solved_boundary_value) <= 0.0:
        blockers.append(f"boundary_trace_nonfinite_solved_boundary_value:{route}")

    residuals = trace.get("residuals")
    residuals = residuals if isinstance(residuals, dict) else {}
    for residual in REQUIRED_BOUNDARY_RESIDUALS:
        if not _finite_number(residuals.get(residual)):
            blockers.append(f"boundary_trace_missing_residual:{route}:{residual}")

    return blockers


def evaluate_boundary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    points = _trace_points(payload)
    blockers: list[str] = []
    accepted = 0
    for point in points:
        point_blockers = _validate_boundary_trace(point)
        blockers.extend(point_blockers)
        if not point_blockers and point.get("status") == "accepted":
            accepted += 1
    blockers = sorted(set(blockers))
    return {
        "complete": bool(points) and not blockers,
        "blockers": blockers,
        "trace_summary": {
            "total": len(points),
            "accepted": accepted,
            "failed": len(points) - accepted,
        },
    }


def _base_payload(args: argparse.Namespace, workflows: list[dict[str, Any]], blockers: list[str]) -> dict[str, Any]:
    summary = _route_point_summary(workflows)
    trace_result = evaluate_boundary_payload({"workflows": workflows})
    cloud_shadow_gate = (
        evaluate_cloud_shadow_gate(args.cloud_shadow_case_dir, workflows=workflows)
        if getattr(args, "cloud_shadow_gate", False)
        else None
    )
    cloud_shadow_blockers = cloud_shadow_gate["source_data_blockers"] if cloud_shadow_gate else []
    all_blockers = list(dict.fromkeys([*blockers, *trace_result["blockers"], *cloud_shadow_blockers]))
    route_complete = (
        summary["requested_route_point_count"] > 0
        and summary["failed_route_point_count"] == 0
        and not blockers
        and not trace_result["blockers"]
    )
    if cloud_shadow_gate and not args.run_current_boundary_route:
        complete = bool(cloud_shadow_gate["complete"])
    else:
        complete = route_complete and not all_blockers
    if cloud_shadow_gate and not args.run_current_boundary_route:
        status = "cloud_shadow_gate_complete" if complete else "cloud_shadow_gate_blocked"
    elif not args.run_current_boundary_route:
        status = "contracts_available"
    elif complete:
        status = "complete_route_convergence"
    else:
        status = "blocked_route_convergence"
    payload = {
        "boundary_status": status,
        "complete": complete,
        "source_fixture": _source_fixture(args.case_dir),
        "requested_route_point_count": summary["requested_route_point_count"],
        "route_point_summary": summary,
        "boundary_trace_status": (
            "not_requested"
            if summary["requested_route_point_count"] == 0
            else ("complete" if trace_result["complete"] else "blocked")
        ),
        "boundary_trace_summary": trace_result["trace_summary"],
        "blockers": all_blockers,
        "workflows": workflows,
    }
    if cloud_shadow_gate:
        payload["cloud_shadow_gate"] = cloud_shadow_gate
    return payload


def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if getattr(args, "require_cloud_shadow_gate", False):
        args.cloud_shadow_gate = True
    selected_route_count = len(_selected_routes(args.route)) if args.run_current_boundary_route else 0
    requested_route_point_count = selected_route_count * int(args.route_point_count)
    if requested_route_point_count > 1 and not args.allow_route_sweep:
        workflows = _workflow_contracts()
        payload = {
            "boundary_status": "route_sweep_rejected",
            "complete": False,
            "source_fixture": _source_fixture(args.case_dir),
            "requested_route_point_count": requested_route_point_count,
            "route_point_summary": _route_point_summary(workflows),
            "blockers": ["explicit_route_or_allow_route_sweep_required"],
            "workflows": workflows,
        }
        return payload, 2

    if args.contracts_only or not args.run_current_boundary_route:
        payload = _base_payload(args, _workflow_contracts(), [])
        if args.require_cloud_shadow_gate and not payload.get("cloud_shadow_gate", {}).get("complete", False):
            return payload, 2
        return payload, 0

    if not _native_ipopt_compiled():
        payload = _base_payload(args, _workflow_contracts(), ["native_ipopt_not_compiled"])
        return payload, 2 if args.require_complete else 0

    route_points_by_label, blockers = _run_route_points(args)
    workflows = _workflow_contracts(route_points_by_label)
    payload = _base_payload(args, workflows, blockers)
    if args.require_complete and not payload["complete"]:
        return payload, 2
    return payload, 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check derived boundary workflow contracts.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--cloud-shadow-case-dir", type=Path, default=DEFAULT_CLOUD_SHADOW_CASE_DIR)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--contracts-only", action="store_true", help="Check workflow contracts without route solves.")
    parser.add_argument(
        "--cloud-shadow-gate",
        action="store_true",
        help="Check retained cloud/shadow source-data gate without running native cloud/shadow routes.",
    )
    parser.add_argument(
        "--require-cloud-shadow-gate",
        action="store_true",
        help="Return nonzero unless the retained cloud/shadow source-data gate passes.",
    )
    parser.add_argument(
        "--run-current-boundary-route",
        action="store_true",
        help="Run current executable bubble/dew routes. Requires one route unless --allow-route-sweep is set.",
    )
    parser.add_argument("--route", choices=tuple(BOUNDARY_ROUTES), help="Run one current boundary route.")
    parser.add_argument("--route-point-count", type=int, default=1)
    parser.add_argument(
        "--allow-route-sweep",
        action="store_true",
        help="Allow multiple route points. Keep this off for routine validation and debugging.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use Ipopt print_level=5 and redirect native iteration output to stderr when --json is active.",
    )
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return nonzero unless every requested current boundary route point strictly converges.",
    )
    return parser


def _print_text(payload: dict[str, Any]) -> None:
    print(f"Boundary status: {payload['boundary_status']}")
    print(f"source_fixture: {payload['source_fixture']}")
    print(f"requested_route_point_count: {payload['requested_route_point_count']}")
    if payload["blockers"]:
        print("blockers:")
        for blocker in payload["blockers"]:
            print(f"  - {blocker}")
    if "cloud_shadow_gate" in payload:
        gate = payload["cloud_shadow_gate"]
        print(f"cloud_shadow_gate: status={gate['status']} complete={gate['complete']}")
        print(f"  source_fixture: {gate['source_fixture']}")
        print(
            f"  binodal_points={gate['binodal_point_count']} "
            f"paired_cloud_shadow={gate['paired_cloud_shadow_count']}"
        )
        if gate["source_data_blockers"]:
            print("  source_data_blockers:")
            for blocker in gate["source_data_blockers"]:
                print(f"    - {blocker}")
        if gate["route_admission_blockers"]:
            print("  route_admission_blockers:")
            for blocker in gate["route_admission_blockers"]:
                print(f"    - {blocker}")
    for workflow in payload["workflows"]:
        print(
            f"{workflow['label']}: runtime={workflow['runtime_status']} "
            f"route_points={workflow['route_point_status']} points={len(workflow['route_points'])}"
        )
        for point in workflow["route_points"]:
            print(
                "  route_point: "
                f"route={point['route']} "
                f"status={point['status']} "
                f"solver={point['solver_status']} "
                f"application={point['application_status']} "
                f"iterations={point['iteration_count']} "
                f"iteration_limit_seeds={point['iteration_limit_seed_attempts']}"
            )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload, exit_code = evaluate(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_text(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
