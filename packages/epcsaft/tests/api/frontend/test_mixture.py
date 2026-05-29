from __future__ import annotations

import json
from dataclasses import replace

import pytest

import epcsaft
from support.hydrocarbon_cases import HYDROCARBON_COMPONENTS, hydrocarbon_parameter_set


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


def test_model_options_reject_retired_public_keys() -> None:
    with pytest.raises(epcsaft.InputError, match="retired public option"):
        epcsaft.ModelOptions.from_user_options({"elec_model": {"rel_perm": {"rule": 1}}})


def test_parameter_set_round_trips_resolved_runtime_options_without_reparsing_public_schema() -> None:
    parameters = hydrocarbon_parameter_set()
    runtime_options = epcsaft.ModelOptions(
        relative_permittivity_rule="linear",
        born_model=epcsaft.BornModelOptions(
            enabled=True,
            born_diameter_rule="fitted",
            solvation_shell_model=False,
            dielectric_saturation=False,
        ),
    ).to_runtime_options(parameters)

    configured = replace(parameters, runtime_options=runtime_options)
    payload = configured.to_runtime_dict()

    assert payload["elec_model"]["include_born_model"] is True
    assert payload["elec_model"]["born_model"]["d_Born_mode"] == 3


def test_model_options_help_and_explain_describe_autodiff_born_defaults() -> None:
    options = epcsaft.ModelOptions()

    assert "autodiff" in epcsaft.ModelOptions.help()
    assert options.born_model.enabled is True
    assert options.born_model.solvation_shell_model is True
    assert options.born_model.dielectric_saturation is True
    assert "CppAD" in options.explain()


def test_mixture_from_folder_loads_parameters_and_model_options(tmp_path) -> None:
    root = tmp_path / "case"
    root.mkdir()
    hydrocarbon_parameter_set().to_json(root / "parameter_set.json")
    (root / "model_options.json").write_text(
        json.dumps(
            {
                "differential_mode": "autodiff",
                "relative_permittivity_rule": "constant",
                "born_model": {"enabled": False},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    mixture = epcsaft.Mixture.from_folder(root, components=HYDROCARBON_COMPONENTS)

    assert mixture.components == HYDROCARBON_COMPONENTS
    assert mixture.model_options.relative_permittivity_rule == "constant"
    assert mixture.model_options.born_model.enabled is False
