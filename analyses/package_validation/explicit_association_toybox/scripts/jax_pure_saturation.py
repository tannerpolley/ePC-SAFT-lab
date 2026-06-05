from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib.util import find_spec
from typing import Mapping

import jax
import jax.numpy as jnp
import numpy as np
from scipy.optimize import least_squares

from .closure_models import PICARD7_CLOSURE
from .pcsaft_inputs import N_AV
from .pure_saturation import INITIAL_GUESS_POLICY, _vapor_density_seed
from .toy_property_eos import (
    GAS_CONSTANT,
    solve_liquid_density_root,
)

jax.config.update("jax_enable_x64", True)

JAX_SCIPY_BACKEND = "jax_scipy_least_squares_exact_jacobian"
PYTHON_IPOPT_BACKEND = "python_ipopt_cyipopt"
JAX_AUTODIFF_BACKEND = "jax"


@dataclass(frozen=True)
class PythonIpoptStatus:
    status: str
    message: str


@dataclass(frozen=True)
class JaxPureSaturationResult:
    closure_name: str
    model_role: str
    status: str
    optimizer_backend: str
    autodiff_backend: str
    T_K: float
    p_sat_Pa: float
    rho_vap_mol_m3: float
    rho_liq_mol_m3: float
    pressure_vap_residual_Pa: float
    pressure_liq_residual_Pa: float
    log_fugacity_residual: float
    objective_value: float
    residual_norm: float
    residual_jacobian_condition_number: float
    objective_gradient_norm: float
    objective_hessian_min_eigenvalue: float
    objective_hessian_max_eigenvalue: float
    solver_iteration_count: int
    objective_evaluation_count: int
    initial_guess_policy: str
    python_ipopt_status: str
    python_ipopt_message: str
    message: str


@dataclass(frozen=True)
class PureJaxParameters:
    m: float
    sigma: float
    epsilon_over_k: float
    e_assoc: float
    vol_a: float
    k_hb: float


def python_ipopt_availability() -> PythonIpoptStatus:
    if find_spec("cyipopt") is None:
        return PythonIpoptStatus(
            status="python_ipopt_missing",
            message="cyipopt is not importable in this environment.",
        )
    try:
        import cyipopt  # noqa: F401
    except Exception as exc:
        return PythonIpoptStatus(
            status="python_ipopt_missing",
            message=f"cyipopt import failed: {exc}",
        )
    return PythonIpoptStatus(status="python_ipopt_available", message="cyipopt imported successfully.")


