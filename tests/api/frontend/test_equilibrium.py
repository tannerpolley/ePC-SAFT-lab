from __future__ import annotations

import pytest

import epcsaft
from epcsaft import _core
from tests.support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_RHO,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)


def test_workflow_object_is_constructed_directly() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    equilibrium = epcsaft.Equilibrium(mixture, max_iterations=200)

    assert equilibrium.mixture is mixture


def test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    result = epcsaft.Equilibrium(
        epcsaft.Mixture(hydrocarbon_parameter_set()),
        max_iterations=200,
        tolerance=1.0e-8,
        ipopt_iteration_history_limit=4,
    ).bubble_pressure(T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X)

    diagnostics = result.diagnostics
    assert result.problem_kind == "neutral_bubble_p"
    assert result.phases[0].composition == pytest.approx(HYDROCARBON_LIQUID_X, abs=1.0e-10)
    assert result.phases[1].composition == pytest.approx(HYDROCARBON_VAPOR_Y, rel=5.0e-5, abs=5.0e-7)
    assert result.phases[0].pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.phases[0].density == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=5.0e-5)
    assert result.phases[1].density == pytest.approx(HYDROCARBON_VAPOR_RHO, rel=5.0e-5)
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["eval_h_calls"] > 0
