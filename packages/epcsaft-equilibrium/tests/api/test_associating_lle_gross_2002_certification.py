from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("epcsaft_equilibrium._native_core")

from scripts.validation import check_gross_2002_association_acceptance as checker


@pytest.fixture(scope="module")
def gross_2002_associating_lle_certification_payload() -> dict[str, Any]:
    return checker.evaluate_campaign(
        require_complete=True,
        require_exact_association_hessian=True,
        require_fresh_native=True,
    )


def test_associating_lle_gross_2002_certification_payload_reports_shared_contract(
    gross_2002_associating_lle_certification_payload: dict[str, Any],
) -> None:
    payload = gross_2002_associating_lle_certification_payload

    assert payload["complete"] is True
    assert payload["blockers"] == []
    shared = payload["shared_certification"]
    assert shared["status"] == "accepted"
    assert shared["selector_family"] == "neutral_lle"
    assert shared["family_residual_block"] == "lle"
    assert shared["public_routes"] == ["lle"]
    assert set(shared["required_associating_evidence_quantities"]) == {
        "associating_neutral_lle_gross_2002_public_exact_hessian",
        "associating_neutral_lle_gross_2002_figure_10_public_exact_hessian",
    }
    evidence_by_quantity = {row["quantity"]: row for row in shared["associating_evidence_rows"]}
    assert set(evidence_by_quantity) == set(shared["required_associating_evidence_quantities"])
    for row in evidence_by_quantity.values():
        assert row["backend"] == "cppad_implicit_association"
        assert row["classification"] == "production_supported"
        assert row["public_admission_state"] == "public_route_open"
        assert row["public_route"] == "lle"


def test_associating_lle_gross_2002_certification_retains_source_margins_and_overlay_gaps(
    gross_2002_associating_lle_certification_payload: dict[str, Any],
) -> None:
    margins = gross_2002_associating_lle_certification_payload["source_tolerance_margins"]

    assert set(margins) == {"figure_08", "figure_10"}
    for figure_margins in margins.values():
        assert figure_margins["source_point_count"]["status"] == "accepted"
        assert figure_margins["normalized_plot_score"]["status"] == "accepted"
        assert figure_margins["branch_coverage_score"]["status"] == "accepted"
        assert figure_margins["mass_action_residual"]["status"] == "accepted"
        assert figure_margins["fit_pass"]["status"] == "accepted"
        assert figure_margins["derivative_status"]["status"] == "accepted"
        assert figure_margins["literature_overlay"]["counts_toward_completion"] is False
        assert figure_margins["literature_overlay"]["status"] == "regression_followup_not_m4_acceptance"
