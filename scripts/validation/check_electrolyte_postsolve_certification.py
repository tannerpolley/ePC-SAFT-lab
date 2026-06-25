from __future__ import annotations

import argparse
import copy
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

from scripts.validation import check_electrolyte_gfpe_gate
from scripts.validation import check_electrolyte_stage_iii_refinement
from scripts.validation import check_electrolyte_tpd_gate

ALGORITHM_SCOPE = "held2_electrolyte_postsolve_phase_set_certification_only"
STAGE_III_SCOPE = check_electrolyte_stage_iii_refinement.ALGORITHM_SCOPE
CHARGE_TOLERANCE = check_electrolyte_tpd_gate.CHARGE_TOLERANCE
TPD_TOLERANCE = check_electrolyte_tpd_gate.TPD_TOLERANCE
CANDIDATE_MASS_BALANCE_TOLERANCE = check_electrolyte_tpd_gate.CANDIDATE_MASS_BALANCE_TOLERANCE
NATIVE_SPECIES = check_electrolyte_tpd_gate.NATIVE_SPECIES
CHARGE_VECTOR = check_electrolyte_tpd_gate.CHARGE_VECTOR.astype(float)
RESIDUAL_TOLERANCE = check_electrolyte_stage_iii_refinement.RESIDUAL_TOLERANCE
PHASE_DISTANCE_TOLERANCE = check_electrolyte_stage_iii_refinement.PHASE_DISTANCE_TOLERANCE
ACTIVE_BOUND_TOLERANCE = check_electrolyte_stage_iii_refinement.ACTIVE_BOUND_TOLERANCE


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


def _finite_nested(values: Any) -> bool:
    if isinstance(values, (list, tuple)):
        return all(_finite_nested(value) for value in values)
    try:
        value = float(values)
    except (TypeError, ValueError):
        return False
    return math.isfinite(value)


def _max_abs(values: Any) -> float:
    if not isinstance(values, (list, tuple)) or not values:
        return math.inf
    try:
        return max(abs(float(value)) for value in values)
    except (TypeError, ValueError):
        return math.inf


def _native_postsolve_payload(case_dir: Path, checker_command: list[str] | None) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    from epcsaft_equilibrium._native import extension_native_core
    from scripts.validation import native_freshness

    mixture, feed, temperature, pressure = check_electrolyte_tpd_gate._khudaida_mixture_and_feed(case_dir)
    core = extension_native_core()
    postsolve = core._native_electrolyte_postsolve_certification(
        mixture._native,
        temperature,
        pressure,
        feed.tolist(),
        CHARGE_VECTOR.tolist(),
        NATIVE_SPECIES,
        [0, 0],
        CHARGE_TOLERANCE,
        TPD_TOLERANCE,
        CANDIDATE_MASS_BALANCE_TOLERANCE,
        RESIDUAL_TOLERANCE,
        PHASE_DISTANCE_TOLERANCE,
        ACTIVE_BOUND_TOLERANCE,
    )
    postsolve = dict(postsolve)
    receipt = native_freshness.build_receipt(
        native_module=core,
        checker_command=checker_command
        or [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_electrolyte_postsolve_certification.py",
            "--json",
            "--require-complete",
        ],
    )
    postsolve["native_freshness_receipt"] = native_freshness.receipt_to_jsonable(receipt)
    return _jsonable(postsolve)


