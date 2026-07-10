from __future__ import annotations

import argparse
import statistics
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import CANDIDATE_CLOSURES
    from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
        solve_exact_site_fractions,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
        evaluate_named_closure,
        timed_closure,
        write_rows_csv,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.topology_reductions import topology_system
else:
    from .closure_models import CANDIDATE_CLOSURES
    from .exact_baseline import solve_exact_site_fractions
    from .propagation_evidence import evaluate_named_closure, timed_closure, write_rows_csv
    from .topology_reductions import topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "amortized_timing" / "output" / "amortized_timing.csv"
DEFAULT_CLOSURES = CANDIDATE_CLOSURES
DEFAULT_CASES = (
    ("topology_2b_low", "2B", 0.03, 4.0),
    ("topology_2b_moderate", "2B", 0.05, 10.0),
    ("topology_3b_moderate", "3B", 0.05, 10.0),
    ("topology_4c_moderate", "4C", 0.05, 10.0),
)


def summarize_amortized_timing_samples(samples: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, int, str], list[Mapping[str, object]]] = {}
    for sample in samples:
        key = (
            str(sample["case_id"]),
            str(sample["topology_id"]),
            int(sample["site_count"]),
            str(sample["closure_name"]),
        )
        grouped.setdefault(key, []).append(sample)
    rows: list[dict[str, object]] = []
    for (case_id, topology_id, site_count, closure_name), group in sorted(grouped.items()):
        exact_elapsed = [float(row["exact_implicit_elapsed_seconds"]) for row in group]
        closure_elapsed = [float(row["closure_elapsed_seconds"]) for row in group]
        exact_iterations = [float(row["exact_iteration_count"]) for row in group]
        exact_median = statistics.median(exact_elapsed)
        closure_median = statistics.median(closure_elapsed)
        rows.append(
            {
                "case_id": case_id,
                "topology_id": topology_id,
                "site_count": site_count,
                "closure_name": closure_name,
                "repeat_count": len(group),
                "exact_implicit_elapsed_median_seconds": exact_median,
                "closure_elapsed_median_seconds": closure_median,
                "exact_implicit_elapsed_iqr_seconds": _iqr(exact_elapsed),
                "closure_elapsed_iqr_seconds": _iqr(closure_elapsed),
                "speedup_vs_exact_implicit": exact_median / closure_median if closure_median > 0.0 else np.nan,
                "exact_iteration_count_median": statistics.median(exact_iterations),
            }
        )
    return rows


def run_amortized_timings(
    *,
    repeat_count: int = 101,
    closure_names: Iterable[str] = DEFAULT_CLOSURES,
) -> list[dict[str, object]]:
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive.")
    samples: list[dict[str, object]] = []
    for case_id, topology_id, density, strength in DEFAULT_CASES:
        system = topology_system(topology_id)
        composition = np.array([1.0], dtype=float)
        delta = system.delta_matrix(strength)
        for _ in range(repeat_count):
            exact, exact_elapsed = timed_closure(
                lambda system=system, density=density, composition=composition, delta=delta: solve_exact_site_fractions(
                    density=density,
                    x_assoc=system.x_assoc(composition),
                    delta=delta,
                )
            )
            for closure_name in closure_names:
                _, closure_elapsed = timed_closure(
                    lambda closure_name=closure_name, system=system, density=density, composition=composition, delta=delta: evaluate_named_closure(
                        closure_name,
                        system=system,
                        density=density,
                        composition=composition,
                        delta=delta,
                    )
                )
                samples.append(
                    {
                        "case_id": case_id,
                        "topology_id": topology_id,
                        "site_count": system.site_count,
                        "closure_name": closure_name,
                        "exact_implicit_elapsed_seconds": exact_elapsed,
                        "closure_elapsed_seconds": closure_elapsed,
                        "exact_iteration_count": exact.iteration_count,
                    }
                )
    return summarize_amortized_timing_samples(samples)


def generate_amortized_timing(*, output_path: Path = DEFAULT_OUTPUT, repeat_count: int = 101) -> Path:
    return write_rows_csv(run_amortized_timings(repeat_count=repeat_count), output_path)


def _iqr(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return float(np.percentile(values, 75) - np.percentile(values, 25))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run amortized explicit association timing diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repeat-count", type=int, default=101)
    args = parser.parse_args()
    print(generate_amortized_timing(output_path=args.output, repeat_count=args.repeat_count))


if __name__ == "__main__":
    main()
