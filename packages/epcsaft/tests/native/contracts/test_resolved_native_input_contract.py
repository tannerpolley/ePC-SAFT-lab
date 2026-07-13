from __future__ import annotations

import importlib
import re
from dataclasses import replace
from pathlib import Path

import epcsaft
import epcsaft._core as _core
import pytest
from epcsaft._types import InputError
from epcsaft.model import SourceBundleSelection

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


def _domain() -> epcsaft.TemperatureDomain:
    return epcsaft.TemperatureDomain(
        minimum_K=100.0,
        maximum_K=500.0,
        evidence=epcsaft.DomainEvidence(
            kind="source_validity",
            source="Stage 4 native contract fixture interval",
        ),
    )


def _source(kind: str = "literature") -> epcsaft.ScientificSource:
    return epcsaft.ScientificSource(
        kind=kind,
        locator="Stage 4 native contract fixture source",
    )


def _record(component: str, field: str, value: float, units: str) -> epcsaft.ScientificRecord:
    return epcsaft.ScientificRecord(
        record_id=f"{component}-{field}",
        component=component,
        field=field,
        units=units,
        source=_source(),
        dependency_signature=epcsaft.DependencySignature(variables=()),
        temperature_domain=_domain(),
        definition=epcsaft.ConstantCorrelation(value=value),
    )


def _selection(
    *,
    mutation: tuple[str, str, float] | None = None,
    interaction_reason: str = "The cited combining rule supplies no correction.",
) -> SourceBundleSelection:
    components = ("Methane", "Ethane")
    values = {
        "Methane": {
            "molar_mass_kg_per_mol": (0.016043, "kg/mol"),
            "segment_count": (1.0, "dimensionless"),
            "sigma_angstrom": (3.7039, "angstrom"),
            "epsilon_k_K": (150.03, "K"),
            "charge_number": (0.0, "dimensionless"),
            "association_energy_K": (0.0, "K"),
            "association_volume": (0.0, "dimensionless"),
        },
        "Ethane": {
            "molar_mass_kg_per_mol": (0.03007, "kg/mol"),
            "segment_count": (1.6069, "dimensionless"),
            "sigma_angstrom": (3.5206, "angstrom"),
            "epsilon_k_K": (191.42, "K"),
            "charge_number": (0.0, "dimensionless"),
            "association_energy_K": (0.0, "K"),
            "association_volume": (0.0, "dimensionless"),
        },
    }
    formulation_values = {
        "relative_permittivity": (1.0, "dimensionless"),
        "born_diameter_angstrom": (3.0, "angstrom"),
        "solvation_factor": (1.0, "dimensionless"),
    }
    if mutation is not None:
        component, field, value = mutation
        if field in values[component]:
            values[component][field] = (value, values[component][field][1])
        else:
            formulation_values[field] = (value, formulation_values[field][1])
    pure_records = tuple(
        _record(component, field, value, units)
        for component in components
        for field, (value, units) in values[component].items()
    )
    formulation_records = tuple(
        _record(component, field, value, units)
        for component in components
        for field, (value, units) in formulation_values.items()
    )
    policies = tuple(
        epcsaft.ScientificStructuralZero(
            record_id=f"methane-ethane-{family}-zero",
            family=family,
            components=components,
            reason=interaction_reason,
            source=epcsaft.ScientificSource(
                kind="model_structural_zero",
                locator="Stage 4 native contract fixture combining rule",
            ),
        )
        for family in ("k_ij", "l_ij", "k_hb_ij")
    )
    parameters = epcsaft.ParameterSet.from_schema3_records(
        components=components,
        pure_records=pure_records,
        formulation_records=formulation_records,
        interaction_policies=policies,
        metadata={"source": "Stage 4 native contract fixture"},
    )
    return SourceBundleSelection(
        parameter_set=parameters,
        model_options=epcsaft.ModelOptions.from_user_options(NEUTRAL_CONFIGURATION),
        source_files=(Path("parameter_set.json"), Path("model_configuration.json")),
    )


