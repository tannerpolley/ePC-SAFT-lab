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


def test_reactive_electrolyte_regression_public_surfaces_are_current() -> None:
    row_fields = fields(epcsaft.ReactiveElectrolyteRow)
    row_names = tuple(field.name for field in row_fields)
    option_names = tuple(field.name for field in fields(epcsaft.ReactiveElectrolyteBatchOptions))
    result_names = tuple(field.name for field in fields(epcsaft.ReactiveElectrolyteRowResult))

    assert row_names == (
        "row_id",
        "T",
        "P",
        "initial_x",
        "balances",
        "totals",
        "reactions",
        "vapor_species",
        "target_pressure",
        "target_speciation",
        "target_activity",
        "target_fugacity",
        "target_density",
        "target_relative_permittivity",
        "target_partial_pressures",
        "weights",
        "source",
        "split",
        "metadata",
        "mode",
    )
    assert row_fields[2].default is MISSING
    assert option_names == ("penalty_value", "failure_residual_mode", "include_state_outputs")
    assert result_names == (
        "row_id",
        "success",
        "message",
        "composition",
        "pressure",
        "ln_fugacity",
        "activity_coefficients",
        "density",
        "relative_permittivity",
        "residuals",
        "residual_names",
        "failure_diagnostics",
        "active_bounds",
        "elapsed_seconds",
        "partial_pressures",
        "y_vap",
        "named_reaction_residuals",
        "source",
        "split",
        "metadata",
    )
