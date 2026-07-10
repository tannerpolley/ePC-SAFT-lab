from __future__ import annotations

import copy
import csv
import inspect
import json
from pathlib import Path

import numpy as np
import pytest
from epcsaft import ParameterSet
from epcsaft._types import InputError
from epcsaft.model import datasets
from epcsaft.model.parameters import PureRecord
from epcsaft.model.sources import load_canonical_user_options
from epcsaft.model.validation import validate_dataset_bundle

REPO_ROOT = Path(__file__).resolve().parents[5]


def _canonical_payload(*, component: str = "Test neutral") -> dict[str, object]:
    return {
        "schema": "epcsaft.parameter-set",
        "schema_version": 2,
        "components": [component],
        "pure_records": [
            {
                "component": component,
                "molar_mass": 44.01e-3,
                "molar_mass_units": "kg/mol",
                "m": 2.1,
                "sigma": 3.4,
                "epsilon_k": 220.0,
                "charge": 0.0,
                "epsilon_k_ab": 0.0,
                "kappa_ab": 0.0,
                "association_scheme": None,
                "association_sites": [],
                "relative_permittivity": 1.0,
                "born_diameter": 0.0,
                "solvation_factor": 1.0,
            }
        ],
        "interactions": [],
        "interaction_policies": [],
        "metadata": {
            "source": "Test literature table",
            "source_backed": True,
        },
    }


def _pure_record(payload: dict[str, object]) -> dict[str, object]:
    records = payload["pure_records"]
    assert isinstance(records, list)
    record = records[0]
    assert isinstance(record, dict)
    return record


