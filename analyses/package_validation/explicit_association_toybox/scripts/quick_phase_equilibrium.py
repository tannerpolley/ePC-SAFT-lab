from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from .closure_models import EXACT_MASS_ACTION_BASELINE, PICARD7_CLOSURE
from .fixed_state_property_residuals import load_provider_cases, load_public_saturation_rows
from .toy_property_eos import (
    GAS_CONSTANT,
    N_AV,
    PACKING_FRACTION_LIMIT,
    pressure_result_from_state,
    state_from_provider_case,
)

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "quick_phase_equilibrium" / "output" / "quick_phase_equilibrium.csv"
DEFAULT_CLOSURES = (EXACT_MASS_ACTION_BASELINE, PICARD7_CLOSURE)


@dataclass(frozen=True)
class PhasePairResult:
    status: str
    vapor_density_mol_m3: float
    liquid_density_mol_m3: float
    vapor_pressure_Pa: float
    liquid_pressure_Pa: float
    vapor_reduced_mu: float
    liquid_reduced_mu: float
    pressure_residual_Pa: float
    reduced_mu_residual: float
    scaled_residual_norm: float
    initial_scaled_residual_norm: float
    iteration_count: int
    pressure_scale_Pa: float


def reduced_chemical_potential(state, case: Mapping[str, object], *, closure_name: str) -> float:
    _, ares, z_terms = pressure_result_from_state(state, case, closure_name=closure_name)
    return float(math.log(state.density) + ares + z_terms.total)


def solve_pure_phase_pair(
    case: Mapping[str, object],
    *,
    temperature: float,
    closure_name: str,
    vapor_density_seed_mol_m3: float,
    liquid_density_seed_mol_m3: float,
    pressure_scale_Pa: float,
    max_iterations: int = 18,
    tolerance: float = 1.0e-6,
) -> PhasePairResult:
    bounds = _density_bounds(case, temperature=temperature)
    vapor_seed = _clip_density(vapor_density_seed_mol_m3, bounds)
    liquid_seed = _clip_density(liquid_density_seed_mol_m3, bounds)
    if vapor_seed >= liquid_seed:
        raise ValueError("phase-pair solve requires vapor seed density below liquid seed density.")
    if pressure_scale_Pa <= 0.0 or not np.isfinite(pressure_scale_Pa):
        raise ValueError("pressure_scale_Pa must be positive and finite.")

    logs = np.log(np.array([vapor_seed, liquid_seed], dtype=float))
    initial_vector = _phase_residual_vector(
        logs,
        case,
        temperature=temperature,
        closure_name=closure_name,
        pressure_scale_Pa=pressure_scale_Pa,
    )
    initial_norm = float(np.linalg.norm(initial_vector, ord=2))
    current_norm = initial_norm
    status = "iteration_limit_phase_pair"
    iterations = 0
    for iteration in range(1, max_iterations + 1):
        vector = _phase_residual_vector(
            logs,
            case,
            temperature=temperature,
            closure_name=closure_name,
            pressure_scale_Pa=pressure_scale_Pa,
        )
        current_norm = float(np.linalg.norm(vector, ord=2))
        if current_norm <= tolerance:
            status = "converged_phase_pair"
            iterations = iteration - 1
            break
        jacobian = _finite_difference_jacobian(
            logs,
            case,
            temperature=temperature,
            closure_name=closure_name,
            pressure_scale_Pa=pressure_scale_Pa,
        )
        try:
            step = np.linalg.solve(jacobian, -vector)
        except np.linalg.LinAlgError:
            status = "singular_phase_pair_linearization"
            iterations = iteration - 1
            break
        accepted = False
        for damping in (1.0, 0.5, 0.25, 0.125, 0.0625):
            trial = logs + damping * step
            if not _valid_log_density_pair(trial, bounds):
                continue
            trial_vector = _phase_residual_vector(
                trial,
                case,
                temperature=temperature,
                closure_name=closure_name,
                pressure_scale_Pa=pressure_scale_Pa,
            )
            trial_norm = float(np.linalg.norm(trial_vector, ord=2))
            if trial_norm < current_norm:
                logs = trial
                current_norm = trial_norm
                accepted = True
                break
        iterations = iteration
        if not accepted:
            status = "phase_pair_line_search_stalled"
            break
    else:
        final_vector = _phase_residual_vector(
            logs,
            case,
            temperature=temperature,
            closure_name=closure_name,
            pressure_scale_Pa=pressure_scale_Pa,
        )
        current_norm = float(np.linalg.norm(final_vector, ord=2))
        if current_norm <= tolerance:
            status = "converged_phase_pair"

    vapor_density, liquid_density = np.exp(logs)
    residuals = _phase_residuals(
        case,
        temperature=temperature,
        closure_name=closure_name,
        vapor_density_mol_m3=float(vapor_density),
        liquid_density_mol_m3=float(liquid_density),
        pressure_scale_Pa=pressure_scale_Pa,
    )
    return PhasePairResult(
        status=status,
        vapor_density_mol_m3=float(vapor_density),
        liquid_density_mol_m3=float(liquid_density),
        vapor_pressure_Pa=residuals["vapor_pressure_Pa"],
        liquid_pressure_Pa=residuals["liquid_pressure_Pa"],
        vapor_reduced_mu=residuals["vapor_reduced_mu"],
        liquid_reduced_mu=residuals["liquid_reduced_mu"],
        pressure_residual_Pa=residuals["pressure_residual_Pa"],
        reduced_mu_residual=residuals["reduced_mu_residual"],
        scaled_residual_norm=float(
            np.linalg.norm(
                np.array(
                    [
                        residuals["pressure_residual_Pa"] / pressure_scale_Pa,
                        residuals["reduced_mu_residual"],
                    ],
                    dtype=float,
                ),
                ord=2,
            )
        ),
        initial_scaled_residual_norm=initial_norm,
        iteration_count=iterations,
        pressure_scale_Pa=pressure_scale_Pa,
    )


