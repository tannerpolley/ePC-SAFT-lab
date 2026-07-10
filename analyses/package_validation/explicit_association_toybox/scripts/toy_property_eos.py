from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from .association_models import AssociationSystem, association_helmholtz
from .closure_models import EXACT_MASS_ACTION_BASELINE, PICARD7_CLOSURE, evaluate_closure
from .dispersion import ares_disp, dispersion_polynomials, mixed_dispersion_moments
from .exact_baseline import solve_exact_site_fractions
from .hard_chain import ares_hc, hard_chain_state
from .pcsaft_inputs import N_AV, ToyPCSAFTState

GAS_CONSTANT = 8.31446261815324
PACKING_FRACTION_LIMIT = 0.7405 - 1.0e-4


@dataclass(frozen=True)
class DensityRootResult:
    rho_mol_m3: float | None
    status: str
    residual_Pa: float | None
    bracket_count: int
    initial_guess_mol_m3: float
    initial_guess_policy: str
    bracket_policy: str
    pressure_evaluation_count: int


@dataclass(frozen=True)
class CompressibilityTerms:
    ideal: float
    hard_chain: float
    dispersion: float
    association: float
    total: float


@dataclass(frozen=True)
class ToyPropertyResult:
    pressure_at_density_Pa: float
    density_root: DensityRootResult
    ares_at_density: float
    z_at_density: float
    z_terms: CompressibilityTerms
    closure_name: str
    model_role: str


def evaluate_toy_property_coupling(
    case: Mapping[str, object],
    row: Mapping[str, object],
    *,
    closure_name: str,
) -> ToyPropertyResult:
    temperature = float(row["T_K"])
    density = float(row["rho_sat_liq_mol_m3"])
    pressure = float(row["p_sat_Pa"])
    state = state_from_provider_case(case, temperature=temperature, density=density)
    pressure_at_density, ares_at_density, z_terms = pressure_result_from_state(
        state,
        case,
        closure_name=closure_name,
    )
    root = solve_liquid_density_root(
        case,
        temperature=temperature,
        target_pressure_Pa=pressure,
        closure_name=closure_name,
        density_seed_mol_m3=density,
    )
    return ToyPropertyResult(
        pressure_at_density_Pa=pressure_at_density,
        density_root=root,
        ares_at_density=ares_at_density,
        z_at_density=z_terms.total,
        z_terms=z_terms,
        closure_name=closure_name,
        model_role=_model_role(closure_name),
    )


def pressure_result_from_state(
    state: ToyPCSAFTState,
    case: Mapping[str, object],
    *,
    closure_name: str,
) -> tuple[float, float, CompressibilityTerms]:
    ares_value = residual_helmholtz(state, case, closure_name=closure_name)
    z_terms = compressibility_terms(state, case, closure_name=closure_name)
    pressure = state.density * GAS_CONSTANT * state.temperature * z_terms.total
    if not np.isfinite(pressure):
        raise ValueError("toy pressure coupling produced a non-finite pressure.")
    return float(pressure), float(ares_value), z_terms


def pressure_from_state(
    state: ToyPCSAFTState,
    case: Mapping[str, object],
    *,
    closure_name: str,
) -> tuple[float, float, float]:
    pressure, ares_value, z_terms = pressure_result_from_state(state, case, closure_name=closure_name)
    return pressure, ares_value, z_terms.total


def compressibility_terms(
    state: ToyPCSAFTState,
    case: Mapping[str, object],
    *,
    closure_name: str,
) -> CompressibilityTerms:
    hc = hard_chain_state(state)
    z_hc = hard_chain_z(state, hc)
    z_disp = dispersion_z(state, hc)
    z_assoc = association_z(state, case, closure_name=closure_name)
    total = 1.0 + z_hc + z_disp + z_assoc
    if not np.isfinite(total):
        raise ValueError("toy compressibility calculation produced a non-finite Z.")
    return CompressibilityTerms(
        ideal=1.0,
        hard_chain=float(z_hc),
        dispersion=float(z_disp),
        association=float(z_assoc),
        total=float(total),
    )


