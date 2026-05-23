"""Helpers for creating user-owned ePC-SAFT parameter templates."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

PURE_TEMPLATE_COLUMNS = [
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

MATRIX_TEMPLATE_COLUMNS = ["component"]
REL_PERM_TEMPLATE_COLUMNS = ["organic", "a", "b", "c"]
SUPPORTED_SCHEMAS = {"legacy", "canonical"}
INPUT_TEMPLATE_WORKFLOWS = {"state", "equilibrium", "regression"}
INPUT_PURE_COLUMNS = [
    "component",
    "molar_mass_kg_per_mol",
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
]
INPUT_BINARY_COLUMNS = ["component_i", "component_j", "k_ij", "l_ij", "k_hb_ij"]
INPUT_PERMITTIVITY_COLUMNS = ["component", "epsilon_i_model", "epsilon_i_value", "epsilon_i_units"]


def _prompt(prompt: str) -> str:
    value = input(f"{prompt}: ").strip()
    if not value:
        raise ValueError(f"{prompt} is required.")
    return value


def _normalize_species(species: Iterable[str] | str) -> list[str]:
    if isinstance(species, str):
        items = species.split(",")
    else:
        items = species
    normalized = [str(item).strip() for item in items if str(item).strip()]
    if not normalized:
        raise ValueError("At least one species must be provided.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Species names must be unique.")
    return normalized


def _infer_pure_template_name(species: list[str]) -> str:
    solvent_aliases = {
        "h2o": "water",
        "water": "water",
        "methanol": "methanol",
        "meoh": "methanol",
        "ethanol": "ethanol",
        "etoh": "ethanol",
        "propanol": "propanol",
        "butanol": "butanol",
        "isobutanol": "butanol",
    }
    neutrals = [
        name.strip().lower() for name in species if not name.strip().endswith("+") and not name.strip().endswith("-")
    ]
    if len(neutrals) == 1 and neutrals[0] in solvent_aliases:
        return f"{solvent_aliases[neutrals[0]]}.csv"
    return "any_solvent.csv"


def _write_csv(path: Path, header: list[str], rows: list[list[str | float | int | None]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows:
            writer.writerow(["" if value is None else value for value in row])


def _write_matrix_template(path: Path, species: list[str]) -> None:
    header = MATRIX_TEMPLATE_COLUMNS + species
    rows: list[list[str | float | int | None]] = []
    for row_species in species:
        row = [row_species]
        for _col_species in species:
            row.append(0.0)
        rows.append(row)
    _write_csv(path, header, rows)


def _write_pure_template(path: Path, species: list[str]) -> None:
    rows = [[name] + [None] * (len(PURE_TEMPLATE_COLUMNS) - 1) for name in species]
    _write_csv(path, PURE_TEMPLATE_COLUMNS, rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _canonical_pure_record(component: str) -> dict[str, Any]:
    return {
        "component": component,
        "molar_mass": None,
        "molar_mass_units": "kg/mol",
        "m": None,
        "sigma": None,
        "epsilon_k": None,
        "charge": 0.0,
        "epsilon_k_ab": 0.0,
        "kappa_ab": 0.0,
        "association_scheme": None,
        "association_sites": [],
        "relative_permittivity": None,
        "born_diameter": 0.0,
        "solvation_factor": 1.0,
    }


def _write_canonical_template(root: Path, species: list[str]) -> None:
    root.mkdir(parents=True, exist_ok=False)
    _write_json(
        root / "parameter_set.json",
        {
            "schema": "canonical",
            "schema_version": 1,
            "components": species,
            "pure_records": [_canonical_pure_record(component) for component in species],
            "binary_records": [],
            "metadata": {
                "template_note": (
                    "Fill molar_mass in kg/mol or construct records with "
                    "PureRecord.from_g_per_mol(...) before loading."
                )
            },
        },
    )
    _write_json(root / "user_options.json", {})


def _write_legacy_template(root: Path, species: list[str]) -> None:
    (root / "pure").mkdir(parents=True, exist_ok=False)
    (root / "mixed" / "binary_interaction").mkdir(parents=True, exist_ok=False)
    (root / "mixed" / "rel_perm").mkdir(parents=True, exist_ok=False)

    pure_name = _infer_pure_template_name(species)
    _write_pure_template(root / "pure" / pure_name, species)
    _write_matrix_template(root / "mixed" / "binary_interaction" / "k_ij.csv", species)
    _write_matrix_template(root / "mixed" / "binary_interaction" / "l_ij.csv", species)
    _write_matrix_template(root / "mixed" / "binary_interaction" / "k_hb_ij.csv", species)
    _write_csv(root / "mixed" / "rel_perm" / "parameters.csv", REL_PERM_TEMPLATE_COLUMNS, [])
    _write_json(root / "user_options.json", {})


def create_parameter_template(
    location: str | Path | None = None,
    folder_name: str | None = None,
    species: Iterable[str] | str | None = None,
    *,
    schema: str = "legacy",
) -> Path:
    """Create a user-owned dataset scaffold and return its root path.

    If any of the inputs are omitted, the function prompts for them.
    ``schema="legacy"`` preserves the older CSV layout consumed by the internal
    runtime bridge. ``schema="canonical"`` writes a JSON scaffold aligned to
    ``PureRecord`` and ``BinaryRecord`` fields.
    """

    if location is None:
        location = _prompt("Template location")
    if folder_name is None:
        folder_name = _prompt("Template folder name")
    if species is None:
        species = _prompt("Comma-separated species list")

    schema_name = str(schema).strip().lower()
    if schema_name not in SUPPORTED_SCHEMAS:
        raise ValueError(f"Unsupported parameter template schema {schema!r}; expected 'legacy' or 'canonical'.")

    root = Path(location).expanduser() / str(folder_name).strip()
    if root.exists():
        raise FileExistsError(f"Template folder already exists: {root}")

    species_list = _normalize_species(species)

    if schema_name == "canonical":
        _write_canonical_template(root, species_list)
    else:
        _write_legacy_template(root, species_list)

    return root


def create_input_template(
    path: str | Path,
    *,
    components: Iterable[str] | str,
    workflows: Iterable[str] = ("state", "equilibrium", "regression"),
) -> Path:
    """Create the reset API input scaffold.

    The scaffold separates parameter tables from workflow/model options so that
    ``ParameterSet`` owns only ePC-SAFT parameter data.
    """

    root = Path(path).expanduser()
    if root.exists():
        raise FileExistsError(f"Input template folder already exists: {root}")
    component_list = _normalize_species(components)
    workflow_list = _normalize_workflows(workflows)
    root.mkdir(parents=True, exist_ok=False)

    _write_csv(root / "pure_parameters.csv", INPUT_PURE_COLUMNS, _input_pure_rows(component_list))
    _write_csv(root / "binary_parameters.csv", INPUT_BINARY_COLUMNS, _input_binary_rows(component_list))
    _write_csv(root / "permittivity_parameters.csv", INPUT_PERMITTIVITY_COLUMNS, _input_permittivity_rows(component_list))
    _write_json(
        root / "model_options.json",
        {
            "relative_permittivity_rule": "component_linear",
            "born_formulation": "disabled",
        },
    )
    if "state" in workflow_list:
        _write_json(root / "state_options.json", {"phase": "liq", "closure": "pressure"})
    if "equilibrium" in workflow_list:
        _write_json(
            root / "equilibrium_options.json",
            {
                "max_iterations": 180,
                "tolerance": 1.0e-8,
                "ipopt_iteration_history_limit": 20,
            },
        )
    if "regression" in workflow_list:
        _write_json(
            root / "regression_options.json",
            {
                "optimizer": "ceres",
                "jacobian": "cppad",
            },
        )
    return root


def _normalize_workflows(workflows: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(str(item).strip().lower() for item in workflows if str(item).strip())
    if not normalized:
        raise ValueError("At least one workflow must be provided.")
    unknown = sorted(set(normalized) - INPUT_TEMPLATE_WORKFLOWS)
    if unknown:
        raise ValueError(f"Unsupported workflow(s): {', '.join(unknown)}.")
    return normalized


def _input_pure_rows(components: list[str]) -> list[list[str | float | int | None]]:
    return [[component] + [None] * (len(INPUT_PURE_COLUMNS) - 1) for component in components]


def _input_binary_rows(components: list[str]) -> list[list[str | float | int | None]]:
    rows: list[list[str | float | int | None]] = []
    for i, left in enumerate(components):
        for right in components[i + 1 :]:
            rows.append([left, right, 0.0, 0.0, 0.0])
    return rows


def _input_permittivity_rows(components: list[str]) -> list[list[str | float | int | None]]:
    return [[component, "constant", None, "dimensionless"] for component in components]
