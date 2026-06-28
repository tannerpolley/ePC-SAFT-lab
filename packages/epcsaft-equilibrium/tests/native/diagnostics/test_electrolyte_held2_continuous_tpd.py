from __future__ import annotations

import math

from scripts.validation import check_electrolyte_held2_continuous_tpd as checker


def test_electrolyte_held2_continuous_tpd_reports_replayable_start_diagnostics() -> None:
    payload = checker.evaluate_continuous_tpd(require_native_continuous_tpd=True)

    assert payload["complete"] is True, payload["blockers"]
    evidence = payload["electrolyte_held2_continuous_tpd"]
    assert evidence["native_binding"] == "_native_electrolyte_held2_continuous_tpd_minimizer"
    assert evidence["algorithm_scope"] == "held2_continuous_reduced_electroneutral_tpd_minimizer_only"
    assert evidence["phase_discovery_backend"] == "continuous_reduced_electroneutral_tpd_minimization"
    assert evidence["continuous_tpd_backend"] == "continuous_reduced_electroneutral_coordinate_search"
    assert evidence["deterministic_screening_role"] == "seed_support_only"
    assert evidence["deterministic_screening_is_full_held"] is False
    assert evidence["public_route_admission_status"] == "separate_public_admission_gate"

    assert evidence["continuous_tpd_status"] in {"converged", "complete_with_rejected_starts"}
    assert evidence["continuous_tpd_start_count"] > 0
    assert evidence["continuous_tpd_solve_count"] == evidence["continuous_tpd_start_count"]
    assert evidence["continuous_tpd_converged_count"] == evidence["accepted_start_count"]
    assert evidence["accepted_start_count"] > 0
    assert evidence["rejected_start_count"] > 0
    assert math.isfinite(evidence["continuous_tpd_min"])
    assert evidence["max_charge_residual"] <= checker.CHARGE_TOLERANCE
    assert evidence["min_domain_margin"] > 0.0

    start_records = evidence["start_records"]
    assert len(start_records) == evidence["continuous_tpd_start_count"]
    assert any(record["accepted"] for record in start_records)
    assert any(not record["accepted"] for record in start_records)
    for record in start_records:
        assert record["record_type"] == "trial_phase"
        assert record["coordinate_basis"] == "reduced_electroneutral_modified_mole_fractions"
        assert record["source"]
        assert record["start_source"]
        assert record["phase_kind"] in {0, 1}
        assert len(record["composition"]) == len(checker.CHARGE_VECTOR)
        assert len(record["reduced_coordinates"]) == len(checker.CHARGE_VECTOR) - 2
        assert abs(sum(record["composition"]) - 1.0) <= checker.NORMALIZATION_TOLERANCE
        assert abs(sum(value * charge for value, charge in zip(record["composition"], checker.CHARGE_VECTOR))) <= (
            checker.CHARGE_TOLERANCE
        )
        assert record["domain_margin"] > 0.0
        assert math.isfinite(record["tpd"])
        assert math.isfinite(record["molar_volume"])
        assert record["molar_volume"] > 0.0
        assert record["tpd_backend"] == "continuous_reduced_electroneutral_coordinate_search"
        assert record["tpd_status"] in {"converged", "iteration_limit"}
        assert record["rejection_reason"] in {
            "",
            "continuous_tpd_iteration_limit",
        }
