from __future__ import annotations

import json

import epcsaft
import pytest
from support.hydrocarbon_cases import HYDROCARBON_COMPONENTS
from support.model_configurations import (
    NEUTRAL_MODEL_CONFIGURATION,
    neutral_model_options,
    neutral_scientific_parameter_set,
    scientific_hydrocarbon_parameter_set,
)


def test_mixture_owns_only_components_parameters_and_model_options() -> None:
    mixture = epcsaft.Mixture(
        scientific_hydrocarbon_parameter_set(),
        components=HYDROCARBON_COMPONENTS,
        model_options=neutral_model_options(),
    )

    assert mixture.components == HYDROCARBON_COMPONENTS
    assert not hasattr(mixture, "state")
    assert not hasattr(mixture, "equilibrium")
    assert not hasattr(mixture, "regression")


def test_model_options_are_owned_by_mixture_not_parameter_set() -> None:
    parameters = scientific_hydrocarbon_parameter_set()
    model_options = neutral_model_options()

    mixture = epcsaft.Mixture(parameters, model_options=model_options)

    assert mixture.model_options == model_options
    assert mixture.components == HYDROCARBON_COMPONENTS
    assert "model_options" not in parameters.to_json()


def test_model_options_reject_retired_public_keys() -> None:
    invalid = json.loads(json.dumps(NEUTRAL_MODEL_CONFIGURATION))
    invalid["elec_model"] = {"rel_perm": {"rule": 1}}

    with pytest.raises(epcsaft.InputError, match="unknown key"):
        epcsaft.ModelOptions.from_user_options(invalid)


def test_parameter_set_and_configuration_remain_separate_definition_owners() -> None:
    parameters = scientific_hydrocarbon_parameter_set()
    mixture = epcsaft.Mixture(parameters, model_options=neutral_model_options())

    assert "configuration" not in json.loads(parameters.to_json())
    assert mixture.configuration_receipt["configuration"] == neutral_model_options().receipt


def test_model_options_receipt_records_explicit_disabled_neutral_formulation() -> None:
    receipt = neutral_model_options().receipt

    assert receipt["selection_origin"] == "explicit_configuration"
    assert all(not item["enabled"] for item in receipt["formulation"].values())


def test_mixture_from_folder_loads_parameters_and_model_options(tmp_path) -> None:
    root = tmp_path / "case"
    root.mkdir()
    scientific_hydrocarbon_parameter_set().to_json(root / "parameter_set.json")
    (root / "model_configuration.json").write_text(
        json.dumps(NEUTRAL_MODEL_CONFIGURATION)
        + "\n",
        encoding="utf-8",
    )

    mixture = epcsaft.Mixture.from_folder(root, components=HYDROCARBON_COMPONENTS)

    assert mixture.components == HYDROCARBON_COMPONENTS
    assert mixture.model_options.receipt == neutral_model_options().receipt


def test_mixture_requires_explicit_configuration_and_exposes_only_detached_receipt() -> None:
    parameters = neutral_scientific_parameter_set()

    with pytest.raises(TypeError, match="model_options"):
        epcsaft.Mixture(parameters)

    mixture = epcsaft.Mixture(parameters, model_options=neutral_model_options())
    receipt = mixture.configuration_receipt
    receipt["components"][0] = "mutated"

    assert mixture.configuration_receipt["components"] == ["Methane", "Ethane"]
    assert mixture.resolved_model_input.components == ("Methane", "Ethane")
    assert not hasattr(mixture, "native")
    assert not hasattr(mixture, "_runtime_parameters")


def test_displaced_runtime_options_and_schema2_surfaces_are_absent() -> None:
    import epcsaft.model.options as options_module
    from epcsaft.model.parameters import ParameterSource

    assert not hasattr(options_module, "LegacyRuntimeOptionsState")
    assert not hasattr(epcsaft.ModelOptions, "_from_stage4_legacy_runtime_options")
    assert not hasattr(epcsaft.ModelOptions, "_to_stage4_legacy_runtime_options")
    assert not hasattr(epcsaft.ParameterSet, "_to_stage4_legacy_runtime_dict")
    assert not hasattr(ParameterSource, "to_runtime_dict")

    with pytest.raises(epcsaft.InputError, match="schema-3"):
        epcsaft.ParameterSet.from_dict(
            {
                "schema": "epcsaft.parameter-set",
                "schema_version": 2,
                "components": [],
                "pure_records": [],
                "interactions": [],
                "interaction_policies": [],
                "metadata": {},
                "runtime_options": {},
            }
        )
