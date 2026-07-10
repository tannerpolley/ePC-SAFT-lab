from __future__ import annotations

import argparse
import json
import math
import os
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

from scripts.validation import check_electrolyte_gfpe_gate, check_electrolyte_held2_readiness

NATIVE_SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
CHARGE_VECTOR = np.asarray([0.0, 0.0, 0.0, 1.0, -1.0], dtype=float)
CHARGE_TOLERANCE = 1.0e-8
TPD_TOLERANCE = 1.0e-8
CANDIDATE_MASS_BALANCE_TOLERANCE = 1.0e-8
REMAINING_HELD2_GATES = [
    "held2_dual_phase_discovery",
    "electrolyte_stage_iii_refinement",
    "postsolve_electrolyte_phase_set_certification",
    "public_electrolyte_route_admission",
]


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _source_gate_payload(
    case_dir: Path,
    checker_command: list[str] | None,
    *,
    require_public_routes_closed: bool,
) -> dict[str, Any]:
    command = checker_command or [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_tpd_gate.py",
    ]
    return check_electrolyte_gfpe_gate.evaluate_case_dir(
        case_dir,
        require_source_data=True,
        require_parameter_bundle=True,
        require_native_diagnostics=True,
        require_public_routes_closed=require_public_routes_closed,
        checker_command=command,
    )


def _held2_readiness_payload(case_dir: Path, *, require_public_routes_closed: bool) -> dict[str, Any]:
    return check_electrolyte_held2_readiness.evaluate_readiness(
        case_dir,
        require_source_gate=True,
        require_reduced_basis=True,
        require_born_ssm_ds=True,
        require_public_routes_closed=require_public_routes_closed,
    )


def _khudaida_mixture_and_feed(case_dir: Path) -> tuple[Any, np.ndarray, float, float]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    fixture, expanded_feed_rows, _expanded_tieline_rows = check_electrolyte_gfpe_gate._source_fixture_payload(case_dir)
    if fixture.get("status") != "source_backed":
        raise ValueError(f"Khudaida source fixture incomplete: {fixture.get('blockers', [])}")
    if not expanded_feed_rows:
        raise ValueError("Khudaida source fixture has no expanded feed rows")
    feed_row = expanded_feed_rows[0]
    parameter_bundle, mixture = check_electrolyte_gfpe_gate._parameter_bundle_payload(
        fixture.get("metadata", {}),
        feed_row,
    )
    if parameter_bundle.get("status") != "constructs_native_mixture" or mixture is None:
        raise ValueError(f"Khudaida parameter bundle incomplete: {parameter_bundle.get('blockers', [])}")
    phase_system_mixture = check_electrolyte_gfpe_gate._nonassociating_diagnostic_mixture(mixture)
    temperature = float(feed_row["temperature_K"])
    pressure = float(fixture.get("metadata", {}).get("pressure_Pa", 100000.0))
    feed = np.asarray(feed_row["expanded"], dtype=float)
    return phase_system_mixture, feed, temperature, pressure


def _max_candidate_charge_residual(candidates: list[list[float]]) -> float:
    if not candidates:
        return math.inf
    residuals = [abs(float(np.asarray(candidate, dtype=float) @ CHARGE_VECTOR)) for candidate in candidates]
    return max(residuals)


