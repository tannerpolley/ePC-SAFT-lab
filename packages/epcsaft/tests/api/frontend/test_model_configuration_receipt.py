from __future__ import annotations

import copy
import json
from pathlib import Path

import epcsaft
import pytest
from support.model_configurations import neutral_scientific_parameter_set

MODEL_CONFIGURATION_SCHEMA = "epcsaft.model-configuration"
MODEL_CONFIGURATION_SCHEMA_VERSION = 1
MODEL_CONFIGURATION_FILENAME = "model_configuration.json"
MODEL_CONFIGURATION_PRESETS: tuple[str, ...] = ()


EXPLICIT_NEUTRAL_CONFIGURATION = {
    "schema": "epcsaft.model-configuration",
    "schema_version": 1,
    "selection_origin": "explicit_configuration",
    "formulation": {
        "electrostatics": {"enabled": False},
        "relative_permittivity": {"enabled": False},
        "debye_huckel": {"enabled": False},
        "born": {"enabled": False},
        "solvated_ion_diameter": {"enabled": False},
        "ion_dispersion": {"enabled": False},
    },
}

EXPLICIT_ELECTROLYTE_CONFIGURATION = {
    "schema": "epcsaft.model-configuration",
    "schema_version": 1,
    "selection_origin": "explicit_configuration",
    "formulation": {
        "electrostatics": {"enabled": True},
        "relative_permittivity": {"enabled": True, "rule": "component_linear"},
        "debye_huckel": {
            "enabled": True,
            "ion_diameter_rule": "sigma_reduced",
            "bjerrum_pairing": False,
        },
        "born": {
            "enabled": True,
            "born_diameter_rule": "sigma",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "bulk_mode": "mix",
        },
        "solvated_ion_diameter": {"enabled": False},
        "ion_dispersion": {"enabled": True},
    },
}


def _parse(payload: dict[str, object]) -> epcsaft.ModelOptions:
    return epcsaft.ModelOptions.from_user_options(copy.deepcopy(payload))


def test_explicit_neutral_configuration_has_a_detached_deterministic_receipt() -> None:
    options = _parse(EXPLICIT_NEUTRAL_CONFIGURATION)

    first = options.receipt
    first["formulation"]["born"]["enabled"] = True

    assert options.receipt == EXPLICIT_NEUTRAL_CONFIGURATION
    assert options.receipt is not options.receipt


def test_complete_explicit_electrolyte_configuration_round_trips() -> None:
    options = _parse(EXPLICIT_ELECTROLYTE_CONFIGURATION)

    assert options.receipt == EXPLICIT_ELECTROLYTE_CONFIGURATION
    assert options.born.enabled is True
    assert options.relative_permittivity.rule == "component_linear"
    assert options.debye_huckel.ion_diameter_rule == "sigma_reduced"


@pytest.mark.parametrize(
    ("formulation", "field", "value"),
    (
        ("relative_permittivity", "rule", "invented"),
        ("debye_huckel", "ion_diameter_rule", "invented"),
        ("born", "born_diameter_rule", "invented"),
        ("born", "bulk_mode", "invented"),
    ),
)
def test_enabled_formulations_reject_unsupported_tokens(formulation: str, field: str, value: str) -> None:
    payload = copy.deepcopy(EXPLICIT_ELECTROLYTE_CONFIGURATION)
    payload["formulation"][formulation][field] = value

    with pytest.raises(epcsaft.InputError, match=r"unsupported|must be"):
        _parse(payload)


@pytest.mark.parametrize(
    ("formulation", "field"),
    (
        ("debye_huckel", "bjerrum_pairing"),
        ("born", "solvation_shell_model"),
        ("born", "dielectric_saturation"),
    ),
)
def test_enabled_formulation_boolean_fields_are_strict(formulation: str, field: str) -> None:
    payload = copy.deepcopy(EXPLICIT_ELECTROLYTE_CONFIGURATION)
    payload["formulation"][formulation][field] = "true"

    with pytest.raises(epcsaft.InputError, match="must be a boolean"):
        _parse(payload)


@pytest.mark.parametrize("missing", ("schema", "schema_version", "selection_origin", "formulation"))
def test_model_configuration_rejects_each_missing_top_level_key(missing: str) -> None:
    payload = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    del payload[missing]

    with pytest.raises(epcsaft.InputError, match="missing required key"):
        _parse(payload)


@pytest.mark.parametrize("missing", tuple(EXPLICIT_NEUTRAL_CONFIGURATION["formulation"]))
def test_model_configuration_rejects_each_missing_formulation(missing: str) -> None:
    payload = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    del payload["formulation"][missing]

    with pytest.raises(epcsaft.InputError, match="missing required key"):
        _parse(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("schema", "epcsaft.other"),
        ("schema", 1),
        ("schema_version", 2),
        ("schema_version", "1"),
        ("schema_version", True),
        ("selection_origin", "preset"),
    ),
)
def test_model_configuration_rejects_wrong_schema_and_selection_scalars(field: str, value: object) -> None:
    payload = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    payload[field] = value

    with pytest.raises(epcsaft.InputError):
        _parse(payload)


@pytest.mark.parametrize("value", (0, 1, "false", "true", None))
def test_model_configuration_booleans_are_strict(value: object) -> None:
    payload = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    payload["formulation"]["born"]["enabled"] = value

    with pytest.raises(epcsaft.InputError, match="must be a boolean"):
        _parse(payload)


