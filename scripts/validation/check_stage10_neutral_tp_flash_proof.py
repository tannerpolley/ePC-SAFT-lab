from __future__ import annotations

import argparse
import csv
from contextlib import contextmanager
import itertools
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for import_root in (REPO_ROOT, SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env
from scripts.validation import check_equilibrium_benchmark_readiness as readiness
from scripts.validation import check_stage9_phase_discovery_evidence as stage9_evidence

apply_native_runtime_env(os.environ)

from epcsaft.state.native_adapter import ePCSAFTMixture
import epcsaft._core as _core

DEFAULT_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_tp_flash"
    / "hydrocarbon_workbook_flash"
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


@contextmanager
def _suppress_native_stdout():
    sys.stdout.flush()
    saved_stdout = os.dup(1)
    try:
        with tempfile.TemporaryFile(mode="w+b") as sink:
            os.dup2(sink.fileno(), 1)
            yield
            sys.stdout.flush()
    finally:
        os.dup2(saved_stdout, 1)
        os.close(saved_stdout)


@contextmanager
def _redirect_native_stdout_to_stderr():
    sys.stdout.flush()
    sys.stderr.flush()
    saved_stdout = os.dup(1)
    try:
        os.dup2(2, 1)
        yield
        sys.stdout.flush()
    finally:
        os.dup2(saved_stdout, 1)
        os.close(saved_stdout)


def _indexed_columns(row: dict[str, str], prefix: str) -> list[str]:
    return readiness._indexed_columns(row, prefix)


def _composition(row: dict[str, str]) -> list[float]:
    return [float(row[column]) for column in _indexed_columns(row, "x")]


def _case_rows(case_dir: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(case_dir / "phase_splits.csv")
    case_keys = {row["case_key"] for row in rows}
    if len(case_keys) != 1:
        raise ValueError(f"Stage 10 proof expects exactly one case_key, got {sorted(case_keys)}")
    return {row["phase"]: row for row in rows}


def _species(case_rows: dict[str, dict[str, str]], metadata: dict[str, Any]) -> list[str]:
    if isinstance(metadata.get("species"), list) and metadata["species"]:
        return [str(item) for item in metadata["species"]]
    feed = case_rows["feed"]
    return [feed[column] for column in _indexed_columns(feed, "component_")]


def _mixture(case_dir: Path, species: list[str]) -> ePCSAFTMixture:
    parameter_rows = {row["species"]: row for row in _read_csv(case_dir / "pc_saft_parameters.csv")}
    if set(parameter_rows) != set(species):
        raise ValueError("pc_saft_parameters.csv species do not match phase_splits.csv species")
    index = {name: position for position, name in enumerate(species)}
    k_ij = np.zeros((len(species), len(species)), dtype=float)
    for row in _read_csv(case_dir / "binary_interactions.csv"):
        i = index[row["component_i"]]
        j = index[row["component_j"]]
        value = float(row["k_ij"])
        k_ij[i, j] = value
        k_ij[j, i] = value
    return ePCSAFTMixture.from_params(
        {
            "m": np.asarray([float(parameter_rows[name]["m"]) for name in species], dtype=float),
            "s": np.asarray([float(parameter_rows[name]["s_A"]) for name in species], dtype=float),
            "e": np.asarray([float(parameter_rows[name]["e_over_k_K"]) for name in species], dtype=float),
            "k_ij": k_ij,
        },
        species=species,
    )


def _phase_totals(route_payload: dict[str, Any]) -> list[float]:
    postsolve = route_payload.get("postsolve")
    if isinstance(postsolve, dict) and isinstance(postsolve.get("phase_amount_totals"), list):
        return [float(value) for value in postsolve["phase_amount_totals"]]
    return [float(sum(phase_amounts)) for phase_amounts in route_payload.get("phase_amounts", [])]


def _material_balance_row(case_dir: Path) -> dict[str, str]:
    rows = _read_csv(case_dir / "material_balance_readiness.csv")
    if len(rows) != 1:
        raise ValueError("Stage 10 proof expects exactly one material-balance readiness row")
    return rows[0]


def _expected_phase_fractions(case_dir: Path) -> dict[str, float]:
    row = _material_balance_row(case_dir)
    return {
        "vapor": float(row["vapor_fraction"]),
        "liquid": float(row["liquid_fraction"]),
    }


def _best_phase_match(
    actual_compositions: list[list[float]],
    actual_fractions: list[float],
    expected_compositions: dict[str, list[float]],
    expected_fractions: dict[str, float],
) -> dict[str, Any]:
    labels = list(expected_compositions)
    best: dict[str, Any] | None = None
    for permutation in itertools.permutations(range(len(actual_compositions)), len(labels)):
        composition_errors = []
        fraction_errors = []
        mapping: dict[str, int] = {}
        for label, actual_index in zip(labels, permutation, strict=True):
            mapping[label] = actual_index
            expected = expected_compositions[label]
            actual = actual_compositions[actual_index]
            composition_errors.append(max(abs(left - right) for left, right in zip(expected, actual, strict=True)))
            fraction_errors.append(abs(expected_fractions[label] - actual_fractions[actual_index]))
        candidate = {
            "phase_index_by_expected_label": mapping,
            "max_composition_abs_error": max(composition_errors),
            "max_phase_fraction_abs_error": max(fraction_errors),
        }
        if best is None or (
            candidate["max_composition_abs_error"] + candidate["max_phase_fraction_abs_error"]
            < best["max_composition_abs_error"] + best["max_phase_fraction_abs_error"]
        ):
            best = candidate
    if best is None:
        raise ValueError("No phase match could be constructed")
    return best


def _run_route_payload(case_dir: Path, metadata: dict[str, Any], *, debug: bool) -> dict[str, Any]:
    case_rows = _case_rows(case_dir)
    species = _species(case_rows, metadata)
    mix = _mixture(case_dir, species)
    feed = case_rows["feed"]
    request = {
        "route": "neutral_tp_flash",
        "temperature": float(feed["temperature_K"]),
        "pressure": float(feed["pressure_MPa"]) * 1.0e6,
        "composition": _composition(feed),
        "composition_role": "feed",
    }
    return dict(
        _core._native_equilibrium_selector_route_result(
            mix._native,
            request,
            260,
            1.0e-8,
            0.0,
            "auto",
            50 if debug else 8,
            1.0e-8,
            1.0e-3,
            1.0e-8,
            1.0e-8,
            {},
            linear_solver="auto",
            print_level=5 if debug else 0,
        )
    )


def _run_route(
    case_dir: Path,
    metadata: dict[str, Any],
    *,
    debug: bool,
    show_native_output: bool,
    redirect_native_output_to_stderr: bool,
) -> dict[str, Any]:
    if show_native_output:
        return _run_route_payload(case_dir, metadata, debug=debug)
    if redirect_native_output_to_stderr:
        with _redirect_native_stdout_to_stderr():
            return _run_route_payload(case_dir, metadata, debug=debug)
    with _suppress_native_stdout():
        return _run_route_payload(case_dir, metadata, debug=debug)


def evaluate_proof(
    case_dir: Path,
    stage9_evidence_payload: dict[str, Any] | None,
    *,
    debug: bool = False,
    show_native_output: bool = False,
    redirect_native_output_to_stderr: bool = False,
) -> dict[str, Any]:
    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    readiness_payload = readiness.evaluate_case_dir(case_dir, stage9_evidence_payload=stage9_evidence_payload)
    blockers = list(readiness_payload["blockers"])
    route_payload: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    route_accepted = False
    if readiness_payload["executable"]:
        route_payload = _run_route(
            case_dir,
            metadata,
            debug=debug,
            show_native_output=show_native_output,
            redirect_native_output_to_stderr=redirect_native_output_to_stderr,
        )
        postsolve = route_payload.get("postsolve")
        postsolve = postsolve if isinstance(postsolve, dict) else {}
        actual_compositions = [list(map(float, row)) for row in postsolve.get("phase_compositions", [])]
        phase_totals = _phase_totals(route_payload)
        total_amount = sum(phase_totals)
        actual_fractions = [amount / total_amount for amount in phase_totals] if total_amount > 0.0 else []
        case_rows = _case_rows(case_dir)
        expected_compositions = {
            "liquid": _composition(case_rows["liquid"]),
            "vapor": _composition(case_rows["vapor"]),
        }
        expected_fractions = _expected_phase_fractions(case_dir)
        comparison = _best_phase_match(
            actual_compositions,
            actual_fractions,
            expected_compositions,
            expected_fractions,
        )
        tolerances = metadata["acceptance_tolerances"]
        route_accepted = (
            route_payload.get("status") == "production_accepted"
            and route_payload.get("solver_status") == "success"
            and route_payload.get("application_status") == "solve_succeeded"
            and route_payload.get("accepted") is True
            and route_payload.get("hessian_approximation") == "exact"
            and route_payload.get("exact_hessian_available") is True
            and int(route_payload.get("eval_h_calls", 0)) > 0
            and postsolve.get("accepted") is True
            and postsolve.get("stability_accepted") is True
            and comparison["max_composition_abs_error"] <= tolerances["composition_abs"]
            and comparison["max_phase_fraction_abs_error"] <= tolerances["phase_fraction_abs"]
            and float(postsolve.get("material_balance_norm", math.inf)) <= tolerances["material_balance_abs"]
            and float(postsolve.get("pressure_consistency_norm", math.inf)) <= tolerances["pressure_abs_Pa"]
            and float(postsolve.get("ln_fugacity_consistency_norm", math.inf)) <= tolerances["ln_fugacity_abs"]
        )
        if not route_accepted:
            if route_payload.get("solver_status") != "success":
                blockers.append(f"stage10_route_solver_not_converged_{route_payload.get('solver_status', 'unknown')}")
            if route_payload.get("application_status") != "solve_succeeded":
                blockers.append(
                    f"stage10_route_application_not_converged_{route_payload.get('application_status', 'unknown')}"
                )
            blockers.append("stage10_route_proof_failed")
    proof_complete = readiness_payload["executable"] and route_accepted and not blockers
    route_summary = None
    if route_payload is not None:
        seed_attempts = list(route_payload.get("seed_attempts") or ())
        route_summary = {
            "status": route_payload.get("status"),
            "solver_status": route_payload.get("solver_status"),
            "application_status": route_payload.get("application_status"),
            "accepted": route_payload.get("accepted"),
            "hessian_approximation": route_payload.get("hessian_approximation"),
            "hessian_backend": route_payload.get("hessian_backend"),
            "exact_hessian_available": route_payload.get("exact_hessian_available"),
            "eval_h_calls": route_payload.get("eval_h_calls"),
            "ipopt_print_level": route_payload.get("ipopt_print_level"),
            "max_iterations": route_payload.get("max_iterations"),
            "iteration_count": route_payload.get("iteration_count"),
            "iteration_history_limit": route_payload.get("iteration_history_limit"),
            "iteration_history_size": route_payload.get("iteration_history_size"),
            "iteration_history": route_payload.get("iteration_history"),
            "scaled_acceptance_passed": route_payload.get("scaled_acceptance_passed"),
            "seed_attempt_count": len(seed_attempts),
            "seed_attempts": seed_attempts,
            "postsolve": route_payload.get("postsolve"),
        }
    return {
        "case_label": metadata["case_label"],
        "family_label": metadata["family_label"],
        "proof_status": "complete" if proof_complete else "blocked",
        "proof_complete": proof_complete,
        "readiness": readiness_payload,
        "route": route_summary,
        "comparison": comparison,
        "blockers": list(dict.fromkeys(blockers)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Stage 10 neutral TP flash executable proof.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    stage9_source = parser.add_mutually_exclusive_group(required=True)
    stage9_source.add_argument(
        "--stage9-evidence-json",
        type=Path,
        help="Read a previously generated Stage 9 evidence JSON payload.",
    )
    stage9_source.add_argument(
        "--generate-stage9-evidence",
        action="store_true",
        help="Explicitly generate Stage 9 route-refinement evidence before running the Stage 10 proof.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use Ipopt print_level=5, retain more iteration history, and expose native iteration output.",
    )
    parser.add_argument(
        "--require-proof",
        action="store_true",
        help="Return a failing exit code unless the Stage 10 proof completes.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.debug:
        os.environ["EPCSAFT_EQUILIBRIUM_DEBUG"] = "1"
    show_native_output = args.debug and not args.json
    redirect_native_output_to_stderr = args.debug and args.json
    if args.generate_stage9_evidence:
        stage9_payload = stage9_evidence.evaluate_stage9_evidence(
            include_route_refinement=True,
            show_native_output=show_native_output,
            redirect_native_output_to_stderr=redirect_native_output_to_stderr,
        )
        stage9_source = "generated"
    else:
        stage9_payload = readiness._read_optional_stage9_evidence(args.stage9_evidence_json)
        stage9_source = str(args.stage9_evidence_json)
    payload = evaluate_proof(
        args.case_dir,
        stage9_payload,
        debug=args.debug,
        show_native_output=show_native_output,
        redirect_native_output_to_stderr=redirect_native_output_to_stderr,
    )
    payload["stage9_evidence_source"] = stage9_source
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['case_label']}: {payload['proof_status']}")
        if payload["blockers"]:
            print("  blockers: " + ", ".join(str(item) for item in payload["blockers"]))
        route = payload.get("route") or {}
        if route:
            print(
                "  route: "
                f"solver={route.get('solver_status')} "
                f"application={route.get('application_status')} "
                f"iterations={route.get('iteration_count')}"
            )
            iteration_history = list(route.get("iteration_history") or ())
            if iteration_history:
                print("  last_ipopt_iterations:")
                for record in iteration_history[-5:]:
                    record = dict(record)
                    print(
                        "    "
                        f"iter={record.get('iteration')} "
                        f"objective={record.get('objective')} "
                        f"inf_pr={record.get('primal_infeasibility')} "
                        f"inf_du={record.get('dual_infeasibility')} "
                        f"mu={record.get('barrier_parameter')} "
                        f"alpha_pr={record.get('step_size_primal')} "
                        f"ls={record.get('step_trial_count')}"
                    )
        comparison = payload.get("comparison") or {}
        if comparison:
            print(
                "  comparison: "
                f"composition_abs={comparison.get('max_composition_abs_error')} "
                f"phase_fraction_abs={comparison.get('max_phase_fraction_abs_error')}"
            )
    if args.require_proof and not payload["proof_complete"]:
        print(f"{payload['case_label']} did not complete Stage 10 proof.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
