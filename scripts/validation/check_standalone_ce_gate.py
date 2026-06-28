from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REFERENCE_ORACLE_PATH = (
    REPO_ROOT / "analyses" / "reference_oracles" / "chemical_equilibrium" / "cantera_pope_reference_cases.json"
)
VALIDATION_LADDER_PATH = (
    REPO_ROOT / "analyses" / "paper_validation" / "standalone_ce" / "shared" / "results" / "summary.json"
)
REQUIRED_VALIDATION_FAMILIES = (
    "analytic_ideal",
    "charged_conservation",
    "ascani_2023",
    "mea_speciation",
    "cantera_reference_oracle",
    "pope_reference_oracle",
)
REQUIRED_CLOSED_SURFACES = ["reactive_lle", "reactive_electrolyte_lle", "cpe"]

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    EquilibriumConstantRecord,
    StandardStateRecord,
    build_standard_state_registry,
    compile_reaction_set,
    solve_chemical_equilibrium_nlp_activation,
)


def _ideal_ab_problem() -> tuple[Any, Any]:
    standard_state = StandardStateRecord(
        label="mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
    )
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("A", {"X": 1.0}),
            ChemicalSpecies("B", {"X": 1.0}),
        ],
        reactions=[ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0})],
        feed_amounts={"A": 1.0, "B": 0.0},
    )
    registry = build_standard_state_registry(
        [
            EquilibriumConstantRecord(
                reaction_label="a_to_b",
                value=math.log(3.0),
                form="ln_K",
                units="dimensionless",
                standard_state=standard_state,
                source="native checker fixture",
                source_constant_label="ln_K",
            )
        ]
    )
    return compiled, registry


def _side_channel_bindings_absent() -> bool:
    core = extension_native_core()
    expected = {
        "_native_chemical_equilibrium_block",
        "_native_chemical_equilibrium_nlp_activation",
    }
    chemical_equilibrium_bindings = {name for name in dir(core) if name.startswith("_native_chemical_equilibrium")}
    return chemical_equilibrium_bindings == expected


def single_nlp_path_blockers(report: dict[str, Any]) -> list[str]:
    path = dict(report.get("single_nlp_path") or {})
    solver = dict(report.get("solver") or {})
    solution = dict(report.get("solution") or {})
    blockers: list[str] = []

    expected_path = {
        "activation_family": "reactive_speciation",
        "activation_compiler": "activation_plan",
        "native_binding": "_native_chemical_equilibrium_nlp_activation",
        "problem_name": "reactive_speciation_ideal_gibbs_nlp",
        "solver_backend": "ipopt",
    }
    for key, expected in expected_path.items():
        if path.get(key) != expected:
            blockers.append(f"{key}_mismatch")
    if path.get("activation_compiler") != "activation_plan":
        blockers.append("activation_compiler_mismatch")
    if path.get("uses_ipopt_adapter") is not True:
        blockers.append("ipopt_adapter_missing_use")
    if path.get("uses_homogeneous_ce_block") is not True:
        blockers.append("homogeneous_ce_block_missing_use")
    if path.get("side_channel_bindings_absent") is not True:
        blockers.append("side_channel_bindings_present")
    if solver.get("solver_status") != "success":
        blockers.append("ipopt_solver_status_mismatch")
    if solver.get("application_status") != "solve_succeeded":
        blockers.append("ipopt_application_status_mismatch")
    if float(solution.get("balance_inf_norm", 1.0)) > 1.0e-9:
        blockers.append("conserved_balance_norm_above_tolerance")
    if float(solution.get("reaction_stationarity_inf_norm", 1.0)) > 1.0e-8:
        blockers.append("reaction_stationarity_norm_above_tolerance")
    return sorted(set(blockers))


def _load_reference_oracle_payload(path: Path = REFERENCE_ORACLE_PATH) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": "",
            "scope": "",
            "runtime_dependencies": [],
            "cases": [],
            "load_error": f"missing:{path.as_posix()}",
        }
    return json.loads(path.read_text(encoding="utf-8"))


