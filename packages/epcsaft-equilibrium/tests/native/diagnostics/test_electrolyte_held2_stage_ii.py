from __future__ import annotations

import math

from scripts.validation import check_electrolyte_held2_stage_ii as checker


def test_electrolyte_held2_stage_ii_consumes_stage_i_and_reports_replayable_bound_gap() -> None:
    payload = checker.evaluate_stage_ii(
        require_stage_i=True,
        require_bound_gap=True,
        require_replay=True,
        require_complete=True,
    )

    assert payload["complete"] is True, payload["blockers"]
    stage_i = payload["electrolyte_held2_stage_i"]
    evidence = payload["electrolyte_held2_stage_ii"]
    assert evidence["algorithm_scope"] == "held2_stage_ii_electrolyte_dual_phase_discovery_only"
    assert evidence["native_binding"] == "_native_electrolyte_held2_phase_discovery"
    assert evidence["stage_i_certificate"]["status"] == "consumed"
    assert evidence["stage_i_certificate"]["stage_i_classification"] == "unstable_negative_tpd"
    assert stage_i["stage_i_classification"] == "unstable_negative_tpd"
    assert evidence["stage_ii_status"] == "dual_loop_verified"
    assert evidence["candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert evidence["dual_loop_status"] == "verified"
    assert evidence["stopping_reason"] == "bound_gap_closed"
    assert evidence["stage_iii_refinement_status"] == "pending_ipopt_refinement"
    assert evidence["public_route_admission_status"] == "separate_public_admission_gate"

    bounds = evidence["candidate_bounds"]
    assert bounds["major_iterations"] > 0
    assert bounds["candidate_count"] >= bounds["selected_candidate_count"] >= 2
    assert math.isfinite(bounds["lower_bound"])
    assert math.isfinite(bounds["upper_bound"])
    assert 0.0 <= bounds["bound_gap"] <= bounds["bound_tolerance"] <= checker.STAGE_II_BOUND_TOLERANCE
    assert len(bounds["lower_bound_history"]) == bounds["major_iterations"]
    assert len(bounds["upper_bound_history"]) == bounds["major_iterations"]
    assert len(bounds["bound_gap_history"]) == bounds["major_iterations"]
    assert bounds["lower_bound_history"][-1] == bounds["lower_bound"]
    assert bounds["upper_bound_history"][-1] == bounds["upper_bound"]
    assert bounds["bound_gap_history"][-1] == bounds["bound_gap"]

    replay = evidence["replay_payload"]
    assert replay["status"] == "replayable"
    assert replay["replay_ready"] is True
    assert replay["source"] == "stage_ii_dual_loop_selected_candidates"
    assert replay["stage_iii_status"] == "pending_ipopt_refinement"
    assert replay["candidate_count"] == len(replay["phase_fractions"])
    assert replay["candidate_count"] == len(replay["phase_kinds"])
    assert replay["candidate_count"] == len(replay["phase_compositions"])
    assert replay["max_charge_residual"] <= checker.CHARGE_TOLERANCE
    assert replay["max_composition_sum_residual"] <= checker.CANDIDATE_MASS_BALANCE_TOLERANCE

    rejected = evidence["rejected_candidates"]
    assert evidence["rejected_candidate_count"] == len(rejected) > 0
    for record in rejected:
        assert record["reason"] == "not_selected_by_dual_loop_mass_balance_gate"
        assert math.isfinite(record["tpd"])
        assert record["charge_residual"] <= checker.CHARGE_TOLERANCE
        assert record["composition_sum_residual"] <= checker.CANDIDATE_MASS_BALANCE_TOLERANCE
        assert record["domain_margin"] > 0.0


def test_electrolyte_held2_stage_ii_retains_reduced_basis_coverage() -> None:
    payload = checker.evaluate_stage_ii(
        require_stage_i=True,
        require_bound_gap=True,
        require_replay=True,
        require_complete=True,
    )

    assert payload["complete"] is True, payload["blockers"]
    coverage = payload["electrolyte_held2_stage_ii"]["reduced_basis_coverage"]
    assert set(coverage) == {"neutral_only", "single_salt", "common_ion", "mixed_salt"}
    assert coverage["neutral_only"]["active_charge_rank"] == 0
    for key, evidence in coverage.items():
        assert evidence["status"] == "covered"
        assert evidence["max_charge_residual"] <= checker.CHARGE_TOLERANCE
        assert evidence["composition_sum_residual"] <= checker.CANDIDATE_MASS_BALANCE_TOLERANCE
        assert evidence["round_trip_residual"] <= checker.ROUND_TRIP_TOLERANCE
        assert evidence["component_nonnegativity_margin"] >= -1.0e-12


def test_electrolyte_held2_stage_ii_requires_closed_bound_gap() -> None:
    payload = checker.minimal_complete_payload_for_tests()
    stage_i = checker.minimal_stage_i_payload_for_tests()
    tpd_discovery = payload["held2_phase_discovery"]["tpd_discovery"]
    tpd_discovery["held_stage_ii_bound_gap"] = 1.0e-3
    tpd_discovery["held_stage_ii_bound_gap_history"] = [1.0e-3]
    tpd_discovery["held_stage_ii_candidate_bound_audit_status"] = "candidate_bound_gap_open"
    tpd_discovery["held_stage_ii_status"] = "dual_loop_incomplete"
    tpd_discovery["held_stage_ii_dual_loop_status"] = "incomplete_candidate_bound_gap_open"

    result = checker.evaluate_stage_ii_payload(
        payload,
        stage_i_payload=stage_i,
        require_bound_gap=True,
        require_replay=True,
        require_complete=True,
    )

    assert result["complete"] is False
    assert "stage_ii_bound_gap_open" in result["blockers"]


def test_electrolyte_held2_stage_ii_requires_replay_payload() -> None:
    payload = checker.minimal_complete_payload_for_tests()
    stage_i = checker.minimal_stage_i_payload_for_tests()
    tpd_discovery = payload["held2_phase_discovery"]["tpd_discovery"]
    tpd_discovery["held_stage_ii_replay_ready"] = False
    tpd_discovery["held_stage_ii_replay_phase_fractions"] = []
    tpd_discovery["held_stage_ii_replay_phase_kinds"] = []
    tpd_discovery["held_stage_ii_replay_phase_compositions"] = []

    result = checker.evaluate_stage_ii_payload(
        payload,
        stage_i_payload=stage_i,
        require_bound_gap=True,
        require_replay=True,
        require_complete=True,
    )

    assert result["complete"] is False
    assert "stage_ii_replay_payload_missing" in result["blockers"]
