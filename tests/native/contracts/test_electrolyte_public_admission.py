from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_public_admission.py"
REQUIRED_CLI_FLAGS = [
    "--json",
    "--require-source-gate",
    "--require-readiness-gate",
    "--require-tpd-gate",
    "--require-held2-discovery",
    "--require-stage-iii",
    "--require-postsolve-certification",
    "--require-public-admission",
    "--require-complete",
]
PUBLIC_STATE_MUTATIONS = [
    (("electrolyte_lle", "present"), False, "electrolyte_lle_activation_row_missing"),
    (
        ("electrolyte_lle", "production_exposed"),
        False,
        "electrolyte_lle_public_route_not_exposed",
    ),
    (
        ("electrolyte_lle", "exposure_status"),
        "declared_not_exposed",
        "electrolyte_lle_exposure_status_mismatch",
    ),
    (
        ("electrolyte_lle", "public_routes"),
        [],
        "electrolyte_lle_public_route_mismatch",
    ),
    (
        ("electrolyte_lle", "proof_routes"),
        [],
        "electrolyte_lle_proof_route_mismatch",
    ),
    (("capabilities_public_routes",), [], "electrolyte_lle_capability_public_route_missing"),
    (("production_families",), [], "electrolyte_lle_production_family_missing"),
    (("public_route_family_map",), {}, "electrolyte_lle_family_map_mismatch"),
]


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_public_admission", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def checker() -> Any:
    return _load_checker()


def _closed_payload(checker: Any) -> dict[str, Any]:
    payload = checker.minimal_complete_payload_for_tests()
    public_state = checker._public_route_state_payload()
    payload["public_route_state"] = public_state
    payload["registry_evidence"] = checker._registry_evidence_payload(public_state)
    payload["parent_closeout"] = checker._parent_closeout_payload(public_state)
    payload["shared_certification"] = checker._shared_certification_payload(payload)
    return payload


def test_current_activation_is_an_explicit_closed_repair_target(checker: Any) -> None:
    public_state = checker._public_route_state_payload()

    assert public_state["electrolyte_lle"] == {
        "present": True,
        "production_exposed": False,
        "exposure_status": "declared_not_exposed",
        "public_routes": [],
        "proof_routes": [],
    }
    assert checker._registry_evidence_payload(public_state)["public_route_status"] == "closed_repair_target"
    assert checker._parent_closeout_payload(public_state) == {
        "parent_issue": 191,
        "status": "blocked_pending_readmission",
        "remaining_m4_blockers": [
            "native_selector_integration",
            "current_public_route_absent",
        ],
        "next_gate": "M4 electrolyte readmission",
    }


def test_closed_state_cannot_complete_admission_or_parent_closeout(checker: Any) -> None:
    payload = _closed_payload(checker)

    result = checker.evaluate_payload(
        payload,
        require_public_admission=True,
        require_parent_closeout=True,
    )

    assert result["complete"] is False
    assert result["registry_evidence"]["public_route_status"] == "closed_repair_target"
    assert result["parent_closeout"]["status"] == "blocked_pending_readmission"
    assert result["shared_certification"]["shared_contract_level"] == "internal_repair_evidence"
    assert result["shared_certification"]["status"] == "blocked"
    assert "electrolyte_lle_public_route_not_exposed" in result["blockers"]
    assert "electrolyte_lle_public_route_mismatch" in result["blockers"]
    assert "electrolyte_lle_proof_route_mismatch" in result["blockers"]
    assert "parent_issue_m4_blockers_remain" in result["blockers"]