def solve_jax_picard_pure_saturation(
    case: Mapping[str, object],
    *,
    temperature: float,
    pressure_seed_Pa: float,
    liquid_density_seed_mol_m3: float,
    vapor_density_seed_mol_m3: float | None = None,
) -> JaxPureSaturationResult:
    temperature = float(temperature)
    pressure_seed = float(pressure_seed_Pa)
    liquid_seed = float(liquid_density_seed_mol_m3)
    parameters = pure_jax_parameters_from_case(case)
    if not (np.isfinite(temperature) and temperature > 0.0):
        raise ValueError("JAX pure saturation solve requires a positive finite temperature.")
    if not (np.isfinite(pressure_seed) and pressure_seed > 0.0):
        raise ValueError("JAX pure saturation solve requires a positive finite pressure seed.")
    if not (np.isfinite(liquid_seed) and liquid_seed > 0.0):
        raise ValueError("JAX pure saturation solve requires a positive finite liquid density seed.")

    vapor_seed = _vapor_density_seed(
        pressure_seed_Pa=pressure_seed,
        temperature=temperature,
        provided_seed=vapor_density_seed_mol_m3,
    )
    if vapor_seed >= liquid_seed:
        raise ValueError("JAX vapor density seed must be below liquid density seed.")
    liquid_root = solve_liquid_density_root(
        case,
        temperature=temperature,
        target_pressure_Pa=pressure_seed,
        closure_name=PICARD7_CLOSURE,
        density_seed_mol_m3=liquid_seed,
    )
    if liquid_root.rho_mol_m3 is None:
        raise ValueError(
            "JAX pure saturation solve could not find a Picard liquid-density root at the pressure seed "
            f"(status={liquid_root.status})."
        )
    liquid_seed = float(liquid_root.rho_mol_m3)
    if vapor_seed >= liquid_seed:
        raise ValueError("JAX vapor density seed must be below liquid density seed.")

    initial = np.log(np.asarray([vapor_seed, liquid_seed - vapor_seed, pressure_seed], dtype=float))
    residual_function, objective_function, jacobian_function, gradient_function, hessian_function = (
        jax_pure_saturation_functions(parameters=parameters, temperature=temperature)
    )

    def residual(values: np.ndarray) -> np.ndarray:
        return np.asarray(residual_function(jnp.asarray(values, dtype=jnp.float64)), dtype=float)

    def jacobian(values: np.ndarray) -> np.ndarray:
        return np.asarray(jacobian_function(jnp.asarray(values, dtype=jnp.float64)), dtype=float)

    result = least_squares(
        residual,
        initial,
        jac=jacobian,
        xtol=1.0e-10,
        ftol=1.0e-10,
        gtol=1.0e-10,
        max_nfev=120,
    )
    residuals = residual(result.x)
    residual_jacobian = jacobian(result.x)
    objective_value = float(objective_function(jnp.asarray(result.x, dtype=jnp.float64)))
    objective_gradient = np.asarray(gradient_function(jnp.asarray(result.x, dtype=jnp.float64)), dtype=float)
    objective_hessian = np.asarray(hessian_function(jnp.asarray(result.x, dtype=jnp.float64)), dtype=float)
    rho_v, rho_l, p_sat = decode_jax_saturation_variables(result.x)
    p_v, _, ln_phi_v = pure_jax_pressure_ares_ln_phi(parameters, temperature, rho_v)
    p_l, _, ln_phi_l = pure_jax_pressure_ares_ln_phi(parameters, temperature, rho_l)
    pressure_v_residual = float(p_v - p_sat)
    pressure_l_residual = float(p_l - p_sat)
    fugacity_residual = float(ln_phi_v - ln_phi_l)
    pressure_tolerance = max(abs(p_sat) * 1.0e-6, 1.0)
    residual_norm = float(np.linalg.norm(residuals, ord=2))
    if (
        not bool(result.success)
        or rho_v <= 0.0
        or rho_l <= rho_v
        or p_sat <= 0.0
        or abs(pressure_v_residual) > pressure_tolerance
        or abs(pressure_l_residual) > pressure_tolerance
        or abs(fugacity_residual) > 1.0e-6
        or residual_norm > 1.0e-6
    ):
        raise ValueError(
            "JAX pure saturation solve failed to satisfy pressure and fugacity equality "
            f"(status={result.status}, message={result.message!s})."
        )
    ipopt_status = python_ipopt_availability()
    hessian_eigenvalues = np.linalg.eigvalsh(objective_hessian)
    return JaxPureSaturationResult(
        closure_name=PICARD7_CLOSURE,
        model_role="toy_pcsaft_picard_association_jax_autodiff",
        status="computed_toy_pure_saturation",
        optimizer_backend=JAX_SCIPY_BACKEND,
        autodiff_backend=JAX_AUTODIFF_BACKEND,
        T_K=temperature,
        p_sat_Pa=float(p_sat),
        rho_vap_mol_m3=float(rho_v),
        rho_liq_mol_m3=float(rho_l),
        pressure_vap_residual_Pa=pressure_v_residual,
        pressure_liq_residual_Pa=pressure_l_residual,
        log_fugacity_residual=fugacity_residual,
        objective_value=objective_value,
        residual_norm=residual_norm,
        residual_jacobian_condition_number=float(np.linalg.cond(residual_jacobian)),
        objective_gradient_norm=float(np.linalg.norm(objective_gradient, ord=2)),
        objective_hessian_min_eigenvalue=float(np.min(hessian_eigenvalues)),
        objective_hessian_max_eigenvalue=float(np.max(hessian_eigenvalues)),
        solver_iteration_count=int(getattr(result, "njev", 0) or getattr(result, "nfev", 0)),
        objective_evaluation_count=int(getattr(result, "nfev", 0)),
        initial_guess_policy=INITIAL_GUESS_POLICY,
        python_ipopt_status=ipopt_status.status,
        python_ipopt_message=ipopt_status.message,
        message=(
            "Computed from JAX residual Jacobian, objective gradient, and objective Hessian "
            "for the explicit Picard association path."
        ),
    )


