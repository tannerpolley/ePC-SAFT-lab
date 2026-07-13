from __future__ import annotations

import inspect
import json

import epcsaft
import epcsaft.model as model
import pytest
from epcsaft._types import InputError

NEUTRAL_CONFIGURATION = {
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


def _api(name: str):
    value = getattr(model, name, None)
    assert value is not None, f"epcsaft.model.{name} is required"
    return value


def _parameter_set():
    domain = _api("TemperatureDomain")(
        minimum_K=100.0,
        maximum_K=400.0,
        evidence=_api("DomainEvidence")(
            kind="source_validity",
            source="test_source_bundle_loading.py interval",
        ),
    )
    source = _api("ScientificSource")(
        kind="literature",
        locator="Gross and Sadowski 2001 Table 2",
    )
    dependency = _api("DependencySignature")(variables=())
    values = {
        "molar_mass_kg_per_mol": (0.016043, "kg/mol"),
        "segment_count": (1.0, "dimensionless"),
        "sigma_angstrom": (3.7039, "angstrom"),
        "epsilon_k_K": (150.03, "K"),
        "charge_number": (0.0, "dimensionless"),
        "association_energy_K": (0.0, "K"),
        "association_volume": (0.0, "dimensionless"),
    }
    records = tuple(
        _api("ScientificRecord")(
            record_id=f"methane-{field}",
            component="Methane",
            field=field,
            units=units,
            source=source,
            dependency_signature=dependency,
            temperature_domain=domain,
            definition=_api("ConstantCorrelation")(value=value),
        )
        for field, (value, units) in values.items()
    )
    return epcsaft.ParameterSet.from_schema3_records(components=("Methane",), pure_records=records)


def _write_bundle(root) -> None:
    root.mkdir()
    (root / "parameter_set.json").write_text(_parameter_set().to_json() + "\n", encoding="utf-8")
    (root / "model_configuration.json").write_text(
        json.dumps(NEUTRAL_CONFIGURATION) + "\n",
        encoding="utf-8",
    )


def test_source_bundle_selection_loads_definitions_and_configuration_without_state_arguments(tmp_path) -> None:
    root = tmp_path / "bundle"
    _write_bundle(root)
    loader = _api("load_source_bundle_selection")

    assert set(inspect.signature(loader).parameters) == {"path", "components"}
    selection = loader(root, components=("Methane",))
    record = selection.pure_record("Methane", "sigma_angstrom")

    assert selection.parameter_set.schema_origin == "scientific_v3"
    assert selection.model_options.receipt == NEUTRAL_CONFIGURATION
    assert record.definition.value == 3.7039
    assert {path.name for path in selection.source_files} == {
        "parameter_set.json",
        "model_configuration.json",
    }


def test_source_bundle_loading_does_not_evaluate_correlations(monkeypatch, tmp_path) -> None:
    root = tmp_path / "bundle"
    _write_bundle(root)

    def forbidden(*args, **kwargs):
        raise AssertionError("source loading evaluated a scientific definition")

    monkeypatch.setattr(_api("ConstantCorrelation"), "evaluate", forbidden)
    selection = _api("load_source_bundle_selection")(root, components=("Methane",))

    assert len(selection.parameter_set.pure_records) == 7


def test_source_bundle_rejects_missing_configuration_retired_names_and_component_reordering(tmp_path) -> None:
    missing = tmp_path / "missing"
    missing.mkdir()
    (missing / "parameter_set.json").write_text(_parameter_set().to_json(), encoding="utf-8")
    with pytest.raises(InputError, match=r"model_configuration\.json"):
        _api("load_source_bundle_selection")(missing, components=("Methane",))

    retired = tmp_path / "retired"
    _write_bundle(retired)
    (retired / "user_options.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(InputError, match="unsupported"):
        _api("load_source_bundle_selection")(retired, components=("Methane",))

    reordered = tmp_path / "reordered"
    _write_bundle(reordered)
    with pytest.raises(InputError, match="component order"):
        _api("load_source_bundle_selection")(reordered, components=("Ethane",))


def test_source_bundle_lookup_fails_for_missing_or_duplicate_records(tmp_path) -> None:
    root = tmp_path / "bundle"
    _write_bundle(root)
    selection = _api("load_source_bundle_selection")(root, components=("Methane",))

    with pytest.raises(InputError, match="unique pure record"):
        selection.pure_record("Methane", "relative_permittivity")
