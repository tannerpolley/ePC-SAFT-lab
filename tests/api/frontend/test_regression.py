from __future__ import annotations

import pytest

import epcsaft
from tests.support.hydrocarbon_cases import hydrocarbon_parameter_set
from tests.support.regression_cases import (
    _load_workbook_reference_rows,
    _neutral_fixed_parameters,
    _real_saturation_records,
)


def test_workflow_object_is_constructed_directly() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    regression = epcsaft.Regression(mixture)

    assert regression.mixture is mixture


def test_regression_hydrocarbon_anchor_routes_through_new_object_api() -> None:
    reference = _load_workbook_reference_rows()["Methane"]

    debug = epcsaft.Regression(epcsaft.Mixture(hydrocarbon_parameter_set())).evaluate_pure_neutral_derivatives(
        _real_saturation_records("Methane"),
        component="Methane",
        assoc_scheme="",
        fixed_parameters=_neutral_fixed_parameters("Methane"),
        initial_guess=reference,
        x=reference,
    )

    assert debug["objective"] == pytest.approx(9.701615164740784e-06, rel=2.0e-4)
    assert debug["jacobian_shape"] == (8, 3)
    assert debug["jacobian_backend"].startswith("cppad")
    assert debug["density_solves"] >= 4
    assert debug["fused_state_evaluations"] >= 4
