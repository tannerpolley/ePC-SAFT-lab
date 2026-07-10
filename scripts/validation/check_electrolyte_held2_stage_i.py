from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.validation import check_electrolyte_held2_continuous_tpd

ALGORITHM_SCOPE = "held2_stage_i_electrolyte_stability_certificate_only"
STABILITY_CERTIFICATE = "electrolyte_held2_stage_i_stability_certificate"
STAGE_I_TPD_FLOOR = 1.0e-10
CHARGE_TOLERANCE = check_electrolyte_held2_continuous_tpd.CHARGE_TOLERANCE
NORMALIZATION_TOLERANCE = check_electrolyte_held2_continuous_tpd.NORMALIZATION_TOLERANCE
COORDINATE_BASIS = check_electrolyte_held2_continuous_tpd.COORDINATE_BASIS


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _continuous_tpd_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    if "electrolyte_held2_continuous_tpd" in payload:
        return dict(payload["electrolyte_held2_continuous_tpd"])
    return dict(payload)


def _finite_float(value: Any, default: float = math.inf) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _accepted_trial_phases(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(record)
        for record in records
        if record.get("accepted") is True and str(record.get("tpd_status", "")) == "converged"
    ]


def _suspect_trial_phases(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(record)
        for record in records
        if record.get("accepted") is not True or str(record.get("tpd_status", "")) != "converged"
    ]


def _negative_trial_phases(accepted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(record)
        for record in accepted
        if math.isfinite(_finite_float(record.get("tpd"))) and _finite_float(record.get("tpd")) < -STAGE_I_TPD_FLOOR
    ]


def _minimum_tpd(accepted: list[dict[str, Any]], continuous: dict[str, Any]) -> float:
    values = [_finite_float(record.get("tpd")) for record in accepted]
    finite_values = [value for value in values if math.isfinite(value)]
    if finite_values:
        return min(finite_values)
    return _finite_float(continuous.get("continuous_tpd_min"))


def _residual_and_bound_summary(records: list[dict[str, Any]], continuous: dict[str, Any]) -> dict[str, Any]:
    max_charge = max((_finite_float(record.get("charge_residual")) for record in records), default=math.inf)
    max_normalization = max((_finite_float(record.get("normalization_residual")) for record in records), default=math.inf)
    min_domain = min((_finite_float(record.get("domain_margin"), default=-math.inf) for record in records), default=-math.inf)
    reported_max_charge = _finite_float(continuous.get("max_charge_residual"))
    reported_max_normalization = _finite_float(continuous.get("max_normalization_residual"))
    reported_min_domain = _finite_float(continuous.get("min_domain_margin"), default=-math.inf)
    if math.isfinite(reported_max_charge):
        max_charge = max(max_charge, reported_max_charge)
    if math.isfinite(reported_max_normalization):
        max_normalization = max(max_normalization, reported_max_normalization)
    if math.isfinite(reported_min_domain):
        min_domain = min(min_domain, reported_min_domain)
    return {
        "charge_tolerance": CHARGE_TOLERANCE,
        "normalization_tolerance": NORMALIZATION_TOLERANCE,
        "domain_margin_floor": 0.0,
        "tpd_floor": STAGE_I_TPD_FLOOR,
        "max_charge_residual": max_charge,
        "max_normalization_residual": max_normalization,
        "min_domain_margin": min_domain,
        "retained_fields": [
            "tpd",
            "tpd_status",
            "tpd_iteration_count",
            "tpd_step_final",
            "charge_residual",
            "normalization_residual",
            "domain_margin",
            "reduced_coordinates",
            "neutral_closure_species",
            "eliminated_charged_species",
        ],
    }


