from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import epcsaft
import epcsaft._core as _core
import numpy as np
import pytest
from epcsaft._types import InputError
from support.model_configurations import (
    neutral_model_options,
    neutral_scientific_parameter_set,
    with_temperature_dependent_sigma,
)


def _resolve(*, reverse_records: bool = False, source_locator: str | None = None):
    kwargs = {"reverse_records": reverse_records}
    if source_locator is not None:
        kwargs["source_locator"] = source_locator
    return epcsaft.ResolvedModelInput.resolve(
        neutral_scientific_parameter_set(**kwargs),
        neutral_model_options(),
    )


def test_equivalent_definition_order_has_byte_identical_receipt_and_fingerprint() -> None:
    baseline = _resolve()
    reordered = _resolve(reverse_records=True)

    assert baseline.components == ("Methane", "Ethane")
    assert baseline.fingerprint_sha256 == reordered.fingerprint_sha256
    assert baseline._configuration_receipt_json == reordered._configuration_receipt_json
    receipt = baseline.configuration_receipt
    assert receipt["schema"] == "epcsaft.resolved-model-input"
    assert receipt["schema_version"] == 1
    assert receipt["definition_fingerprint_sha256"] == baseline.fingerprint_sha256
    assert receipt["configuration"] == neutral_model_options().receipt
    assert [item["record_id"] for item in receipt["definitions"]["pure_records"]] == sorted(
        item["record_id"] for item in receipt["definitions"]["pure_records"]
    )
    with pytest.raises(FrozenInstanceError):
        baseline.fingerprint_sha256 = "0" * 64


def test_resolver_accepts_only_typed_schema3_inputs_and_exact_component_order() -> None:
    parameters = neutral_scientific_parameter_set()
    options = neutral_model_options()

    with pytest.raises((InputError, TypeError), match="ParameterSet"):
        epcsaft.ResolvedModelInput.resolve({}, options)
    with pytest.raises((InputError, TypeError), match="ModelOptions"):
        epcsaft.ResolvedModelInput.resolve(parameters, {})
    with pytest.raises(InputError, match="component order"):
        epcsaft.ResolvedModelInput.resolve(
            parameters,
            options,
            components=("Ethane", "Methane"),
        )
    with pytest.raises(TypeError):
        _core.ResolvedNativeInput(parameters)


def test_source_object_mutation_after_resolution_cannot_change_receipts_or_evaluation() -> None:
    parameters = neutral_scientific_parameter_set()
    resolved = epcsaft.ResolvedModelInput.resolve(parameters, neutral_model_options())
    receipt = resolved.configuration_receipt
    baseline = resolved.evaluate(temperature=300.0, composition=(0.4, 0.6))

    parameters.metadata["source"] = "mutated after compilation"

    assert resolved.configuration_receipt == receipt
    assert (
        resolved.evaluate(
            temperature=300.0,
            composition=(0.4, 0.6),
        ).snapshot_fingerprint_sha256
        == baseline.snapshot_fingerprint_sha256
    )


def test_evaluation_preserves_exact_vector_and_returns_detached_receipts() -> None:
    resolved = _resolve()
    composition = np.array([0.4000000000000001, 0.5999999999999999])
    evaluated = resolved.evaluate(temperature=300.0, composition=composition)
    composition[:] = (0.2, 0.8)

    assert evaluated.definition_fingerprint_sha256 == resolved.fingerprint_sha256
    assert evaluated.snapshot_fingerprint_sha256 == evaluated.native_handle.snapshot_fingerprint_sha256
    assert evaluated.native_handle.definition_fingerprint_sha256 == resolved.fingerprint_sha256
    assert evaluated.native_handle.canonical_composition == [
        0.4000000000000001,
        0.5999999999999999,
    ]
    receipt = evaluated.receipt
    assert receipt["state"] == {
        "temperature_K": 300.0,
        "composition_basis": "mole_fraction",
        "canonical_composition": [0.4000000000000001, 0.5999999999999999],
    }
    receipt["state"]["canonical_composition"][0] = 1.0
    receipt["evaluated_records"][0]["record_id"] = "mutated"
    assert evaluated.receipt["state"]["canonical_composition"][0] == 0.4000000000000001
    assert evaluated.receipt["evaluated_records"][0]["record_id"] != "mutated"


