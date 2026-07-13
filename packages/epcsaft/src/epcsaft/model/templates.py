"""Helpers for creating strict user-owned ePC-SAFT input templates."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

INPUT_TEMPLATE_WORKFLOWS = {"state", "equilibrium", "regression"}


def _normalize_components(components: Iterable[str] | str) -> list[str]:
    items = components.split(",") if isinstance(components, str) else components
    normalized = [str(item).strip() for item in items if str(item).strip()]
    if not normalized:
        raise ValueError("At least one component must be provided.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Component names must be unique.")
    return normalized


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _unresolved_scientific_records(component: str) -> list[dict[str, Any]]:
    fields = {
        "molar_mass_kg_per_mol": "kg/mol",
        "segment_count": "dimensionless",
        "sigma_angstrom": "angstrom",
        "epsilon_k_K": "K",
        "charge_number": "dimensionless",
        "association_energy_K": "K",
        "association_volume": "dimensionless",
    }
    return [
        {
            "record_id": f"{component}-{field_name}",
            "component": component,
            "field": field_name,
            "units": units,
            "source": None,
            "dependency_signature": {
                "variables": [],
                "composition_components": [],
            },
            "temperature_domain": None,
            "definition": None,
        }
        for field_name, units in fields.items()
    ]


def create_input_template(
    path: str | Path,
    *,
    components: Iterable[str] | str,
    workflows: Iterable[str] = ("state", "equilibrium", "regression"),
) -> Path:
    """Create a strict canonical input scaffold.

    Every scientific parameter is unresolved in the generated parameter set.
    The file therefore fails validation until the user supplies traceable
    values and provenance.
    """

    root = Path(path).expanduser()
    if root.exists():
        raise FileExistsError(f"Input template folder already exists: {root}")
    component_list = _normalize_components(components)
    workflow_list = _normalize_workflows(workflows)
    root.mkdir(parents=True, exist_ok=False)

    _write_json(
        root / "parameter_set.json",
        {
            "schema": "epcsaft.parameter-set",
            "schema_version": 3,
            "components": component_list,
            "pure_records": [
                record
                for component in component_list
                for record in _unresolved_scientific_records(component)
            ],
            "formulation_records": [],
            "interactions": [],
            "interaction_policies": [],
            "metadata": {"source": None},
        },
    )
    _write_json(
        root / "model_configuration.json",
        {
            "schema": "epcsaft.model-configuration",
            "schema_version": 1,
            "selection_origin": "explicit_configuration",
            "formulation": {
                "electrostatics": {"enabled": None},
                "relative_permittivity": {"enabled": None},
                "debye_huckel": {"enabled": None},
                "born": {"enabled": None},
                "solvated_ion_diameter": {"enabled": None},
                "ion_dispersion": {"enabled": None},
            },
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
        _write_json(root / "regression_options.json", {"optimizer": "ceres", "jacobian": "cppad"})
    return root


def _normalize_workflows(workflows: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(str(item).strip().lower() for item in workflows if str(item).strip())
    if not normalized:
        raise ValueError("At least one workflow must be provided.")
    unknown = sorted(set(normalized) - INPUT_TEMPLATE_WORKFLOWS)
    if unknown:
        raise ValueError(f"Unsupported workflow(s): {', '.join(unknown)}.")
    return normalized