def _native_tpd_payload(case_dir: Path) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    from epcsaft_equilibrium._native import extension_native_core

    from scripts.validation import native_freshness

    mixture, feed, temperature, pressure = _khudaida_mixture_and_feed(case_dir)
    core = extension_native_core()
    discovery = core._native_electrolyte_tpd_phase_discovery(
        mixture._native,
        temperature,
        pressure,
        feed.tolist(),
        CHARGE_VECTOR.tolist(),
        [0, 0],
        CHARGE_TOLERANCE,
        TPD_TOLERANCE,
        CANDIDATE_MASS_BALANCE_TOLERANCE,
    )
    candidates = [dict(candidate) for candidate in discovery.get("candidates", [])]
    candidate_compositions = [
        [float(value) for value in candidate.get("composition", [])]
        for candidate in candidates
    ]
    candidate_values = [float(candidate.get("tpd", math.inf)) for candidate in candidates]
    blockers: list[str] = []
    if discovery.get("phase_discovery_backend") != "charge_neutral_deterministic_tpd_candidate_screening":
        blockers.append("electrolyte_tpd_native_backend_mismatch")
    if discovery.get("stability_certificate") != "electrolyte_charge_neutral_tpd_screening":
        blockers.append("electrolyte_tpd_certificate_mismatch")
    if discovery.get("stability_checked") is not True:
        blockers.append("electrolyte_tpd_stability_not_checked")
    if int(discovery.get("unique_candidate_count", 0)) <= 0:
        blockers.append("electrolyte_tpd_candidates_missing")
    if int(discovery.get("selected_candidate_count", 0)) <= 0:
        blockers.append("electrolyte_tpd_selected_candidates_missing")
    if not candidate_values or not all(math.isfinite(value) for value in candidate_values):
        blockers.append("electrolyte_tpd_candidate_values_not_finite")
    max_charge = _max_candidate_charge_residual(candidate_compositions)
    if max_charge > CHARGE_TOLERANCE:
        blockers.append("electrolyte_tpd_candidate_charge_residual_exceeds_threshold")
    min_tpd = float(discovery.get("min_tpd", math.inf))
    if not math.isfinite(min_tpd):
        blockers.append("electrolyte_tpd_min_tpd_not_finite")

    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=core,
        checker_command=[
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_electrolyte_tpd_gate.py",
            "--json",
            "--require-complete",
        ],
    )
    return {
        "status": "charge_neutral_tpd_screening_complete" if not blockers else "incomplete",
        "blockers": blockers,
        "native_binding": "_native_electrolyte_tpd_phase_discovery",
        "phase_discovery_backend": discovery.get("phase_discovery_backend"),
        "stability_certificate": discovery.get("stability_certificate"),
        "phase_set_status": discovery.get("phase_set_status"),
        "stability_checked": bool(discovery.get("stability_checked", False)),
        "stability_accepted": bool(discovery.get("stability_accepted", False)),
        "candidate_count": int(discovery.get("unique_candidate_count", 0)),
        "tpd_candidate_count": int(discovery.get("tpd_candidate_count", 0)),
        "selected_candidate_count": int(discovery.get("selected_candidate_count", 0)),
        "min_tpd": min_tpd,
        "candidate_values": candidate_values,
        "candidate_phase_kinds": [int(candidate.get("phase_kind", -1)) for candidate in candidates],
        "candidate_compositions": candidate_compositions,
        "candidate_statuses": [str(candidate.get("tpd_status", "")) for candidate in candidates],
        "max_candidate_charge_residual": max_charge,
        "charge_tolerance": CHARGE_TOLERANCE,
        "tpd_tolerance": TPD_TOLERANCE,
        "candidate_mass_balance_norm": float(discovery.get("candidate_mass_balance_norm", math.inf)),
        "selected_phase_fractions": list(discovery.get("selected_phase_fractions", [])),
        "held_stage_i_status": discovery.get("held_stage_i_status"),
        "held_stage_ii_status": discovery.get("held_stage_ii_status"),
        "held_stage_iii_status": discovery.get("held_stage_iii_status"),
        "native_freshness_receipt": native_freshness.receipt_to_jsonable(receipt),
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_gate: bool = False,
    require_held2_readiness: bool = False,
    require_native_tpd: bool = False,
    require_public_routes_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))

    source_gate = payload.get("source_gate", {})
    if require_source_gate:
        if source_gate.get("complete") is not True:
            blockers.append("electrolyte_source_gate_incomplete")
        blockers.extend(str(item) for item in source_gate.get("blockers", []))

    held2 = payload.get("held2_readiness_gate", {})
    if require_held2_readiness:
        if held2.get("complete") is not True:
            blockers.append("electrolyte_held2_readiness_gate_incomplete")
        blockers.extend(str(item) for item in held2.get("blockers", []))

    tpd = payload.get("electrolyte_tpd", {})
    if require_native_tpd:
        if tpd.get("status") != "charge_neutral_tpd_screening_complete":
            blockers.append("electrolyte_tpd_gate_incomplete")
        blockers.extend(str(item) for item in tpd.get("blockers", []))
        if tpd.get("stability_checked") is not True:
            blockers.append("electrolyte_tpd_stability_not_checked")
        if int(tpd.get("candidate_count", 0)) <= 0:
            blockers.append("electrolyte_tpd_candidates_missing")
        if int(tpd.get("selected_candidate_count", 0)) <= 0:
            blockers.append("electrolyte_tpd_selected_candidates_missing")
        if float(tpd.get("max_candidate_charge_residual", math.inf)) > float(tpd.get("charge_tolerance", CHARGE_TOLERANCE)):
            blockers.append("electrolyte_tpd_candidate_charge_residual_exceeds_threshold")
        if not math.isfinite(float(tpd.get("min_tpd", math.inf))):
            blockers.append("electrolyte_tpd_min_tpd_not_finite")

    held2_status = payload.get("held2_status", {})
    if held2_status.get("readiness_only") is not True:
        blockers.append("electrolyte_tpd_gate_not_marked_readiness_only")
    if held2_status.get("full_held2_claimed") is True:
        blockers.append("full_held2_claimed_by_tpd_gate")
    pending = set(str(item) for item in held2_status.get("pending_gates", []))
    for gate in REMAINING_HELD2_GATES:
        if gate not in pending:
            blockers.append(f"held2_pending_gate_missing:{gate}")

    public_state = payload.get("public_route_state", {})
    electrolyte = public_state.get("electrolyte_lle", {})
    if require_public_routes_closed:
        if electrolyte.get("present") is not True:
            blockers.append("electrolyte_lle_activation_row_missing")
        if electrolyte.get("production_exposed") is True:
            blockers.append("electrolyte_lle_public_route_exposed")
        if electrolyte.get("public_routes"):
            blockers.append("electrolyte_lle_public_route_exposed")
        if electrolyte.get("proof_routes"):
            blockers.append("electrolyte_lle_proof_route_exposed")
        if "electrolyte_lle" in public_state.get("capabilities_public_routes", []):
            blockers.append("electrolyte_lle_capability_public_route_exposed")
        if "electrolyte_lle" in public_state.get("production_families", []):
            blockers.append("electrolyte_lle_production_family_exposed")

    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    return _jsonable(result)


