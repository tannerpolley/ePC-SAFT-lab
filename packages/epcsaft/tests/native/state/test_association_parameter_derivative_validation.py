from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy

import epcsaft._core as _core
import numpy as np
import pytest
from epcsaft.state.native_adapter import ePCSAFTMixture


def _water_sigma(temperature: float) -> float:
    return float(2.7927 + 10.11 * np.exp(-0.01775 * temperature) - 1.417 * np.exp(-0.01146 * temperature))


def _copy_params(params: dict[str, object]) -> dict[str, object]:
    copied = deepcopy(params)
    for key, value in list(copied.items()):
        if isinstance(value, np.ndarray):
            copied[key] = np.asarray(value, dtype=float).copy()
    return copied


def _pure_associating_case() -> tuple[dict[str, object], list[str], float, np.ndarray, float]:
    temperature = 298.15
    params: dict[str, object] = {
        "m": np.asarray([1.2047]),
        "s": np.asarray([_water_sigma(temperature)]),
        "e": np.asarray([353.95]),
        "e_assoc": np.asarray([2425.7]),
        "vol_a": np.asarray([0.04509]),
        "assoc_scheme": ["2B"],
    }
    return params, ["water"], temperature, np.asarray([1.0]), 1000.0


def _binary_associating_case() -> tuple[dict[str, object], list[str], float, np.ndarray, float]:
    temperature = 298.15
    params: dict[str, object] = {
        "m": np.asarray([1.2047, 1.6069]),
        "s": np.asarray([_water_sigma(temperature), 3.5206]),
        "e": np.asarray([353.95, 191.42]),
        "e_assoc": np.asarray([2425.7, 1200.0]),
        "vol_a": np.asarray([0.04509, 0.025]),
        "assoc_scheme": ["2B", "2B"],
        "k_ij": np.asarray([[0.0, 0.01], [0.01, 0.0]]),
        "l_ij": np.asarray([[0.0, 2.0e-4], [2.0e-4, 0.0]]),
        "k_hb": np.asarray([[0.0, 0.03], [0.03, 0.0]]),
    }
    return params, ["water", "B"], temperature, np.asarray([0.55, 0.45]), 1000.0


def _state(
    params: dict[str, object],
    species: list[str],
    temperature: float,
    composition: np.ndarray,
    density: float,
):
    return ePCSAFTMixture.from_params(params, species=species).state(
        T=temperature,
        x=composition,
        rho=density,
    )


def _central_difference(
    params: dict[str, object],
    species: list[str],
    temperature: float,
    composition: np.ndarray,
    density: float,
    perturb: Callable[[dict[str, object], float], None],
    output: Callable[[object], np.ndarray],
    step: float,
) -> np.ndarray:
    high = _copy_params(params)
    low = _copy_params(params)
    perturb(high, step)
    perturb(low, -step)
    high_value = output(_state(high, species, temperature, composition, density))
    low_value = output(_state(low, species, temperature, composition, density))
    return (high_value - low_value) / (2.0 * step)


def _pressure_output(state: object) -> np.ndarray:
    return np.asarray([state.pressure()], dtype=float)


def _ln_fugacity_output(state: object) -> np.ndarray:
    return np.asarray(state.fugacity_coefficient(natural_log=True), dtype=float)


def _perturb_vector(name: str, index: int) -> Callable[[dict[str, object], float], None]:
    def perturb(params: dict[str, object], delta: float) -> None:
        values = np.asarray(params[name], dtype=float).copy()
        values[index] += delta
        params[name] = values

    return perturb


def _perturb_pair(name: str, i: int, j: int) -> Callable[[dict[str, object], float], None]:
    def perturb(params: dict[str, object], delta: float) -> None:
        values = np.asarray(params[name], dtype=float).copy()
        values[i, j] += delta
        values[j, i] += delta
        params[name] = values

    return perturb


@pytest.mark.skipif(
    not _core._native_cppad_smoke()["cppad_compiled"],
    reason="validation-only association parameter derivative checks require CppAD",
)
@pytest.mark.parametrize(
    ("parameter_name", "step"),
    [
        ("e_assoc", 1.0e-2),
        ("vol_a", 1.0e-6),
    ],
)
def test_validation_only_pure_association_parameter_derivatives_match_central_diff(
    parameter_name: str,
    step: float,
) -> None:
    """Central-difference use here is validation-only, not a production derivative backend."""

    params, species, temperature, composition, density = _pure_associating_case()
    state = _state(params, species, temperature, composition, density)
    parameter_order = tuple(state.pressure_parameter_derivative_result()["parameter_order"])
    column = parameter_order.index(f"{parameter_name}:water")
    perturb = _perturb_vector(parameter_name, 0)

    pressure = state.pressure_parameter_derivative_result()
    pressure_jacobian = np.asarray(pressure["jacobian"], dtype=float)
    pressure_check = _central_difference(
        params,
        species,
        temperature,
        composition,
        density,
        perturb,
        _pressure_output,
        step,
    )
    assert pressure_jacobian[:, column] == pytest.approx(pressure_check, rel=1.0e-4, abs=1.0e-6)

    fugacity = state.ln_fugacity_parameter_derivative_result()
    fugacity_jacobian = np.asarray(fugacity["jacobian"], dtype=float)
    fugacity_check = _central_difference(
        params,
        species,
        temperature,
        composition,
        density,
        perturb,
        _ln_fugacity_output,
        step,
    )
    assert fugacity_jacobian[:, column] == pytest.approx(fugacity_check, rel=1.0e-4, abs=1.0e-6)


@pytest.mark.skipif(
    not _core._native_cppad_smoke()["cppad_compiled"],
    reason="validation-only association parameter derivative checks require CppAD",
)
@pytest.mark.parametrize(
    ("matrix_name", "parameter_name", "step"),
    [
        ("l_ij", "l_ij", 1.0e-6),
        ("k_hb", "k_hb_ij", 1.0e-5),
    ],
)
def test_validation_only_binary_association_parameter_derivatives_match_central_diff(
    matrix_name: str,
    parameter_name: str,
    step: float,
) -> None:
    """Central-difference use here is validation-only, not a production derivative backend."""

    params, species, temperature, composition, density = _binary_associating_case()
    state = _state(params, species, temperature, composition, density)
    parameter_order = tuple(state.pressure_parameter_derivative_result()["parameter_order"])
    column = parameter_order.index(f"{parameter_name}:water:B")
    perturb = _perturb_pair(matrix_name, 0, 1)

    pressure = state.pressure_parameter_derivative_result()
    pressure_jacobian = np.asarray(pressure["jacobian"], dtype=float)
    pressure_check = _central_difference(
        params,
        species,
        temperature,
        composition,
        density,
        perturb,
        _pressure_output,
        step,
    )
    assert pressure_jacobian[:, column] == pytest.approx(pressure_check, rel=1.0e-4, abs=1.0e-6)

    fugacity = state.ln_fugacity_parameter_derivative_result()
    fugacity_jacobian = np.asarray(fugacity["jacobian"], dtype=float)
    fugacity_check = _central_difference(
        params,
        species,
        temperature,
        composition,
        density,
        perturb,
        _ln_fugacity_output,
        step,
    )
    assert fugacity_jacobian[:, column] == pytest.approx(fugacity_check, rel=1.0e-4, abs=1.0e-6)