def _native_module():
    return importlib.import_module("epcsaft.model._resolved_input_native")


def _handle(selection: SourceBundleSelection | None = None):
    module = _native_module()
    selected = selection or _selection()
    resolved = module._build_native_resolved_input(selected, components=selected.parameter_set.components)
    return module._evaluate_native_resolved_input(
        resolved,
        temperature_K=300.0,
        canonical_composition=(0.4, 0.6),
    )


def test_provider_handle_is_immutable_and_carries_exact_identity_and_evidence() -> None:
    handle = _handle()

    assert handle.contract_id == "provider_resolved_input_handle_v1"
    assert handle.schema == "epcsaft.resolved-model-input"
    assert handle.schema_version == 1
    assert handle.component_order == ["Methane", "Ethane"]
    assert handle.temperature_K == 300.0
    assert handle.composition_basis == "mole_fraction"
    assert handle.canonical_composition == pytest.approx([0.4, 0.6])
    assert re.fullmatch(r"[0-9a-f]{64}", handle.definition_fingerprint_sha256)
    assert re.fullmatch(r"[0-9a-f]{64}", handle.snapshot_fingerprint_sha256)
    assert re.fullmatch(r"[0-9a-f]{64}", handle.association_topology_fingerprint_sha256)
    assert handle.trial_phase_composition_invariant is True
    assert handle.active_residual_families == ["hard_chain", "dispersion"]
    assert handle.ionic_component_indices == []
    assert len(handle.evaluated_records) == 20
    assert len(handle.structural_zeros) == 3
    assert handle.affected_record_ids == {}
    with pytest.raises(AttributeError):
        handle.temperature_K = 310.0
    with pytest.raises(TypeError):
        _core.ProviderResolvedInputHandleV1()


def test_typed_factory_rejects_raw_mappings_component_mismatch_and_bad_conditions() -> None:
    module = _native_module()
    selection = _selection()

    with pytest.raises((InputError, TypeError), match="SourceBundleSelection"):
        module._build_native_resolved_input({}, components=selection.parameter_set.components)
    with pytest.raises(InputError, match="component order"):
        module._build_native_resolved_input(selection, components=("Ethane", "Methane"))
    resolved = module._build_native_resolved_input(selection, components=selection.parameter_set.components)
    with pytest.raises((InputError, _core.NativeValueError), match="sum to one"):
        module._evaluate_native_resolved_input(
            resolved,
            temperature_K=300.0,
            canonical_composition=(0.4, 0.5),
        )


@pytest.mark.parametrize(
    "mutation",
    (
        ("Methane", "segment_count", 1.01),
        ("Methane", "relative_permittivity", 1.1),
        ("Methane", "charge_number", 1.0),
        ("Methane", "born_diameter_angstrom", 3.1),
        ("Methane", "solvation_factor", 1.1),
    ),
)
def test_each_scientific_family_mutation_changes_definition_and_snapshot_identity(mutation) -> None:
    baseline = _handle()
    changed = _handle(_selection(mutation=mutation))

    assert changed.definition_fingerprint_sha256 != baseline.definition_fingerprint_sha256
    assert changed.snapshot_fingerprint_sha256 != baseline.snapshot_fingerprint_sha256
    assert (
        changed.association_topology_fingerprint_sha256
        == baseline.association_topology_fingerprint_sha256
    )


def test_structural_zero_mutation_changes_identity() -> None:
    baseline = _handle()
    changed = _handle(_selection(interaction_reason="A different cited equation supplies this zero."))

    assert changed.definition_fingerprint_sha256 != baseline.definition_fingerprint_sha256
    assert changed.snapshot_fingerprint_sha256 != baseline.snapshot_fingerprint_sha256
    assert (
        changed.association_topology_fingerprint_sha256
        != baseline.association_topology_fingerprint_sha256
    )


