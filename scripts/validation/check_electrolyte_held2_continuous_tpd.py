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

from scripts.validation import check_electrolyte_held2_readiness
from scripts.validation import check_electrolyte_gfpe_gate
from scripts.validation import check_electrolyte_tpd_gate

ALGORITHM_SCOPE = "held2_continuous_reduced_electroneutral_tpd_minimizer_only"
COORDINATE_BASIS = "reduced_electroneutral_modified_mole_fractions"
CHARGE_TOLERANCE = check_electrolyte_tpd_gate.CHARGE_TOLERANCE
TPD_TOLERANCE = check_electrolyte_tpd_gate.TPD_TOLERANCE
CANDIDATE_MASS_BALANCE_TOLERANCE = check_electrolyte_tpd_gate.CANDIDATE_MASS_BALANCE_TOLERANCE
NORMALIZATION_TOLERANCE = 1.0e-10
NATIVE_SPECIES = check_electrolyte_tpd_gate.NATIVE_SPECIES
CHARGE_VECTOR = check_electrolyte_tpd_gate.CHARGE_VECTOR.astype(float)
PERDOMO_HELD2_SOURCE = (
    REPO_ROOT
    / "docs"
    / "papers"
    / "md"
    / "Equilibrium"
    / "Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems.md"
)


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


def _charge_residual(composition: list[float]) -> float:
    return abs(float(np.asarray(composition, dtype=float) @ CHARGE_VECTOR))


def _select_neutral_closure(composition: list[float]) -> int:
    neutral_indices = [index for index, charge in enumerate(CHARGE_VECTOR) if abs(float(charge)) == 0.0]
    if not neutral_indices:
        raise ValueError("continuous reduced-electroneutral diagnostics require a neutral closure species")
    return max(neutral_indices, key=lambda index: (float(composition[index]), -index))


def _select_eliminated_charged(composition: list[float]) -> int:
    charged_indices = [index for index, charge in enumerate(CHARGE_VECTOR) if abs(float(charge)) > 0.0]
    if not charged_indices:
        raise ValueError("continuous reduced-electroneutral diagnostics require charged species")
    return max(charged_indices, key=lambda index: (float(composition[index]), -index))


def _reduced_coordinate_indices(composition: list[float]) -> tuple[int, int, list[int]]:
    closure = _select_neutral_closure(composition)
    eliminated = _select_eliminated_charged(composition)
    indices = [
        index
        for index in range(len(composition))
        if index not in {closure, eliminated}
    ]
    return closure, eliminated, indices


def _reduced_coordinates(composition: list[float]) -> dict[str, Any]:
    closure, eliminated, indices = _reduced_coordinate_indices(composition)
    return {
        "coordinate_basis": COORDINATE_BASIS,
        "neutral_closure_species": NATIVE_SPECIES[closure],
        "eliminated_charged_species": NATIVE_SPECIES[eliminated],
        "coordinate_species": [NATIVE_SPECIES[index] for index in indices],
        "values": [float(composition[index]) for index in indices],
    }


def _start_record(raw: dict[str, Any]) -> dict[str, Any]:
    composition = [float(value) for value in raw.get("composition", [])]
    reduced = _reduced_coordinates(composition)
    charge_residual = _charge_residual(composition)
    normalization_residual = abs(sum(composition) - 1.0)
    domain_margin = min(composition) if composition else -math.inf
    tpd_status = str(raw.get("tpd_status", ""))
    accepted = (
        tpd_status == "converged"
        and charge_residual <= CHARGE_TOLERANCE
        and normalization_residual <= NORMALIZATION_TOLERANCE
        and domain_margin > 0.0
    )
    feasibility_status = str(raw.get("feasibility_status", ""))
    rejection_reason = ""
    if not accepted:
        rejection_reason = (
            "continuous_tpd_iteration_limit"
            if tpd_status == "iteration_limit"
            else feasibility_status or "continuous_tpd_start_rejected"
        )
    return {
        "record_type": "trial_phase",
        "coordinate_basis": COORDINATE_BASIS,
        "source": str(raw.get("source", "")),
        "start_source": str(raw.get("start_source", "")),
        "phase_kind": int(raw.get("phase_kind", -1)),
        "composition": composition,
        "reduced_coordinate_species": reduced["coordinate_species"],
        "reduced_coordinates": reduced["values"],
        "neutral_closure_species": reduced["neutral_closure_species"],
        "eliminated_charged_species": reduced["eliminated_charged_species"],
        "charge_residual": charge_residual,
        "normalization_residual": normalization_residual,
        "domain_margin": domain_margin,
        "molar_volume": float(raw.get("molar_volume", math.inf)),
        "tpd": float(raw.get("tpd", math.inf)),
        "tpd_backend": str(raw.get("tpd_backend", "")),
        "tpd_status": tpd_status,
        "tpd_iteration_count": int(raw.get("tpd_iteration_count", 0)),
        "tpd_step_final": float(raw.get("tpd_step_final", 0.0)),
        "accepted": accepted,
        "rejection_reason": rejection_reason,
    }


