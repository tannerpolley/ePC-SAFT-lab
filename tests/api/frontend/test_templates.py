from __future__ import annotations

import json

import epcsaft


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
    assert json.loads((root / "model_options.json").read_text(encoding="utf-8"))["relative_permittivity_rule"]
    assert "Methane" in (root / "pure_parameters.csv").read_text(encoding="utf-8")
