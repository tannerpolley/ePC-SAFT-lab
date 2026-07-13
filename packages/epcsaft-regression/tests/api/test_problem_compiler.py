from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace

import epcsaft
import pytest
from epcsaft import InputError
from epcsaft.model.resolved_input import EvaluatedModelInput
from epcsaft_regression import (
    CompositionBasis,
    CompositionRecord,
    FittedParameter,
    LossKind,
    Regression,
    RegressionControls,
    SourceIdentity,
    SourceKind,
    TargetDataset,
    TargetFamily,
    TargetRow,
    compile_regression_problem,
)
from epcsaft_regression.problem import _canonical_problem_json

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


def _record(component: str, field: str, value: float, units: str, *, maximum_K: float):
    return epcsaft.ScientificRecord(
        record_id=f"{component}-{field}",
        component=component,
        field=field,
        units=units,
        source=epcsaft.ScientificSource(
            kind="literature",
            locator="Gross and Sadowski 2001 Table 2",
        ),
        dependency_signature=epcsaft.DependencySignature(variables=()),
        temperature_domain=epcsaft.TemperatureDomain(
            minimum_K=100.0,
            maximum_K=maximum_K,
            evidence=epcsaft.DomainEvidence(
                kind="source_validity",
                source="test_problem_compiler.py retained interval",
            ),
        ),
        definition=epcsaft.ConstantCorrelation(value=value),
    )


def _mixture(*, epsilon_k: float = 150.03, maximum_K: float = 200.0) -> epcsaft.Mixture:
    component = "Methane"
    values = {
        "molar_mass_kg_per_mol": (0.016043, "kg/mol"),
        "segment_count": (1.0, "dimensionless"),
        "sigma_angstrom": (3.7039, "angstrom"),
        "epsilon_k_K": (epsilon_k, "K"),
        "charge_number": (0.0, "dimensionless"),
        "association_energy_K": (0.0, "K"),
        "association_volume": (0.0, "dimensionless"),
    }
    formulation = {
        "relative_permittivity": (1.0, "dimensionless"),
        "born_diameter_angstrom": (3.0, "angstrom"),
        "solvation_factor": (1.0, "dimensionless"),
    }
    parameters = epcsaft.ParameterSet.from_schema3_records(
        components=(component,),
        pure_records=tuple(
            _record(component, field, value, units, maximum_K=maximum_K) for field, (value, units) in values.items()
        ),
        formulation_records=tuple(
            _record(component, field, value, units, maximum_K=maximum_K)
            for field, (value, units) in formulation.items()
        ),
        metadata={"source": "Gross and Sadowski 2001 Table 2"},
    )
    return epcsaft.Mixture(
        parameters,
        model_options=epcsaft.ModelOptions.from_user_options(NEUTRAL_CONFIGURATION),
    )


def _binary_mixture() -> epcsaft.Mixture:
    components = ("Methane", "Ethane")
    values = {
        "Methane": (0.016043, 1.0, 3.7039, 150.03),
        "Ethane": (0.030070, 1.6069, 3.5206, 191.42),
    }
    pure_records = []
    formulation_records = []
    for component, (molar_mass, segments, sigma, epsilon_k) in values.items():
        pure_records.extend(
            (
                _record(component, "molar_mass_kg_per_mol", molar_mass, "kg/mol", maximum_K=400.0),
                _record(component, "segment_count", segments, "dimensionless", maximum_K=400.0),
                _record(component, "sigma_angstrom", sigma, "angstrom", maximum_K=400.0),
                _record(component, "epsilon_k_K", epsilon_k, "K", maximum_K=400.0),
                _record(component, "charge_number", 0.0, "dimensionless", maximum_K=400.0),
                _record(component, "association_energy_K", 0.0, "K", maximum_K=400.0),
                _record(component, "association_volume", 0.0, "dimensionless", maximum_K=400.0),
            )
        )
        formulation_records.extend(
            (
                _record(component, "relative_permittivity", 1.0, "dimensionless", maximum_K=400.0),
                _record(component, "born_diameter_angstrom", 3.0, "angstrom", maximum_K=400.0),
                _record(component, "solvation_factor", 1.0, "dimensionless", maximum_K=400.0),
            )
        )
    zeros = tuple(
        epcsaft.ScientificStructuralZero(
            record_id=f"Methane-Ethane-{family}-zero",
            family=family,
            components=components,
            reason="The retained combining rule supplies no correction.",
            source=epcsaft.ScientificSource(
                kind="model_structural_zero",
                locator="test_problem_compiler.py combining rule",
            ),
        )
        for family in ("k_ij", "l_ij", "k_hb_ij")
    )
    parameters = epcsaft.ParameterSet.from_schema3_records(
        components=components,
        pure_records=tuple(pure_records),
        formulation_records=tuple(formulation_records),
        interaction_policies=zeros,
        metadata={"source": "Gross and Sadowski 2001 Tables 2 and 4"},
    )
    return epcsaft.Mixture(
        parameters,
        model_options=epcsaft.ModelOptions.from_user_options(NEUTRAL_CONFIGURATION),
    )


