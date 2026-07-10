from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.validation import check_neutral_lle_showcase as checker

REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "perfluorohexane_hexane"
)


class _SampledCandidateCore:
    def _native_neutral_tpd_phase_discovery(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "held_stage_ii_status": "sampled_candidate_audit_complete",
            "held_stage_ii_dual_loop_status": "not_performed",
            "phase_set_status": (
                "sampled_candidate_audit_complete_global_completeness_unproven"
            ),
            "candidate_completeness_accepted": False,
            "selected_phase_compositions": [[0.2, 0.8], [0.5497, 0.4503]],
            "selected_phase_fractions": [0.5, 0.5],
        }


def test_matsuda_checker_is_internal_sampled_candidate_diagnostic(monkeypatch) -> None:
    monkeypatch.setattr(checker, "_core", _SampledCandidateCore())
    monkeypatch.setattr(
        checker.native_freshness,
        "build_equilibrium_native_receipt",
        lambda **_kwargs: {"source_identity_matches": True},
    )

    payload = checker.evaluate_case_dir(CASE_DIR)

    assert payload["complete"] is True
    assert payload["status"] == "internal_diagnostic_complete"
    assert payload["production_route_admitted"] is False
    assert payload["global_phase_set_certified"] is False
    assert payload["shared_certification"] == {
        "status": "internal_validation",
        "selector_family": "neutral_lle",
        "production_exposed": False,
        "public_routes": [],
        "global_held_proof": False,
    }
    assert payload["comparison"]["max_composition_abs_error"] == 0.0
    assert payload["comparison"]["max_phase_fraction_abs_error"] == 0.0


def test_matsuda_checker_source_contains_no_production_selector_call() -> None:
    source = Path(checker.__file__).read_text(encoding="utf-8")

    assert "_native_equilibrium_selector_route_result" not in source
    assert '"production_accepted"' not in source
    assert '"dual_loop_verified"' not in source
    assert '"phase_set_certified"' not in source
