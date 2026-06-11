from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = ANALYSIS_ROOT / "shared" / "results"
FIXTURE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_tp_flash"
    / "hydrocarbon_workbook_flash"
)

for import_root in (
    REPO_ROOT,
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "tests",
):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

import epcsaft
import epcsaft_equilibrium
from equilibrium_support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_FLASH_Z,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)
from scripts.validation import check_phase_discovery


COMPONENTS = ("Methane", "Ethane", "Propane")


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _max_component_error(expected: tuple[float, ...], actual: tuple[float, ...]) -> float:
    return max(abs(left - right) for left, right in zip(expected, actual, strict=True))


def _status_class(status: str) -> str:
    if status.startswith("verified"):
        return "verified"
    if status.startswith("not_requested"):
        return "not_requested"
    return "incomplete"


def _run_neutral_flash() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    result = epcsaft_equilibrium.Equilibrium(
        mixture,
        route="flash",
        T=HYDROCARBON_T,
        P=HYDROCARBON_BUBBLE_P,
        z=HYDROCARBON_FLASH_Z,
    ).solve(
        solver_options={
            "max_iterations": 200,
            "tolerance": 1.0e-8,
            "ipopt_iteration_history_limit": 4,
        }
    )

    liquid = result.phases["liquid"]
    vapor = result.phases["vapor"]
    liquid_x = tuple(float(value) for value in liquid.composition)
    vapor_y = tuple(float(value) for value in vapor.composition)
    source_liquid = tuple(float(value) for value in HYDROCARBON_LIQUID_X)
    source_vapor = tuple(float(value) for value in HYDROCARBON_VAPOR_Y)
    source_feed = tuple(float(value) for value in HYDROCARBON_FLASH_Z)

    phase_rows: list[dict[str, Any]] = []
    for role, source, composition in (
        ("feed", "constructed_equal_phase_feed", source_feed),
        ("source_liquid", "workbook", source_liquid),
        ("source_vapor", "workbook", source_vapor),
        ("solved_liquid", "current_main_route", liquid_x),
        ("solved_vapor", "current_main_route", vapor_y),
    ):
        phase_rows.append(
            {
                "role": role,
                "source": source,
                "temperature_K": HYDROCARBON_T,
                "pressure_Pa": HYDROCARBON_BUBBLE_P,
                "Methane": composition[0],
                "Ethane": composition[1],
                "Propane": composition[2],
            }
        )

    component_error_rows: list[dict[str, Any]] = []
    for phase, expected, actual in (
        ("liquid", source_liquid, liquid_x),
        ("vapor", source_vapor, vapor_y),
    ):
        for component, expected_value, actual_value in zip(COMPONENTS, expected, actual, strict=True):
            component_error_rows.append(
                {
                    "phase": phase,
                    "component": component,
                    "expected_mole_fraction": expected_value,
                    "actual_mole_fraction": actual_value,
                    "absolute_error": abs(expected_value - actual_value),
                }
            )

    diagnostics = result.diagnostics
    metadata = json.loads((FIXTURE_DIR / "metadata.json").read_text(encoding="utf-8"))
    tolerances = metadata["acceptance_tolerances"]
    liquid_fraction_error = abs(0.5 - float(liquid.phase_fraction))
    vapor_fraction_error = abs(0.5 - float(vapor.phase_fraction))
    tolerance_rows = [
        {
            "metric": "composition_abs",
            "observed_abs": max(
                _max_component_error(source_liquid, liquid_x),
                _max_component_error(source_vapor, vapor_y),
            ),
            "tolerance": tolerances["composition_abs"],
            "unit": "mole_fraction",
        },
        {
            "metric": "phase_fraction_abs",
            "observed_abs": max(liquid_fraction_error, vapor_fraction_error),
            "tolerance": tolerances["phase_fraction_abs"],
            "unit": "phase_fraction",
        },
        {
            "metric": "material_balance_abs",
            "observed_abs": float(diagnostics["material_balance_norm"]),
            "tolerance": tolerances["material_balance_abs"],
            "unit": "mole_balance",
        },
        {
            "metric": "pressure_abs_Pa",
            "observed_abs": float(diagnostics["pressure_consistency_norm"]),
            "tolerance": tolerances["pressure_abs_Pa"],
            "unit": "Pa",
        },
        {
            "metric": "ln_fugacity_abs",
            "observed_abs": float(diagnostics["ln_fugacity_consistency_norm"]),
            "tolerance": tolerances["ln_fugacity_abs"],
            "unit": "ln_fugacity",
        },
    ]
    for row in tolerance_rows:
        observed = float(row["observed_abs"])
        tolerance = float(row["tolerance"])
        row["observed_to_tolerance"] = observed / tolerance if tolerance > 0 else math.inf
        row["accepted"] = observed <= tolerance

    summary = {
        "case_label": metadata["case_label"],
        "family_label": metadata["family_label"],
        "species": list(COMPONENTS),
        "temperature_K": HYDROCARBON_T,
        "pressure_Pa": HYDROCARBON_BUBBLE_P,
        "pressure_MPa": HYDROCARBON_BUBBLE_P / 1.0e6,
        "route_status": diagnostics.get("route_status"),
        "solver_status": diagnostics.get("solver_status"),
        "application_status": diagnostics.get("application_status"),
        "selected_candidate_count": diagnostics.get("selected_candidate_count"),
        "phase_distance": diagnostics.get("phase_distance"),
        "stability_checked": diagnostics.get("stability_checked"),
        "stability_accepted": diagnostics.get("stability_accepted"),
        "candidate_completeness_accepted": diagnostics.get("candidate_completeness_accepted"),
        "note": "Neutral TP flash route evidence only; this is not LLE, associating, electrolyte, or reactive route evidence.",
    }
    return phase_rows, component_error_rows, tolerance_rows, summary


