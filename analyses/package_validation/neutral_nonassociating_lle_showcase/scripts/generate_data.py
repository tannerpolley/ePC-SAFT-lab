from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
SHARED_RESULTS = ANALYSIS_ROOT / "shared" / "results"
FIXTURE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "perfluorohexane_hexane"
)

for import_root in (
    REPO_ROOT,
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from scripts.validation import check_neutral_lle_showcase


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _single_row(path: Path) -> dict[str, str]:
    rows = _read_csv(path)
    if len(rows) != 1:
        raise ValueError(f"expected exactly one row in {path}")
    return rows[0]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _phase_points(payload: dict[str, Any]) -> list[dict[str, Any]]:
    feed = _single_row(FIXTURE_DIR / "feed_compositions.csv")
    source = _single_row(FIXTURE_DIR / "experimental_tielines.csv")
    sampled_compositions = payload["comparison"]["sampled_phase_compositions"]
    sampled_fractions = payload["comparison"]["sampled_phase_fractions"]
    temperature = float(source["temperature_K"])
    pressure = float(source["pressure_Pa"])
    rows = [
        {
            "role": "source_liquid1",
            "series": "source",
            "temperature_K": temperature,
            "pressure_Pa": pressure,
            "x_perfluorohexane": float(source["liquid1_x1"]),
            "x_hexane": float(source["liquid1_x2"]),
            "phase_fraction": float(feed["liquid1_phase_fraction"]),
        },
        {
            "role": "source_liquid2",
            "series": "source",
            "temperature_K": temperature,
            "pressure_Pa": pressure,
            "x_perfluorohexane": float(source["liquid2_x1"]),
            "x_hexane": float(source["liquid2_x2"]),
            "phase_fraction": float(feed["liquid2_phase_fraction"]),
        },
    ]
    for index, composition in enumerate(sampled_compositions, start=1):
        rows.append(
            {
                "role": f"sampled_liquid{index}",
                "series": "internal_sampled_candidate_diagnostic",
                "temperature_K": temperature,
                "pressure_Pa": pressure,
                "x_perfluorohexane": float(composition[0]),
                "x_hexane": float(composition[1]),
                "phase_fraction": float(sampled_fractions[index - 1]),
            }
        )
    rows.append(
        {
            "role": "feed",
            "series": "constructed_feed",
            "temperature_K": float(feed["temperature_K"]),
            "pressure_Pa": float(feed["pressure_Pa"]),
            "x_perfluorohexane": float(feed["z1"]),
            "x_hexane": float(feed["z2"]),
            "phase_fraction": 1.0,
        }
    )
    return rows


def _component_errors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    source = _single_row(FIXTURE_DIR / "experimental_tielines.csv")
    sampled = payload["comparison"]["sampled_phase_compositions"]
    rows: list[dict[str, Any]] = []
    for label in ("liquid1", "liquid2"):
        actual = sampled[0 if label == "liquid1" else 1]
        expected = [float(source[f"{label}_x1"]), float(source[f"{label}_x2"])]
        for component, expected_value, actual_value in zip(("perfluorohexane", "hexane"), expected, actual, strict=True):
            rows.append(
                {
                    "phase": label,
                    "component": component,
                    "source_mole_fraction": expected_value,
                    "sampled_mole_fraction": float(actual_value),
                    "absolute_error": abs(expected_value - float(actual_value)),
                }
            )
    return rows


def _tolerance_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    thresholds = _read_json(FIXTURE_DIR / "thresholds.json")
    diagnostic = payload["diagnostic"]
    comparison = payload["comparison"]
    compositions = comparison["sampled_phase_compositions"]
    phase_distance = max(
        abs(left - right)
        for left, right in zip(compositions[0], compositions[1], strict=True)
    )
    rows = [
        {
            "metric": "composition_abs",
            "observed_abs": comparison["max_composition_abs_error"],
            "limit": thresholds["composition_abs"],
            "direction": "max",
            "unit": "mole_fraction",
        },
        {
            "metric": "phase_fraction_abs",
            "observed_abs": comparison["max_phase_fraction_abs_error"],
            "limit": thresholds["phase_fraction_abs"],
            "direction": "max",
            "unit": "phase_fraction",
        },
        {
            "metric": "material_balance_abs",
            "observed_abs": diagnostic["candidate_mass_balance_norm"],
            "limit": thresholds["material_balance_abs"],
            "direction": "max",
            "unit": "mole_balance",
        },
        {
            "metric": "phase_distance_min",
            "observed_abs": phase_distance,
            "limit": thresholds["phase_distance_min"],
            "direction": "min",
            "unit": "mole_fraction",
        },
    ]
    for row in rows:
        observed = float(row["observed_abs"])
        limit = float(row["limit"])
        if row["direction"] == "max":
            row["margin_ratio"] = observed / limit if limit > 0 else math.inf
            row["accepted"] = observed <= limit
        else:
            row["margin_ratio"] = limit / observed if observed > 0 else math.inf
            row["accepted"] = observed >= limit
    return rows


def _held_stage_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostic = payload["diagnostic"]
    receipt = payload["native_freshness_receipt"]
    gates = [
        ("deterministic_screening", "Deterministic screening", diagnostic["deterministic_screening_status"] == "completed"),
        ("continuous_tpd_minimization", "Continuous TPD minimization", diagnostic["continuous_tpd_status"] == "converged"),
        ("held_stage_i_stability", "HELD Stage I stability", diagnostic["held_stage_i_status"] in {"negative_tpd_candidate_found", "no_negative_tpd_candidate_found"}),
        (
            "sampled_candidate_bound_audit",
            "Sampled-candidate bound audit",
            diagnostic["held_stage_ii_status"] == "sampled_candidate_audit_complete"
            and diagnostic["held_stage_ii_dual_loop_status"] == "not_performed",
        ),
    ]
    rows = []
    for order, (gate, label, accepted) in enumerate(gates, start=1):
        rows.append(
            {
                "order": order,
                "gate": gate,
                "label": label,
                "status": "observed" if accepted else "missing",
                "accepted": accepted,
                "native_git_commit": receipt["git_commit"],
                "native_module_path": receipt["native_module_path"],
                "native_build_refresh_command": receipt["build_refresh_command"],
                "native_checker_command": " ".join(str(item) for item in receipt["checker_command"]),
            }
        )
    return rows


def main() -> int:
    payload = check_neutral_lle_showcase.evaluate_case_dir(
        FIXTURE_DIR,
        checker_command=[
            "uv",
            "run",
            "--no-sync",
            "python",
            "analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py",
        ],
    )
    if not payload["complete"]:
        raise RuntimeError("neutral LLE showcase checker did not complete: " + ", ".join(payload["blockers"]))

    SHARED_RESULTS.mkdir(parents=True, exist_ok=True)
    _write_json(SHARED_RESULTS / "neutral_lle_showcase_check.json", payload)
    _write_json(
        SHARED_RESULTS / "run_summary.json",
        {
            "case_label": payload["case_label"],
            "family_label": payload["family_label"],
            "complete": payload["complete"],
            "diagnostic_status": payload["status"],
            "production_route_admitted": payload["production_route_admitted"],
            "global_phase_set_certified": payload["global_phase_set_certified"],
            "max_composition_abs_error": payload["comparison"]["max_composition_abs_error"],
            "max_phase_fraction_abs_error": payload["comparison"]["max_phase_fraction_abs_error"],
            "scope": "internal sampled-candidate validation for one neutral binary",
        },
    )
    _write_csv(
        SHARED_RESULTS / "neutral_lle_phase_points.csv",
        [
            "role",
            "series",
            "temperature_K",
            "pressure_Pa",
            "x_perfluorohexane",
            "x_hexane",
            "phase_fraction",
        ],
        _phase_points(payload),
    )
    _write_csv(
        SHARED_RESULTS / "neutral_lle_component_errors.csv",
        ["phase", "component", "source_mole_fraction", "sampled_mole_fraction", "absolute_error"],
        _component_errors(payload),
    )
    _write_csv(
        SHARED_RESULTS / "neutral_lle_tolerance_summary.csv",
        ["metric", "observed_abs", "limit", "direction", "unit", "margin_ratio", "accepted"],
        _tolerance_rows(payload),
    )
    _write_csv(
        SHARED_RESULTS / "held_stage_status.csv",
        [
            "order",
            "gate",
            "label",
            "status",
            "accepted",
            "native_git_commit",
            "native_module_path",
            "native_build_refresh_command",
            "native_checker_command",
        ],
        _held_stage_rows(payload),
    )
    _write_csv(
        SHARED_RESULTS / "neutral_lle_source_binodal_points.csv",
        [
            "source_dataset",
            "row_index",
            "temperature_K",
            "pressure_kPa",
            "component_1",
            "component_2",
            "x_perfluorohexane",
            "combined_temperature_uncertainty_K",
            "method",
        ],
        _read_csv(FIXTURE_DIR / "source_binodal_points.csv"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