def reference_oracle_payload_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "epcsaft.ce_reference_oracles.v1":
        blockers.append("reference_oracle_schema_version_mismatch")
    if payload.get("scope") != "standalone_chemical_equilibrium_only":
        blockers.append("reference_oracle_scope_mismatch")
    if payload.get("runtime_dependencies") != []:
        blockers.append("reference_oracle_runtime_dependency_present")
    if payload.get("load_error"):
        blockers.append("reference_oracle_fixture_missing")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        blockers.append("reference_oracle_cases_missing")
        return sorted(set(blockers))

    required_case_fields = {
        "case_id",
        "source",
        "solver",
        "species_order",
        "reaction_set",
        "standard_state_registry",
        "initial_amounts",
        "expected",
        "balances",
        "affinities",
        "tolerances",
    }
    for index, case in enumerate(cases):
        case_id = str(case.get("case_id") or f"case_{index}")
        missing = sorted(field for field in required_case_fields if field not in case)
        blockers.extend(f"{case_id}_missing_{field}" for field in missing)
        if case.get("ce_only") is not True:
            blockers.append(f"{case_id}_not_ce_only")
        if case.get("phase_scope") != "homogeneous_single_phase":
            blockers.append(f"{case_id}_phase_scope_not_homogeneous_single_phase")
        if case.get("claimed_equilibrium_scopes") != ["standalone_chemical_equilibrium"]:
            blockers.append(f"{case_id}_claims_non_ce_scope")
        if case.get("oracle_role") != "reference_only":
            blockers.append(f"{case_id}_oracle_role_mismatch")
        solver = dict(case.get("solver") or {})
        if solver.get("runtime_dependency") != "none":
            blockers.append(f"{case_id}_runtime_dependency_present")
        reaction_set = dict(case.get("reaction_set") or {})
        species = list(reaction_set.get("species") or [])
        species_order = list(case.get("species_order") or [])
        if species_order != [str(item.get("label")) for item in species]:
            blockers.append(f"{case_id}_species_order_mismatch")
        balances = dict(case.get("balances") or {})
        tolerances = dict(case.get("tolerances") or {})
        if float(balances.get("balance_inf_norm", 1.0)) > float(tolerances.get("balance_abs", 0.0)):
            blockers.append(f"{case_id}_balance_residual_above_tolerance")
        affinities = dict(case.get("affinities") or {})
        if float(affinities.get("stationarity_inf_norm", 1.0)) > float(tolerances.get("affinity_abs", 0.0)):
            blockers.append(f"{case_id}_affinity_residual_above_tolerance")
    return sorted(set(blockers))


def _compiled_oracle_case(case: dict[str, Any]) -> tuple[Any, Any]:
    reaction_set = dict(case["reaction_set"])
    species = [
        ChemicalSpecies(
            str(item["label"]),
            dict(item["elements"]),
            charge=float(item.get("charge", 0.0)),
        )
        for item in reaction_set["species"]
    ]
    reactions = [
        ChemicalReaction(str(item["label"]), dict(item["stoichiometry"])) for item in reaction_set["reactions"]
    ]
    compiled = compile_reaction_set(
        species=species,
        reactions=reactions,
        feed_amounts=dict(reaction_set["feed_amounts"]),
    )
    records = []
    for item in case["standard_state_registry"]["records"]:
        standard_state_payload = dict(item["standard_state"])
        standard_state = StandardStateRecord(
            label=str(standard_state_payload["label"]),
            activity_convention=str(standard_state_payload["activity_convention"]),
            temperature_K=float(standard_state_payload["temperature_K"]),
            pressure_Pa=float(standard_state_payload["pressure_Pa"]),
            standard_molality_mol_kg=standard_state_payload.get("standard_molality_mol_kg"),
            standard_fugacity_Pa=standard_state_payload.get("standard_fugacity_Pa"),
            eos_reference_phase=standard_state_payload.get("eos_reference_phase"),
            metadata=standard_state_payload.get("metadata"),
        )
        records.append(
            EquilibriumConstantRecord(
                reaction_label=str(item["reaction_label"]),
                value=float(item["value"]),
                form=str(item["form"]),
                units=str(item["units"]),
                standard_state=standard_state,
                source=str(item["source"]),
                source_constant_label=str(item["source_constant_label"]),
                metadata=item.get("metadata"),
            )
        )
    return compiled, build_standard_state_registry(records)