def _run_held_gate_status() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = check_phase_discovery.evaluate_phase_discovery(include_route_refinement=True)
    rows: list[dict[str, Any]] = []
    labels = {
        "deterministic_screening": "Deterministic screening",
        "continuous_tpd_minimization": "Continuous TPD minimization",
        "held_stage_i_stability": "HELD Stage I stability",
        "held_stage_ii_dual_phase_discovery": "HELD Stage II dual discovery",
        "held_stage_iii_ipopt_refinement": "HELD Stage III Ipopt refinement",
    }
    for index, key in enumerate(labels):
        status = str(payload["requirement_status"][key])
        rows.append(
            {
                "order": index,
                "gate": key,
                "label": labels[key],
                "status": status,
                "status_class": _status_class(status),
                "accepted": status.startswith("verified"),
            }
        )
    summary = {
        "case_label": payload["case_label"],
        "family_label": payload["family_label"],
        "complete": payload["complete"],
        "incomplete_requirements": payload["incomplete_requirements"],
        "diagnostics": {
            key: value
            for key, value in dict(payload["diagnostics"]).items()
            if key
            in {
                "phase_discovery_backend",
                "continuous_tpd_converged_count",
                "continuous_tpd_min",
                "held_stage_ii_status",
                "held_stage_ii_bound_gap",
                "held_stage_ii_replay_ready",
                "held_stage_iii_status",
                "held_stage_iii_consumed_stage_ii_replay_metadata",
                "route_solver_status",
                "route_application_status",
                "route_status",
                "route_scaled_acceptance_passed",
            }
        },
    }
    return rows, summary


def main() -> int:
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    phase_rows, component_error_rows, tolerance_rows, flash_summary = _run_neutral_flash()
    gate_rows, gate_summary = _run_held_gate_status()

    _write_csv(
        RESULTS_ROOT / "neutral_tp_flash_phase_points.csv",
        ["role", "source", "temperature_K", "pressure_Pa", "Methane", "Ethane", "Propane"],
        phase_rows,
    )
    _write_csv(
        RESULTS_ROOT / "neutral_tp_flash_component_errors.csv",
        ["phase", "component", "expected_mole_fraction", "actual_mole_fraction", "absolute_error"],
        component_error_rows,
    )
    _write_csv(
        RESULTS_ROOT / "neutral_tp_flash_tolerance_summary.csv",
        ["metric", "observed_abs", "tolerance", "unit", "observed_to_tolerance", "accepted"],
        tolerance_rows,
    )
    _write_csv(
        RESULTS_ROOT / "held_1_0_gate_status.csv",
        ["order", "gate", "label", "status", "status_class", "accepted"],
        gate_rows,
    )
    (RESULTS_ROOT / "run_summary.json").write_text(
        json.dumps({"neutral_tp_flash": flash_summary, "held_1_0": gate_summary}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