def jax_pure_saturation_functions(*, parameters: PureJaxParameters, temperature: float):
    raw_residual_function, raw_jacobian_function = _compiled_jax_pure_saturation_functions(parameters)
    temperature_value = jnp.asarray(float(temperature), dtype=jnp.float64)

    def residual_function(values):
        return raw_residual_function(jnp.asarray(values, dtype=jnp.float64), temperature_value)

    def jacobian_function(values):
        return raw_jacobian_function(jnp.asarray(values, dtype=jnp.float64), temperature_value)

    def objective_function(values):
        residuals = residual_function(values)
        return 0.5 * jnp.dot(residuals, residuals)

    def gradient_function(values):
        residuals = residual_function(values)
        jacobian = jacobian_function(values)
        return jacobian.T @ residuals

    def hessian_function(values):
        jacobian = jacobian_function(values)
        return jacobian.T @ jacobian

    _block_until_ready(residual_function(jnp.asarray([0.0, 1.0, 1.0], dtype=jnp.float64)))
    _block_until_ready(jacobian_function(jnp.asarray([0.0, 1.0, 1.0], dtype=jnp.float64)))
    return residual_function, objective_function, jacobian_function, gradient_function, hessian_function


@lru_cache(maxsize=32)
def _compiled_jax_pure_saturation_functions(parameters: PureJaxParameters):
    def residual_core(values, temperature):
        return pure_saturation_residuals_jax(values, parameters, temperature)

    raw_residual_function = jax.jit(residual_core)
    raw_jacobian_function = jax.jit(jax.jacobian(residual_core, argnums=0))
    return raw_residual_function, raw_jacobian_function


def pure_saturation_residuals_jax(values, parameters: PureJaxParameters, temperature: float):
    rho_v = jnp.exp(values[0])
    rho_l = rho_v + jnp.exp(values[1])
    pressure = jnp.exp(values[2])
    p_v, _, ln_phi_v = _pure_jax_pressure_ares_ln_phi_values(parameters, temperature, rho_v)
    p_l, _, ln_phi_l = _pure_jax_pressure_ares_ln_phi_values(parameters, temperature, rho_l)
    pressure_scale = jnp.maximum(jnp.abs(pressure), 1.0)
    return jnp.asarray(
        [
            (p_v - pressure) / pressure_scale,
            (p_l - pressure) / pressure_scale,
            ln_phi_v - ln_phi_l,
        ],
        dtype=jnp.float64,
    )


def pure_jax_pressure_ares_ln_phi(
    parameters: PureJaxParameters,
    temperature: float,
    rho_mol_m3: float,
) -> tuple[float, float, float]:
    pressure, ares, ln_phi = _pure_jax_pressure_ares_ln_phi_values(parameters, temperature, rho_mol_m3)
    return float(pressure), float(ares), float(ln_phi)


def _pure_jax_pressure_ares_ln_phi_values(
    parameters: PureJaxParameters,
    temperature: float,
    rho_mol_m3,
):
    pressure, ares, z_value = _pure_jax_pressure_ares_z(
        jnp.asarray(rho_mol_m3, dtype=jnp.float64),
        parameters,
        temperature,
    )
    ln_phi = ares + z_value - 1.0 - jnp.log(z_value)
    return pressure, ares, ln_phi