def _row(
    *,
    row_id: str = "methane-fugacity-130K",
    temperature: float = 130.0,
    family: TargetFamily = TargetFamily.PURE_SATURATION_FUGACITY_BALANCE,
) -> TargetRow:
    density = family is TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE
    target = 420.0 if density else 0.0
    return TargetRow(
        row_id=row_id,
        target_family=family,
        conditions={"temperature": temperature, "pressure": 367300.0},
        observations={"target": target},
        units={
            "temperature": "K",
            "pressure": "Pa",
            "target": "kg/m3" if density else "dimensionless",
        },
        weight=1.0,
        residual_scale=target if density else 1.0,
        source=SourceIdentity(
            source_id="NIST_methane_saturation",
            source_kind=SourceKind.LITERATURE,
            citation="NIST Chemistry WebBook SRD 69",
            locator=f"Methane saturation table, {temperature:g} K",
        ),
        phase="liquid_vapor",
        compositions=(),
    )


def _dataset(*, temperature: float = 130.0) -> TargetDataset:
    return TargetDataset(
        rows=(
            _row(temperature=temperature),
            _row(
                row_id="methane-density-130K",
                temperature=temperature,
                family=TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE,
            ),
        ),
        dataset_id="methane-contract-targets",
    )


def _binary_dataset() -> TargetDataset:
    components = ("Methane", "Ethane")
    row = TargetRow(
        row_id="methane-ethane-vle-001",
        target_family=TargetFamily.BINARY_VLE,
        conditions={"temperature": 180.0, "pressure": 1.0e6},
        observations={},
        units={"temperature": "K", "pressure": "Pa"},
        weight=1.0,
        residual_scale=1.0,
        source=SourceIdentity(
            source_id="binary-component-contract",
            source_kind=SourceKind.COMPONENT_TEST,
            citation="",
            locator="test_problem_compiler.py binary row",
        ),
        phase="vle",
        compositions=(
            CompositionRecord("liquid", CompositionBasis.MOLE_FRACTION, components, (0.4, 0.6)),
            CompositionRecord("vapor", CompositionBasis.MOLE_FRACTION, components, (0.7, 0.3)),
        ),
    )
    return TargetDataset(rows=(row,), dataset_id="binary-contract-targets")


def _controls(**changes) -> RegressionControls:
    values = {
        "loss": LossKind.LINEAR,
        "max_num_iterations": 80,
        "function_tolerance": 1.0e-10,
        "gradient_tolerance": 1.0e-10,
        "parameter_tolerance": 1.0e-10,
    }
    values.update(changes)
    return RegressionControls(**values)


def _parameters() -> tuple[FittedParameter, ...]:
    return (
        FittedParameter("Methane.m", start=1.08, lower=0.5, upper=3.5),
        FittedParameter("Methane.sigma", start=3.55, lower=2.0, upper=5.0),
        FittedParameter("Methane.epsilon_k", start=155.0, lower=50.0, upper=400.0),
    )


