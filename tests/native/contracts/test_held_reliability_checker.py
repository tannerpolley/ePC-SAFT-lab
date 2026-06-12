from __future__ import annotations


def test_reliability_summary_requires_exact_campaign_size() -> None:
    from scripts.validation import check_held_reliability as checker

    summary = checker.summarize_campaign(
        conditions=[
            checker.ConditionResult(
                condition_index=0,
                accepted=True,
                repeats=[checker.accepted_repeat_for_test()],
            )
        ],
        required_conditions=100,
        required_repeats=100,
    )

    assert summary["complete"] is False
    assert "accepted_condition_count_mismatch" in summary["blockers"]
    assert "attempted_repeat_count_mismatch" in summary["blockers"]


def test_reliability_summary_accepts_full_clean_campaign() -> None:
    from scripts.validation import check_held_reliability as checker

    conditions = [
        checker.ConditionResult(
            condition_index=condition_index,
            accepted=True,
            repeats=[
                checker.accepted_repeat_for_test(
                    condition_index=condition_index,
                    repeat_index=repeat_index,
                    pressure_transformed_objective=float(condition_index),
                )
                for repeat_index in range(2)
            ],
        )
        for condition_index in range(2)
    ]

    summary = checker.summarize_campaign(
        conditions=conditions,
        required_conditions=2,
        required_repeats=2,
    )

    assert summary["complete"] is True
    assert summary["blockers"] == []
    assert summary["accepted_conditions"] == 2
    assert summary["attempted_repeats"] == 4
    assert summary["failed_repeats"] == 0
    assert summary["first_failure"] is None


def test_reliability_summary_rejects_objective_spread_above_tolerance() -> None:
    from scripts.validation import check_held_reliability as checker

    summary = checker.summarize_campaign(
        conditions=[
            checker.ConditionResult(
                condition_index=0,
                accepted=True,
                repeats=[
                    checker.accepted_repeat_for_test(pressure_transformed_objective=1.0),
                    checker.accepted_repeat_for_test(
                        repeat_index=1,
                        pressure_transformed_objective=1.0 + 2.0e-6,
                    ),
                ],
            )
        ],
        required_conditions=1,
        required_repeats=2,
    )

    assert summary["complete"] is False
    assert "objective_spread_above_tolerance" in summary["blockers"]
    assert summary["condition_summaries"][0]["objective_spread"] > 1.0e-6


def test_reliability_summary_records_first_failure_reproduction() -> None:
    from scripts.validation import check_held_reliability as checker

    failed_repeat = checker.RepeatResult(
        condition_index=7,
        repeat_index=5,
        accepted=False,
        temperature=223.0,
        pressure=1.1e6,
        feed_composition=[0.45, 0.55],
        random_seed=2001,
        native_module_path="C:/repo/epcsaft_equilibrium/_native_core.pyd",
        stage_statuses={
            "continuous_tpd_status": "converged",
            "held_stage_ii_status": "dual_loop_verified",
            "held_stage_iii_status": "solver_rejected",
        },
        rejection_reason="solver_rejected",
    )

    summary = checker.summarize_campaign(
        conditions=[
            checker.ConditionResult(
                condition_index=7,
                accepted=True,
                repeats=[
                    checker.accepted_repeat_for_test(condition_index=7, repeat_index=0),
                    failed_repeat,
                ],
            )
        ],
        required_conditions=1,
        required_repeats=2,
    )

    assert summary["complete"] is False
    assert summary["failed_repeats"] == 1
    assert "failed_repeat" in summary["blockers"]
    assert summary["first_failure"] == {
        "condition_index": 7,
        "repeat_index": 5,
        "temperature": 223.0,
        "pressure": 1.1e6,
        "feed_composition": [0.45, 0.55],
        "random_seed": 2001,
        "native_module_path": "C:/repo/epcsaft_equilibrium/_native_core.pyd",
        "stage_statuses": {
            "continuous_tpd_status": "converged",
            "held_stage_ii_status": "dual_loop_verified",
            "held_stage_iii_status": "solver_rejected",
        },
        "rejection_reason": "solver_rejected",
    }
