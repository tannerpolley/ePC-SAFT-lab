from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("epcsaft_equilibrium._native_core")

from scripts.validation import check_neutral_tp_flash_fixture as checker


REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_tp_flash"
    / "methane_ethane_propane"
)

VERIFIED_PHASE_DISCOVERY_STATUS = {
    "deterministic_screening": "verified_not_full_held",
    "continuous_tpd_minimization": "verified_converged",
    "held_stage_i_stability": "verified_from_converged_continuous_tpd",
    "held_stage_ii_dual_phase_discovery": "verified_dual_loop_replayable",
    "held_stage_iii_ipopt_refinement": "verified_current_route_refinement_consumed_stage_ii_replay",
}

VERIFIED_PHASE_DISCOVERY_PAYLOAD = {
    "complete": True,
    "requirement_status": VERIFIED_PHASE_DISCOVERY_STATUS,
}


def _route_payload(*, postsolve_updates: dict[str, Any] | None = None) -> dict[str, Any]:
    postsolve: dict[str, Any] = {
        "accepted": True,
        "stability_certificate": "tpd_postsolve",
        "stability_checked": True,
        "stability_accepted": True,
        "candidate_completeness_accepted": True,
        "phase_set_status": "phase_set_certified",
        "selected_candidate_count": 2,
        "phase_distance": 0.624657,
        "phase_compositions": [
            [0.1, 0.3, 0.6],
            [0.7246628928343289, 0.20293191372324873, 0.0724051934424223],
        ],
        "phase_amount_totals": [1.0, 1.0],
        "material_balance_norm": 0.0,
        "pressure_consistency_norm": 0.0,
        "ln_fugacity_consistency_norm": 0.0,
    }
    if postsolve_updates:
        postsolve.update(postsolve_updates)
    return {
        "status": "production_accepted",
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "accepted": True,
        "hessian_approximation": "exact",
        "exact_hessian_available": True,
        "eval_h_calls": 1,
        "postsolve": postsolve,
    }


def _patch_route(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    def fake_run_route(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(checker, "_run_route", fake_run_route)


def test_neutral_tp_flash_fixture_reports_held_tpd_admission_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_route(monkeypatch, _route_payload())

    payload = checker.evaluate_neutral_flash(CASE_DIR, VERIFIED_PHASE_DISCOVERY_PAYLOAD)

    assert payload["complete"] is True
    assert payload["held_tpd_admission"] == {
        "required": True,
        "accepted": True,
        "source": "phase_discovery_payload",
        "requirement_status": VERIFIED_PHASE_DISCOVERY_STATUS,
        "incomplete_requirements": [],
    }


@pytest.mark.parametrize(
    ("postsolve_updates", "expected_blocker"),
    [
        ({"candidate_completeness_accepted": False}, "neutral_flash_candidate_completeness_not_accepted"),
        ({"phase_set_status": "candidate_set_incomplete"}, "neutral_flash_phase_set_not_certified"),
        ({"phase_distance": 0.0}, "neutral_flash_phase_distance_not_distinct"),
        ({"selected_candidate_count": 1}, "neutral_flash_selected_candidate_count_mismatch"),
    ],
)
def test_neutral_tp_flash_fixture_requires_result_certification_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    postsolve_updates: dict[str, Any],
    expected_blocker: str,
) -> None:
    _patch_route(monkeypatch, _route_payload(postsolve_updates=postsolve_updates))

    payload = checker.evaluate_neutral_flash(CASE_DIR, VERIFIED_PHASE_DISCOVERY_PAYLOAD)

    assert payload["complete"] is False
    assert expected_blocker in payload["blockers"]