def decode_jax_saturation_variables(values: np.ndarray) -> tuple[float, float, float]:
    rho_v = float(np.exp(values[0]))
    rho_l = rho_v + float(np.exp(values[1]))
    pressure = float(np.exp(values[2]))
    return rho_v, rho_l, pressure


def pure_jax_parameters_from_case(case: Mapping[str, object]) -> PureJaxParameters:
    species = case.get("species")
    parameters = case.get("parameters")
    if isinstance(species, list) and len(species) != 1:
        raise ValueError("JAX pure saturation solve only accepts one-component cases.")
    if not isinstance(parameters, Mapping):
        raise ValueError("JAX pure saturation solve requires a parameters mapping.")
    scheme = _first_parameter(parameters, "assoc_scheme", "NONE")
    if str(scheme).strip().upper() != "2B":
        raise ValueError("JAX Picard pure saturation currently requires pure 2B association.")
    return PureJaxParameters(
        m=float(_first_parameter(parameters, "m")),
        sigma=float(_first_parameter(parameters, "s")),
        epsilon_over_k=float(_first_parameter(parameters, "e")),
        e_assoc=float(_first_parameter(parameters, "e_assoc")),
        vol_a=float(_first_parameter(parameters, "vol_a")),
        k_hb=float(_first_matrix_parameter(parameters, "k_hb", default=0.0)),
    )


def _pure_jax_pressure_ares_z(rho_mol_m3, parameters: PureJaxParameters, temperature: float):
    ares = _pure_jax_residual_helmholtz(rho_mol_m3, parameters, temperature)
    z_value = _pure_jax_compressibility(rho_mol_m3, parameters, temperature)
    pressure = rho_mol_m3 * GAS_CONSTANT * temperature * z_value
    return pressure, ares, z_value


def _pure_jax_compressibility(rho_mol_m3, parameters: PureJaxParameters, temperature: float):
    hc = _pure_jax_hard_chain_state(rho_mol_m3, parameters, temperature)
    z_hc = _pure_jax_hard_chain_z(parameters, hc)
    z_disp = _pure_jax_dispersion_z(rho_mol_m3, parameters, temperature, hc)
    z_assoc = rho_mol_m3 * jax.grad(
        lambda rho: _pure_jax_association_ares(rho, parameters, temperature)
    )(rho_mol_m3)
    return 1.0 + z_hc + z_disp + z_assoc


def _pure_jax_residual_helmholtz(rho_mol_m3, parameters: PureJaxParameters, temperature: float):
    hc = _pure_jax_hard_chain_state(rho_mol_m3, parameters, temperature)
    return (
        _pure_jax_ares_hc(parameters, hc)
        + _pure_jax_ares_disp(rho_mol_m3, parameters, temperature, hc)
        + _pure_jax_association_ares(rho_mol_m3, parameters, temperature)
    )


def _pure_jax_hard_chain_state(rho_mol_m3, parameters: PureJaxParameters, temperature: float):
    number_density = rho_mol_m3 * N_AV / 1.0e30
    diameter = parameters.sigma * (1.0 - 0.12 * jnp.exp(-3.0 * parameters.epsilon_over_k / temperature))
    orders = jnp.arange(4, dtype=jnp.float64)
    zeta = jnp.pi / 6.0 * number_density * parameters.m * diameter**orders
    eta = zeta[3]
    pair_diameter = diameter / 2.0
    one_minus_eta = 1.0 - eta
    ghs = (
        1.0 / one_minus_eta
        + pair_diameter * 3.0 * zeta[2] / one_minus_eta**2
        + pair_diameter**2 * 2.0 * zeta[2] ** 2 / one_minus_eta**3
    )
    return zeta, eta, ghs, diameter, pair_diameter, number_density