def _compile(**changes):
    values = {
        "mixture": _mixture(),
        "dataset": _dataset(),
        "parameters": _parameters(),
        "controls": _controls(),
    }
    values.update(changes)
    return compile_regression_problem(**values)


def test_compiler_retains_one_definition_and_ordered_typed_state_inputs() -> None:
    mixture = _mixture()
    dataset = _dataset()
    compiled = _compile(mixture=mixture, dataset=dataset)

    assert compiled.provider_definition_fingerprint == mixture.resolved_model_input.fingerprint_sha256
    assert compiled.row_ids == dataset.row_ids
    assert compiled.source_ids == tuple(row.source.source_id for row in dataset.rows)
    assert compiled.state_keys == tuple(f"{row_id}:pure" for row_id in dataset.row_ids)
    assert all(isinstance(item, EvaluatedModelInput) for item in compiled.evaluated_inputs)
    assert compiled.native_handles == tuple(item.native_handle for item in compiled.evaluated_inputs)
    assert compiled.snapshot_fingerprints == tuple(
        item.snapshot_fingerprint_sha256 for item in compiled.evaluated_inputs
    )
    assert all(
        item.definition_fingerprint_sha256 == compiled.provider_definition_fingerprint
        for item in compiled.evaluated_inputs
    )
    assert compiled.parameter_keys == tuple(sorted(parameter.key for parameter in _parameters()))
    assert compiled.fixed_parameter_fingerprints
    assert not hasattr(compiled, "parameter_set")
    assert not hasattr(compiled, "provider_payload")

    with pytest.raises(FrozenInstanceError):
        compiled.provider_definition_fingerprint = "changed"


def test_definition_and_state_receipts_are_detached_and_exact() -> None:
    compiled = _compile()
    definition = compiled.definition_receipt
    states = compiled.state_receipts
    definition["components"][0] = "changed"
    states[0]["state"]["canonical_composition"][0] = 0.0

    assert compiled.definition_receipt["components"] == ["Methane"]
    assert compiled.state_receipts[0]["state"]["canonical_composition"] == [1.0]
    assert compiled.state_receipts[0]["state"]["temperature_K"] == 130.0


def test_binary_row_compiles_liquid_then_vapor_handles_against_one_fixed_graph() -> None:
    compiled = compile_regression_problem(
        mixture=_binary_mixture(),
        dataset=_binary_dataset(),
        parameters=(FittedParameter("Methane:Ethane.k_ij", 0.0, -0.2, 0.2),),
        controls=_controls(),
    )

    assert compiled.state_keys == (
        "methane-ethane-vle-001:liquid",
        "methane-ethane-vle-001:vapor",
    )
    assert len(compiled.native_handles) == 2
    assert [receipt["state"]["canonical_composition"] for receipt in compiled.state_receipts] == [
        [0.4, 0.6],
        [0.7, 0.3],
    ]
    assert "Methane-Ethane-k_ij-zero" not in dict(compiled.fixed_parameter_fingerprints)


def test_configured_workflow_compiles_its_exact_mixture() -> None:
    first = Regression(_mixture())
    second = Regression(_mixture(epsilon_k=151.0))

    first_problem = first.compile(_dataset(), parameters=_parameters(), controls=_controls())
    second_problem = second.compile(_dataset(), parameters=_parameters(), controls=_controls())

    assert first_problem.provider_definition_fingerprint != second_problem.provider_definition_fingerprint
    assert first_problem.provider_definition_fingerprint == first.mixture.resolved_model_input.fingerprint_sha256
    assert second_problem.provider_definition_fingerprint == second.mixture.resolved_model_input.fingerprint_sha256


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("max_num_iterations", 81),
        ("function_tolerance", 2.0e-10),
        ("gradient_tolerance", 2.0e-10),
        ("parameter_tolerance", 2.0e-10),
    ),
)
def test_each_control_changes_the_canonical_compiled_problem(field: str, value: object) -> None:
    baseline = _compile()
    changed = _compile(controls=_controls(**{field: value}))

    assert _canonical_problem_json(changed) != _canonical_problem_json(baseline)