def test_receipt_retains_dependencies_domains_classifications_and_native_mapping() -> None:
    parameters = with_temperature_dependent_sigma(neutral_scientific_parameter_set())
    resolved = epcsaft.ResolvedModelInput.resolve(parameters, neutral_model_options())
    receipt = resolved.evaluate(temperature=310.0, composition=(0.4, 0.6)).receipt

    definition = next(
        item
        for item in receipt["definitions"]["pure_records"]
        if item["record_id"] == "Methane-sigma_angstrom"
    )
    evaluated = next(
        item
        for item in receipt["evaluated_records"]
        if item["record_id"] == "Methane-sigma_angstrom"
    )
    assert definition["dependency_signature"]["variables"] == ["temperature_K"]
    assert definition["temperature_domain"]["evidence"]["kind"] == "source_validity"
    assert receipt["dependency_groups"] == {
        "temperature_K": ["Methane-sigma_angstrom"]
    }
    assert receipt["trial_phase_composition_invariant"] is True
    assert receipt["active_residual_families"] == ["hard_chain", "dispersion"]
    assert receipt["ionic_component_indices"] == []
    assert len(receipt["structural_zeros"]) == 3
    assert receipt["association_topology_fingerprint_sha256"]
    assert receipt["scientific_source_classifications"] == [
        "literature",
        "model_structural_zero",
    ]
    assert evaluated["native_field"] == "s"
    assert receipt["native_mapping"]["Methane-sigma_angstrom"]["field"] == "s"


@pytest.mark.parametrize(
    ("composition", "match"),
    (
        ((0.4, 0.5), "sum to one"),
        ((0.4, 0.6, 0.0), "length"),
        ((-0.1, 1.1), "non-negative"),
        ((float("nan"), 1.0), "finite"),
        (((0.4, 0.6),), "one-dimensional"),
    ),
)
def test_canonical_composition_validation_rejects_without_normalization(
    composition,
    match: str,
) -> None:
    with pytest.raises(InputError, match=match):
        _resolve().evaluate(temperature=300.0, composition=composition)


def test_canonical_composition_validation_returns_an_exact_read_only_copy() -> None:
    from epcsaft.state.input_validation import validate_canonical_composition

    source = np.array([0.40000001, 0.59999999])
    canonical = validate_canonical_composition(source, 2)
    source[:] = (0.1, 0.9)

    assert canonical.tolist() == [0.40000001, 0.59999999]
    assert canonical.flags.writeable is False
    with pytest.raises(ValueError, match="read-only"):
        canonical[0] = 0.2


def test_source_formulation_temperature_and_composition_change_owned_identity() -> None:
    baseline = _resolve()
    source_changed = _resolve(source_locator="A different literature locator")
    formulation = copy.deepcopy(neutral_model_options().receipt)
    formulation["formulation"]["electrostatics"] = {"enabled": True}
    formulation_changed = epcsaft.ResolvedModelInput.resolve(
        neutral_scientific_parameter_set(),
        epcsaft.ModelOptions.from_user_options(formulation),
    )
    evaluated = baseline.evaluate(temperature=300.0, composition=(0.4, 0.6))

    assert source_changed.fingerprint_sha256 != baseline.fingerprint_sha256
    assert formulation_changed.fingerprint_sha256 != baseline.fingerprint_sha256
    assert (
        baseline.evaluate(temperature=310.0, composition=(0.4, 0.6)).snapshot_fingerprint_sha256
        != evaluated.snapshot_fingerprint_sha256
    )
    assert (
        baseline.evaluate(temperature=300.0, composition=(0.3, 0.7)).snapshot_fingerprint_sha256
        != evaluated.snapshot_fingerprint_sha256
    )


def test_failed_domain_evaluation_does_not_change_later_evaluation() -> None:
    resolved = _resolve()
    baseline = resolved.evaluate(temperature=300.0, composition=(0.4, 0.6))

    with pytest.raises(InputError, match="outside the sourced record domain"):
        resolved.evaluate(temperature=501.0, composition=(0.4, 0.6))

    repeated = resolved.evaluate(temperature=300.0, composition=(0.4, 0.6))
    assert repeated.snapshot_fingerprint_sha256 == baseline.snapshot_fingerprint_sha256
    assert repeated.receipt == baseline.receipt


def test_provider_handle_definition_mismatch_is_rejected(monkeypatch) -> None:
    import epcsaft.model.resolved_input as implementation

    baseline = _resolve()
    foreign = _resolve(source_locator="Foreign source").evaluate(
        temperature=300.0,
        composition=(0.4, 0.6),
    )
    monkeypatch.setattr(
        implementation,
        "_evaluate_native_resolved_input",
        lambda *args, **kwargs: foreign.native_handle,
    )

    with pytest.raises(InputError, match="definition fingerprint mismatch"):
        baseline.evaluate(temperature=300.0, composition=(0.4, 0.6))
