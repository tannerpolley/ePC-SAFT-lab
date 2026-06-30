from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections.abc import Mapping, Sequence
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
MEA_RETAINED_SUMMARY_PATH = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "standalone_ce"
    / "figures"
    / "mea_reactive_speciation_oracle_comparison"
    / "results"
    / "mea_ce_oracle_speciation_comparison_summary.json"
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
REQUIRED_MEA_RETAINED_SUMMARY_PATH = MEA_RETAINED_SUMMARY_PATH.relative_to(REPO_ROOT).as_posix()
REQUIRED_MEA_SEED_POLICY = "max_min_feasible_interior_no_oracle"
REQUIRED_MEA_TEMPERATURES_C = [20.0, 40.0]
REQUIRED_MEA_LOADING_COUNT = 161
REQUIRED_MEA_STATE_POINT_COUNT = 322
REQUIRED_MEA_SPECIES_ROW_COUNT = 3220
MEA_STRICT_TOLERANCES = {
    "balance_abs": 1.0e-8,
    "affinity_abs": 1.0e-6,
    "mole_fraction_abs": 1.0e-8,
    "loading_abs": 1.0e-8,
    "charge_abs": 1.0e-8,
}
REQUIRED_MEA_ROBUSTNESS_FIELDS = [
    "activity_model",
    "solver_status",
    "application_status",
    "accepted",
    "failure_class",
    "balance_inf_norm",
    "reaction_stationarity_inf_norm",
    "seed_source",
    "uses_source_oracle_initial_amounts",
    "stage_count",
    "final_proof_status",
    "physical_proof_corrector_attempted",
    "physical_proof_corrector_rejection_reason",
    "physical_proof_corrector_initial_reaction_stationarity_inf_norm",
    "physical_proof_corrector_final_reaction_stationarity_inf_norm",
    "physical_proof_corrector_final_balance_inf_norm",
]

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft_equilibrium import EquilibriumSolverOptions, reactive_speciation
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


def _mea_standard_state() -> StandardStateRecord:
    return StandardStateRecord(
        label="smith_missen_mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=313.15,
        pressure_Pa=101325.0,
        metadata={
            "source_project": "MEA-Thermodynamics",
            "source_module": "MEA.smith_missen.ideal_speciation",
            "temperature_label": "40 C",
        },
    )


def _mea_species() -> list[ChemicalSpecies]:
    return [
        ChemicalSpecies("CO2", {"C": 1.0, "O": 2.0}),
        ChemicalSpecies("MEA", {"C": 2.0, "H": 7.0, "N": 1.0, "O": 1.0}),
        ChemicalSpecies("H2O", {"H": 2.0, "O": 1.0}),
        ChemicalSpecies("MEAH+", {"C": 2.0, "H": 8.0, "N": 1.0, "O": 1.0}, charge=1.0),
        ChemicalSpecies("MEACOO-", {"C": 3.0, "H": 6.0, "N": 1.0, "O": 3.0}, charge=-1.0),
        ChemicalSpecies("HCO3-", {"H": 1.0, "C": 1.0, "O": 3.0}, charge=-1.0),
        ChemicalSpecies("CO3^2-", {"C": 1.0, "O": 3.0}, charge=-2.0),
        ChemicalSpecies("H3O+", {"H": 3.0, "O": 1.0}, charge=1.0),
        ChemicalSpecies("OH-", {"H": 1.0, "O": 1.0}, charge=-1.0),
    ]


def _mea_reactions() -> list[ChemicalReaction]:
    return [
        ChemicalReaction("R1_water_autoionization", {"H2O": -2.0, "H3O+": 1.0, "OH-": 1.0}),
        ChemicalReaction("R2_CO2_to_HCO3", {"CO2": -1.0, "H2O": -2.0, "HCO3-": 1.0, "H3O+": 1.0}),
        ChemicalReaction("R3_HCO3_to_CO3", {"H2O": -1.0, "HCO3-": -1.0, "CO3^2-": 1.0, "H3O+": 1.0}),
        ChemicalReaction("R4_MEACOO_hydrolysis", {"MEA": 1.0, "H2O": -1.0, "MEACOO-": -1.0, "HCO3-": 1.0}),
        ChemicalReaction("R5_MEAH_dissociation", {"MEA": 1.0, "H2O": -1.0, "MEAH+": -1.0, "H3O+": 1.0}),
    ]


