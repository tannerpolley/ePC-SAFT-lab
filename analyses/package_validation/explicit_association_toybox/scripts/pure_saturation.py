from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from scipy.optimize import least_squares

from .closure_models import EXACT_MASS_ACTION_BASELINE, PICARD7_CLOSURE
from .toy_property_eos import (
    GAS_CONSTANT,
    pressure_from_state,
    solve_liquid_density_root,
    state_from_provider_case,
)


INITIAL_GUESS_POLICY = "reference_pressure_liquid_density_ideal_vapor_seed"


@dataclass(frozen=True)
class PureSaturationResult:
    closure_name: str
    model_role: str
    status: str
    T_K: float
    p_sat_Pa: float
    rho_vap_mol_m3: float
    rho_liq_mol_m3: float
    pressure_vap_residual_Pa: float
    pressure_liq_residual_Pa: float
    log_fugacity_residual: float
    solver_iteration_count: int
    pressure_evaluation_count: int
    initial_guess_policy: str
    message: str


def solve_pure_saturation(
    case: Mapping[str, object],
    *,
    temperature: float,
    closure_name: str,
    pressure_seed_Pa: float,
    liquid_density_seed_mol_m3: float,
    vapor_density_seed_mol_m3: float | None = None,
) -> PureSaturationResult:
    _validate_pure_component_case(case)
    temperature = float(temperature)
    pressure_seed = float(pressure_seed_Pa)
    liquid_seed = float(liquid_density_seed_mol_m3)
    if not (np.isfinite(temperature) and temperature > 0.0):
        raise ValueError("pure saturation solve requires a positive finite temperature.")
    if not (np.isfinite(pressure_seed) and pressure_seed > 0.0):
        raise ValueError("pure saturation solve requires a positive finite pressure seed.")
    if not (np.isfinite(liquid_seed) and liquid_seed > 0.0):
        raise ValueError("pure saturation solve requires a positive finite liquid density seed.")

    vapor_seed = _vapor_density_seed(
        pressure_seed_Pa=pressure_seed,
        temperature=temperature,
        provided_seed=vapor_density_seed_mol_m3,
    )
    if vapor_seed >= liquid_seed:
        raise ValueError("vapor density seed must be below liquid density seed.")

    liquid_root = solve_liquid_density_root(
        case,
        temperature=temperature,
        target_pressure_Pa=pressure_seed,
        closure_name=closure_name,
        density_seed_mol_m3=liquid_seed,
    )
    if liquid_root.rho_mol_m3 is None:
        raise ValueError(
            "pure saturation solve could not find a model liquid-density root at the pressure seed "
            f"(status={liquid_root.status})."
        )
    liquid_seed = float(liquid_root.rho_mol_m3)
    if vapor_seed >= liquid_seed:
        raise ValueError("vapor density seed must be below liquid density seed.")

    pressure_evaluation_count = int(liquid_root.pressure_evaluation_count)

    def phase_values(rho_mol_m3: float) -> tuple[float, float, float]:
        nonlocal pressure_evaluation_count
        state = state_from_provider_case(case, temperature=temperature, density=float(rho_mol_m3))
        pressure, ares, z_value = pressure_from_state(state, case, closure_name=closure_name)
        pressure_evaluation_count += 1
        if pressure <= 0.0 or z_value <= 0.0 or not np.all(np.isfinite([pressure, ares, z_value])):
            raise FloatingPointError("pure saturation residual reached a non-physical phase state.")
        ln_phi = float(ares + z_value - 1.0 - np.log(z_value))
        if not np.isfinite(ln_phi):
            raise FloatingPointError("pure saturation fugacity coefficient is non-finite.")
        return float(pressure), float(ares), ln_phi

    def decode(variables: np.ndarray) -> tuple[float, float, float]:
        rho_v = float(np.exp(variables[0]))
        rho_l = rho_v + float(np.exp(variables[1]))
        pressure = float(np.exp(variables[2]))
        return rho_v, rho_l, pressure

    def residuals(variables: np.ndarray) -> np.ndarray:
        rho_v, rho_l, pressure = decode(variables)
        try:
            p_v, _, ln_phi_v = phase_values(rho_v)
            p_l, _, ln_phi_l = phase_values(rho_l)
        except Exception:
            return np.asarray([1.0e6, 1.0e6, 1.0e6], dtype=float)
        pressure_scale = max(abs(pressure), 1.0)
        return np.asarray(
            [
                (p_v - pressure) / pressure_scale,
                (p_l - pressure) / pressure_scale,
                ln_phi_v - ln_phi_l,
            ],
            dtype=float,
        )

    initial = np.log(
        np.asarray(
            [
                vapor_seed,
                liquid_seed - vapor_seed,
                pressure_seed,
            ],
            dtype=float,
        )
    )
    lower = np.log(np.asarray([1.0e-12, 1.0e-12, 1.0e-6], dtype=float))
    upper_density = max(liquid_seed * 3.0, vapor_seed * 100.0, 1.0)
    upper_pressure = max(pressure_seed * 100.0, 1.0e8)
    upper = np.log(np.asarray([upper_density, upper_density, upper_pressure], dtype=float))
    result = least_squares(
        residuals,
        initial,
        bounds=(lower, upper),
        xtol=1.0e-10,
        ftol=1.0e-10,
        gtol=1.0e-10,
        max_nfev=250,
    )
    rho_v, rho_l, p_sat = decode(result.x)
    p_v, _, ln_phi_v = phase_values(rho_v)
    p_l, _, ln_phi_l = phase_values(rho_l)
    pressure_v_residual = float(p_v - p_sat)
    pressure_l_residual = float(p_l - p_sat)
    fugacity_residual = float(ln_phi_v - ln_phi_l)
    pressure_tolerance = max(abs(p_sat) * 1.0e-6, 1.0)
    if (
        not result.success
        or rho_v <= 0.0
        or rho_l <= rho_v
        or p_sat <= 0.0
        or abs(pressure_v_residual) > pressure_tolerance
        or abs(pressure_l_residual) > pressure_tolerance
        or abs(fugacity_residual) > 1.0e-6
    ):
        raise ValueError(
            "pure saturation solve failed to satisfy pressure and fugacity equality "
            f"(status={result.status}, message={result.message!s})."
        )
    return PureSaturationResult(
        closure_name=closure_name,
        model_role=_model_role(closure_name),
        status="computed_toy_pure_saturation",
        T_K=temperature,
        p_sat_Pa=float(p_sat),
        rho_vap_mol_m3=float(rho_v),
        rho_liq_mol_m3=float(rho_l),
        pressure_vap_residual_Pa=pressure_v_residual,
        pressure_liq_residual_Pa=pressure_l_residual,
        log_fugacity_residual=fugacity_residual,
        solver_iteration_count=int(result.nfev),
        pressure_evaluation_count=pressure_evaluation_count,
        initial_guess_policy=INITIAL_GUESS_POLICY,
        message="Computed from pressure equality and pure-component fugacity-coefficient equality.",
    )


def _vapor_density_seed(
    *,
    pressure_seed_Pa: float,
    temperature: float,
    provided_seed: float | None,
) -> float:
    if provided_seed is not None:
        seed = float(provided_seed)
        if not (np.isfinite(seed) and seed > 0.0):
            raise ValueError("vapor density seed must be positive and finite.")
        return seed
    return float(max(pressure_seed_Pa / (GAS_CONSTANT * temperature), 1.0e-9))


def _validate_pure_component_case(case: Mapping[str, object]) -> None:
    species = case.get("species")
    if isinstance(species, list) and len(species) != 1:
        raise ValueError("pure saturation solve only accepts one-component cases.")
    parameters = case.get("parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("pure saturation solve requires a parameters mapping.")
    m_values = parameters.get("m")
    if isinstance(m_values, list) and len(m_values) != 1:
        raise ValueError("pure saturation solve only accepts one-component parameter sets.")


def _model_role(closure_name: str) -> str:
    if closure_name == EXACT_MASS_ACTION_BASELINE:
        return "toy_pcsaft_exact_implicit_association"
    if closure_name == PICARD7_CLOSURE:
        return "toy_pcsaft_picard_association"
    return f"toy_pcsaft_{closure_name}"
