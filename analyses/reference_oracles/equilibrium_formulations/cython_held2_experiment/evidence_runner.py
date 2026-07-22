"""Generate compact installed-wheel evidence for the Cython HELD2 experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import cython_held2_experiment as held2


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _installed_origin() -> dict[str, Any]:
    origin = Path(held2.__file__).resolve()
    return {
        "kind": "installed_site_packages",
        "relative_path": "/".join(origin.parts[-3:]),
        "site_packages": "site-packages" in origin.parts,
    }


def _phase_summary(phase: dict[str, Any]) -> dict[str, Any]:
    return {
        key: phase[key]
        for key in (
            "id",
            "beta",
            "modified_fraction",
            "volume",
            "packing_fraction",
            "relative_pressure_residual",
            "charge_residual",
        )
    }


def _manufactured_summary(wheel: Path) -> dict[str, Any]:
    cases = {name: held2.manufactured_full_demo(name) for name in ("stable", "unstable", "feedback", "trace")}
    inactive = held2.manufactured_stage3_demo("inactive")
    return {
        "schema_version": 1,
        "result": "pass",
        "authority_effect": "none",
        "artifact": {
            "filename": wheel.name,
            "sha256": _sha256(wheel),
            "import_origin": _installed_origin(),
            "editable": False,
        },
        "cases": {
            name: {
                "outcome": result["outcome"],
                "solver_status": result["solver_status"],
                "numerical_status": result["numerical_status"],
                "physical_status": result["physical_status"],
                "step_ledger": result["step_ledger"],
            }
            for name, result in cases.items()
        },
        "unstable_phases": [_phase_summary(phase) for phase in cases["unstable"]["stage3"]["phases"]],
        "feedback_step9": cases["feedback"]["stage3"]["step9"],
        "trace": cases["trace"]["trace"],
        "inactive_retirement": {
            "initial_dual_pullback": inactive["initial_solve"]["dual_pullback"],
            "initial_kkt_inf_norm": inactive["initial_solve"]["stationarity_inf_norm"],
            "initial_complementarity_inf_norm": inactive["initial_solve"]["complementarity_inf_norm"],
            "retirement": inactive["retirement"],
            "active_set_confirmation": inactive["active_set_confirmation"],
            "final_phases": [_phase_summary(phase) for phase in inactive["phases"]],
        },
        "claim_boundary": {
            "manufactured_controller_conformance_only": True,
            "global_minimum_proven": False,
            "production_authority": False,
        },
    }


def _perdomo_summary(wheel: Path) -> dict[str, Any]:
    result = held2.run_perdomo_table3_demo()
    stage1 = result["stage1"]
    reference = stage1.get("reference", {})
    attempts = stage1.get("attempts", [])
    payload = {
        "schema_version": 1,
        "result": "recorded",
        "authority_effect": "none",
        "artifact": {
            "filename": wheel.name,
            "sha256": _sha256(wheel),
            "import_origin": _installed_origin(),
            "editable": False,
        },
        "source_case": result["source_case"],
        "temperature_k": result["temperature_k"],
        "pressure_pa": result["pressure_pa"],
        "feed_amounts": result["feed_amounts"],
        "feed_modified_ion_fraction": result["feed_modified_ion_fraction"],
        "source_eos": result["source_eos"],
        "experiment_eos": result["experiment_eos"],
        "comparison_scope": result["comparison_scope"],
        "parameter_tuning": result["parameter_tuning"],
        "terminal": result["terminal"],
        "solver_status": result["solver_status"],
        "numerical_status": result["numerical_status"],
        "physical_status": result["physical_status"],
        "stage1": {
            "outcome": stage1["outcome"],
            "search_status": stage1["search_status"],
            "reference_outcome": reference.get("outcome"),
            "reference_scan_status": reference.get("scan_status"),
            "attempt_count": len(attempts),
            "solver_passed": sum(attempt.get("solver_convergence") == "passed" for attempt in attempts),
            "numerical_passed": sum(attempt.get("numerical_convergence") == "passed" for attempt in attempts),
            "physical_passed": sum(attempt.get("physical_validity") == "passed" for attempt in attempts),
            "attempt_objectives": [attempt.get("objective") for attempt in attempts],
        },
        "stage2_outcome": None if result["stage2"] is None else result["stage2"]["outcome"],
        "stage3_outcome": None if result["stage3"] is None else result["stage3"]["outcome"],
        "interpretation": (
            "The installed ePC-SAFT experiment stopped fail-closed in Stage I after all four local "
            "solvers returned but only two attempts passed numerical certification and no trial passed "
            "physical certification. This is not a reproduction failure of Perdomo's SAFT-gamma-Mie result."
        ),
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--manufactured-output", required=True, type=Path)
    parser.add_argument("--perdomo-output", required=True, type=Path)
    arguments = parser.parse_args()
    if not arguments.wheel.is_file():
        raise SystemExit(f"wheel does not exist: {arguments.wheel}")
    manufactured = _manufactured_summary(arguments.wheel)
    perdomo = _perdomo_summary(arguments.wheel)
    arguments.manufactured_output.write_text(
        json.dumps(manufactured, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    arguments.perdomo_output.write_text(
        json.dumps(perdomo, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