def evaluate_tpd_gate(
    case_dir: Path = check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR,
    *,
    require_source_gate: bool = False,
    require_held2_readiness: bool = False,
    require_native_tpd: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    source_gate = _source_gate_payload(
        case_dir,
        checker_command,
        require_public_routes_closed=require_public_routes_closed,
    )
    held2 = _held2_readiness_payload(case_dir, require_public_routes_closed=require_public_routes_closed)
    public_state = source_gate.get("public_route_state", {})
    try:
        tpd = _native_tpd_payload(case_dir)
    except Exception as exc:
        tpd = {
            "status": "failed",
            "blockers": [f"electrolyte_tpd_native_receipt_failed:{exc}"],
            "candidate_count": 0,
            "selected_candidate_count": 0,
            "max_candidate_charge_residual": math.inf,
            "charge_tolerance": CHARGE_TOLERANCE,
            "min_tpd": math.inf,
        }
    payload = {
        "checker": "electrolyte_charge_neutral_tpd_gate",
        "case_label": "Khudaida 2026 electrolyte LLE",
        "source_gate": source_gate,
        "held2_readiness_gate": held2,
        "electrolyte_tpd": tpd,
        "held2_status": {
            "status": "charge_neutral_tpd_screening_ready",
            "readiness_only": True,
            "full_held2_claimed": False,
            "ready_prerequisites": [
                "khudaida_source_gate",
                "reduced_charge_neutral_NaCl_amount_lift",
                "cppad_born_ssm_ds_derivative_receipts",
                "charge_neutral_electrolyte_tpd_screening",
                "public_electrolyte_route_admission_gate",
            ],
            "pending_gates": REMAINING_HELD2_GATES,
        },
        "public_route_state": public_state,
    }
    return evaluate_payload(
        payload,
        require_source_gate=require_source_gate,
        require_held2_readiness=require_held2_readiness,
        require_native_tpd=require_native_tpd,
        require_public_routes_closed=require_public_routes_closed,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-gate", action="store_true")
    parser.add_argument("--require-held2-readiness", action="store_true")
    parser.add_argument("--require-native-tpd", action="store_true")
    parser.add_argument("--require-public-routes-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    args = build_arg_parser().parse_args(argv)
    checker_command = sys.argv[:] if argv is None else [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_tpd_gate.py",
        *argv,
    ]
    output = evaluate_tpd_gate(
        args.case_dir,
        require_source_gate=args.require_source_gate or args.require_complete,
        require_held2_readiness=args.require_held2_readiness or args.require_complete,
        require_native_tpd=args.require_native_tpd or args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("electrolyte_tpd", {}).get("native_freshness_receipt", {})
        if receipt:
            from scripts.validation import native_freshness

            try:
                native_freshness.require_equilibrium_native_fresh(dict(receipt))
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"complete={output['complete']} blockers={','.join(output['blockers'])}")
    if args.require_complete and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