def test_active_association_parameters_require_typed_discrete_topology() -> None:
    module = _native_module()
    baseline_selection = _selection()
    associating_selection = _selection(
        mutation=("Methane", "association_energy_K", 10.0)
    )
    baseline = module._build_native_resolved_input(
        baseline_selection,
        components=baseline_selection.parameter_set.components,
    )
    associating = module._build_native_resolved_input(
        associating_selection,
        components=associating_selection.parameter_set.components,
    )

    assert associating.definition_fingerprint_sha256 != baseline.definition_fingerprint_sha256
    with pytest.raises(
        _core.NativeValueError,
        match="typed discrete association-topology record",
    ):
        module._evaluate_native_resolved_input(
            associating,
            temperature_K=300.0,
            canonical_composition=(0.4, 0.6),
        )


def test_every_native_parameter_field_has_one_snapshot_or_typed_formulation_owner() -> None:
    header = Path(epcsaft.__file__).resolve().parent / "native" / "model" / "resolved_input.h"
    block = re.search(
        r"struct NativeEvaluatedInputSnapshot final \{(?P<body>.*?)\n\};",
        header.read_text(encoding="utf-8"),
        re.S,
    )
    assert block is not None
    parameter_fields = block.group("body").split(
        'std::string contract_id{"provider_resolved_input_handle_v1"};',
        maxsplit=1,
    )[0]
    fields = set(
        re.findall(
            r"(?:vector<[^>]+>|std::string|int)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\{[^;]*\}|=[^;]+)?;",
            parameter_fields,
        )
    )
    accounting = _core._native_resolved_input_field_accounting()

    assert set(accounting) == fields
    assert all(value.startswith(("snapshot.", "snapshot.formulation.")) for value in accounting.values())


def test_handle_properties_are_detached_and_condition_identity_is_exact() -> None:
    module = _native_module()
    selection = _selection()
    resolved = module._build_native_resolved_input(
        selection,
        components=selection.parameter_set.components,
    )
    baseline = module._evaluate_native_resolved_input(
        resolved,
        temperature_K=300.0,
        canonical_composition=(0.4, 0.6),
    )
    changed_temperature = module._evaluate_native_resolved_input(
        resolved,
        temperature_K=310.0,
        canonical_composition=(0.4, 0.6),
    )
    changed_composition = module._evaluate_native_resolved_input(
        resolved,
        temperature_K=300.0,
        canonical_composition=(0.3, 0.7),
    )

    detached = baseline.evaluated_records
    detached[0]["record_id"] = "mutated-detached-copy"
    assert baseline.evaluated_records[0]["record_id"] != "mutated-detached-copy"
    assert changed_temperature.definition_fingerprint_sha256 == baseline.definition_fingerprint_sha256
    assert changed_temperature.snapshot_fingerprint_sha256 != baseline.snapshot_fingerprint_sha256
    assert changed_composition.definition_fingerprint_sha256 == baseline.definition_fingerprint_sha256
    assert changed_composition.snapshot_fingerprint_sha256 != baseline.snapshot_fingerprint_sha256


def _replace_scientific_record(selection: SourceBundleSelection, replacement) -> SourceBundleSelection:
    parameters = selection.parameter_set
    pure_records = tuple(
        replacement if record.record_id == replacement.record_id else record
        for record in parameters.pure_records
    )
    formulation_records = tuple(
        replacement if record.record_id == replacement.record_id else record
        for record in parameters.formulation_records
    )
    return SourceBundleSelection(
        epcsaft.ParameterSet.from_schema3_records(
            components=parameters.components,
            pure_records=pure_records,
            formulation_records=formulation_records,
            interactions=parameters.interactions,
            interaction_policies=parameters.interaction_policies,
            metadata=parameters.metadata,
        ),
        selection.model_options,
        selection.source_files,
    )


