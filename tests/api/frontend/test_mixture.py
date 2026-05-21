from __future__ import annotations

import epcsaft
from tests.support.hydrocarbon_cases import HYDROCARBON_COMPONENTS, hydrocarbon_parameter_set


def test_mixture_owns_only_components_parameters_and_model_options() -> None:
    mixture = epcsaft.Mixture(
        hydrocarbon_parameter_set(),
        components=HYDROCARBON_COMPONENTS,
        model_options=epcsaft.ModelOptions(),
    )

    assert mixture.components == HYDROCARBON_COMPONENTS
    assert not hasattr(mixture, "state")
    assert not hasattr(mixture, "equilibrium")
    assert not hasattr(mixture, "regression")


def test_model_options_are_owned_by_mixture_not_parameter_set() -> None:
    parameters = hydrocarbon_parameter_set()
    model_options = epcsaft.ModelOptions(relative_permittivity_rule="component_linear")

    mixture = epcsaft.Mixture(parameters, model_options=model_options)

    assert mixture.model_options == model_options
    assert mixture.components == HYDROCARBON_COMPONENTS
    assert "model_options" not in parameters.to_json()
