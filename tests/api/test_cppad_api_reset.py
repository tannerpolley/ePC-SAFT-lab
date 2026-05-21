from __future__ import annotations

import json

import numpy as np
import pytest

import epcsaft
import epcsaft.eos as eos
from epcsaft import _core
from tests.support.regression_cases import (
    _load_workbook_reference_rows,
    _neutral_fixed_parameters,
    _real_saturation_records,
)
from tests.support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_COMPONENTS,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_RHO,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)


def test_root_public_api_is_reset_to_clean_frontend_names() -> None:
    required = {
        "Mixture",
        "State",
        "Equilibrium",
        "Regression",
        "ParameterSet",
        "ModelOptions",
        "create_input_template",
    }
    legacy = {
        "ePCSAFTMixture",
        "ePCSAFTState",
        "bubble_p",
        "dew_p",
        "fit_pure_neutral",
        "fit_pure_parameters",
        "BubblePoint",
        "TPFlash",
    }

    assert required <= set(epcsaft.__all__)
    assert legacy.isdisjoint(epcsaft.__all__)
    for name in legacy:
        assert not hasattr(epcsaft, name)
        assert not hasattr(eos, name)
    assert eos.Mixture is epcsaft.Mixture
    assert eos.State is epcsaft.State


def test_model_options_are_owned_by_mixture_not_parameter_set() -> None:
    parameters = hydrocarbon_parameter_set()
    model_options = epcsaft.ModelOptions(relative_permittivity_rule="component_linear")

    mixture = epcsaft.Mixture(parameters, model_options=model_options)

    assert mixture.model_options == model_options
    assert mixture.components == HYDROCARBON_COMPONENTS
    assert "model_options" not in parameters.to_json()


def test_cppad_state_proves_hydrocarbon_values_and_derivatives() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    state = mixture.state(T=HYDROCARBON_T, P=HYDROCARBON_BUBBLE_P, x=HYDROCARBON_LIQUID_X, phase="liq")

    assert isinstance(state, epcsaft.State)
    assert state.molar_density() == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=5.0e-5)
    assert state.compressibility_factor() == pytest.approx(0.0459462, rel=5.0e-5)
    assert state.ln_fugacity_coefficients() == pytest.approx(
        np.asarray([1.9324151168689134, -0.5740965595882255, -2.407779856320623]), rel=5.0e-5
    )

    pressure_density = state.pressure_density_derivative()
    fugacity_composition = state.ln_fugacity_composition_derivative()

    assert pressure_density["derivative_backend"] == "cppad"
    assert pressure_density["jacobian"].shape == (1, 1)
    assert fugacity_composition["derivative_backend"].startswith("cppad")
    assert fugacity_composition["jacobian"].shape == (3, 3)


def test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    result = epcsaft.Mixture(hydrocarbon_parameter_set()).equilibrium(
        max_iterations=200,
        tolerance=1.0e-8,
        ipopt_iteration_history_limit=4,
    ).bubble_pressure(T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X)

    diagnostics = result.diagnostics
    assert result.problem_kind == "neutral_bubble_p"
    assert result.phases[0].composition == pytest.approx(HYDROCARBON_LIQUID_X, abs=1.0e-10)
    assert result.phases[1].composition == pytest.approx(HYDROCARBON_VAPOR_Y, rel=5.0e-5, abs=5.0e-7)
    assert result.phases[0].pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.phases[0].density == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=5.0e-5)
    assert result.phases[1].density == pytest.approx(HYDROCARBON_VAPOR_RHO, rel=5.0e-5)
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["eval_h_calls"] > 0


def test_regression_hydrocarbon_anchor_routes_through_new_object_api() -> None:
    reference = _load_workbook_reference_rows()["Methane"]

    debug = epcsaft.Mixture(hydrocarbon_parameter_set()).regression().evaluate_pure_neutral_derivatives(
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


def test_create_input_template_writes_parameters_and_workflow_options(tmp_path) -> None:
    root = epcsaft.create_input_template(
        tmp_path / "case",
        components=("Methane", "Ethane"),
        workflows=("state", "equilibrium", "regression"),
    )

    expected_files = {
        "pure_parameters.csv",
        "binary_parameters.csv",
        "permittivity_parameters.csv",
        "model_options.json",
        "state_options.json",
        "equilibrium_options.json",
        "regression_options.json",
    }
    assert {path.name for path in root.iterdir()} == expected_files
    assert (root / "pure_parameters.csv").read_text(encoding="utf-8").splitlines()[0].startswith("component,")
    assert json.loads((root / "model_options.json").read_text(encoding="utf-8"))["relative_permittivity_rule"]
    assert "Methane" in (root / "pure_parameters.csv").read_text(encoding="utf-8")
