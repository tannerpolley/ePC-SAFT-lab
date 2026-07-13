from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError
from importlib import import_module

import epcsaft_regression as regression
import pytest
from epcsaft import InputError


def _api(name: str):
    value = getattr(regression, name, None)
    assert value is not None, f"epcsaft_regression.{name} is required"
    return value


def _literature_source():
    return _api("SourceIdentity")(
        source_id="Susial_2021_JCED",
        source_kind=_api("SourceKind").LITERATURE,
        citation="10.1021/acs.jced.0c00686",
        locator="Table 6, 100 kPa, row 1",
    )


def _binary_row(*, row_id: str = "susial-table6-row001"):
    composition = _api("CompositionRecord")
    basis = _api("CompositionBasis").MOLE_FRACTION
    return _api("TargetRow")(
        row_id=row_id,
        target_family=_api("TargetFamily").BINARY_VLE,
        conditions={"temperature": 372.3, "pressure": 100000.0},
        observations={},
        units={"temperature": "K", "pressure": "Pa"},
        weight=1.0,
        residual_scale=1.0,
        source=_literature_source(),
        phase="vle",
        compositions=(
            composition("liquid", basis, ("Ethanol", "H2O"), (0.001, 0.999)),
            composition("vapor", basis, ("Ethanol", "H2O"), (0.014, 0.986)),
        ),
    )


def _pure_row(*, family, observation: float, scale: float, units: str):
    return _api("TargetRow")(
        row_id=f"methane-{family.value}-001",
        target_family=family,
        conditions={"temperature": 130.0, "pressure": 367300.0},
        observations={"target": observation},
        units={"temperature": "K", "pressure": "Pa", "target": units},
        weight=0.25,
        residual_scale=scale,
        source=_api("SourceIdentity")(
            source_id="NIST_methane_saturation",
            source_kind=_api("SourceKind").LITERATURE,
            citation="NIST Chemistry WebBook SRD 69",
            locator="Methane saturation table, 130 K",
        ),
        phase="liquid_vapor",
        compositions=(),
    )


def test_strict_dataset_preserves_exact_row_order_and_identity() -> None:
    first = _binary_row(row_id="susial-table6-row001")
    second = _binary_row(row_id="susial-table6-row002")
    dataset = _api("TargetDataset")(
        rows=(first, second),
        dataset_id="susial-2021-table6",
    )

    assert dataset.row_ids == (
        "susial-table6-row001",
        "susial-table6-row002",
    )
    assert dataset.rows == (first, second)
    with pytest.raises(FrozenInstanceError):
        dataset.dataset_id = "changed"


@pytest.mark.parametrize("row_id", ("", " "))
def test_row_identity_is_required(row_id: str) -> None:
    with pytest.raises(InputError, match=r"row_id.*nonblank"):
        _binary_row(row_id=row_id)


def test_dataset_rejects_blank_identity_empty_rows_and_duplicate_row_ids() -> None:
    dataset = _api("TargetDataset")
    row = _binary_row()

    with pytest.raises(InputError, match=r"dataset_id.*nonblank"):
        dataset(rows=(row,), dataset_id="")
    with pytest.raises(InputError, match="at least one"):
        dataset(rows=(), dataset_id="empty")
    with pytest.raises(InputError, match="duplicate row_id"):
        dataset(rows=(row, row), dataset_id="duplicate")


def test_source_kind_rules_distinguish_literature_measurement_and_component_test() -> None:
    source = _api("SourceIdentity")
    kind = _api("SourceKind")

    with pytest.raises(InputError, match="citation"):
        source("literature", kind.LITERATURE, "", "Table 1")
    with pytest.raises(InputError, match="locator"):
        source("literature", kind.LITERATURE, "doi:example", "")
    measurement = source(
        "lab-campaign-2026",
        kind.USER_MEASUREMENT,
        "",
        "Run sheet row 17",
    )
    component = source(
        "generated-native-contract",
        kind.COMPONENT_TEST,
        "",
        "test_targets.py deterministic component case",
    )

    assert measurement.citation == ""
    assert component.source_kind is kind.COMPONENT_TEST


def test_composition_requires_exact_basis_order_length_sum_and_no_normalization() -> None:
    composition = _api("CompositionRecord")
    basis = _api("CompositionBasis").MOLE_FRACTION

    exact = composition(
        "liquid",
        basis,
        ("A", "B"),
        (0.40000001, 0.59999999),
    )

    assert exact.fractions == (0.40000001, 0.59999999)
    with pytest.raises(InputError, match="same length"):
        composition("liquid", basis, ("A", "B"), (1.0,))
    with pytest.raises(InputError, match="unique"):
        composition("liquid", basis, ("A", "A"), (0.5, 0.5))
    with pytest.raises(InputError, match="sum to one"):
        composition("liquid", basis, ("A", "B"), (0.4, 0.5))
    with pytest.raises((InputError, ValueError), match=r"basis|CompositionBasis"):
        composition("liquid", "mass_fraction", ("A", "B"), (0.4, 0.6))
    with pytest.raises(InputError, match="finite number"):
        composition("liquid", basis, ("A", "B"), ("0.4", 0.6))