def _mea_constants() -> list[EquilibriumConstantRecord]:
    standard_state = _mea_standard_state()
    ln_k_by_reaction = {
        "R1_water_autoionization": -39.20847211814555,
        "R2_CO2_to_HCO3": -18.52157205941222,
        "R3_HCO3_to_CO3": -27.55307337666852,
        "R4_MEACOO_hydrolysis": -6.79989583266805,
        "R5_MEAH_dissociation": -26.37413522909149,
    }
    return [
        EquilibriumConstantRecord(
            reaction_label=label,
            value=ln_k,
            form="ln_K",
            units="dimensionless",
            standard_state=standard_state,
            source="MEA-Thermodynamics Smith-Missen Phase 1 retained fixture",
            source_constant_label=label,
            metadata={"basis": "mole fraction", "temperature_K": 313.15},
        )
        for label, ln_k in ln_k_by_reaction.items()
    ]


_MEA_WATER_PER_AMINE = 7.909507954125047
_MEA_EXPECTED_MOLE_FRACTIONS = {
    0.1: {
        "CO2": 6.683924651954811e-09,
        "MEA": 0.08989223566464728,
        "H2O": 0.8873375669739914,
        "MEAH+": 0.011527775080012528,
        "MEACOO-": 0.010819632394452237,
        "HCO3-": 0.00011896575214617932,
        "CO3^2-": 0.00028535948338821623,
        "H3O+": 3.999178474611162e-13,
        "OH-": 1.845796703766678e-05,
    },
    0.4: {
        "CO2": 1.4322412188376851e-06,
        "MEA": 0.02419700925042081,
        "H2O": 0.88572243609252,
        "MEAH+": 0.04518349608467077,
        "MEACOO-": 0.042858977799977424,
        "HCO3-": 0.001747513447705002,
        "CO3^2-": 0.000287869765126298,
        "H3O+": 5.812652925262093e-12,
        "OH-": 1.265312548334571e-06,
    },
    0.8: {
        "CO2": 0.005192618263938971,
        "MEA": 0.00043545843921396094,
        "H2O": 0.8260154916473321,
        "MEAH+": 0.08422357694784907,
        "MEACOO-": 0.026997790877452618,
        "HCO3-": 0.057044328501079176,
        "CO3^2-": 9.072336914185697e-05,
        "H3O+": 5.614793231095988e-10,
        "OH-": 1.1392512989995421e-08,
    },
}


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
            "proof_metrics": dict(result.get("proof_metrics") or {}),
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
        proof_metrics = dict(evidence["proof_metrics"])
        if not proof_metrics:
            blockers.append(f"{case['case_id']}_proof_metrics_missing")
        if not math.isclose(
            _as_float(proof_metrics, "unscaled_reaction_stationarity_inf_norm"),
            float(result["reaction_stationarity_inf_norm"]),
            rel_tol=0.0,
            abs_tol=1.0e-14,
        ):
            blockers.append(f"{case['case_id']}_proof_metrics_unscaled_affinity_mismatch")

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


def _load_mea_retained_summary_payload(path: Path = MEA_RETAINED_SUMMARY_PATH) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": "",
            "public_route": "",
            "temperature_C": [],
            "loading_count": 0,
            "pointwise_unassisted": {},
            "ce_owned_continuation_trace": {},
            "shuffled_subset": {},
            "load_error": f"missing:{path.as_posix()}",
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _as_float(payload: Mapping[str, Any], key: str, default: float = math.inf) -> float:
    try:
        return float(payload.get(key, default))
    except (TypeError, ValueError):
        return default


def _mea_artifact_strict_gates_pass(payload: Mapping[str, Any]) -> bool:
    pointwise = dict(payload.get("pointwise_unassisted") or {})
    return (
        payload.get("strict_gates_passed") is True
        and payload.get("all_accepted") is True
        and pointwise.get("all_accepted") is True
        and pointwise.get("all_no_source_oracle_seed") is True
        and pointwise.get("all_final_lambda_one") is True
        and _as_float(payload, "max_abs_error") <= MEA_STRICT_TOLERANCES["mole_fraction_abs"]
        and _as_float(payload, "max_balance_inf_norm") <= MEA_STRICT_TOLERANCES["balance_abs"]
        and _as_float(payload, "max_reaction_stationarity_inf_norm") <= MEA_STRICT_TOLERANCES["affinity_abs"]
    )


