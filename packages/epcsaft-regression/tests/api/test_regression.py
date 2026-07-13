from __future__ import annotations

from api.test_problem_compiler import _controls, _dataset, _mixture, _parameters
from epcsaft_regression import Regression


def test_workflow_object_owns_explicit_controls_and_mixture() -> None:
    mixture = _mixture()
    controls = _controls()

    regression = Regression(mixture, controls=controls)

    assert regression.mixture is mixture
    assert regression.controls is controls


def test_regression_compiles_only_its_configured_provider_definition() -> None:
    regression = Regression(_mixture(), controls=_controls())

    problem = regression.compile(_dataset(), parameters=_parameters())

    assert problem.provider_definition_fingerprint == (
        regression.mixture.resolved_model_input.fingerprint_sha256
    )
    assert problem.controls is regression.controls
    assert problem.row_ids == _dataset().row_ids
