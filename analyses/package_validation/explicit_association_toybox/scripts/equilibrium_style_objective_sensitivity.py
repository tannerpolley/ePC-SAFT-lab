from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .closure_models import CANDIDATE_CLOSURES, PICARD7_CLOSURE
from .derivative_agreement import pressure_proxy_from_ares
from .propagation_evidence import (
    classify_propagated_evidence_band,
    closure_association_value,
    exact_association_value,
    load_propagation_thresholds,
    mass_residual_inf,
    relative_error,
    write_rows_csv,
)
from .topology_reductions import topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ANALYSIS_ROOT
    / "figures"
    / "equilibrium_style_objective_sensitivity"
    / "output"
    / "equilibrium_style_objective_sensitivity.csv"
)
OBJECTIVE_COORDINATES = ("density", "composition_component_0")
DEFAULT_CLOSURES = CANDIDATE_CLOSURES


def local_objective_value(*, ares_total: float, pressure_proxy: float, pressure_weight: float) -> float:
    return float(ares_total + pressure_weight * pressure_proxy)


def max_symmetric_matrix_abs_error(exact: np.ndarray, closure: np.ndarray) -> float:
    exact = np.asarray(exact, dtype=float)
    closure = np.asarray(closure, dtype=float)
    if exact.shape != closure.shape:
        raise ValueError("matrix shapes must match.")
    return float(np.max(np.abs(closure - exact)))


def run_objective_sensitivity_cases(*, closure_names: Iterable[str] = DEFAULT_CLOSURES) -> list[dict[str, object]]:
    thresholds = load_propagation_thresholds()
    samples: list[dict[str, object]] = []
    case = _objective_case()
    exact_value, exact_gradient, exact_hessian, exact_elapsed = _objective_bundle(case, exact=True, closure_name=PICARD7_CLOSURE)
    for closure_name in closure_names:
        closure_value, closure_gradient, closure_hessian, closure_elapsed = _objective_bundle(
            case,
            exact=False,
            closure_name=closure_name,
        )
        gradient_error = float(np.linalg.norm(closure_gradient - exact_gradient, ord=2))
        hessian_error = float(np.linalg.norm(closure_hessian - exact_hessian, ord="fro"))
        objective_abs_error = abs(closure_value - exact_value)
        speedup = exact_elapsed / closure_elapsed if closure_elapsed > 0.0 else np.nan
        mass_action_residual = _closure_mass_action_residual(case, closure_name=closure_name)
        evidence_band = classify_propagated_evidence_band(
            association_model="explicit_approx",
            assoc_ares_rel_error=relative_error(closure_value, exact_value),
            derivative_rel_error=gradient_error / max(float(np.linalg.norm(exact_gradient, ord=2)), 1.0e-14),
            property_rel_error=objective_abs_error / max(abs(exact_value), 1.0e-14),
            mass_action_residual_inf=mass_action_residual,
            speedup_vs_exact_implicit=speedup,
            information_loss="none",
            thresholds=thresholds,
        )
        samples.append(
            {
                "case_id": case["case_id"],
                "topology_id": "cross_binary_2b",
                "state_id": "local_density_composition_probe",
                "closure_name": closure_name,
                "objective_value_exact": exact_value,
                "objective_value_picard": closure_value,
                "objective_value_closure": closure_value,
                "objective_abs_error": objective_abs_error,
                "gradient_norm_exact": float(np.linalg.norm(exact_gradient, ord=2)),
                "gradient_norm_picard": float(np.linalg.norm(closure_gradient, ord=2)),
                "gradient_absolute_error_norm": gradient_error,
                "gradient_max_abs_error": float(np.max(np.abs(closure_gradient - exact_gradient))),
                "hessian_frobenius_exact": float(np.linalg.norm(exact_hessian, ord="fro")),
                "hessian_frobenius_picard": float(np.linalg.norm(closure_hessian, ord="fro")),
                "hessian_absolute_error_norm": hessian_error,
                "hessian_proxy_max_abs_error": max_symmetric_matrix_abs_error(exact_hessian, closure_hessian),
                "hessian_condition_indicator": float(np.linalg.cond(closure_hessian)),
                "picard_mass_action_residual_norm": mass_action_residual,
                "exact_implicit_elapsed_seconds": exact_elapsed,
                "closure_elapsed_seconds": closure_elapsed,
                "speedup_vs_exact_implicit": speedup,
                "evidence_band": evidence_band,
                "admission_status": _admission_status(evidence_band),
            }
        )
    return samples


def generate_objective_sensitivity(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_objective_sensitivity_cases(), output_path)


