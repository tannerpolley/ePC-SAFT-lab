from __future__ import annotations

import csv
import json

import epcsaft
from epcsaft.model.templates import create_parameter_template
from epcsaft.model.validation import validate_dataset_bundle


def test_create_input_template_writes_parameters_and_workflow_options(tmp_path) -> None:
    root = epcsaft.create_input_template(
        tmp_path / "case",
        components=("Methane", "Ethane"),
        workflows=("state", "equilibrium", "regression"),
    )

    expected_files = {
        "pure_parameters.csv",
        "binary_parameters.csv",
        "permittivity_parameters.csv",
        "model_options.json",
        "state_options.json",
        "equilibrium_options.json",
        "regression_options.json",
    }
    assert {path.name for path in root.iterdir()} == expected_files
    assert (root / "pure_parameters.csv").read_text(encoding="utf-8").splitlines()[0].startswith("component,")
    model_options = json.loads((root / "model_options.json").read_text(encoding="utf-8"))
    assert model_options["differential_mode"] == "autodiff"
    assert model_options["relative_permittivity_rule"] == "component_linear"
    assert model_options["born_model"]["enabled"] is True
    assert "Methane" in (root / "pure_parameters.csv").read_text(encoding="utf-8")


def test_create_parameter_template_writes_source_metadata_and_zero_binary_matrices(tmp_path) -> None:
    root = create_parameter_template(tmp_path, "dataset", species=("H2O", "Na+", "Cl-"))

    pure_file = next((root / "pure").glob("*.csv"))
    pure_header = pure_file.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert pure_header == [
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

    for filename in ("k_ij.csv", "l_ij.csv", "k_hb_ij.csv"):
        with (root / "mixed" / "binary_interaction" / filename).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        for row in rows:
            assert {key: row[key] for key in ("H2O", "Na+", "Cl-")} == {
                "H2O": "0.0",
                "Na+": "0.0",
                "Cl-": "0.0",
            }


def test_legacy_parameter_loader_ignores_source_metadata_column(tmp_path) -> None:
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
    (root / "mixed" / "rel_perm" / "parameters.csv").write_text("organic,a,b,c\n", encoding="utf-8")
    (root / "user_options.json").write_text("{}", encoding="utf-8")

    report = validate_dataset_bundle(root, species=("H2O", "Na+"), x=(0.9, 0.1))

    assert report["valid"]
