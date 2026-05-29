from __future__ import annotations

import numpy as np
import pytest

from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()


def test_association_mass_action_block_reports_exact_residual_and_jacobians() -> None:
    density = 0.5
    site_fractions = np.asarray([0.8, 0.6], dtype=float)
    site_composition = np.asarray([0.25, 0.75], dtype=float)
    delta = np.asarray([[0.0, 2.0], [3.0, 0.0]], dtype=float)

    payload = _core._native_association_mass_action_block(
        density,
        site_fractions.tolist(),
        site_composition.tolist(),
        delta.ravel().tolist(),
    )

    association_sums = density * (delta @ (site_composition * site_fractions))
    expected_residuals = site_fractions * (1.0 + association_sums) - 1.0
    expected_site_jacobian = np.diag(1.0 + association_sums) + density * site_fractions[:, None] * delta * site_composition
    expected_composition_jacobian = density * site_fractions[:, None] * delta * site_fractions
    expected_density_derivative = site_fractions * (delta @ (site_composition * site_fractions))
    expected_site_hessian = np.zeros((2, 2, 2), dtype=float)
    for row in range(2):
        for left in range(2):
            for right in range(2):
                if row == left:
                    expected_site_hessian[row, left, right] += density * site_composition[right] * delta[row, right]
                if row == right:
                    expected_site_hessian[row, left, right] += density * site_composition[left] * delta[row, left]

    assert payload["block"] == "association_mass_action"
    assert payload["derivative_backend"] == "analytic"
    assert payload["constraint_names"] == ["association_site_0", "association_site_1"]
    assert payload["site_fraction_hessian_backend"] == "analytic_fixed_delta"
    assert payload["site_fraction_hessian_shape"] == (2, 2, 2)
    assert payload["residuals"] == pytest.approx(expected_residuals.tolist(), rel=1.0e-14, abs=1.0e-14)
    assert np.asarray(payload["site_fraction_jacobian_row_major"], dtype=float).reshape((2, 2)) == pytest.approx(
        expected_site_jacobian,
        rel=1.0e-14,
        abs=1.0e-14,
    )
    assert np.asarray(payload["site_composition_jacobian_row_major"], dtype=float).reshape((2, 2)) == pytest.approx(
        expected_composition_jacobian,
        rel=1.0e-14,
        abs=1.0e-14,
    )
    assert payload["density_derivative"] == pytest.approx(expected_density_derivative.tolist())
    assert np.asarray(payload["site_fraction_hessian_tensor_row_major"], dtype=float).reshape((2, 2, 2)) == pytest.approx(
        expected_site_hessian,
        rel=1.0e-14,
        abs=1.0e-14,
    )