@pytest.mark.parametrize(
    ("field", "value", "match"),
    (
        ("weight", 0.0, "weight.*positive"),
        ("weight", float("nan"), "weight.*finite"),
        ("residual_scale", 0.0, "residual_scale.*positive"),
        ("residual_scale", float("inf"), "residual_scale.*finite"),
    ),
)
def test_rows_require_explicit_positive_finite_weight_and_scale(
    field: str,
    value: float,
    match: str,
) -> None:
    values = {
        "row_id": "weighted-row",
        "target_family": _api("TargetFamily").BINARY_VLE,
        "conditions": {"temperature": 300.0, "pressure": 100000.0},
        "observations": {},
        "units": {"temperature": "K", "pressure": "Pa"},
        "weight": 1.0,
        "residual_scale": 1.0,
        "source": _literature_source(),
        "phase": "vle",
        "compositions": _binary_row().compositions,
    }
    values[field] = value

    with pytest.raises(InputError, match=match):
        _api("TargetRow")(**values)


@pytest.mark.parametrize(
    ("mutation", "match"),
    (
        ({"temperature": "degC", "pressure": "Pa"}, "canonical units"),
        ({"temperature": "K", "pressure": "bar"}, "canonical units"),
    ),
)
def test_binary_vle_requires_canonical_units(mutation, match: str) -> None:
    row = _binary_row()
    values = row.to_dict()
    values["units"] = mutation

    with pytest.raises(InputError, match=match):
        _api("TargetRow").from_dict(values)


def test_binary_vle_model_targets_are_ordered_log_fugacity_imbalances() -> None:
    targets = import_module("epcsaft_regression.targets")
    row = _binary_row()
    terms = targets._ordered_model_target_pairs(
        row,
        {
            "liquid_fugacity_coefficients": (1.2, 0.9),
            "vapor_fugacity_coefficients": (0.8, 1.1),
        },
    )

    assert [term[0] for term in terms] == ["Ethanol", "H2O"]
    assert terms[0][1] == pytest.approx(
        __import__("math").log(0.001 * 1.2 / (0.014 * 0.8))
    )
    assert terms[1][1] == pytest.approx(
        __import__("math").log(0.999 * 0.9 / (0.986 * 1.1))
    )
    assert [term[2] for term in terms] == [0.0, 0.0]
    with pytest.raises(InputError, match="positive"):
        targets._ordered_model_target_pairs(
            row,
            {
                "liquid_fugacity_coefficients": (0.0, 0.9),
                "vapor_fugacity_coefficients": (0.8, 1.1),
            },
        )


def test_pure_observed_pressure_families_keep_exact_target_meaning() -> None:
    targets = import_module("epcsaft_regression.targets")
    family = _api("TargetFamily")
    fugacity = _pure_row(
        family=family.PURE_SATURATION_FUGACITY_BALANCE,
        observation=0.0,
        scale=1.0,
        units="dimensionless",
    )
    density = _pure_row(
        family=family.PURE_LIQUID_DENSITY_AT_PRESSURE,
        observation=420.0,
        scale=420.0,
        units="kg/m3",
    )

    fugacity_terms = targets._ordered_model_target_pairs(
        fugacity,
        {"liquid_log_fugacity": 12.0, "vapor_log_fugacity": 11.75},
    )
    density_terms = targets._ordered_model_target_pairs(
        density,
        {"liquid_density_kg_per_m3": 410.0},
    )

    assert fugacity_terms == (("fugacity_balance", 0.25, 0.0),)
    assert density_terms == (("liquid_density", 410.0, 420.0),)
    direct_pressure = fugacity.to_dict()
    direct_pressure["observations"] = {"target": 367300.0}
    direct_pressure["units"]["target"] = "Pa"
    with pytest.raises(InputError, match="zero dimensionless target"):
        _api("TargetRow").from_dict(direct_pressure)
    wrong_scale = density.to_dict()
    wrong_scale["residual_scale"] = 1.0
    with pytest.raises(InputError, match="equal the retained density observation"):
        _api("TargetRow").from_dict(wrong_scale)


def test_named_mapping_constructor_rejects_unknown_fields_and_preserves_order() -> None:
    first = _binary_row(row_id="row-2").to_dict()
    second = _binary_row(row_id="row-1").to_dict()
    dataset = _api("TargetDataset").from_records(
        (first, second),
        dataset_id="ordered",
    )

    assert dataset.row_ids == ("row-2", "row-1")
    unknown = copy.deepcopy(first)
    unknown["mystery"] = True
    with pytest.raises(InputError, match=r"unknown key.*mystery"):
        _api("TargetDataset").from_records((unknown,), dataset_id="bad")


def test_target_payloads_are_frozen_copied_and_detached() -> None:
    conditions = {"temperature": 372.3, "pressure": 100000.0}
    payload = _binary_row().to_dict()
    payload["conditions"] = conditions
    row = _api("TargetRow").from_dict(payload)
    conditions["temperature"] = 999.0
    detached = row.to_dict()
    detached["conditions"]["temperature"] = 888.0

    assert row.conditions["temperature"] == 372.3
    assert row.to_dict()["conditions"]["temperature"] == 372.3
    with pytest.raises(TypeError):
        row.conditions["temperature"] = 300.0