def _objective_bundle(case: Mapping[str, object], *, exact: bool, closure_name: str) -> tuple[float, np.ndarray, np.ndarray, float]:
    coordinates = OBJECTIVE_COORDINATES
    value, elapsed = _objective_scalar(case, exact=exact, closure_name=closure_name)
    gradient = np.array(
        [
            _centered_coordinate_slope(case, exact=exact, closure_name=closure_name, coordinate=coordinate)
            for coordinate in coordinates
        ],
        dtype=float,
    )
    hessian = np.zeros((len(coordinates), len(coordinates)), dtype=float)
    for i, first in enumerate(coordinates):
        for j, second in enumerate(coordinates):
            hessian[i, j] = _second_coordinate_slope(
                case,
                exact=exact,
                closure_name=closure_name,
                first=first,
                second=second,
            )
    return value, gradient, 0.5 * (hessian + hessian.T), elapsed


def _objective_scalar(case: Mapping[str, object], *, exact: bool, closure_name: str) -> tuple[float, float]:
    system = case["system"]
    if not hasattr(system, "site_count"):
        raise ValueError("objective case system must be an AssociationSystem.")
    density = float(case["density"])
    strength = float(case["strength"])
    composition = np.asarray(case["composition"], dtype=float)
    delta = system.delta_matrix(strength)
    if exact:
        _, ares, elapsed = exact_association_value(system=system, density=density, composition=composition, delta=delta)
    else:
        _, ares, elapsed = closure_association_value(
            closure_name,
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        )
    pressure_proxy = pressure_proxy_from_ares(density=density, ares_value=ares, density_slope=ares / max(density, 1.0e-14))
    return (
        local_objective_value(
            ares_total=float(case["ares_hc_disp"]) + ares,
            pressure_proxy=pressure_proxy,
            pressure_weight=float(case["pressure_weight"]),
        ),
        elapsed,
    )


def _closure_mass_action_residual(case: Mapping[str, object], *, closure_name: str) -> float:
    system = case["system"]
    if not hasattr(system, "site_count"):
        raise ValueError("objective case system must be an AssociationSystem.")
    density = float(case["density"])
    strength = float(case["strength"])
    composition = np.asarray(case["composition"], dtype=float)
    delta = system.delta_matrix(strength)
    closure, _, _ = closure_association_value(
        closure_name,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )
    return mass_residual_inf(
        closure,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )


def _admission_status(evidence_band: str) -> str:
    if evidence_band in {"candidate_accuracy", "exact_reference"}:
        return "passes_probe"
    if evidence_band in {"speed_only_candidate", "diagnostic_only"}:
        return "needs_more_evidence"
    return "fails_probe"


def _centered_coordinate_slope(case: Mapping[str, object], *, exact: bool, closure_name: str, coordinate: str) -> float:
    step = 1.0e-4
    minus = _perturb_case(case, coordinate, -step)
    plus = _perturb_case(case, coordinate, step)
    low, _ = _objective_scalar(minus, exact=exact, closure_name=closure_name)
    high, _ = _objective_scalar(plus, exact=exact, closure_name=closure_name)
    return float((high - low) / (2.0 * step))


def _second_coordinate_slope(
    case: Mapping[str, object],
    *,
    exact: bool,
    closure_name: str,
    first: str,
    second: str,
) -> float:
    step = 1.0e-4
    pp = _perturb_case(_perturb_case(case, first, step), second, step)
    pm = _perturb_case(_perturb_case(case, first, step), second, -step)
    mp = _perturb_case(_perturb_case(case, first, -step), second, step)
    mm = _perturb_case(_perturb_case(case, first, -step), second, -step)
    fpp, _ = _objective_scalar(pp, exact=exact, closure_name=closure_name)
    fpm, _ = _objective_scalar(pm, exact=exact, closure_name=closure_name)
    fmp, _ = _objective_scalar(mp, exact=exact, closure_name=closure_name)
    fmm, _ = _objective_scalar(mm, exact=exact, closure_name=closure_name)
    return float((fpp - fpm - fmp + fmm) / (4.0 * step * step))


def _perturb_case(case: Mapping[str, object], coordinate: str, amount: float) -> dict[str, object]:
    changed = dict(case)
    if coordinate == "density":
        changed["density"] = max(float(case["density"]) + amount, 1.0e-8)
        return changed
    if coordinate == "composition_component_0":
        x0 = float(np.asarray(case["composition"], dtype=float)[0]) + amount
        x0 = min(max(x0, 1.0e-6), 1.0 - 1.0e-6)
        changed["composition"] = np.array([x0, 1.0 - x0], dtype=float)
        return changed
    raise ValueError(f"Unknown objective coordinate: {coordinate}")


def _objective_case() -> dict[str, object]:
    system = topology_system("2B")
    return {
        "case_id": "local_objective_cross_binary_proxy",
        "system": type(system)(
            component_count=2,
            site_component_index=np.array([0, 1], dtype=int),
            site_kind=("D", "A"),
            active_pairs=((0, 1), (1, 0)),
        ),
        "density": 0.05,
        "strength": 10.0,
        "composition": np.array([0.35, 0.65], dtype=float),
        "ares_hc_disp": -0.15,
        "pressure_weight": 0.01,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local objective sensitivity diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_objective_sensitivity(args.output))


if __name__ == "__main__":
    main()
