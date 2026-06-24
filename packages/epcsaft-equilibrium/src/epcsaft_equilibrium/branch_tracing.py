"""Internal boundary-route branch tracing helpers."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
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


def trace_boundary_route(
    *,
    anchors: Sequence[BranchTraceAnchor],
    options: BranchTraceOptions,
    solve_point: Callable[[BranchSolveRequest], BranchTracePoint],
) -> BranchTraceResult:
    validate_branch_trace_inputs(options, anchors)

    blockers: set[str] = set()
    points: list[BranchTracePoint] = []
    anchor_order = sorted(anchors, key=lambda anchor: (not anchor.required, float(anchor.coordinate)))

    for anchor in anchor_order:
        point = _solve_trace_point(
            solve_point,
            BranchSolveRequest(
                route=options.route,
                component_index=options.component_index,
                fixed_variable=options.fixed_variable,
                fixed_value=options.fixed_value,
                coordinate=float(anchor.coordinate),
                source_anchor_id=str(anchor.anchor_id),
            ),
            options,
            blockers,
        )
        points.append(point)

    for _iteration in range(options.max_refinement_iterations):
        accepted = _accepted_sorted_points(points)
        segments = _segments_from_points(accepted, options)
        invalid = [segment for segment in segments if not segment.accepted]
        if not invalid:
            return _result_from_points(options, anchors, points, segments, blockers)
        if len(accepted) + len(invalid) > options.max_points:
            blockers.add("max_points_exhausted")
            break

        added = False
        for segment in invalid:
            if len(_accepted_sorted_points(points)) >= options.max_points:
                blockers.add("max_points_exhausted")
                break
            left = _point_by_id(points, segment.left_point_id)
            right = _point_by_id(points, segment.right_point_id)
            if left is None or right is None:
                blockers.add("segment_endpoint_missing")
                continue
            midpoint = (left.solved_coordinate + right.solved_coordinate) / 2.0
            continuation_state = left.continuation_state_returned or right.continuation_state_returned
            point = _solve_trace_point(
                solve_point,
                BranchSolveRequest(
                    route=options.route,
                    component_index=options.component_index,
                    fixed_variable=options.fixed_variable,
                    fixed_value=options.fixed_value,
                    coordinate=midpoint,
                    continuation_state=continuation_state,
                ),
                options,
                blockers,
            )
            points.append(point)
            added = True
        if not added:
            break

    accepted = _accepted_sorted_points(points)
    segments = _segments_from_points(accepted, options)
    if any(not segment.accepted for segment in segments):
        blockers.add("max_refinement_iterations_exhausted")
    return _result_from_points(options, anchors, points, segments, blockers)


def _solve_trace_point(
    solve_point: Callable[[BranchSolveRequest], BranchTracePoint],
    request: BranchSolveRequest,
    options: BranchTraceOptions,
    blockers: set[str],
) -> BranchTracePoint:
    try:
        point = solve_point(request)
    except Exception as exc:
        blockers.add("point_solve_failed")
        return BranchTracePoint(
            point_id=f"{request.route}:{request.coordinate:.12g}:rejected",
            route=request.route,
            requested_coordinate=request.coordinate,
            solved_coordinate=request.coordinate,
            paired_coordinate=math.nan,
            pressure_bar=math.nan,
            temperature_k=request.fixed_value if request.fixed_variable == "T_K" else math.nan,
            continuation_state_used=request.continuation_state,
            source_anchor_id=request.source_anchor_id,
            accepted=False,
            rejection_reason=f"point_solve_failed: {exc}",
        )

    rejection_reason = _point_rejection_reason(point, options)
    if rejection_reason:
        blockers.add(rejection_reason)
        return replace(point, accepted=False, rejection_reason=rejection_reason)
    return replace(point, accepted=True, rejection_reason="")


def _point_rejection_reason(point: BranchTracePoint, options: BranchTraceOptions) -> str:
    if abs(point.solved_coordinate - point.requested_coordinate) > options.requested_coordinate_tolerance:
        return "coordinate_drift_exceeds_tolerance"
    if options.require_exact_hessian:
        if point.exact_hessian_available is not True or point.hessian_approximation != "exact":
            return "exact_hessian_missing"
    if options.require_postsolve and point.postsolve_accepted is not True:
        return "postsolve_missing"
    return ""


def _accepted_sorted_points(points: Sequence[BranchTracePoint]) -> list[BranchTracePoint]:
    accepted = [point for point in points if point.accepted]
    accepted.sort(key=lambda point: point.solved_coordinate)
    deduped: list[BranchTracePoint] = []
    for point in accepted:
        if deduped and abs(point.solved_coordinate - deduped[-1].solved_coordinate) <= 1.0e-12:
            continue
        deduped.append(point)
    return deduped


def _segments_from_points(points: Sequence[BranchTracePoint], options: BranchTraceOptions) -> tuple[BranchTraceSegment, ...]:
    if len(points) < 2:
        return ()

    segments: list[BranchTraceSegment] = []
    for left, right in zip(points[:-1], points[1:]):
        coordinate_gap = right.solved_coordinate - left.solved_coordinate
        value_gap = _trace_value(right, options) - _trace_value(left, options)
        accepted = coordinate_gap <= options.max_coordinate_gap
        reason = "" if accepted else "coordinate_gap_exceeds_threshold"
        segments.append(
            BranchTraceSegment(
                left_point_id=left.point_id,
                right_point_id=right.point_id,
                coordinate_gap=coordinate_gap,
                value_gap=abs(value_gap),
                interpolation_error=0.0,
                refinement_reason=reason,
                accepted=accepted,
            )
        )
    return tuple(segments)


def _trace_value(point: BranchTracePoint, options: BranchTraceOptions) -> float:
    if options.fixed_variable == "T_K":
        return point.pressure_bar
    return point.temperature_k


def _point_by_id(points: Sequence[BranchTracePoint], point_id: str) -> BranchTracePoint | None:
    for point in points:
        if point.point_id == point_id:
            return point
    return None


def _result_from_points(
    options: BranchTraceOptions,
    anchors: Sequence[BranchTraceAnchor],
    points: Sequence[BranchTracePoint],
    segments: Sequence[BranchTraceSegment],
    blockers: set[str],
) -> BranchTraceResult:
    required_anchor_ids = {str(anchor.anchor_id) for anchor in anchors if anchor.required}
    solved_required_anchor_ids = {
        str(point.source_anchor_id) for point in points if point.accepted and str(point.source_anchor_id) in required_anchor_ids
    }
    if solved_required_anchor_ids != required_anchor_ids:
        blockers.add("required_anchor_incomplete")
    if any(not segment.accepted for segment in segments):
        blockers.add("segment_incomplete")
    complete = not blockers
    return BranchTraceResult(
        route=options.route,
        fixed_variable=options.fixed_variable,
        fixed_value=options.fixed_value,
        points=tuple(points),
        segments=tuple(segments),
        required_anchor_count=len(required_anchor_ids),
        solved_required_anchor_count=len(solved_required_anchor_ids),
        complete=complete,
        blockers=tuple(sorted(blockers)),
    )