def _mea_artifact_continuation_gates_pass(payload: Mapping[str, Any]) -> bool:
    continuation = dict(payload.get("ce_owned_continuation_trace") or payload.get("continuation_evidence") or {})
    return (
        int(continuation.get("max_stage_count", -1)) == 3
        and int(continuation.get("homotopy_point_count", -1)) == 12
        and int(continuation.get("physical_proof_corrector_point_count", -1)) == REQUIRED_MEA_STATE_POINT_COUNT
        and continuation.get("all_final_lambda_one") is True
        and continuation.get("all_final_proof_accepted") is True
    )


def _mea_artifact_corrector_repair_gates_pass(payload: Mapping[str, Any]) -> bool:
    continuation = dict(payload.get("ce_owned_continuation_trace") or payload.get("continuation_evidence") or {})
    return (
        int(continuation.get("corrected_stationarity_point_count", -1)) >= 1
        and _as_float(continuation, "max_initial_physical_proof_corrector_reaction_stationarity_inf_norm")
        > MEA_STRICT_TOLERANCES["affinity_abs"]
        and _as_float(continuation, "max_final_physical_proof_corrector_reaction_stationarity_inf_norm")
        <= MEA_STRICT_TOLERANCES["affinity_abs"]
        and _as_float(continuation, "max_final_physical_proof_corrector_balance_inf_norm")
        <= MEA_STRICT_TOLERANCES["balance_abs"]
        and continuation.get("all_physical_proof_corrector_rejection_reasons_empty") is True
    )


def _mea_artifact_shuffled_subset_gates_pass(payload: Mapping[str, Any]) -> bool:
    shuffled = dict(payload.get("shuffled_subset") or {})
    return (
        int(shuffled.get("attempt_count", -1)) >= 34
        and shuffled.get("all_accepted") is True
        and shuffled.get("all_no_source_oracle_seed") is True
        and _as_float(shuffled, "max_abs_error") <= MEA_STRICT_TOLERANCES["mole_fraction_abs"]
    )


def mea_retained_summary_payload_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "epcsaft.standalone_ce.mea_speciation_oracle_comparison.v2":
        blockers.append("mea_retained_summary_schema_version_mismatch")
    if payload.get("public_route") != "reactive_speciation":
        blockers.append("mea_retained_summary_public_route_mismatch")
    if payload.get("ce_workflow") != "epcsaft_equilibrium.reactive_speciation":
        blockers.append("mea_retained_summary_workflow_mismatch")
    if payload.get("temperature_C") != REQUIRED_MEA_TEMPERATURES_C:
        blockers.append("mea_retained_summary_temperature_grid_mismatch")
    if int(payload.get("loading_count", 0)) != REQUIRED_MEA_LOADING_COUNT:
        blockers.append("mea_retained_summary_loading_count_mismatch")
    pointwise = dict(payload.get("pointwise_unassisted") or {})
    if int(pointwise.get("row_count", 0)) != REQUIRED_MEA_SPECIES_ROW_COUNT:
        blockers.append("mea_retained_summary_species_row_count_mismatch")
    if int(pointwise.get("loading_count", 0)) != REQUIRED_MEA_LOADING_COUNT:
        blockers.append("mea_retained_summary_pointwise_loading_count_mismatch")
    if payload.get("seed_policy") != REQUIRED_MEA_SEED_POLICY:
        blockers.append("mea_retained_summary_seed_policy_mismatch")
    if payload.get("uses_source_oracle_initial_amounts") is not False:
        blockers.append("mea_retained_summary_source_oracle_seeded")
    solver_options = dict(payload.get("solver_options") or {})
    if solver_options.get("max_iterations") != 1000 or float(solver_options.get("tolerance", 1.0)) != 1.0e-8:
        blockers.append("mea_retained_summary_solver_options_mismatch")
    if not _mea_artifact_strict_gates_pass(payload):
        blockers.append("mea_retained_summary_strict_gates_missing")
    if not _mea_artifact_continuation_gates_pass(payload):
        blockers.append("mea_retained_summary_continuation_trace_missing")
    if not _mea_artifact_corrector_repair_gates_pass(payload):
        blockers.append("mea_retained_summary_physical_corrector_repair_evidence_missing")
    if not _mea_artifact_shuffled_subset_gates_pass(payload):
        blockers.append("mea_retained_summary_shuffled_subset_missing")
    robustness = dict(payload.get("robustness_diagnostics") or {})
    if not robustness:
        blockers.append("mea_retained_summary_robustness_diagnostics_missing")
    else:
        if robustness.get("artifact") != "analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/results/mea_ce_unassisted_seed_audit.csv":
            blockers.append("mea_retained_summary_robustness_artifact_mismatch")
        if list(robustness.get("required_fields") or []) != REQUIRED_MEA_ROBUSTNESS_FIELDS:
            blockers.append("mea_retained_summary_robustness_fields_mismatch")
        if robustness.get("activity_model") != "mole_fraction_activity":
            blockers.append("mea_retained_summary_activity_model_mismatch")
        if list(robustness.get("failure_classes") or []) != ["accepted"]:
            blockers.append("mea_retained_summary_failure_classes_mismatch")
        if int(robustness.get("state_point_count") or 0) != REQUIRED_MEA_STATE_POINT_COUNT:
            blockers.append("mea_retained_summary_robustness_state_point_count_mismatch")
        if int(robustness.get("accepted_state_point_count") or 0) != REQUIRED_MEA_STATE_POINT_COUNT:
            blockers.append("mea_retained_summary_robustness_accepted_count_mismatch")
    if payload.get("load_error"):
        blockers.append("mea_retained_summary_fixture_missing")
    return sorted(set(blockers))


