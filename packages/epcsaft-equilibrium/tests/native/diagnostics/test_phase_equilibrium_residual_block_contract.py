from __future__ import annotations

import numpy as np
import pytest

from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()


def _symmetric_ternary_nonassociating_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.5, 1.5, 1.5], dtype=float),
        "s": np.asarray([3.7, 3.7, 3.7], dtype=float),
        "e": np.asarray([220.0, 220.0, 220.0], dtype=float),
        "k_ij": np.asarray(
            [
                [0.0, 0.8, 0.8],
                [0.8, 0.0, 0.8],
                [0.8, 0.8, 0.0],
            ],
            dtype=float,
        ),
    }
    return ePCSAFTMixture.from_params(params, species=["A", "B", "C"])


def _three_phase_amount_volume_case() -> tuple[list[list[float]], list[float]]:
    phase_compositions = [
        np.asarray([0.985, 0.010, 0.005], dtype=float),
        np.asarray([0.010, 0.985, 0.005], dtype=float),
        np.asarray([0.010, 0.005, 0.985], dtype=float),
    ]
    phase_totals = np.asarray([0.34, 0.33, 0.33], dtype=float)
    density = 1_000.0
    phase_amounts = [(total * composition).tolist() for total, composition in zip(phase_totals, phase_compositions)]
    volumes = [float(total / density) for total in phase_totals]
    return phase_amounts, volumes


def test_phase_equilibrium_residual_block_contract_reports_square_three_phase_layout() -> None:
    mix = _symmetric_ternary_nonassociating_mixture()
    phase_amounts, volumes = _three_phase_amount_volume_case()

    payload = _core._native_phase_equilibrium_residual_block_contract(
        mix._native,
        200.0,
        1.0e6,
        phase_amounts,
        volumes,
    )

    assert payload["block"] == "phase_equilibrium_residual"
    assert payload["phase_count"] == 3
    assert payload["species_count"] == 3
    assert payload["variable_count"] == 12
    assert payload["constraint_count"] == 6
    assert payload["residual_count"] == 6
    assert payload["full_square_constraint_count"] == 12
    assert payload["jacobian_backend"] in {
        "cppad_explicit_density",
        "cppad_explicit_density_implicit_association",
    }
    assert payload["hessian_backend"] in {
        "cppad_explicit_density",
        "cppad_explicit_density_implicit_association",
    }
    assert payload["exact_jacobian_available"] is True
    assert payload["exact_hessian_available"] is True
    assert payload["residual_names"] == [
        "phase_1.reduced_ln_fugacity_0_minus_phase_0",
        "phase_1.reduced_ln_fugacity_1_minus_phase_0",
        "phase_1.reduced_ln_fugacity_2_minus_phase_0",
        "phase_2.reduced_ln_fugacity_0_minus_phase_0",
        "phase_2.reduced_ln_fugacity_1_minus_phase_0",
        "phase_2.reduced_ln_fugacity_2_minus_phase_0",
    ]


def test_phase_equilibrium_residual_block_reports_exact_chain_rule_derivatives() -> None:
    mix = _symmetric_ternary_nonassociating_mixture()
    phase_amounts, volumes = _three_phase_amount_volume_case()

    payload = _core._native_phase_equilibrium_residual_block_contract(
        mix._native,
        200.0,
        1.0e6,
        phase_amounts,
        volumes,
    )

    for key in (
        "density_amount_jacobian",
        "composition_amount_jacobian",
        "reduced_fugacity_local_jacobian_shape",
        "reduced_fugacity_local_hessian_shape",
        "residual_jacobian_nonzero_count",
        "residual_hessian_nonzero_count",
    ):
        assert payload[key]

    density_amount_jacobian = np.asarray(payload["density_amount_jacobian"], dtype=float).reshape((3, 4))
    first_phase_total = float(np.sum(phase_amounts[0]))
    first_phase_volume = volumes[0]
    assert density_amount_jacobian[0, :3] == pytest.approx([1.0 / first_phase_volume] * 3)
    assert density_amount_jacobian[0, 3] == pytest.approx(-first_phase_total / first_phase_volume**2)
    assert payload["reduced_fugacity_local_jacobian_shape"] == (3, 4)
    assert payload["reduced_fugacity_local_hessian_shape"] == (3, 4, 4)
    assert payload["global_jacobian_shape"] == (6, 12)
    assert payload["global_hessian_shape"] == (6, 12, 12)


def test_phase_equilibrium_residual_block_keeps_trace_component_derivatives_finite() -> None:
    mix = _symmetric_ternary_nonassociating_mixture()
    phase_amounts, volumes = _three_phase_amount_volume_case()
    phase_amounts[2][1] = 1.0e-9
    phase_amounts[2][0] = 0.004999999
    phase_amounts[2][2] = 0.325
    volumes[2] = float(sum(phase_amounts[2]) / 1_000.0)

    payload = _core._native_phase_equilibrium_residual_block_contract(
        mix._native,
        200.0,
        1.0e6,
        phase_amounts,
        volumes,
    )

    assert np.all(np.isfinite(np.asarray(payload["residuals"], dtype=float)))
    assert np.all(np.isfinite(np.asarray(payload["jacobian_row_major"], dtype=float)))
    assert np.all(np.isfinite(np.asarray(payload["hessian_tensor_row_major"], dtype=float)))
    assert min(payload["phase_minimum_compositions"]) > 0.0
