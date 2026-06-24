from __future__ import annotations

import pytest

from epcsaft_equilibrium.branch_tracing import (
    BranchSolveRequest,
    BranchTraceAnchor,
    BranchTraceOptions,
    BranchTracePoint,
    solve_equilibrium_boundary_point,
    trace_boundary_route,
    trace_equilibrium_boundary_route,
    validate_branch_trace_inputs,
)
from epcsaft_equilibrium import branch_tracing as branch_tracing_module


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


def test_trace_carries_continuation_state_between_required_anchors() -> None:
    anchor_states: list[object] = []

    def solver(request: BranchSolveRequest) -> BranchTracePoint:
        anchor_states.append(request.continuation_state)
        return _fake_point(request, pressure_bar=12.0 + request.coordinate)

    result = trace_boundary_route(
        anchors=[
            BranchTraceAnchor(anchor_id="left", coordinate=0.10, required=True),
            BranchTraceAnchor(anchor_id="right", coordinate=0.12, required=True),
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
    assert anchor_states == [None, {"variables": [0.1, 12.1]}]


def test_equilibrium_point_adapter_maps_bubble_route_and_continuation_state(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeResult:
        route = "bubble_pressure"
        x = [0.75, 0.25]
        y = [0.65, 0.35]
        pressure = 1.23e6
        temperature = 373.15
        problem_kind = "derived_bubble_pressure"
        diagnostics = {
            "exact_hessian_available": True,
            "hessian_approximation": "exact",
            "postsolve_accepted": True,
            "route_status": "accepted",
            "solver_status": "Solve_Succeeded",
            "iteration_count": 7,
            "pressure_consistency_norm": 1.0e-9,
            "chemical_potential_consistency_norm": 2.0e-9,
            "continuation_state": {"variables": [0.25, 12.3]},
        }

    class FakeEquilibrium:
        def __init__(self, mixture: object, **kwargs: object) -> None:
            calls.append({"mixture": mixture, "kwargs": kwargs})

        def solve(self, *, solver_options: object = None) -> FakeResult:
            calls[-1]["solver_options"] = solver_options
            return FakeResult()

    monkeypatch.setattr(branch_tracing_module, "Equilibrium", FakeEquilibrium)
    mixture = object()

    point = solve_equilibrium_boundary_point(
        BranchSolveRequest(
            route="bubble_pressure",
            component_index=1,
            fixed_variable="T_K",
            fixed_value=373.15,
            coordinate=0.25,
            continuation_state={"variables": [0.20, 11.0]},
            source_anchor_id="source-a",
        ),
        mixture=mixture,
        solver_options={"max_iterations": 25},
    )

    assert calls[0]["kwargs"] == {"route": "bubble_pressure", "T": 373.15, "x": [0.75, 0.25]}
    assert calls[0]["solver_options"] == {"max_iterations": 25, "continuation_state": {"variables": [0.20, 11.0]}}
    assert point.solved_coordinate == 0.25
    assert point.paired_coordinate == 0.35
    assert point.pressure_bar == pytest.approx(12.3)
    assert point.continuation_state_returned == {"variables": [0.25, 12.3]}


def test_equilibrium_point_adapter_maps_dew_route(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeResult:
        route = "dew_pressure"
        x = [0.60, 0.40]
        y = [0.72, 0.28]
        pressure = 1.1e6
        temperature = 373.15
        problem_kind = "derived_dew_pressure"
        diagnostics = {
            "exact_hessian_available": True,
            "hessian_approximation": "exact",
            "postsolve_accepted": True,
            "route_status": "accepted",
            "solver_status": "Solve_Succeeded",
        }

    class FakeEquilibrium:
        def __init__(self, mixture: object, **kwargs: object) -> None:
            calls.append({"mixture": mixture, "kwargs": kwargs})

        def solve(self, *, solver_options: object = None) -> FakeResult:
            calls[-1]["solver_options"] = solver_options
            return FakeResult()

    monkeypatch.setattr(branch_tracing_module, "Equilibrium", FakeEquilibrium)

    point = solve_equilibrium_boundary_point(
        BranchSolveRequest(
            route="dew_pressure",
            component_index=1,
            fixed_variable="T_K",
            fixed_value=373.15,
            coordinate=0.28,
        ),
        mixture=object(),
    )

    assert calls[0]["kwargs"] == {"route": "dew_pressure", "T": 373.15, "y": [0.72, 0.28]}
    assert point.solved_coordinate == 0.28
    assert point.paired_coordinate == 0.40


def test_equilibrium_branch_trace_wrapper_uses_default_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_solve(request: BranchSolveRequest, *, mixture: object, solver_options: object = None) -> BranchTracePoint:
        assert solver_options == {"max_iterations": 5}
        return _fake_point(request, pressure_bar=10.0 + request.coordinate)

    monkeypatch.setattr(branch_tracing_module, "solve_equilibrium_boundary_point", fake_solve)

    result = trace_equilibrium_boundary_route(
        object(),
        anchors=[BranchTraceAnchor(anchor_id="a", coordinate=0.10), BranchTraceAnchor(anchor_id="b", coordinate=0.12)],
        options=BranchTraceOptions(
            route="bubble_pressure",
            component_index=1,
            fixed_variable="T_K",
            fixed_value=373.15,
            solver_options={"max_iterations": 5},
        ),
    )

    assert result.complete is True
