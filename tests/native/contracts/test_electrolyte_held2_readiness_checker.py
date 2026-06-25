from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_held2_readiness.py"


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_held2_readiness", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _complete_payload() -> dict[str, Any]:
    return {
        "checker": "electrolyte_held2_readiness_gate",
        "case_label": "Khudaida 2026 electrolyte LLE",
        "source_gate": {
            "checker": "electrolyte_gfpe_closed_admission_gate",
            "complete": True,
            "blockers": [],
        },
        "reduced_basis": {
            "status": "verified_exact_charge_neutral_lift",
            "basis_species": ["H2O", "Ethanol", "Butanol", "NaCl"],
            "native_species": ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"],
            "charge_vector": [0.0, 0.0, 0.0, 1.0, -1.0],
            "lift_matrix_row_major": [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            "max_abs_charge_balance": 0.0,
            "charge_balance_threshold": 1.0e-10,
        },
        "born_ssm_ds_exactness": {
            "status": "verified_cppad_born_ssm_ds_receipts",
            "backend": "cppad",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "composition_derivative_backend": "cppad",
            "finite_composition_derivatives": True,
            "finite_fugacity_derivatives": True,
            "finite_activity_derivatives": True,
            "finite_parameter_derivatives": True,
            "parameter_families": ["d_born", "f_solv"],
        },
        "held2_readiness": {
            "status": "readiness_prerequisites_verified",
            "readiness_only": True,
            "full_held2_claimed": False,
            "pending_gates": [
                "electrolyte_tpd",
                "held2_dual_phase_discovery",
                "electrolyte_stage_iii_refinement",
                "postsolve_electrolyte_phase_set_certification",
                "public_electrolyte_route_admission",
            ],
        },
        "public_route_state": {
            "electrolyte_lle": {
                "present": True,
                "production_exposed": False,
                "public_routes": [],
                "proof_routes": [],
            },
            "capabilities_public_routes": ["bubble_pressure", "dew_pressure", "lle"],
            "production_families": ["bubble_dew_derived_routes", "neutral_lle"],
            "route_derivative_evidence_quantities": [
                "neutral_lle",
                "associating_neutral_lle_gross_2002_public_exact_hessian",
            ],
        },
    }


def test_complete_payload_records_readiness_without_public_route_claim() -> None:
    checker = _load_checker()

    result = checker.evaluate_payload(
        _complete_payload(),
        require_source_gate=True,
        require_reduced_basis=True,
        require_born_ssm_ds=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is True
    assert result["blockers"] == []
    assert result["held2_readiness"]["readiness_only"] is True
    assert result["held2_readiness"]["full_held2_claimed"] is False
    assert "electrolyte_tpd" in result["held2_readiness"]["pending_gates"]


@pytest.mark.parametrize(
    ("mutate", "expected_blocker"),
    [
        (
            lambda payload: payload["source_gate"].update({"complete": False, "blockers": ["source_gate_failed"]}),
            "electrolyte_source_gate_incomplete",
        ),
        (
            lambda payload: payload["reduced_basis"].update({"max_abs_charge_balance": 1.0e-7}),
            "electrolyte_reduced_basis_charge_balance_exceeds_threshold",
        ),
        (
            lambda payload: payload["born_ssm_ds_exactness"].update({"status": "missing"}),
            "born_ssm_ds_exactness_missing",
        ),
        (
            lambda payload: payload["held2_readiness"].update({"full_held2_claimed": True}),
            "full_held2_claimed_by_readiness_gate",
        ),
        (
            lambda payload: payload["public_route_state"]["electrolyte_lle"].update({"production_exposed": True}),
            "electrolyte_lle_public_route_exposed",
        ),
    ],
)
def test_evaluate_payload_fails_closed_for_missing_readiness_evidence(
    mutate: Callable[[dict[str, Any]], None],
    expected_blocker: str,
) -> None:
    checker = _load_checker()
    payload = copy.deepcopy(_complete_payload())
    mutate(payload)

    result = checker.evaluate_payload(
        payload,
        require_source_gate=True,
        require_reduced_basis=True,
        require_born_ssm_ds=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert expected_blocker in result["blockers"]


def test_evaluate_readiness_uses_real_source_gate_and_provider_receipts() -> None:
    checker = _load_checker()

    result = checker.evaluate_readiness(
        require_source_gate=True,
        require_reduced_basis=True,
        require_born_ssm_ds=True,
    )

    assert result["complete"] is True
    assert result["source_gate"]["complete"] is True
    assert result["reduced_basis"]["max_abs_charge_balance"] <= 1.0e-10
    assert result["born_ssm_ds_exactness"]["backend"] == "cppad"
    assert result["born_ssm_ds_exactness"]["finite_composition_derivatives"] is True
    assert result["born_ssm_ds_exactness"]["finite_parameter_derivatives"] is True
    assert result["held2_readiness"]["readiness_only"] is True
    assert result["public_route_state"]["electrolyte_lle"]["production_exposed"] is True


def test_cli_requires_complete_readiness_evidence() -> None:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-source-gate",
            "--require-reduced-basis",
            "--require-born-ssm-ds",
            "--require-complete",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["complete"] is True
    assert payload["blockers"] == []
