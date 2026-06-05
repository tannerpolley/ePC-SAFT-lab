from __future__ import annotations

import math

import numpy as np
import pytest

import epcsaft._core as _provider_core
from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()


def _pure_ethane_mixture() -> ePCSAFTMixture:
    params = {
        "MW": np.asarray([30.070e-3]),
        "m": np.asarray([1.6069]),
        "s": np.asarray([3.5206]),
        "e": np.asarray([191.42]),
    }
    return ePCSAFTMixture.from_params(params, species=["Ethane"])


def _binary_mixture() -> ePCSAFTMixture:
    params = {
        "MW": np.asarray([16.043e-3, 30.070e-3]),
        "m": np.asarray([1.0, 1.6069]),
        "s": np.asarray([3.7039, 3.5206]),
        "e": np.asarray([150.03, 191.42]),
        "k_ij": np.asarray([[0.0, 3.0e-4], [3.0e-4, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["Methane", "Ethane"])


def test_single_component_vle_block_reports_pressure_and_chemical_potential_residuals() -> None:
    mix = _pure_ethane_mixture()
    temperature = 233.15
    vapor_density = 730.0
    liquid_density = 14_300.0
    composition = [1.0]
    vapor_state = mix.state(T=temperature, rho=vapor_density, x=composition, phase="vapor")
    liquid_state = mix.state(T=temperature, rho=liquid_density, x=composition, phase="liquid")
    p_sat = vapor_state.pressure()

    payload = _core._native_saturation_block(
        mix._native,
        temperature,
        math.log(vapor_density),
        math.log(liquid_density),
        math.log(p_sat),
    )

    vapor_reduced_mu = math.log(vapor_density) + float(vapor_state.residual_chemical_potential()[0])
    liquid_reduced_mu = math.log(liquid_density) + float(liquid_state.residual_chemical_potential()[0])

    assert payload["block"] == "single_component_vle"
    assert payload["variable_names"] == ["log_rho_v", "log_rho_l", "log_p_sat"]
    assert payload["constraint_names"] == [
        "vapor_pressure_consistency",
        "liquid_pressure_consistency",
        "chemical_potential_equality",
    ]
    assert payload["temperature"] == pytest.approx(temperature)
    assert payload["vapor_density"] == pytest.approx(vapor_density)
    assert payload["liquid_density"] == pytest.approx(liquid_density)
    assert payload["p_sat"] == pytest.approx(p_sat)
    assert payload["vapor_pressure"] == pytest.approx(p_sat)
    assert payload["liquid_pressure"] == pytest.approx(liquid_state.pressure())
    assert payload["residuals"] == pytest.approx(
        [
            0.0,
            liquid_state.pressure() - p_sat,
            vapor_reduced_mu - liquid_reduced_mu,
        ],
        rel=1.0e-12,
        abs=1.0e-8,
    )


def test_single_component_vle_block_reports_exact_jacobian_metadata() -> None:
    mix = _pure_ethane_mixture()
    temperature = 233.15
    vapor_density = 730.0
    liquid_density = 14_300.0
    p_sat = mix.state(T=temperature, rho=vapor_density, x=[1.0], phase="vapor").pressure()

    payload = _core._native_saturation_block(
        mix._native,
        temperature,
        math.log(vapor_density),
        math.log(liquid_density),
        math.log(p_sat),
    )

    jacobian = np.asarray(payload["jacobian_row_major"], dtype=float).reshape((3, 3))
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["jacobian_backend"] == "cppad_phase_blocks"
    assert payload["jacobian_shape"] == (3, 3)
    assert np.all(np.isfinite(jacobian))
    assert jacobian[0, 0] == pytest.approx(
        payload["vapor_pressure_density_derivative"] * payload["vapor_density"],
        rel=1.0e-12,
        abs=1.0e-8,
    )
    assert jacobian[0, 1] == pytest.approx(0.0, abs=0.0)
    assert jacobian[0, 2] == pytest.approx(-payload["p_sat"], rel=1.0e-12, abs=1.0e-8)
    assert jacobian[1, 0] == pytest.approx(0.0, abs=0.0)
    assert jacobian[1, 1] == pytest.approx(
        payload["liquid_pressure_density_derivative"] * payload["liquid_density"],
        rel=1.0e-12,
        abs=1.0e-8,
    )
    assert jacobian[1, 2] == pytest.approx(-payload["p_sat"], rel=1.0e-12, abs=1.0e-8)
    assert jacobian[2, 2] == pytest.approx(0.0, abs=0.0)
    assert payload["constraint_scaling"] == pytest.approx(
        [1.0 / max(abs(payload["p_sat"]), 1.0e5), 1.0 / max(abs(payload["p_sat"]), 1.0e5), 1.0]
    )


def test_single_component_vle_block_rejects_mixtures_with_more_than_one_component() -> None:
    mix = _binary_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="requires exactly one component"):
        _core._native_saturation_block(
            mix._native,
            233.15,
            math.log(730.0),
            math.log(14_300.0),
            math.log(1.0e6),
        )