def _validate_public_routes_closed(public_state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    electrolyte = public_state.get("electrolyte_lle", {})
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
    return blockers


def _validate_postsolve_certification(certification: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not certification:
        return ["postsolve_certification_missing"]
    if certification.get("algorithm_scope") != ALGORITHM_SCOPE:
        blockers.append("postsolve_algorithm_scope_mismatch")
    if certification.get("status") != "complete":
        blockers.append("postsolve_certification_incomplete")
    if certification.get("native_binding") != "_native_electrolyte_postsolve_certification":
        blockers.append("postsolve_native_binding_mismatch")

    stages = certification.get("stage_statuses", {})
    if stages.get("phase_discovery") != "complete":
        blockers.append("postsolve_phase_discovery_incomplete")
    if stages.get("stage_iii_refinement") != "complete":
        blockers.append("postsolve_stage_iii_incomplete")
    if stages.get("postsolve_certification") != "complete":
        blockers.append("postsolve_status_incomplete")
    if stages.get("public_route_admission") != "closed":
        blockers.append("postsolve_public_route_admission_claimed")

    reconstruction = certification.get("explicit_ion_reconstruction", {})
    if reconstruction.get("status") != "accepted":
        blockers.append("postsolve_explicit_ion_reconstruction_not_accepted")
    if not reconstruction.get("component_labels"):
        blockers.append("postsolve_component_labels_missing")
    if reconstruction.get("feed_reconstruction_inf_norm", math.inf) > reconstruction.get(
        "feed_reconstruction_tolerance", RESIDUAL_TOLERANCE
    ):
        blockers.append("postsolve_feed_reconstruction_not_certified")
    if float(reconstruction.get("component_nonnegativity_margin", -math.inf)) < 0.0:
        blockers.append("postsolve_component_nonnegativity_not_certified")
    if not _finite_nested(reconstruction.get("reconstructed_feed_composition", [])):
        blockers.append("postsolve_reconstructed_feed_not_finite")

    charges = certification.get("charge_balance", {})
    if charges.get("status") != "accepted":
        blockers.append("postsolve_charge_balance_not_accepted")
    if not charges.get("phase_charge_residuals"):
        blockers.append("postsolve_phase_charge_residuals_missing")
    if charges.get("max_phase_charge_residual", math.inf) > charges.get("phase_charge_tolerance", CHARGE_TOLERANCE):
        blockers.append("postsolve_phase_charge_balance_not_certified")
    if charges.get("total_charge_residual", math.inf) > charges.get("total_charge_tolerance", CHARGE_TOLERANCE):
        blockers.append("postsolve_total_charge_balance_not_certified")

    transfer = certification.get("transfer_residuals", {})
    neutral = transfer.get("neutral_transfer", {})
    mean_ionic = transfer.get("mean_ionic_transfer", {})
    if transfer.get("status") != "accepted":
        blockers.append("postsolve_transfer_residuals_not_accepted")
    if not neutral:
        blockers.append("postsolve_neutral_transfer_missing")
    elif not neutral.get("species_labels"):
        blockers.append("postsolve_neutral_transfer_species_missing")
    elif neutral.get("max_abs_residual", math.inf) > neutral.get("tolerance", RESIDUAL_TOLERANCE):
        blockers.append("postsolve_neutral_transfer_not_certified")
    if not mean_ionic:
        blockers.append("postsolve_mean_ionic_transfer_missing")
    elif not mean_ionic.get("pair_labels"):
        blockers.append("postsolve_mean_ionic_pairs_missing")
    elif mean_ionic.get("max_abs_residual", math.inf) > mean_ionic.get("tolerance", RESIDUAL_TOLERANCE):
        blockers.append("postsolve_mean_ionic_transfer_not_certified")

    pressure = certification.get("pressure_consistency", {})
    if pressure.get("status") != "accepted":
        blockers.append("postsolve_pressure_consistency_not_accepted")
    if pressure.get("pressure_consistency_norm", math.inf) > pressure.get("pressure_tolerance", RESIDUAL_TOLERANCE):
        blockers.append("postsolve_pressure_consistency_not_certified")

    phase_set = certification.get("phase_set", {})
    if phase_set.get("status") != "accepted":
        blockers.append("postsolve_phase_set_not_accepted")
    if int(phase_set.get("phase_count", 0)) < 2:
        blockers.append("postsolve_phase_set_collapsed")
    if not phase_set.get("phase_amount_totals"):
        blockers.append("postsolve_phase_amounts_missing")
    if phase_set.get("phase_fraction_sum_residual", math.inf) > phase_set.get(
        "phase_fraction_sum_tolerance", 1.0e-8
    ):
        blockers.append("postsolve_phase_fraction_sum_not_certified")
    if _max_abs(phase_set.get("composition_sum_residuals", [])) > phase_set.get("composition_sum_tolerance", 1.0e-8):
        blockers.append("postsolve_composition_normalization_not_certified")
    if not _finite_nested(phase_set.get("phase_compositions", [])):
        blockers.append("postsolve_phase_compositions_not_finite")

    domain = certification.get("domain_margins", {})
    if domain.get("status") != "accepted":
        blockers.append("postsolve_domain_margins_not_accepted")
    if float(domain.get("minimum_component_mole_fraction", -math.inf)) < 0.0:
        blockers.append("postsolve_component_domain_not_certified")
    if float(domain.get("minimum_phase_amount", -math.inf)) <= 0.0:
        blockers.append("postsolve_phase_amount_domain_not_certified")
    if float(domain.get("phase_distance", 0.0)) <= float(
        domain.get("phase_distance_tolerance", PHASE_DISTANCE_TOLERANCE)
    ):
        blockers.append("postsolve_phase_distance_not_certified")
    return blockers


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_stage_iii: bool = False,
    require_postsolve_certification: bool = False,
    require_public_routes_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))

    stage_iii = payload.get("electrolyte_stage_iii_refinement", {})
    if require_stage_iii:
        blockers.extend(check_electrolyte_stage_iii_refinement._validate_stage_iii_payload(stage_iii))
        if stage_iii.get("algorithm_scope") != STAGE_III_SCOPE:
            blockers.append("stage_iii_algorithm_scope_mismatch")

    if require_postsolve_certification:
        blockers.extend(_validate_postsolve_certification(payload.get("electrolyte_postsolve_certification", {})))

    if require_public_routes_closed:
        blockers.extend(_validate_public_routes_closed(payload.get("public_route_state", {})))

    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    return _jsonable(result)


