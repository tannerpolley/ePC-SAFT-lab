from __future__ import annotations

from pathlib import Path

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_case_matrix import (
    association_case_by_id,
)
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
    PICARD7_CLOSURE,
    PICARD_DEFAULT_POLICY,
    PICARD_POLICY_GRID,
    PicardPolicy,
    evaluate_closure,
    evaluate_picard_policy,
)
from analyses.package_validation.explicit_association_toybox.scripts.picard_policy_grid import (
    generate_picard_policy_grid,
    run_picard_policy_grid,
)


def test_picard_policy_grid_contains_required_fixed_policies() -> None:
    policies = PICARD_POLICY_GRID

    assert {policy.step_count for policy in policies} == {3, 5, 7, 9, 11}
    assert {policy.damping for policy in policies} == {0.35, 0.5, 0.65, 0.8, 1.0}
    assert len({policy.closure_name for policy in policies}) == len(policies)
    assert PICARD_DEFAULT_POLICY == PicardPolicy(step_count=7, damping=0.5)


def test_picard_default_policy_matches_legacy_closure_name() -> None:
    case = association_case_by_id("pure_2b_self")
    density = case.density_grid[1]
    delta = case.scaled_delta(case.strength_scale)

    legacy = evaluate_closure(
        PICARD7_CLOSURE,
        system=case.system,
        density=density,
        composition=case.composition,
        delta=delta,
    )
    policy = evaluate_picard_policy(
        PICARD_DEFAULT_POLICY,
        system=case.system,
        density=density,
        composition=case.composition,
        delta=delta,
    )

    assert np.array_equal(policy.xa, legacy.xa)
    assert policy.name == PICARD_DEFAULT_POLICY.closure_name
    assert policy.association_closure == PICARD_DEFAULT_POLICY.closure_name


def test_picard_policy_grid_rows_retain_metrics_and_rankings() -> None:
    rows = run_picard_policy_grid(repeat_count=1)

    assert rows
    assert {
        "case_id",
        "topology_id",
        "step_count",
        "damping",
        "policy_name",
        "exact_iteration_count",
        "site_fraction_max_abs_error",
        "mass_action_residual_inf",
        "association_helmholtz_relative_error",
        "pressure_proxy_relative_error",
        "derivative_max_relative_error",
        "hessian_max_relative_error",
        "exact_implicit_elapsed_median_seconds",
        "policy_elapsed_median_seconds",
        "speedup_vs_exact_implicit",
        "evaluation_count_proxy",
        "graph_depth_proxy",
        "pareto_band",
        "candidate_policy_label",
    } <= set(rows[0])
    assert {int(row["step_count"]) for row in rows} == {3, 5, 7, 9, 11}
    assert {float(row["damping"]) for row in rows} == {0.35, 0.5, 0.65, 0.8, 1.0}
    assert "high_accuracy" in {row["candidate_policy_label"] for row in rows}
    assert all(float(row["mass_action_residual_inf"]) >= 0.0 for row in rows)


def test_generate_picard_policy_grid_writes_evidence_and_handoff(tmp_path: Path) -> None:
    output = tmp_path / "picard_policy_grid.csv"
    handoff = tmp_path / "picard_policy_cppad_handoff_matrix.csv"

    generated = generate_picard_policy_grid(output_path=output, handoff_path=handoff, repeat_count=1)

    assert generated == output
    assert output.exists()
    assert handoff.exists()
    output_text = output.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")
    assert "policy_name" in output_text
    assert "pareto_band" in output_text
    assert "expected_derivative_orders" in handoff_text
    assert "failure_modes" in handoff_text
