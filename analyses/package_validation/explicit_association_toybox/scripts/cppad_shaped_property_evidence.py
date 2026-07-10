from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Iterable, Mapping
from functools import lru_cache
from pathlib import Path

import numpy as np

from .association_case_matrix import AssociationEvidenceCase, association_evidence_cases
from .association_models import association_helmholtz, mass_action_residual
from .closure_models import PICARD7_CLOSURE, evaluate_closure
from .derivative_agreement import centered_slope
from .exact_baseline import solve_exact_site_fractions
from .propagation_evidence import relative_error, write_rows_csv

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
DEFAULT_OUTPUT = (
    ANALYSIS_ROOT
    / "figures"
    / "cppad_shaped_picard_property_evidence"
    / "output"
    / "cppad_shaped_picard_property_evidence.csv"
)
BACKEND_MODULE = "analyses.package_validation.explicit_association_toybox.scripts.cppad_shaped_jax_backend"


def run_cppad_shaped_property_evidence(
    *,
    include_jax: bool = True,
    cases: Iterable[AssociationEvidenceCase] | None = None,
) -> list[dict[str, object]]:
    case_rows = tuple(cases or association_evidence_cases())
    jax_index = _jax_property_index() if include_jax else {}
    rows: list[dict[str, object]] = []
    for case in case_rows:
        for temperature, density in zip(case.temperature_grid, case.density_grid, strict=True):
            rows.extend(_property_rows_for_state(case, temperature=temperature, density=density, jax_index=jax_index))
    return rows


def generate_cppad_shaped_property_evidence(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_cppad_shaped_property_evidence(), output_path)


def _property_rows_for_state(
    case: AssociationEvidenceCase,
    *,
    temperature: float,
    density: float,
    jax_index: Mapping[tuple[str, float], Mapping[str, object]],
) -> list[dict[str, object]]:
    exact_assoc, exact_residual, exact_iterations = _exact_association(case, density=density)
    exact_slope = _density_slope(case, density=density, exact=True)
    exact_total = _total_proxy(case, temperature=temperature, density=density, association_value=exact_assoc)
    exact_pressure = _pressure_proxy(density=density, total_ares=exact_total, density_slope=exact_slope)
    exact_fugacity = _fugacity_proxy(exact_total)

    rows = [
        _row(
            case,
            temperature=temperature,
            density=density,
            picard_backend="numpy",
            picard_assoc=_picard_numpy_association(case, density=density),
            exact_assoc=exact_assoc,
            exact_total=exact_total,
            exact_pressure=exact_pressure,
            exact_fugacity=exact_fugacity,
            exact_residual=exact_residual,
            exact_iterations=exact_iterations,
        )
    ]
    if case.system is None:
        rows.append(
            _row(
                case,
                temperature=temperature,
                density=density,
                picard_backend="jax",
                picard_assoc=0.0,
                exact_assoc=exact_assoc,
                exact_total=exact_total,
                exact_pressure=exact_pressure,
                exact_fugacity=exact_fugacity,
                exact_residual=exact_residual,
                exact_iterations=exact_iterations,
            )
        )
    else:
        key = (case.case_id, float(density))
        if key not in jax_index:
            raise RuntimeError(f"JAX property backend did not emit case_id={case.case_id} density={density}.")
        rows.append(
            _row(
                case,
                temperature=temperature,
                density=density,
                picard_backend="jax",
                picard_assoc=float(jax_index[key]["picard_jax_value"]),
                exact_assoc=exact_assoc,
                exact_total=exact_total,
                exact_pressure=exact_pressure,
                exact_fugacity=exact_fugacity,
                exact_residual=exact_residual,
                exact_iterations=exact_iterations,
            )
        )
    return rows


