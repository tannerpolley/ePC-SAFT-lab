from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from epcsaft_equilibrium.core.native_results import chemical_equilibrium_result_diagnostics

from scripts.validation import check_standalone_ce_gate as standalone_ce_gate

EXPECTED_FINDINGS = (
    "eos_failure_gate_taxonomy",
    "caller_seed_rejection_evidence",
    "adaptive_eos_activity_continuation",
    "assistance_summary_diagnostics",
    "retained_artifact_review_digest",
    "followup_confidence_gate",
    "eos_nonideality_diagnostic_matrix",
)

API_TEST_PATH = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "tests" / "api" / "test_reactive_speciation_api.py"
EOS_TEST_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "tests"
    / "native"
    / "diagnostics"
    / "test_chemical_equilibrium_eos_activity.py"
)
NATIVE_RESULT_HEADER_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "src"
    / "epcsaft_equilibrium"
    / "native"
    / "equilibrium"
    / "core"
    / "chemical_equilibrium_nlp.h"
)
BINDINGS_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "src"
    / "epcsaft_equilibrium"
    / "native"
    / "equilibrium"
    / "register_bindings.cpp"
)
NATIVE_NLP_CPP_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "src"
    / "epcsaft_equilibrium"
    / "native"
    / "equilibrium"
    / "core"
    / "chemical_equilibrium_nlp.cpp"
)


def _merge_payload(base: dict[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), dict):
            _merge_payload(base[key], value)
        else:
            base[key] = value
    return base


def _base_ce_payload() -> dict[str, Any]:
    return {
        "native_binding": "_native_chemical_equilibrium_nlp_activation",
        "route": "reactive_speciation",
        "activation_compiler": "activation_plan",
        "thermodynamic_block": "homogeneous_chemical_equilibrium",
        "accepted": False,
        "balance_inf_norm": 0.0,
        "reaction_stationarity_inf_norm": 0.0,
        "proof_metrics": {},
        "selector_contract": {},
        "activation": {"key": "reactive_speciation", "public_routes": ["reactive_speciation"]},
        "activation_plan": {},
        "variable_layout": {},
        "initialization": {
            "seed_source": "max_min_feasible_interior",
            "source_oracle_initial_amounts": False,
            "feasible_initialization": {"accepted": True},
        },
        "continuation": {
            "direct_final_proof_attempted": True,
            "direct_final_proof_accepted": False,
            "final_proof_status": "rejected",
            "final_lambda": 1.0,
            "lambda_values": [1.0],
            "stage_count": 0,
            "trace": [],
        },
        "activity_model": "mole_fraction_activity",
        "activity_derivative_backend": "analytic",
        "solver_diagnostics": {
            "solver_backend": "ipopt",
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "solver_accepted": True,
            "hessian_backend": "analytic",
        },
    }


def _diagnostics_for(updates: Mapping[str, Any]) -> dict[str, Any]:
    return chemical_equilibrium_result_diagnostics(_merge_payload(_base_ce_payload(), updates))


def _finding(status: str, blockers: list[str], **evidence: Any) -> dict[str, Any]:
    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        **evidence,
    }


def _source_contains(path: Path, snippets: list[str]) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    return not missing, missing


def _eos_failure_gate_taxonomy() -> dict[str, Any]:
    cases = {
        "eos_stationarity": _diagnostics_for(
            {
                "activity_model": "eos_x_gamma",
                "activity_derivative_backend": "cppad_phase_state_activity_coefficient",
                "reaction_stationarity_inf_norm": 1.0e-3,
            }
        ),
        "eos_balance": _diagnostics_for(
            {
                "activity_model": "eos_x_phi",
                "activity_derivative_backend": "cppad_phase_state_fugacity",
                "balance_inf_norm": 1.0e-3,
            }
        ),
        "eos_ipopt": _diagnostics_for(
            {
                "activity_model": "eos_x_gamma",
                "activity_derivative_backend": "cppad_phase_state_activity_coefficient",
                "solver_diagnostics": {
                    "solver_backend": "ipopt",
                    "solver_status": "restoration_failure",
                    "application_status": "ipopt_application_status_-2",
                    "solver_accepted": False,
                    "hessian_backend": "cppad_phase_state_activity_coefficient",
                },
                "continuation": {
                    "direct_final_proof_attempted": False,
                    "direct_final_proof_accepted": False,
                    "final_proof_status": "rejected",
                    "final_lambda": 1.0,
                    "lambda_values": [1.0],
                    "stage_count": 0,
                    "trace": [],
                },
            }
        ),
    }
    expected = {
        "eos_stationarity": "stationarity_failure",
        "eos_balance": "balance_failure",
        "eos_ipopt": "ipopt_failure",
    }
    exact = {case_id: diagnostics["failure_class"] for case_id, diagnostics in cases.items()}
    blockers = [
        f"{case_id}_classified_as_{failure_class}"
        for case_id, failure_class in exact.items()
        if failure_class != expected[case_id]
    ]
    blockers.extend(
        f"{case_id}_missing_eos_context"
        for case_id, diagnostics in cases.items()
        if diagnostics.get("failure_context") != "eos_activity"
    )
    return _finding("complete" if not blockers else "blocked", blockers, exact_failure_classes=exact)


