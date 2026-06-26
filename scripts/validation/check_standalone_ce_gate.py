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
    chemical_equilibrium_bindings = {
        name for name in dir(core) if name.startswith("_native_chemical_equilibrium")
    }
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


def evaluate_standalone_ce_gate(*, require_single_nlp_path: bool) -> dict[str, Any]:
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
    report["blockers"] = blockers
    report["status"] = "complete" if not blockers else "blocked"
    if require_single_nlp_path and blockers:
        report["status"] = "blocked"
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON evidence.")
    parser.add_argument("--require-single-nlp-path", action="store_true")
    args = parser.parse_args(argv)

    report = evaluate_standalone_ce_gate(require_single_nlp_path=args.require_single_nlp_path)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