def _native_continuous_tpd_payload(checker_command: list[str] | None) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    from epcsaft_equilibrium._native import extension_native_core
    from scripts.validation import native_freshness

    mixture, feed, temperature, pressure = check_electrolyte_tpd_gate._khudaida_mixture_and_feed(
        check_electrolyte_gfpe_case_dir()
    )
    core = extension_native_core()
    blockers: list[str] = []
    if not hasattr(core, "_native_electrolyte_held2_continuous_tpd_minimizer"):
        return {
            "status": "incomplete",
            "blockers": ["native_continuous_tpd_binding_missing"],
            "native_binding": "_native_electrolyte_held2_continuous_tpd_minimizer",
        }

    discovery = dict(
        core._native_electrolyte_held2_continuous_tpd_minimizer(
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
    )
    start_records = [
        _start_record(dict(record))
        for record in discovery.get("continuous_tpd_start_records", [])
    ]
    accepted = [record for record in start_records if record["accepted"]]
    rejected = [record for record in start_records if not record["accepted"]]
    max_charge = max((record["charge_residual"] for record in start_records), default=math.inf)
    max_normalization = max((record["normalization_residual"] for record in start_records), default=math.inf)
    min_domain = min((record["domain_margin"] for record in start_records), default=-math.inf)

    if discovery.get("phase_discovery_backend") != "continuous_reduced_electroneutral_tpd_minimization":
        blockers.append("continuous_tpd_backend_mismatch")
    if discovery.get("stability_certificate") != "electrolyte_continuous_reduced_electroneutral_tpd_minimizer":
        blockers.append("continuous_tpd_certificate_mismatch")
    if discovery.get("continuous_tpd_backend") != "continuous_reduced_electroneutral_coordinate_search":
        blockers.append("continuous_tpd_coordinate_search_backend_mismatch")
    if discovery.get("continuous_tpd_status") not in {"converged", "complete_with_rejected_starts"}:
        blockers.append("continuous_tpd_not_converged")
    if int(discovery.get("continuous_tpd_start_count", 0)) <= 0:
        blockers.append("continuous_tpd_starts_missing")
    if int(discovery.get("continuous_tpd_solve_count", 0)) != int(discovery.get("continuous_tpd_start_count", -1)):
        blockers.append("continuous_tpd_solve_count_mismatch")
    if len(start_records) != int(discovery.get("continuous_tpd_start_count", -1)):
        blockers.append("continuous_tpd_start_records_not_replayable")
    if not accepted:
        blockers.append("continuous_tpd_accepted_start_missing")
    if not rejected:
        blockers.append("continuous_tpd_rejected_start_missing")
    if not math.isfinite(float(discovery.get("continuous_tpd_min", math.inf))):
        blockers.append("continuous_tpd_min_not_finite")
    if max_charge > CHARGE_TOLERANCE:
        blockers.append("continuous_tpd_charge_residual_exceeds_threshold")
    if max_normalization > NORMALIZATION_TOLERANCE:
        blockers.append("continuous_tpd_normalization_residual_exceeds_threshold")
    if min_domain <= 0.0:
        blockers.append("continuous_tpd_domain_margin_not_positive")
    if discovery.get("deterministic_screening_is_full_held") is True:
        blockers.append("deterministic_screening_claimed_full_held")
    if discovery.get("held_stage_ii_status") in {"dual_loop_verified", "complete"}:
        blockers.append("stage_ii_claimed_complete_by_continuous_tpd_gate")
    if discovery.get("held_stage_iii_status") == "complete":
        blockers.append("stage_iii_claimed_complete_by_continuous_tpd_gate")

    receipt = native_freshness.build_receipt(
        native_module=core,
        checker_command=checker_command
        or [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_electrolyte_held2_continuous_tpd.py",
            "--json",
            "--require-complete",
        ],
    )
    return _jsonable(
        {
            "status": "complete" if not blockers else "incomplete",
            "blockers": blockers,
            "native_binding": "_native_electrolyte_held2_continuous_tpd_minimizer",
            "algorithm_scope": ALGORITHM_SCOPE,
            "algorithm_source": str(PERDOMO_HELD2_SOURCE),
            "phase_discovery_backend": discovery.get("phase_discovery_backend"),
            "stability_certificate": discovery.get("stability_certificate"),
            "phase_set_status": discovery.get("phase_set_status"),
            "continuous_tpd_status": discovery.get("continuous_tpd_status"),
            "continuous_tpd_backend": discovery.get("continuous_tpd_backend"),
            "continuous_tpd_best_source": discovery.get("continuous_tpd_best_source"),
            "continuous_tpd_start_count": int(discovery.get("continuous_tpd_start_count", 0)),
            "continuous_tpd_solve_count": int(discovery.get("continuous_tpd_solve_count", 0)),
            "continuous_tpd_converged_count": int(discovery.get("continuous_tpd_converged_count", 0)),
            "continuous_tpd_iteration_count_total": int(discovery.get("continuous_tpd_iteration_count_total", 0)),
            "continuous_tpd_iteration_count_max": int(discovery.get("continuous_tpd_iteration_count_max", 0)),
            "continuous_tpd_min": float(discovery.get("continuous_tpd_min", math.inf)),
            "continuous_tpd_step_final_max": float(discovery.get("continuous_tpd_step_final_max", math.inf)),
            "deterministic_candidate_count": int(discovery.get("deterministic_candidate_count", 0)),
            "deterministic_screening_status": discovery.get("deterministic_screening_status"),
            "deterministic_screening_is_full_held": bool(discovery.get("deterministic_screening_is_full_held", True)),
            "deterministic_screening_role": "seed_support_only",
            "selected_candidate_count": int(discovery.get("selected_candidate_count", 0)),
            "accepted_start_count": len(accepted),
            "rejected_start_count": len(rejected),
            "max_charge_residual": max_charge,
            "max_normalization_residual": max_normalization,
            "min_domain_margin": min_domain,
            "start_records": start_records,
            "public_route_admission_status": "separate_public_admission_gate",
            "stage_statuses": {
                "stage_i_certificate": discovery.get("held_stage_i_status"),
                "stage_ii_discovery": discovery.get("held_stage_ii_status"),
                "stage_iii_refinement": discovery.get("held_stage_iii_status"),
                "public_route_admission": "separate_public_admission_gate",
            },
            "native_freshness_receipt": native_freshness.receipt_to_jsonable(receipt),
        }
    )


def check_electrolyte_gfpe_case_dir() -> Path:
    return check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR


def evaluate_continuous_tpd(
    *,
    require_source_gate: bool = False,
    require_held2_readiness: bool = False,
    require_native_continuous_tpd: bool = False,
    require_complete: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    source_gate = check_electrolyte_tpd_gate._source_gate_payload(
        check_electrolyte_gfpe_case_dir(),
        checker_command,
        require_public_routes_closed=require_public_routes_closed,
    )
    readiness_gate = check_electrolyte_held2_readiness.evaluate_readiness(
        check_electrolyte_gfpe_case_dir(),
        require_source_gate=False,
        require_reduced_basis=True,
        require_born_ssm_ds=True,
        require_public_routes_closed=require_public_routes_closed,
    )
    native_evidence = _native_continuous_tpd_payload(checker_command)

    blockers: list[str] = []
    effective_require_source = require_source_gate or require_complete
    effective_require_readiness = require_held2_readiness or require_complete
    effective_require_native = require_native_continuous_tpd or require_complete

    if effective_require_source:
        if source_gate.get("complete") is not True:
            blockers.append("electrolyte_source_gate_incomplete")
        blockers.extend(str(item) for item in source_gate.get("blockers", []))
    if effective_require_readiness:
        if readiness_gate.get("complete") is not True:
            blockers.append("electrolyte_held2_readiness_gate_incomplete")
        blockers.extend(str(item) for item in readiness_gate.get("blockers", []))
    if effective_require_native:
        if native_evidence.get("status") != "complete":
            blockers.append("electrolyte_held2_continuous_tpd_incomplete")
        blockers.extend(str(item) for item in native_evidence.get("blockers", []))

    return _jsonable(
        {
            "checker": "electrolyte_held2_continuous_tpd",
            "complete": not blockers,
            "blockers": sorted(set(blockers)),
            "source_gate": source_gate,
            "held2_readiness_gate": readiness_gate,
            "electrolyte_held2_continuous_tpd": native_evidence,
        }
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate electrolyte HELD2 continuous reduced TPD minimizer.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--require-source-gate", action="store_true")
    parser.add_argument("--require-held2-readiness", action="store_true")
    parser.add_argument("--require-native-continuous-tpd", action="store_true")
    parser.add_argument("--require-public-routes-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    command = ["uv", "run", "--no-sync", "python", "scripts/validation/check_electrolyte_held2_continuous_tpd.py"]
    if args.json:
        command.append("--json")
    if args.require_complete:
        command.append("--require-complete")
    payload = evaluate_continuous_tpd(
        require_source_gate=args.require_source_gate,
        require_held2_readiness=args.require_held2_readiness,
        require_native_continuous_tpd=args.require_native_continuous_tpd,
        require_complete=args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed,
        checker_command=command,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload["complete"]:
        print("Electrolyte HELD2 continuous TPD minimizer validation passed.")
    else:
        print("Electrolyte HELD2 continuous TPD minimizer validation failed:")
        for blocker in payload["blockers"]:
            print(f"- {blocker}")
    return 0 if payload["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
