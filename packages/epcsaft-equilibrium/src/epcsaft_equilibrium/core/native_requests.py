"""Internal builders for native equilibrium request payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


_CHEMICAL_POTENTIAL_TOLERANCE_FLOOR = 1.0e-7
_PHASE_DISTANCE_TOLERANCE_FLOOR = 1.0e-4


@dataclass(frozen=True, slots=True)
class NativeSelectorRouteSpec:
    selector_route: str
    composition_key: str
    composition_role: str
    requires_temperature: bool
    requires_pressure: bool
    knowns: tuple[str, ...]
    unknowns: tuple[str, ...]
    problem_kind: str
    route_label: str
    selector_family: str
    phase_labels: tuple[str, ...] = ("liquid", "vapor")


EQUILIBRIUM_ROUTE_SPECS: dict[str, NativeSelectorRouteSpec] = {
    "bubble_pressure": NativeSelectorRouteSpec(
        selector_route="bubble_pressure",
        composition_key="x",
        composition_role="liquid",
        requires_temperature=True,
        requires_pressure=False,
        knowns=("T", "x"),
        unknowns=("P", "y", "phase_volumes"),
        problem_kind="neutral_bubble_p",
        route_label="bubble_pressure",
        selector_family="bubble_dew_derived_routes",
    ),
    "bubble_temperature": NativeSelectorRouteSpec(
        selector_route="bubble_temperature",
        composition_key="x",
        composition_role="liquid",
        requires_temperature=False,
        requires_pressure=True,
        knowns=("P", "x"),
        unknowns=("T", "y", "phase_volumes"),
        problem_kind="neutral_bubble_t",
        route_label="bubble_temperature",
        selector_family="bubble_dew_derived_routes",
    ),
    "dew_pressure": NativeSelectorRouteSpec(
        selector_route="dew_pressure",
        composition_key="y",
        composition_role="vapor",
        requires_temperature=True,
        requires_pressure=False,
        knowns=("T", "y"),
        unknowns=("P", "x", "phase_volumes"),
        problem_kind="neutral_dew_p",
        route_label="dew_pressure",
        selector_family="bubble_dew_derived_routes",
    ),
    "dew_temperature": NativeSelectorRouteSpec(
        selector_route="dew_temperature",
        composition_key="y",
        composition_role="vapor",
        requires_temperature=False,
        requires_pressure=True,
        knowns=("P", "y"),
        unknowns=("T", "x", "phase_volumes"),
        problem_kind="neutral_dew_t",
        route_label="dew_temperature",
        selector_family="bubble_dew_derived_routes",
    ),
    "flash": NativeSelectorRouteSpec(
        selector_route="neutral_tp_flash",
        composition_key="z",
        composition_role="feed",
        requires_temperature=True,
        requires_pressure=True,
        knowns=("T", "P", "z"),
        unknowns=("x", "y", "phase_amounts", "phase_volumes"),
        problem_kind="neutral_tp_flash",
        route_label="flash",
        selector_family="neutral_tp_flash",
    ),
    "lle": NativeSelectorRouteSpec(
        selector_route="neutral_lle",
        composition_key="z",
        composition_role="feed",
        requires_temperature=True,
        requires_pressure=True,
        knowns=("T", "P", "z"),
        unknowns=("liquid1", "liquid2", "phase_amounts", "phase_volumes"),
        problem_kind="neutral_lle",
        route_label="lle",
        selector_family="neutral_lle",
        phase_labels=("liquid1", "liquid2"),
    ),
}


def selector_request_payload(
    *,
    route: str,
    composition: np.ndarray,
    composition_role: str,
    temperature: float | None = None,
    pressure: float | None = None,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "route": route,
        "composition": composition.tolist(),
        "composition_role": composition_role,
    }
    if temperature is not None:
        request["temperature"] = float(temperature)
    if pressure is not None:
        request["pressure"] = float(pressure)
    return request


def selector_route_solver_tolerances(options: Any) -> tuple[float, float, float, float]:
    material_tolerance = float(options.tolerance)
    return (
        material_tolerance,
        max(1.0e5 * material_tolerance, material_tolerance),
        material_tolerance,
        max(10.0 * float(options.min_composition), 1.0e-8),
    )


def neutral_two_phase_eos_tolerances(P: float, options: Any) -> tuple[float, float, float, float]:
    material_tolerance = float(options.tolerance)
    pressure_tolerance = max(abs(float(P)) * material_tolerance, material_tolerance)
    chemical_potential_tolerance = max(material_tolerance, _CHEMICAL_POTENTIAL_TOLERANCE_FLOOR)
    phase_distance_tolerance = max(10.0 * float(options.min_composition), _PHASE_DISTANCE_TOLERANCE_FLOOR)
    return material_tolerance, pressure_tolerance, chemical_potential_tolerance, phase_distance_tolerance