def _stage_ii_handoff(
    *,
    classification: str,
    negative_tpd_trial_phases: list[dict[str, Any]],
    minimum_tpd: float,
) -> dict[str, Any]:
    if classification == "unstable_negative_tpd":
        return {
            "status": "ready_for_stage_ii_discovery",
            "source": "stage_i_negative_tpd_trial_phases",
            "coordinate_basis": COORDINATE_BASIS,
            "tpd_floor": STAGE_I_TPD_FLOOR,
            "minimum_tpd": minimum_tpd,
            "trial_phase_count": len(negative_tpd_trial_phases),
            "trial_phases": negative_tpd_trial_phases,
        }
    if classification == "stable_no_negative_tpd":
        return {
            "status": "stable_feed_no_stage_ii_handoff",
            "source": "stage_i_no_negative_tpd_certificate",
            "coordinate_basis": COORDINATE_BASIS,
            "tpd_floor": STAGE_I_TPD_FLOOR,
            "minimum_tpd": minimum_tpd,
            "trial_phase_count": 0,
            "trial_phases": [],
        }
    return {
        "status": "blocked_by_stage_i_certificate",
        "source": "stage_i_incomplete_or_suspect_start_evidence",
        "coordinate_basis": COORDINATE_BASIS,
        "tpd_floor": STAGE_I_TPD_FLOOR,
        "minimum_tpd": minimum_tpd,
        "trial_phase_count": 0,
        "trial_phases": [],
    }


