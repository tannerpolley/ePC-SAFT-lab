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


def _canonical_pure_record(component: str) -> dict[str, Any]:
    return {
        "component": component,
        "molar_mass": None,
        "molar_mass_units": "kg/mol",
        "m": None,
        "sigma": None,
        "epsilon_k": None,
        "charge": None,
        "epsilon_k_ab": None,
        "kappa_ab": None,
        "association_scheme": None,
        "association_sites": [],
        "relative_permittivity": None,
        "born_diameter": None,
        "solvation_factor": None,
    }


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
            "schema_version": 2,
            "components": component_list,
            "pure_records": [_canonical_pure_record(component) for component in component_list],
            "interactions": [],
            "interaction_policies": [],
            "metadata": {"source": None, "source_backed": False},
        },
    )
    _write_json(
        root / "model_options.json",
        {
            "differential_mode": "autodiff",
            "relative_permittivity_rule": "component_linear",
            "born_model": {
                "enabled": True,
                "born_diameter_rule": "sigma",
                "solvation_shell_model": True,
                "dielectric_saturation": True,
                "bulk_mode": "mix",
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
