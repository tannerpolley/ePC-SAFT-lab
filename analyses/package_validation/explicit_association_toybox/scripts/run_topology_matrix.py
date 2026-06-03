from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import yaml

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
    from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
    from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row, timed_closure
    from analyses.package_validation.explicit_association_toybox.scripts.topology_reductions import (
        HUANG_RADOSZ_TOPOLOGIES,
        evaluate_topology_reduction,
        topology_system,
    )
else:
    from .closure_models import evaluate_closure
    from .exact_baseline import solve_exact_site_fractions
    from .metrics import metric_row, timed_closure
    from .topology_reductions import HUANG_RADOSZ_TOPOLOGIES, evaluate_topology_reduction, topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "topology_validation_matrix" / "output" / "topology_matrix.csv"
DEFAULT_DENSITY_GRID = (0.001, 0.01, 0.05, 0.1)
DEFAULT_STRENGTH_GRID = (0.1, 1.0, 10.0, 50.0)
DEFAULT_CLOSURES = (
    "closure_2b_exact_reduction",
    "explicit_picard_unroll_1",
    "explicit_damped_picard_unroll_3",
    "explicit_damped_picard_unroll_5",
    "explicit_picard3_diag_newton1",
    "collapsed_donor_acceptor_mean_field",
)
TOPOLOGY_MATRIX_COLUMNS = (
    "system",
    "paper_topology_type",
    "closure",
    "association_model",
    "association_closure",
    "exact_derivative_of",
    "information_loss",
    "source_formula_family",
    "source_formula_id",
    "derivation_family",
    "comparison_role",
    "topology_gate",
    "exactness_claim",
    "derivation_relationship",
    "density",
    "strength",
    "composition",
    "max_abs_x_error",
    "max_rel_x_error",
    "mass_residual_inf",
    "assoc_helmholtz_exact",
    "assoc_helmholtz_closure",
    "assoc_helmholtz_abs_error",
    "assoc_helmholtz_rel_error",
    "assoc_compressibility_abs_error",
    "assoc_mu_abs_error",
    "assoc_fugacity_abs_error",
    "exact_iteration_count",
    "exact_residual_norm",
    "closure_elapsed_seconds",
    "evidence_band",
)


def run_topology_matrix(
    *,
    output_path: Path = DEFAULT_OUTPUT,
    topology_types: Iterable[str] | None = None,
    closure_names: Iterable[str] | None = None,
    density_grid: Iterable[float] | None = None,
    strength_grid: Iterable[float] | None = None,
) -> Path:
    thresholds = _thresholds()
    selected_topologies = [str(item).upper() for item in (topology_types or HUANG_RADOSZ_TOPOLOGIES)]
    selected_closures = tuple(closure_names or DEFAULT_CLOSURES)
    densities = tuple(float(value) for value in (density_grid or DEFAULT_DENSITY_GRID))
    strengths = tuple(float(value) for value in (strength_grid or DEFAULT_STRENGTH_GRID))

    rows: list[dict[str, object]] = []
    for topology_type in selected_topologies:
        system = topology_system(topology_type)
        composition = np.array([1.0], dtype=float)
        for density in densities:
            for strength in strengths:
                delta = system.delta_matrix(strength)
                exact = solve_exact_site_fractions(
                    density=density,
                    x_assoc=system.x_assoc(composition),
                    delta=delta,
                )
                reduction = evaluate_topology_reduction(topology_type, density=density, strength=strength)
                rows.append(
                    _metadata_row(
                        row=metric_row(
                            system_name=f"huang_radosz_{topology_type.lower()}",
                            system=system,
                            density=density,
                            strength=strength,
                            composition=composition,
                            delta=delta,
                            exact=exact,
                            closure=reduction.as_closure_result(),
                            thresholds=thresholds,
                            elapsed_seconds=0.0,
                        ),
                        topology_type=topology_type,
                        source_formula_family=reduction.source_formula_family,
                        source_formula_id=reduction.source_formula_id,
                        derivation_family=reduction.derivation_family,
                        comparison_role=reduction.comparison_role,
                        topology_gate=reduction.topology_gate,
                        exactness_claim=reduction.exactness_claim,
                        derivation_relationship=reduction.derivation_relationship,
                    )
                )
                for closure_name in selected_closures:
                    if closure_name == "closure_2b_exact_reduction" and topology_type != "2B":
                        continue
                    closure, elapsed = timed_closure(
                        lambda closure_name=closure_name: evaluate_closure(
                            closure_name,
                            system=system,
                            density=density,
                            composition=composition,
                            delta=delta,
                        )
                    )
                    rows.append(
                        _metadata_row(
                            row=metric_row(
                                system_name=f"huang_radosz_{topology_type.lower()}",
                                system=system,
                                density=density,
                                strength=strength,
                                composition=composition,
                                delta=delta,
                                exact=exact,
                                closure=closure,
                                thresholds=thresholds,
                                elapsed_seconds=elapsed,
                            ),
                            topology_type=topology_type,
                            source_formula_family="repo_derivation",
                            source_formula_id=str(closure_name),
                            derivation_family=_closure_derivation_family(str(closure_name)),
                            comparison_role=_closure_comparison_role(str(closure_name)),
                            topology_gate="compared_against_huang_radosz_topology_exact_baseline",
                            exactness_claim=_closure_exactness_claim(str(closure_name)),
                            derivation_relationship=_closure_derivation_family(str(closure_name)),
                        )
                    )
    if not rows:
        raise ValueError("topology matrix selection produced no rows.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(TOPOLOGY_MATRIX_COLUMNS))
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in TOPOLOGY_MATRIX_COLUMNS} for row in rows)
    return output_path


