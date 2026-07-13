from __future__ import annotations

import ast
import json
from pathlib import Path

import epcsaft
import epcsaft.model as model
import pytest
from epcsaft._types import InputError
from epcsaft.model.parameters import ParameterSource, PureRecord

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


def _legacy_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_records(
        (
            PureRecord(
                component="Methane",
                molar_mass=0.016043,
                m=1.0,
                sigma=3.7039,
                epsilon_k=150.03,
                charge=0.0,
                epsilon_k_ab=0.0,
                kappa_ab=0.0,
                association_scheme=None,
                relative_permittivity=1.0,
                born_diameter=0.0,
                solvation_factor=1.0,
            ),
        ),
        metadata={"source": "Gross and Sadowski 2001 Table 2", "source_backed": True},
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


def test_schema3_is_rejected_by_both_legacy_serializer_gates() -> None:
    parameters = _schema3_parameter_set()

    with pytest.raises(InputError, match="scientific_v3"):
        parameters._to_stage4_legacy_runtime_dict()
    with pytest.raises(InputError, match="scientific_v3"):
        ParameterSource(parameters).to_runtime_dict()


def test_legacy_parameter_source_remains_the_only_public_runtime_serializer() -> None:
    payload = ParameterSource(_legacy_parameter_set()).to_runtime_dict()

    assert payload["m"].tolist() == [1.0]
    assert payload["s"].tolist() == [3.7039]
    assert payload["e"].tolist() == [150.03]


def test_private_legacy_serializer_has_the_exact_direct_caller_allowlist() -> None:
    source_root = Path(epcsaft.__file__).resolve().parent
    callers: set[str] = set()
    for path in source_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "_to_stage4_legacy_runtime_dict"
            ):
                callers.add(path.relative_to(source_root).as_posix())

    assert callers == {
        "model/parameters.py",
        "model/datasets.py",
        "model/validation.py",
        "state/native_payload.py",
    }
