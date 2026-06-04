from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np
import yaml

from .association_models import AssociationSystem
from .closure_models import CANDIDATE_CLOSURES
from .exact_baseline import solve_exact_site_fractions
from .propagation_evidence import (
    classify_propagated_evidence_band,
    closure_association_value,
    exact_association_value,
    load_propagation_thresholds,
    mass_residual_inf,
    relative_error,
    write_rows_csv,
)

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ANALYSIS_ROOT / "config" / "asymmetric_binary_cases.yaml"
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "asymmetric_binary_closures" / "output" / "asymmetric_binary_closures.csv"
DEFAULT_CLOSURES = CANDIDATE_CLOSURES


def load_asymmetric_binary_cases(path: Path = DEFAULT_CONFIG) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("cases"), list):
        raise ValueError(f"{path} must define a cases list.")
    return [_validate_case(row) for row in data["cases"]]


def build_association_system(case: Mapping[str, object]) -> AssociationSystem:
    return AssociationSystem(
        component_count=int(case["component_count"]),
        site_component_index=np.asarray(case["site_component_index"], dtype=int),
        site_kind=tuple(str(value) for value in case["site_kind"]),
        active_pairs=tuple(tuple(int(value) for value in pair) for pair in case["active_pairs"]),
    )


def delta_from_pairs(case: Mapping[str, object]) -> np.ndarray:
    system = build_association_system(case)
    delta = np.zeros((system.site_count, system.site_count), dtype=float)
    for raw_pair in case["delta_pairs"]:
        i, j, value = raw_pair
        delta[int(i), int(j)] = float(value)
    return delta


def run_asymmetric_binary_closures(
    *,
    closure_names: Iterable[str] = DEFAULT_CLOSURES,
) -> list[dict[str, object]]:
    thresholds = load_propagation_thresholds()
    rows: list[dict[str, object]] = []
    for case in load_asymmetric_binary_cases():
        system = build_association_system(case)
        composition = np.asarray(case["composition"], dtype=float)
        density = float(case["density"])
        delta = delta_from_pairs(case)
        exact, exact_a, exact_elapsed = exact_association_value(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        )
        for closure_name in closure_names:
            closure, closure_a, closure_elapsed = closure_association_value(
                closure_name,
                system=system,
                density=density,
                composition=composition,
                delta=delta,
            )
            rel = relative_error(closure_a, exact_a)
            residual = mass_residual_inf(
                closure,
                system=system,
                density=density,
                composition=composition,
                delta=delta,
            )
            speedup = exact_elapsed / closure_elapsed if closure_elapsed > 0.0 else np.nan
            rows.append(
                {
                    "case_id": case["case_id"],
                    "case_role": case["case_role"],
                    "closure_name": closure_name,
                    "site_count": system.site_count,
                    "composition": ";".join(f"{value:.12g}" for value in composition),
                    "ares_assoc_exact": exact_a,
                    "ares_assoc_closure": closure_a,
                    "ares_assoc_rel_error": rel,
                    "mass_action_residual_inf": residual,
                    "exact_iteration_count": exact.iteration_count,
                    "exact_implicit_elapsed_seconds": exact_elapsed,
                    "closure_elapsed_seconds": closure_elapsed,
                    "speedup_vs_exact_implicit": speedup,
                    "evidence_band": classify_propagated_evidence_band(
                        association_model=closure.association_model,
                        assoc_ares_rel_error=rel,
                        derivative_rel_error=rel,
                        property_rel_error=rel,
                        mass_action_residual_inf=residual,
                        speedup_vs_exact_implicit=speedup,
                        information_loss=closure.information_loss,
                        thresholds=thresholds,
                    ),
                }
            )
    return rows


def generate_asymmetric_binary_closures(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_asymmetric_binary_closures(), output_path)


def _validate_case(raw: Mapping[str, object]) -> dict[str, object]:
    required = {
        "case_id",
        "case_role",
        "component_count",
        "site_component_index",
        "site_kind",
        "active_pairs",
        "composition",
        "density",
        "delta_pairs",
    }
    missing = required - set(raw)
    if missing:
        raise ValueError(f"asymmetric binary case is missing required fields: {sorted(missing)}")
    component_count = int(raw["component_count"])
    composition = np.asarray(raw["composition"], dtype=float)
    if composition.shape != (component_count,) or not np.isclose(float(np.sum(composition)), 1.0):
        raise ValueError("asymmetric binary composition must match component_count and sum to one.")
    case = dict(raw)
    case["component_count"] = component_count
    case["composition"] = [float(value) for value in composition]
    case["density"] = float(raw["density"])
    return case


def main() -> None:
    parser = argparse.ArgumentParser(description="Run asymmetric binary explicit association closure diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_asymmetric_binary_closures(args.output))


if __name__ == "__main__":
    main()
