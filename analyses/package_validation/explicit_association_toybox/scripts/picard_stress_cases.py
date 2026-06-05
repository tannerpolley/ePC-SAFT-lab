from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from collections.abc import Mapping

import numpy as np
import yaml

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.association_case_matrix import (
        AssociationEvidenceCase,
        association_case_by_id,
    )
else:
    from .association_case_matrix import AssociationEvidenceCase, association_case_by_id

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ANALYSIS_ROOT / "config" / "picard_stress_evidence.yaml"


@dataclass(frozen=True)
class PicardStressSpec:
    case_id: str
    case_family: str
    topology_id: str
    simulation_scope: str
    decision_role: str
    axes: Mapping[str, object]


@dataclass(frozen=True)
class PicardStressCase:
    stress_case_id: str
    source_case_id: str
    case_family: str
    topology_id: str
    simulation_scope: str
    decision_role: str
    axis_id: str
    density: float
    temperature: float
    strength_scale: float
    composition: np.ndarray
    source_case: AssociationEvidenceCase

    @property
    def case_id(self) -> str:
        return self.stress_case_id

    @property
    def composition_text(self) -> str:
        return ";".join(f"{float(value):.12g}" for value in self.composition)

    def scaled_delta(self) -> np.ndarray:
        return self.source_case.scaled_delta(self.strength_scale)


def load_picard_stress_specs(path: Path = DEFAULT_CONFIG) -> tuple[PicardStressSpec, ...]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("stress_matrix"), list):
        raise ValueError(f"{path} must define a stress_matrix list.")
    specs: list[PicardStressSpec] = []
    for entry in data["stress_matrix"]:
        if not isinstance(entry, Mapping):
            raise ValueError("each Picard stress entry must be a mapping.")
        base = association_case_by_id(str(entry["case_id"]))
        axes = entry.get("axes")
        if not isinstance(axes, Mapping) or not axes:
            raise ValueError(f"{base.case_id} must define stress axes.")
        specs.append(
            PicardStressSpec(
                case_id=base.case_id,
                case_family=str(entry["case_family"]),
                topology_id=base.topology_id,
                simulation_scope=str(entry["simulation_scope"]),
                decision_role=str(entry["decision_role"]),
                axes=dict(axes),
            )
        )
    return tuple(specs)


def materialize_picard_stress_cases(
    specs: tuple[PicardStressSpec, ...] | None = None,
    *,
    max_cases: int | None = None,
) -> tuple[PicardStressCase, ...]:
    selected_specs = specs if specs is not None else load_picard_stress_specs()
    cases: list[PicardStressCase] = []
    for spec in selected_specs:
        source = association_case_by_id(spec.case_id)
        if source.system is None:
            continue
        cases.extend(_axis_cases(spec, source))
    if max_cases is not None:
        return tuple(cases[:max_cases])
    return tuple(cases)


def _axis_cases(spec: PicardStressSpec, source: AssociationEvidenceCase) -> list[PicardStressCase]:
    density = _middle(source.density_grid)
    temperature = _middle(source.temperature_grid)
    strength = float(source.strength_scale)
    composition = np.asarray(source.composition, dtype=float)
    rows: list[PicardStressCase] = []
    for value in _axis_values(spec.axes.get("density"), source.density_grid):
        rows.append(_case(spec, source, axis_id="density", density=value, temperature=temperature, strength=strength, composition=composition))
    for value in _axis_values(spec.axes.get("temperature"), source.temperature_grid):
        rows.append(
            _case(spec, source, axis_id="temperature", density=density, temperature=value, strength=strength, composition=composition)
        )
    strength_axis = spec.axes.get("association_strength", (1.0,))
    for multiplier in _numeric_axis(strength_axis):
        rows.append(
            _case(
                spec,
                source,
                axis_id="association_strength",
                density=density,
                temperature=temperature,
                strength=strength * multiplier,
                composition=composition,
            )
        )
    if source.component_count == 2 and "composition_component_0" in spec.axes:
        for x0 in _numeric_axis(spec.axes["composition_component_0"]):
            rows.append(
                _case(
                    spec,
                    source,
                    axis_id="composition",
                    density=density,
                    temperature=temperature,
                    strength=strength,
                    composition=np.array([x0, 1.0 - x0], dtype=float),
                )
            )
    return rows


def _case(
    spec: PicardStressSpec,
    source: AssociationEvidenceCase,
    *,
    axis_id: str,
    density: float,
    temperature: float,
    strength: float,
    composition: np.ndarray,
) -> PicardStressCase:
    composition = np.asarray(composition, dtype=float)
    if not np.isclose(float(np.sum(composition)), 1.0):
        raise ValueError(f"{source.case_id} composition axis must sum to one.")
    point = _axis_point_text(axis_id, density=density, temperature=temperature, strength=strength, composition=composition)
    return PicardStressCase(
        stress_case_id=f"{source.case_id}:{axis_id}:{point}",
        source_case_id=source.case_id,
        case_family=spec.case_family,
        topology_id=spec.topology_id,
        simulation_scope=spec.simulation_scope,
        decision_role=spec.decision_role,
        axis_id=axis_id,
        density=float(density),
        temperature=float(temperature),
        strength_scale=float(strength),
        composition=composition,
        source_case=source,
    )


def _axis_values(axis: object, source_grid: tuple[float, ...]) -> tuple[float, ...]:
    if axis == "source_grid":
        return tuple(float(value) for value in source_grid)
    return _numeric_axis(axis)


def _numeric_axis(axis: object) -> tuple[float, ...]:
    if isinstance(axis, list | tuple):
        values = tuple(float(value) for value in axis)
        if not values:
            raise ValueError("stress axis values are required.")
        return values
    if isinstance(axis, int | float):
        return (float(axis),)
    raise ValueError("stress axis must be a numeric value, numeric list, or source_grid.")


def _middle(values: tuple[float, ...]) -> float:
    if not values:
        raise ValueError("source grid cannot be empty.")
    return float(values[len(values) // 2])


def _axis_point_text(
    axis_id: str,
    *,
    density: float,
    temperature: float,
    strength: float,
    composition: np.ndarray,
) -> str:
    if axis_id == "density":
        return f"rho{density:.6g}"
    if axis_id == "temperature":
        return f"T{temperature:.6g}"
    if axis_id == "association_strength":
        return f"Delta{strength:.6g}"
    if axis_id == "composition":
        return f"x0{float(composition[0]):.6g}"
    raise ValueError(f"unknown Picard stress axis: {axis_id}")