def test_synthetic_future_admission_can_complete_only_as_a_fully_aligned_state(checker: Any) -> None:
    payload = checker.minimal_complete_payload_for_tests()

    result = checker.evaluate_payload(
        payload,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_held2_stage_ii=True,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_admission=True,
        require_parent_closeout=True,
    )

    assert result["complete"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["registry_evidence"]["public_route_status"] == "public_route_open"
    assert result["parent_closeout"]["status"] == "ready_for_close"
    assert result["shared_certification"]["shared_contract_level"] == "production_public_route"
    assert result["shared_certification"]["status"] == "accepted"


@pytest.mark.parametrize(
    ("state_path", "replacement", "expected_blocker"),
    PUBLIC_STATE_MUTATIONS,
)
def test_synthetic_future_activation_mutations_fail_closed(
    checker: Any,
    state_path: tuple[str, ...],
    replacement: Any,
    expected_blocker: str,
) -> None:
    payload = checker.minimal_complete_payload_for_tests()
    target = payload["public_route_state"]
    for key in state_path[:-1]:
        target = target[key]
    target[state_path[-1]] = replacement

    result = checker.evaluate_payload(payload, require_public_admission=True)

    assert result["complete"] is False
    assert expected_blocker in result["blockers"]


@pytest.mark.parametrize(
    ("state_path", "replacement", "_expected_blocker"),
    PUBLIC_STATE_MUTATIONS,
)
def test_registry_and_parent_views_never_report_a_half_open_future_state(
    checker: Any,
    state_path: tuple[str, ...],
    replacement: Any,
    _expected_blocker: str,
) -> None:
    public_state = copy.deepcopy(checker.minimal_complete_payload_for_tests()["public_route_state"])
    target = public_state
    for key in state_path[:-1]:
        target = target[key]
    target[state_path[-1]] = replacement

    assert checker._registry_evidence_payload(public_state)["public_route_status"] == "closed_repair_target"
    assert checker._parent_closeout_payload(public_state)["status"] == "blocked_pending_readmission"


@pytest.mark.parametrize(
    ("gate", "expected_blocker"),
    [
        ("source_gate", "source_gate_incomplete"),
        ("held2_readiness_gate", "readiness_gate_incomplete"),
        ("electrolyte_tpd_gate", "tpd_gate_incomplete"),
        ("held2_phase_discovery", "held2_phase_discovery_incomplete"),
        ("electrolyte_stage_iii_refinement", "stage_iii_refinement_incomplete"),
        ("electrolyte_postsolve_certification", "postsolve_certification_incomplete"),
    ],
)
def test_synthetic_future_admission_rejects_incomplete_prerequisite_gates(
    checker: Any,
    gate: str,
    expected_blocker: str,
) -> None:
    payload = checker.minimal_complete_payload_for_tests()
    payload[gate]["complete"] = False
    payload[gate]["status"] = "incomplete"

    result = checker.evaluate_payload(
        payload,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_admission=True,
    )

    assert result["complete"] is False
    assert expected_blocker in result["blockers"]


def test_synthetic_future_admission_rejects_missing_or_invalid_shared_certification(checker: Any) -> None:
    payload = checker.minimal_complete_payload_for_tests()
    missing = copy.deepcopy(payload)
    missing.pop("shared_certification")
    raw_single_ion = copy.deepcopy(payload)
    raw_single_ion["shared_certification"]["raw_single_ion_equality_used"] = True

    missing_result = checker.evaluate_payload(missing, require_public_admission=True)
    raw_single_ion_result = checker.evaluate_payload(raw_single_ion, require_public_admission=True)

    assert "electrolyte_shared_certification_missing" in missing_result["blockers"]
    assert "electrolyte_shared_certification_raw_single_ion_equality_used" in raw_single_ion_result["blockers"]


def test_completion_cli_emits_valid_closed_json_and_exits_one(
    checker: Any,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    closed = checker.evaluate_payload(
        _closed_payload(checker),
        require_public_admission=True,
        require_parent_closeout=True,
    )
    monkeypatch.setattr(checker, "evaluate_public_admission", lambda *args, **kwargs: closed)

    return_code = checker.main(REQUIRED_CLI_FLAGS)
    output = json.loads(capsys.readouterr().out)

    assert return_code == 1
    assert output["complete"] is False
    assert output["public_route_state"]["electrolyte_lle"]["production_exposed"] is False
    assert output["public_route_state"]["electrolyte_lle"]["public_routes"] == []
    assert output["public_route_state"]["electrolyte_lle"]["proof_routes"] == []
    assert output["registry_evidence"]["public_route_status"] == "closed_repair_target"
    assert output["parent_closeout"]["status"] == "blocked_pending_readmission"
    assert output["shared_certification"]["shared_contract_level"] == "internal_repair_evidence"
    assert output["shared_certification"]["status"] == "blocked"
