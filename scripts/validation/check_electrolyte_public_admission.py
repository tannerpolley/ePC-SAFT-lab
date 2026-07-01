from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
from collections.abc import Mapping
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

from scripts.data.paper_validation_parameters import paper_validation_parameter_path
from scripts.validation import check_electrolyte_gfpe_gate
from scripts.validation import check_electrolyte_postsolve_certification
from scripts.validation import check_electrolyte_stage_iii_refinement
from scripts.validation import check_electrolyte_tpd_gate

ALGORITHM_SCOPE = "source_backed_electrolyte_lle_public_admission"
PUBLIC_ROUTE = "electrolyte_lle"
SELECTOR_FAMILY = "electrolyte_lle"
SOURCE_FIXTURE = "data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl"
PARAMETER_BUNDLE = "analyses/paper_validation/2026_khudaida/parameters"
CHECKER_CHAIN = [
    "check_electrolyte_gfpe_gate.py",
    "check_electrolyte_held2_readiness.py",
    "check_electrolyte_tpd_gate.py",
    "check_electrolyte_held2_phase_discovery.py",
    "check_electrolyte_stage_iii_refinement.py",
    "check_electrolyte_postsolve_certification.py",
    "check_electrolyte_public_admission.py",
]
UNSUPPORTED_SURFACES = {
    "reactive_electrolyte_lle": "closed",
    "reactive_lle": "closed",
    "reactive_speciation": "closed",
    "ce": "closed",
    "cpe": "closed",
    "regression": "closed",
    "release_claim": "closed",
    "unsupported_generalized_electrolyte": "closed",
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return value.relative_to(REPO_ROOT).as_posix() if value.is_absolute() else value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _gate_complete(gate: dict[str, Any], *, complete_status: str = "complete") -> bool:
    return gate.get("complete") is True or gate.get("status") == complete_status


def _validate_gate(gate: dict[str, Any], *, blocker: str, complete_status: str = "complete") -> list[str]:
    if not gate:
        return [blocker]
    blockers = [str(item) for item in gate.get("blockers", [])]
    if not _gate_complete(gate, complete_status=complete_status):
        blockers.append(blocker)
    return blockers


def _registry_evidence_payload() -> dict[str, Any]:
    return {
        "source_fixture": SOURCE_FIXTURE,
        "parameter_bundle": PARAMETER_BUNDLE,
        "checker_chain": CHECKER_CHAIN,
        "public_route_status": "public_route_open",
        "public_route": PUBLIC_ROUTE,
        "selector_family": SELECTOR_FAMILY,
        "tolerances": {
            "charge_balance": check_electrolyte_tpd_gate.CHARGE_TOLERANCE,
            "tpd": check_electrolyte_tpd_gate.TPD_TOLERANCE,
            "candidate_mass_balance": check_electrolyte_tpd_gate.CANDIDATE_MASS_BALANCE_TOLERANCE,
            "postsolve_residual": check_electrolyte_stage_iii_refinement.RESIDUAL_TOLERANCE,
            "phase_distance": check_electrolyte_stage_iii_refinement.PHASE_DISTANCE_TOLERANCE,
            "active_bound": check_electrolyte_stage_iii_refinement.ACTIVE_BOUND_TOLERANCE,
        },
    }


def _public_route_state_payload() -> dict[str, Any]:
    import epcsaft_equilibrium

    capabilities = epcsaft_equilibrium.capabilities()
    rows = capabilities["activation_matrix"]["rows"]
    activation = {str(row["key"]): row for row in rows}
    electrolyte = activation.get("electrolyte_lle", {})
    return {
        "electrolyte_lle": {
            "present": bool(electrolyte),
            "production_exposed": bool(electrolyte.get("production_exposed", False)),
            "exposure_status": electrolyte.get("exposure_status"),
            "public_routes": list(electrolyte.get("public_routes", [])),
            "proof_routes": list(electrolyte.get("proof_routes", [])),
        },
        "capabilities_public_routes": list(capabilities.get("public_routes", [])),
        "production_families": list(capabilities.get("production_families", [])),
        "declared_not_exposed_families": list(capabilities.get("declared_not_exposed_families", [])),
        "public_route_family_map": dict(capabilities.get("activation_matrix", {}).get("public_route_family_map", {})),
    }


def _public_route_payload(case_dir: Path, checker_command: list[str] | None) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    import epcsaft
    import epcsaft_equilibrium
    from scripts.validation import native_freshness

    fixture, expanded_feed_rows, _expanded_tieline_rows = check_electrolyte_gfpe_gate._source_fixture_payload(case_dir)
    if fixture.get("status") != "source_backed":
        return {
            "status": "failed",
            "blockers": ["source_fixture_not_source_backed"],
            "public_route": PUBLIC_ROUTE,
        }
    if not expanded_feed_rows:
        return {
            "status": "failed",
            "blockers": ["source_fixture_feed_missing"],
            "public_route": PUBLIC_ROUTE,
        }
    feed_row = expanded_feed_rows[0]
    metadata = fixture.get("metadata", {})
    species = [str(item) for item in metadata.get("species", check_electrolyte_gfpe_gate.NATIVE_SPECIES)]
    temperature = float(feed_row["temperature_K"])
    pressure = float(metadata.get("pressure_Pa", 100000.0))
    feed = np.asarray(feed_row["expanded"], dtype=float)
    parameter_dir = paper_validation_parameter_path(str(metadata.get("parameter_dataset", "2026_Khudaida")))

    try:
        mixture = epcsaft.Mixture.from_folder(
            parameter_dir,
            components=species,
            reference_temperature=temperature,
            reference_composition=feed,
        )
        result = epcsaft_equilibrium.Equilibrium(
            mixture,
            route=PUBLIC_ROUTE,
            T=temperature,
            P=pressure,
            z=feed,
        ).solve(
            solver_options={
                "max_iterations": 180,
                "tolerance": 1.0e-6,
                "hessian_mode": "auto",
                "ipopt_iteration_history_limit": 8,
                "ipopt_acceptable_tolerance": 1.0e-7,
                "ipopt_constraint_violation_tolerance": 1.0e-8,
                "ipopt_dual_infeasibility_tolerance": 1.0e-8,
                "ipopt_complementarity_tolerance": 1.0e-8,
            }
        )
    except Exception as exc:
        return {
            "status": "failed",
            "blockers": [f"public_route_failed:{exc}"],
            "public_route": PUBLIC_ROUTE,
            "selector_family": SELECTOR_FAMILY,
        }

    diagnostics = dict(result.diagnostics)
    postsolve = dict(diagnostics.get("postsolve_certification", {}))
    receipt = native_freshness.build_receipt(
        native_module=epcsaft_equilibrium._native.extension_native_core(),
        checker_command=checker_command
        or [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_electrolyte_public_admission.py",
            "--json",
            "--require-complete",
        ],
    )
    return _jsonable(
        {
            "algorithm_scope": ALGORITHM_SCOPE,
            "status": "accepted",
            "public_route": result.route,
            "selector_family": result.selector_route,
            "problem_kind": result.problem_kind,
            "entrypoint": "Equilibrium(mixture, route='electrolyte_lle', T=..., P=..., z=...).solve()",
            "source_fixture": SOURCE_FIXTURE,
            "parameter_bundle": parameter_dir,
            "component_set": species,
            "feed_composition": result.z,
            "temperature_K": result.temperature,
            "pressure_Pa": result.pressure,
            "phase_labels": result.phase_labels,
            "phase_fractions": dict(result.phase_fractions),
            "phase_compositions": {label: values for label, values in result.phase_compositions.items()},
            "postsolve_certification": postsolve,
            "charge_balance": diagnostics.get("charge_balance", {}),
            "transfer_residuals": diagnostics.get("transfer_residuals", {}),
            "pressure_consistency": diagnostics.get("pressure_consistency", {}),
            "domain_margins": diagnostics.get("domain_margins", {}),
            "electrolyte_stage_iii_refinement": diagnostics.get("electrolyte_stage_iii_refinement", {}),
            "held2_phase_discovery": diagnostics.get("held2_phase_discovery", {}),
            "hessian_approximation": diagnostics.get("hessian_approximation"),
            "route_hessian_approximation": diagnostics.get("route_hessian_approximation"),
            "exact_hessian_available": diagnostics.get("exact_hessian_available"),
            "native_freshness_receipt": native_freshness.receipt_to_jsonable(receipt),
            "blockers": [],
        }
    )


def _parent_closeout_payload() -> dict[str, Any]:
    return {
        "parent_issue": 191,
        "status": "prepared_for_close_after_issue_314_merge",
        "remaining_m4_blockers": [],
        "next_gate": "M6 issue #192 downstream electrolyte evidence",
    }


def _validate_public_route_state(public_state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    electrolyte = public_state.get("electrolyte_lle", {})
    if electrolyte.get("present") is not True:
        blockers.append("electrolyte_lle_activation_row_missing")
    if electrolyte.get("production_exposed") is not True:
        blockers.append("electrolyte_lle_public_route_not_exposed")
    if electrolyte.get("public_routes") != [PUBLIC_ROUTE]:
        blockers.append("electrolyte_lle_public_route_mismatch")
    if PUBLIC_ROUTE not in public_state.get("capabilities_public_routes", []):
        blockers.append("electrolyte_lle_capability_public_route_missing")
    if SELECTOR_FAMILY not in public_state.get("production_families", []):
        blockers.append("electrolyte_lle_production_family_missing")
    if public_state.get("public_route_family_map", {}).get(PUBLIC_ROUTE) != SELECTOR_FAMILY:
        blockers.append("electrolyte_lle_family_map_mismatch")
    for family in ("reactive_speciation", "reactive_lle", "reactive_electrolyte_lle"):
        if family not in public_state.get("declared_not_exposed_families", []):
            blockers.append(f"{family}_not_closed")
    return blockers


def _finite_float(value: Any, default: float = math.inf) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _accepted_status(block: Mapping[str, Any]) -> bool:
    return str(block.get("status", "")) in {
        "accepted",
        "verified_exact_charge_neutral_lift",
        "verified_cppad_born_ssm_ds_receipts",
    }


def _shared_certification_blockers(shared: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if shared.get("route") != PUBLIC_ROUTE:
        blockers.append("electrolyte_shared_certification_route_mismatch")
    if shared.get("selector_family") != SELECTOR_FAMILY:
        blockers.append("electrolyte_shared_certification_selector_family_mismatch")
    if shared.get("family_residual_block") != "electrolyte_lle":
        blockers.append("electrolyte_shared_certification_family_block_mismatch")
    if shared.get("raw_single_ion_equality_used") is True:
        blockers.append("electrolyte_shared_certification_raw_single_ion_equality_used")

    residuals = shared.get("residual_blocks", {})
    if not isinstance(residuals, Mapping):
        return blockers + ["electrolyte_shared_certification_residual_blocks_missing"]

    reduced = residuals.get("reduced_electroneutral_basis", {})
    if not isinstance(reduced, Mapping) or not _accepted_status(reduced):
        blockers.append("electrolyte_shared_certification_reduced_basis_missing")

    lift = residuals.get("lift_back_lift", {})
    if not isinstance(lift, Mapping) or not _accepted_status(lift):
        blockers.append("electrolyte_shared_certification_lift_back_lift_missing")
    elif _finite_float(lift.get("max_charge_residual")) > _finite_float(lift.get("charge_tolerance"), 1.0e-8):
        blockers.append("electrolyte_shared_certification_lift_charge_residual")
    elif _finite_float(lift.get("round_trip_residual")) > _finite_float(lift.get("round_trip_tolerance"), 1.0e-10):
        blockers.append("electrolyte_shared_certification_lift_round_trip_residual")

    charge = residuals.get("charge_balance", {})
    if not isinstance(charge, Mapping) or charge.get("status") != "accepted":
        blockers.append("electrolyte_shared_certification_charge_balance_missing")
    elif _finite_float(charge.get("max_phase_charge_residual")) > _finite_float(
        charge.get("phase_charge_tolerance"), 1.0e-8
    ):
        blockers.append("electrolyte_shared_certification_charge_residual")

    projected = residuals.get("projected_transfer", {})
    if not isinstance(projected, Mapping) or projected.get("status") != "accepted":
        blockers.append("electrolyte_shared_certification_projected_transfer_missing")
    else:
        families = {str(item) for item in projected.get("equation_families", [])}
        labels = {str(item) for item in projected.get("equation_labels", [])}
        if projected.get("enforced_in_solver") is not True:
            blockers.append("electrolyte_shared_certification_projected_transfer_not_enforced")
        if projected.get("projected_charged_transfer") != "mean_ionic_counterion_pairs":
            blockers.append("electrolyte_shared_certification_projected_transfer_basis_mismatch")
        if "mean_ionic_transfer" not in families and not any("mean_ionic" in label for label in labels):
            blockers.append("electrolyte_shared_certification_projected_mean_ionic_equation_missing")

    mean_ionic = residuals.get("mean_ionic_transfer", {})
    if not isinstance(mean_ionic, Mapping) or mean_ionic.get("status") != "accepted":
        blockers.append("electrolyte_shared_certification_mean_ionic_transfer_missing")
    elif _finite_float(mean_ionic.get("max_abs_residual")) > _finite_float(mean_ionic.get("tolerance"), 1.0e-4):
        blockers.append("electrolyte_shared_certification_mean_ionic_transfer_residual")

    active = residuals.get("active_electrolyte_blocks", {})
    if not isinstance(active, Mapping):
        blockers.append("electrolyte_shared_certification_active_blocks_missing")
    else:
        if active.get("born_ssm_ds_exactness") != "accepted":
            blockers.append("electrolyte_shared_certification_born_ssm_ds_exactness_missing")
        if active.get("exact_reduced_jacobian_available") is not True:
            blockers.append("electrolyte_shared_certification_exact_reduced_jacobian_missing")
        if active.get("exact_reduced_hessian_available") is not True:
            blockers.append("electrolyte_shared_certification_exact_reduced_hessian_missing")

    return blockers


def _validate_shared_certification(shared: Any) -> list[str]:
    if not isinstance(shared, Mapping):
        return ["electrolyte_shared_certification_missing"]
    blockers = [str(item) for item in shared.get("validation_blockers", [])]
    blockers.extend(_shared_certification_blockers(shared))
    if shared.get("status") != "accepted":
        blockers.append("electrolyte_shared_certification_not_accepted")
    return sorted(set(blockers))


def _shared_certification_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    public = dict(payload.get("public_admission", {}))
    stage_iii = dict(payload.get("electrolyte_stage_iii_refinement", public.get("electrolyte_stage_iii_refinement", {})))
    postsolve = dict(payload.get("electrolyte_postsolve_certification", {}))
    readiness = dict(payload.get("held2_readiness_gate", {}))
    held2 = dict(payload.get("held2_phase_discovery", public.get("held2_phase_discovery", {})))

    readiness_basis = dict(readiness.get("reduced_basis", {}))
    lift = dict(held2.get("electroneutral_lift", {}))
    charge = dict(public.get("charge_balance", postsolve.get("charge_balance", {})))
    transfer = dict(public.get("transfer_residuals", postsolve.get("transfer_residuals", {})))
    mean_ionic = dict(transfer.get("mean_ionic_transfer", {}))
    projected = dict(stage_iii.get("projected_residual_route", {}))
    derivatives = dict(stage_iii.get("derivative_receipts", {}))
    born = dict(readiness.get("born_ssm_ds_exactness", {}))

    projected_families = [str(item) for item in projected.get("equation_families", [])]
    projected_labels = [str(item) for item in projected.get("equation_labels", [])]
    raw_single_ion = (
        str(projected.get("projected_charged_transfer", "")) == "single_ion"
        or any("single_ion" in item for item in projected_families)
        or any("single_ion" in item for item in projected_labels)
    )

    shared: dict[str, Any] = {
        "schema_version": 1,
        "source": "check_electrolyte_public_admission.py",
        "route": public.get("public_route"),
        "selector_family": public.get("selector_family"),
        "problem_kind": public.get("problem_kind"),
        "family_residual_block": "electrolyte_lle",
        "variable_model": "counterion_pair_reduced_phase_amounts_plus_phase_volume",
        "shared_contract_level": "production_public_route",
        "raw_single_ion_equality_used": raw_single_ion,
        "phase_labels": list(public.get("phase_labels", [])),
        "stage_provenance": {
            "stage_ii_status": dict(held2.get("tpd_discovery", {})).get("held_stage_ii_status"),
            "stage_ii_replay_ready": dict(held2.get("tpd_discovery", {})).get("held_stage_ii_replay_ready"),
            "stage_iii_status": stage_iii.get("status"),
            "postsolve_status": postsolve.get("status") or dict(public.get("postsolve_certification", {})).get("status"),
        },
        "residual_blocks": {
            "reduced_electroneutral_basis": {
                "status": "accepted"
                if readiness_basis.get("status") == "verified_exact_charge_neutral_lift"
                or lift.get("basis_label")
                else "blocked",
                "basis_label": lift.get("basis_label") or readiness_basis.get("basis_semantics"),
                "basis_species": list(readiness_basis.get("basis_species", [])),
                "native_species": list(readiness_basis.get("native_species", [])),
                "charge_vector": list(readiness_basis.get("charge_vector", [])),
                "max_abs_charge_balance": readiness_basis.get("max_abs_charge_balance", lift.get("max_charge_residual")),
                "charge_balance_threshold": readiness_basis.get("charge_balance_threshold", 1.0e-10),
            },
            "lift_back_lift": {
                "status": "accepted" if lift else "blocked",
                "basis_label": lift.get("basis_label"),
                "max_charge_residual": lift.get("max_charge_residual"),
                "charge_tolerance": check_electrolyte_tpd_gate.CHARGE_TOLERANCE,
                "composition_sum_residual": lift.get("composition_sum_residual"),
                "round_trip_residual": lift.get("round_trip_residual"),
                "round_trip_tolerance": lift.get("round_trip_tolerance"),
                "component_nonnegativity_margin": lift.get("component_nonnegativity_margin"),
            },
            "charge_balance": {
                "status": charge.get("status"),
                "max_phase_charge_residual": charge.get("max_phase_charge_residual"),
                "phase_charge_tolerance": charge.get("phase_charge_tolerance", check_electrolyte_tpd_gate.CHARGE_TOLERANCE),
                "total_charge_residual": charge.get("total_charge_residual"),
                "total_charge_tolerance": charge.get("total_charge_tolerance"),
            },
            "projected_transfer": {
                "status": "accepted"
                if projected.get("enforced_in_solver") is True
                and projected.get("projected_charged_transfer") == "mean_ionic_counterion_pairs"
                else "blocked",
                "enforced_in_solver": projected.get("enforced_in_solver"),
                "problem_name": projected.get("problem_name"),
                "equation_families": projected_families,
                "equation_labels": projected_labels,
                "projected_charged_transfer": projected.get("projected_charged_transfer"),
            },
            "mean_ionic_transfer": {
                "status": mean_ionic.get("status"),
                "pair_labels": list(mean_ionic.get("pair_labels", [])),
                "residual_values": list(mean_ionic.get("residual_values", [])),
                "max_abs_residual": mean_ionic.get("max_abs_residual"),
                "tolerance": mean_ionic.get("tolerance"),
            },
            "active_electrolyte_blocks": {
                "status": "accepted"
                if born.get("status") == "verified_cppad_born_ssm_ds_receipts"
                or derivatives.get("born_ssm_ds_active_block_exact_hessian") is True
                else "blocked",
                "born_ssm_ds_exactness": "accepted"
                if born.get("status") == "verified_cppad_born_ssm_ds_receipts"
                or derivatives.get("born_ssm_ds_active_block_exact_hessian") is True
                else "blocked",
                "born_ssm_ds_status": born.get("status"),
                "solvation_shell_model": born.get("solvation_shell_model"),
                "dielectric_saturation": born.get("dielectric_saturation"),
                "derivative_backend": derivatives.get("derivative_backend"),
                "route_hessian_backend": derivatives.get("route_hessian_backend"),
                "exact_reduced_jacobian_available": derivatives.get("exact_reduced_jacobian_available"),
                "exact_reduced_hessian_available": derivatives.get("exact_reduced_hessian_available"),
            },
        },
    }
    validation_blockers = _shared_certification_blockers(shared)
    shared["validation_blockers"] = validation_blockers
    shared["status"] = "accepted" if not validation_blockers else "blocked"
    return shared


def _validate_public_admission(public_admission: dict[str, Any]) -> list[str]:
    blockers: list[str] = [str(item) for item in public_admission.get("blockers", [])]
    if public_admission.get("status") != "accepted":
        blockers.append("public_admission_not_accepted")
    if public_admission.get("public_route") != PUBLIC_ROUTE:
        blockers.append("public_admission_route_mismatch")
    if public_admission.get("selector_family") != SELECTOR_FAMILY:
        blockers.append("public_admission_selector_family_mismatch")
    if public_admission.get("phase_labels") != ["liquid1", "liquid2"]:
        blockers.append("public_admission_phase_labels_mismatch")
    if public_admission.get("exact_hessian_available") is not True:
        blockers.append("public_admission_exact_hessian_receipt_missing")
    charge = public_admission.get("charge_balance", {})
    if charge.get("max_phase_charge_residual", math.inf) > charge.get("phase_charge_tolerance", 1.0e-8):
        blockers.append("public_admission_phase_charge_not_certified")
    pressure = public_admission.get("pressure_consistency", {})
    if pressure.get("pressure_consistency_norm", math.inf) > pressure.get("pressure_tolerance", 1.0e-4):
        blockers.append("public_admission_pressure_not_certified")
    domain = public_admission.get("domain_margins", {})
    if float(domain.get("phase_distance", 0.0)) <= float(domain.get("phase_distance_tolerance", 1.0e-8)):
        blockers.append("public_admission_phase_distance_not_certified")
    held2 = public_admission.get("held2_phase_discovery", {})
    if not isinstance(held2, Mapping):
        blockers.append("public_admission_held2_discovery_missing")
    else:
        blockers.extend(
            f"public_admission_{blocker}" for blocker in _validate_held2_stage_ii(dict(held2))
        )
    stage_iii = public_admission.get("electrolyte_stage_iii_refinement", {})
    if not isinstance(stage_iii, Mapping) or stage_iii.get("status") != "complete":
        blockers.append("public_admission_stage_iii_missing")
    else:
        seed = stage_iii.get("seed_provenance", {})
        if not isinstance(seed, Mapping) or seed.get("stage_ii_replay_ready") is not True:
            blockers.append("public_admission_stage_ii_replay_not_consumed")
    return blockers


def _validate_held2_stage_ii(held2_phase_discovery: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not held2_phase_discovery:
        return ["held2_stage_ii_missing"]
    status = held2_phase_discovery.get("status")
    if status is not None and status != "complete" and held2_phase_discovery.get("complete") is not True:
        blockers.append("held2_phase_discovery_incomplete")
    tpd = held2_phase_discovery.get("tpd_discovery", {})
    if not isinstance(tpd, Mapping):
        return blockers + ["held2_stage_ii_discovery_missing"]
    if tpd.get("held_stage_ii_status") != "dual_loop_verified":
        blockers.append("held2_stage_ii_incomplete")
    if tpd.get("held_stage_ii_candidate_bound_audit_status") != "candidate_bound_gap_closed":
        blockers.append("held2_stage_ii_bound_gap_open")
    if tpd.get("held_stage_ii_dual_loop_status") != "verified":
        blockers.append("held2_stage_ii_dual_loop_incomplete")
    replay_fractions = list(tpd.get("held_stage_ii_replay_phase_fractions", []))
    replay_kinds = list(tpd.get("held_stage_ii_replay_phase_kinds", []))
    replay_compositions = list(tpd.get("held_stage_ii_replay_phase_compositions", []))
    if (
        tpd.get("held_stage_ii_replay_ready") is not True
        or len(replay_fractions) < 2
        or len(replay_kinds) != len(replay_fractions)
        or len(replay_compositions) != len(replay_fractions)
    ):
        blockers.append("held2_stage_ii_replay_missing")
    if tpd.get("held_stage_ii_replay_source") != "stage_ii_dual_loop_selected_candidates":
        blockers.append("held2_stage_ii_replay_source_mismatch")
    if tpd.get("held_stage_ii_replay_seed_name") != "held_stage_ii_dual_loop_candidate_pair":
        blockers.append("held2_stage_ii_replay_seed_mismatch")
    return blockers


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_gate: bool = False,
    require_readiness_gate: bool = False,
    require_tpd_gate: bool = False,
    require_held2_discovery: bool = False,
    require_held2_stage_ii: bool = False,
    require_stage_iii: bool = False,
    require_postsolve_certification: bool = False,
    require_public_admission: bool = False,
    require_parent_closeout: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))
    if require_source_gate:
        blockers.extend(_validate_gate(payload.get("source_gate", {}), blocker="source_gate_incomplete"))
    if require_readiness_gate:
        blockers.extend(_validate_gate(payload.get("held2_readiness_gate", {}), blocker="readiness_gate_incomplete"))
    if require_tpd_gate:
        blockers.extend(_validate_gate(payload.get("electrolyte_tpd_gate", {}), blocker="tpd_gate_incomplete"))
    if require_held2_discovery:
        blockers.extend(
            _validate_gate(payload.get("held2_phase_discovery", {}), blocker="held2_phase_discovery_incomplete")
        )
    if require_held2_stage_ii:
        blockers.extend(_validate_held2_stage_ii(payload.get("held2_phase_discovery", {})))
    if require_stage_iii:
        blockers.extend(
            _validate_gate(
                payload.get("electrolyte_stage_iii_refinement", {}),
                blocker="stage_iii_refinement_incomplete",
            )
        )
    if require_postsolve_certification:
        blockers.extend(
            _validate_gate(
                payload.get("electrolyte_postsolve_certification", {}),
                blocker="postsolve_certification_incomplete",
            )
        )
    if require_public_admission:
        blockers.extend(_validate_public_route_state(payload.get("public_route_state", {})))
        blockers.extend(_validate_public_admission(payload.get("public_admission", {})))
        blockers.extend(_validate_shared_certification(payload.get("shared_certification")))
        unsupported = payload.get("unsupported_surfaces", {})
        for surface, status in UNSUPPORTED_SURFACES.items():
            if unsupported.get(surface) != status:
                blockers.append(f"{surface}_status_mismatch")
    if require_parent_closeout:
        parent = payload.get("parent_closeout", {})
        if parent.get("parent_issue") != 191:
            blockers.append("parent_issue_mismatch")
        if parent.get("remaining_m4_blockers") != []:
            blockers.append("parent_issue_m4_blockers_remain")

    result = dict(payload)
    result["blockers"] = sorted(set(str(item) for item in blockers))
    result["complete"] = not result["blockers"]
    return _jsonable(result)


def evaluate_public_admission(
    case_dir: Path = check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR,
    *,
    require_source_gate: bool = False,
    require_readiness_gate: bool = False,
    require_tpd_gate: bool = False,
    require_held2_discovery: bool = False,
    require_held2_stage_ii: bool = False,
    require_stage_iii: bool = False,
    require_postsolve_certification: bool = False,
    require_public_admission: bool = False,
    require_parent_closeout: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    postsolve_payload = check_electrolyte_postsolve_certification.evaluate_postsolve_certification(
        case_dir,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=False,
        checker_command=checker_command,
    )
    stage_iii = copy.deepcopy(postsolve_payload.get("electrolyte_stage_iii_refinement", {}))
    stage_iii["complete"] = stage_iii.get("status") == "complete"
    postsolve = copy.deepcopy(postsolve_payload.get("electrolyte_postsolve_certification", {}))
    postsolve["complete"] = postsolve.get("status") == "complete"
    payload = {
        "checker": "electrolyte_public_admission_gate",
        "case_label": "Khudaida 2026 electrolyte LLE public admission",
        "algorithm_scope": ALGORITHM_SCOPE,
        "source_gate": postsolve_payload.get("source_gate", {}),
        "held2_readiness_gate": postsolve_payload.get("held2_readiness_gate", {}),
        "electrolyte_tpd_gate": postsolve_payload.get("electrolyte_tpd_gate", {}),
        "held2_phase_discovery": postsolve_payload.get("held2_phase_discovery", {}),
        "electrolyte_stage_iii_refinement": stage_iii,
        "electrolyte_postsolve_certification": postsolve,
        "public_admission": _public_route_payload(case_dir, checker_command),
        "public_route_state": _public_route_state_payload(),
        "registry_evidence": _registry_evidence_payload(),
        "unsupported_surfaces": dict(UNSUPPORTED_SURFACES),
        "parent_closeout": _parent_closeout_payload(),
        "blockers": list(postsolve_payload.get("blockers", [])),
    }
    payload["shared_certification"] = _shared_certification_payload(payload)
    return evaluate_payload(
        payload,
        require_source_gate=require_source_gate,
        require_readiness_gate=require_readiness_gate,
        require_tpd_gate=require_tpd_gate,
        require_held2_discovery=require_held2_discovery,
        require_held2_stage_ii=require_held2_stage_ii,
        require_stage_iii=require_stage_iii,
        require_postsolve_certification=require_postsolve_certification,
        require_public_admission=require_public_admission,
        require_parent_closeout=require_parent_closeout,
    )


def minimal_complete_payload_for_tests() -> dict[str, Any]:
    postsolve = check_electrolyte_postsolve_certification.minimal_complete_payload_for_tests()
    stage_iii = copy.deepcopy(postsolve["electrolyte_stage_iii_refinement"])
    stage_iii["complete"] = True
    stage_iii["projected_residual_route"] = {
        "enforced_in_solver": True,
        "problem_name": "electrolyte_stage_iii_projected_residual_refinement",
        "equation_families": [
            "material_balance",
            "pressure_equality",
            "neutral_transfer",
            "mean_ionic_transfer",
            "phase_charge_balance",
            "phase_distance",
        ],
        "projected_charged_transfer": "mean_ionic_counterion_pairs",
        "equation_labels": [
            "pair_mean_ionic_equality:Na+/Cl-",
            "phase_fraction_closure",
            "phase_charge_balance:phase_0",
            "phase_charge_balance:phase_1",
        ],
    }
    certification = copy.deepcopy(postsolve["electrolyte_postsolve_certification"])
    certification["complete"] = True
    certification["charge_balance"]["status"] = "accepted"
    certification["transfer_residuals"]["mean_ionic_transfer"]["status"] = "accepted"
    held2 = copy.deepcopy(postsolve["held2_phase_discovery"])
    held2["complete"] = True
    payload = {
        "checker": "electrolyte_public_admission_gate",
        "algorithm_scope": ALGORITHM_SCOPE,
        "source_gate": {"complete": True, "blockers": []},
        "held2_readiness_gate": {
            "complete": True,
            "blockers": [],
            "reduced_basis": {
                "status": "verified_exact_charge_neutral_lift",
                "basis_species": ["H2O", "Ethanol", "Butanol", "NaCl"],
                "native_species": ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"],
                "charge_vector": [0.0, 0.0, 0.0, 1.0, -1.0],
                "max_abs_charge_balance": 0.0,
                "charge_balance_threshold": 1.0e-10,
                "basis_semantics": "charge_neutral_reduced_amount_lift_for_strong_NaCl_electrolyte",
            },
            "born_ssm_ds_exactness": {
                "status": "verified_cppad_born_ssm_ds_receipts",
                "solvation_shell_model": True,
                "dielectric_saturation": True,
            },
        },
        "electrolyte_tpd_gate": {
            "complete": True,
            "blockers": [],
            "electrolyte_tpd": {"status": "charge_neutral_tpd_screening_complete"},
        },
        "held2_phase_discovery": held2,
        "electrolyte_stage_iii_refinement": stage_iii,
        "electrolyte_postsolve_certification": certification,
        "public_admission": {
            "algorithm_scope": ALGORITHM_SCOPE,
            "status": "accepted",
            "public_route": PUBLIC_ROUTE,
            "selector_family": SELECTOR_FAMILY,
            "problem_kind": "electrolyte_lle",
            "phase_labels": ["liquid1", "liquid2"],
            "phase_fractions": {"liquid1": 0.4, "liquid2": 0.6},
            "phase_compositions": {
                "liquid1": [0.97, 0.015, 0.015],
                "liquid2": [0.9866666666666667, 0.006666666666666667, 0.006666666666666667],
            },
            "postsolve_certification": {"accepted": True},
            "charge_balance": {
                "status": "accepted",
                "max_phase_charge_residual": 0.0,
                "phase_charge_tolerance": check_electrolyte_tpd_gate.CHARGE_TOLERANCE,
                "total_charge_residual": 0.0,
                "total_charge_tolerance": check_electrolyte_tpd_gate.CHARGE_TOLERANCE,
            },
            "pressure_consistency": {
                "pressure_consistency_norm": 0.0,
                "pressure_tolerance": check_electrolyte_stage_iii_refinement.RESIDUAL_TOLERANCE,
            },
            "domain_margins": {
                "phase_distance": 0.02,
                "phase_distance_tolerance": check_electrolyte_stage_iii_refinement.PHASE_DISTANCE_TOLERANCE,
            },
            "transfer_residuals": certification["transfer_residuals"],
            "held2_phase_discovery": held2,
            "electrolyte_stage_iii_refinement": stage_iii,
            "hessian_approximation": "exact",
            "route_hessian_approximation": "exact",
            "exact_hessian_available": True,
            "blockers": [],
        },
        "public_route_state": {
            "electrolyte_lle": {
                "present": True,
                "production_exposed": True,
                "exposure_status": "production_exposed",
                "public_routes": [PUBLIC_ROUTE],
                "proof_routes": ["electrolyte_held2_public_route_admission"],
            },
            "capabilities_public_routes": [PUBLIC_ROUTE],
            "production_families": [SELECTOR_FAMILY],
            "declared_not_exposed_families": ["reactive_speciation", "reactive_lle", "reactive_electrolyte_lle"],
            "public_route_family_map": {PUBLIC_ROUTE: SELECTOR_FAMILY},
        },
        "registry_evidence": _registry_evidence_payload(),
        "unsupported_surfaces": dict(UNSUPPORTED_SURFACES),
        "parent_closeout": _parent_closeout_payload(),
        "blockers": [],
        "complete": True,
    }
    payload["shared_certification"] = _shared_certification_payload(payload)
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-gate", action="store_true")
    parser.add_argument("--require-readiness-gate", action="store_true")
    parser.add_argument("--require-tpd-gate", action="store_true")
    parser.add_argument("--require-held2-discovery", action="store_true")
    parser.add_argument("--require-held2-stage-ii", action="store_true")
    parser.add_argument("--require-stage-iii", action="store_true")
    parser.add_argument("--require-postsolve-certification", action="store_true")
    parser.add_argument("--require-public-admission", action="store_true")
    parser.add_argument("--require-parent-closeout", action="store_true")
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
        "scripts/validation/check_electrolyte_public_admission.py",
        *argv,
    ]
    output = evaluate_public_admission(
        args.case_dir,
        require_source_gate=args.require_source_gate or args.require_complete,
        require_readiness_gate=args.require_readiness_gate or args.require_complete,
        require_tpd_gate=args.require_tpd_gate or args.require_complete,
        require_held2_discovery=args.require_held2_discovery or args.require_complete,
        require_held2_stage_ii=args.require_held2_stage_ii or args.require_complete,
        require_stage_iii=args.require_stage_iii or args.require_complete,
        require_postsolve_certification=args.require_postsolve_certification or args.require_complete,
        require_public_admission=args.require_public_admission or args.require_complete,
        require_parent_closeout=args.require_parent_closeout,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("public_admission", {}).get("native_freshness_receipt", {})
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