def reference_oracle_evidence() -> dict[str, Any]:
    payload = _load_reference_oracle_payload()
    blockers = reference_oracle_payload_blockers(payload)
    case_evidence: list[dict[str, Any]] = []
    if blockers:
        return {
            "status": "blocked",
            "blockers": blockers,
            "case_count": len(payload.get("cases") or []),
            "cases": case_evidence,
        }

    for case in payload["cases"]:
        compiled, registry = _compiled_oracle_case(case)
        result = solve_chemical_equilibrium_nlp_activation(
            compiled,
            registry,
            initial_amounts=case["initial_amounts"],
            max_iterations=200,
            tolerance=1.0e-10,
        )
        solver = dict(result["solver_diagnostics"])
        expected_amounts = [float(value) for value in case["expected"]["amounts"]]
        amount_errors = [abs(float(actual) - expected) for actual, expected in zip(result["amounts"], expected_amounts)]
        amount_error = max(amount_errors, default=0.0)
        tolerances = dict(case["tolerances"])
        evidence = {
            "case_id": case["case_id"],
            "ce_only": case["ce_only"],
            "activation_family": result["activation"]["key"],
            "native_binding": result["native_binding"],
            "solver_backend": solver["solver_backend"],
            "uses_homogeneous_ce_block": result["thermodynamic_block"] == "homogeneous_chemical_equilibrium",
            "amount_error_inf_norm": amount_error,
            "balance_inf_norm": result["balance_inf_norm"],
            "reaction_stationarity_inf_norm": result["reaction_stationarity_inf_norm"],
            "tolerances": tolerances,
        }
        case_evidence.append(evidence)
        if result["activation"]["key"] != "reactive_speciation":
            blockers.append(f"{case['case_id']}_activation_family_mismatch")
        if result["native_binding"] != "_native_chemical_equilibrium_nlp_activation":
            blockers.append(f"{case['case_id']}_native_binding_mismatch")
        if solver["solver_backend"] != "ipopt":
            blockers.append(f"{case['case_id']}_solver_backend_mismatch")
        if evidence["uses_homogeneous_ce_block"] is not True:
            blockers.append(f"{case['case_id']}_homogeneous_ce_block_missing_use")
        if amount_error > float(tolerances["amount_abs"]):
            blockers.append(f"{case['case_id']}_amount_error_above_tolerance")
        if float(result["balance_inf_norm"]) > float(tolerances["balance_abs"]):
            blockers.append(f"{case['case_id']}_balance_norm_above_tolerance")
        if float(result["reaction_stationarity_inf_norm"]) > float(tolerances["affinity_abs"]):
            blockers.append(f"{case['case_id']}_affinity_norm_above_tolerance")

    unique_blockers = sorted(set(blockers))
    return {
        "status": "complete" if not unique_blockers else "blocked",
        "blockers": unique_blockers,
        "case_count": len(case_evidence),
        "cases": case_evidence,
    }


def _load_validation_ladder_payload(path: Path = VALIDATION_LADDER_PATH) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": "",
            "scope": "",
            "validation_families": [],
            "runtime_dependencies": [],
            "public_routes": [],
            "closed_surfaces": [],
            "load_error": f"missing:{path.as_posix()}",
        }
    return json.loads(path.read_text(encoding="utf-8"))


