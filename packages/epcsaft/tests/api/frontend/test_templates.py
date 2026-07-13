from __future__ import annotations

import csv
import json

import epcsaft
import pytest
from epcsaft._types import InputError
from epcsaft.model.validation import validate_dataset_bundle


def test_create_input_template_writes_versioned_parameter_set_and_workflow_options(tmp_path) -> None:
    root = epcsaft.create_input_template(
        tmp_path / "case",
        components=("Methane", "Ethane"),
        workflows=("state", "equilibrium", "regression"),
    )

    expected_files = {
        "parameter_set.json",
        "model_configuration.json",
        "state_options.json",
        "equilibrium_options.json",
        "regression_options.json",
    }
    assert {path.name for path in root.iterdir()} == expected_files
    parameter_set = json.loads((root / "parameter_set.json").read_text(encoding="utf-8"))
    assert parameter_set["schema"] == "epcsaft.parameter-set"
    assert parameter_set["schema_version"] == 3
    assert parameter_set["components"] == ["Methane", "Ethane"]
    assert parameter_set["formulation_records"] == []
    assert parameter_set["interactions"] == []
    assert parameter_set["interaction_policies"] == []
    assert parameter_set["metadata"] == {"source": None}
    expected_fields = {
        "molar_mass_kg_per_mol",
        "segment_count",
        "sigma_angstrom",
        "epsilon_k_K",
        "charge_number",
        "association_energy_K",
        "association_volume",
    }
    for component in ("Methane", "Ethane"):
        records = [record for record in parameter_set["pure_records"] if record["component"] == component]
        assert {record["field"] for record in records} == expected_fields
        assert all(record["source"] is None for record in records)
        assert all(record["temperature_domain"] is None for record in records)
        assert all(record["definition"] is None for record in records)
    configuration = json.loads((root / "model_configuration.json").read_text(encoding="utf-8"))
    assert configuration["schema"] == "epcsaft.model-configuration"
    assert configuration["schema_version"] == 1
    assert all(record == {"enabled": None} for record in configuration["formulation"].values())
    assert not (root / "model_options.json").exists()
    assert not (root / "user_options.json").exists()


def test_created_input_template_fails_loudly_until_scientific_values_are_filled(tmp_path) -> None:
    root = epcsaft.create_input_template(tmp_path / "case", components=("Methane",), workflows=("state",))

    with pytest.raises(InputError, match="scientific source"):
        epcsaft.model.load_source_bundle_selection(root, components=("Methane",))


def test_source_dataset_loader_preserves_source_metadata_column(tmp_path) -> None:
    root = tmp_path / "dataset"
    (root / "pure").mkdir(parents=True)
    (root / "mixed" / "binary_interaction").mkdir(parents=True)
    (root / "mixed" / "rel_perm").mkdir(parents=True)
    (root / "pure" / "any_solvent.csv").write_text(
        "\n".join(
            [
                "component,m,s,e,e_assoc,vol_a,assoc_scheme,z,dielc,d_born,f_solv,MW,source",
                "H2O,1.2047,3.0,353.95,2425.7,0.04509,2B,0,78.09,0,1.5,0.01801528,Test Table",
                "Na+,1,2.0,100,0,0,,1,8,3.445,1,0.02299,Test Table",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for filename in ("k_ij.csv", "l_ij.csv", "k_hb_ij.csv"):
        (root / "mixed" / "binary_interaction" / filename).write_text(
            "component,H2O,Na+\nH2O,0,0\nNa+,0,0\n",
            encoding="utf-8",
        )
    (root / "mixed" / "binary_interaction" / "source_manifest.csv").write_text(
        "parameter,component_i,component_j,value,source,provenance_status\n"
        "k_ij,H2O,Na+,0,Test interaction table,source_backed\n"
        "l_ij,H2O,Na+,0,Test interaction table,source_backed\n"
        "k_hb_ij,H2O,Na+,0,Test interaction table,source_backed\n",
        encoding="utf-8",
    )
    (root / "mixed" / "rel_perm" / "parameters.csv").write_text("organic,a,b,c\n", encoding="utf-8")
    (root / "user_options.json").write_text("{}", encoding="utf-8")

    report = validate_dataset_bundle(root, species=("H2O", "Na+"), x=(0.9, 0.1))

    assert report["valid"]
