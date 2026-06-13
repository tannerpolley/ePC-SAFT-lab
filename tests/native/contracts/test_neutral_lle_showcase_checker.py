from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("epcsaft_equilibrium._native_core")

from scripts.validation import check_neutral_lle_showcase as checker


REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "matsuda_2011_pfhexane_hexane"
)


def _route_payload(*, postsolve_updates: dict[str, Any] | None = None) -> dict[str, Any]:
    postsolve: dict[str, Any] = {
        "accepted": True,
        "phase_discovery_backend": "continuous_tpd_held_dual_phase_discovery",
        "stability_certificate": "tpd_postsolve",
        "stability_checked": True,
        "stability_accepted": True,
        "candidate_completeness_accepted": True,
        "phase_set_status": "phase_set_certified",
        "selected_candidate_count": 2,
        "phase_distance": 0.3472340466839401,
        "phase_compositions": [
            [0.19253198692922618, 0.8074680130707738],
            [0.5397660336131663, 0.46023396638683367],
        ],
        "selected_phase_fractions": [0.47494200291734767, 0.5250579970826523],
        "phase_amount_totals": [0.47494200291734767, 0.5250579970826523],
        "material_balance_norm": 0.0,
        "pressure_consistency_norm": 0.0,
        "ln_fugacity_consistency_norm": 0.0,
        "held_stage_ii_candidate_bound_audit_status": "candidate_bound_gap_closed",
        "held_stage_ii_status": "dual_loop_verified",
        "held_stage_ii_dual_loop_status": "verified",
        "held_stage_ii_replay_ready": True,
        "held_stage_iii_status": "ipopt_refinement_completed_current_route",
        "held_stage_iii_consumed_stage_ii_replay_metadata": True,
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


def test_neutral_lle_showcase_fixture_reports_source_backed_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_route(monkeypatch, _route_payload())

    payload = checker.evaluate_case_dir(CASE_DIR)

    assert payload["complete"] is True
    assert payload["case_label"] == "Matsuda 2011 perfluorohexane + hexane neutral LLE"
    assert payload["fixture"]["source_data"]["status"] == "source_backed"
    assert payload["fixture"]["binary_interaction"]["status"] == "source_fitted"
    assert payload["comparison"]["max_composition_abs_error"] <= 0.02
    assert payload["comparison"]["max_phase_fraction_abs_error"] <= 0.03


@pytest.mark.parametrize(
    ("postsolve_updates", "expected_blocker"),
    [
        ({"held_stage_ii_status": "pending"}, "neutral_lle_held_stage_ii_not_verified"),
        ({"held_stage_ii_replay_ready": False}, "neutral_lle_held_stage_ii_not_replay_ready"),
        ({"held_stage_iii_status": "pending"}, "neutral_lle_held_stage_iii_not_completed"),
        (
            {"held_stage_iii_consumed_stage_ii_replay_metadata": False},
            "neutral_lle_held_stage_iii_did_not_consume_stage_ii_replay",
        ),
    ],
)
def test_neutral_lle_showcase_requires_held_stage_ii_and_iii_certification(
    monkeypatch: pytest.MonkeyPatch,
    postsolve_updates: dict[str, Any],
    expected_blocker: str,
) -> None:
    _patch_route(monkeypatch, _route_payload(postsolve_updates=postsolve_updates))

    payload = checker.evaluate_case_dir(CASE_DIR)

    assert payload["complete"] is False
    assert expected_blocker in payload["blockers"]
