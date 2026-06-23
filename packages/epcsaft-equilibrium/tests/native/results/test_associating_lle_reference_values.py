from __future__ import annotations

from pathlib import Path

from scripts.validation import check_associating_lle_gross_2002 as checker


REPO_ROOT = Path(__file__).resolve().parents[5]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "associating_lle"
    / "methanol_cyclohexane"
)


def test_internal_gross_2002_associating_lle_source_pair_is_certified() -> None:
    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_source_data=True,
        require_exact_association_hessian=True,
        require_internal_route=True,
        require_route_closed=True,
    )

    assert payload["complete"] is True
    route = payload["internal_route"]
    assert route["status"] == "internal_source_pair_certified"
    assert route["phase_count"] == 2
    assert route["phase_branches"] == ["methanol_lean_liquid", "methanol_rich_liquid"]
    assert route["phase_distance"] > 0.5
    assert route["max_branch_composition_abs_error"] <= 0.10
    assert route["max_temperature_abs_error_K"] <= 5.0
    assert route["association_hessian_status"] == "verified_exact"
    postsolve = route["postsolve"]
    assert postsolve["neutral_held_tpd_contract_preserved"] is True
    assert postsolve["public_admission_state"] == "closed_until_issue_190"
    assert postsolve["stability_certificate"] == "tpd_postsolve_contract_required_for_public_admission"
    assert postsolve["phase_set_status"] == "source_pair_certified"