def hard_chain_z(state: ToyPCSAFTState, hc) -> float:
    z0, z1, z2, z3 = hc.zeta
    one_minus_eta = 1.0 - z3
    z_hs = (
        z3 / one_minus_eta
        + 3.0 * z1 * z2 / z0 / one_minus_eta**2.0
        + (3.0 * z2**3.0 - z3 * z2**3.0) / z0 / one_minus_eta**3.0
    )
    d = state.segment_diameter
    denghs = np.zeros_like(hc.ghs)
    for i in range(state.component_count):
        for j in range(state.component_count):
            pair_diameter = d[i] * d[j] / (d[i] + d[j])
            denghs[i, j] = (
                z3 / one_minus_eta**2.0
                + pair_diameter
                * (
                    3.0 * z2 / one_minus_eta**2.0
                    + 6.0 * z2 * z3 / one_minus_eta**3.0
                )
                + pair_diameter**2.0
                * (
                    4.0 * z2**2.0 / one_minus_eta**3.0
                    + 6.0 * z2**2.0 * z3 / one_minus_eta**4.0
                )
            )
    chain_sum = float(
        np.sum(
            state.composition
            * (state.segments - 1.0)
            / np.diag(hc.ghs)
            * np.diag(denghs)
        )
    )
    return float(state.m_bar * z_hs - chain_sum)


def dispersion_z(state: ToyPCSAFTState, hc) -> float:
    polynomials = dispersion_polynomials(m_bar=state.m_bar, eta=hc.eta)
    moments = mixed_dispersion_moments(state)
    powers = hc.eta ** np.arange(7, dtype=float)
    derivative_powers = (np.arange(7, dtype=float) + 1.0) * powers
    d_eta_i1_d_eta = float(np.dot(polynomials.a, derivative_powers))
    d_eta_i2_d_eta = float(np.dot(polynomials.b, derivative_powers))
    eta = hc.eta
    m_bar = state.m_bar
    c2 = -polynomials.c1**2.0 * (
        m_bar * (-4.0 * eta**2.0 + 20.0 * eta + 8.0) / (1.0 - eta) ** 5.0
        + (1.0 - m_bar)
        * (2.0 * eta**3.0 + 12.0 * eta**2.0 - 48.0 * eta + 40.0)
        / ((1.0 - eta) * (2.0 - eta)) ** 3.0
    )
    return float(
        -2.0 * np.pi * state.number_density * d_eta_i1_d_eta * moments.m2epssigma3
        - np.pi
        * state.number_density
        * m_bar
        * (polynomials.c1 * d_eta_i2_d_eta + c2 * eta * polynomials.i2)
        * moments.m2eps2sigma3
    )


def association_z(state: ToyPCSAFTState, case: Mapping[str, object], *, closure_name: str) -> float:
    if association_system_from_case(case) is None:
        return 0.0
    return float(
        state.density
        * density_derivative(
            lambda rho: association_ares(
                _state_like(state, density=float(rho)),
                case,
                closure_name=closure_name,
            ),
            state.density,
        )
    )


def residual_helmholtz(state: ToyPCSAFTState, case: Mapping[str, object], *, closure_name: str) -> float:
    hc = hard_chain_state(state)
    assoc = association_ares(state, case, closure_name=closure_name)
    return float(ares_hc(state, hc) + ares_disp(state, hc, mixed_dispersion_moments(state)) + assoc)


def association_ares(state: ToyPCSAFTState, case: Mapping[str, object], *, closure_name: str) -> float:
    system = association_system_from_case(case)
    if system is None:
        return 0.0
    composition = state.composition
    delta = association_delta_matrix(state, case, system)
    density = state.number_density
    x_assoc = system.x_assoc(composition)
    if closure_name == EXACT_MASS_ACTION_BASELINE:
        exact = solve_exact_site_fractions(density=density, x_assoc=x_assoc, delta=delta)
        xa = exact.xa
    else:
        xa = evaluate_closure(
            closure_name,
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        ).xa
    return association_helmholtz(xa, composition, system.site_component_index)


