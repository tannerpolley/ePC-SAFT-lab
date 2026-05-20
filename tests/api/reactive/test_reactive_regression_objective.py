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


def test_reactive_regression_objective_and_jacobian_are_consistent(monkeypatch) -> None:
    def fake_solve(**kwargs):
        mix = kwargs["mixture_factory"](kwargs["initial_x"], kwargs["T"], kwargs["P"])
        sigma = float(np.asarray(mix._params["s"], dtype=float)[0])
        pressure = 100000.0 + 1000.0 * (sigma - 3.0)
        x_a = 0.2 + 0.01 * (sigma - 3.0)
        return epcsaft.ReactiveElectrolyteBubbleResult(
            success=True,
            message="converged",
            x_liq={"A": x_a, "B": 1.0 - x_a},
            activity_coefficients={"A": 1.0, "B": 1.0},
            mass_balance_residuals={"total": 0.0},
            charge_residual=0.0,
            reaction_residuals=[],
            named_reaction_residuals={},
            P_total=pressure,
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
                target_pressure=100000.0,
                target_speciation={"A": 0.2},
            )
        ],
        balances={"a_total": {"A": 1.0}, "b_total": {"B": 1.0}},
        reactions=[],
        vapor_species=["A", "B"],
        base_parameters=_tiny_base_parameters(),
        options=epcsaft.ReactiveElectrolyteBatchOptions(include_state_outputs=False),
    )
    context = epcsaft.ReactiveElectrolyteRegressionContext.from_batch(
        species=batch.species,
        rows=batch.rows,
        balances=batch.balances,
        reactions=batch.reactions,
        options=batch.options,
        vapor_species=batch.vapor_species,
        base_parameters=batch.base_parameters,
    )

    objective = context.evaluate_objective({"A.sigma": 3.0})
    assert objective.residuals.shape == (2,)
    with pytest.raises(epcsaft.InputError, match="native Ceres derivative coverage"):
        context.evaluate_derivatives({"A.sigma": 3.0}, parameters=["A.sigma"])