def _pure_jax_ares_hc(parameters: PureJaxParameters, hc):
    zeta, _, ghs, _, _, _ = hc
    z0, z1, z2, z3 = zeta
    a_hs = (
        3.0 * z1 * z2 / (1.0 - z3)
        + z2**3 / (z3 * (1.0 - z3) ** 2)
        + (z2**3 / z3**2 - z0) * jnp.log(1.0 - z3)
    ) / z0
    return parameters.m * a_hs - (parameters.m - 1.0) * jnp.log(ghs)


def _pure_jax_hard_chain_z(parameters: PureJaxParameters, hc):
    zeta, _, ghs, _, pair_diameter, _ = hc
    z0, z1, z2, z3 = zeta
    one_minus_eta = 1.0 - z3
    z_hs = (
        z3 / one_minus_eta
        + 3.0 * z1 * z2 / z0 / one_minus_eta**2
        + (3.0 * z2**3 - z3 * z2**3) / z0 / one_minus_eta**3
    )
    dghs_deta = (
        z3 / one_minus_eta**2
        + pair_diameter * (3.0 * z2 / one_minus_eta**2 + 6.0 * z2 * z3 / one_minus_eta**3)
        + pair_diameter**2
        * (4.0 * z2**2 / one_minus_eta**3 + 6.0 * z2**2 * z3 / one_minus_eta**4)
    )
    chain_sum = (parameters.m - 1.0) / ghs * dghs_deta
    return parameters.m * z_hs - chain_sum


def _pure_jax_dispersion_polynomials(parameters: PureJaxParameters, eta):
    a0 = jnp.asarray(
        [0.9105631445, 0.6361281449, 2.6861347891, -26.547362491, 97.759208784, -159.59154087, 91.297774084],
        dtype=jnp.float64,
    )
    a1 = jnp.asarray(
        [-0.3084016918, 0.1860531159, -2.5030047259, 21.419793629, -65.255885330, 83.318680481, -33.746922930],
        dtype=jnp.float64,
    )
    a2 = jnp.asarray(
        [-0.0906148351, 0.4527842806, 0.5962700728, -1.7241829131, -4.1302112531, 13.776631870, -8.6728470368],
        dtype=jnp.float64,
    )
    b0 = jnp.asarray(
        [0.7240946941, 2.2382791861, -4.0025849485, -21.003576815, 26.855641363, 206.55133841, -355.60235612],
        dtype=jnp.float64,
    )
    b1 = jnp.asarray(
        [-0.5755498075, 0.6995095521, 3.8925673390, -17.215471648, 192.67226447, -161.82646165, -165.20769346],
        dtype=jnp.float64,
    )
    b2 = jnp.asarray(
        [0.0976883116, -0.2557574982, -9.1558561530, 20.642075974, -38.804430052, 93.626774077, -29.666905585],
        dtype=jnp.float64,
    )
    c1_m = (parameters.m - 1.0) / parameters.m
    c2_m = (parameters.m - 2.0) / parameters.m
    a = a0 + c1_m * a1 + c1_m * c2_m * a2
    b = b0 + c1_m * b1 + c1_m * c2_m * b2
    powers = eta ** jnp.arange(7, dtype=jnp.float64)
    i1 = jnp.dot(a, powers)
    i2 = jnp.dot(b, powers)
    c1 = 1.0 / (
        1.0
        + parameters.m * (8.0 * eta - 2.0 * eta**2) / (1.0 - eta) ** 4
        + (1.0 - parameters.m)
        * (20.0 * eta - 27.0 * eta**2 + 12.0 * eta**3 - 2.0 * eta**4)
        / ((1.0 - eta) * (2.0 - eta)) ** 2
    )
    return a, b, i1, i2, c1


