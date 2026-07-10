from __future__ import annotations

import epcsaft._core as _core
import numpy as np
import pytest
from epcsaft.state.native_adapter import create_struct
from support.runtime_cases import _ionic_params


def _neutral_args():
    return create_struct(
        {
            "m": np.asarray([1.0, 1.6069]),
            "s": np.asarray([3.7039, 3.5206]),
            "e": np.asarray([150.03, 191.42]),
            "k_ij": np.zeros((2, 2)),
        }
    )


def _nonassociating_born_ionic_args():
    params = _ionic_params()
    params["e_assoc"] = np.zeros(3)
    params["vol_a"] = np.zeros(3)
    params["assoc_scheme"] = [None, None, None]
    params["elec_model"] = {
        "rel_perm": {"rule": "empirical", "differential_mode": "cppad"},
        "born_model": {
            "d_Born_mode": "fitted_param",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {"differential_mode": "cppad", "comp_dep_delta_d": True},
        },
    }
    return create_struct(params)


def test_cppad_eos_contribution_recording_matches_double_value_path() -> None:
    args = _neutral_args()
    x = [0.35, 0.65]
    t = 310.0
    rho = 8200.0

    result = _core._native_cppad_eos_contributions(t, rho, x, args)

    state = _core.NativeState(_core.NativeMixture(args), t, x, 0, False, 0.0, True, rho, False, 0.0)
    expected = state.residual_helmholtz_result()

    assert result["derivative_backend"] == "cppad"
    assert result["cppad_used"] is True
    assert result["outputs"] == ["hc", "disp", "assoc", "ion", "born", "total"]
    assert result["variables"] == ["x_0", "x_1"]
    assert result["shape"] == (6, 2)
    assert result["value"] == pytest.approx(
        [expected.hc, expected.disp, expected.assoc, expected.ion, expected.born, expected.total]
    )

    jacobian = np.asarray(result["jacobian_row_major"], dtype=float).reshape(result["shape"])
    assert np.all(np.isfinite(jacobian))
    assert jacobian[-1] == pytest.approx(jacobian[:-1].sum(axis=0))


def test_cppad_eos_contribution_recording_accepts_canonical_born_model() -> None:
    args = _nonassociating_born_ionic_args()
    x = [0.9998, 1.0e-4, 1.0e-4]
    t = 298.15
    rho = 55000.0

    result = _core._native_cppad_eos_contributions(t, rho, x, args)

    state = _core.NativeState(_core.NativeMixture(args), t, x, 0, False, 0.0, True, rho, False, 0.0)
    expected = state.residual_helmholtz_result()
    jacobian = np.asarray(result["jacobian_row_major"], dtype=float).reshape(result["shape"])

    assert result["derivative_backend"] == "cppad"
    assert result["cppad_used"] is True
    assert result["value"][4] == pytest.approx(expected.born)
    assert np.all(np.isfinite(jacobian))
    assert np.any(np.abs(jacobian[4]) > 0.0)


def test_native_born_auto_mode_reports_cppad_composition_backend() -> None:
    args = _nonassociating_born_ionic_args()
    args.mu_born_diff_mode = 3
    args.born_diff_mode = 5
    state = _core.NativeState(
        _core.NativeMixture(args),
        298.15,
        [0.9998, 1.0e-4, 1.0e-4],
        0,
        False,
        0.0,
        True,
        55000.0,
        False,
        0.0,
    )

    result = state.composition_derivative_residual_helmholtz_result()

    assert dict(result.derivative_backend)["born"] == "cppad"
    assert np.all(np.isfinite(result.dadx.born))


def test_native_born_rejects_raw_non_cppad_derivative_mode() -> None:
    args = _nonassociating_born_ionic_args()
    args.mu_born_diff_mode = 0
    args.born_diff_mode = 0
    state = _core.NativeState(
        _core.NativeMixture(args),
        298.15,
        [0.9998, 1.0e-4, 1.0e-4],
        0,
        False,
        0.0,
        True,
        55000.0,
        False,
        0.0,
    )

    with pytest.raises(_core.NativeValueError, match="SSM/DS Born requires CppAD"):
        state.residual_helmholtz_result()


def test_cppad_eos_contribution_recording_rejects_active_association() -> None:
    args = _neutral_args()
    args.assoc_num = [1, 1]

    with pytest.raises(_core.NativeValueError, match="unsupported"):
        _core._native_cppad_eos_contributions(310.0, 8200.0, [0.35, 0.65], args)
