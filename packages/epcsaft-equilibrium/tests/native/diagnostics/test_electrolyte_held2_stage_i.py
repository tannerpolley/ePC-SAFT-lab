from __future__ import annotations

import math

from scripts.validation import check_electrolyte_held2_stage_i as checker


def _trial_phase(
    *,
    tpd: float,
    accepted: bool = True,
    tpd_status: str = "converged",
    rejection_reason: str = "",
) -> dict[str, object]:
    return {
        "record_type": "trial_phase",
        "coordinate_basis": "reduced_electroneutral_modified_mole_fractions",
        "source": "unit_start",
        "start_source": "unit_start",
        "phase_kind": 0,
        "composition": [0.97, 0.01, 0.0, 0.01, 0.01],
        "reduced_coordinate_species": ["H2O", "Ethanol", "Butanol"],
        "reduced_coordinates": [0.97, 0.01, 0.0],
        "neutral_closure_species": "H2O",
        "eliminated_charged_species": "Na+",
        "charge_residual": 0.0,
        "normalization_residual": 0.0,
        "domain_margin": 0.01,
        "molar_volume": 1.8e-5,
        "tpd": tpd,
        "tpd_backend": "continuous_reduced_electroneutral_coordinate_search",
        "tpd_status": tpd_status,
        "tpd_iteration_count": 24,
        "tpd_step_final": 1.0e-12,
        "accepted": accepted,
        "rejection_reason": rejection_reason,
    }


def _continuous_payload(start_records: list[dict[str, object]], *, status: str = "complete") -> dict[str, object]:
    accepted = [record for record in start_records if record["accepted"]]
    rejected = [record for record in start_records if not record["accepted"]]
    tpd_values = [float(record["tpd"]) for record in accepted]
    return {
        "checker": "electrolyte_held2_continuous_tpd",
        "complete": status == "complete",
        "blockers": [] if status == "complete" else ["continuous_tpd_incomplete"],
        "electrolyte_held2_continuous_tpd": {
            "status": status,
            "blockers": [] if status == "complete" else ["continuous_tpd_incomplete"],
            "algorithm_scope": "held2_continuous_reduced_electroneutral_tpd_minimizer_only",
            "phase_discovery_backend": "continuous_reduced_electroneutral_tpd_minimization",
            "stability_certificate": "electrolyte_continuous_reduced_electroneutral_tpd_minimizer",
            "continuous_tpd_status": "converged" if not rejected else "complete_with_rejected_starts",
            "continuous_tpd_backend": "continuous_reduced_electroneutral_coordinate_search",
            "continuous_tpd_start_count": len(start_records),
            "continuous_tpd_solve_count": len(start_records),
            "continuous_tpd_converged_count": len(accepted),
            "continuous_tpd_iteration_count_total": 24 * len(start_records),
            "continuous_tpd_iteration_count_max": 24 if start_records else 0,
            "continuous_tpd_min": min(tpd_values) if tpd_values else math.inf,
            "accepted_start_count": len(accepted),
            "rejected_start_count": len(rejected),
            "max_charge_residual": 0.0,
            "max_normalization_residual": 0.0,
            "min_domain_margin": 0.01 if start_records else math.inf,
            "start_records": start_records,
            "stage_statuses": {
                "stage_i_certificate": "pending_stage_i_stability_certificate",
                "stage_ii_discovery": "pending_held2_stage_ii_discovery",
                "stage_iii_refinement": "pending_ipopt_refinement",
                "public_route_admission": "separate_public_admission_gate",
            },
        },
    }


