from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

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
EXPECTED_CLOUD_SHADOW_ROUTE = "cloud_temperature"
EXPECTED_CLOUD_SHADOW_SELECTOR_FAMILY = "cloud_shadow_derived_routes"
EXPECTED_CLOUD_SHADOW_PROBLEM_NAME = "neutral_cloud_t_eos"
EXPECTED_CLOUD_SHADOW_COMPOSITION_ROLE = "parent_liquid"
EXPECTED_CLOUD_SHADOW_PHASE_LABELS = ["parent_liquid", "shadow_liquid"]
EXPECTED_CLOUD_SHADOW_PHASE_ROLES = ["parent_liquid", "incipient_liquid"]
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


def _cloud_shadow_composition_from_prefix(row: dict[str, str], prefix: str, count: int) -> list[float]:
    values = [float(row[f"{prefix}{index}"]) for index in range(1, count + 1)]
    if not _composition_valid(values):
        raise ValueError(f"{prefix} composition is invalid")
    return values


def _cloud_shadow_case_mixture(case_dir: Path, species: list[str]) -> Any:
    pure_rows = {row["species"]: row for row in _read_csv(case_dir / "pure_component_parameters.csv")}
    if set(pure_rows) != set(species):
        raise ValueError("cloud_shadow_parameter_species_mismatch")
    index = {name: position for position, name in enumerate(species)}
    k_ij = np.zeros((len(species), len(species)), dtype=float)
    for row in _read_csv(case_dir / "binary_interactions.csv"):
        i = index[row["component_i"]]
        j = index[row["component_j"]]
        value = float(row["k_ij"])
        k_ij[i, j] = value
        k_ij[j, i] = value
    return runtime.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([float(pure_rows[name]["m"]) for name in species], dtype=float),
            "s": np.asarray([float(pure_rows[name]["s_A"]) for name in species], dtype=float),
            "e": np.asarray([float(pure_rows[name]["e_over_k_K"]) for name in species], dtype=float),
            "k_ij": k_ij,
        },
        species=species,
    )


def _cloud_shadow_pair_source(case_dir: Path) -> dict[str, Any]:
    rows = _read_csv(case_dir / "experimental_tielines.csv")
    if len(rows) != 1:
        raise ValueError("cloud_shadow_paired_branch_rows_missing")
    row = rows[0]
    species_count = len(EXPECTED_CLOUD_SHADOW_SPECIES)
    return {
        "source_row_pair": row.get("source_row_pair"),
        "pressure_Pa": float(row["pressure_Pa"]),
        "source_temperature_K": float(row["temperature_K"]),
        "parent_liquid_composition": _cloud_shadow_composition_from_prefix(row, "liquid1_x", species_count),
        "source_shadow_composition": _cloud_shadow_composition_from_prefix(row, "liquid2_x", species_count),
    }


def _cloud_shadow_feed_source(case_dir: Path, species_count: int) -> dict[str, Any]:
    rows = _read_csv(case_dir / "feed_compositions.csv")
    if len(rows) != 1:
        raise ValueError("cloud_shadow_expected_one_feed_row")
    row = rows[0]
    return {
        "temperature_K": float(row["temperature_K"]),
        "pressure_Pa": float(row["pressure_Pa"]),
        "feed_composition": _cloud_shadow_composition_from_prefix(row, "z", species_count),
    }


def _cloud_shadow_composition_error(left: list[float], right: list[float]) -> list[float]:
    if len(left) != len(right):
        return []
    return [abs(a - b) for a, b in zip(left, right, strict=True)]


def _cloud_shadow_max_composition_error(left: list[float], right: list[float]) -> float | None:
    errors = _cloud_shadow_composition_error(left, right)
    return max(errors) if errors else None


