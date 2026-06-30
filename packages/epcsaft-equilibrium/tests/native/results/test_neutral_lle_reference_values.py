from __future__ import annotations

import os

import numpy as np
import pytest

from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
from equilibrium_support.equilibrium_cases import _nonideal_lle_binary_mixture
from equilibrium_support.route_assertions import assert_neutral_lle_stage_iii_replay_receipt

STAGE9_PHASE_DISCOVERY_STEPS = [
    "deterministic_screening",
    "continuous_tpd_minimization",
    "held_stage_i_stability",
    "held_stage_ii_candidate_bound_audit",
    "held_stage_ii_dual_loop_verification",
    "held_stage_iii_ipopt_refinement",
]
def test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian() -> None:
    _skip_without_ipopt()
    mix = _nonideal_lle_binary_mixture()

    route = _core._native_equilibrium_selector_route_result(
        mix._native,
        {
            "route": "neutral_lle",
            "temperature": 225.0,
            "pressure": 1.0e6,
            "composition": [0.5, 0.5],
            "composition_role": "feed",
        },
        260,
        1.0e-6,
        0.0,
        "auto",
        8,
        1.0e-8,
        1.0e-3,
        1.0e-6,
        1.0e-6,
        {},
        linear_solver="auto",
        print_level=_ipopt_print_level(),
        acceptable_tolerance=1.0e-7,
        constraint_violation_tolerance=1.0e-7,
        dual_infeasibility_tolerance=1.0e-8,
        complementarity_tolerance=1.0e-8,
    )

    assert route["accepted"] is True
    assert route["status"] == "production_accepted"
    assert route["solver_accepted"] is True
    assert route["postsolve_accepted"] is True
    assert route["rejection_reason"] == "accepted"
    assert route["solver_status"] == "success"
    assert route["application_status"] == "solve_succeeded"
    assert route["selector_family"] == "neutral_lle"
    assert route["route"] == "neutral_lle"
    assert route["problem_name"] == "neutral_lle_eos"
    assert route["phase_labels"] == ["liquid1", "liquid2"]
    assert route["phase_roles"] == ["liquid", "liquid"]
    assert route["activation"]["production_exposed"] is True
    assert route["activation_compiler"] == "activation_plan"
    assert route["constraint_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert "phase_volume_gap" not in route["constraint_families"]
    assert route["hessian_approximation"] == "exact"
    assert route["option_profile"] == "held_refinement"
    assert route["exact_hessian_available"] is True
    assert route["scaled_acceptance_passed"] is True
    assert route["constraint_violation_tolerance"] == pytest.approx(1.0e-7)
    assert route["eval_h_calls"] > 0

    postsolve = route["postsolve"]
    assert postsolve["accepted"] is True
    assert postsolve["phase_discovery_backend"] == "continuous_tpd_held_dual_phase_discovery"
    assert postsolve["stability_certificate"] == "tpd_postsolve"
    assert postsolve["stage9_phase_discovery_steps"] == STAGE9_PHASE_DISCOVERY_STEPS
    assert postsolve["deterministic_screening_status"] == "completed"
    assert postsolve["deterministic_screening_is_full_held"] is False
    assert postsolve["continuous_tpd_status"] == "converged"
    assert postsolve["continuous_tpd_backend"] == "continuous_coordinate_search"
    assert postsolve["continuous_tpd_start_count"] > 0
    assert postsolve["continuous_tpd_solve_count"] == postsolve["continuous_tpd_start_count"]
    assert postsolve["continuous_tpd_converged_count"] == postsolve["continuous_tpd_solve_count"]
    assert postsolve["continuous_tpd_iteration_count_total"] >= postsolve["continuous_tpd_solve_count"]
    assert postsolve["continuous_tpd_iteration_count_max"] > 0
    assert postsolve["continuous_tpd_step_final_max"] > 0.0
    assert postsolve["continuous_tpd_best_source"]
    assert len(postsolve["continuous_tpd_best_composition"]) == 2
    assert postsolve["held_stage_i_status"] in {
        "negative_tpd_candidate_found",
        "no_negative_tpd_candidate_found",
    }
    assert postsolve["held_stage_i_start_count"] == postsolve["continuous_tpd_start_count"]
    assert postsolve["held_stage_i_min_tpd"] == pytest.approx(postsolve["continuous_tpd_min"])
    assert postsolve["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert postsolve["held_stage_ii_status"] == "dual_loop_verified"
    assert postsolve["held_stage_ii_dual_loop_status"] == "verified"
    assert postsolve["held_stage_ii_major_iterations"] > 0
    assert postsolve["held_stage_ii_candidate_count"] == postsolve["unique_candidate_count"]
    assert postsolve["held_stage_ii_lower_bound"] <= postsolve["held_stage_ii_upper_bound"]
    assert postsolve["held_stage_ii_bound_gap"] <= 1.0e-6
    assert postsolve["held_stage_ii_bound_tolerance"] > 0.0
    assert postsolve["held_stage_ii_bound_gap"] <= postsolve["held_stage_ii_bound_tolerance"]
    assert postsolve["held_stage_ii_stopping_reason"] == "bound_gap_closed"
    assert len(postsolve["held_stage_ii_lower_bound_history"]) == postsolve["held_stage_ii_major_iterations"]
    assert len(postsolve["held_stage_ii_upper_bound_history"]) == postsolve["held_stage_ii_major_iterations"]
    assert len(postsolve["held_stage_ii_bound_gap_history"]) == postsolve["held_stage_ii_major_iterations"]
    assert postsolve["held_stage_ii_replay_ready"] is True
    assert postsolve["held_stage_ii_replay_source"] == "stage_ii_dual_loop_selected_candidates"
    assert postsolve["held_stage_ii_replay_seed_name"] == "held_stage_ii_dual_loop_candidate_pair"
    assert postsolve["held_stage_ii_replay_candidate_count"] == postsolve["unique_candidate_count"]
    assert postsolve["held_stage_ii_replay_phase_fractions"] == pytest.approx(
        postsolve["selected_phase_fractions"]
    )
    assert postsolve["held_stage_ii_replay_phase_kinds"] == postsolve["selected_phase_kinds"]
    np.testing.assert_allclose(
        np.asarray(postsolve["held_stage_ii_replay_phase_compositions"], dtype=float),
        np.asarray(postsolve["selected_phase_compositions"], dtype=float),
    )
    assert postsolve["held_stage_iii_status"] == "ipopt_refinement_completed_current_route"
    assert postsolve["held_stage_iii_refined_phase_count"] == 2
    assert_neutral_lle_stage_iii_replay_receipt(route)
    assert postsolve["stability_checked"] is True
    assert postsolve["stability_accepted"] is True
    assert postsolve["candidate_completeness_accepted"] is True
    assert postsolve["phase_set_mass_balance_feasible"] is True
    assert postsolve["phase_set_status"] == "phase_set_certified"
    assert postsolve["tpd_candidate_count"] >= postsolve["unique_candidate_count"] >= 1
    assert postsolve["selected_candidate_count"] == 2
    assert len(postsolve["tpd_candidate_ranks"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_sources"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_pressure_residuals"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_iteration_counts"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_step_finals"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_feasibility_statuses"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_selected"]) == postsolve["unique_candidate_count"]
    assert postsolve["seed_and_stability"]["phase_discovery_backend"] == "continuous_tpd_held_dual_phase_discovery"
    assert postsolve["seed_and_stability"]["candidate_source_count"] == postsolve["unique_candidate_count"]
    assert postsolve["seed_and_stability"]["candidate_sources"] == postsolve["tpd_candidate_sources"]
    assert (
        postsolve["seed_and_stability"]["candidate_iteration_counts"]
        == postsolve["tpd_candidate_iteration_counts"]
    )
    assert postsolve["seed_and_stability"]["deterministic_screening_is_full_held"] is False
    assert postsolve["seed_and_stability"]["continuous_tpd_status"] == "converged"
    assert postsolve["seed_and_stability"]["held_stage_i_status"] == postsolve["held_stage_i_status"]
    assert postsolve["seed_and_stability"]["held_stage_ii_status"] == "dual_loop_verified"
    assert (
        postsolve["seed_and_stability"]["held_stage_ii_candidate_bound_audit_status"]
        == "candidate_bound_gap_closed"
    )
    assert postsolve["seed_and_stability"]["held_stage_ii_dual_loop_status"] == "verified"
    assert postsolve["seed_and_stability"]["held_stage_ii_replay_ready"] is True
    assert (
        postsolve["seed_and_stability"]["held_stage_ii_replay_seed_name"]
        == "held_stage_ii_dual_loop_candidate_pair"
    )
    assert (
        postsolve["seed_and_stability"]["held_stage_iii_consumed_stage_ii_replay_metadata"]
        is postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"]
    )
    assert postsolve["candidate_mass_balance_norm"] <= 1.0e-8
    assert postsolve["material_balance_norm"] <= 1.0e-8
    assert postsolve["pressure_consistency_norm"] <= 1.0e-3
    assert postsolve["ln_fugacity_consistency_norm"] <= 1.0e-6
    assert postsolve["phase_distance"] >= 1.0e-6

    evidence = route["physical_evidence"]
    assert evidence["available"] is True
    assert evidence["phase_labels"] == ["liquid1", "liquid2"]
    assert evidence["phase_roles"] == ["liquid", "liquid"]
    assert evidence["material_balance_norm"] == pytest.approx(postsolve["material_balance_norm"])
    assert evidence["pressure_consistency_norm"] == pytest.approx(postsolve["pressure_consistency_norm"])
    assert evidence["ln_fugacity_consistency_norm"] == pytest.approx(postsolve["ln_fugacity_consistency_norm"])
    assert evidence["phase_distance"] == pytest.approx(postsolve["phase_distance"])
    assert evidence["stability_checked"] is True
    assert evidence["deterministic_screening_is_full_held"] is False
    assert evidence["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert evidence["held_stage_ii_status"] == "dual_loop_verified"
    assert evidence["held_stage_ii_dual_loop_status"] == "verified"
    assert evidence["held_stage_ii_replay_ready"] is True
    assert evidence["held_stage_iii_status"] == "ipopt_refinement_completed_current_route"
    assert (
        evidence["held_stage_iii_consumed_stage_ii_replay_metadata"]
        is postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"]
    )
    assert [phase["label"] for phase in evidence["phases"]] == ["liquid1", "liquid2"]
    assert [phase["role"] for phase in evidence["phases"]] == ["liquid", "liquid"]

    compositions = np.asarray(postsolve["phase_compositions"], dtype=float)
    amounts = np.asarray(route["phase_amounts"], dtype=float)
    assert compositions.shape == (2, 2)
    assert amounts.shape == (2, 2)
    assert np.all(amounts > 0.0)
    assert np.max(np.abs(compositions[0] - compositions[1])) == pytest.approx(
        postsolve["phase_distance"],
        rel=1.0e-8,
        abs=1.0e-10,
    )

    certificate = route["stability_certificate"]
    assert certificate["accepted"] is True
    assert certificate["method"] == "tpd_postsolve"
    assert certificate["phase_discovery_backend"] == "continuous_tpd_held_dual_phase_discovery"
    assert certificate["deterministic_screening_is_full_held"] is False
    assert certificate["continuous_tpd_status"] == "converged"
    assert certificate["held_stage_i_status"] == postsolve["held_stage_i_status"]
    assert certificate["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert certificate["held_stage_ii_status"] == "dual_loop_verified"
    assert certificate["held_stage_ii_dual_loop_status"] == "verified"
    assert certificate["held_stage_ii_replay_ready"] is True
    assert certificate["held_stage_iii_status"] == "ipopt_refinement_completed_current_route"
    assert (
        certificate["held_stage_iii_consumed_stage_ii_replay_metadata"]
        is postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"]
    )
    assert certificate["stability_checked"] is True
    assert certificate["stability_accepted"] is True
    assert certificate["candidate_set_complete"] is True
    assert certificate["status"] == "phase_set_certified"
    assert certificate["min_tpd"] == pytest.approx(postsolve["min_tpd"])


def test_neutral_lle_does_not_accept_time_limited_ipopt_postsolve() -> None:
    _skip_without_ipopt()
    mix = _nonideal_lle_binary_mixture()

    route = _core._native_equilibrium_selector_route_result(
        mix._native,
        {
            "route": "neutral_lle",
            "temperature": 225.0,
            "pressure": 1.0e6,
            "composition": [0.5, 0.5],
            "composition_role": "feed",
        },
        1,
        1.0e-6,
        1.0e-6,
        "auto",
        4,
        1.0e-8,
        1.0e-3,
        1.0e-6,
        1.0e-6,
        {},
        linear_solver="auto",
        option_profile="diagnostic",
        print_level=0,
        acceptable_tolerance=1.0e-7,
        constraint_violation_tolerance=1.0e-7,
        dual_infeasibility_tolerance=1.0e-8,
        complementarity_tolerance=1.0e-8,
    )

    assert route["accepted"] is False
    assert route["status"] == "solver_rejected"
    assert route["solver_accepted"] is False
    assert route["postsolve_accepted"] is False
    assert route["rejection_reason"] == "solver_rejected"
    assert route["solver_status"] == "wall_time_exceeded"
    assert route["application_status"] == "maximum_wall_time_exceeded"
    assert route["postsolve"]["accepted"] is False
    assert route["postsolve"]["held_stage_iii_status"] == "pending"
    assert route["phase_amounts"] == []
    assert route["phase_volumes"] == []
    assert route["seed_attempts"]
    assert all(attempt["solver_accepted"] is False for attempt in route["seed_attempts"])


def test_neutral_tpd_phase_discovery_reports_candidate_set_for_lle_binary() -> None:
    mix = _nonideal_lle_binary_mixture()

    discovery = _core._native_neutral_tpd_phase_discovery(
        mix._native,
        225.0,
        1.0e6,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
    )

    assert discovery["phase_discovery_backend"] == "continuous_tpd_held_dual_phase_discovery"
    assert discovery["stability_certificate"] == "tpd_postsolve"
    assert discovery["stage9_phase_discovery_steps"] == STAGE9_PHASE_DISCOVERY_STEPS
    assert discovery["deterministic_screening_status"] == "completed"
    assert discovery["deterministic_screening_is_full_held"] is False
    assert discovery["deterministic_candidate_count"] > 0
    assert discovery["continuous_tpd_status"] == "converged"
    assert discovery["continuous_tpd_backend"] == "continuous_coordinate_search"
    assert discovery["continuous_tpd_start_count"] > 0
    assert discovery["continuous_tpd_solve_count"] == discovery["continuous_tpd_start_count"]
    assert discovery["continuous_tpd_converged_count"] == discovery["continuous_tpd_solve_count"]
    assert discovery["continuous_tpd_iteration_count_total"] >= discovery["continuous_tpd_solve_count"]
    assert discovery["continuous_tpd_iteration_count_max"] > 0
    assert discovery["continuous_tpd_step_final_max"] > 0.0
    assert discovery["continuous_tpd_best_source"]
    assert len(discovery["continuous_tpd_best_composition"]) == 2
    assert discovery["held_stage_i_status"] in {
        "negative_tpd_candidate_found",
        "no_negative_tpd_candidate_found",
    }
    assert discovery["held_stage_i_start_count"] == discovery["continuous_tpd_start_count"]
    assert discovery["held_stage_i_min_tpd"] == pytest.approx(discovery["continuous_tpd_min"])
    assert discovery["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert discovery["held_stage_ii_status"] == "dual_loop_verified"
    assert discovery["held_stage_ii_dual_loop_status"] == "verified"
    assert discovery["held_stage_ii_major_iterations"] > 0
    assert discovery["held_stage_ii_candidate_count"] == discovery["unique_candidate_count"]
    assert discovery["held_stage_ii_lower_bound"] == pytest.approx(discovery["min_tpd"])
    assert discovery["held_stage_ii_lower_bound"] <= discovery["held_stage_ii_upper_bound"]
    assert discovery["held_stage_ii_bound_gap"] == pytest.approx(
        discovery["held_stage_ii_upper_bound"] - discovery["held_stage_ii_lower_bound"]
    )
    assert discovery["held_stage_ii_bound_gap"] <= 1.0e-6
    assert discovery["held_stage_ii_replay_ready"] is True
    assert discovery["held_stage_ii_replay_seed_name"] == "held_stage_ii_dual_loop_candidate_pair"
    assert discovery["held_stage_iii_status"] == "pending_ipopt_refinement"
    assert discovery["held_stage_iii_refined_phase_count"] == 0
    assert discovery["stability_checked"] is True
    assert discovery["tpd_candidate_count"] >= discovery["unique_candidate_count"] >= 1
    assert discovery["phase_set_mass_balance_feasible"] is True
    assert discovery["candidate_completeness_accepted"] is True
    assert discovery["candidate_mass_balance_norm"] <= 1.0e-6
    assert discovery["selected_candidate_count"] == 2
    assert len(discovery["selected_phase_compositions"]) == 2
    assert len(discovery["candidates"]) == discovery["unique_candidate_count"]
    assert [candidate["candidate_rank"] for candidate in discovery["candidates"]] == list(
        range(discovery["unique_candidate_count"])
    )
    assert sum(candidate["selected"] for candidate in discovery["candidates"]) == discovery["selected_candidate_count"]
    selected_tpds = [candidate["tpd"] for candidate in discovery["candidates"] if candidate["selected"]]
    assert min(selected_tpds) == pytest.approx(discovery["min_tpd"])
    for candidate in discovery["candidates"]:
        assert candidate["source"].startswith("feed_phase_kind_")
        assert candidate["tpd_backend"] in {
            "deterministic_grid_evaluation",
            "continuous_coordinate_search",
        }
        if candidate["tpd_backend"] == "continuous_coordinate_search":
            assert candidate["tpd_status"] == "converged"
            assert candidate["start_source"].startswith("feed_phase_kind_")
            assert candidate["tpd_iteration_count"] >= 0
        assert candidate["feasibility_status"] in {
            "selected_mass_balance_feasible",
            "mass_balance_pair_unselected",
            "candidate_mass_balance_incomplete",
        }
        assert np.isfinite(candidate["pressure_residual_estimate"])
        assert abs(candidate["pressure_residual_estimate"]) <= 1.0e-5


def test_neutral_tpd_phase_discovery_can_run_deterministic_screening_without_continuous_tpd() -> None:
    mix = _nonideal_lle_binary_mixture()

    discovery = _core._native_neutral_tpd_phase_discovery(
        mix._native,
        225.0,
        1.0e6,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
        continuous_tpd_required=False,
    )

    assert discovery["deterministic_screening_status"] == "completed"
    assert discovery["deterministic_screening_is_full_held"] is False
    assert discovery["deterministic_candidate_count"] > 0
    assert discovery["continuous_tpd_status"] == "not_requested"
    assert discovery["continuous_tpd_start_count"] == 0
    assert discovery["continuous_tpd_solve_count"] == 0
    assert discovery["continuous_tpd_converged_count"] == 0
    assert discovery["continuous_tpd_iteration_count_total"] == 0
    assert discovery["continuous_tpd_iteration_count_max"] == 0
    assert discovery["continuous_tpd_step_final_max"] == 0.0
    assert discovery["held_stage_i_status"] == "not_requested"
    assert discovery["held_stage_ii_status"] == "not_requested"
    assert discovery["held_stage_ii_major_iterations"] == 0
    assert {candidate["tpd_backend"] for candidate in discovery["candidates"]} == {
        "deterministic_grid_evaluation",
    }
    assert all(candidate["tpd_iteration_count"] == 0 for candidate in discovery["candidates"])


def test_stage9_phase_discovery_ladder_reports_distinct_layers() -> None:
    mix = _nonideal_lle_binary_mixture()
    from scripts.validation import equilibrium_validation_runtime as runtime

    runtime_case = runtime.neutral_lle_synthetic_case()
    assert runtime_case["route"] == "neutral_lle"
    assert runtime_case["temperature"] == pytest.approx(225.0)
    assert runtime_case["pressure"] == pytest.approx(1.0e6)
    assert runtime_case["composition"] == pytest.approx([0.5, 0.5])
    assert runtime_case["evidence_scope"] == "synthetic_neutral_lle_algorithm"

    discovery = _core._native_neutral_tpd_phase_discovery(
        mix._native,
        225.0,
        1.0e6,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
    )

    assert discovery["stage9_phase_discovery_steps"] == STAGE9_PHASE_DISCOVERY_STEPS
    assert discovery["deterministic_screening_status"] == "completed"
    assert discovery["deterministic_screening_is_full_held"] is False
    assert discovery["continuous_tpd_status"] == "converged"
    assert discovery["continuous_tpd_solve_count"] == discovery["continuous_tpd_converged_count"]
    assert discovery["held_stage_i_status"] in {
        "negative_tpd_candidate_found",
        "no_negative_tpd_candidate_found",
    }
    assert discovery["held_stage_i_status"] != discovery["continuous_tpd_status"]
    assert discovery["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert discovery["held_stage_ii_status"] == "dual_loop_verified"
    assert discovery["held_stage_ii_dual_loop_status"] == "verified"
    assert discovery["held_stage_ii_status"] != discovery["held_stage_i_status"]
    assert discovery["held_stage_ii_major_iterations"] > 0
    assert discovery["held_stage_ii_bound_gap"] <= 1.0e-6
    assert discovery["held_stage_iii_status"] == "pending_ipopt_refinement"
    assert discovery["held_stage_iii_status"] != discovery["held_stage_ii_status"]

    candidate_backends = {candidate["tpd_backend"] for candidate in discovery["candidates"]}
    assert candidate_backends == {
        "deterministic_grid_evaluation",
        "continuous_coordinate_search",
    }
    assert discovery["deterministic_candidate_count"] > discovery["continuous_tpd_solve_count"]
    for candidate in discovery["candidates"]:
        if candidate["tpd_backend"] == "deterministic_grid_evaluation":
            assert candidate["tpd_status"] == "candidate_generated"
            assert candidate["tpd_iteration_count"] == 0
            continue

        assert candidate["tpd_backend"] == "continuous_coordinate_search"
        assert candidate["tpd_status"] == "converged"
        assert candidate["start_source"].startswith("feed_phase_kind_")
        assert candidate["tpd_iteration_count"] > 0


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def _ipopt_print_level() -> int:
    enabled = os.environ.get("EPCSAFT_EQUILIBRIUM_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    return 5 if enabled else 0
