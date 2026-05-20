from __future__ import annotations

from dataclasses import MISSING, fields

import numpy as np
import pytest

import epcsaft
from tests.api.reactive.reactive_regression_cases import (
    _native_mixed_pressure_speciation_batch,
    _tiny_base_parameters,
)
from tests.api.reactive.reactive_speciation_cases import _native_ipopt_compiled


def test_reactive_regression_context_runs_native_speciation_objective_and_jacobian() -> None:
    row = epcsaft.ReactiveElectrolyteRow(
        row_id="native-row",
        T=298.15,
        P=101325.0,
        initial_x=[0.9, 0.05, 0.025, 0.025],
        balances={
            "water": {"H2O": 1.0},
            "sodium": {"NaCl": 1.0, "Na+": 1.0},
            "chloride": {"NaCl": 1.0, "Cl-": 1.0},
        },
        totals={"water": 0.9, "sodium": 0.075, "chloride": 0.075},
        reactions=[
            epcsaft.ReactionDefinition(
                {"NaCl": -1.0, "Na+": 1.0, "Cl-": 1.0},
                np.log(1.0e-2),
                name="salt_dissociation",
                standard_state="mole_fraction_activity",
            )
        ],
        mode="speciation",
    )
    batch = epcsaft.ReactiveElectrolyteBatch(
        species=["H2O", "NaCl", "Na+", "Cl-"],
        rows=[row],
        balances=row.balances,
        reactions=row.reactions,
        base_parameters={
            "MW": np.asarray([18.01528e-3, 58.44e-3, 22.98e-3, 35.45e-3], dtype=float),
            "m": np.asarray([1.2047, 1.0, 1.0, 1.0], dtype=float),
            "s": np.asarray([2.7927, 3.1, 2.8232, 2.7560], dtype=float),
            "e": np.asarray([353.95, 230.0, 230.0, 170.0], dtype=float),
            "z": np.asarray([0.0, 0.0, 1.0, -1.0], dtype=float),
            "dielc": np.asarray([78.09, 78.09, 8.0, 8.0], dtype=float),
            "d_born": np.asarray([0.0, 0.0, 3.0, 3.0], dtype=float),
        },
        options=epcsaft.ReactiveElectrolyteBatchOptions(include_state_outputs=False),
    )
    context = epcsaft.ReactiveElectrolyteRegressionContext.from_batch(
        species=batch.species,
        rows=batch.rows,
        balances=batch.balances,
        reactions=batch.reactions,
        base_parameters=batch.base_parameters,
        options=batch.options,
    )

    objective = context.evaluate_objective({"Na+.sigma": 2.8232})
    assert objective.residual_names == ("native-row.reaction.salt_dissociation",)
    assert objective.residuals.shape == (1,)
    if not _native_ipopt_compiled():
        assert objective.batch_result.success_count == 0
        assert objective.batch_result.failure_count == 1
        assert "EPCSAFT_ENABLE_IPOPT=ON" in objective.batch_result.row_results[0].message
    else:
        assert objective.batch_result.success_count == 1
        assert objective.batch_result.failure_count == 0
        assert objective.batch_result.row_results[0].failure_diagnostics == {}
    with pytest.raises(epcsaft.InputError, match="native Ceres derivative coverage"):
        context.evaluate_derivatives({"Na+.sigma": 2.8232}, parameters=["Na+.sigma"])

def test_reactive_regression_context_evaluates_batch_with_explicit_row_inputs(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_solve(**kwargs):
        bubble_options = None if kwargs["options"] is None else kwargs["options"].bubble_options
        calls.append(
            {
                "P": kwargs["P"],
                "initial_x": list(kwargs["initial_x"]),
                "bubble_options": bubble_options,
            }
        )
        return epcsaft.ReactiveElectrolyteBubbleResult(
            success=True,
            message="converged",
            x_liq={"A": 0.2, "B": 0.8},
            activity_coefficients={"A": 1.1, "B": 0.95},
            mass_balance_residuals={"total": 0.0},
            charge_residual=0.0,
            reaction_residuals=[],
            named_reaction_residuals={},
            P_total=120000.0 + 1000.0 * len(calls),
            y_vap={"A": 0.3, "B": 0.7},
            partial_pressures={"A": 30000.0},
            fugacity_residual={"A": 0.0},
            fugacity_residual_norm=1.0e-9,
            penalty_residuals=[],
            diagnostics={},
        )

    monkeypatch.setattr("epcsaft.reactive_electrolyte.solve_reactive_electrolyte_bubble", fake_solve)

    batch = epcsaft.ReactiveElectrolyteBatch(
        species=["A", "B"],
        rows=[
            epcsaft.ReactiveElectrolyteRow(
                row_id="row1",
                T=298.15,
                P=101325.0,
                totals={"A": 0.2, "B": 0.8},
                initial_x=[0.2, 0.8],
                balances={"a_total": {"A": 1.0}, "b_total": {"B": 1.0}},
                reactions=[],
                vapor_species=["A", "B"],
                target_partial_pressures={"A": 30000.0},
                target_speciation={"A": 0.2},
            ),
            epcsaft.ReactiveElectrolyteRow(
                row_id="row2",
                T=298.15,
                P=95000.0,
                totals={"A": 0.21, "B": 0.79},
                initial_x=[0.21, 0.79],
                balances={"a_total": {"A": 1.0}, "b_total": {"B": 1.0}},
                reactions=[],
                vapor_species=["A", "B"],
                target_partial_pressures={"A": 30000.0},
                target_speciation={"A": 0.2},
            ),
        ],
        balances={"a_total": {"A": 1.0}, "b_total": {"B": 1.0}},
        reactions=[],
        vapor_species=["A", "B"],
        mixture_factory=lambda x, T, P: None,
        options=epcsaft.ReactiveElectrolyteBatchOptions(
            penalty_value=8.0,
            include_state_outputs=False,
        ),
    )
    context = epcsaft.ReactiveElectrolyteRegressionContext.from_batch(
        species=batch.species,
        rows=batch.rows,
        balances=batch.balances,
        reactions=batch.reactions,
        options=batch.options,
        vapor_species=batch.vapor_species,
        mixture_factory=batch.mixture_factory,
    )

    first = context.evaluate()
    second = context.evaluate()

    assert first.success_count == 2
    assert first.failure_count == 0
    assert first.residual_names == (
        "row1.partial_pressure.A",
        "row1.x.A",
        "row2.partial_pressure.A",
        "row2.x.A",
    )
    assert first.residuals.shape == (4,)
    assert second.cache_stats["context_evaluations"] >= 2
    assert calls[1]["P"] == pytest.approx(95000.0)
    assert calls[1]["initial_x"] == pytest.approx([0.21, 0.79])
    assert calls[1]["bubble_options"] is None
    assert first.cache_stats["context_evaluations"] >= 1
