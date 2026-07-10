from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.equilibrium_style_objective_sensitivity import (
        run_objective_sensitivity_cases,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import relative_error
else:
    from .equilibrium_style_objective_sensitivity import run_objective_sensitivity_cases
    from .propagation_evidence import relative_error


def run_picard_stress_objective_rows() -> list[dict[str, object]]:
    return [_objective_row(row) for row in run_objective_sensitivity_cases()]


def _objective_row(row: Mapping[str, object]) -> dict[str, object]:
    gradient_error = float(row["gradient_absolute_error_norm"])
    gradient_norm = float(row["gradient_norm_exact"])
    hessian_error = float(row["hessian_absolute_error_norm"])
    hessian_norm = float(row["hessian_frobenius_exact"])
    objective_relative_error = relative_error(float(row["objective_value_picard"]), float(row["objective_value_exact"]))
    gradient_relative_error = gradient_error / max(gradient_norm, 1.0e-14)
    hessian_relative_error = hessian_error / max(hessian_norm, 1.0e-14)
    return {
        "probe_scope": "m8_fixed_state_objective_probe",
        "case_id": row["case_id"],
        "closure_name": row["closure_name"],
        "objective_value_exact": row["objective_value_exact"],
        "objective_value_picard": row["objective_value_picard"],
        "objective_relative_error": objective_relative_error,
        "gradient_relative_error": gradient_relative_error,
        "hessian_relative_error": hessian_relative_error,
        "local_step_direction_agreement": _direction_agreement(gradient_relative_error),
        "hessian_conditioning_indicator": row["hessian_condition_indicator"],
        "objective_admission_status": _objective_status(row, objective_relative_error, gradient_relative_error, hessian_relative_error),
        "exact_implicit_elapsed_seconds": row["exact_implicit_elapsed_seconds"],
        "picard_elapsed_seconds": row["closure_elapsed_seconds"],
        "simulation_speedup_vs_exact": row["speedup_vs_exact_implicit"],
    }


def _direction_agreement(gradient_relative_error: float) -> str:
    if not np.isfinite(gradient_relative_error):
        return "changed"
    return "aligned" if gradient_relative_error <= 0.25 else "changed"


def _objective_status(
    row: Mapping[str, object],
    objective_relative_error: float,
    gradient_relative_error: float,
    hessian_relative_error: float,
) -> str:
    if str(row["admission_status"]) == "fails_probe":
        return "reject_for_objective_use"
    if max(objective_relative_error, gradient_relative_error, hessian_relative_error) <= 1.0e-3:
        return "passes_objective_stress"
    if float(row["speedup_vs_exact_implicit"]) > 1.0:
        return "research_only_objective_stress"
    return "reject_for_objective_use"