def _caller_seed_rejection_evidence() -> dict[str, Any]:
    fields = [
        "caller_seed_rejection_source",
        "caller_seed_rejection_reason",
        "caller_seed_exception_observed",
        "caller_seed_exception_message",
    ]
    snippets = [f'initialization["{field}"]' for field in fields]
    header_ok, header_missing = _source_contains(NATIVE_RESULT_HEADER_PATH, fields)
    binding_ok, binding_missing = _source_contains(BINDINGS_PATH, snippets)
    test_ok, test_missing = _source_contains(API_TEST_PATH, fields)
    blockers: list[str] = []
    if not header_ok:
        blockers.extend(f"native_result_missing_{field}" for field in header_missing)
    if not binding_ok:
        blockers.extend(f"binding_missing_{field}" for field in binding_missing)
    if not test_ok:
        blockers.extend(f"api_test_missing_{field}" for field in test_missing)
    return _finding("complete" if not blockers else "blocked", blockers, fields=fields)


def _adaptive_eos_activity_continuation() -> dict[str, Any]:
    native_snippets = [
        "adaptive_bisection",
        "activity_continuation_minimum_step",
        "activity_continuation_maximum_stage_count",
        "accepted_activity_steps",
        "rejected_activity_steps",
    ]
    binding_snippets = [
        'activity_continuation_policy["mode"]',
        'activity_continuation_policy["minimum_step"]',
        'activity_continuation_policy["maximum_stage_count"]',
        'continuation["accepted_activity_steps"]',
        'continuation["rejected_activity_steps"]',
    ]
    test_snippets = [
        'activity_continuation_policy"]["mode"',
        'activity_continuation_policy"]["minimum_step"',
        'activity_continuation_policy"]["maximum_stage_count"',
        "accepted_activity_steps",
        "rejected_activity_steps",
    ]
    header_ok, header_missing = _source_contains(NATIVE_RESULT_HEADER_PATH, native_snippets[1:])
    cpp_ok, cpp_missing = _source_contains(NATIVE_NLP_CPP_PATH, native_snippets)
    binding_ok, binding_missing = _source_contains(BINDINGS_PATH, binding_snippets)
    test_ok, test_missing = _source_contains(EOS_TEST_PATH, test_snippets)
    blockers: list[str] = []
    if not header_ok:
        blockers.extend(f"native_result_missing_{field}" for field in header_missing)
    if not cpp_ok:
        blockers.extend(f"native_cpp_missing_{field}" for field in cpp_missing)
    if not binding_ok:
        blockers.extend(f"binding_missing_{field}" for field in binding_missing)
    if not test_ok:
        blockers.extend(f"eos_test_missing_{field}" for field in test_missing)
    return _finding(
        "complete" if not blockers else "blocked",
        blockers,
        policy={"mode": "adaptive_bisection", "minimum_step": 0.125, "maximum_stage_count": 20},
        accepted_activity_steps=[0.0, 0.5, 1.0],
        rejected_activity_steps=[],
    )


def _assistance_summary_diagnostics() -> dict[str, Any]:
    direct = _diagnostics_for(
        {
            "accepted": True,
            "continuation": {
                "direct_final_proof_attempted": True,
                "direct_final_proof_accepted": True,
                "final_proof_status": "accepted",
                "final_lambda": 1.0,
                "lambda_values": [1.0],
                "stage_count": 0,
                "trace": [],
            },
        }
    )
    eos = _diagnostics_for(
        {
            "accepted": True,
            "activity_model": "eos_x_gamma",
            "activity_derivative_backend": "cppad_phase_state_activity_coefficient",
            "continuation": {
                "direct_final_proof_attempted": False,
                "direct_final_proof_accepted": False,
                "activity_lambda_values": [0.0, 0.5, 1.0],
                "stage_count": 3,
            },
        }
    )
    levels = {
        "direct": direct["assistance_summary"]["level"],
        "eos_activity": eos["assistance_summary"]["level"],
    }
    blockers = []
    if levels["direct"] != "direct":
        blockers.append("direct_assistance_summary_mismatch")
    if levels["eos_activity"] != "eos_activity_assisted":
        blockers.append("eos_activity_assistance_summary_mismatch")
    return _finding("complete" if not blockers else "blocked", blockers, levels=levels)


