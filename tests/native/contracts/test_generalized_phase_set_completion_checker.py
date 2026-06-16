from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from scripts.validation import check_generalized_phase_set as checker

SEED_NAME = "held_stage_ii_dual_loop_candidate_set"


def _record(
    index: int,
    *,
    phase_count: int,
    selected: bool,
    composition: list[float] | None = None,
) -> dict[str, Any]:
    return {
        "record_id": f"{'selected' if selected else 'rejected'}-{index}",
        "phase_count": phase_count,
        "phase_index": index,
        "phase_kind": "liquid",
        "phase_role": "accepted_phase" if selected else "candidate_phase",
        "source": "deterministic_tpd_candidate_screening",
        "phase_amount_total": 1.0 / phase_count,
        "phase_fraction": 1.0 / phase_count,
        "volume": 1.0e-5,
        "density": 20_000.0,
        "composition": composition or [0.2, 0.3, 0.5],
        "objective": -1.0 if selected else 0.0,
        "tpd": -1.0e-4 if selected else 1.0e-4,
        "feasibility_status": "accepted" if selected else "candidate_generated",
        "selection_status": "selected" if selected else "rejected",
        "rejection_reason": "accepted" if selected else "duplicate_or_collapsed",
        "phase_set_status": "phase_set_certified",
        "mass_balance_feasible": True,
        "stability_accepted": True,
        "candidate_completeness_accepted": True,
    }


def _selected_compositions(phase_count: int) -> list[list[float]]:
    if phase_count == 3:
        return [
            [0.92, 0.04, 0.04],
            [0.04, 0.92, 0.04],
            [0.04, 0.04, 0.92],
        ]
    return [
        [0.91, 0.03, 0.03, 0.03],
        [0.03, 0.91, 0.03, 0.03],
        [0.03, 0.03, 0.91, 0.03],
        [0.03, 0.03, 0.03, 0.91],
    ]


def _completion_payload(*, requested_phase_kinds: list[str] | None = None) -> dict[str, Any]:
    phase_kinds = requested_phase_kinds or ["liquid", "liquid", "liquid"]
    phase_count = len(phase_kinds)
    selected = _selected_compositions(phase_count)
    records = [
        _record(index, phase_count=phase_count, selected=True, composition=composition)
        for index, composition in enumerate(selected)
    ]
    records.append(
        _record(
            phase_count,
            phase_count=phase_count,
            selected=False,
            composition=[1.0 / phase_count for _ in range(phase_count)],
        )
    )
    return {
        "requested_phase_kinds": phase_kinds,
        "requested_phase_count": phase_count,
        "public_routes": ["flash", "lle"],
        "native_freshness_receipt": {
            "status": "fresh",
            "extension_path": "epcsaft_equilibrium._native",
            "source_digest": "test",
        },
        "postsolve": {
            "accepted": True,
            "phase_count": phase_count,
            "selected_candidate_count": phase_count,
            "selected_phase_fractions": [1.0 / phase_count for _ in range(phase_count)],
            "selected_phase_compositions": selected,
            "selected_phase_kinds": [0 for _ in range(phase_count)],
            "phase_set_status": "phase_set_certified",
            "phase_set_mass_balance_feasible": True,
            "candidate_completeness_accepted": True,
            "stability_accepted": True,
            "candidate_mass_balance_norm": 2.0e-12,
            "material_balance_norm": 2.0e-12,
            "pressure_consistency_norm": 2.0e-6,
            "ln_fugacity_consistency_norm": 2.0e-10,
            "phase_distance": 0.35,
            "phase_set_records": records,
            "held_stage_ii_replay_ready": True,
            "held_stage_ii_replay_seed_name": SEED_NAME,
            "held_stage_ii_replay_candidate_count": phase_count,
            "held_stage_iii_status": "ipopt_refinement_completed_current_route",
            "held_stage_iii_consumed_stage_ii_replay_metadata": True,
            "held_stage_iii_replay_source": "stage_ii_dual_loop_candidate_set",
            "held_stage_iii_replay_seed_name": SEED_NAME,
            "held_stage_iii_replay_candidate_count": phase_count,
        },
        "route_refinement": {
            "problem_name": "neutral_multiphase_eos",
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "accepted": True,
            "exact_hessian_available": True,
            "hessian_backend": "cppad_phase_system",
            "selected_seed_attempt_statuses": ["success"],
            "postsolve": {"accepted": True},
            "public_route_admission": "closed",
        },
    }


def _evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    return checker.evaluate_generalized_phase_set_completion(payload)