def _cloud_shadow_phase_match(
    phase_compositions: list[list[float]],
    source_parent: list[float],
    source_shadow: list[float],
) -> dict[str, Any]:
    if len(phase_compositions) < 2:
        return {
            "complete": False,
            "blockers": ["cloud_shadow_model_reference_phase_compositions_missing"],
        }
    best: dict[str, Any] | None = None
    for parent_index, shadow_index in ((0, 1), (1, 0)):
        parent = phase_compositions[parent_index]
        shadow = phase_compositions[shadow_index]
        parent_error = _cloud_shadow_max_composition_error(parent, source_parent)
        shadow_error = _cloud_shadow_max_composition_error(shadow, source_shadow)
        if parent_error is None or shadow_error is None:
            continue
        candidate = {
            "complete": True,
            "parent_index": parent_index,
            "shadow_index": shadow_index,
            "parent_liquid_composition": parent,
            "shadow_liquid_composition": shadow,
            "source_parent_composition_abs_error": _cloud_shadow_composition_error(parent, source_parent),
            "source_shadow_composition_abs_error": _cloud_shadow_composition_error(shadow, source_shadow),
            "max_source_parent_composition_abs_error": parent_error,
            "max_source_shadow_composition_abs_error": shadow_error,
            "blockers": [],
        }
        score = parent_error + shadow_error
        if best is None or score < float(best["score"]):
            candidate["score"] = score
            best = candidate
    if best is None:
        return {
            "complete": False,
            "blockers": ["cloud_shadow_model_reference_phase_match_missing"],
        }
    best.pop("score")
    return best


def _run_cloud_shadow_model_reference_route(
    mix: Any,
    request: dict[str, Any],
    thresholds: dict[str, Any],
    *,
    debug: bool,
) -> dict[str, Any]:
    def run() -> dict[str, Any]:
        return dict(
            _core._native_equilibrium_selector_route_result(
                mix._native,
                request,
                int(thresholds["solver_max_iterations"]),
                float(thresholds["solver_tolerance"]),
                0.0,
                "auto",
                50 if debug else 8,
                float(thresholds["material_balance_abs"]),
                float(thresholds["pressure_abs_Pa"]),
                float(thresholds["solver_tolerance"]),
                float(thresholds["solver_tolerance"]),
                {},
                linear_solver="auto",
                print_level=5 if debug else 0,
                acceptable_tolerance=float(thresholds["acceptable_tolerance"]),
                constraint_violation_tolerance=float(thresholds["constraint_violation_tolerance"]),
                dual_infeasibility_tolerance=float(thresholds["dual_infeasibility_tolerance"]),
                complementarity_tolerance=float(thresholds["complementarity_tolerance"]),
            )
        )

    if debug:
        with runtime.redirect_native_stdout_to_stderr():
            return run()
    with runtime.suppress_native_stdout():
        return run()


def _cloud_shadow_model_reference(
    mix: Any,
    case_dir: Path,
    species_count: int,
    source: dict[str, Any],
    thresholds: dict[str, Any],
    *,
    debug: bool,
) -> dict[str, Any]:
    feed = _cloud_shadow_feed_source(case_dir, species_count)
    request = {
        "route": "neutral_lle",
        "temperature": float(feed["temperature_K"]),
        "pressure": float(feed["pressure_Pa"]),
        "composition": list(feed["feed_composition"]),
        "composition_role": "feed",
    }
    route_payload = _run_cloud_shadow_model_reference_route(mix, request, thresholds, debug=debug)
    postsolve = route_payload.get("postsolve")
    postsolve = postsolve if isinstance(postsolve, dict) else {}
    phase_compositions = [
        [float(value) for value in composition]
        for composition in postsolve.get("phase_compositions", [])
        if isinstance(composition, list)
    ]
    match = _cloud_shadow_phase_match(
        phase_compositions,
        list(source.get("parent_liquid_composition", [])),
        list(source.get("source_shadow_composition", [])),
    )
    blockers = list(match.get("blockers", []))
    if not math.isclose(feed["temperature_K"], float(source["source_temperature_K"]), rel_tol=0.0, abs_tol=1.0e-9):
        blockers.append("cloud_shadow_model_reference_temperature_source_mismatch")
    if not math.isclose(feed["pressure_Pa"], float(source["pressure_Pa"]), rel_tol=0.0, abs_tol=1.0e-6):
        blockers.append("cloud_shadow_model_reference_pressure_source_mismatch")
    if route_payload.get("status") != "production_accepted":
        blockers.append("cloud_shadow_model_reference_route_not_production_accepted")
    if route_payload.get("solver_status") != "success":
        blockers.append("cloud_shadow_model_reference_solver_not_success")
    if route_payload.get("application_status") != "solve_succeeded":
        blockers.append("cloud_shadow_model_reference_application_not_solved")
    if route_payload.get("accepted") is not True:
        blockers.append("cloud_shadow_model_reference_not_accepted")
    parent_error = match.get("max_source_parent_composition_abs_error")
    shadow_error = match.get("max_source_shadow_composition_abs_error")
    composition_threshold = _threshold_value(thresholds, "composition_abs")
    if parent_error is None or float(parent_error) > composition_threshold:
        blockers.append("cloud_shadow_model_parent_source_error_exceeds_threshold")
    if shadow_error is None or float(shadow_error) > composition_threshold:
        blockers.append("cloud_shadow_model_shadow_source_error_exceeds_threshold")
    return {
        "complete": not blockers,
        "status": "model_reference_complete" if not blockers else "model_reference_blocked",
        "blockers": sorted(set(blockers)),
        "route": "neutral_lle",
        "route_status": route_payload.get("status"),
        "solver_status": route_payload.get("solver_status"),
        "application_status": route_payload.get("application_status"),
        "source_temperature_K": feed["temperature_K"],
        "pressure_Pa": feed["pressure_Pa"],
        "feed_composition": feed["feed_composition"],
        **{key: value for key, value in match.items() if key not in {"blockers", "complete"}},
    }