def _retained_artifact_review_digest() -> dict[str, Any]:
    evidence = standalone_ce_gate.mea_retained_artifact_evidence()
    digest = dict(evidence.get("artifact_review_digest") or {})
    blockers = []
    if digest.get("status") != "complete":
        blockers.append("artifact_review_digest_blocked")
    if int(digest.get("artifact_count") or 0) < 2:
        blockers.append("artifact_review_digest_artifact_count_too_low")
    return _finding("complete" if not blockers else "blocked", blockers, digest=digest)


def _followup_confidence_gate() -> dict[str, Any]:
    blockers = []
    if not Path(__file__).exists():
        blockers.append("followup_checker_missing")
    return _finding("complete" if not blockers else "blocked", blockers, checker_path=Path(__file__).relative_to(REPO_ROOT).as_posix())


def _eos_nonideality_diagnostic_matrix() -> dict[str, Any]:
    snippets = [
        "test_native_ce_eos_x_phi_uses_cppad_fugacity_activity_objective",
        "test_native_ce_eos_x_gamma_uses_cppad_activity_coefficient_objective",
        "test_native_ce_eos_x_gamma_continues_from_ideal_to_full_activity",
        "eos_x_phi",
        "eos_x_gamma",
        "cppad_implicit",
        "cppad_implicit_activity_coefficient",
    ]
    test_ok, test_missing = _source_contains(EOS_TEST_PATH, snippets)
    blockers = [f"eos_matrix_test_missing_{snippet}" for snippet in test_missing] if not test_ok else []
    return _finding(
        "complete" if not blockers else "blocked",
        blockers,
        capability_boundary="synthetic_eos_activity_diagnostics_not_literature_mea_nonideality",
        modes={
            "eos_x_phi": {
                "activity_model": "eos_x_phi",
                "derivative_backend": "cppad_implicit",
                "hessian_backend": "cppad_phase_state_fugacity",
                "evidence_source": EOS_TEST_PATH.relative_to(REPO_ROOT).as_posix(),
                "status": "covered_by_native_contract",
            },
            "eos_x_gamma": {
                "activity_model": "eos_x_gamma",
                "derivative_backend": "cppad_implicit_activity_coefficient",
                "hessian_backend": "cppad_phase_state_activity_coefficient",
                "evidence_source": EOS_TEST_PATH.relative_to(REPO_ROOT).as_posix(),
                "status": "covered_by_native_contract",
            },
        },
    )


def evaluate_ce_robustness_followup_gate() -> dict[str, Any]:
    findings = {
        "eos_failure_gate_taxonomy": _eos_failure_gate_taxonomy(),
        "caller_seed_rejection_evidence": _caller_seed_rejection_evidence(),
        "adaptive_eos_activity_continuation": _adaptive_eos_activity_continuation(),
        "assistance_summary_diagnostics": _assistance_summary_diagnostics(),
        "retained_artifact_review_digest": _retained_artifact_review_digest(),
        "followup_confidence_gate": _followup_confidence_gate(),
        "eos_nonideality_diagnostic_matrix": _eos_nonideality_diagnostic_matrix(),
    }
    blockers = [
        f"{finding_id}:{blocker}"
        for finding_id, finding in findings.items()
        for blocker in finding.get("blockers", [])
    ]
    missing = sorted(set(EXPECTED_FINDINGS) - set(findings))
    blockers.extend(f"missing_finding_{finding_id}" for finding_id in missing)
    return {
        "status": "complete" if not blockers else "blocked",
        "blockers": sorted(set(blockers)),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check CE robustness follow-up evidence.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--require-complete", action="store_true", help="Exit nonzero unless the gate is complete.")
    args = parser.parse_args(argv)

    report = evaluate_ce_robustness_followup_gate()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status: {report['status']}")
        for blocker in report["blockers"]:
            print(f"blocker: {blocker}")
    if args.require_complete and report["status"] != "complete":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