def _thresholds() -> dict[str, float]:
    path = ANALYSIS_ROOT / "config" / "closure_sweep.yaml"
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("evidence_bands"), dict):
        raise ValueError(f"{path} must define evidence_bands.")
    return {str(key): float(value) for key, value in data["evidence_bands"].items()}


def _metadata_row(
    *,
    row: dict[str, object],
    topology_type: str,
    source_formula_family: str,
    source_formula_id: str,
    derivation_family: str,
    comparison_role: str,
    topology_gate: str,
    exactness_claim: str,
    derivation_relationship: str,
) -> dict[str, object]:
    row = dict(row)
    row.update(
        {
            "paper_topology_type": topology_type,
            "source_formula_family": source_formula_family,
            "source_formula_id": source_formula_id,
            "derivation_family": derivation_family,
            "comparison_role": comparison_role,
            "topology_gate": topology_gate,
            "exactness_claim": exactness_claim,
            "derivation_relationship": derivation_relationship,
        }
    )
    return row


def _closure_derivation_family(closure_name: str) -> str:
    if closure_name == "closure_2b_exact_reduction":
        return "closure_a_2b"
    if closure_name.startswith("explicit_picard") or closure_name.startswith("explicit_damped_picard"):
        return "closure_b_picard"
    if closure_name == "explicit_picard3_diag_newton1":
        return "closure_c_picard_diagonal_newton"
    if closure_name == "collapsed_donor_acceptor_mean_field":
        return "closure_d_collapsed_mean_field"
    raise ValueError(f"Closure metadata is not mapped for: {closure_name}")


def _closure_comparison_role(closure_name: str) -> str:
    if closure_name == "closure_2b_exact_reduction":
        return "exact_topology_reduction"
    if closure_name == "collapsed_donor_acceptor_mean_field":
        return "diagnostic_collapse"
    return "explicit_approximation"


def _closure_exactness_claim(closure_name: str) -> str:
    if closure_name == "closure_2b_exact_reduction":
        return "exact_when_topology_is_one_component_2b_da"
    return "exact_derivative_of_approximate_closure_only"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Huang/Radosz topology and explicit-closure comparison matrix.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    path = run_topology_matrix(output_path=args.output)
    print(path)


if __name__ == "__main__":
    main()