def _classify_stage_i(continuous_payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    continuous = _continuous_tpd_evidence(continuous_payload)
    upstream_complete = continuous_payload.get("complete", True) is True and continuous.get("status") == "complete"
    upstream_blockers = [str(item) for item in continuous_payload.get("blockers", [])]
    upstream_blockers.extend(str(item) for item in continuous.get("blockers", []))
    records = [dict(record) for record in continuous.get("start_records", [])]
    accepted = _accepted_trial_phases(records)
    suspect = _suspect_trial_phases(records)
    negative = _negative_trial_phases(accepted)
    minimum_tpd = _minimum_tpd(accepted, continuous)

    blockers: list[str] = []
    continuous_status = str(continuous.get("continuous_tpd_status", ""))
    if not upstream_complete or upstream_blockers:
        blockers.append("stage_i_continuous_tpd_incomplete")
    if continuous.get("phase_discovery_backend") != "continuous_reduced_electroneutral_tpd_minimization":
        blockers.append("stage_i_continuous_tpd_backend_mismatch")
    if continuous.get("stability_certificate") != "electrolyte_continuous_reduced_electroneutral_tpd_minimizer":
        blockers.append("stage_i_continuous_tpd_certificate_mismatch")
    if continuous_status not in {"converged", "complete_with_rejected_starts"}:
        blockers.append("stage_i_continuous_tpd_status_incomplete")
    if not records:
        blockers.append("stage_i_start_records_missing")
    if not accepted:
        blockers.append("stage_i_accepted_start_missing")
    if not math.isfinite(minimum_tpd):
        blockers.append("stage_i_minimum_tpd_nonfinite")

    negative_tpd_found = bool(negative)
    if not records or not accepted or "stage_i_continuous_tpd_incomplete" in blockers:
        classification = "incomplete_continuous_tpd"
        certificate_status = "incomplete"
    elif negative_tpd_found:
        classification = "unstable_negative_tpd"
        certificate_status = "complete"
    elif suspect:
        classification = "suspect_start_incomplete"
        certificate_status = "incomplete"
        blockers.append("stage_i_suspect_starts_block_stable_certificate")
    else:
        classification = "stable_no_negative_tpd"
        certificate_status = "complete"

    no_negative = {
        "retained": classification == "stable_no_negative_tpd",
        "minimum_tpd": minimum_tpd,
        "tpd_floor": STAGE_I_TPD_FLOOR,
        "accepted_start_count": len(accepted),
        "governed_start_count": len(records),
    }
    if classification != "stable_no_negative_tpd":
        no_negative["retained"] = False

    suspect_status = "suspect_starts_absent"
    if suspect and negative_tpd_found:
        suspect_status = "suspect_starts_retained_with_decisive_negative_tpd"
    elif suspect:
        suspect_status = "suspect_starts_block_stable_certificate"

    stage_ii_handoff = _stage_ii_handoff(
        classification=classification,
        negative_tpd_trial_phases=negative,
        minimum_tpd=minimum_tpd,
    )
    evidence = {
        "algorithm_scope": ALGORITHM_SCOPE,
        "algorithm_source": continuous.get("algorithm_source"),
        "stability_certificate": STABILITY_CERTIFICATE,
        "continuous_tpd_certificate": continuous.get("stability_certificate"),
        "phase_discovery_backend": continuous.get("phase_discovery_backend"),
        "continuous_tpd_status": continuous_status,
        "continuous_tpd_min": minimum_tpd,
        "stage_i_classification": classification,
        "certificate_status": certificate_status,
        "negative_tpd_found": negative_tpd_found,
        "negative_tpd_trial_phases": negative,
        "no_negative_tpd_certificate": no_negative,
        "governed_start_count": len(records),
        "accepted_start_count": len(accepted),
        "suspect_start_count": len(suspect),
        "suspect_start_status": suspect_status,
        "suspect_start_records": suspect,
        "start_records": records,
        "residual_and_bound_summary": _residual_and_bound_summary(records, continuous),
        "stage_ii_handoff_ready": classification == "unstable_negative_tpd",
        "stage_ii_handoff": stage_ii_handoff,
        "replay_payload": {
            "status": "replayable",
            "source": "stage_i_certificate_payload",
            "stage_i_classification": classification,
            "certificate_status": certificate_status,
            "tpd_floor": STAGE_I_TPD_FLOOR,
            "start_records": records,
            "negative_tpd_trial_phases": negative,
            "no_negative_tpd_certificate": no_negative,
        },
        "public_route_admission_status": "separate_public_admission_gate",
        "stage_statuses": {
            "stage_i_certificate": classification,
            "stage_ii_discovery": "pending_held2_stage_ii_discovery",
            "stage_iii_refinement": "pending_ipopt_refinement",
            "public_route_admission": "separate_public_admission_gate",
        },
        "native_freshness_receipt": continuous.get("native_freshness_receipt", {}),
    }
    if certificate_status != "complete":
        blockers.append(f"stage_i_certificate_{certificate_status}")
    blockers.extend(upstream_blockers)
    return _jsonable(evidence), sorted(set(blockers))


def evaluate_stage_i_payload(
    continuous_payload: dict[str, Any],
    *,
    require_continuous_tpd: bool = False,
    require_complete: bool = False,
) -> dict[str, Any]:
    evidence, blockers = _classify_stage_i(continuous_payload)
    continuous = _continuous_tpd_evidence(continuous_payload)
    if require_continuous_tpd and continuous.get("status") != "complete":
        blockers.append("stage_i_continuous_tpd_incomplete")
    if require_complete and evidence.get("certificate_status") != "complete":
        blockers.append("stage_i_certificate_incomplete")
    result = {
        "checker": "electrolyte_held2_stage_i",
        "complete": not blockers,
        "blockers": sorted(set(blockers)),
        "source_gate": continuous_payload.get("source_gate", {}),
        "held2_readiness_gate": continuous_payload.get("held2_readiness_gate", {}),
        "electrolyte_held2_continuous_tpd": continuous,
        "electrolyte_held2_stage_i": evidence,
    }
    return _jsonable(result)


def evaluate_stage_i(
    *,
    require_continuous_tpd: bool = False,
    require_complete: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    command = checker_command or [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_held2_stage_i.py",
        "--json",
    ]
    effective_require_continuous = require_continuous_tpd or require_complete
    continuous_payload = check_electrolyte_held2_continuous_tpd.evaluate_continuous_tpd(
        require_native_continuous_tpd=effective_require_continuous,
        require_complete=effective_require_continuous,
        checker_command=command,
    )
    return evaluate_stage_i_payload(
        continuous_payload,
        require_continuous_tpd=effective_require_continuous,
        require_complete=require_complete,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate electrolyte HELD2 Stage I stability certificate.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--require-continuous-tpd", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    command = ["uv", "run", "--no-sync", "python", "scripts/validation/check_electrolyte_held2_stage_i.py"]
    if args.json:
        command.append("--json")
    if args.require_continuous_tpd:
        command.append("--require-continuous-tpd")
    if args.require_complete:
        command.append("--require-complete")
    payload = evaluate_stage_i(
        require_continuous_tpd=args.require_continuous_tpd,
        require_complete=args.require_complete,
        checker_command=command,
    )
    if args.require_complete:
        receipt = payload.get("electrolyte_held2_stage_i", {}).get("native_freshness_receipt", {})
        if receipt:
            from scripts.validation import native_freshness

            try:
                native_freshness.require_equilibrium_native_fresh(dict(receipt))
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload["complete"]:
        print("Electrolyte HELD2 Stage I stability certificate validation passed.")
    else:
        print("Electrolyte HELD2 Stage I stability certificate validation failed:")
        for blocker in payload["blockers"]:
            print(f"- {blocker}")
    return 0 if payload["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
