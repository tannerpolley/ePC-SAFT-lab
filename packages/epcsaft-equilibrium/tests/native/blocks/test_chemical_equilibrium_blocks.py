from __future__ import annotations

import math

import epcsaft._core as _provider_core
import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()


def _evaluate_block(
    *,
    amounts: list[float],
    stoichiometry: list[float],
    log_k: list[float],
    conservation_matrix: list[float],
    conservation_totals: list[float],
) -> dict[str, object]:
    return _core._native_chemical_equilibrium_block(
        amounts,
        len(log_k),
        stoichiometry,
        len(conservation_totals),
        conservation_matrix,
        conservation_totals,
        log_k,
    )


def test_ideal_a_to_b_reports_balances_affinity_and_exact_derivatives() -> None:
    result = _evaluate_block(
        amounts=[0.25, 0.75],
        stoichiometry=[-1.0, 1.0],
        log_k=[math.log(3.0)],
        conservation_matrix=[1.0, 1.0],
        conservation_totals=[1.0],
    )

    assert result["model"] == "homogeneous_chemical_equilibrium"
    assert result["residual_families"] == ["conservation_balance", "reaction_affinity"]
    assert result["balance_residuals"] == pytest.approx([0.0])
    assert result["reaction_affinities"] == pytest.approx([0.0], abs=1.0e-14)
    assert result["reaction_residuals"] == pytest.approx([0.0], abs=1.0e-14)
    assert result["gradient"] == pytest.approx(result["objective_gradient"])
    assert result["hessian_row_major"] == pytest.approx([3.0, -1.0, -1.0, 1.0 / 3.0])
    assert result["balance_jacobian_row_major"] == pytest.approx([1.0, 1.0])
    assert result["affinity_jacobian_row_major"] == pytest.approx([-4.0, 4.0 / 3.0])
    assert result["exact_derivative_metadata"] == {
        "derivative_backend": "analytic",
        "objective_gradient_exact": True,
        "balance_jacobian_exact": True,
        "affinity_jacobian_exact": True,
        "objective_hessian_exact": True,
        "hessian_backend": "analytic",
    }
    assert result["domain_margins"]["minimum_amount"] == pytest.approx(0.25)
    assert result["domain_margins"]["amount_lower_margin"] == pytest.approx(0.25)
    assert result["scaling"]["objective_scaling"] > 0.0
    assert result["scaling"]["variable_scaling"] == pytest.approx([1.0, 1.0])
    assert result["scaling"]["balance_scaling"] == pytest.approx([1.0])
    assert result["scaling"]["affinity_scaling"] == pytest.approx([1.0])


def test_associating_stoichiometry_reports_affinity_jacobian_and_hessian_shape() -> None:
    log_k = math.log(15.0)
    result = _evaluate_block(
        amounts=[0.25, 0.25, 0.75],
        stoichiometry=[-1.0, -1.0, 1.0],
        log_k=[log_k],
        conservation_matrix=[1.0, 0.0, 1.0, 0.0, 1.0, 1.0],
        conservation_totals=[1.0, 1.0],
    )

    assert result["balance_residuals"] == pytest.approx([0.0, 0.0])
    assert result["reaction_affinities"] == pytest.approx([0.0], abs=1.0e-14)
    assert result["affinity_jacobian_row_major"] == pytest.approx([-3.2, -3.2, 2.1333333333333333])
    assert len(result["hessian_row_major"]) == 9
    assert result["hessian_row_major"][0] == pytest.approx(1.0 / 0.25 - 1.0 / 1.25)
    assert result["hessian_row_major"][4] == pytest.approx(1.0 / 0.25 - 1.0 / 1.25)
    assert result["hessian_row_major"][8] == pytest.approx(1.0 / 0.75 - 1.0 / 1.25)
    assert result["constraint_count"] == 2
    assert result["reaction_count"] == 1
    assert result["species_count"] == 3


def test_charged_conservation_rows_report_charge_balance_and_domain_margin() -> None:
    amounts = [0.98, 0.01, 0.01]
    log_k = math.log((0.01 * 0.01) / 0.98)
    result = _evaluate_block(
        amounts=amounts,
        stoichiometry=[-1.0, 1.0, 1.0],
        log_k=[log_k],
        conservation_matrix=[2.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, -1.0],
        conservation_totals=[1.98, 0.99, 0.0],
    )

    assert result["balance_residuals"] == pytest.approx([0.0, 0.0, 0.0])
    assert result["reaction_affinities"] == pytest.approx([0.0], abs=1.0e-14)
    assert result["domain_margins"]["minimum_amount"] == pytest.approx(0.01)
    assert result["domain_safety_policy"] == "strict_positive_amounts"


def test_native_chemical_equilibrium_block_rejects_nonpositive_amounts() -> None:
    with pytest.raises(_provider_core.NativeValueError, match="positive"):
        _evaluate_block(
            amounts=[1.0, 0.0],
            stoichiometry=[-1.0, 1.0],
            log_k=[0.0],
            conservation_matrix=[1.0, 1.0],
            conservation_totals=[1.0],
        )
