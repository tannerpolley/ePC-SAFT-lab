from __future__ import annotations

import pytest

from epcsaft_equilibrium.branch_tracing import (
    BranchSolveRequest,
    BranchTraceAnchor,
    BranchTraceOptions,
    BranchTracePoint,
    trace_boundary_route,
    validate_branch_trace_inputs,
)


def test_branch_trace_options_validate_supported_route_and_anchor_ids() -> None:
    anchors = [
        BranchTraceAnchor(anchor_id="low", coordinate=0.05, source_role="bubble_line", required=True),
        BranchTraceAnchor(anchor_id="high", coordinate=0.25, source_role="bubble_line", required=True),
    ]
    options = BranchTraceOptions(route="bubble_pressure", component_index=1, fixed_variable="T_K", fixed_value=373.15)

    validate_branch_trace_inputs(options, anchors)


def test_branch_trace_options_reject_duplicate_anchor_ids() -> None:
    anchors = [
        BranchTraceAnchor(anchor_id="same", coordinate=0.05, required=True),
        BranchTraceAnchor(anchor_id="same", coordinate=0.25, required=True),
    ]
    options = BranchTraceOptions(route="bubble_pressure", component_index=1, fixed_variable="T_K", fixed_value=373.15)

    with pytest.raises(ValueError, match="duplicate branch trace anchor id"):
        validate_branch_trace_inputs(options, anchors)


def test_branch_trace_options_reject_unsupported_route() -> None:
    anchors = [BranchTraceAnchor(anchor_id="a", coordinate=0.5, required=True)]
    options = BranchTraceOptions(route="flash", component_index=1, fixed_variable="T_K", fixed_value=373.15)

    with pytest.raises(ValueError, match="unsupported branch trace route"):
        validate_branch_trace_inputs(options, anchors)


def _fake_point(
    request: BranchSolveRequest,
    *,
    pressure_bar: float,
    solved_coordinate: float | None = None,
    exact_hessian_available: bool = True,
    hessian_approximation: str = "exact",
    postsolve_accepted: bool = True,
) -> BranchTracePoint:
    coordinate = request.coordinate if solved_coordinate is None else solved_coordinate
    return BranchTracePoint(
        point_id=f"{request.route}:{coordinate:.6f}",
        route=request.route,
        requested_coordinate=request.coordinate,
        solved_coordinate=coordinate,
        paired_coordinate=min(0.999, coordinate + 0.1),
        pressure_bar=pressure_bar,
        temperature_k=request.fixed_value if request.fixed_variable == "T_K" else 373.15,
        continuation_state_used=request.continuation_state,
        continuation_state_returned={"variables": [coordinate, pressure_bar]},
        exact_hessian_available=exact_hessian_available,
        hessian_approximation=hessian_approximation,
        postsolve_accepted=postsolve_accepted,
        route_status="accepted",
        solver_status="Solve_Succeeded",
        residuals={},
        source_anchor_id=request.source_anchor_id,
        accepted=True,
        rejection_reason="",
    )


def test_trace_refines_until_coordinate_gap_is_bounded() -> None:
    calls: list[float] = []

    def solver(request: BranchSolveRequest) -> BranchTracePoint:
        calls.append(request.coordinate)
        return _fake_point(request, pressure_bar=10.0 + request.coordinate)

    result = trace_boundary_route(
        anchors=[
            BranchTraceAnchor(anchor_id="left", coordinate=0.001, required=True),
            BranchTraceAnchor(anchor_id="right", coordinate=0.30, required=True),
        ],
        options=BranchTraceOptions(
            route="bubble_pressure",
            component_index=1,
            fixed_variable="T_K",
            fixed_value=373.15,
            max_coordinate_gap=0.075,
            max_interpolation_error=0.35,
            max_refinement_iterations=8,
            max_points=240,
        ),
        solve_point=solver,
    )

    assert result.complete is True
    assert result.max_coordinate_gap <= 0.075
    assert len(calls) > 2


def test_trace_rejects_coordinate_drift_beyond_tolerance() -> None:
    def solver(request: BranchSolveRequest) -> BranchTracePoint:
        return _fake_point(request, pressure_bar=10.0, solved_coordinate=request.coordinate + 0.01)

    result = trace_boundary_route(
        anchors=[BranchTraceAnchor(anchor_id="a", coordinate=0.25, required=True)],
        options=BranchTraceOptions(
            route="bubble_pressure",
            component_index=1,
            fixed_variable="T_K",
            fixed_value=373.15,
            requested_coordinate_tolerance=2.0e-4,
        ),
        solve_point=solver,
    )

    assert result.complete is False
    assert "coordinate_drift_exceeds_tolerance" in result.blockers


def test_trace_carries_continuation_state_to_refinement_point() -> None:
    refinement_states: list[object] = []

    def solver(request: BranchSolveRequest) -> BranchTracePoint:
        if not request.source_anchor_id:
            refinement_states.append(request.continuation_state)
        return _fake_point(request, pressure_bar=12.0 + request.coordinate)

    result = trace_boundary_route(
        anchors=[
            BranchTraceAnchor(anchor_id="left", coordinate=0.10, required=True),
            BranchTraceAnchor(anchor_id="right", coordinate=0.30, required=True),
        ],
        options=BranchTraceOptions(
            route="bubble_pressure",
            component_index=1,
            fixed_variable="T_K",
            fixed_value=373.15,
            max_coordinate_gap=0.05,
            max_interpolation_error=0.35,
        ),
        solve_point=solver,
    )

    assert result.complete is True
    assert refinement_states
    assert refinement_states[0] == {"variables": [0.1, 12.1]}
