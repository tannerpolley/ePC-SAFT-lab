from __future__ import annotations

import epcsaft
import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
import epcsaft_equilibrium
from equilibrium_support.hydrocarbon_cases import HYDROCARBON_LIQUID_X, HYDROCARBON_T, hydrocarbon_parameter_set


def test_neutral_bubble_uses_native_ipopt_route_gate() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    equilibrium = epcsaft_equilibrium.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    )

    if not _core._native_ipopt_smoke()["compiled"]:
        with pytest.raises(
            epcsaft.InputError,
            match=r"bubble_pressure requires the native Ipopt selector equilibrium route",
        ):
            equilibrium.solve()
        return

    result = equilibrium.solve()

    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["exact_hessian_available"] is True
