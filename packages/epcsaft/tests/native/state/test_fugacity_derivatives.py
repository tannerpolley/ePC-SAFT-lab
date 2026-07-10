from __future__ import annotations

import epcsaft._core as _core
import numpy as np
import pytest
from epcsaft._types import InputError
from epcsaft.state.native_adapter import ePCSAFTMixture
from support.native_cases import _neutral_state


def _state():
    mix, _species, _pressure, density, temperature, composition = _neutral_state()
    return mix.state(T=temperature, x=composition, rho=density)


def _neutral_binary_state():
    species = ["A", "B"]
    params = {
        "m": np.asarray([1.0000, 1.6069]),
        "s": np.asarray([3.7039, 3.5206]),
        "e": np.asarray([150.03, 191.42]),
        "k_ij": np.asarray([[0.0, 3.0e-4], [3.0e-4, 0.0]]),
        "l_ij": np.asarray([[0.0, 2.0e-4], [2.0e-4, 0.0]]),
    }
    mix = ePCSAFTMixture.from_params(params, species=species)
    return mix.state(T=233.15, x=np.asarray([0.35, 0.65]), rho=1000.0)


def _associating_binary_state(kij=0.01):
    temperature = 298.15
    water_sigma = 2.7927 + 10.11 * np.exp(-0.01775 * temperature) - 1.417 * np.exp(-0.01146 * temperature)
    params = {
        "m": np.asarray([1.2047, 1.6069]),
        "s": np.asarray([water_sigma, 3.5206]),
        "e": np.asarray([353.95, 191.42]),
        "e_assoc": np.asarray([2425.7, 0.0]),
        "vol_a": np.asarray([0.04509, 0.0]),
        "assoc_scheme": ["2B", None],
        "k_ij": np.asarray([[0.0, kij], [kij, 0.0]]),
    }
    mix = ePCSAFTMixture.from_params(params, species=["water", "B"])
    return mix.state(T=temperature, x=np.asarray([0.55, 0.45]), rho=3000.0)


def _associating_binary_association_parameter_state():
    temperature = 298.15
    water_sigma = 2.7927 + 10.11 * np.exp(-0.01775 * temperature) - 1.417 * np.exp(-0.01146 * temperature)
    params = {
        "m": np.asarray([1.2047, 1.6069]),
        "s": np.asarray([water_sigma, 3.5206]),
        "e": np.asarray([353.95, 191.42]),
        "e_assoc": np.asarray([2425.7, 1200.0]),
        "vol_a": np.asarray([0.04509, 0.025]),
        "assoc_scheme": ["2B", "2B"],
        "k_ij": np.asarray([[0.0, 0.01], [0.01, 0.0]]),
        "l_ij": np.asarray([[0.0, 2.0e-4], [2.0e-4, 0.0]]),
        "k_hb": np.asarray([[0.0, 0.03], [0.03, 0.0]]),
    }
    mix = ePCSAFTMixture.from_params(params, species=["water", "B"])
    return mix.state(T=temperature, x=np.asarray([0.55, 0.45]), rho=1000.0)


def _pure_associating_state():
    temperature = 298.15
    water_sigma = 2.7927 + 10.11 * np.exp(-0.01775 * temperature) - 1.417 * np.exp(-0.01146 * temperature)
    params = {
        "m": np.asarray([1.2047]),
        "s": np.asarray([water_sigma]),
        "e": np.asarray([353.95]),
        "e_assoc": np.asarray([2425.7]),
        "vol_a": np.asarray([0.04509]),
        "assoc_scheme": ["2B"],
    }
    mix = ePCSAFTMixture.from_params(params, species=["water"])
    return mix.state(T=temperature, x=np.asarray([1.0]), rho=1000.0)


def _pure_neutral_state():
    params = {
        "m": np.asarray([1.6069]),
        "s": np.asarray([3.5206]),
        "e": np.asarray([191.42]),
    }
    mix = ePCSAFTMixture.from_params(params, species=["A"])
    return mix.state(T=233.15, x=np.asarray([1.0]), rho=1000.0)


def test_ares_composition_derivative_result_uses_explicit_backend_labels() -> None:
    state = _state()

    result = state.ares_composition_derivative_result()

    assert result["supported"] is True
    assert result["backend"] in {"analytic", "cppad"}
    assert result["shape"] == [1, state.x.size]
    assert np.asarray(result["jacobian"], dtype=float).shape == (1, state.x.size)


def test_ln_fugacity_composition_derivative_route_raises_until_supported() -> None:
    state = _state()

    with pytest.raises(InputError, match="second composition derivatives"):
        state.ln_fugacity_composition_derivative_result()


def test_ln_fugacity_parameter_derivative_route_raises_without_born_path() -> None:
    state = _state()

    with pytest.raises(InputError, match="unsupported"):
        state.ln_fugacity_parameter_derivative_result()


def test_ln_fugacity_parameter_derivative_result_supports_neutral_binary_kij() -> None:
    state = _neutral_binary_state()

    result = state.ln_fugacity_parameter_derivative_result()

    assert result["supported"] is True
    assert result["backend"] == "cppad"
    assert result["shape"] == [state.x.size, 2]
    assert result["parameter_order"] == ("k_ij:A:B", "l_ij:A:B")
    assert result["component_order"] == ("A", "B")
    assert np.asarray(result["jacobian"], dtype=float).shape == (state.x.size, 2)


