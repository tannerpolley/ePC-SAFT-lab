"""Internal builders for native equilibrium request payloads."""

from __future__ import annotations

from typing import Any


_CHEMICAL_POTENTIAL_TOLERANCE_FLOOR = 1.0e-7
_PHASE_DISTANCE_TOLERANCE_FLOOR = 1.0e-4


def neutral_two_phase_eos_tolerances(P: float, options: Any) -> tuple[float, float, float, float]:
    material_tolerance = float(options.tolerance)
    pressure_tolerance = max(abs(float(P)) * material_tolerance, material_tolerance)
    chemical_potential_tolerance = max(material_tolerance, _CHEMICAL_POTENTIAL_TOLERANCE_FLOOR)
    phase_distance_tolerance = max(10.0 * float(options.min_composition), _PHASE_DISTANCE_TOLERANCE_FLOOR)
    return material_tolerance, pressure_tolerance, chemical_potential_tolerance, phase_distance_tolerance