def _row(
    case: AssociationEvidenceCase,
    *,
    temperature: float,
    density: float,
    picard_backend: str,
    picard_assoc: float,
    exact_assoc: float,
    exact_total: float,
    exact_pressure: float,
    exact_fugacity: float,
    exact_residual: float,
    exact_iterations: int,
) -> dict[str, object]:
    picard_slope = _density_slope(case, density=density, exact=False, picard_value=picard_assoc)
    picard_total = _total_proxy(case, temperature=temperature, density=density, association_value=picard_assoc)
    picard_pressure = _pressure_proxy(density=density, total_ares=picard_total, density_slope=picard_slope)
    picard_fugacity = _fugacity_proxy(picard_total)
    residual = _picard_residual(case, density=density, picard_assoc=picard_assoc)
    return {
        "case_id": case.case_id,
        "topology_id": case.topology_id,
        "component_family": case.component_family,
        "mixture_family": case.mixture_family,
        "temperature": float(temperature),
        "density": float(density),
        "pressure": picard_pressure,
        "composition": case.composition_text(),
        "association_strength_matrix": case.strength_matrix_text(),
        "picard_backend": picard_backend,
        "picard_iteration_count": 7,
        "picard_damping": 0.5,
        "association_helmholtz_exact": exact_assoc,
        "association_helmholtz_picard": picard_assoc,
        "total_residual_helmholtz_exact": exact_total,
        "total_residual_helmholtz_picard": picard_total,
        "pressure_exact": exact_pressure,
        "pressure_picard": picard_pressure,
        "fugacity_proxy_exact": exact_fugacity,
        "fugacity_proxy_picard": picard_fugacity,
        "density_root_status": "fixed_density_grid_point",
        "mass_action_residual_norm": residual,
        "exact_mass_action_residual_norm": exact_residual,
        "exact_iteration_count": exact_iterations,
        "absolute_error": abs(picard_assoc - exact_assoc),
        "relative_error": relative_error(picard_assoc, exact_assoc),
        "source_status": case.source_status,
        "diagnostic_scope": "python_toybox_cppad_shaped_property_evidence",
    }


def _exact_association(case: AssociationEvidenceCase, *, density: float) -> tuple[float, float, int]:
    if case.system is None:
        return 0.0, 0.0, 0
    exact = solve_exact_site_fractions(
        density=density,
        x_assoc=case.system.x_assoc(case.composition),
        delta=case.delta_matrix,
    )
    return (
        association_helmholtz(exact.xa, case.composition, case.system.site_component_index),
        exact.residual_norm,
        exact.iteration_count,
    )


def _picard_numpy_association(case: AssociationEvidenceCase, *, density: float) -> float:
    if case.system is None:
        return 0.0
    closure = evaluate_closure(
        PICARD7_CLOSURE,
        system=case.system,
        density=density,
        composition=case.composition,
        delta=case.delta_matrix,
    )
    return association_helmholtz(closure.xa, case.composition, case.system.site_component_index)


def _picard_residual(case: AssociationEvidenceCase, *, density: float, picard_assoc: float) -> float:
    del picard_assoc
    if case.system is None:
        return 0.0
    closure = evaluate_closure(
        PICARD7_CLOSURE,
        system=case.system,
        density=density,
        composition=case.composition,
        delta=case.delta_matrix,
    )
    residual = mass_action_residual(
        closure.xa,
        density=density,
        x_assoc=case.system.x_assoc(case.composition),
        delta=case.delta_matrix,
    )
    return float(np.linalg.norm(residual, ord=np.inf))


def _density_slope(
    case: AssociationEvidenceCase,
    *,
    density: float,
    exact: bool,
    picard_value: float | None = None,
) -> float:
    del picard_value
    if case.system is None:
        return 0.0
    return centered_slope(
        lambda rho: _exact_association(case, density=rho)[0]
        if exact
        else _picard_numpy_association(case, density=rho),
        base_value=density,
        step_size=max(1.0e-5, density * 1.0e-3),
    )


def _total_proxy(case: AssociationEvidenceCase, *, temperature: float, density: float, association_value: float) -> float:
    neutral_context = 0.02 * case.component_count + 0.015 * case.site_count + 0.25 * density + 25.0 / temperature
    return float(neutral_context + association_value)


def _pressure_proxy(*, density: float, total_ares: float, density_slope: float) -> float:
    return float(density * (1.0 + total_ares) + density * density * density_slope)


def _fugacity_proxy(total_ares: float) -> float:
    return float(np.exp(np.clip(total_ares, -50.0, 50.0)))


@lru_cache(maxsize=1)
def _jax_property_rows() -> tuple[dict[str, object], ...]:
    completed = subprocess.run(
        ["uv", "run", "--group", "autodiff", "python", "-m", BACKEND_MODULE, "--mode", "property"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError("JAX property backend emitted no rows.")
    return tuple(json.loads(stdout))


def _jax_property_index() -> dict[tuple[str, float], Mapping[str, object]]:
    return {
        (str(row["case_id"]), float(row["density"])): row
        for row in _jax_property_rows()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CppAD-shaped Picard property evidence.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_cppad_shaped_property_evidence(args.output))


if __name__ == "__main__":
    main()