def association_delta_matrix(
    state: ToyPCSAFTState,
    case: Mapping[str, object],
    system: AssociationSystem,
) -> np.ndarray:
    parameters = _parameters(case)
    e_assoc = _vector_parameter(parameters, "e_assoc", state.component_count)
    vol_a = _vector_parameter(parameters, "vol_a", state.component_count)
    k_hb = _matrix_parameter(parameters, "k_hb", state.component_count, default=0.0)

    hc = hard_chain_state(state)
    sigma_ij = 0.5 * (state.sigma[:, np.newaxis] + state.sigma[np.newaxis, :])
    delta = np.zeros((system.site_count, system.site_count), dtype=float)
    for site_i, site_j in system.active_pairs:
        comp_i = int(system.site_component_index[site_i])
        comp_j = int(system.site_component_index[site_j])
        if vol_a[comp_i] <= 0.0 or vol_a[comp_j] <= 0.0:
            continue
        association_volume = float(np.sqrt(vol_a[comp_i] * vol_a[comp_j]))
        pure_pair_scale = (
            np.sqrt(sigma_ij[comp_i, comp_i] * sigma_ij[comp_j, comp_j])
            / (0.5 * (sigma_ij[comp_i, comp_i] + sigma_ij[comp_j, comp_j]))
        ) ** 3.0
        association_volume *= pure_pair_scale * (1.0 - float(k_hb[comp_i, comp_j]))
        energy = 0.5 * (e_assoc[comp_i] + e_assoc[comp_j])
        delta[site_i, site_j] = (
            hc.ghs[comp_i, comp_j]
            * (np.exp(energy / state.temperature) - 1.0)
            * sigma_ij[comp_i, comp_j] ** 3.0
            * association_volume
        )
    return delta


def association_system_from_case(case: Mapping[str, object]) -> AssociationSystem | None:
    parameters = _parameters(case)
    component_count = _component_count(case)
    schemes = parameters.get("assoc_scheme", [])
    scheme_values = schemes if isinstance(schemes, list) else [schemes]
    if not scheme_values or all(_scheme_token(value) in {"NONE", ""} for value in scheme_values):
        return None
    if len(scheme_values) != component_count:
        raise ValueError("assoc_scheme length must match the toy PC-SAFT component count.")

    site_component_index: list[int] = []
    site_kind: list[str] = []
    for component_index, raw_scheme in enumerate(scheme_values):
        token = _scheme_token(raw_scheme)
        if token in {"NONE", ""}:
            continue
        if token == "2B":
            site_component_index.extend([component_index, component_index])
            site_kind.extend(["D", "A"])
            continue
        if token == "1":
            site_component_index.append(component_index)
            site_kind.append("S")
            continue
        raise ValueError(f"toy property coupling does not support assoc_scheme={raw_scheme!r}.")
    if not site_component_index:
        return None
    active_pairs = tuple(
        (i, j)
        for i, kind_i in enumerate(site_kind)
        for j, kind_j in enumerate(site_kind)
        if _active_association_pair(kind_i, kind_j)
    )
    if not active_pairs:
        raise ValueError("association scheme produced no active association site pairs.")
    return AssociationSystem(
        component_count=component_count,
        site_component_index=np.asarray(site_component_index, dtype=int),
        site_kind=tuple(site_kind),
        active_pairs=active_pairs,
    )