def _cloud_shadow_route_request(source: dict[str, Any], parent_liquid_composition: list[float]) -> dict[str, Any]:
    return {
        "route": EXPECTED_CLOUD_SHADOW_ROUTE,
        "pressure": float(source["pressure_Pa"]),
        "composition": list(parent_liquid_composition),
        "composition_role": EXPECTED_CLOUD_SHADOW_COMPOSITION_ROLE,
    }


def _run_cloud_shadow_native_route(
    mix: Any,
    request: dict[str, Any],
    thresholds: dict[str, Any],
    *,
    debug: bool,
) -> dict[str, Any]:
    def run() -> dict[str, Any]:
        return dict(
            _core._native_equilibrium_cloud_shadow_route_result(
                mix._native,
                request,
                int(thresholds["solver_max_iterations"]),
                float(thresholds["solver_tolerance"]),
                0.0,
                "auto",
                50 if debug else 8,
                float(thresholds["material_balance_abs"]),
                float(thresholds["pressure_abs_Pa"]),
                float(thresholds["ln_fugacity_abs"]),
                float(thresholds["phase_distance_min"]),
                {},
                linear_solver="auto",
                option_profile="held_refinement",
                print_level=5 if debug else 0,
                acceptable_tolerance=float(thresholds["acceptable_tolerance"]),
                constraint_violation_tolerance=float(thresholds["constraint_violation_tolerance"]),
                dual_infeasibility_tolerance=float(thresholds["dual_infeasibility_tolerance"]),
                complementarity_tolerance=float(thresholds["complementarity_tolerance"]),
            )
        )

    if debug:
        with runtime.redirect_native_stdout_to_stderr():
            return run()
    with runtime.suppress_native_stdout():
        return run()


def _normalized_phase_amount_composition(route_payload: dict[str, Any], phase_index: int) -> list[float]:
    phase_amounts = route_payload.get("phase_amounts")
    if not isinstance(phase_amounts, list) or len(phase_amounts) <= phase_index:
        return []
    values = [float(value) for value in phase_amounts[phase_index]]
    total = sum(values)
    if total <= 0.0 or not math.isfinite(total):
        return []
    return [value / total for value in values]


def _cloud_shadow_phase_composition(route_payload: dict[str, Any], label: str, phase_index: int) -> list[float]:
    physical = route_payload.get("physical_evidence")
    physical = physical if isinstance(physical, dict) else {}
    for phase in physical.get("phases", []) if isinstance(physical.get("phases"), list) else []:
        if isinstance(phase, dict) and phase.get("label") == label and isinstance(phase.get("composition"), list):
            return [float(value) for value in phase["composition"]]
    return _normalized_phase_amount_composition(route_payload, phase_index)


