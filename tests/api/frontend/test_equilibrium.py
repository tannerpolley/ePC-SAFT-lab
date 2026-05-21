from __future__ import annotations

import pytest

import epcsaft
import epcsaft._core as _core
from tests.support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_FLASH_Z,
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


def _equilibrium() -> epcsaft.Equilibrium:
    return epcsaft.Equilibrium(
        epcsaft.Mixture(hydrocarbon_parameter_set()),
        max_iterations=200,
        tolerance=1.0e-8,
        ipopt_iteration_history_limit=4,
    )


def _assert_hydrocarbon_pair(result, *, problem_kind: str) -> None:
    diagnostics = result.diagnostics
    assert result.problem_kind == problem_kind
    assert result.phases[0].composition == pytest.approx(HYDROCARBON_LIQUID_X, rel=1.0e-4, abs=5.0e-7)
    assert result.phases[1].composition == pytest.approx(HYDROCARBON_VAPOR_Y, rel=1.0e-4, abs=5.0e-7)
    assert result.phases[0].temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
    assert result.phases[1].temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
    assert result.phases[0].pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.phases[1].pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.phases[0].density == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=1.0e-4)
    assert result.phases[1].density == pytest.approx(HYDROCARBON_VAPOR_RHO, rel=1.0e-4)
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["eval_h_calls"] > 0
    assert diagnostics["postsolve_certification"]["accepted"] is True


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route() -> None:
    _skip_without_ipopt()

    result = _equilibrium().solve(route="bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_p")


def test_equilibrium_bubble_temperature_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _equilibrium().solve(route="bubble_temperature", P=HYDROCARBON_BUBBLE_P, x=HYDROCARBON_LIQUID_X)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_t")


def test_equilibrium_dew_pressure_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _equilibrium().solve(route="dew_pressure", T=HYDROCARBON_T, y=HYDROCARBON_VAPOR_Y)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_p")


def test_equilibrium_dew_temperature_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _equilibrium().solve(route="dew_temperature", P=HYDROCARBON_BUBBLE_P, y=HYDROCARBON_VAPOR_Y)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_t")


def test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _equilibrium().solve(route="flash", T=HYDROCARBON_T, P=HYDROCARBON_BUBBLE_P, z=HYDROCARBON_FLASH_Z)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_tp_flash")
    assert result.split_detected is True
    assert result.phases[0].phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
    assert result.phases[1].phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
