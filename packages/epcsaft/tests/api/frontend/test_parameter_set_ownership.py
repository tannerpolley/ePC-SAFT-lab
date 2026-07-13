from __future__ import annotations

import json
from pathlib import Path

import epcsaft
import epcsaft.model as model
import pytest
from epcsaft._types import InputError
from epcsaft.model.parameters import ParameterSource

SCHEMA3_KEYS = {
    "schema",
    "schema_version",
    "components",
    "pure_records",
    "formulation_records",
    "interactions",
    "interaction_policies",
    "metadata",
}


def _api(name: str):
    value = getattr(model, name, None)
    assert value is not None, f"epcsaft.model.{name} is required"
    return value


def _domain():
    return _api("TemperatureDomain")(
        minimum_K=250.0,
        maximum_K=400.0,
        evidence=_api("DomainEvidence")(
            kind="source_validity",
            source="test_parameter_set_ownership.py interval",
        ),
    )


def _record(component: str, field: str, value: float, units: str):
    return _api("ScientificRecord")(
        record_id=f"{component}-{field}",
        component=component,
        field=field,
        units=units,
        source=_api("ScientificSource")(
            kind="literature",
            locator="Gross and Sadowski 2001 Table 2",
        ),
        dependency_signature=_api("DependencySignature")(variables=()),
        temperature_domain=_domain(),
        definition=_api("ConstantCorrelation")(value=value),
    )


def _schema3_parameter_set():
    component = "Methane"
    records = (
        _record(component, "molar_mass_kg_per_mol", 0.016043, "kg/mol"),
        _record(component, "segment_count", 1.0, "dimensionless"),
        _record(component, "sigma_angstrom", 3.7039, "angstrom"),
        _record(component, "epsilon_k_K", 150.03, "K"),
        _record(component, "charge_number", 0.0, "dimensionless"),
        _record(component, "association_energy_K", 0.0, "K"),
        _record(component, "association_volume", 0.0, "dimensionless"),
    )
    return epcsaft.ParameterSet.from_schema3_records(
        components=(component,),
        pure_records=records,
        metadata={"source": "Gross and Sadowski 2001 Table 2"},
    )


def test_schema3_parameter_set_has_the_exact_policy_free_top_level_shape() -> None:
    parameters = _schema3_parameter_set()
    payload = json.loads(parameters.to_json())

    assert set(payload) == SCHEMA3_KEYS
    assert payload["schema"] == "epcsaft.parameter-set"
    assert payload["schema_version"] == 3
    assert parameters.schema_origin == "scientific_v3"
    assert not hasattr(epcsaft.ParameterSet, "to_runtime_dict")


@pytest.mark.parametrize("forbidden", ("runtime_options", "T", "x", "model_options", "formulation"))
def test_schema3_loader_rejects_runtime_policy_state_and_wrong_owner_keys(forbidden: str) -> None:
    payload = json.loads(_schema3_parameter_set().to_json())
    payload[forbidden] = {}

    with pytest.raises(InputError, match="unsupported key"):
        epcsaft.ParameterSet.from_schema3(payload)


def test_schema3_loader_rejects_schema2_and_free_form_definitions() -> None:
    payload = json.loads(_schema3_parameter_set().to_json())
    payload["schema_version"] = 2
    with pytest.raises(InputError, match="schema_version 3"):
        epcsaft.ParameterSet.from_schema3(payload)

    payload = json.loads(_schema3_parameter_set().to_json())
    payload["pure_records"][0]["definition"] = "1.0 + expression(T)"
    with pytest.raises(InputError, match="typed correlation"):
        epcsaft.ParameterSet.from_schema3(payload)


def test_schema3_round_trip_preserves_definitions_without_evaluating() -> None:
    parameters = _schema3_parameter_set()
    restored = epcsaft.ParameterSet.from_schema3(json.loads(parameters.to_json()))

    assert restored == parameters
    assert restored.to_json() == parameters.to_json()


def test_schema3_rejects_duplicate_record_ids_and_missing_core_records() -> None:
    parameters = _schema3_parameter_set()
    records = list(parameters.pure_records)
    with pytest.raises(InputError, match="duplicate record_id"):
        epcsaft.ParameterSet.from_schema3_records(
            components=parameters.components,
            pure_records=(*records, records[0]),
        )
    with pytest.raises(InputError, match="missing scientific record"):
        epcsaft.ParameterSet.from_schema3_records(
            components=parameters.components,
            pure_records=tuple(records[:-1]),
        )


def test_schema3_enforces_record_categories_and_complete_binary_source_coverage() -> None:
    methane = _schema3_parameter_set()
    misplaced_formulation = _record("Methane", "relative_permittivity", 78.0, "dimensionless")
    with pytest.raises(InputError, match="pure_records scientific field"):
        epcsaft.ParameterSet.from_schema3_records(
            components=methane.components,
            pure_records=(*methane.pure_records, misplaced_formulation),
        )

    ethane_records = tuple(
        _record("Ethane", record.field, record.definition.value, record.units)
        for record in methane.pure_records
    )
    with pytest.raises(InputError, match="missing scientific interaction coverage"):
        epcsaft.ParameterSet.from_schema3_records(
            components=("Methane", "Ethane"),
            pure_records=(*methane.pure_records, *ethane_records),
        )


def test_schema3_has_no_runtime_serializer_gates() -> None:
    parameters = _schema3_parameter_set()

    assert not hasattr(parameters, "_to_stage4_legacy_runtime_dict")
    assert not hasattr(ParameterSource(parameters), "to_runtime_dict")
    assert not hasattr(parameters, "runtime_options")


def test_schema2_and_legacy_record_construction_are_rejected() -> None:
    with pytest.raises(InputError, match="schema-3"):
        epcsaft.ParameterSet.from_dict({"schema": "epcsaft.parameter-set", "schema_version": 2})
    assert not hasattr(epcsaft.ParameterSet, "from_records")
