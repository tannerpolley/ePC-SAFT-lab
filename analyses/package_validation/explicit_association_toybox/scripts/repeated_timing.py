from __future__ import annotations

import argparse
import csv
import statistics
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .closure_models import evaluate_closure
from .exact_baseline import solve_exact_site_fractions
from .metrics import timed_closure
from .topology_reductions import topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "timing_repeatability" / "output" / "timing_repeatability.csv"
DEFAULT_CLOSURES = (
    "implicit_exact_mass_action",
    "explicit_damped_picard_unroll_3",
    "explicit_damped_picard_unroll_5",
    "explicit_picard3_diag_newton1",
)


def summarize_repeated_timings(samples: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[Mapping[str, object]]] = {}
    for sample in samples:
        grouped.setdefault(str(sample["closure_name"]), []).append(sample)
    rows: list[dict[str, object]] = []
    for closure_name, closure_samples in sorted(grouped.items()):
        elapsed = [float(sample["elapsed_seconds"]) for sample in closure_samples]
        exact_elapsed = [float(sample["exact_elapsed_seconds"]) for sample in closure_samples]
        speedups = [
            reference / value if value > 0.0 else np.nan
            for reference, value in zip(exact_elapsed, elapsed, strict=True)
        ]
        rows.append(
            {
                "closure_name": closure_name,
                "repeat_count": len(elapsed),
                "elapsed_median_seconds": statistics.median(elapsed),
                "elapsed_iqr_seconds": _iqr(elapsed),
                "elapsed_min_seconds": min(elapsed),
                "elapsed_max_seconds": max(elapsed),
                "speedup_median": statistics.median(speedups),
            }
        )
    return rows


def run_repeated_timings(
    *,
    repeat_count: int = 7,
    closure_names: Iterable[str] = DEFAULT_CLOSURES,
) -> list[dict[str, object]]:
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive.")
    system = topology_system("2B")
    composition = np.array([1.0], dtype=float)
    density = 0.05
    strength = 10.0
    delta = system.delta_matrix(strength)
    samples: list[dict[str, object]] = []
    for _ in range(repeat_count):
        exact, exact_elapsed = timed_closure(
            lambda: solve_exact_site_fractions(
                density=density,
                x_assoc=system.x_assoc(composition),
                delta=delta,
            )
        )
        for closure_name in closure_names:
            if closure_name == "implicit_exact_mass_action":
                samples.append(
                    {
                        "closure_name": closure_name,
                        "elapsed_seconds": exact_elapsed,
                        "exact_elapsed_seconds": exact_elapsed,
                    }
                )
                continue
            _, elapsed = timed_closure(
                lambda closure_name=closure_name: evaluate_closure(
                    closure_name,
                    system=system,
                    density=density,
                    composition=composition,
                    delta=delta,
                )
            )
            samples.append(
                {
                    "closure_name": closure_name,
                    "elapsed_seconds": elapsed,
                    "exact_elapsed_seconds": exact_elapsed,
                    "exact_iteration_count": exact.iteration_count,
                }
            )
    return summarize_repeated_timings(samples)


def write_repeated_timing_csv(rows: list[dict[str, object]], output_path: Path = DEFAULT_OUTPUT) -> Path:
    if not rows:
        raise ValueError("repeated timing rows are required.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def generate_repeated_timing(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_repeated_timing_csv(run_repeated_timings(), output_path)


def _iqr(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return float(np.percentile(values, 75) - np.percentile(values, 25))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated explicit association timing diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_repeated_timing(args.output))


if __name__ == "__main__":
    main()
