"""Run the live 32-point NIST single-component VLE production proof."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Final

REPO_ROOT = Path(__file__).resolve().parents[2]
for source_root in (
    REPO_ROOT,
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
):
    source_path = str(source_root)
    if source_path not in sys.path:
        sys.path.insert(0, source_path)

from epcsaft_equilibrium._native import extension_native_core

from analyses.package_validation.equilibrium_single_component_vle.figures.hydrocarbon_saturation_pressure.scripts.generate_data import (
    generate_validation_rows,
)
from scripts.validation import equilibrium_validation_runtime as runtime
from scripts.validation import native_freshness
from scripts.validation.nist_saturation_contract import (
    EXPECTED_SOURCE_GRID,
    MAX_ITERATIONS,
    SOLVER_TOLERANCE,
    load_canonical_source_rows,
)

ACCEPTANCE_THRESHOLDS: Final[dict[str, float | int | str]] = {
    "joined_source_row_count": 32,
    "max_pressure_absolute_relative_error_percent": 4.0,
    "max_liquid_density_absolute_relative_error_percent": 2.0,
    "max_pressure_consistency_norm": 1.0e-2,
    "max_chemical_potential_consistency_norm": 1.0e-6,
    "min_phase_distance": 1.0e-2,
    "route_status": "accepted",
    "solver_status": "success",
}
EXACT_HESSIAN_BACKEND: Final[str] = "cppad_phase_pressure_route"
DIAGNOSTIC_ONLY_METRICS: Final[dict[str, dict[str, str]]] = {
    "ln_fugacity_consistency_norm": {
        "summary_metric": "max_ln_fugacity_consistency_norm",
        "acceptance_role": "diagnostic_only",
        "rationale": (
            "The native pure-density saturation route certifies phase pressure and "
            "chemical-potential consistency; the logarithmic fugacity difference is "
            "retained separately to expose low-pressure conditioning."
        ),
    }
}
RAW_VALUE_FIELDS: Final[tuple[str, ...]] = (
    "p_sat_nist_Pa",
    "p_sat_route_Pa",
    "rho_sat_liq_nist_kg_m3",
    "rho_liquid_route_kg_m3",
)
STORED_ERROR_FIELDS: Final[tuple[str, ...]] = (
    "absolute_error_Pa",
    "relative_error_percent",
    "absolute_relative_error_percent",
    "rho_sat_liq_absolute_error_kg_m3",
    "rho_sat_liq_relative_error_percent",
    "rho_sat_liq_absolute_relative_error_percent",
)


def _finite_float(row: dict[str, object], field: str) -> float | None:
    if field not in row:
        return None
    try:
        value = float(row[field])
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _positive_finite_float(row: dict[str, object], field: str) -> float | None:
    value = _finite_float(row, field)
    return value if value is not None and value > 0.0 else None


def _recomputed_error_values(row: dict[str, object]) -> dict[str, float] | None:
    raw_values = {field: _positive_finite_float(row, field) for field in RAW_VALUE_FIELDS}
    if any(value is None for value in raw_values.values()):
        return None
    pressure_reference = raw_values["p_sat_nist_Pa"]
    pressure_model = raw_values["p_sat_route_Pa"]
    density_reference = raw_values["rho_sat_liq_nist_kg_m3"]
    density_model = raw_values["rho_liquid_route_kg_m3"]
    assert pressure_reference is not None
    assert pressure_model is not None
    assert density_reference is not None
    assert density_model is not None
    pressure_absolute_error = pressure_model - pressure_reference
    pressure_relative_error = 100.0 * pressure_absolute_error / pressure_reference
    density_absolute_error = density_model - density_reference
    density_relative_error = 100.0 * density_absolute_error / density_reference
    return {
        "absolute_error_Pa": pressure_absolute_error,
        "relative_error_percent": pressure_relative_error,
        "absolute_relative_error_percent": abs(pressure_relative_error),
        "rho_sat_liq_absolute_error_kg_m3": density_absolute_error,
        "rho_sat_liq_relative_error_percent": density_relative_error,
        "rho_sat_liq_absolute_relative_error_percent": abs(density_relative_error),
    }


def _source_float_matches(row: dict[str, object], source_row: dict[str, str], field: str) -> bool:
    source_field = {
        "p_sat_nist_Pa": "p_sat_Pa",
        "rho_sat_liq_nist_kg_m3": "rho_sat_liq_kg_m3",
    }.get(field, field)
    try:
        return float(row[field]) == float(source_row[source_field])
    except (KeyError, TypeError, ValueError):
        return False


def _point_label(row: dict[str, object], index: int) -> str:
    species = str(row.get("species", "")).strip()
    temperature = _finite_float(row, "T_K")
    if species and temperature is not None:
        return f"{species}:{temperature:g}K"
    return f"row-{index}"


def _integer_value(row: dict[str, object], field: str) -> int | None:
    value = _finite_float(row, field)
    if value is None or not value.is_integer():
        return None
    return int(value)


def evaluate_live_rows(
    rows: list[dict[str, object]],
    *,
    native_freshness_receipt: dict[str, object],
    require_fresh_native: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    try:
        canonical_source_rows = load_canonical_source_rows()
    except (OSError, ValueError) as exc:
        canonical_source_rows = []
        blockers.append(f"nist_canonical_source_load_failed:{type(exc).__name__}")
    canonical_rows_by_key = {
        (str(source_row["species"]), float(source_row["T_K"])): source_row for source_row in canonical_source_rows
    }
    source_grid: set[tuple[str, float]] = set()
    species_counts: Counter[str] = Counter()
    metric_values: dict[str, list[float]] = {
        "absolute_relative_error_percent": [],
        "rho_sat_liq_absolute_relative_error_percent": [],
        "pressure_consistency_norm": [],
        "chemical_potential_consistency_norm": [],
        "ln_fugacity_consistency_norm": [],
        "phase_distance": [],
    }
    exact_hessian_row_count = 0
    hessian_approximations: set[str] = set()
    jacobian_approximations: set[str] = set()
    hessian_backends: set[str] = set()
    eval_h_call_counts: list[int] = []

    if len(rows) != ACCEPTANCE_THRESHOLDS["joined_source_row_count"]:
        blockers.append("nist_source_grid_mismatch")

    for index, row in enumerate(rows):
        label = _point_label(row, index)
        species = str(row.get("species", "")).strip()
        temperature = _finite_float(row, "T_K")
        if species and temperature is not None:
            source_grid.add((species, temperature))
            species_counts[species] += 1

        canonical_source_row = canonical_rows_by_key.get((species, temperature)) if temperature is not None else None
        if canonical_source_row is None:
            blockers.append(f"nist_source_row_missing:{label}")
        else:
            if row.get("source") != canonical_source_row["source"]:
                blockers.append(f"nist_source_identity_mismatch:{label}")
            if not _source_float_matches(row, canonical_source_row, "T_K"):
                blockers.append(f"nist_source_reference_mismatch:T_K:{label}")
            for field in ("p_sat_nist_Pa", "rho_sat_liq_nist_kg_m3"):
                if not _source_float_matches(row, canonical_source_row, field):
                    blockers.append(f"nist_source_reference_mismatch:{field}:{label}")

        solver_tolerance = _finite_float(row, "solver_tolerance")
        if solver_tolerance is None or solver_tolerance != SOLVER_TOLERANCE:
            blockers.append(f"solver_tolerance_mismatch:{label}")
        max_iterations = _integer_value(row, "max_iterations")
        if max_iterations != MAX_ITERATIONS:
            blockers.append(f"max_iterations_mismatch:{label}")

        for field in RAW_VALUE_FIELDS:
            if _positive_finite_float(row, field) is None:
                blockers.append(f"missing_or_nonpositive_or_nonfinite_raw_value:{field}:{label}")

        recomputed_errors = _recomputed_error_values(row)
        if recomputed_errors is not None:
            for field in STORED_ERROR_FIELDS:
                stored_error = _finite_float(row, field)
                expected_error = recomputed_errors[field]
                # Stored errors are a zero-ULP serialization contract: the
                # parsed float must equal the raw-column recomputation exactly.
                if stored_error is None or stored_error != expected_error:
                    blockers.append(f"stored_error_mismatch:{field}:{label}")

        if row.get("route_status") != ACCEPTANCE_THRESHOLDS["route_status"]:
            blockers.append(f"route_status_not_accepted:{label}")
        if row.get("solver_status") != ACCEPTANCE_THRESHOLDS["solver_status"]:
            blockers.append(f"solver_status_not_success:{label}")

        exact_hessian_available = row.get("exact_hessian_available") is True
        hessian_approximation = str(row.get("hessian_approximation", ""))
        jacobian_approximation = str(row.get("jacobian_approximation", ""))
        hessian_backend = str(row.get("hessian_backend", ""))
        eval_h_calls = _integer_value(row, "eval_h_calls")
        if exact_hessian_available:
            exact_hessian_row_count += 1
        else:
            blockers.append(f"exact_hessian_missing:{label}")
        hessian_approximations.add(hessian_approximation)
        jacobian_approximations.add(jacobian_approximation)
        hessian_backends.add(hessian_backend)
        if hessian_approximation != "exact":
            blockers.append(f"hessian_approximation_not_exact:{label}")
        if jacobian_approximation != "exact":
            blockers.append(f"jacobian_approximation_not_exact:{label}")
        if hessian_backend != EXACT_HESSIAN_BACKEND:
            blockers.append(f"hessian_backend_not_exact_pressure_route:{label}")
        if eval_h_calls is None or eval_h_calls <= 0:
            blockers.append(f"eval_h_calls_not_positive:{label}")
        else:
            eval_h_call_counts.append(eval_h_calls)

        pressure_ape = recomputed_errors["absolute_relative_error_percent"] if recomputed_errors is not None else None
        density_ape = (
            recomputed_errors["rho_sat_liq_absolute_relative_error_percent"] if recomputed_errors is not None else None
        )
        pressure_norm = _finite_float(row, "pressure_consistency_norm")
        chemical_potential_norm = _finite_float(row, "chemical_potential_consistency_norm")
        ln_fugacity_norm = _finite_float(row, "ln_fugacity_consistency_norm")
        phase_distance = _finite_float(row, "phase_distance")
        for field, value in (
            ("absolute_relative_error_percent", pressure_ape),
            ("rho_sat_liq_absolute_relative_error_percent", density_ape),
            ("pressure_consistency_norm", pressure_norm),
            ("chemical_potential_consistency_norm", chemical_potential_norm),
            ("ln_fugacity_consistency_norm", ln_fugacity_norm),
            ("phase_distance", phase_distance),
        ):
            if value is None:
                blockers.append(f"missing_or_nonfinite_metric:{field}:{label}")
            else:
                metric_values[field].append(value)
                if value < 0.0:
                    blockers.append(f"negative_metric:{field}:{label}")

        for field in (
            "absolute_relative_error_percent",
            "rho_sat_liq_absolute_relative_error_percent",
        ):
            stored_value = _finite_float(row, field)
            if stored_value is not None and stored_value < 0.0:
                blockers.append(f"negative_metric:{field}:{label}")

        stored_pressure_ape = _finite_float(row, "absolute_relative_error_percent")
        stored_density_ape = _finite_float(row, "rho_sat_liq_absolute_relative_error_percent")
        if pressure_ape is not None and pressure_ape > float(
            ACCEPTANCE_THRESHOLDS["max_pressure_absolute_relative_error_percent"]
        ):
            blockers.append(f"pressure_absolute_relative_error_above_threshold:{label}")
        if stored_pressure_ape is not None and stored_pressure_ape > float(
            ACCEPTANCE_THRESHOLDS["max_pressure_absolute_relative_error_percent"]
        ):
            blockers.append(f"pressure_absolute_relative_error_above_threshold:{label}")
        if density_ape is not None and density_ape > float(
            ACCEPTANCE_THRESHOLDS["max_liquid_density_absolute_relative_error_percent"]
        ):
            blockers.append(f"liquid_density_absolute_relative_error_above_threshold:{label}")
        if stored_density_ape is not None and stored_density_ape > float(
            ACCEPTANCE_THRESHOLDS["max_liquid_density_absolute_relative_error_percent"]
        ):
            blockers.append(f"liquid_density_absolute_relative_error_above_threshold:{label}")
        if pressure_norm is not None and pressure_norm > float(ACCEPTANCE_THRESHOLDS["max_pressure_consistency_norm"]):
            blockers.append(f"pressure_consistency_norm_above_threshold:{label}")
        if chemical_potential_norm is not None and chemical_potential_norm > float(
            ACCEPTANCE_THRESHOLDS["max_chemical_potential_consistency_norm"]
        ):
            blockers.append(f"chemical_potential_consistency_norm_above_threshold:{label}")
        if phase_distance is not None and phase_distance < float(ACCEPTANCE_THRESHOLDS["min_phase_distance"]):
            blockers.append(f"phase_distance_below_threshold:{label}")

    if source_grid != EXPECTED_SOURCE_GRID and "nist_source_grid_mismatch" not in blockers:
        blockers.append("nist_source_grid_mismatch")

    if require_fresh_native:
        try:
            native_freshness.require_equilibrium_native_fresh(native_freshness_receipt)
        except ValueError:
            blockers.append(
                "native_source_identity_mismatch"
                if native_freshness_receipt.get("embedded_source_identity")
                else "native_freshness_receipt_missing"
            )

    metrics: dict[str, float | None] = {
        "max_pressure_absolute_relative_error_percent": (
            max(metric_values["absolute_relative_error_percent"])
            if metric_values["absolute_relative_error_percent"]
            else None
        ),
        "max_liquid_density_absolute_relative_error_percent": (
            max(metric_values["rho_sat_liq_absolute_relative_error_percent"])
            if metric_values["rho_sat_liq_absolute_relative_error_percent"]
            else None
        ),
        "max_pressure_consistency_norm": (
            max(metric_values["pressure_consistency_norm"]) if metric_values["pressure_consistency_norm"] else None
        ),
        "max_chemical_potential_consistency_norm": (
            max(metric_values["chemical_potential_consistency_norm"])
            if metric_values["chemical_potential_consistency_norm"]
            else None
        ),
        "max_ln_fugacity_consistency_norm": (
            max(metric_values["ln_fugacity_consistency_norm"])
            if metric_values["ln_fugacity_consistency_norm"]
            else None
        ),
        "min_phase_distance": (min(metric_values["phase_distance"]) if metric_values["phase_distance"] else None),
    }
    unique_blockers = list(dict.fromkeys(blockers))
    derivative_evidence: dict[str, object] = {
        "exact_hessian_row_count": exact_hessian_row_count,
        "hessian_approximation": (
            next(iter(hessian_approximations)) if len(hessian_approximations) == 1 else "mixed_or_missing"
        ),
        "jacobian_approximation": (
            next(iter(jacobian_approximations)) if len(jacobian_approximations) == 1 else "mixed_or_missing"
        ),
        "hessian_backend": (next(iter(hessian_backends)) if len(hessian_backends) == 1 else "mixed_or_missing"),
        "min_eval_h_calls": min(eval_h_call_counts) if eval_h_call_counts else None,
    }
    return {
        "checker": "single_component_vle_nist_saturation",
        "evidence_mode": "live_solver_execution",
        "complete": not unique_blockers,
        "blockers": unique_blockers,
        "row_count": len(rows),
        "species_row_counts": dict(sorted(species_counts.items())),
        "thresholds": dict(ACCEPTANCE_THRESHOLDS),
        "metrics": metrics,
        "diagnostic_only_metrics": DIAGNOSTIC_ONLY_METRICS,
        "derivative_evidence": derivative_evidence,
        "native_freshness_receipt": native_freshness.receipt_to_jsonable(native_freshness_receipt),
    }


def run_live_validation(
    *,
    checker_command: list[str],
    require_fresh_native: bool,
) -> dict[str, Any]:
    native_core = extension_native_core()
    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=native_core,
        checker_command=checker_command,
    )
    if require_fresh_native:
        try:
            native_freshness.require_equilibrium_native_fresh(receipt)
        except ValueError:
            return evaluate_live_rows(
                [],
                native_freshness_receipt=receipt,
                require_fresh_native=True,
            )
    with runtime.suppress_native_stdout():
        rows = generate_validation_rows()
    return evaluate_live_rows(
        rows,
        native_freshness_receipt=receipt,
        require_fresh_native=require_fresh_native,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-fresh-native", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    checker_command = (
        sys.argv[:]
        if argv is None
        else [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_single_component_vle_nist_saturation.py",
            *argv,
        ]
    )
    payload = run_live_validation(
        checker_command=checker_command,
        require_fresh_native=args.require_fresh_native,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"complete={payload['complete']} blockers={','.join(payload['blockers'])}")
    if (args.require_complete or args.require_fresh_native) and not payload["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