def _mea_retained_artifact_evidence_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    pointwise = dict(payload.get("pointwise_unassisted") or {})
    continuation = dict(payload.get("ce_owned_continuation_trace") or {})
    shuffled_subset = dict(payload.get("shuffled_subset") or {})
    robustness = dict(payload.get("robustness_diagnostics") or {})
    temperature_count = len(payload.get("temperature_C") or [])
    loading_count = int(payload.get("loading_count") or 0)
    state_point_count = loading_count * temperature_count
    blockers = mea_retained_summary_payload_blockers(payload)
    return {
        "status": "complete" if not blockers else "blocked",
        "blockers": blockers,
        "artifact_path": REQUIRED_MEA_RETAINED_SUMMARY_PATH,
        "schema_version": payload.get("schema_version"),
        "public_route": payload.get("public_route"),
        "temperature_C": list(payload.get("temperature_C") or []),
        "loading_count": loading_count,
        "temperature_count": temperature_count,
        "state_point_count": state_point_count,
        "species_row_count": int(pointwise.get("row_count") or 0),
        "strict_gates_passed": payload.get("strict_gates_passed") is True,
        "seed_policy": payload.get("seed_policy"),
        "uses_source_oracle_initial_amounts": payload.get("uses_source_oracle_initial_amounts"),
        "max_mole_fraction_abs_error": payload.get("max_abs_error"),
        "max_balance_inf_norm": payload.get("max_balance_inf_norm"),
        "max_reaction_stationarity_inf_norm": payload.get("max_reaction_stationarity_inf_norm"),
        "pointwise_unassisted": pointwise,
        "continuation_evidence": continuation,
        "robustness_diagnostics": robustness,
        "shuffled_subset": shuffled_subset,
    }