def _pure_jax_ares_disp(rho_mol_m3, parameters: PureJaxParameters, temperature: float, hc):
    _, eta, _, _, _, number_density = hc
    _, _, i1, i2, c1 = _pure_jax_dispersion_polynomials(parameters, eta)
    sigma3 = parameters.sigma**3
    e_over_t = parameters.epsilon_over_k / temperature
    m2epssigma3 = parameters.m**2 * e_over_t * sigma3
    m2eps2sigma3 = parameters.m**2 * e_over_t**2 * sigma3
    return (
        -2.0 * jnp.pi * number_density * i1 * m2epssigma3
        - jnp.pi * number_density * parameters.m * c1 * i2 * m2eps2sigma3
    )


def _pure_jax_dispersion_z(rho_mol_m3, parameters: PureJaxParameters, temperature: float, hc):
    _, eta, _, _, _, number_density = hc
    a, b, _, i2, c1 = _pure_jax_dispersion_polynomials(parameters, eta)
    powers = eta ** jnp.arange(7, dtype=jnp.float64)
    derivative_powers = (jnp.arange(7, dtype=jnp.float64) + 1.0) * powers
    d_eta_i1_d_eta = jnp.dot(a, derivative_powers)
    d_eta_i2_d_eta = jnp.dot(b, derivative_powers)
    c2 = -c1**2 * (
        parameters.m * (-4.0 * eta**2 + 20.0 * eta + 8.0) / (1.0 - eta) ** 5
        + (1.0 - parameters.m)
        * (2.0 * eta**3 + 12.0 * eta**2 - 48.0 * eta + 40.0)
        / ((1.0 - eta) * (2.0 - eta)) ** 3
    )
    sigma3 = parameters.sigma**3
    e_over_t = parameters.epsilon_over_k / temperature
    m2epssigma3 = parameters.m**2 * e_over_t * sigma3
    m2eps2sigma3 = parameters.m**2 * e_over_t**2 * sigma3
    return (
        -2.0 * jnp.pi * number_density * d_eta_i1_d_eta * m2epssigma3
        - jnp.pi
        * number_density
        * parameters.m
        * (c1 * d_eta_i2_d_eta + c2 * eta * i2)
        * m2eps2sigma3
    )


def _pure_jax_association_ares(rho_mol_m3, parameters: PureJaxParameters, temperature: float):
    number_density = rho_mol_m3 * N_AV / 1.0e30
    hc = _pure_jax_hard_chain_state(rho_mol_m3, parameters, temperature)
    _, _, ghs, _, _, _ = hc
    association_volume = parameters.vol_a * (1.0 - parameters.k_hb)
    delta = ghs * (jnp.exp(parameters.e_assoc / temperature) - 1.0) * parameters.sigma**3 * association_volume
    xa = _pure_jax_picard_2b(number_density, delta)
    terms = jnp.log(xa) - 0.5 * xa + 0.5
    return 2.0 * terms


def _pure_jax_picard_2b(number_density, delta):
    strength = number_density * delta
    xa = 2.0 / (1.0 + jnp.sqrt(1.0 + 4.0 * strength))
    damping = 0.5
    for _ in range(7):
        proposal = 1.0 / (1.0 + strength * xa)
        xa = (1.0 - damping) * xa + damping * proposal
    return jnp.clip(xa, 1.0e-14, 1.0)


def _first_parameter(parameters: Mapping[str, object], key: str, default: object | None = None) -> object:
    raw = parameters.get(key, default)
    if raw is None:
        raise ValueError(f"JAX pure saturation solve requires parameter {key}.")
    return raw[0] if isinstance(raw, list) else raw


def _first_matrix_parameter(parameters: Mapping[str, object], key: str, *, default: float) -> object:
    raw = parameters.get(key)
    if raw is None:
        return default
    array = np.asarray(raw, dtype=float)
    if array.ndim == 0:
        return float(array)
    return float(array.reshape(-1)[0])


def _block_until_ready(value):
    if hasattr(value, "block_until_ready"):
        return value.block_until_ready()
    return value
