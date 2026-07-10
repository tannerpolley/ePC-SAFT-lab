from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.hessian_agreement import (
        run_hessian_agreement_cases,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.jax_picard_derivatives import (
        run_jax_picard_derivative_cases,
    )
else:
    from .hessian_agreement import run_hessian_agreement_cases
    from .jax_picard_derivatives import run_jax_picard_derivative_cases


def run_picard_stress_derivative_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    first_order = run_jax_picard_derivative_cases()
    rows.extend(_first_order_row(row) for row in first_order)
    rows.extend(_second_order_row(row) for row in run_hessian_agreement_cases(jax_rows=first_order))
    return rows


def _first_order_row(row: Mapping[str, object]) -> dict[str, object]:
    target = str(row["target"])
    return {
        "stress_evidence_role": _role_for_target(target),
        "case_id": row["case_id"],
        "closure_name": row["closure_name"],
        "target": target,
        "target_pair": target,
        "derivative_order": int(row["derivative_order"]),
        "exact_implicit_value": row["exact_implicit_value"],
        "picard_jax_value": row["picard_jax_value"],
        "absolute_error": row["abs_error"],
        "relative_error": row["rel_error"],
        "autodiff_backend": row["autodiff_backend"],
        "baseline_status": row["baseline_status"],
        "implicit_jacobian_condition_number": row["implicit_jacobian_condition_number"],
        "mass_action_residual_inf": row["mass_action_residual_inf"],
    }


def _second_order_row(row: Mapping[str, object]) -> dict[str, object]:
    target = str(row["target"])
    return {
        "stress_evidence_role": _role_for_target(target),
        "case_id": row["case_id"],
        "closure_name": row["closure_name"],
        "target": target,
        "target_pair": row["target_pair"],
        "derivative_order": int(row["derivative_order"]),
        "exact_implicit_value": row["exact_hessian_value"],
        "picard_jax_value": row["picard_jax_hessian_value"],
        "absolute_error": row["absolute_error"],
        "relative_error": row["relative_error"],
        "autodiff_backend": row["autodiff_backend"],
        "baseline_status": row["baseline_status"],
        "implicit_jacobian_condition_number": row["implicit_jacobian_condition_number"],
        "mass_action_residual_inf": row["mass_action_residual_inf"],
    }


def _role_for_target(target: str) -> str:
    if "composition" in target:
        return "composition_jacobian_hessian_stress"
    if "strength" in target:
        return "association_strength_jacobian_hessian_stress"
    if "density" in target:
        return "density_jacobian_hessian_stress"
    if "temperature" in target:
        return "temperature_jacobian_hessian_stress"
    return "local_derivative_stress"