def test_controls_reject_unknown_missing_and_unsupported_values() -> None:
    payload = _controls().to_dict()
    payload["mystery"] = 1
    with pytest.raises(InputError, match=r"unknown control key.*mystery"):
        RegressionControls.from_mapping(payload)

    missing = _controls().to_dict()
    del missing["gradient_tolerance"]
    with pytest.raises(InputError, match=r"missing control key.*gradient_tolerance"):
        RegressionControls.from_mapping(missing)

    with pytest.raises(InputError, match="LossKind"):
        RegressionControls.from_mapping({**_controls().to_dict(), "loss": "huber"})
    with pytest.raises(InputError, match="positive integer"):
        _controls(max_num_iterations=0)
    with pytest.raises(InputError, match="finite and positive"):
        _controls(function_tolerance=float("nan"))


@pytest.mark.parametrize(
    "mutation",
    (
        {"start": None},
        {"lower": None},
        {"upper": None},
        {"lower": 2.0, "upper": 1.0},
        {"start": float("inf")},
        {"start": 4.0, "lower": 0.5, "upper": 3.5},
    ),
)
def test_fitted_parameters_require_explicit_finite_ordered_bounds(mutation) -> None:
    payload = {"key": "Methane.m", "start": 1.0, "lower": 0.5, "upper": 3.5}
    payload.update(mutation)

    with pytest.raises(InputError, match=r"start|bound|finite|lower|upper"):
        FittedParameter.from_mapping(payload)


def test_duplicate_and_unsupported_parameter_keys_fail_before_provider_evaluation(monkeypatch) -> None:
    calls = 0
    original = epcsaft.ResolvedModelInput.evaluate

    def counted(self, **kwargs):
        nonlocal calls
        calls += 1
        return original(self, **kwargs)

    monkeypatch.setattr(epcsaft.ResolvedModelInput, "evaluate", counted)
    duplicate = (_parameters()[0], replace(_parameters()[0], start=1.1))
    with pytest.raises(InputError, match="duplicate fitted parameter key"):
        _compile(parameters=duplicate)
    with pytest.raises(InputError, match="not compatible"):
        _compile(parameters=(FittedParameter("Methane.born_diameter", 3.0, 2.0, 4.0),))

    assert calls == 0


def test_row_loss_override_and_untyped_compiler_inputs_are_rejected() -> None:
    row = _row().to_dict()
    row["loss"] = "linear"
    with pytest.raises(InputError, match=r"unknown key.*loss"):
        TargetDataset.from_records((row,), dataset_id="row-loss")
    with pytest.raises(InputError, match="TargetDataset"):
        _compile(dataset={"rows": []})
    with pytest.raises(InputError, match="RegressionControls"):
        _compile(controls=_controls().to_dict())
    with pytest.raises(InputError, match="FittedParameter"):
        _compile(parameters=({"key": "Methane.m"},))


def test_state_correlation_outside_retained_domain_fails_during_compilation() -> None:
    with pytest.raises(InputError, match="outside the sourced record domain"):
        _compile(mixture=_mixture(maximum_K=200.0), dataset=_dataset(temperature=250.0))


def test_canonical_problem_bytes_ignore_mapping_and_parameter_input_order_but_not_row_order() -> None:
    baseline = _compile()
    reversed_parameters = _compile(parameters=tuple(reversed(_parameters())))
    reversed_rows = _compile(
        dataset=TargetDataset(
            rows=tuple(reversed(_dataset().rows)),
            dataset_id=_dataset().dataset_id,
        )
    )

    assert _canonical_problem_json(baseline) == _canonical_problem_json(reversed_parameters)
    assert _canonical_problem_json(baseline) != _canonical_problem_json(reversed_rows)
    assert json.loads(_canonical_problem_json(baseline))["row_ids"] == list(_dataset().row_ids)