def test_completion_checker_accepts_route_refined_candidate_set_replay() -> None:
    result = _evaluate(_completion_payload())

    assert result["complete"] is True
    assert result["blockers"] == []
    assert result["requested_phase_kinds"] == ["liquid", "liquid", "liquid"]
    assert result["selected_candidate_count"] == 3
    assert result["held_stage_iii_status"] == "ipopt_refinement_completed_current_route"


def test_completion_checker_requires_route_refinement_block() -> None:
    payload = _completion_payload()
    payload.pop("route_refinement")

    result = _evaluate(payload)

    assert result["complete"] is False
    assert "missing_generalized_route_refinement" in result["blockers"]


@pytest.mark.parametrize(
    ("mutator", "blocker"),
    [
        (
            lambda payload: payload["postsolve"].pop("held_stage_ii_replay_seed_name"),
            "held_stage_ii_candidate_set_replay_missing",
        ),
        (
            lambda payload: payload["postsolve"].__setitem__(
                "held_stage_iii_consumed_stage_ii_replay_metadata", False
            ),
            "held_stage_iii_candidate_set_replay_not_consumed",
        ),
        (
            lambda payload: payload["postsolve"].__setitem__("selected_candidate_count", 2),
            "generalized_selected_phase_count_mismatch",
        ),
    ],
)
def test_completion_checker_rejects_missing_or_incomplete_replay_metadata(
    mutator: Any,
    blocker: str,
) -> None:
    payload = _completion_payload()
    mutator(payload)

    result = _evaluate(payload)

    assert result["complete"] is False
    assert blocker in result["blockers"]


@pytest.mark.parametrize(
    ("mutator", "blocker"),
    [
        (
            lambda payload: payload["route_refinement"].__setitem__("solver_status", "max_iterations_exceeded"),
            "stage_iii_ipopt_status_not_success",
        ),
        (
            lambda payload: payload["route_refinement"].__setitem__("application_status", "iteration_limit"),
            "stage_iii_application_status_not_solve_succeeded",
        ),
        (
            lambda payload: payload["postsolve"].__setitem__("material_balance_norm", 2.0e-7),
            "material_balance_norm_above_tolerance",
        ),
        (
            lambda payload: payload["postsolve"].__setitem__("pressure_consistency_norm", 2.0e-2),
            "pressure_consistency_norm_above_tolerance",
        ),
        (
            lambda payload: payload["postsolve"].__setitem__("ln_fugacity_consistency_norm", 2.0e-4),
            "ln_fugacity_consistency_norm_above_tolerance",
        ),
        (
            lambda payload: payload["postsolve"].__setitem__("phase_distance", 0.0),
            "collapsed_phase_distance",
        ),
    ],
)
def test_completion_checker_rejects_failed_stage_iii_or_residual_metrics(
    mutator: Any,
    blocker: str,
) -> None:
    payload = _completion_payload()
    mutator(payload)

    result = _evaluate(payload)

    assert result["complete"] is False
    assert blocker in result["blockers"]


def test_completion_checker_rejects_selected_seed_iteration_limit_attempts() -> None:
    payload = _completion_payload()
    payload["route_refinement"]["selected_seed_attempt_statuses"] = ["max_iterations_exceeded", "success"]

    result = _evaluate(payload)

    assert result["complete"] is False
    assert "stage_iii_selected_seed_iteration_limit" in result["blockers"]


def test_completion_checker_accepts_four_requested_phases_without_three_phase_hard_coding() -> None:
    result = _evaluate(_completion_payload(requested_phase_kinds=["liquid", "liquid", "liquid", "liquid"]))

    assert result["complete"] is True
    assert "generalized_phase_count_hard_coded" not in result["blockers"]
    assert result["requested_phase_count"] == 4
    assert result["selected_candidate_count"] == 4


def test_completion_checker_rejects_public_route_exposure() -> None:
    payload = _completion_payload()
    payload["public_routes"] = ["flash", "neutral_multiphase_nonassoc"]

    result = _evaluate(payload)

    assert result["complete"] is False
    assert "neutral_multiphase_public_route_exposed" in result["blockers"]


def test_completion_checker_rejects_lower_free_energy_rejected_candidate() -> None:
    payload = _completion_payload()
    records = deepcopy(payload["postsolve"]["phase_set_records"])
    records[-1]["objective"] = -2.0
    records[-1]["tpd"] = -2.0
    records[-1]["rejection_reason"] = "not_selected_by_generalized_phase_set_gate"
    payload["postsolve"]["phase_set_records"] = records

    result = _evaluate(payload)

    assert result["complete"] is False
    assert "lower_free_energy_omitted_candidate" in result["blockers"]