def mea_retained_artifact_evidence() -> dict[str, Any]:
    return _mea_retained_artifact_evidence_from_payload(_load_mea_retained_summary_payload())


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
    if payload.get("public_routes") != ["reactive_speciation"]:
        blockers.append("validation_ladder_public_routes_mismatch")
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
        if family_id == "mea_speciation":
            if record.get("evidence_role") != "retained_no_oracle_public_reactive_speciation_sweep":
                blockers.append("validation_family_mea_speciation_evidence_role_mismatch")
            if record.get("source_path") != REQUIRED_MEA_RETAINED_SUMMARY_PATH:
                blockers.append("validation_family_mea_speciation_source_path_mismatch")
            if record.get("temperature_C") != REQUIRED_MEA_TEMPERATURES_C:
                blockers.append("validation_family_mea_speciation_temperature_grid_mismatch")
            if int(record.get("loading_count", 0)) != REQUIRED_MEA_LOADING_COUNT:
                blockers.append("validation_family_mea_speciation_retained_loading_count_mismatch")
            if record.get("seed_policy") != REQUIRED_MEA_SEED_POLICY:
                blockers.append("validation_family_mea_speciation_seed_policy_mismatch")
            if record.get("uses_source_oracle_initial_amounts") is not False:
                blockers.append("validation_family_mea_speciation_source_oracle_seeded")
            solver_options = dict(record.get("solver_options") or {})
            if solver_options.get("max_iterations") != 1000 or float(solver_options.get("tolerance", 1.0)) != 1.0e-8:
                blockers.append("validation_family_mea_speciation_solver_options_mismatch")
            standard_state = dict(record.get("standard_state_metadata") or {})
            if standard_state.get("activity_convention") != "mole_fraction_activity":
                blockers.append("validation_family_mea_speciation_standard_state_mismatch")
            residuals = dict(record.get("residuals") or {})
            tolerances = dict(record.get("tolerances") or {})
            strict_gates_pass = (
                int(residuals.get("state_point_count", 0)) == REQUIRED_MEA_STATE_POINT_COUNT
                and int(residuals.get("species_row_count", 0)) == REQUIRED_MEA_SPECIES_ROW_COUNT
                and _as_float(residuals, "max_mole_fraction_abs_error") <= float(tolerances.get("mole_fraction_abs", 0.0))
                and _as_float(residuals, "max_balance_inf_norm") <= float(tolerances.get("balance_abs", 0.0))
                and _as_float(residuals, "max_reaction_stationarity_inf_norm")
                <= float(tolerances.get("affinity_abs", 0.0))
            )
            if not strict_gates_pass:
                blockers.append("validation_family_mea_speciation_strict_gates_missing")
            continuation = dict(record.get("continuation_evidence") or {})
            if not (
                int(continuation.get("max_stage_count", -1)) == 3
                and int(continuation.get("homotopy_point_count", -1)) == 12
                and int(continuation.get("physical_proof_corrector_point_count", -1))
                == REQUIRED_MEA_STATE_POINT_COUNT
                and continuation.get("all_final_lambda_one") is True
                and continuation.get("all_final_proof_accepted") is True
            ):
                blockers.append("validation_family_mea_speciation_continuation_trace_missing")
            shuffled_subset = dict(record.get("shuffled_subset") or {})
            if not (
                int(shuffled_subset.get("attempt_count", -1)) >= 34
                and shuffled_subset.get("all_accepted") is True
                and shuffled_subset.get("all_no_source_oracle_seed") is True
                and _as_float(shuffled_subset, "max_abs_error") <= float(tolerances.get("mole_fraction_abs", 0.0))
            ):
                blockers.append("validation_family_mea_speciation_shuffled_subset_missing")

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
    if capability.get("status") != "standalone_ce_open_cpe_closed":
        blockers.append("capability_evidence_status_mismatch")
    if capability.get("activation_gate") != "issue_0330_complete":
        blockers.append("capability_activation_gate_mismatch")
    if capability.get("production") is not True:
        blockers.append("capability_production_missing")
    public_routes = list(capability.get("public_routes") or [])
    if public_routes != ["reactive_speciation"]:
        blockers.append("capability_public_routes_mismatch")
    if any(str(route) in REQUIRED_CLOSED_SURFACES for route in public_routes):
        blockers.append("capability_reactive_phase_route_claimed")
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


