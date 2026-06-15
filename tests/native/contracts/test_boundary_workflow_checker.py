from __future__ import annotations

from typing import Any

from scripts.validation import check_boundary_workflows as checker


def _trace(**overrides: Any) -> dict[str, Any]:
    trace = {
        "schema_version": 1,
        "route": "bubble_pressure",
        "workflow_label": "Bubble point",
        "workflow_kind": "derived_boundary",
        "diagram_target": "P-x",
        "known_variables": ["T", "x"],
        "free_variables": ["P", "y", "phase_volumes"],
        "solved_boundary_variable": "P",
        "fixed_composition_role": "liquid",
        "phase_roles": ["liquid", "vapor"],
        "source_fixture": "data/reference/equilibrium_benchmarks/neutral_tp_flash/hydrocarbon_workbook_flash",
        "selector_family": "bubble_dew_derived_routes",
        "problem_name": "neutral_bubble_p_eos",
        "variable_model": "phase_species_amounts_plus_phase_volume",
        "density_backend": "explicit_phase_volume_pressure_constraint",
        "residual_families": [
            "material_balance",
            "phase_pressure_consistency",
            "phase_equilibrium",
            "phase_distance",
        ],
        "constraint_families": ["material_balance", "phase_pressure_consistency"],
        "strict_convergence": True,
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "seed_attempts": [],
        "iteration_limit_seed_attempts": [],
        "residuals": {
            "material_balance_norm": 1.0e-10,
            "pressure_consistency_norm": 1.0e-5,
            "ln_fugacity_consistency_norm": 1.0e-8,
            "phase_equilibrium_norm": 1.0e-8,
            "scaled_constraint_violation_inf_norm": 1.0e-8,
        },
    }
    trace.update(overrides)
    return trace


def _point(**overrides: Any) -> dict[str, Any]:
    point = {
        "route": "bubble_pressure",
        "sample_index": 0,
        "status": "accepted",
        "fixed_composition_role": "liquid",
        "boundary_variable": "P",
        "solved_boundary_value": 1.276e6,
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "strict_convergence": True,
        "iteration_limit_seed_attempts": [],
        "boundary_trace": _trace(),
    }
    point.update(overrides)
    return point


def _payload(point: dict[str, Any]) -> dict[str, Any]:
    return {
        "boundary_status": "complete_route_convergence",
        "complete": True,
        "workflows": [
            {
                "label": "Bubble point",
                "workflow_kind": "derived_boundary",
                "route_points": [point],
            }
        ],
    }


def test_boundary_trace_checker_accepts_complete_route_point_trace() -> None:
    result = checker.evaluate_boundary_payload(_payload(_point()))

    assert result["complete"] is True
    assert result["blockers"] == []
    assert result["trace_summary"] == {"total": 1, "accepted": 1, "failed": 0}


def test_boundary_trace_checker_rejects_missing_trace() -> None:
    point = _point()
    point.pop("boundary_trace")

    result = checker.evaluate_boundary_payload(_payload(point))

    assert result["complete"] is False
    assert "missing_boundary_trace:bubble_pressure:0" in result["blockers"]


def test_boundary_trace_checker_rejects_dof_mapping_mismatch() -> None:
    point = _point(boundary_trace=_trace(known_variables=["P", "x"]))

    result = checker.evaluate_boundary_payload(_payload(point))

    assert result["complete"] is False
    assert "boundary_trace_known_variables_mismatch:bubble_pressure" in result["blockers"]


def test_boundary_trace_checker_rejects_missing_residual_evidence() -> None:
    trace = _trace()
    trace["residuals"]["pressure_consistency_norm"] = None

    result = checker.evaluate_boundary_payload(_payload(_point(boundary_trace=trace)))

    assert result["complete"] is False
    assert "boundary_trace_missing_residual:bubble_pressure:pressure_consistency_norm" in result["blockers"]


def test_boundary_trace_checker_rejects_iteration_limit_seed_attempt() -> None:
    trace = _trace(iteration_limit_seed_attempts=["wilson_seed"])

    result = checker.evaluate_boundary_payload(
        _payload(_point(boundary_trace=trace, iteration_limit_seed_attempts=["wilson_seed"]))
    )

    assert result["complete"] is False
    assert "boundary_trace_iteration_limit_seed_attempt:bubble_pressure" in result["blockers"]


def test_boundary_trace_checker_rejects_nonfinite_solved_boundary_value() -> None:
    result = checker.evaluate_boundary_payload(_payload(_point(solved_boundary_value=float("inf"))))

    assert result["complete"] is False
    assert "boundary_trace_nonfinite_solved_boundary_value:bubble_pressure" in result["blockers"]