def validation_ladder_payload_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "epcsaft.standalone_ce.validation_ladder.v1":
        blockers.append("validation_ladder_schema_version_mismatch")
    if payload.get("scope") != "standalone_chemical_equilibrium_only":
        blockers.append("validation_ladder_scope_mismatch")
    if payload.get("claimed_equilibrium_scopes") != ["standalone_chemical_equilibrium"]:
        blockers.append("validation_ladder_claims_non_ce_scope")
    if payload.get("runtime_dependencies") != []:
        blockers.append("validation_ladder_runtime_dependency_present")
    if payload.get("public_routes") != []:
        blockers.append("validation_ladder_public_routes_claimed")
    if payload.get("closed_surfaces") != REQUIRED_CLOSED_SURFACES:
        blockers.append("validation_ladder_closed_surfaces_mismatch")
    if payload.get("load_error"):
        blockers.append("validation_ladder_fixture_missing")

    records = payload.get("validation_families")
    if not isinstance(records, list) or not records:
        blockers.append("validation_families_missing")
        return sorted(set(blockers))

    family_ids = [str(record.get("family_id") or "") for record in records if isinstance(record, dict)]
    for family_id in REQUIRED_VALIDATION_FAMILIES:
        if family_id not in family_ids:
            blockers.append(f"validation_family_{family_id}_missing")
    unexpected = sorted(set(family_ids) - set(REQUIRED_VALIDATION_FAMILIES))
    blockers.extend(f"validation_family_{family_id}_unexpected" for family_id in unexpected)
    duplicates = sorted({family_id for family_id in family_ids if family_ids.count(family_id) > 1})
    blockers.extend(f"validation_family_{family_id}_duplicate" for family_id in duplicates)

    required_record_fields = {
        "family_id",
        "label",
        "status",
        "source",
        "source_path",
        "evidence_role",
        "species_order",
        "units",
        "residuals",
        "tolerances",
        "standard_state_metadata",
    }
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            blockers.append(f"validation_family_{index}_malformed")
            continue
        family_id = str(record.get("family_id") or f"family_{index}")
        missing = sorted(field for field in required_record_fields if field not in record)
        blockers.extend(f"validation_family_{family_id}_missing_{field}" for field in missing)
        if record.get("ce_only") is not True:
            blockers.append(f"validation_family_{family_id}_not_ce_only")
        if record.get("phase_scope") != "homogeneous_single_phase":
            blockers.append(f"validation_family_{family_id}_phase_scope_mismatch")
        if record.get("claimed_equilibrium_scopes") != ["standalone_chemical_equilibrium"]:
            blockers.append(f"validation_family_{family_id}_claims_non_ce_scope")
        if record.get("status") not in {"complete", "retained_source_blocker_disclosed"}:
            blockers.append(f"validation_family_{family_id}_status_mismatch")
        if not isinstance(record.get("species_order"), list) or not record.get("species_order"):
            blockers.append(f"validation_family_{family_id}_species_order_missing")
        if not isinstance(record.get("tolerances"), dict) or not record.get("tolerances"):
            blockers.append(f"validation_family_{family_id}_tolerances_missing")
        if not isinstance(record.get("residuals"), dict) or not record.get("residuals"):
            blockers.append(f"validation_family_{family_id}_residuals_missing")

    derivative = dict(payload.get("derivative_evidence") or {})
    if derivative.get("status") != "complete":
        blockers.append("derivative_evidence_status_mismatch")
    if derivative.get("backend") != "analytic":
        blockers.append("derivative_evidence_backend_mismatch")
    for key, blocker in (
        ("objective_gradient_exact", "derivative_evidence_objective_gradient_not_exact"),
        ("constraint_jacobian_exact", "derivative_evidence_constraint_jacobian_not_exact"),
        ("lagrangian_hessian_exact", "derivative_evidence_lagrangian_hessian_not_exact"),
    ):
        if derivative.get(key) is not True:
            blockers.append(blocker)
    if not derivative.get("source"):
        blockers.append("derivative_evidence_source_missing")

    capability = dict(payload.get("capability_evidence") or {})
    if capability.get("status") != "closed_until_activation_gate":
        blockers.append("capability_evidence_status_mismatch")
    if capability.get("activation_gate") != "issue_0330":
        blockers.append("capability_activation_gate_mismatch")
    if capability.get("production") is not False:
        blockers.append("capability_production_claimed")
    if capability.get("public_routes") != []:
        blockers.append("capability_public_routes_claimed")
    if capability.get("closed_surfaces") != REQUIRED_CLOSED_SURFACES:
        blockers.append("capability_closed_surfaces_mismatch")
    return sorted(set(blockers))