def test_electrolyte_held2_stage_i_classifies_real_negative_tpd_for_stage_ii_replay() -> None:
    payload = checker.evaluate_stage_i(require_continuous_tpd=True)

    assert payload["complete"] is True, payload["blockers"]
    evidence = payload["electrolyte_held2_stage_i"]
    assert evidence["algorithm_scope"] == "held2_stage_i_electrolyte_stability_certificate_only"
    assert evidence["stability_certificate"] == "electrolyte_held2_stage_i_stability_certificate"
    assert evidence["stage_i_classification"] == "unstable_negative_tpd"
    assert evidence["certificate_status"] == "complete"
    assert evidence["negative_tpd_found"] is True
    assert evidence["stage_ii_handoff_ready"] is True
    assert evidence["stage_ii_handoff"]["status"] == "ready_for_stage_ii_discovery"
    assert evidence["stage_ii_handoff"]["trial_phase_count"] == len(evidence["negative_tpd_trial_phases"]) > 0
    assert evidence["no_negative_tpd_certificate"]["retained"] is False
    assert evidence["public_route_admission_status"] == "separate_public_admission_gate"
    assert evidence["suspect_start_count"] > 0
    assert evidence["suspect_start_status"] == "suspect_starts_retained_with_decisive_negative_tpd"
    assert evidence["continuous_tpd_min"] < -checker.STAGE_I_TPD_FLOOR
    for record in evidence["negative_tpd_trial_phases"]:
        assert record["accepted"] is True
        assert record["tpd"] < -checker.STAGE_I_TPD_FLOOR
        assert record["charge_residual"] <= checker.CHARGE_TOLERANCE
        assert record["normalization_residual"] <= checker.NORMALIZATION_TOLERANCE
        assert record["domain_margin"] > 0.0


def test_electrolyte_held2_stage_i_retains_stable_no_negative_tpd_certificate() -> None:
    stable = _continuous_payload(
        [
            _trial_phase(tpd=2.0e-9),
            _trial_phase(tpd=1.0e-8),
        ]
    )

    payload = checker.evaluate_stage_i_payload(stable, require_complete=True)

    assert payload["complete"] is True, payload["blockers"]
    evidence = payload["electrolyte_held2_stage_i"]
    assert evidence["stage_i_classification"] == "stable_no_negative_tpd"
    assert evidence["certificate_status"] == "complete"
    assert evidence["negative_tpd_found"] is False
    assert evidence["negative_tpd_trial_phases"] == []
    assert evidence["stage_ii_handoff_ready"] is False
    assert evidence["stage_ii_handoff"]["status"] == "stable_feed_no_stage_ii_handoff"
    assert evidence["no_negative_tpd_certificate"] == {
        "retained": True,
        "minimum_tpd": 2.0e-9,
        "tpd_floor": checker.STAGE_I_TPD_FLOOR,
        "accepted_start_count": 2,
        "governed_start_count": 2,
    }


def test_electrolyte_held2_stage_i_rejects_suspect_starts_without_negative_tpd() -> None:
    suspect = _continuous_payload(
        [
            _trial_phase(tpd=5.0e-9),
            _trial_phase(
                tpd=7.0e-9,
                accepted=False,
                tpd_status="iteration_limit",
                rejection_reason="continuous_tpd_iteration_limit",
            ),
        ]
    )

    payload = checker.evaluate_stage_i_payload(suspect, require_complete=True)

    assert payload["complete"] is False
    assert "stage_i_suspect_starts_block_stable_certificate" in payload["blockers"]
    evidence = payload["electrolyte_held2_stage_i"]
    assert evidence["stage_i_classification"] == "suspect_start_incomplete"
    assert evidence["certificate_status"] == "incomplete"
    assert evidence["suspect_start_count"] == 1
    assert evidence["negative_tpd_found"] is False
    assert evidence["stage_ii_handoff_ready"] is False


def test_electrolyte_held2_stage_i_fails_loudly_when_continuous_tpd_is_incomplete() -> None:
    incomplete = _continuous_payload([], status="incomplete")

    payload = checker.evaluate_stage_i_payload(incomplete, require_complete=True)

    assert payload["complete"] is False
    assert "stage_i_continuous_tpd_incomplete" in payload["blockers"]
    evidence = payload["electrolyte_held2_stage_i"]
    assert evidence["stage_i_classification"] == "incomplete_continuous_tpd"
    assert evidence["certificate_status"] == "incomplete"
    assert evidence["negative_tpd_trial_phases"] == []
    assert evidence["no_negative_tpd_certificate"]["retained"] is False