def evaluate_postsolve_certification(
    case_dir: Path = check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR,
    *,
    require_stage_iii: bool = False,
    require_postsolve_certification: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    stage_iii_payload = check_electrolyte_stage_iii_refinement.evaluate_stage_iii_refinement(
        case_dir,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_native_stage_iii=True,
        require_public_routes_closed=True,
        checker_command=checker_command,
    )
    try:
        certification = _native_postsolve_payload(case_dir, checker_command)
    except Exception as exc:
        certification = {
            "algorithm_scope": ALGORITHM_SCOPE,
            "status": "failed",
            "native_binding": "_native_electrolyte_postsolve_certification",
            "blockers": [f"postsolve_native_receipt_failed:{exc}"],
        }

    payload = {
        "checker": "electrolyte_postsolve_phase_set_certification_gate",
        "case_label": "Khudaida 2026 electrolyte LLE postsolve certification",
        "source_gate": stage_iii_payload.get("source_gate", {}),
        "held2_readiness_gate": stage_iii_payload.get("held2_readiness_gate", {}),
        "electrolyte_tpd_gate": stage_iii_payload.get("electrolyte_tpd_gate", {}),
        "held2_phase_discovery": stage_iii_payload.get("held2_phase_discovery", {}),
        "electrolyte_stage_iii_refinement": stage_iii_payload.get("electrolyte_stage_iii_refinement", {}),
        "electrolyte_postsolve_certification": certification,
        "public_route_state": stage_iii_payload.get("public_route_state", {}),
        "blockers": list(certification.get("blockers", [])),
    }
    return evaluate_payload(
        payload,
        require_stage_iii=require_stage_iii,
        require_postsolve_certification=require_postsolve_certification,
        require_public_routes_closed=require_public_routes_closed,
    )


def minimal_complete_payload_for_tests() -> dict[str, Any]:
    stage_payload = check_electrolyte_stage_iii_refinement.minimal_complete_payload_for_tests()
    stage_iii = stage_payload["electrolyte_stage_iii_refinement"]
    stage_iii["solver_diagnostics"]["phase_distance"] = 0.02
    stage_iii["stage_statuses"]["postsolve_certification"] = "pending"
    certification = {
        "algorithm_scope": ALGORITHM_SCOPE,
        "status": "complete",
        "native_binding": "_native_electrolyte_postsolve_certification",
        "stage_statuses": {
            "phase_discovery": "complete",
            "stage_iii_refinement": "complete",
            "postsolve_certification": "complete",
            "public_route_admission": "closed",
        },
        "explicit_ion_reconstruction": {
            "status": "accepted",
            "component_labels": ["water", "Na+", "Cl-"],
            "feed_composition": [0.98, 0.01, 0.01],
            "reconstructed_feed_composition": [0.98, 0.01, 0.01],
            "feed_reconstruction_residuals": [0.0, 0.0, 0.0],
            "feed_reconstruction_inf_norm": 0.0,
            "feed_reconstruction_tolerance": RESIDUAL_TOLERANCE,
            "component_nonnegativity_margin": 0.005,
        },
        "charge_balance": {
            "status": "accepted",
            "charge_vector": [0.0, 1.0, -1.0],
            "phase_charge_residuals": [0.0, 0.0],
            "max_phase_charge_residual": 0.0,
            "phase_charge_tolerance": CHARGE_TOLERANCE,
            "total_charge_residual": 0.0,
            "total_charge_tolerance": CHARGE_TOLERANCE,
        },
        "transfer_residuals": {
            "status": "accepted",
            "neutral_transfer": {
                "species_labels": ["water"],
                "residual_values": [0.0],
                "max_abs_residual": 0.0,
                "tolerance": RESIDUAL_TOLERANCE,
            },
            "mean_ionic_transfer": {
                "pair_labels": ["Na+/Cl-"],
                "residual_values": [0.0],
                "max_abs_residual": 0.0,
                "tolerance": RESIDUAL_TOLERANCE,
            },
        },
        "pressure_consistency": {
            "status": "accepted",
            "pressure_consistency_norm": 0.0,
            "pressure_tolerance": RESIDUAL_TOLERANCE,
        },
        "phase_set": {
            "status": "accepted",
            "phase_count": 2,
            "phase_amount_totals": [0.4, 0.6],
            "phase_fractions": [0.4, 0.6],
            "phase_compositions": [[0.97, 0.015, 0.015], [0.9866666666666667, 0.006666666666666667, 0.006666666666666667]],
            "composition_sum_residuals": [0.0, 0.0],
            "composition_sum_tolerance": 1.0e-8,
            "phase_fraction_sum_residual": 0.0,
            "phase_fraction_sum_tolerance": 1.0e-8,
        },
        "domain_margins": {
            "status": "accepted",
            "minimum_component_mole_fraction": 0.005,
            "minimum_phase_amount": 0.4,
            "phase_distance": 0.02,
            "phase_distance_tolerance": PHASE_DISTANCE_TOLERANCE,
        },
    }
    return {
        "checker": "electrolyte_postsolve_phase_set_certification_gate",
        "source_gate": stage_payload["source_gate"],
        "held2_readiness_gate": stage_payload["held2_readiness_gate"],
        "electrolyte_tpd_gate": stage_payload["electrolyte_tpd_gate"],
        "held2_phase_discovery": stage_payload["held2_phase_discovery"],
        "electrolyte_stage_iii_refinement": stage_iii,
        "electrolyte_postsolve_certification": certification,
        "public_route_state": stage_payload["public_route_state"],
        "blockers": [],
        "complete": True,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR)
    parser.add_argument("--require-stage-iii", action="store_true")
    parser.add_argument("--require-postsolve-certification", action="store_true")
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
        "scripts/validation/check_electrolyte_postsolve_certification.py",
        *argv,
    ]
    output = evaluate_postsolve_certification(
        args.case_dir,
        require_stage_iii=args.require_stage_iii or args.require_complete,
        require_postsolve_certification=args.require_postsolve_certification or args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed or args.require_complete,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("electrolyte_postsolve_certification", {}).get("native_freshness_receipt", {})
        if receipt:
            from scripts.validation import native_freshness

            try:
                native_freshness.require_receipt(dict(receipt))
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