def validation_ladder_evidence() -> dict[str, Any]:
    payload = _load_validation_ladder_payload()
    blockers = validation_ladder_payload_blockers(payload)
    records = payload.get("validation_families") if isinstance(payload.get("validation_families"), list) else []
    families = [
        str(record.get("family_id"))
        for record in records
        if isinstance(record, dict) and record.get("family_id")
    ]
    return {
        "status": "complete" if not blockers else "blocked",
        "blockers": blockers,
        "artifact_path": VALIDATION_LADDER_PATH.relative_to(REPO_ROOT).as_posix(),
        "family_count": len(families),
        "families": families,
        "derivative_evidence": dict(payload.get("derivative_evidence") or {}),
        "capability_evidence": dict(payload.get("capability_evidence") or {}),
    }


def evaluate_standalone_ce_gate(
    *,
    require_single_nlp_path: bool,
    require_oracles: bool = False,
    require_complete: bool = False,
) -> dict[str, Any]:
    core = extension_native_core()
    smoke = core._native_ipopt_smoke()
    if not smoke["compiled"]:
        report = {
            "status": "blocked",
            "blockers": ["ipopt_adapter_missing_compile"],
            "ipopt": smoke,
        }
        return report

    compiled, registry = _ideal_ab_problem()
    result = solve_chemical_equilibrium_nlp_activation(
        compiled,
        registry,
        initial_amounts=[0.5, 0.5],
        max_iterations=100,
        tolerance=1.0e-10,
    )
    solver = dict(result["solver_diagnostics"])
    report = {
        "status": "complete",
        "blockers": [],
        "single_nlp_path": {
            "activation_family": result["activation"]["key"],
            "activation_compiler": result["activation_compiler"],
            "native_binding": result["native_binding"],
            "problem_name": result["activated"]["problem_name"],
            "solver_backend": solver["solver_backend"],
            "uses_ipopt_adapter": solver["solver_backend"] == "ipopt",
            "uses_homogeneous_ce_block": result["thermodynamic_block"] == "homogeneous_chemical_equilibrium",
            "side_channel_bindings_absent": _side_channel_bindings_absent(),
        },
        "solver": {
            "solver_status": solver["solver_status"],
            "application_status": solver["application_status"],
            "iteration_count": solver["iteration_count"],
            "hessian_backend": solver["hessian_backend"],
        },
        "solution": {
            "amounts": result["amounts"],
            "mole_fractions": result["mole_fractions"],
            "balance_inf_norm": result["balance_inf_norm"],
            "reaction_stationarity_inf_norm": result["reaction_stationarity_inf_norm"],
        },
    }
    blockers = single_nlp_path_blockers(report)
    if require_oracles:
        oracle_evidence = reference_oracle_evidence()
        report["oracle_evidence"] = oracle_evidence
        blockers.extend(str(blocker) for blocker in oracle_evidence["blockers"])
    if require_complete:
        if "oracle_evidence" not in report:
            oracle_evidence = reference_oracle_evidence()
            report["oracle_evidence"] = oracle_evidence
            blockers.extend(str(blocker) for blocker in oracle_evidence["blockers"])
        ladder_evidence = validation_ladder_evidence()
        report["validation_ladder"] = ladder_evidence
        blockers.extend(str(blocker) for blocker in ladder_evidence["blockers"])
    report["blockers"] = sorted(set(blockers))
    report["status"] = "complete" if not report["blockers"] else "blocked"
    if require_single_nlp_path and report["blockers"]:
        report["status"] = "blocked"
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON evidence.")
    parser.add_argument("--require-single-nlp-path", action="store_true")
    parser.add_argument("--require-oracles", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    report = evaluate_standalone_ce_gate(
        require_single_nlp_path=args.require_single_nlp_path,
        require_oracles=args.require_oracles,
        require_complete=args.require_complete,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
