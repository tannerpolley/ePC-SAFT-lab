from __future__ import annotations

import numpy as np
import pytest
from epcsaft_equilibrium._native import extension_native_core
from equilibrium_support.equilibrium_cases import _nonideal_lle_binary_mixture

_core = extension_native_core()

STAGE9_PHASE_DISCOVERY_STEPS = [
    "deterministic_screening",
    "continuous_tpd_minimization",
    "held_stage_i_stability",
    "held_stage_ii_candidate_bound_audit",
    "sampled_candidate_bound_audit",
    "held_stage_iii_ipopt_refinement",
]


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

    assert discovery["phase_discovery_backend"] == "continuous_tpd_sampled_candidate_audit"
    assert discovery["stage9_phase_discovery_steps"] == STAGE9_PHASE_DISCOVERY_STEPS
    assert discovery["deterministic_screening_status"] == "completed"
    assert discovery["deterministic_screening_is_full_held"] is False
    assert discovery["continuous_tpd_status"] == "converged"
    assert discovery["continuous_tpd_backend"] == "continuous_coordinate_search"
    assert discovery["continuous_tpd_start_count"] > 0
    assert discovery["continuous_tpd_solve_count"] == discovery["continuous_tpd_start_count"]
    assert discovery["continuous_tpd_converged_count"] == discovery["continuous_tpd_solve_count"]
    assert discovery["held_stage_i_status"] in {
        "negative_tpd_candidate_found",
        "no_negative_tpd_candidate_found",
    }
    assert discovery["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert discovery["held_stage_ii_status"] == "sampled_candidate_audit_complete"
    assert discovery["held_stage_ii_dual_loop_status"] == "not_performed"
    assert discovery["held_stage_ii_stopping_reason"] == "sampled_candidate_bound_gap_closed"
    assert discovery["held_stage_ii_major_iterations"] == 1
    assert discovery["held_stage_ii_candidate_count"] == discovery["unique_candidate_count"]
    assert discovery["held_stage_ii_lower_bound"] == pytest.approx(discovery["min_tpd"])
    assert discovery["held_stage_ii_lower_bound"] <= discovery["held_stage_ii_upper_bound"]
    assert discovery["held_stage_ii_bound_gap"] <= discovery["held_stage_ii_bound_tolerance"]
    assert discovery["held_stage_ii_replay_ready"] is True
    assert discovery["held_stage_ii_replay_source"] == "sampled_candidate_audit_selected_candidates"
    assert discovery["held_stage_ii_replay_seed_name"] == "sampled_candidate_pair_replay"
    assert discovery["held_stage_iii_status"] == "pending_ipopt_refinement"
    assert discovery["phase_set_mass_balance_feasible"] is True
    assert discovery["stability_accepted"] is False
    assert discovery["candidate_completeness_accepted"] is False
    assert discovery["phase_set_status"] == (
        "sampled_candidate_audit_complete_global_completeness_unproven"
    )
    assert discovery["selected_candidate_count"] == 2
    assert len(discovery["selected_phase_compositions"]) == 2
    assert len(discovery["candidates"]) == discovery["unique_candidate_count"]
    assert sum(candidate["selected"] for candidate in discovery["candidates"]) == 2
    assert all(np.isfinite(candidate["tpd"]) for candidate in discovery["candidates"])


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
    assert discovery["continuous_tpd_status"] == "not_requested"
    assert discovery["continuous_tpd_start_count"] == 0
    assert discovery["held_stage_i_status"] == "not_requested"
    assert discovery["held_stage_ii_status"] == "not_requested"
    assert discovery["held_stage_ii_major_iterations"] == 0
    assert {candidate["tpd_backend"] for candidate in discovery["candidates"]} == {
        "deterministic_grid_evaluation",
    }


def test_neutral_sampled_candidate_ladder_reports_distinct_layers() -> None:
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

    assert discovery["stage9_phase_discovery_steps"] == STAGE9_PHASE_DISCOVERY_STEPS
    assert discovery["deterministic_screening_status"] == "completed"
    assert discovery["continuous_tpd_status"] == "converged"
    assert discovery["held_stage_ii_status"] == "sampled_candidate_audit_complete"
    assert discovery["held_stage_ii_dual_loop_status"] == "not_performed"
    assert discovery["held_stage_ii_status"] != discovery["held_stage_i_status"]
    assert discovery["held_stage_iii_status"] == "pending_ipopt_refinement"
    assert {candidate["tpd_backend"] for candidate in discovery["candidates"]} == {
        "deterministic_grid_evaluation",
        "continuous_coordinate_search",
    }