def mea_speciation_public_sweep_evidence() -> dict[str, Any]:
    species = _mea_species()
    reactions = _mea_reactions()
    constants = _mea_constants()
    solver_options = EquilibriumSolverOptions(max_iterations=1000, tolerance=1.0e-8)
    tolerances = dict(MEA_STRICT_TOLERANCES)
    blockers: list[str] = []
    rows: list[dict[str, Any]] = []
    for loading, expected in _MEA_EXPECTED_MOLE_FRACTIONS.items():
        result = reactive_speciation(
            species=species,
            reactions=reactions,
            feed_amounts={"MEA": 1.0, "H2O": _MEA_WATER_PER_AMINE, "CO2": loading},
            equilibrium_constants=constants,
            initial_amounts=None,
            solver_options=solver_options,
        )
        diagnostics = dict(result.diagnostics)
        initialization = dict(diagnostics.get("initialization") or {})
        feasible_initialization = dict(initialization.get("feasible_initialization") or {})
        continuation = dict(diagnostics.get("continuation") or {})
        physical_corrector = dict(continuation.get("physical_proof_corrector") or {})
        proof_metrics = dict(diagnostics.get("proof_metrics") or {})
        physical_corrector_metrics = dict(physical_corrector.get("proof_metrics") or {})
        amounts = result.species_amounts
        reconstructed_loading = (
            amounts["CO2"] + amounts["MEACOO-"] + amounts["HCO3-"] + amounts["CO3^2-"]
        ) / (amounts["MEA"] + amounts["MEAH+"] + amounts["MEACOO-"])
        charge = (
            amounts["MEAH+"]
            + amounts["H3O+"]
            - amounts["MEACOO-"]
            - amounts["HCO3-"]
            - 2.0 * amounts["CO3^2-"]
            - amounts["OH-"]
        )
        mole_fraction_errors = [
            abs(float(actual) - float(expected[label]))
            for actual, label in zip(result.mole_fractions.tolist(), result.species_labels)
        ]
        balance_inf_norm = max(abs(float(value)) for value in result.balances.values())
        affinity_inf_norm = max(abs(float(value)) for value in result.affinities.values())
        row = {
            "loading_mol_co2_per_mol_mea": loading,
            "max_mole_fraction_abs_error": max(mole_fraction_errors, default=0.0),
            "balance_inf_norm": balance_inf_norm,
            "reaction_stationarity_inf_norm": affinity_inf_norm,
            "reaction_scaling_min": _as_float(proof_metrics, "reaction_scaling_min"),
            "reaction_scaling_max": _as_float(proof_metrics, "reaction_scaling_max"),
            "reaction_basis_condition_estimate": _as_float(proof_metrics, "reaction_basis_condition_estimate"),
            "scaled_reaction_stationarity_inf_norm": _as_float(
                proof_metrics, "scaled_reaction_stationarity_inf_norm"
            ),
            "unscaled_reaction_stationarity_inf_norm": _as_float(
                proof_metrics, "unscaled_reaction_stationarity_inf_norm"
            ),
            "reconstructed_loading_abs_error": abs(reconstructed_loading - loading),
            "charge_balance": charge,
            "solver_status": str(result.diagnostics["solver_status"]),
            "application_status": str(result.diagnostics["application_status"]),
            "accepted": diagnostics.get("accepted") is True,
            "seed_policy": REQUIRED_MEA_SEED_POLICY,
            "seed_source": initialization.get("seed_source"),
            "uses_source_oracle_initial_amounts": initialization.get("source_oracle_initial_amounts"),
            "feasible_initialization_accepted": feasible_initialization.get("accepted") is True,
            "feasible_initialization_margin": feasible_initialization.get("margin"),
            "direct_final_proof_attempted": continuation.get("direct_final_proof_attempted") is True,
            "direct_final_proof_accepted": continuation.get("direct_final_proof_accepted") is True,
            "final_proof_status": continuation.get("final_proof_status"),
            "final_stage_id": continuation.get("final_stage_id"),
            "final_lambda": continuation.get("final_lambda"),
            "stage_count": continuation.get("stage_count"),
            "physical_proof_corrector_attempted": physical_corrector.get("attempted") is True,
            "physical_proof_corrector_accepted": physical_corrector.get("accepted") is True,
            "physical_proof_corrector_status": physical_corrector.get("status"),
            "physical_proof_corrector_rejection_reason": physical_corrector.get("rejection_reason"),
            "physical_proof_corrector_initial_reaction_stationarity_inf_norm": _as_float(
                physical_corrector, "initial_reaction_stationarity_inf_norm"
            ),
            "physical_proof_corrector_final_reaction_stationarity_inf_norm": _as_float(
                physical_corrector, "final_reaction_stationarity_inf_norm"
            ),
            "physical_proof_corrector_scaled_reaction_stationarity_inf_norm": _as_float(
                physical_corrector_metrics, "scaled_reaction_stationarity_inf_norm"
            ),
            "physical_proof_corrector_final_balance_inf_norm": _as_float(
                physical_corrector, "final_balance_inf_norm"
            ),
        }
        rows.append(row)
        if row["solver_status"] != "success":
            blockers.append(f"mea_loading_{loading}_solver_status_mismatch")
        if row["application_status"] != "solve_succeeded":
            blockers.append(f"mea_loading_{loading}_application_status_mismatch")
        if row["accepted"] is not True:
            blockers.append(f"mea_loading_{loading}_not_accepted")
        if row["uses_source_oracle_initial_amounts"] is not False:
            blockers.append(f"mea_loading_{loading}_source_oracle_seeded")
        if row["seed_source"] != "max_min_feasible_interior":
            blockers.append(f"mea_loading_{loading}_seed_source_mismatch")
        if row["feasible_initialization_accepted"] is not True:
            blockers.append(f"mea_loading_{loading}_feasible_initialization_rejected")
        if row["final_proof_status"] != "accepted":
            blockers.append(f"mea_loading_{loading}_final_proof_status_mismatch")
        if not math.isclose(float(row["final_lambda"] or 0.0), 1.0, rel_tol=0.0, abs_tol=1.0e-12):
            blockers.append(f"mea_loading_{loading}_final_lambda_mismatch")
        if row["direct_final_proof_accepted"] and row["physical_proof_corrector_attempted"]:
            blockers.append(f"mea_loading_{loading}_direct_proof_labeled_after_corrector")
        if row["physical_proof_corrector_attempted"] and row["physical_proof_corrector_accepted"] is not True:
            blockers.append(f"mea_loading_{loading}_physical_proof_corrector_rejected")
        if row["physical_proof_corrector_attempted"]:
            if row["physical_proof_corrector_rejection_reason"] not in ("", None):
                blockers.append(f"mea_loading_{loading}_physical_proof_corrector_rejection_reason")
            if row["physical_proof_corrector_initial_reaction_stationarity_inf_norm"] <= tolerances["affinity_abs"]:
                blockers.append(f"mea_loading_{loading}_physical_proof_corrector_initial_affinity_not_hard")
            if row["physical_proof_corrector_final_reaction_stationarity_inf_norm"] > tolerances["affinity_abs"]:
                blockers.append(f"mea_loading_{loading}_physical_proof_corrector_final_affinity_above_tolerance")
            if row["physical_proof_corrector_final_balance_inf_norm"] > tolerances["balance_abs"]:
                blockers.append(f"mea_loading_{loading}_physical_proof_corrector_final_balance_above_tolerance")
        if row["max_mole_fraction_abs_error"] > tolerances["mole_fraction_abs"]:
            blockers.append(f"mea_loading_{loading}_mole_fraction_error_above_tolerance")
        if row["balance_inf_norm"] > tolerances["balance_abs"]:
            blockers.append(f"mea_loading_{loading}_balance_above_tolerance")
        if row["reaction_stationarity_inf_norm"] > tolerances["affinity_abs"]:
            blockers.append(f"mea_loading_{loading}_affinity_above_tolerance")
        if not proof_metrics:
            blockers.append(f"mea_loading_{loading}_proof_metrics_missing")
        if not math.isclose(
            row["unscaled_reaction_stationarity_inf_norm"],
            row["reaction_stationarity_inf_norm"],
            rel_tol=0.0,
            abs_tol=1.0e-14,
        ):
            blockers.append(f"mea_loading_{loading}_proof_metrics_unscaled_affinity_mismatch")
        if not math.isfinite(row["scaled_reaction_stationarity_inf_norm"]):
            blockers.append(f"mea_loading_{loading}_proof_metrics_scaled_affinity_missing")
        if row["reconstructed_loading_abs_error"] > tolerances["loading_abs"]:
            blockers.append(f"mea_loading_{loading}_loading_above_tolerance")
        if abs(charge) > tolerances["charge_abs"]:
            blockers.append(f"mea_loading_{loading}_charge_above_tolerance")
    return {
        "status": "complete" if not blockers else "blocked",
        "blockers": sorted(set(blockers)),
        "source": "MEA-Thermodynamics Smith-Missen Phase 1 retained fixture",
        "public_route": "reactive_speciation",
        "loading_grid": list(_MEA_EXPECTED_MOLE_FRACTIONS),
        "seed_policy": REQUIRED_MEA_SEED_POLICY,
        "uses_source_oracle_initial_amounts": False,
        "solver_options": {
            "max_iterations": solver_options.max_iterations,
            "tolerance": solver_options.tolerance,
        },
        "tolerances": tolerances,
        "rows": rows,
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
            "proof_metrics": dict(result.get("proof_metrics") or {}),
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
        retained_mea_evidence = mea_retained_artifact_evidence()
        report["mea_retained_artifact_evidence"] = retained_mea_evidence
        blockers.extend(str(blocker) for blocker in retained_mea_evidence["blockers"])
        mea_evidence = mea_speciation_public_sweep_evidence()
        report["mea_speciation_evidence"] = mea_evidence
        blockers.extend(str(blocker) for blocker in mea_evidence["blockers"])
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
