from __future__ import annotations

HELD_STAGE_II_REPLAY_SEED = "held_stage_ii_dual_loop_candidate_pair"


def assert_neutral_lle_stage_iii_replay_receipt(route: dict) -> None:
    postsolve = route["postsolve"]
    attempts = list(route["seed_attempts"])
    assert attempts
    assert attempts[0]["seed_name"] == HELD_STAGE_II_REPLAY_SEED
    replay_attempt = next(
        attempt for attempt in attempts if attempt["seed_name"] == HELD_STAGE_II_REPLAY_SEED
    )
    accepted_attempts = [attempt for attempt in attempts if attempt["accepted"] is True]
    assert accepted_attempts
    assert route["seed_name"] == accepted_attempts[0]["seed_name"]

    if route["seed_name"] == HELD_STAGE_II_REPLAY_SEED:
        assert postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"] is True
        assert postsolve["held_stage_iii_replay_source"] == "stage_ii_dual_loop_candidate_seed"
        assert postsolve["held_stage_iii_replay_seed_name"] == HELD_STAGE_II_REPLAY_SEED
        assert postsolve["held_stage_iii_replay_candidate_count"] == postsolve["held_stage_ii_replay_candidate_count"]
        assert replay_attempt["accepted"] is True
        return

    assert postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"] is False
    assert postsolve["held_stage_iii_replay_source"] == ""
    assert postsolve["held_stage_iii_replay_seed_name"] == ""
    assert postsolve["held_stage_iii_replay_candidate_count"] == 0
    assert replay_attempt["accepted"] is False
    assert replay_attempt["status"] == "postsolve_rejected"
    assert replay_attempt["solver_status"] == "success"
    assert replay_attempt["application_status"] == "solve_succeeded"
    assert replay_attempt["phase_equilibrium_norm"] > 1.0e-6
    assert accepted_attempts[0]["phase_equilibrium_norm"] <= 1.0e-6
