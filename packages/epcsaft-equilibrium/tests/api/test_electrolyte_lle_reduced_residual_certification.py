from __future__ import annotations

from scripts.validation import check_electrolyte_public_admission as checker


def test_electrolyte_held2_reduced_residual_certification_payload_accepts_public_route() -> None:
    payload = checker.evaluate_public_admission(
        require_held2_stage_ii=True,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_admission=True,
    )

    shared = payload["shared_certification"]

    assert payload["complete"] is True, payload["blockers"]
    assert shared["status"] == "accepted"
    assert shared["route"] == "electrolyte_lle"
    assert shared["selector_family"] == "electrolyte_lle"
    assert shared["family_residual_block"] == "electrolyte_lle"
    assert shared["raw_single_ion_equality_used"] is False

    residuals = shared["residual_blocks"]
    assert residuals["reduced_electroneutral_basis"]["status"] == "accepted"
    assert residuals["lift_back_lift"]["status"] == "accepted"
    assert residuals["projected_transfer"]["status"] == "accepted"
    assert residuals["mean_ionic_transfer"]["status"] == "accepted"
    assert residuals["active_electrolyte_blocks"]["born_ssm_ds_exactness"] == "accepted"
    assert residuals["active_electrolyte_blocks"]["exact_reduced_hessian_available"] is True