def test_model_configuration_rejects_unknown_top_level_and_nested_keys() -> None:
    top = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    top["unexpected"] = True
    nested = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    nested["formulation"]["born"]["unexpected"] = True

    with pytest.raises(epcsaft.InputError, match="unknown key"):
        _parse(top)
    with pytest.raises(epcsaft.InputError, match="unknown key"):
        _parse(nested)


def test_disabled_formulations_reject_active_only_fields() -> None:
    payload = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    payload["formulation"]["born"]["bulk_mode"] = "mix"

    with pytest.raises(epcsaft.InputError, match="disabled formulation"):
        _parse(payload)


@pytest.mark.parametrize(
    ("formulation", "missing"),
    (
        ("relative_permittivity", "rule"),
        ("debye_huckel", "ion_diameter_rule"),
        ("debye_huckel", "bjerrum_pairing"),
        ("born", "born_diameter_rule"),
        ("born", "solvation_shell_model"),
        ("born", "dielectric_saturation"),
        ("born", "bulk_mode"),
    ),
)
def test_enabled_formulations_reject_partial_choices(formulation: str, missing: str) -> None:
    payload = copy.deepcopy(EXPLICIT_ELECTROLYTE_CONFIGURATION)
    del payload["formulation"][formulation][missing]

    with pytest.raises(epcsaft.InputError, match="missing required key"):
        _parse(payload)


def test_neutral_parent_switch_does_not_allow_enabled_dependents() -> None:
    payload = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    payload["formulation"]["born"] = copy.deepcopy(EXPLICIT_ELECTROLYTE_CONFIGURATION["formulation"]["born"])

    with pytest.raises(epcsaft.InputError, match="electrostatics is disabled"):
        _parse(payload)


def test_direct_model_options_construction_is_closed() -> None:
    with pytest.raises(TypeError):
        epcsaft.ModelOptions()


def test_empty_preset_catalog_rejects_preset_and_conflicting_selection() -> None:
    preset = {
        "schema": MODEL_CONFIGURATION_SCHEMA,
        "schema_version": MODEL_CONFIGURATION_SCHEMA_VERSION,
        "selection_origin": "admitted_preset",
        "preset_id": "not-admitted",
    }
    conflict = copy.deepcopy(EXPLICIT_NEUTRAL_CONFIGURATION)
    conflict["preset_id"] = "not-admitted"

    assert MODEL_CONFIGURATION_PRESETS == ()
    with pytest.raises(epcsaft.InputError, match="no admitted presets"):
        _parse(preset)
    with pytest.raises(epcsaft.InputError, match="cannot include preset_id"):
        _parse(conflict)


def test_folder_requires_only_the_canonical_configuration_filename(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    missing.mkdir()
    retired = tmp_path / "retired"
    retired.mkdir()
    (retired / "user_options.json").write_text("{}\n", encoding="utf-8")
    both = tmp_path / "both"
    both.mkdir()
    (both / MODEL_CONFIGURATION_FILENAME).write_text(
        json.dumps(EXPLICIT_NEUTRAL_CONFIGURATION) + "\n", encoding="utf-8"
    )
    (both / "model_options.json").write_text("{}\n", encoding="utf-8")
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / MODEL_CONFIGURATION_FILENAME).write_text(
        json.dumps(EXPLICIT_NEUTRAL_CONFIGURATION) + "\n", encoding="utf-8"
    )

    with pytest.raises(epcsaft.InputError, match=MODEL_CONFIGURATION_FILENAME):
        epcsaft.ModelOptions.from_user_options(missing)
    with pytest.raises(epcsaft.InputError, match="unsupported"):
        epcsaft.ModelOptions.from_user_options(retired)
    with pytest.raises(epcsaft.InputError, match="unsupported"):
        epcsaft.ModelOptions.from_user_options(both)
    assert epcsaft.ModelOptions.from_user_options(canonical).receipt == EXPLICIT_NEUTRAL_CONFIGURATION


def test_json_duplicate_keys_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / MODEL_CONFIGURATION_FILENAME
    path.write_text(
        '{"schema":"epcsaft.model-configuration","schema":"epcsaft.model-configuration"}\n',
        encoding="utf-8",
    )

    with pytest.raises(epcsaft.InputError, match="duplicate key"):
        epcsaft.ModelOptions.from_user_options(path)


def test_strict_configuration_is_the_only_mixture_configuration_path() -> None:
    strict = _parse(EXPLICIT_NEUTRAL_CONFIGURATION)
    mixture = epcsaft.Mixture(neutral_scientific_parameter_set(), model_options=strict)

    assert mixture.model_options is strict
    assert mixture.configuration_receipt["configuration"] == strict.receipt


def test_temporary_legacy_option_owners_are_absent() -> None:
    import epcsaft.model.options as options_module

    assert not hasattr(epcsaft.ModelOptions, "_from_stage4_legacy_runtime_options")
    assert not hasattr(epcsaft.ModelOptions, "_to_stage4_legacy_runtime_options")
    assert not hasattr(options_module, "LegacyRuntimeOptionsState")
    assert "LegacyRuntimeOptionsState" not in epcsaft.__all__
    assert not hasattr(epcsaft, "LegacyRuntimeOptionsState")
