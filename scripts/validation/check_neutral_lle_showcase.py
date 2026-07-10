"""Check the retained Matsuda LLE fixture as an internal sampled-candidate diagnostic.

The diagnostic exercises native TPD candidate generation and a one-pass audit of
the sampled candidates. It does not solve a public LLE route and does not claim a
globally complete phase set.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from itertools import permutations
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
for import_root in (
    REPO_ROOT,
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core

from scripts.dev.native_runtime_env import apply_native_runtime_env
from scripts.validation import native_freshness

apply_native_runtime_env(os.environ)
_core = extension_native_core()

DEFAULT_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "perfluorohexane_hexane"
)
REQUIRED_FILES = (
    "metadata.json",
    "thresholds.json",
    "pure_component_parameters.csv",
    "binary_interactions.csv",
    "experimental_tielines.csv",
    "feed_compositions.csv",
)


def _read_json(path: Path) -> dict[str, Any]:
    return dict(json.loads(path.read_text(encoding="utf-8")))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _fixture_blockers(case_dir: Path) -> list[str]:
    blockers = [name for name in REQUIRED_FILES if not (case_dir / name).is_file()]
    if blockers:
        return [f"missing_required_file:{name}" for name in blockers]
    metadata = _read_json(case_dir / "metadata.json")
    if metadata.get("route") != "internal_neutral_lle_tpd_diagnostic":
        blockers.append("metadata_route_not_internal_tpd_diagnostic")
    if metadata.get("selector_route") != "neutral_lle":
        blockers.append("metadata_selector_route_mismatch")
    if metadata.get("evidence_scope") != "internal_sampled_candidate_diagnostic":
        blockers.append("metadata_evidence_scope_mismatch")
    if metadata.get("public_admission_state") != "closed":
        blockers.append("metadata_public_admission_not_closed")
    if metadata.get("global_held_proof") is not False:
        blockers.append("metadata_global_held_claim_present")
    if metadata.get("source_status") != "source_backed":
        blockers.append("metadata_source_not_source_backed")
    if metadata.get("expected_phase_count") != 2:
        blockers.append("metadata_expected_phase_count_mismatch")
    if len(_read_csv(case_dir / "experimental_tielines.csv")) != 1:
        blockers.append("expected_one_source_tieline")
    if len(_read_csv(case_dir / "feed_compositions.csv")) != 1:
        blockers.append("expected_one_feed_row")
    return blockers


def _build_mixture(case_dir: Path, species: list[str]) -> ePCSAFTMixture:
    pure = {row["species"]: row for row in _read_csv(case_dir / "pure_component_parameters.csv")}
    indices = {name: index for index, name in enumerate(species)}
    k_ij = np.zeros((len(species), len(species)), dtype=float)
    for row in _read_csv(case_dir / "binary_interactions.csv"):
        i = indices[row["component_i"]]
        j = indices[row["component_j"]]
        k_ij[i, j] = k_ij[j, i] = float(row["k_ij"])
    return ePCSAFTMixture.from_params(
        {
            "m": np.asarray([float(pure[name]["m"]) for name in species]),
            "s": np.asarray([float(pure[name]["s_A"]) for name in species]),
            "e": np.asarray([float(pure[name]["e_over_k_K"]) for name in species]),
            "k_ij": k_ij,
        },
        species=species,
    )


def _best_source_alignment(
    sampled: list[list[float]],
    source: list[list[float]],
) -> tuple[list[list[float]], tuple[int, ...], float]:
    best_order: tuple[int, ...] | None = None
    best_error = float("inf")
    for order in permutations(range(len(sampled))):
        error = max(
            abs(sampled[order[phase]][component] - source[phase][component])
            for phase in range(len(source))
            for component in range(len(source[phase]))
        )
        if error < best_error:
            best_order = order
            best_error = error
    if best_order is None:
        raise ValueError("sampled-candidate alignment requires phase compositions")
    return [sampled[index] for index in best_order], best_order, best_error


def evaluate_case_dir(
    case_dir: Path = DEFAULT_CASE_DIR,
    *,
    debug: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    blockers = _fixture_blockers(case_dir)
    if blockers:
        return {
            "complete": False,
            "status": "blocked",
            "blockers": blockers,
            "claim_scope": "internal_sampled_candidate_diagnostic",
            "production_route_admitted": False,
            "global_phase_set_certified": False,
        }

    metadata = _read_json(case_dir / "metadata.json")
    thresholds = _read_json(case_dir / "thresholds.json")
    feed = _read_csv(case_dir / "feed_compositions.csv")[0]
    tieline = _read_csv(case_dir / "experimental_tielines.csv")[0]
    species = [str(value) for value in metadata["species"]]
    mixture = _build_mixture(case_dir, species)
    diagnostic = dict(
        _core._native_neutral_tpd_phase_discovery(
            mixture._native,
            float(feed["temperature_K"]),
            float(feed["pressure_Pa"]),
            [float(feed["z1"]), float(feed["z2"])],
            [0, 0],
            float(thresholds["solver_tolerance"]),
            float(thresholds["material_balance_abs"]),
        )
    )

    sampled = [
        [float(value) for value in composition]
        for composition in diagnostic.get("selected_phase_compositions", [])
    ]
    source = [
        [float(tieline["liquid1_x1"]), float(tieline["liquid1_x2"])],
        [float(tieline["liquid2_x1"]), float(tieline["liquid2_x2"])],
    ]
    if len(sampled) == 2:
        aligned, alignment_order, composition_error = _best_source_alignment(sampled, source)
    else:
        aligned, alignment_order, composition_error = sampled, (), float("inf")
    raw_sampled_fractions = [
        float(value) for value in diagnostic.get("selected_phase_fractions", [])
    ]
    sampled_fractions = (
        [raw_sampled_fractions[index] for index in alignment_order]
        if len(raw_sampled_fractions) == len(alignment_order) == 2
        else raw_sampled_fractions
    )
    source_fractions = [float(feed["liquid1_phase_fraction"]), float(feed["liquid2_phase_fraction"])]
    fraction_error = (
        max(
            abs(left - right)
            for left, right in zip(sampled_fractions, source_fractions, strict=True)
        )
        if len(sampled_fractions) == 2
        else float("inf")
    )
    validation_findings: list[str] = []

    expected_status = diagnostic.get("held_stage_ii_status") == "sampled_candidate_audit_complete"
    honest_dual_loop = diagnostic.get("held_stage_ii_dual_loop_status") == "not_performed"
    closed_scope = (
        diagnostic.get("phase_set_status")
        == "sampled_candidate_audit_complete_global_completeness_unproven"
        and diagnostic.get("candidate_completeness_accepted") is False
    )
    if not expected_status:
        blockers.append("sampled_candidate_audit_not_complete")
    if not honest_dual_loop:
        blockers.append("dual_loop_claim_present")
    if not closed_scope:
        blockers.append("global_completeness_claim_present")
    if composition_error > float(thresholds["composition_abs"]):
        validation_findings.append("sampled_candidate_composition_error_exceeds_previous_route_threshold")
    if fraction_error > float(thresholds["phase_fraction_abs"]):
        validation_findings.append("sampled_candidate_fraction_error_exceeds_previous_route_threshold")

    command = checker_command or [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_neutral_lle_showcase.py",
    ]
    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=_core,
        checker_command=command,
    )
    return {
        "complete": not blockers,
        "status": "internal_diagnostic_complete" if not blockers else "blocked",
        "blockers": sorted(set(blockers)),
        "validation_findings": validation_findings,
        "case_label": metadata["case_label"],
        "family_label": metadata["family_label"],
        "claim_scope": "internal_sampled_candidate_diagnostic",
        "production_route_admitted": False,
        "global_phase_set_certified": False,
        "fixture": {
            "source_data": {"status": "source_backed"},
            "binary_interaction": {"status": "source_fitted"},
        },
        "diagnostic": diagnostic,
        "comparison": {
            "source_phase_compositions": source,
            "sampled_phase_compositions": aligned,
            "source_phase_fractions": source_fractions,
            "sampled_phase_fractions": sampled_fractions,
            "max_composition_abs_error": composition_error,
            "max_phase_fraction_abs_error": fraction_error,
            "previous_route_composition_threshold_passed": (
                composition_error <= float(thresholds["composition_abs"])
            ),
            "previous_route_phase_fraction_threshold_passed": (
                fraction_error <= float(thresholds["phase_fraction_abs"])
            ),
        },
        "shared_certification": {
            "status": "internal_validation",
            "selector_family": "neutral_lle",
            "production_exposed": False,
            "public_routes": [],
            "global_held_proof": False,
        },
        "native_freshness_receipt": receipt,
        "debug": bool(debug),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-fresh-native", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = sys.argv[:] if argv is None else [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_neutral_lle_showcase.py",
        *argv,
    ]
    payload = evaluate_case_dir(args.case_dir, debug=args.debug, checker_command=command)
    if args.require_fresh_native:
        native_freshness.require_equilibrium_native_fresh(payload["native_freshness_receipt"])
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload.get('case_label', 'neutral LLE diagnostic')}: {payload['status']}")
        if payload["blockers"]:
            print("  blockers: " + ", ".join(payload["blockers"]))
    return 2 if args.require_complete and not payload["complete"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