def quick_phase_equilibrium_rows(
    source_rows: Sequence[Mapping[str, object]] | None = None,
    *,
    provider_cases: Mapping[str, Mapping[str, object]] | None = None,
    closure_names: Sequence[str] = DEFAULT_CLOSURES,
    max_rows_per_component: int = 8,
) -> list[dict[str, object]]:
    source_rows = list(source_rows) if source_rows is not None else load_public_saturation_rows()
    provider_cases = provider_cases if provider_cases is not None else load_provider_cases()
    selected = _select_temperature_spread(source_rows, max_rows_per_component=max_rows_per_component)
    rows: list[dict[str, object]] = []
    for row in selected:
        component = str(row["component"]).lower()
        case = provider_cases.get(component)
        if case is None:
            continue
        temperature = float(row["T_K"])
        source_pressure = float(row["p_sat_Pa"])
        source_liquid_density = float(row["rho_sat_liq_mol_m3"])
        vapor_seed = max(source_pressure / (GAS_CONSTANT * temperature), 1.0e-9)
        pressure_scale = max(abs(source_pressure), 1.0e5)
        for closure_name in closure_names:
            result = solve_pure_phase_pair(
                case,
                temperature=temperature,
                closure_name=closure_name,
                vapor_density_seed_mol_m3=vapor_seed,
                liquid_density_seed_mol_m3=source_liquid_density,
                pressure_scale_Pa=pressure_scale,
            )
            rows.append(
                {
                    "component": component,
                    "T_K": temperature,
                    "closure_name": closure_name,
                    "model_label": _model_label(closure_name),
                    "source_pressure_Pa": source_pressure,
                    "source_liquid_density_mol_m3": source_liquid_density,
                    "initial_vapor_density_mol_m3": vapor_seed,
                    "initial_liquid_density_mol_m3": source_liquid_density,
                    "status": result.status,
                    "vapor_density_mol_m3": result.vapor_density_mol_m3,
                    "liquid_density_mol_m3": result.liquid_density_mol_m3,
                    "vapor_pressure_Pa": result.vapor_pressure_Pa,
                    "liquid_pressure_Pa": result.liquid_pressure_Pa,
                    "vapor_reduced_mu": result.vapor_reduced_mu,
                    "liquid_reduced_mu": result.liquid_reduced_mu,
                    "pressure_residual_Pa": result.pressure_residual_Pa,
                    "reduced_mu_residual": result.reduced_mu_residual,
                    "scaled_residual_norm": result.scaled_residual_norm,
                    "initial_scaled_residual_norm": result.initial_scaled_residual_norm,
                    "residual_reduction_factor": (
                        result.initial_scaled_residual_norm / result.scaled_residual_norm
                        if result.scaled_residual_norm > 0.0
                        else np.inf
                    ),
                    "iteration_count": result.iteration_count,
                    "pressure_scale_Pa": result.pressure_scale_Pa,
                    "diagnostic_scope": "toy_pure_phase_pair_pressure_mu_equality",
                    "message": (
                        "Toy pure-component pressure and reduced-chemical-potential equality residual; "
                        "no provider VLE or saturation claim."
                    ),
                }
            )
    if not rows:
        raise ValueError("quick phase equilibrium rows require matching associating source rows and provider cases.")
    return rows


def generate_quick_phase_equilibrium(output_path: Path = DEFAULT_OUTPUT) -> Path:
    rows = quick_phase_equilibrium_rows()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _phase_residual_vector(
    log_densities: np.ndarray,
    case: Mapping[str, object],
    *,
    temperature: float,
    closure_name: str,
    pressure_scale_Pa: float,
) -> np.ndarray:
    densities = np.exp(log_densities)
    residuals = _phase_residuals(
        case,
        temperature=temperature,
        closure_name=closure_name,
        vapor_density_mol_m3=float(densities[0]),
        liquid_density_mol_m3=float(densities[1]),
        pressure_scale_Pa=pressure_scale_Pa,
    )
    return np.array(
        [
            residuals["pressure_residual_Pa"] / pressure_scale_Pa,
            residuals["reduced_mu_residual"],
        ],
        dtype=float,
    )