def solve_liquid_density_root(
    case: Mapping[str, object],
    *,
    temperature: float,
    target_pressure_Pa: float,
    closure_name: str,
    density_seed_mol_m3: float,
) -> DensityRootResult:
    initial_guess = liquid_density_initial_guess(case, temperature=temperature)
    initial_guess_policy = "legacy_pcsaft_liquid_eta_0_5"
    evaluation_count = 0
    residual_cache: dict[float, float] = {}

    def residual_at(density: float) -> float | None:
        nonlocal evaluation_count
        key = float(density)
        if key in residual_cache:
            return residual_cache[key]
        try:
            residual = _pressure_residual(case, temperature, target_pressure_Pa, closure_name, key)
        except Exception:
            return None
        if not np.isfinite(residual):
            return None
        residual_cache[key] = float(residual)
        evaluation_count += 1
        return float(residual)

    bracket, bracket_policy, bracket_count = _local_density_bracket(
        case,
        temperature=temperature,
        density_seed_mol_m3=density_seed_mol_m3,
        initial_guess_mol_m3=initial_guess,
        residual_at=residual_at,
    )
    if bracket is None:
        grid = _density_scan_grid(
            case,
            temperature=temperature,
            density_seed_mol_m3=density_seed_mol_m3,
            initial_guess_mol_m3=initial_guess,
        )
        points: list[tuple[float, float]] = []
        for density in grid:
            residual = residual_at(float(density))
            if residual is not None:
                points.append((float(density), residual))
        brackets = _sign_change_brackets(points)
        bracket_count = len(brackets)
        bracket_policy = "coarse_density_scan"
        bracket = brackets[-1] if brackets else None
    else:
        brackets = [bracket]
    if not brackets:
        return DensityRootResult(
            rho_mol_m3=None,
            status="no_pressure_root_bracket",
            residual_Pa=None,
            bracket_count=0,
            initial_guess_mol_m3=initial_guess,
            initial_guess_policy=initial_guess_policy,
            bracket_policy=bracket_policy,
            pressure_evaluation_count=evaluation_count,
        )
    lo, hi = bracket
    rho, residual = _bisect_density_root(residual_at, lo, hi, target_pressure_Pa)
    return DensityRootResult(
        rho_mol_m3=rho,
        status="computed_toy_liquid_density_root",
        residual_Pa=residual,
        bracket_count=len(brackets),
        initial_guess_mol_m3=initial_guess,
        initial_guess_policy=initial_guess_policy,
        bracket_policy=bracket_policy,
        pressure_evaluation_count=evaluation_count,
    )


def liquid_density_initial_guess(case: Mapping[str, object], *, temperature: float) -> float:
    state = state_from_provider_case(case, temperature=temperature, density=1.0)
    eta_guess = 0.5
    denominator = float(np.sum(state.composition * state.segments * state.segment_diameter**3.0))
    if denominator <= 0.0 or not np.isfinite(denominator):
        raise ValueError("liquid density initial guess requires a positive segment-volume denominator.")
    number_density = 6.0 / np.pi * eta_guess / denominator
    return float(number_density * 1.0e30 / N_AV)


def density_derivative(function, density: float) -> float:
    step = max(abs(density) * 1.0e-4, 1.0e-3)
    lo = max(density - step, density * 0.5)
    hi = density + step
    if hi <= lo:
        raise ValueError("density derivative requires an ordered finite-difference stencil.")
    return float((function(hi) - function(lo)) / (hi - lo))


def _bisect_density_root(
    residual_at,
    lo: float,
    hi: float,
    target_pressure_Pa: float,
) -> tuple[float, float]:
    f_lo = residual_at(lo)
    f_hi = residual_at(hi)
    if f_lo is None or f_hi is None:
        raise ValueError("density bisection requires finite endpoint residuals.")
    if f_lo == 0.0:
        return lo, f_lo
    if f_hi == 0.0:
        return hi, f_hi
    if f_lo * f_hi > 0.0:
        raise ValueError("density bisection requires a sign-changing bracket.")
    mid = 0.5 * (lo + hi)
    f_mid = residual_at(mid)
    if f_mid is None:
        raise ValueError("density bisection requires finite midpoint residuals.")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        f_mid = residual_at(mid)
        if f_mid is None:
            raise ValueError("density bisection produced a non-finite midpoint residual.")
        if abs(f_mid) <= max(1.0e-4, abs(target_pressure_Pa) * 1.0e-8):
            return mid, f_mid
        if f_lo * f_mid <= 0.0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid
        if abs(hi - lo) <= max(1.0e-8, mid * 1.0e-10):
            break
    return mid, f_mid


