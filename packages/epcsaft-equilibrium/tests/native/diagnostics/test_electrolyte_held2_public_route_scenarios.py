from __future__ import annotations

import copy

from scripts.validation import check_electrolyte_held2_public_route_scenarios as checker


def test_electrolyte_held2_public_route_scenario_checker_covers_required_matrix() -> None:
    payload = checker.evaluate_public_route_scenarios(require_complete=True)

    assert payload["complete"] is True, payload["blockers"]
    matrix = payload["validation_matrix"]
    assert set(matrix) == set(checker.REQUIRED_SCENARIOS)
    assert payload["scenario_summary"]["accepted_scenario_count"] == len(checker.REQUIRED_SCENARIOS)

    unstable = matrix["unstable_feed"]
    assert unstable["evidence_level"] == "electrolyte_public_route_solve"
    assert unstable["stage_ii_status"] == "dual_loop_verified"
    assert unstable["stage_ii_replay_ready"] is True
    assert unstable["stage_iii_status"] == "complete"
    assert unstable["postsolve_status"] == "complete"
    assert unstable["negative_tpd_found"] is True

    boundary = matrix["boundary_feed"]
    assert boundary["phase_distance"] > boundary["phase_distance_tolerance"]
    assert boundary["charge_residual"] <= boundary["charge_tolerance"]
    assert boundary["mean_ionic_transfer_residual"] <= boundary["mean_ionic_transfer_tolerance"]

    neutral = matrix["neutral_limit_parity"]
    assert neutral["public_route"] == "lle"
    assert neutral["selector_family"] == "neutral_lle"
    assert neutral["held_stage_i_status"] == "no_negative_tpd_candidate_found"
    assert neutral["charged_residual_family_claimed"] is False

    assert matrix["common_ion_electrolyte"]["matrix_rank"] == matrix["common_ion_electrolyte"]["expected_rank"]
    assert (
        matrix["mixed_salt_asymmetric_electrolyte"]["matrix_rank"]
        == matrix["mixed_salt_asymmetric_electrolyte"]["expected_rank"]
    )


def test_electrolyte_held2_public_route_scenario_checker_requires_postsolve_artifacts() -> None:
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["validation_matrix"]["unstable_feed"]["postsolve_status"] = "pending"
    mutated["validation_matrix"]["unstable_feed"]["postsolve_accepted"] = False

    result = checker.evaluate_payload(mutated, require_complete=True)

    assert result["complete"] is False
    assert "unstable_feed_postsolve_incomplete" in result["blockers"]


def test_electrolyte_held2_public_route_scenario_checker_requires_common_ion_rank() -> None:
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["validation_matrix"]["common_ion_electrolyte"]["matrix_rank"] = 1

    result = checker.evaluate_payload(mutated, require_complete=True)

    assert result["complete"] is False
    assert "common_ion_electrolyte_rank_incomplete" in result["blockers"]