def test_pressure_parameter_derivative_result_supports_associating_binary_kij() -> None:
    state = _associating_binary_state()

    raw = state._neutral_binary_kij_property_derivatives()
    assert raw is not None
    assert raw["backend"] == "cppad_implicit"
    assert raw["parameter_names"] == ["k_ij"]
    assert raw["k_ij_pressure_derivative"] != 0.0

    result = state.pressure_parameter_derivative_result()
    assert result["supported"] is True
    assert result["backend"] == "cppad_implicit"
    assert result["parameter_order"] == ("k_ij:water:B",)
    assert result["outputs"] == ["pressure"]
    assert result["variables"] == ["k_ij:water:B"]
    jacobian = np.asarray(result["jacobian"], dtype=float)
    assert jacobian.shape == (1, 1)
    assert jacobian[0, 0] == pytest.approx(raw["k_ij_pressure_derivative"], rel=0.0, abs=0.0)


def test_associating_pure_parameter_derivative_results_support_e_assoc_and_vol_a() -> None:
    state = _pure_associating_state()

    if not _core._native_cppad_smoke()["cppad_compiled"]:
        with pytest.raises(InputError, match="unsupported"):
            state.pressure_parameter_derivative_result()
        return

    pressure = state.pressure_parameter_derivative_result()
    chemical = state.chemical_potential_parameter_derivative_result()
    fugacity = state.ln_fugacity_parameter_derivative_result()

    expected_order = ("e_assoc:water", "vol_a:water")
    for result in (pressure, chemical, fugacity):
        assert result["supported"] is True
        assert result["backend"] == "cppad_implicit"
        assert result["parameter_order"] == expected_order
        assert result["component_order"] == ("water",)
        assert result["association_sensitivity_backend"] == "cppad_implicit_association"
        assert result["association_sensitivity_helper"] == "association_implicit_sensitivity"
        assert result["association_site_count"] == 2
        assert result["shape"] == [1, 2]
        jacobian = np.asarray(result["jacobian"], dtype=float)
        assert jacobian.shape == (1, 2)
        assert np.all(np.isfinite(jacobian))
        assert np.all(np.abs(jacobian[0]) > 1.0e-12)


def test_associating_binary_parameter_derivative_results_support_lij_and_khb() -> None:
    state = _associating_binary_association_parameter_state()

    if not _core._native_cppad_smoke()["cppad_compiled"]:
        with pytest.raises(InputError, match="unsupported"):
            state.pressure_parameter_derivative_result()
        return

    pressure = state.pressure_parameter_derivative_result()
    chemical = state.chemical_potential_parameter_derivative_result()
    fugacity = state.ln_fugacity_parameter_derivative_result()

    expected_order = ("k_ij:water:B", "l_ij:water:B", "k_hb_ij:water:B")
    for result in (pressure, chemical, fugacity):
        assert result["supported"] is True
        assert result["backend"] == "cppad_implicit"
        assert result["parameter_order"] == expected_order
        assert result["component_order"] == ("water", "B")
        assert result["association_sensitivity_backend"] == "cppad_implicit_association"
        assert result["association_sensitivity_helper"] == "association_implicit_sensitivity"
        assert result["association_site_count"] == 4
        assert result["shape"] == [len(result["outputs"]), 3]
        jacobian = np.asarray(result["jacobian"], dtype=float)
        assert jacobian.shape == (len(result["outputs"]), 3)
        assert np.all(np.isfinite(jacobian))
        assert np.any(np.abs(jacobian[:, 1]) > 1.0e-12)
        assert np.any(np.abs(jacobian[:, 2]) > 1.0e-12)


def test_ln_fugacity_parameter_derivative_result_supports_pure_neutral_m_sigma_epsilon() -> None:
    state = _pure_neutral_state()

    result = state.ln_fugacity_parameter_derivative_result()

    assert result["supported"] is True
    assert result["backend"] == "cppad"
    assert result["shape"] == [1, 3]
    assert result["parameter_order"] == ("m:A", "sigma:A", "epsilon:A")
    assert result["component_order"] == ("A",)
    assert np.asarray(result["jacobian"], dtype=float).shape == (1, 3)


def test_chemical_potential_parameter_derivative_result_supports_neutral_binary_kij() -> None:
    state = _neutral_binary_state()

    result = state.chemical_potential_parameter_derivative_result()

    assert result["supported"] is True
    assert result["backend"] == "cppad"
    assert result["shape"] == [state.x.size, 2]
    assert result["parameter_order"] == ("k_ij:A:B", "l_ij:A:B")
    assert result["component_order"] == ("A", "B")
    assert result["value_basis"] == "residual_chemical_potential"
    assert np.asarray(result["jacobian"], dtype=float).shape == (state.x.size, 2)


def test_chemical_potential_parameter_derivative_result_supports_pure_neutral_m_sigma_epsilon() -> None:
    state = _pure_neutral_state()

    result = state.chemical_potential_parameter_derivative_result()

    assert result["supported"] is True
    assert result["backend"] == "cppad"
    assert result["shape"] == [1, 3]
    assert result["parameter_order"] == ("m:A", "sigma:A", "epsilon:A")
    assert result["component_order"] == ("A",)
    assert result["value_basis"] == "residual_chemical_potential"
    assert np.asarray(result["jacobian"], dtype=float).shape == (1, 3)
