from __future__ import annotations

import numpy as np
import pytest

import epcsaft
import epcsaft._core as _core
from tests.support.hydrocarbon_cases import HYDROCARBON_LIQUID_X, HYDROCARBON_T, hydrocarbon_parameter_set
from tests.support.native_cases import _neutral_state


def test_cppad_pressure_derivative_api_underpins_bubble_policy() -> None:
    mix, _species, _pressure, density, temperature, composition = _neutral_state()
    state = mix.state(T=temperature, x=composition, rho=density)

    pressure_density = state.pressure_density_derivative_result()

    assert pressure_density["backend"] == "cppad"
    assert pressure_density["shape"] == [1, 1]


def test_neutral_bubble_uses_native_ipopt_route_gate() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    equilibrium = epcsaft.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    )

    if not _core._native_ipopt_smoke()["compiled"]:
        with pytest.raises(epcsaft.InputError, match=r"bubble_pressure requires a native Ipopt selector equilibrium route"):
            equilibrium.solve()
        return

    result = equilibrium.solve()

    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["exact_hessian_available"] is True