def test_native_evaluator_preserves_temperature_dependency_and_derivative_evidence() -> None:
    selection = _selection()
    sigma = selection.pure_record("Methane", "sigma_angstrom")
    temperature_dependent = replace(
        sigma,
        dependency_signature=epcsaft.DependencySignature(
            variables=(epcsaft.IndependentVariable.TEMPERATURE_K,)
        ),
        definition=epcsaft.ReferenceTemperatureLinearCorrelation(
            reference_temperature_K=300.0,
            reference_value=3.7039,
            slope_per_K=1.0e-3,
        ),
    )
    handle = _handle(_replace_scientific_record(selection, temperature_dependent))
    evidence = next(
        item for item in handle.evaluated_records if item["record_id"] == sigma.record_id
    )

    assert handle.affected_record_ids == {"temperature_K": [sigma.record_id]}
    assert handle.trial_phase_composition_invariant is True
    assert evidence["dependency_signature"] == ["temperature_K"]
    assert evidence["evaluated_value"] == pytest.approx([3.7039])
    assert evidence["first_derivatives"] == pytest.approx([1.0e-3])
    assert evidence["second_derivatives_row_major"] == pytest.approx([0.0])
    assert evidence["definition_backed_ad"] is False


def test_native_evaluator_marks_composition_dependent_definition_noninvariant() -> None:
    selection = _selection()
    permittivity = next(
        record
        for record in selection.parameter_set.formulation_records
        if record.component == "Methane" and record.field == "relative_permittivity"
    )
    composition_dependent = replace(
        permittivity,
        dependency_signature=epcsaft.DependencySignature(
            variables=(epcsaft.IndependentVariable.MOLE_FRACTION,),
            composition_components=("Methane", "Ethane"),
        ),
        definition=epcsaft.SaltFreeWaterMoleFractionCubicPermittivityCorrelation(
            water_component="Methane",
            organic_component="Ethane",
            composition_basis="salt_free_solvent_mole_fraction",
            coefficient_a=1.0,
            coefficient_b=2.0,
            coefficient_c=3.0,
        ),
    )
    handle = _handle(_replace_scientific_record(selection, composition_dependent))

    assert handle.trial_phase_composition_invariant is False
    assert handle.affected_record_ids == {"mole_fraction": [permittivity.record_id]}
    evidence = next(
        item for item in handle.evaluated_records if item["record_id"] == permittivity.record_id
    )
    expected = 1.0 + 0.4**3 + 2.0 * 0.4**2 + 3.0 * 0.4
    assert evidence["evaluated_value"] == pytest.approx([expected])
    assert evidence["first_derivatives"] == pytest.approx([3.0 * 0.4**2 + 4.0 * 0.4 + 3.0])


def test_definition_fingerprint_is_record_order_independent_but_source_sensitive() -> None:
    selection = _selection()
    parameters = selection.parameter_set
    reordered = SourceBundleSelection(
        epcsaft.ParameterSet.from_schema3_records(
            components=parameters.components,
            pure_records=tuple(reversed(parameters.pure_records)),
            formulation_records=tuple(reversed(parameters.formulation_records)),
            interactions=tuple(reversed(parameters.interactions)),
            interaction_policies=tuple(reversed(parameters.interaction_policies)),
            metadata=parameters.metadata,
        ),
        selection.model_options,
        tuple(reversed(selection.source_files)),
    )
    source_record = selection.pure_record("Methane", "segment_count")
    changed_source = replace(
        source_record,
        source=epcsaft.ScientificSource(
            source_record.source.kind,
            "A different source locator",
        ),
    )

    assert _handle(reordered).definition_fingerprint_sha256 == _handle(selection).definition_fingerprint_sha256
    assert (
        _handle(_replace_scientific_record(selection, changed_source)).definition_fingerprint_sha256
        != _handle(selection).definition_fingerprint_sha256
    )


def test_writable_and_raw_native_provider_bypasses_are_absent() -> None:
    from epcsaft.state import native_adapter

    assert not hasattr(_core, "NativeArgs")
    assert not hasattr(native_adapter.ePCSAFTMixture, "from_params")
    assert not hasattr(native_adapter.ePCSAFTMixture, "from_dataset")

    handle = _handle()
    with pytest.raises(TypeError):
        _core.NativeMixture({})
    with pytest.raises(TypeError):
        _core.NativeMixture(handle, [1.0, 0.0])
