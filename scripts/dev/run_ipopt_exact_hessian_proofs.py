from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

try:
    from scripts.dev.native_runtime_env import apply_native_runtime_env, apply_to_current_process
except ModuleNotFoundError:
    from native_runtime_env import apply_native_runtime_env, apply_to_current_process


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "build" / "generated" / "ipopt_exact_hessian_proofs"
SUMMARY_PREFIX = "IPOPT_PROOF_SUMMARY "
HYDROCARBON_COMPONENTS = ("Methane", "Ethane", "Propane")
HYDROCARBON_TEMPERATURE = 233.15
HYDROCARBON_BUBBLE_PRESSURE = 1_276_369.4735856401
HYDROCARBON_LIQUID_COMPOSITION = [0.1, 0.3, 0.6]
HYDROCARBON_VAPOR_COMPOSITION = [0.7246628928343289, 0.20293191372324873, 0.0724051934424223]
HYDROCARBON_FLASH_FEED = [
    0.5 * (liquid + vapor)
    for liquid, vapor in zip(HYDROCARBON_LIQUID_COMPOSITION, HYDROCARBON_VAPOR_COMPOSITION, strict=True)
]
CASES = ("bubble_pressure", "flash")


def _hydrocarbon_workbook_mixture():
    from epcsaft.state.native_adapter import ePCSAFTMixture

    params = {
        "m": np.asarray([1.0, 1.6069, 2.0020]),
        "s": np.asarray([3.7039, 3.5206, 3.6184]),
        "e": np.asarray([150.03, 191.42, 208.11]),
        "k_ij": np.asarray(
            [
                [0.0, 3.0e-4, 1.15e-2],
                [3.0e-4, 0.0, 5.10e-3],
                [1.15e-2, 5.10e-3, 0.0],
            ],
            dtype=float,
        ),
    }
    return ePCSAFTMixture.from_params(params, species=HYDROCARBON_COMPONENTS)


def _selector_request(case: str) -> dict[str, Any]:
    if case == "bubble_pressure":
        return {
            "route": "bubble_pressure",
            "temperature": HYDROCARBON_TEMPERATURE,
            "composition": HYDROCARBON_LIQUID_COMPOSITION,
            "composition_role": "liquid",
        }
    if case == "flash":
        return {
            "route": "neutral_tp_flash",
            "temperature": HYDROCARBON_TEMPERATURE,
            "pressure": HYDROCARBON_BUBBLE_PRESSURE,
            "composition": HYDROCARBON_FLASH_FEED,
            "composition_role": "feed",
        }
    raise SystemExit(f"Unknown proof case: {case}")


def _phase_totals(payload: dict[str, Any]) -> list[float]:
    postsolve = payload.get("postsolve")
    if isinstance(postsolve, dict) and isinstance(postsolve.get("phase_amount_totals"), list):
        return [float(value) for value in postsolve["phase_amount_totals"]]
    return [float(sum(phase_amounts)) for phase_amounts in payload.get("phase_amounts", [])]


