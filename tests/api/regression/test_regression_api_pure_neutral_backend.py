from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft import fit_pure_neutral
from epcsaft._types import InputError
from epcsaft.regression import _debug_native_pure_neutral_objective
from tests.api.regression.native_backend_cases import (
    _minimal_nacl_records,
    _patch_native_generic_ceres_runner,
)
from tests.helpers.regression_cases import _methane_like_records, _minimal_neutral_metadata


def test_fit_pure_neutral_requires_pressure_for_density_records():
    with pytest.raises(InputError, match="experimental 'P'"):
        fit_pure_neutral(
            [{"T": 320.0, "rho": 9000.0}],
            "Toluene",
            assoc_scheme="",
            fixed_parameters=_minimal_neutral_metadata(92.141e-3),
            initial_guess={"m": 2.8, "s": 3.7, "e": 285.0},
        )

def test_fit_pure_neutral_rejects_non_phase1_targets():
    with pytest.raises(InputError, match="supports only the targets 'm', 's', and 'e'"):
        fit_pure_neutral(
            [{"T": 320.0, "P": 101325.0, "rho": 9000.0}],
            "Toluene",
            assoc_scheme="",
            fit_targets=("m", "s", "e_assoc"),
            fixed_parameters=_minimal_neutral_metadata(92.141e-3),
            initial_guess={"m": 2.8, "s": 3.7, "e_assoc": 1000.0},
        )

def test_native_pure_neutral_debug_gradient_reports_cppad_implicit_backend():
    theta = {"m": 1.05, "s": 3.68, "e": 151.0}
    debug = _debug_native_pure_neutral_objective(
        _methane_like_records(),
        "Methane",
        assoc_scheme="",
        fixed_parameters=_minimal_neutral_metadata(16.043e-3),
        initial_guess=theta,
        x=theta,
    )
    exact = np.asarray(debug["gradient"], dtype=float)
    assert np.all(np.isfinite(exact))
    assert debug["jacobian_backend"] == "cppad_implicit"
    assert debug["residual_evaluations"] >= 1
    assert debug["density_solves"] >= 2
    assert debug["fused_state_evaluations"] >= 2
    assert debug["callback_wall_time_s"] >= 0.0
    assert debug["jacobian_available"] is True
    assert tuple(debug["jacobian_shape"]) == (len(debug["residuals"]), 3)
    assert np.asarray(debug["jacobian_row_major"], dtype=float).shape == (len(debug["residuals"]) * 3,)

def test_fit_pure_neutral_rejects_non_ceres_backend():
    with pytest.raises(InputError, match="Unsupported optimizer_backend"):
        fit_pure_neutral(
            _methane_like_records(),
            "Methane",
            assoc_scheme="",
            fixed_parameters=_minimal_neutral_metadata(16.043e-3),
            initial_guess={"m": 1.08, "s": 3.55, "e": 155.0},
            bounds={
                "m": (0.5, 3.5),
                "s": (2.0, 5.0),
                "e": (50.0, 400.0),
            },
            optimizer_backend="native_optimizer",
        )

@pytest.mark.parametrize(
    "initial_guess",
    [
        {"m": 1.08, "s": 3.55, "e": 155.0},
        {"m": 0.92, "s": 3.90, "e": 143.0},
        {"m": 1.20, "s": 3.30, "e": 170.0},
    ],
)
def test_public_pure_neutral_regression_is_robust_to_distinct_initial_guesses(initial_guess):
    records = _methane_like_records()
    result = fit_pure_neutral(
        records,
        "Methane",
        assoc_scheme="",
        fixed_parameters=_minimal_neutral_metadata(16.043e-3),
        initial_guess=initial_guess,
        bounds={
            "m": (0.5, 3.5),
            "s": (2.0, 5.0),
            "e": (50.0, 400.0),
        },
    )
    assert result.success, result.message
    assert result.backend == "ceres"
    assert result.optimizer_backend == "ceres"
    assert result.metrics_by_term["density"] < 0.02
    assert result.metrics_by_term["pure_vle_fugacity_balance"] < 0.02
    assert result.fitted_values["m"] == pytest.approx(1.0, rel=0.0, abs=0.06)
    assert result.fitted_values["s"] == pytest.approx(3.7039, rel=0.0, abs=0.10)
    assert result.fitted_values["e"] == pytest.approx(150.03, rel=0.0, abs=4.0)
    assert result.initial_parameters == initial_guess
    assert result.final_parameters == result.fitted_values
    assert result.parameter_movement == {
        name: pytest.approx(result.fitted_values[name] - initial_guess[name]) for name in ("m", "s", "e")
    }
    assert result.source_summaries["records"]["record_count"] == len(records)
    assert result.provenance_report["initial_parameters"] == initial_guess
    assert result.provenance_report["final_parameters"] == result.fitted_values