def _phase_residuals(
    case: Mapping[str, object],
    *,
    temperature: float,
    closure_name: str,
    vapor_density_mol_m3: float,
    liquid_density_mol_m3: float,
    pressure_scale_Pa: float,
) -> dict[str, float]:
    del pressure_scale_Pa
    vapor_state = state_from_provider_case(case, temperature=temperature, density=vapor_density_mol_m3)
    liquid_state = state_from_provider_case(case, temperature=temperature, density=liquid_density_mol_m3)
    vapor_pressure, _, _ = pressure_result_from_state(vapor_state, case, closure_name=closure_name)
    liquid_pressure, _, _ = pressure_result_from_state(liquid_state, case, closure_name=closure_name)
    vapor_mu = reduced_chemical_potential(vapor_state, case, closure_name=closure_name)
    liquid_mu = reduced_chemical_potential(liquid_state, case, closure_name=closure_name)
    return {
        "vapor_pressure_Pa": vapor_pressure,
        "liquid_pressure_Pa": liquid_pressure,
        "vapor_reduced_mu": vapor_mu,
        "liquid_reduced_mu": liquid_mu,
        "pressure_residual_Pa": liquid_pressure - vapor_pressure,
        "reduced_mu_residual": liquid_mu - vapor_mu,
    }


def _finite_difference_jacobian(
    log_densities: np.ndarray,
    case: Mapping[str, object],
    *,
    temperature: float,
    closure_name: str,
    pressure_scale_Pa: float,
) -> np.ndarray:
    jacobian = np.zeros((2, 2), dtype=float)
    step = 1.0e-4
    for column in range(2):
        perturb = np.zeros(2, dtype=float)
        perturb[column] = step
        plus = _phase_residual_vector(
            log_densities + perturb,
            case,
            temperature=temperature,
            closure_name=closure_name,
            pressure_scale_Pa=pressure_scale_Pa,
        )
        minus = _phase_residual_vector(
            log_densities - perturb,
            case,
            temperature=temperature,
            closure_name=closure_name,
            pressure_scale_Pa=pressure_scale_Pa,
        )
        jacobian[:, column] = (plus - minus) / (2.0 * step)
    return jacobian


def _density_bounds(case: Mapping[str, object], *, temperature: float) -> tuple[float, float]:
    state = state_from_provider_case(case, temperature=temperature, density=1.0)
    coefficient = np.pi / 6.0 * np.sum(state.composition * state.segments * state.segment_diameter**3.0)
    if coefficient <= 0.0 or not np.isfinite(coefficient):
        raise ValueError("phase-pair density bounds require a positive packing coefficient.")
    upper = float(PACKING_FRACTION_LIMIT / coefficient * 1.0e30 / N_AV)
    return 1.0e-9, upper * 0.999


def _clip_density(value: float, bounds: tuple[float, float]) -> float:
    if value <= 0.0 or not np.isfinite(value):
        raise ValueError("density seed must be positive and finite.")
    return float(min(max(value, bounds[0]), bounds[1]))


def _valid_log_density_pair(logs: np.ndarray, bounds: tuple[float, float]) -> bool:
    if not np.all(np.isfinite(logs)):
        return False
    vapor_density, liquid_density = np.exp(logs)
    return bool(bounds[0] <= vapor_density < liquid_density <= bounds[1])


def _select_temperature_spread(
    source_rows: Sequence[Mapping[str, object]],
    *,
    max_rows_per_component: int,
) -> list[Mapping[str, object]]:
    if max_rows_per_component <= 0:
        raise ValueError("max_rows_per_component must be positive.")
    by_component: dict[str, list[Mapping[str, object]]] = {}
    for row in source_rows:
        by_component.setdefault(str(row["component"]).lower(), []).append(row)
    selected: list[Mapping[str, object]] = []
    for rows in by_component.values():
        ordered = sorted(rows, key=lambda item: float(item["T_K"]))
        if len(ordered) <= max_rows_per_component:
            selected.extend(ordered)
            continue
        indexes = np.linspace(0, len(ordered) - 1, max_rows_per_component)
        selected.extend(ordered[int(round(index))] for index in indexes)
    return sorted(selected, key=lambda item: (str(item["component"]).lower(), float(item["T_K"])))


def _model_label(closure_name: str) -> str:
    if closure_name == EXACT_MASS_ACTION_BASELINE:
        return "Exact implicit"
    if closure_name == PICARD7_CLOSURE:
        return "Picard"
    return closure_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate quick toy phase-equilibrium residual diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_quick_phase_equilibrium(args.output))


if __name__ == "__main__":
    main()
