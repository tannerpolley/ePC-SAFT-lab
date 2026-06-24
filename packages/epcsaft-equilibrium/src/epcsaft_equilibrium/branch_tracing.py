"""Internal boundary-route branch tracing helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

SUPPORTED_BOUNDARY_ROUTES = frozenset({"bubble_pressure", "dew_pressure", "bubble_temperature", "dew_temperature"})
SUPPORTED_FIXED_VARIABLES = frozenset({"T_K", "P_bar"})


@dataclass(frozen=True, slots=True)
class BranchTraceAnchor:
    anchor_id: str
    coordinate: float
    source_role: str = ""
    source_reference: str = ""
    required: bool = True
    expected_value: float | None = None
    uncertainty: float | None = None


@dataclass(frozen=True, slots=True)
class BranchTraceOptions:
    route: str
    component_index: int
    fixed_variable: str
    fixed_value: float
    max_coordinate_gap: float = 0.075
    max_interpolation_error: float = 0.35
    requested_coordinate_tolerance: float = 2.0e-4
    max_refinement_iterations: int = 8
    max_points: int = 240
    require_exact_hessian: bool = True
    require_postsolve: bool = True
    solver_options: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class BranchSolveRequest:
    route: str
    component_index: int
    fixed_variable: str
    fixed_value: float
    coordinate: float
    source_anchor_id: str = ""
    continuation_state: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class BranchTracePoint:
    point_id: str
    route: str
    requested_coordinate: float
    solved_coordinate: float
    paired_coordinate: float
    pressure_bar: float
    temperature_k: float
    continuation_state_used: Mapping[str, Any] | None = None
    continuation_state_returned: Mapping[str, Any] | None = None
    exact_hessian_available: bool = False
    hessian_approximation: str = ""
    postsolve_accepted: bool = False
    route_status: str = ""
    solver_status: str = ""
    residuals: Mapping[str, Any] = field(default_factory=dict)
    source_anchor_id: str = ""
    accepted: bool = False
    rejection_reason: str = ""


@dataclass(frozen=True, slots=True)
class BranchTraceSegment:
    left_point_id: str
    right_point_id: str
    coordinate_gap: float
    value_gap: float
    interpolation_error: float = 0.0
    refinement_reason: str = ""
    accepted: bool = False


@dataclass(frozen=True, slots=True)
class BranchTraceResult:
    route: str
    fixed_variable: str
    fixed_value: float
    points: tuple[BranchTracePoint, ...]
    segments: tuple[BranchTraceSegment, ...]
    required_anchor_count: int
    solved_required_anchor_count: int
    complete: bool
    blockers: tuple[str, ...]

    @property
    def accepted_points(self) -> tuple[BranchTracePoint, ...]:
        return tuple(point for point in self.points if point.accepted)

    @property
    def max_coordinate_gap(self) -> float:
        if not self.segments:
            return 0.0
        return max(segment.coordinate_gap for segment in self.segments)

    @property
    def max_interpolation_error(self) -> float:
        if not self.segments:
            return 0.0
        return max(abs(segment.interpolation_error) for segment in self.segments)


def validate_branch_trace_inputs(options: BranchTraceOptions, anchors: Sequence[BranchTraceAnchor]) -> None:
    if options.route not in SUPPORTED_BOUNDARY_ROUTES:
        raise ValueError(f"unsupported branch trace route: {options.route}")
    if options.component_index < 0:
        raise ValueError("branch trace component_index must be non-negative")
    if options.fixed_variable not in SUPPORTED_FIXED_VARIABLES:
        raise ValueError(f"unsupported branch trace fixed variable: {options.fixed_variable}")
    _require_finite_positive("fixed_value", options.fixed_value)
    _require_finite_positive("max_coordinate_gap", options.max_coordinate_gap)
    _require_finite_positive("max_interpolation_error", options.max_interpolation_error)
    _require_finite_positive("requested_coordinate_tolerance", options.requested_coordinate_tolerance)
    if options.max_refinement_iterations <= 0:
        raise ValueError("max_refinement_iterations must be positive")
    if options.max_points <= 0:
        raise ValueError("max_points must be positive")
    if not anchors:
        raise ValueError("branch trace requires at least one anchor")

    seen_ids: set[str] = set()
    for anchor in anchors:
        anchor_id = str(anchor.anchor_id).strip()
        if not anchor_id:
            raise ValueError("branch trace anchor id must be non-empty")
        if anchor_id in seen_ids:
            raise ValueError(f"duplicate branch trace anchor id: {anchor_id}")
        seen_ids.add(anchor_id)
        if not math.isfinite(float(anchor.coordinate)) or not 0.0 < float(anchor.coordinate) < 1.0:
            raise ValueError(f"branch trace anchor coordinate must be within (0, 1): {anchor_id}")


def _require_finite_positive(name: str, value: float) -> None:
    if not math.isfinite(float(value)) or float(value) <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
