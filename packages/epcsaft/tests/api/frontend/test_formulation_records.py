from __future__ import annotations

import epcsaft.model as model
import pytest
from epcsaft._types import InputError


def _api(name: str):
    value = getattr(model, name, None)
    assert value is not None, f"epcsaft.model.{name} is required"
    return value


def _source(kind: str = "literature"):
    return _api("ScientificSource")(kind=kind, locator="test_formulation_records.py source record")


def _domain():
    evidence = _api("DomainEvidence")(
        kind="source_application",
        source="test_formulation_records.py 250-400 K application interval",
    )
    return _api("TemperatureDomain")(minimum_K=250.0, maximum_K=400.0, evidence=evidence)


def _constant_record(component: str, field: str, value: float, *, units: str = "dimensionless"):
    return _api("ScientificRecord")(
        record_id=f"{component}-{field}",
        component=component,
        field=field,
        units=units,
        source=_source(),
        dependency_signature=_api("DependencySignature")(variables=()),
        temperature_domain=_domain(),
        definition=_api("ConstantCorrelation")(value=value),
    )


def test_formulation_records_are_source_bearing_and_not_model_policy() -> None:
    record = _constant_record("Water", "relative_permittivity", 78.09)

    assert record.field == "relative_permittivity"
    assert record.source.locator.endswith("source record")
    assert not hasattr(record, "enabled")
    assert not hasattr(record, "runtime_options")


def test_interaction_records_require_exact_pairs_sources_dependencies_and_units() -> None:
    interaction_type = _api("ScientificInteractionRecord")
    interaction = interaction_type(
        record_id="methane-ethane-kij",
        family="k_ij",
        components=("Methane", "Ethane"),
        units="dimensionless",
        source=_source(),
        dependency_signature=_api("DependencySignature")(variables=()),
        temperature_domain=_domain(),
        definition=_api("ConstantCorrelation")(value=0.001),
    )

    assert interaction.components == ("Methane", "Ethane")
    with pytest.raises(InputError, match="exactly two"):
        interaction_type(
            record_id="bad-pair",
            family="k_ij",
            components=("Methane",),
            units="dimensionless",
            source=_source(),
            dependency_signature=_api("DependencySignature")(variables=()),
            temperature_domain=_domain(),
            definition=_api("ConstantCorrelation")(value=0.0),
        )


def test_structural_zero_is_a_separate_source_bearing_record() -> None:
    zero = _api("ScientificStructuralZero")(
        record_id="methane-ethane-lij-lorentz",
        family="l_ij",
        components=("Methane", "Ethane"),
        reason="The cited Lorentz combining rule supplies no correction.",
        source=_api("ScientificSource")(
            kind="model_structural_zero",
            locator="EqID sigma_mixing",
        ),
    )

    assert zero.family == "l_ij"
    with pytest.raises(InputError, match="model_structural_zero"):
        _api("ScientificStructuralZero")(
            record_id="bad-zero",
            family="l_ij",
            components=("Methane", "Ethane"),
            reason="not sourced as a structural zero",
            source=_source(),
        )


@pytest.mark.parametrize("field", ("runtime_options", "T", "x", "born_model", "relative_permittivity_rule"))
def test_scientific_records_reject_runtime_policy_and_state_field_names(field: str) -> None:
    with pytest.raises(InputError, match="scientific field"):
        _constant_record("Water", field, 1.0)