def _write_csv_dataset(
    root: Path,
    *,
    rows: list[dict[str, object]],
) -> Path:
    pure_dir = root / "pure"
    pure_dir.mkdir(parents=True)
    path = pure_dir / "any_solvent.csv"
    fieldnames = [
        "component",
        "m",
        "s",
        "e",
        "e_assoc",
        "vol_a",
        "assoc_scheme",
        "z",
        "dielc",
        "d_born",
        "f_solv",
        "MW",
        "source",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return root


def _explicit_dataset_row(component: str = "Test neutral") -> dict[str, object]:
    return {
        "component": component,
        "m": 2.1,
        "s": 3.4,
        "e": 220.0,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": "",
        "z": 0.0,
        "dielc": 1.0,
        "d_born": 0.0,
        "f_solv": 1.0,
        "MW": 44.01e-3,
        "source": "Test literature table",
    }


def test_from_dict_accepts_only_the_versioned_canonical_schema() -> None:
    parameters = ParameterSet.from_dict(_canonical_payload())

    assert parameters.components == ("Test neutral",)

    with pytest.raises(InputError, match="versioned canonical schema"):
        ParameterSet.from_dict(
            {
                "MW": np.asarray([44.01e-3]),
                "m": np.asarray([2.1]),
                "s": np.asarray([3.4]),
                "e": np.asarray([220.0]),
            },
            species=["Test neutral"],
        )


@pytest.mark.parametrize(
    "schema,schema_version",
    [
        (None, 2),
        ("canonical", 2),
        ("epcsaft.parameter-set", None),
        ("epcsaft.parameter-set", 1),
        ("epcsaft.parameter-set", 3),
        ("epcsaft.parameter-set", True),
        ("epcsaft.parameter-set", 2.0),
    ],
)
def test_from_dict_rejects_missing_or_unknown_schema_identity(
    schema: object,
    schema_version: object,
) -> None:
    payload = _canonical_payload()
    if schema is None:
        payload.pop("schema")
    else:
        payload["schema"] = schema
    if schema_version is None:
        payload.pop("schema_version")
    else:
        payload["schema_version"] = schema_version

    with pytest.raises(InputError, match=r"epcsaft.parameter-set.*schema_version 2"):
        ParameterSet.from_dict(payload)


@pytest.mark.parametrize(
    "field",
    [
        "molar_mass",
        "m",
        "sigma",
        "epsilon_k",
        "charge",
        "epsilon_k_ab",
        "kappa_ab",
        "association_scheme",
        "relative_permittivity",
        "born_diameter",
        "solvation_factor",
    ],
)
def test_canonical_pure_records_name_every_missing_scientific_field(field: str) -> None:
    payload = _canonical_payload(component="Component X")
    _pure_record(payload).pop(field)

    with pytest.raises(InputError, match=rf"Component X\.{field}"):
        ParameterSet.from_dict(payload)


@pytest.mark.parametrize(
    "field",
    [
        "molar_mass",
        "m",
        "sigma",
        "epsilon_k",
        "charge",
        "epsilon_k_ab",
        "kappa_ab",
        "relative_permittivity",
        "born_diameter",
        "solvation_factor",
    ],
)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_canonical_pure_records_reject_every_nonfinite_scalar(field: str, value: float) -> None:
    payload = _canonical_payload(component="Component X")
    _pure_record(payload)[field] = value

    with pytest.raises(InputError, match=rf"Component X\.{field}.*finite"):
        ParameterSet.from_dict(payload)


def test_unknown_canonical_keys_are_rejected_at_their_owner() -> None:
    top_level = _canonical_payload()
    top_level["mystery"] = 1
    with pytest.raises(InputError, match=r"canonical parameter payload.*mystery"):
        ParameterSet.from_dict(top_level)

    pure_level = _canonical_payload(component="Component X")
    _pure_record(pure_level)["mystery"] = 1
    with pytest.raises(InputError, match=r"Component X.*mystery"):
        ParameterSet.from_dict(pure_level)


@pytest.mark.parametrize(
    "field,value",
    [
        ("components", "Component X"),
        ("pure_records", {"component": "Component X"}),
        ("interactions", {}),
        ("interaction_policies", {}),
        ("metadata", []),
        ("runtime_options", []),
    ],
)
def test_canonical_collection_fields_require_exact_json_container_types(field: str, value: object) -> None:
    payload = _canonical_payload()
    payload[field] = value

    with pytest.raises(InputError, match=field):
        ParameterSet.from_dict(payload)


@pytest.mark.parametrize(
    "association_sites,match",
    [
        (["donor"], r"association_sites.*mapping"),
        ([{"label": "donor"}], r"association_sites.*kind"),
        ([{"label": "donor", "kind": "donor", "mystery": 1}], r"association_sites.*mystery"),
        ([{"label": "", "kind": "donor"}], r"association_sites.*label"),
    ],
)
def test_association_site_records_are_explicit_and_strict(association_sites: object, match: str) -> None:
    payload = _canonical_payload(component="Associating X")
    record = _pure_record(payload)
    record["epsilon_k_ab"] = 1800.0
    record["kappa_ab"] = 0.03
    record["association_scheme"] = "2B"
    record["association_sites"] = association_sites

    with pytest.raises(InputError, match=match):
        ParameterSet.from_dict(payload)


def test_direct_pure_record_rejects_blank_component_identity() -> None:
    with pytest.raises(InputError, match=r"component.*nonblank"):
        PureRecord(
            component=" ",
            molar_mass=44.01e-3,
            m=2.1,
            sigma=3.4,
            epsilon_k=220.0,
            charge=0.0,
            epsilon_k_ab=0.0,
            kappa_ab=0.0,
            association_scheme=None,
            relative_permittivity=1.0,
            born_diameter=0.0,
            solvation_factor=1.0,
        )


def test_source_backed_metadata_requires_an_exact_boolean_and_source_identity() -> None:
    nonboolean = _canonical_payload()
    metadata = nonboolean["metadata"]
    assert isinstance(metadata, dict)
    metadata["source_backed"] = "false"
    with pytest.raises(InputError, match=r"metadata\.source_backed.*boolean"):
        ParameterSet.from_dict(nonboolean)

    unidentified = _canonical_payload()
    metadata = unidentified["metadata"]
    assert isinstance(metadata, dict)
    metadata["source"] = None
    with pytest.raises(InputError, match=r"source_backed.*source identity"):
        ParameterSet.from_dict(unidentified)


def test_canonical_components_are_unique_and_exactly_match_pure_records() -> None:
    duplicate = _canonical_payload(component="Component X")
    duplicate["components"] = ["Component X", "Component X"]
    with pytest.raises(InputError, match=r"components must be unique"):
        ParameterSet.from_dict(duplicate)

    extra = _canonical_payload(component="Component X")
    second_record = copy.deepcopy(_pure_record(extra))
    second_record["component"] = "Undeclared Y"
    pure_records = extra["pure_records"]
    assert isinstance(pure_records, list)
    pure_records.append(second_record)
    with pytest.raises(InputError, match=r"pure records for undeclared components: Undeclared Y"):
        ParameterSet.from_dict(extra)


def test_association_topology_and_parameters_must_agree() -> None:
    missing_parameters = _canonical_payload(component="Associating X")
    _pure_record(missing_parameters)["association_scheme"] = "2B"
    with pytest.raises(InputError, match=r"Associating X.*association.*positive"):
        ParameterSet.from_dict(missing_parameters)

    hidden_association = _canonical_payload(component="Nonassociating X")
    _pure_record(hidden_association)["epsilon_k_ab"] = 1200.0
    _pure_record(hidden_association)["kappa_ab"] = 0.02
    with pytest.raises(InputError, match=r"Nonassociating X.*association_scheme"):
        ParameterSet.from_dict(hidden_association)


def test_charged_component_requires_explicit_positive_born_and_solvation_inputs() -> None:
    payload = _canonical_payload(component="Ion with arbitrary label")
    record = _pure_record(payload)
    record["charge"] = 1.0
    record["relative_permittivity"] = 8.0

    with pytest.raises(InputError, match=r"Ion with arbitrary label\.born_diameter.*positive"):
        ParameterSet.from_dict(payload)

    record["born_diameter"] = 3.2
    record["solvation_factor"] = 0.0
    with pytest.raises(InputError, match=r"Ion with arbitrary label\.solvation_factor.*positive"):
        ParameterSet.from_dict(payload)


def test_component_suffix_neither_supplies_nor_overrides_charge() -> None:
    missing = _canonical_payload(component="Suffix+")
    _pure_record(missing).pop("charge")
    with pytest.raises(InputError, match=r"Suffix\+\.charge"):
        ParameterSet.from_dict(missing)

    explicit = copy.deepcopy(_canonical_payload(component="Suffix+"))
    parameters = ParameterSet.from_dict(explicit)
    assert parameters.pure_records[0].charge == 0.0


def test_dataset_loader_rejects_suffix_inferred_charge(tmp_path: Path) -> None:
    row = _explicit_dataset_row("Arbitrary+")
    row["z"] = ""
    row["d_born"] = 3.2
    dataset_root = _write_csv_dataset(tmp_path / "dataset", rows=[row])

    with pytest.raises(KeyError, match=r"Arbitrary\+.*z"):
        datasets.get_prop_dict(dataset_root, ["Arbitrary+"], [1.0], 298.15)


@pytest.mark.parametrize("field", ["d_born", "f_solv"])
def test_dataset_loader_rejects_blank_required_ion_fields(tmp_path: Path, field: str) -> None:
    row = _explicit_dataset_row("Ion")
    row["z"] = 1.0
    row["d_born"] = 3.2
    row[field] = ""
    dataset_root = _write_csv_dataset(tmp_path / "dataset", rows=[row])

    with pytest.raises(KeyError, match=rf"Ion.*{field}"):
        datasets.get_prop_dict(dataset_root, ["Ion"], [1.0], 298.15)


@pytest.mark.parametrize("field", ["e_assoc", "vol_a", "dielc"])
def test_dataset_loader_rejects_blank_required_scientific_fields(tmp_path: Path, field: str) -> None:
    row = _explicit_dataset_row("Component X")
    row[field] = ""
    dataset_root = _write_csv_dataset(tmp_path / "dataset", rows=[row])

    with pytest.raises(KeyError, match=rf"Component X.*{field}"):
        datasets.get_prop_dict(dataset_root, ["Component X"], [1.0], 298.15)


def test_dataset_loader_requires_association_topology_for_active_parameters(tmp_path: Path) -> None:
    row = _explicit_dataset_row("Associating X")
    row["e_assoc"] = 1800.0
    row["vol_a"] = 0.03
    dataset_root = _write_csv_dataset(tmp_path / "dataset", rows=[row])

    with pytest.raises(InputError, match=r"Associating X\.association_scheme"):
        ParameterSet.from_dataset(dataset_root, ["Associating X"], x=[1.0], T=298.15)


def test_dataset_loader_rejects_nonfinite_cells_at_the_field_owner(tmp_path: Path) -> None:
    row = _explicit_dataset_row()
    row["m"] = "nan"
    dataset_root = _write_csv_dataset(tmp_path / "dataset", rows=[row])

    with pytest.raises(ValueError, match=r"Test neutral.*m.*finite"):
        datasets.get_prop_dict(dataset_root, ["Test neutral"], [1.0], 298.15)


def test_dataset_loader_rejects_loose_numeric_text(tmp_path: Path) -> None:
    row = _explicit_dataset_row()
    row["s"] = "sigma=3.4"
    dataset_root = _write_csv_dataset(tmp_path / "dataset", rows=[row])

    with pytest.raises(ValueError, match=r"Test neutral.*s.*sigma=3.4"):
        datasets.get_prop_dict(dataset_root, ["Test neutral"], [1.0], 298.15)


def test_dataset_loader_rejects_duplicate_component_rows(tmp_path: Path) -> None:
    dataset_root = _write_csv_dataset(
        tmp_path / "dataset",
        rows=[_explicit_dataset_row(), _explicit_dataset_row()],
    )

    with pytest.raises(ValueError, match=r"duplicate.*Test neutral"):
        datasets.get_prop_dict(dataset_root, ["Test neutral"], [1.0], 298.15)


def test_parameter_set_from_dataset_builds_canonical_records(tmp_path: Path) -> None:
    dataset_root = _write_csv_dataset(
        tmp_path / "dataset",
        rows=[_explicit_dataset_row()],
    )

    parameters = ParameterSet.from_dataset(
        dataset_root,
        ["Test neutral"],
        x=[1.0],
        T=298.15,
    )

    assert parameters.components == ("Test neutral",)
    assert parameters.pure_records[0].sigma == pytest.approx(3.4)
    assert parameters.metadata["dataset"] == str(dataset_root)
    assert parameters.metadata["source"] == "Test literature table"
    assert parameters.metadata["source_backed"] is True
    runtime = parameters.to_runtime_dict()
    assert runtime["_parameter_source_label"] == "Test literature table"
    assert runtime["_parameter_provenance_status"] == "source_backed_parameter_metadata"


def test_dataset_with_multiple_pure_sets_requires_typed_configuration(tmp_path: Path) -> None:
    dataset_root = _write_csv_dataset(
        tmp_path / "dataset",
        rows=[_explicit_dataset_row()],
    )
    (dataset_root / "pure" / "water.csv").write_text(
        (dataset_root / "pure" / "any_solvent.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"multiple pure parameter sets.*versioned model configuration"):
        ParameterSet.from_dataset(dataset_root, ["Test neutral"], x=[1.0], T=298.15)


def test_dataset_user_options_reject_legacy_envelopes_and_nonobjects(tmp_path: Path) -> None:
    (tmp_path / "user_options.json").write_text(
        '{"canonical_user_options": {"elec_model": {}}}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="top-level model configuration object"):
        load_canonical_user_options(tmp_path)

    (tmp_path / "user_options.json").write_text("[]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_canonical_user_options(tmp_path)


def test_parameter_folder_accepts_only_canonical_parameter_set_json(tmp_path: Path) -> None:
    (tmp_path / "pure_parameters.csv").write_text(
        "component,molar_mass_kg_per_mol,m,sigma,epsilon_k\n"
        "Test neutral,0.04401,2.1,3.4,220.0\n",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match=r"parameter_set\.json"):
        ParameterSet.from_folder(tmp_path, components=["Test neutral"])

    assert not hasattr(ParameterSet, "_from_input_template_folder")


def test_parameter_folder_api_has_no_unused_reference_state_arguments() -> None:
    parameters = inspect.signature(ParameterSet.from_folder).parameters

    assert "x" not in parameters
    assert "T" not in parameters
    assert not hasattr(ParameterSet, "to_legacy_dict")


def _nonzero_manifest_pairs(parameter_root: Path) -> set[frozenset[str]]:
    manifest, _wildcards = datasets._load_interaction_source_manifest(
        parameter_root / "mixed" / "binary_interaction" / "source_manifest.csv"
    )
    return {
        pair
        for (family, pair), (signature, _source, _status, _reason) in manifest.items()
        if family == "k_ij" and signature[0] == "constant" and signature[1] != 0.0
    }


def test_source_backed_gross_parameter_counts_are_characterized() -> None:
    gross_2001 = REPO_ROOT / "analyses" / "paper_validation" / "2001_gross" / "parameters"
    gross_2002 = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "parameters"

    assert len(datasets._load_component_rows(gross_2001 / "pure" / "any_solvent.csv")) == 78
    assert len(datasets._load_component_rows(gross_2002 / "pure" / "any_solvent.csv")) == 22
    assert len(_nonzero_manifest_pairs(gross_2001)) == 24
    assert len(_nonzero_manifest_pairs(gross_2002)) == 10


def test_held_2008_catalog_contains_only_the_source_backed_aqueous_subset() -> None:
    path = (
        REPO_ROOT
        / "analyses"
        / "paper_validation"
        / "2008_held"
        / "parameters"
        / "pure"
        / "water.csv"
    )
    rows = datasets._load_component_rows(path)

    assert set(rows) == {"H2O", "Li+", "Na+", "K+", "Cl-", "Br-", "I-"}
    assert all("default fill" not in row["source"] for row in rows.values())


def test_held_2012_ethanol_permittivity_is_the_complete_source_correlation() -> None:
    pure_root = (
        REPO_ROOT
        / "analyses"
        / "paper_validation"
        / "2012_held"
        / "parameters"
        / "pure"
    )

    for path in sorted(pure_root.glob("*.csv")):
        rows = datasets._load_component_rows(path)
        assert rows["Ethanol"]["dielc"] == "-0.132*T+64.072"


def test_held_2012_model_options_do_not_receive_derived_receipt_fields() -> None:
    parameter_root = REPO_ROOT / "analyses" / "paper_validation" / "2012_held" / "parameters"
    source_payload = json.loads((parameter_root / "user_options.json").read_text(encoding="utf-8"))
    loaded = load_canonical_user_options(parameter_root)

    resolved = datasets._resolve_runtime_options(loaded)

    assert loaded == source_payload
    assert {"preset_key", "preset", "catalog"}.isdisjoint(loaded)
    assert {"preset_key", "preset", "catalog"}.issubset(resolved)


def test_figiel_any_solvent_ion_records_are_used_without_inventing_solvent_specific_sets() -> None:
    parameter_root = REPO_ROOT / "analyses" / "paper_validation" / "2025_figiel" / "parameters"
    species = ("Methanol", "H2O", "Li+", "Cl-")
    composition = np.asarray([0.29880, 0.61277, 0.044213, 0.044213], dtype=float)
    composition /= composition.sum()

    with pytest.raises(InputError, match=r"(?i)wildcard interaction"):
        datasets.get_prop_dict(parameter_root, species, composition, 351.25)

    payload = datasets._resolve_dataset_runtime_payload(parameter_root, species, composition, 351.25)

    assert payload["e"].tolist() == pytest.approx([188.90, 353.95, 360.0, 170.0])
    assert payload["mixed_ion_dispersion_sources"] == pytest.approx({"pure/any_solvent.csv": 2.0})


def test_dataset_module_has_no_embedded_component_catalog_or_named_dataset_lookup() -> None:
    assert not hasattr(datasets, "_COMPONENT_DEFAULTS")
    assert not hasattr(datasets, "_deterministic_default")
    assert not hasattr(datasets, "_default_species_entry")
    assert not hasattr(datasets, "available_datasets")


def test_molality_conversion_uses_explicit_charge_and_molar_mass_data() -> None:
    species = ("Solvent", "Cation", "Anion")
    charges = {"Solvent": 0.0, "Cation": 1.0, "Anion": -1.0}
    molar_masses = {"Solvent": 18.01528e-3, "Cation": 22.989e-3, "Anion": 35.45e-3}

    mole_fractions = datasets.molality_to_molefraction(
        1.0,
        species=species,
        solvent="Solvent",
        charges=charges,
        molar_masses=molar_masses,
    )
    recovered = datasets.molefraction_to_molality(
        mole_fractions,
        species=species,
        solvent="Solvent",
        charges=charges,
        molar_masses=molar_masses,
    )

    assert recovered == pytest.approx(1.0)


def test_molality_conversion_does_not_infer_charge_from_component_suffixes() -> None:
    with pytest.raises(ValueError, match=r"charges.*Cation\+"):
        datasets.molality_to_molefraction(
            1.0,
            species=("Solvent", "Cation+", "Anion-"),
            solvent="Solvent",
            charges={"Solvent": 0.0},
            molar_masses={"Solvent": 18.01528e-3, "Cation+": 22.989e-3, "Anion-": 35.45e-3},
        )


def _validation_payload(
    *,
    component: str = "Component",
    charge: float | None = 0.0,
    born_diameter: float | None = 0.0,
) -> dict[str, object]:
    payload = _canonical_payload(component=component)
    record = _pure_record(payload)
    if charge is None:
        record.pop("charge")
    else:
        record["charge"] = charge
    if born_diameter is None:
        record.pop("born_diameter")
    else:
        record["born_diameter"] = born_diameter
    return payload


def test_dataset_validation_requires_explicit_charge_and_born_data() -> None:
    missing_charge = validate_dataset_bundle(
        _validation_payload(charge=None),
        species=["Component"],
    )
    assert missing_charge["valid"] is False
    assert any("Component.charge" in error for error in missing_charge["errors"])

    missing_born = validate_dataset_bundle(
        _validation_payload(charge=1.0, born_diameter=None),
        species=["Component"],
    )
    assert missing_born["valid"] is False
    assert any("Component.born_diameter" in error for error in missing_born["errors"])


def test_dataset_validation_does_not_infer_charge_from_component_suffix() -> None:
    report = validate_dataset_bundle(
        _validation_payload(component="Arbitrary+", charge=0.0),
        species=["Arbitrary+"],
    )

    assert report["valid"] is True
    assert report["errors"] == []


def test_dataset_validation_rejects_raw_parallel_array_mappings() -> None:
    report = validate_dataset_bundle(
        {
            "m": np.asarray([2.1]),
            "s": np.asarray([3.4]),
            "e": np.asarray([220.0]),
            "z": np.asarray([0.0]),
        },
        species=["Component"],
    )

    assert report["valid"] is False
    assert any("versioned canonical schema" in error for error in report["errors"])