def _cloud_shadow_phase_distance(route_payload: dict[str, Any], parent: list[float], shadow: list[float]) -> float | None:
    postsolve = route_payload.get("postsolve")
    postsolve = postsolve if isinstance(postsolve, dict) else {}
    physical = route_payload.get("physical_evidence")
    physical = physical if isinstance(physical, dict) else {}
    for source in (postsolve, physical):
        value = source.get("phase_distance")
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            return float(value)
    if parent and shadow and len(parent) == len(shadow):
        return max(abs(left - right) for left, right in zip(parent, shadow, strict=True))
    return None


def _threshold_value(thresholds: dict[str, Any], key: str) -> float:
    value = thresholds.get(key)
    if not _positive_finite_float(value):
        raise ValueError(f"cloud_shadow_threshold_invalid:{key}")
    return float(value)


def _cloud_shadow_residual_blockers(residuals: dict[str, float | None], phase_distance: float | None, thresholds: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    checks = (
        ("material_balance_norm", "material_balance_abs", "cloud_shadow_material_balance_exceeds_threshold"),
        ("pressure_consistency_norm", "pressure_abs_Pa", "cloud_shadow_pressure_residual_exceeds_threshold"),
        ("ln_fugacity_consistency_norm", "ln_fugacity_abs", "cloud_shadow_ln_fugacity_residual_exceeds_threshold"),
    )
    for residual_key, threshold_key, blocker in checks:
        value = residuals.get(residual_key)
        if value is None or abs(float(value)) > _threshold_value(thresholds, threshold_key):
            blockers.append(blocker)
    if phase_distance is None or phase_distance < _threshold_value(thresholds, "phase_distance_min"):
        blockers.append("cloud_shadow_phase_distance_below_threshold")
    return blockers


def _cloud_shadow_route_trace(
    route_payload: dict[str, Any],
    source_fixture: str,
    parent: list[float],
    residuals: dict[str, float | None],
    seed_attempts: list[dict[str, Any]],
    iteration_limit_attempts: list[str],
    strict: bool,
) -> dict[str, Any]:
    physical_evidence = route_payload.get("physical_evidence")
    physical_evidence = physical_evidence if isinstance(physical_evidence, dict) else {}
    return {
        "schema_version": BOUNDARY_TRACE_SCHEMA_VERSION,
        "route": EXPECTED_CLOUD_SHADOW_ROUTE,
        "workflow_label": "Cloud point",
        "workflow_kind": "derived_boundary",
        "diagram_target": "T-x",
        "known_variables": ["P", "parent_liquid_composition"],
        "free_variables": ["T", "shadow_liquid_composition", "phase_volumes"],
        "solved_boundary_variable": "T",
        "fixed_composition_role": EXPECTED_CLOUD_SHADOW_COMPOSITION_ROLE,
        "fixed_composition": parent,
        "phase_labels": route_payload.get("phase_labels", physical_evidence.get("phase_labels", [])),
        "phase_roles": route_payload.get("phase_roles", physical_evidence.get("phase_roles", [])),
        "phase_amounts": route_payload.get("phase_amounts", []),
        "phase_volumes": route_payload.get("phase_volumes", []),
        "source_fixture": source_fixture,
        "selector_family": route_payload.get("selector_family", EXPECTED_CLOUD_SHADOW_SELECTOR_FAMILY),
        "problem_name": route_payload.get("problem_name", EXPECTED_CLOUD_SHADOW_PROBLEM_NAME),
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
        "public_route_admission": route_payload.get("public_route_admission", "unknown"),
    }


def evaluate_cloud_shadow_route_evidence(
    case_dir: Path = DEFAULT_CLOUD_SHADOW_CASE_DIR,
    *,
    run_native: bool = False,
    debug: bool = False,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    gate = evaluate_cloud_shadow_gate(case_dir)
    thresholds = _read_json(case_dir / "thresholds.json") if (case_dir / "thresholds.json").exists() else {}
    source = _cloud_shadow_pair_source(case_dir) if (case_dir / "experimental_tielines.csv").exists() else {}
    parent = list(source.get("parent_liquid_composition", []))
    source_shadow = list(source.get("source_shadow_composition", []))
    source_fixture = _repo_relative_path(case_dir)
    blockers: list[str] = []
    route_payload: dict[str, Any] = {}
    model_reference: dict[str, Any] = {}
    source_parent_error: list[float] = []
    solved_temperature: float | None = None
    solved_shadow: list[float] = []
    temperature_error: float | None = None
    shadow_error: list[float] = []
    max_shadow_error: float | None = None
    residuals: dict[str, float | None] = {
        "material_balance_norm": None,
        "pressure_consistency_norm": None,
        "ln_fugacity_consistency_norm": None,
        "phase_equilibrium_norm": None,
        "scaled_constraint_violation_inf_norm": None,
    }
    seed_attempts: list[dict[str, Any]] = []
    iteration_limit_attempts: list[str] = []
    strict = False
    phase_distance: float | None = None
    route_trace: dict[str, Any] = {}
    public_route_admission = "closed"

    if not gate["complete"]:
        blockers.extend(gate["source_data_blockers"])
    elif not run_native:
        blockers.append("native_cloud_temperature_route_unrequested")
    elif not hasattr(_core, "_native_equilibrium_cloud_shadow_route_result"):
        blockers.append("native_cloud_temperature_route_missing")
    elif not hasattr(_core, "_native_equilibrium_selector_route_result"):
        blockers.append("native_neutral_lle_model_reference_route_missing")
    else:
        metadata = _read_json(case_dir / "metadata.json")
        species = [str(item) for item in metadata["species"]]
        mix = _cloud_shadow_case_mixture(case_dir, species)
        model_reference = _cloud_shadow_model_reference(
            mix,
            case_dir,
            len(species),
            source,
            thresholds,
            debug=debug,
        )
        blockers.extend(model_reference.get("blockers", []))
        if not model_reference.get("complete"):
            parent = []
        else:
            parent = [float(value) for value in model_reference["parent_liquid_composition"]]
            source_parent_error = [
                float(value) for value in model_reference.get("source_parent_composition_abs_error", [])
            ]
            request = _cloud_shadow_route_request(source, parent)
            route_payload = _run_cloud_shadow_native_route(mix, request, thresholds, debug=debug)
            public_route_admission = str(route_payload.get("public_route_admission", "unknown"))
            seed_attempts = _seed_attempt_summary(route_payload)
            iteration_limit_attempts = _iteration_limit_seed_attempts(route_payload)
            strict = _strict_convergence(route_payload, iteration_limit_attempts)
            residuals = _residuals(route_payload)
            solved_temperature = native_route_solved_temperature(route_payload, EXPECTED_CLOUD_SHADOW_ROUTE)
            solved_shadow = _cloud_shadow_phase_composition(route_payload, "shadow_liquid", 1)
            phase_distance = _cloud_shadow_phase_distance(route_payload, parent, solved_shadow)
            temperature_error = abs(solved_temperature - float(source["source_temperature_K"]))
            shadow_error = [abs(left - right) for left, right in zip(solved_shadow, source_shadow, strict=True)]
            max_shadow_error = max(shadow_error) if shadow_error else None
            route_trace = _cloud_shadow_route_trace(
                route_payload,
                source_fixture,
                parent,
                residuals,
                seed_attempts,
                iteration_limit_attempts,
                strict,
            )
            if not strict:
                blockers.append("native_cloud_temperature_strict_convergence_missing")
            if temperature_error > _threshold_value(thresholds, "source_temperature_pair_abs_K"):
                blockers.append("cloud_shadow_temperature_error_exceeds_threshold")
            if max_shadow_error is None or max_shadow_error > _threshold_value(thresholds, "composition_abs"):
                blockers.append("cloud_shadow_shadow_composition_error_exceeds_threshold")
            blockers.extend(_cloud_shadow_residual_blockers(residuals, phase_distance, thresholds))
            if route_payload.get("selector_family") != EXPECTED_CLOUD_SHADOW_SELECTOR_FAMILY:
                blockers.append("cloud_shadow_selector_family_mismatch")
            if route_payload.get("problem_name") != EXPECTED_CLOUD_SHADOW_PROBLEM_NAME:
                blockers.append("cloud_shadow_problem_name_mismatch")
            if public_route_admission != "closed":
                blockers.append("cloud_shadow_public_route_admission_open")

    blockers = sorted(set(blockers))
    complete = gate["complete"] and run_native and not blockers
    status = "native_route_complete" if complete else "native_route_blocked"
    return {
        "complete": complete,
        "status": status,
        "source_fixture": source_fixture,
        "source_gate_complete": bool(gate["complete"]),
        "source_gate_status": gate["status"],
        "source_data_blockers": list(gate["source_data_blockers"]),
        "route_evidence_blockers": blockers,
        "route": EXPECTED_CLOUD_SHADOW_ROUTE,
        "pressure_Pa": source.get("pressure_Pa", EXPECTED_CLOUD_SHADOW_PRESSURE_PA),
        "parent_liquid_composition": parent,
        "source_parent_liquid_composition": source.get("parent_liquid_composition", []),
        "source_parent_composition_abs_error": source_parent_error,
        "source_temperature_K": source.get("source_temperature_K"),
        "solved_temperature_K": solved_temperature,
        "temperature_abs_error_K": temperature_error,
        "source_shadow_composition": source_shadow,
        "solved_shadow_composition": solved_shadow,
        "shadow_composition_abs_error": shadow_error,
        "max_shadow_composition_abs_error": max_shadow_error,
        "model_reference": model_reference,
        "phase_distance": phase_distance,
        "residuals": residuals,
        "strict_convergence": strict,
        "solver_status": route_payload.get("solver_status"),
        "application_status": route_payload.get("application_status"),
        "seed_attempts": seed_attempts,
        "route_trace": route_trace,
        "public_route_admission": public_route_admission,
        "native_route_payload": route_payload if run_native and route_payload else None,
    }


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
    cloud_shadow_route_evidence = (
        evaluate_cloud_shadow_route_evidence(
            args.cloud_shadow_case_dir,
            run_native=bool(args.run_cloud_shadow_route),
            debug=bool(args.debug),
        )
        if getattr(args, "run_cloud_shadow_route", False) or getattr(args, "require_cloud_shadow_route", False)
        else None
    )
    cloud_shadow_blockers = cloud_shadow_gate["source_data_blockers"] if cloud_shadow_gate else []
    cloud_shadow_route_blockers = (
        cloud_shadow_route_evidence["route_evidence_blockers"] if cloud_shadow_route_evidence else []
    )
    all_blockers = list(
        dict.fromkeys([*blockers, *trace_result["blockers"], *cloud_shadow_blockers, *cloud_shadow_route_blockers])
    )
    route_complete = (
        summary["requested_route_point_count"] > 0
        and summary["failed_route_point_count"] == 0
        and not blockers
        and not trace_result["blockers"]
    )
    if cloud_shadow_route_evidence and not args.run_current_boundary_route:
        complete = bool(cloud_shadow_route_evidence["complete"])
    elif cloud_shadow_gate and not args.run_current_boundary_route:
        complete = bool(cloud_shadow_gate["complete"])
    else:
        complete = route_complete and not all_blockers
    if cloud_shadow_route_evidence and not args.run_current_boundary_route:
        status = "cloud_shadow_route_complete" if complete else "cloud_shadow_route_blocked"
    elif cloud_shadow_gate and not args.run_current_boundary_route:
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
    if cloud_shadow_route_evidence:
        payload["cloud_shadow_route_evidence"] = cloud_shadow_route_evidence
    return payload


def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if getattr(args, "require_cloud_shadow_gate", False):
        args.cloud_shadow_gate = True
    if getattr(args, "require_cloud_shadow_route", False):
        args.run_cloud_shadow_route = True
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
        if args.require_cloud_shadow_route and not payload.get("cloud_shadow_route_evidence", {}).get("complete", False):
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
        "--run-cloud-shadow-route",
        action="store_true",
        help="Run the private cloud/shadow route evidence path for the retained source pair.",
    )
    parser.add_argument(
        "--require-cloud-shadow-route",
        action="store_true",
        help="Return nonzero unless the private cloud/shadow route evidence path passes.",
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
