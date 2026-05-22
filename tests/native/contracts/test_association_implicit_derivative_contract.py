from __future__ import annotations

import numpy as np
import pytest

import epcsaft._core as _core
from epcsaft.state.native_adapter import create_struct
from tests.support.native_cases import _ionic_state


def _state():
    mix, _species, _pressure, density, temperature, composition = _ionic_state()
    return mix.state(T=temperature, x=composition, rho=density)


def test_active_association_reports_implicit_backend_not_direct_cppad() -> None:
    state = _state()

    association_rows = [row for row in state.derivative_coverage_matrix() if row["quantity"] == "association"]

    assert association_rows
    assert association_rows[0]["backend"] == "analytic_implicit"
    assert association_rows[0]["backend"] != "cppad"


def test_association_composition_derivative_includes_solved_site_fraction_response() -> None:
    mix, _species, _pressure, density, temperature, composition = _ionic_state()
    native_state = _core.NativeState(
        mix._native,
        temperature,
        composition.tolist(),
        0,
        False,
        0.0,
        True,
        density,
        False,
        0.0,
    )

    association_jacobian = np.asarray(
        native_state.composition_derivative_residual_helmholtz_result().dadx.assoc,
        dtype=float,
    )

    assert association_jacobian.shape == (composition.size,)
    assert np.all(np.isfinite(association_jacobian))
    assert np.any(np.abs(association_jacobian) > 1.0e-8)

    public_result = mix.state(T=temperature, x=composition, rho=density).ares_composition_derivative_result()
    assert public_result["backend"] == "analytic_implicit"
    assert public_result["backend_details"]["assoc"] == "analytic_implicit"
    public_jacobian = np.asarray(public_result["jacobian"], dtype=float)
    assert public_jacobian.shape == (1, composition.size)
    assert np.all(np.isfinite(public_jacobian))


def test_association_site_fraction_nonconvergence_raises_with_diagnostics() -> None:
    with pytest.raises(
        _core.NativeSolutionError,
        match=(
            "association site-fraction solve did not converge.*"
            "iteration_count=.*max_iterations=.*update_norm=.*residual_norm=.*min_XA=.*max_XA=.*damping_policy="
        ),
    ):
        _core._native_association_site_fraction_solve(
            [0.0, 1000.0, 1000.0, 0.0],
            1000.0,
            [0.5, 0.5],
            1,
            1.0e-30,
            1.0e-30,
        )


def test_association_site_fraction_solve_reports_convergence_diagnostics() -> None:
    result = _core._native_association_site_fraction_solve(
        [0.0, 0.0, 0.0, 0.0],
        1000.0,
        [0.5, 0.5],
    )

    assert np.asarray(result["site_fractions"], dtype=float) == pytest.approx([1.0, 1.0])
    diagnostics = dict(result["diagnostics"])
    assert diagnostics["converged"] is True
    assert diagnostics["iteration_count"] < diagnostics["max_iterations"]
    assert diagnostics["update_norm"] <= diagnostics["update_tolerance"]
    assert diagnostics["residual_norm"] <= diagnostics["residual_tolerance"]
    assert diagnostics["min_XA"] > 0.0
    assert diagnostics["max_XA"] <= 1.0 + 1.0e-12
    assert diagnostics["damping_policy"] == "fixed_under_relaxation"


def test_direct_cppad_eos_contribution_recording_rejects_active_association() -> None:
    mix, _species, _pressure, density, temperature, composition = _ionic_state()
    args = create_struct(mix.parameters)

    if not _core._native_cppad_smoke()["cppad_compiled"]:
        return

    with pytest.raises(_core.NativeValueError, match="unsupported"):
        _core._native_cppad_eos_contributions(temperature, density, composition.tolist(), args)
