"""Object-oriented integration tests for the pybind11 native ePC-SAFT runtime."""

import numpy as np
import pytest

import epcsaft
import epcsaft.epcsaft as epcsaft_module
from epcsaft import ePCSAFTMixture
from epcsaft.eos import StateDiagnosticsView
from tests.helpers.numeric import assert_allclose
from tests.helpers.runtime_cases import (
    _assert_array,
    _ionic_state,
    _neutral_state,
    _sum_term_arrays,
)


def test_state_constructor_rejects_invalid_pressure_and_density():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0]),
            "s": np.asarray([3.0]),
            "e": np.asarray([150.0]),
        }
    )

    with pytest.raises(epcsaft.InputError):
        mix.state(T=300.0, x=np.asarray([1.0]), P=0.0)

    with pytest.raises(epcsaft.InputError):
        mix.state(T=300.0, x=np.asarray([1.0]), rho=-1.0)

def test_state_constructor_rejects_composition_length_mismatch_before_native_call():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0]),
            "s": np.asarray([3.0]),
            "e": np.asarray([150.0]),
        }
    )

    with pytest.raises(epcsaft.InputError, match="composition length"):
        mix.state(T=300.0, x=np.asarray([0.5, 0.5]), rho=100.0)

def test_pressure_based_state_matches_equivalent_density_state():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([2.8149]),
            "s": np.asarray([3.7169]),
            "e": np.asarray([285.69]),
        },
        species=["Toluene"],
    )

    state_tp = mix.state(T=320.0, x=np.asarray([1.0]), P=101325.0, phase="liq")
    state_trho = mix.state(T=320.0, x=np.asarray([1.0]), rho=state_tp.density(), phase="liq")

    assert state_tp.density() == pytest.approx(state_trho.density())
    assert state_tp.pressure() == pytest.approx(state_trho.pressure())
    assert state_tp.compressibility_factor() == pytest.approx(state_trho.compressibility_factor())
    assert state_tp.residual_helmholtz() == pytest.approx(state_trho.residual_helmholtz())

def test_pressure_based_state_accepts_density_guess_without_changing_closure():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([2.8149]),
            "s": np.asarray([3.7169]),
            "e": np.asarray([285.69]),
        },
        species=["Toluene"],
    )

    base = mix.state(T=320.0, x=np.asarray([1.0]), P=101325.0, phase="liq")
    seeded = mix.state(T=320.0, x=np.asarray([1.0]), P=101325.0, phase="liq", rho_guess=base.density())

    assert seeded.density() == pytest.approx(base.density())
    assert seeded.pressure() == pytest.approx(base.pressure())
    assert seeded.fugacity_coefficient() == pytest.approx(base.fugacity_coefficient())

def test_pressure_based_state_with_poor_density_guess_uses_density_recovery():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([2.8149]),
            "s": np.asarray([3.7169]),
            "e": np.asarray([285.69]),
        },
        species=["Toluene"],
    )

    reference = mix.state(T=320.0, x=np.asarray([1.0]), P=101325.0, phase="liq")
    seeded = mix.state(T=320.0, x=np.asarray([1.0]), P=101325.0, phase="liq", rho_guess=1.0e-6)

    assert seeded.density() == pytest.approx(reference.density())
    assert seeded.pressure() == pytest.approx(reference.pressure())

@pytest.mark.parametrize("rho_guess", [0.0, -1.0, np.inf, np.nan])
def test_pressure_based_state_rejects_invalid_density_guess(rho_guess):
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0]),
            "s": np.asarray([3.0]),
            "e": np.asarray([150.0]),
        }
    )

    with pytest.raises(epcsaft.InputError, match="rho_guess must be finite and positive"):
        mix.state(T=300.0, x=np.asarray([1.0]), P=101325.0, rho_guess=rho_guess)

def test_density_guess_is_only_valid_for_pressure_based_states():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0]),
            "s": np.asarray([3.0]),
            "e": np.asarray([150.0]),
        }
    )

    with pytest.raises(epcsaft.InputError, match="rho_guess is only supported"):
        mix.state(T=300.0, x=np.asarray([1.0]), rho=100.0, rho_guess=100.0)

def test_check_density_reports_pressure_consistency_diagnostics():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([2.8149]),
            "s": np.asarray([3.7169]),
            "e": np.asarray([285.69]),
        },
        species=["Toluene"],
    )

    state = mix.state(T=320.0, x=np.asarray([1.0]), P=101325.0, phase="liq")
    matching = mix.check_density(T=320.0, x=np.asarray([1.0]), P=101325.0, rho=state.density(), phase="liq")
    shifted = mix.check_density(T=320.0, x=np.asarray([1.0]), P=101325.0, rho=state.density() * 0.9, phase="liq")

    assert matching["within_tolerance"] is True
    assert matching["pressure_residual"] == pytest.approx(0.0, abs=1.0e-6)
    assert matching["state"].density() == pytest.approx(state.density())
    assert shifted["within_tolerance"] is False
    assert abs(shifted["pressure_residual"]) > abs(matching["pressure_residual"])
    assert set(shifted) == {
        "density",
        "pressure_target",
        "pressure_from_density",
        "pressure_residual",
        "relative_pressure_residual",
        "within_tolerance",
        "state",
    }

def test_pressure_based_state_raises_solver_error_during_construction():
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0]),
            "s": np.asarray([3.0]),
            "e": np.asarray([150.0]),
        },
        species=["A"],
    )

    with pytest.raises(epcsaft.SolutionError) as excinfo:
        mix.state(T=300.0, x=np.asarray([1.0]), P=1.0e-12, phase="liq")

    message = str(excinfo.value)
    assert "pressure-based state solve failed" in message
    assert "T=300.0" in message
    assert "P=1e-12" in message
    assert "phase=liq" in message
    assert "x=[1.0]" in message
    assert excinfo.value.__cause__ is not None

def test_density_based_native_constructor_failure_raises_public_solution_error(monkeypatch):
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0]),
            "s": np.asarray([3.0]),
            "e": np.asarray([150.0]),
        },
        species=["A"],
    )

    original_native_state = epcsaft_module._core.NativeState

    def raising_native_state(*_args, **_kwargs):
        raise RuntimeError("simulated density native failure")

    monkeypatch.setattr(epcsaft_module._core, "NativeState", raising_native_state)
    with pytest.raises(epcsaft.SolutionError) as excinfo:
        mix.state(T=300.0, x=np.asarray([1.0]), rho=100.0, phase="liq")
    monkeypatch.setattr(epcsaft_module._core, "NativeState", original_native_state)

    message = str(excinfo.value)
    assert "density-based state solve failed" in message
    assert "T=300.0" in message
    assert "rho=100.0" in message
    assert "phase=liq" in message
    assert "ncomp=1" in message
    assert "x=[1.0]" in message
    assert "simulated density native failure" in message
    assert excinfo.value.__cause__ is not None