def _summary_from_payload(case: str, request: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    postsolve = payload.get("postsolve")
    postsolve = postsolve if isinstance(postsolve, dict) else {}
    phase_totals = _phase_totals(payload)
    total_amount = sum(phase_totals)
    phase_fractions = [amount / total_amount for amount in phase_totals] if total_amount > 0.0 else []
    return {
        "case": case,
        "request": request,
        "status": str(payload.get("status", "")),
        "solver_status": str(payload.get("solver_status", "")),
        "accepted": bool(payload.get("accepted", False)),
        "solver_accepted": bool(payload.get("solver_accepted", False)),
        "route": str(payload.get("route", "")),
        "selector_family": str(payload.get("selector_family", "")),
        "activation_compiler": str(payload.get("activation_compiler", "")),
        "hessian_approximation": str(payload.get("hessian_approximation", "")),
        "hessian_backend": str(payload.get("hessian_backend", "")),
        "exact_hessian_available": bool(payload.get("exact_hessian_available", False)),
        "eval_h_calls": int(payload.get("eval_h_calls", 0)),
        "iteration_count": int(payload.get("iteration_count", 0)),
        "iteration_history_size": int(payload.get("iteration_history_size", 0)),
        "objective": float(payload.get("objective", 0.0)),
        "phase_amounts": payload.get("phase_amounts", []),
        "phase_amount_totals": phase_totals,
        "phase_fractions": phase_fractions,
        "phase_volumes": payload.get("phase_volumes", []),
        "phase_compositions": postsolve.get("phase_compositions", []),
        "phase_densities_mol_m3": postsolve.get("phase_densities", []),
        "postsolve": {
            "accepted": bool(postsolve.get("accepted", False)),
            "stability_checked": bool(postsolve.get("stability_checked", False)),
            "stability_accepted": bool(postsolve.get("stability_accepted", False)),
            "candidate_completeness_accepted": bool(postsolve.get("candidate_completeness_accepted", False)),
            "phase_set_status": str(postsolve.get("phase_set_status", "")),
            "phase_discovery_backend": str(postsolve.get("phase_discovery_backend", "")),
            "stability_certificate": str(postsolve.get("stability_certificate", "")),
            "material_balance_norm": float(postsolve.get("material_balance_norm", 0.0)),
            "pressure_consistency_norm": float(postsolve.get("pressure_consistency_norm", 0.0)),
            "chemical_potential_consistency_norm": float(
                postsolve.get("chemical_potential_consistency_norm", 0.0)
            ),
            "ln_fugacity_consistency_norm": float(postsolve.get("ln_fugacity_consistency_norm", 0.0)),
            "phase_distance": float(postsolve.get("phase_distance", 0.0)),
            "minimum_phase_fraction": float(postsolve.get("minimum_phase_fraction", 0.0)),
            "min_tpd": float(postsolve.get("min_tpd", 0.0)),
            "candidate_mass_balance_norm": float(postsolve.get("candidate_mass_balance_norm", 0.0)),
            "tpd_candidate_count": int(postsolve.get("tpd_candidate_count", 0)),
            "unique_candidate_count": int(postsolve.get("unique_candidate_count", 0)),
            "selected_candidate_count": int(postsolve.get("selected_candidate_count", 0)),
        },
        "stability_certificate": payload.get("stability_certificate", {}),
    }


def _run_selector_child(case: str) -> dict[str, Any]:
    from epcsaft_equilibrium._native import extension_native_core

    mix = _hydrocarbon_workbook_mixture()
    request = _selector_request(case)
    _core = extension_native_core()
    payload = _core._native_equilibrium_selector_route_result(
        mix._native,
        request,
        200,
        1.0e-8,
        0.0,
        "auto",
        8,
        1.0e-8,
        1.0e-3,
        1.0e-8,
        1.0e-8,
        {},
        print_level=5,
    )
    return _summary_from_payload(case, request, payload)


def _run_child(case: str) -> int:
    apply_to_current_process()
    summary = _run_selector_child(case)
    print(SUMMARY_PREFIX + json.dumps(summary, sort_keys=True))
    return 0


def _parse_summary(log_text: str, case: str) -> dict[str, Any]:
    for line in reversed(log_text.splitlines()):
        if line.startswith(SUMMARY_PREFIX):
            return json.loads(line[len(SUMMARY_PREFIX) :])
    raise RuntimeError(f"{case} proof did not emit a summary line.")


def _assert_proof_summary(summary: dict[str, Any]) -> None:
    case = summary["case"]
    if not summary["accepted"]:
        raise RuntimeError(f"{case} proof was not accepted: {summary}")
    if not summary["solver_accepted"]:
        raise RuntimeError(f"{case} proof solver was not accepted: {summary}")
    if summary["hessian_approximation"] != "exact":
        raise RuntimeError(f"{case} proof did not use exact Hessians: {summary}")
    if summary["hessian_backend"] == "limited-memory":
        raise RuntimeError(f"{case} proof silently used limited-memory Hessians: {summary}")
    if not summary["exact_hessian_available"]:
        raise RuntimeError(f"{case} proof did not report exact Hessian availability: {summary}")
    if summary["eval_h_calls"] <= 0:
        raise RuntimeError(f"{case} proof did not call eval_h: {summary}")


def _assert_log_contains_ipopt_output(case: str, log_text: str) -> None:
    required = ("Ipopt", "Number of Iterations", "EXIT:")
    missing = [token for token in required if token not in log_text]
    if missing:
        raise RuntimeError(f"{case} proof log is missing Ipopt output tokens: {missing}")


def _run_parent(cases: list[str], output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    apply_native_runtime_env(env)
    src_path = str(REPO_ROOT / "src")
    equilibrium_src_path = str(REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    pythonpath_entries = [src_path, equilibrium_src_path]
    if existing_pythonpath:
        pythonpath_entries.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
    summaries: list[dict[str, Any]] = []
    for case in cases:
        command = [sys.executable, str(Path(__file__).resolve()), "--case", case, "--child"]
        result = subprocess.run(command, cwd=REPO_ROOT, env=env, text=True, capture_output=True, check=False)
        log_text = result.stdout
        if result.stderr:
            log_text += "\n[stderr]\n" + result.stderr
        log_path = output_dir / f"{case}.log"
        log_path.write_text(log_text, encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(f"{case} proof failed with exit {result.returncode}; see {log_path}")
        summary = _parse_summary(log_text, case)
        _assert_proof_summary(summary)
        _assert_log_contains_ipopt_output(case, log_text)
        summary["log_path"] = str(log_path)
        summaries.append(summary)
        print(f"{case}: accepted exact Hessian proof captured at {log_path}")
        print(SUMMARY_PREFIX + json.dumps(summary, sort_keys=True))
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps({"proofs": summaries}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"summary: {summary_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture representative native Ipopt exact-Hessian proof logs.")
    parser.add_argument("--case", choices=CASES, action="append", dest="cases")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    cases = args.cases or list(CASES)
    if args.child:
        if len(cases) != 1:
            raise SystemExit("--child requires exactly one --case")
        return _run_child(cases[0])
    return _run_parent(cases, args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
