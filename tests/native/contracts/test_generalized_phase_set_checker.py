from __future__ import annotations

from typing import Any

from scripts.validation import check_generalized_phase_set as checker


def _record(index: int, *, selected: bool, composition: list[float] | None = None) -> dict[str, Any]:
    return {
        "record_id": f"{'selected' if selected else 'rejected'}-{index}",
        "phase_count": 3,
        "phase_index": index,
        "phase_kind": "liquid",
        "phase_role": "accepted_phase" if selected else "candidate_phase",
        "source": "deterministic_tpd_candidate_screening",
        "phase_amount_total": 0.2,
        "phase_fraction": 0.2,
        "volume": 1.0e-5,
        "density": 20_000.0,
        "composition": composition or [0.2, 0.3, 0.5],
        "objective": -1.0,
        "tpd": -1.0e-4,
        "feasibility_status": "accepted" if selected else "candidate_generated",
        "selection_status": "selected" if selected else "rejected",
        "rejection_reason": "accepted" if selected else "duplicate_or_collapsed",
        "phase_set_status": "phase_set_certified",
        "mass_balance_feasible": True,
        "stability_accepted": True,
        "candidate_completeness_accepted": True,
    }


def _payload(*, records: list[dict[str, Any]] | None = None, public_routes: list[str] | None = None) -> dict[str, Any]:
    default_records = [
        _record(0, selected=True, composition=[0.2, 0.3, 0.5]),
        _record(1, selected=True, composition=[0.3, 0.3, 0.4]),
        _record(2, selected=True, composition=[0.4, 0.2, 0.4]),
        _record(3, selected=False),
    ]
    return {
        "public_routes": public_routes or ["flash", "lle"],
        "postsolve": {
            "phase_count": 3,
            "phase_set_status": "phase_set_certified",
            "phase_set_mass_balance_feasible": True,
            "candidate_completeness_accepted": True,
            "stability_accepted": True,
            "phase_distance": 0.1,
            "phase_set_records": records if records is not None else default_records,
        },
    }


def test_checker_accepts_complete_internal_three_phase_records() -> None:
    result = checker.evaluate_payload(_payload())

    assert result["complete"] is True
    assert result["blockers"] == []
    assert result["record_summary"] == {"total": 4, "selected": 3, "rejected": 1}


def test_checker_rejects_missing_records() -> None:
    result = checker.evaluate_payload(_payload(records=[]))

    assert result["complete"] is False
    assert "missing_phase_set_records" in result["blockers"]


def test_checker_rejects_malformed_rows() -> None:
    bad_record = _record(0, selected=True)
    bad_record.pop("composition")

    result = checker.evaluate_payload(_payload(records=[bad_record]))

    assert result["complete"] is False
    assert "malformed_phase_set_record:composition" in result["blockers"]


def test_checker_rejects_infeasible_or_collapsed_phase_sets() -> None:
    records = [
        _record(0, selected=True, composition=[0.2, 0.3, 0.5]),
        _record(1, selected=True, composition=[0.2, 0.3, 0.5]),
        _record(2, selected=True, composition=[0.1, 0.2, 0.7]),
        _record(3, selected=False),
    ]

    result = checker.evaluate_payload(_payload(records=records))

    assert result["complete"] is False
    assert "duplicate_selected_phase_compositions" in result["blockers"]


def test_checker_rejects_public_route_exposure() -> None:
    result = checker.evaluate_payload(_payload(public_routes=["flash", "neutral_multiphase_nonassoc"]))

    assert result["complete"] is False
    assert "neutral_multiphase_public_route_exposed" in result["blockers"]


def test_checker_rejects_lower_free_energy_omitted_candidate_without_distinct_diagnostic() -> None:
    records = [
        _record(0, selected=True, composition=[0.2, 0.3, 0.5]),
        _record(1, selected=True, composition=[0.3, 0.3, 0.4]),
        _record(2, selected=True, composition=[0.4, 0.2, 0.4]),
        _record(3, selected=False, composition=[0.1, 0.1, 0.8]),
    ]
    for selected in records[:3]:
        selected["objective"] = 0.0
        selected["tpd"] = 0.0
    records[3]["objective"] = -1.0
    records[3]["tpd"] = -1.0
    records[3]["feasibility_status"] = "converged"
    records[3]["rejection_reason"] = "not_selected_by_generalized_phase_set_gate"

    result = checker.evaluate_payload(_payload(records=records))

    assert result["complete"] is False
    assert "lower_free_energy_omitted_candidate" in result["blockers"]


def test_checker_rejects_uncertified_phase_set_records_with_named_blocker() -> None:
    records = [_record(0, selected=True), _record(1, selected=True), _record(2, selected=True), _record(3, selected=False)]
    for record in records:
        record["phase_set_status"] = "stability_uncertified"
        record["stability_accepted"] = False
        record["candidate_completeness_accepted"] = False

    payload = _payload(records=records)
    payload["postsolve"]["phase_set_status"] = "stability_uncertified"
    payload["postsolve"]["stability_accepted"] = False
    payload["postsolve"]["candidate_completeness_accepted"] = False

    result = checker.evaluate_payload(payload)

    assert result["complete"] is False
    assert "uncertified_phase_set_record" in result["blockers"]