def _pressure_residual(
    case: Mapping[str, object],
    temperature: float,
    target_pressure_Pa: float,
    closure_name: str,
    density: float,
) -> float:
    pressure, _, _ = pressure_from_state(
        state_from_provider_case(case, temperature=temperature, density=density),
        case,
        closure_name=closure_name,
    )
    return float(pressure - target_pressure_Pa)


def _sign_change_brackets(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    brackets: list[tuple[float, float]] = []
    for (rho_lo, f_lo), (rho_hi, f_hi) in zip(points, points[1:], strict=False):
        if f_lo == 0.0:
            brackets.append((rho_lo, rho_lo))
        elif f_lo * f_hi < 0.0:
            brackets.append((rho_lo, rho_hi))
    return brackets


def _local_density_bracket(
    case: Mapping[str, object],
    *,
    temperature: float,
    density_seed_mol_m3: float,
    initial_guess_mol_m3: float,
    residual_at,
) -> tuple[tuple[float, float] | None, str, int]:
    rho_min = 1.0e-12
    rho_max = _density_upper_bound(case, temperature=temperature, density_seed_mol_m3=density_seed_mol_m3)
    centers = (
        ("experimental_density_center", density_seed_mol_m3),
        ("legacy_eta_guess_center", initial_guess_mol_m3),
    )
    factors = ((0.98, 1.02), (0.9, 1.1), (0.75, 1.25), (0.5, 1.5), (0.2, 2.0))
    attempted = 0
    for center_name, center in centers:
        if not (np.isfinite(center) and center > 0.0):
            continue
        center_residual = residual_at(center)
        attempted += 1
        if center_residual == 0.0:
            return (center, center), f"{center_name}_exact", attempted
        for lo_factor, hi_factor in factors:
            lo = max(rho_min, center * lo_factor)
            hi = min(rho_max, center * hi_factor)
            if not (lo < hi):
                continue
            f_lo = residual_at(lo)
            f_hi = residual_at(hi)
            attempted += 2
            if f_lo is None or f_hi is None:
                continue
            if f_lo == 0.0:
                return (lo, lo), f"{center_name}_local", attempted
            if f_hi == 0.0:
                return (hi, hi), f"{center_name}_local", attempted
            if f_lo * f_hi < 0.0:
                return (lo, hi), f"{center_name}_local", attempted
    return None, "local_bracket_failed", attempted


def _density_scan_grid(
    case: Mapping[str, object],
    *,
    temperature: float,
    density_seed_mol_m3: float,
    initial_guess_mol_m3: float,
) -> np.ndarray:
    rho_max = _density_upper_bound(case, temperature=temperature, density_seed_mol_m3=density_seed_mol_m3)
    center = max(density_seed_mol_m3, initial_guess_mol_m3)
    upper = max(min(rho_max * 0.999, center * 1.5), density_seed_mol_m3 * 1.05)
    lower = max(min(density_seed_mol_m3 * 1.0e-4, 1.0e-6), 1.0e-12)
    log_grid = np.geomspace(lower, max(lower * 10.0, min(upper, density_seed_mol_m3 * 0.2)), 48)
    linear_grid = np.linspace(max(log_grid[-1], lower), upper, 96)
    grid = np.unique(np.concatenate([log_grid, linear_grid, np.array([density_seed_mol_m3, initial_guess_mol_m3])]))
    return grid[(grid > 0.0) & np.isfinite(grid)]


def _density_upper_bound(
    case: Mapping[str, object],
    *,
    temperature: float,
    density_seed_mol_m3: float,
) -> float:
    seed_state = state_from_provider_case(case, temperature=temperature, density=max(density_seed_mol_m3, 1.0))
    coefficient = np.pi / 6.0 * np.sum(
        seed_state.composition * seed_state.segments * seed_state.segment_diameter**3.0
    )
    if coefficient <= 0.0 or not np.isfinite(coefficient):
        raise ValueError("density upper bound requires a positive packing coefficient.")
    return float(PACKING_FRACTION_LIMIT / coefficient * 1.0e30 / N_AV)


def state_from_provider_case(
    case: Mapping[str, object],
    *,
    temperature: float,
    density: float,
    composition: np.ndarray | None = None,
) -> ToyPCSAFTState:
    parameters = _parameters(case)
    component_count = _component_count(case)
    composition_vector = _composition(case, component_count=component_count, composition=composition)
    return ToyPCSAFTState(
        temperature=temperature,
        density=density,
        composition=composition_vector,
        segments=_vector_parameter(parameters, "m", component_count),
        sigma=_vector_parameter(parameters, "s", component_count),
        epsilon_over_k=_vector_parameter(parameters, "e", component_count),
        k_ij=_matrix_parameter(parameters, "k_ij", component_count, default=0.0),
    )


def _state_like(state: ToyPCSAFTState, *, density: float) -> ToyPCSAFTState:
    return ToyPCSAFTState(
        temperature=state.temperature,
        density=density,
        composition=state.composition.copy(),
        segments=state.segments.copy(),
        sigma=state.sigma.copy(),
        epsilon_over_k=state.epsilon_over_k.copy(),
        k_ij=state.k_ij.copy(),
    )


def _parameters(case: Mapping[str, object]) -> Mapping[str, object]:
    raw = case.get("parameters")
    if not isinstance(raw, Mapping):
        raise ValueError("toy property coupling requires a parameters mapping.")
    return raw


def _component_count(case: Mapping[str, object]) -> int:
    parameters = _parameters(case)
    species = case.get("species")
    if isinstance(species, list) and species:
        return len(species)
    m_values = parameters.get("m")
    if isinstance(m_values, list) and m_values:
        return len(m_values)
    return 1


def _composition(
    case: Mapping[str, object],
    *,
    component_count: int,
    composition: np.ndarray | None,
) -> np.ndarray:
    if composition is not None:
        return np.asarray(composition, dtype=float)
    raw = case.get("composition", case.get("x"))
    if raw is not None:
        return np.asarray(raw, dtype=float)
    if component_count == 1:
        return np.ones(1, dtype=float)
    raise ValueError("mixture toy PC-SAFT cases require an explicit composition vector.")


def _matrix_parameter(
    parameters: Mapping[str, object],
    key: str,
    expected_size: int,
    *,
    default: float,
) -> np.ndarray:
    raw = parameters.get(key)
    if raw is None:
        return np.full((expected_size, expected_size), default, dtype=float)
    array = np.asarray(raw, dtype=float)
    if array.size == expected_size * expected_size:
        array = array.reshape((expected_size, expected_size))
    if array.shape != (expected_size, expected_size):
        raise ValueError(f"{key} must be a square component-pair matrix.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{key} must contain finite values.")
    return array


def _scheme_token(value: object) -> str:
    if value is None:
        return "NONE"
    return str(value).strip().upper()


def _active_association_pair(kind_i: str, kind_j: str) -> bool:
    if kind_i == "D" and kind_j == "A":
        return True
    if kind_i == "A" and kind_j == "D":
        return True
    return kind_i == "S" and kind_j == "S"


def _vector_parameter(parameters: Mapping[str, object], key: str, expected_size: int) -> np.ndarray:
    raw = parameters[key]
    values = raw if isinstance(raw, list) else [raw]
    array = np.asarray(values, dtype=float)
    if array.shape != (expected_size,):
        raise ValueError(f"{key} must contain {expected_size} value(s).")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{key} must contain finite values.")
    return array


def _model_role(closure_name: str) -> str:
    if closure_name == EXACT_MASS_ACTION_BASELINE:
        return "toy_pcsaft_exact_implicit_association"
    if closure_name == PICARD7_CLOSURE:
        return "toy_pcsaft_picard_association"
    return f"toy_pcsaft_{closure_name}"
