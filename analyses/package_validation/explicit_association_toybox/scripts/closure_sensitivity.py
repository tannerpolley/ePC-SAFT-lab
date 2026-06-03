from __future__ import annotations

import argparse
import csv
import statistics
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np
import yaml

from .association_models import mass_action_residual
from .closure_models import ClosureResult, _diagonal_polish, _picard
from .exact_baseline import solve_exact_site_fractions
from .metrics import metric_row, timed_closure
from .run_topology_matrix import DEFAULT_DENSITY_GRID, DEFAULT_STRENGTH_GRID, _thresholds
from .topology_reductions import HUANG_RADOSZ_TOPOLOGIES, topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ANALYSIS_ROOT / "config" / "closure_sensitivity.yaml"
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "closure_sensitivity" / "output" / "closure_sensitivity.csv"


def load_closure_sensitivity_variants(path: Path = DEFAULT_CONFIG) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("variants"), list):
        raise ValueError(f"{path} must define a variants list.")
    return [_validate_variant(item) for item in data["variants"]]


def rank_closure_sensitivity(
    *,
    variants: Iterable[Mapping[str, object]] | None = None,
    topology_types: Iterable[str] | None = None,
    density_grid: Iterable[float] | None = None,
    strength_grid: Iterable[float] | None = None,
) -> list[dict[str, object]]:
    selected_variants = list(variants) if variants is not None else load_closure_sensitivity_variants()
    selected_topologies = [str(item).upper() for item in (topology_types or HUANG_RADOSZ_TOPOLOGIES)]
    densities = tuple(float(value) for value in (density_grid or DEFAULT_DENSITY_GRID))
    strengths = tuple(float(value) for value in (strength_grid or DEFAULT_STRENGTH_GRID))
    thresholds = _thresholds()
    grouped: dict[str, list[dict[str, object]]] = {}

    for raw_variant in selected_variants:
        variant = _validate_variant(raw_variant)
        variant_name = str(variant["closure_variant"])
        for topology_type in selected_topologies:
            system = topology_system(topology_type)
            composition = np.array([1.0], dtype=float)
            for density in densities:
                for strength in strengths:
                    delta = system.delta_matrix(strength)
                    exact, exact_elapsed = timed_closure(
                        lambda density=density, composition=composition, delta=delta: solve_exact_site_fractions(
                            density=density,
                            x_assoc=system.x_assoc(composition),
                            delta=delta,
                        )
                    )
                    closure, elapsed = timed_closure(
                        lambda variant=variant, system=system, density=density, composition=composition, delta=delta: _evaluate_variant(
                            variant,
                            system=system,
                            density=density,
                            composition=composition,
                            delta=delta,
                        )
                    )
                    row = metric_row(
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
                        exact_elapsed_seconds=exact_elapsed,
                    )
                    grouped.setdefault(variant_name, []).append(row)

    ranked: list[dict[str, object]] = []
    for raw_variant in selected_variants:
        variant = _validate_variant(raw_variant)
        variant_name = str(variant["closure_variant"])
        rows = grouped[variant_name]
        median_elapsed = statistics.median(float(row["closure_elapsed_seconds"]) for row in rows)
        median_exact_elapsed = statistics.median(float(row["exact_elapsed_seconds"]) for row in rows)
        ranked.append(
            {
                "closure_variant": variant_name,
                "closure_name": variant_name,
                "picard_steps": int(variant["picard_steps"]),
                "damping": float(variant["damping"]),
                "diagonal_polish": bool(variant["diagonal_polish"]),
                "max_ares_assoc_rel_error": max(abs(float(row["assoc_helmholtz_rel_error"])) for row in rows),
                "max_mass_action_residual_inf": max(float(row["mass_residual_inf"]) for row in rows),
                "median_elapsed_seconds": median_elapsed,
                "median_exact_implicit_elapsed_seconds": median_exact_elapsed,
                "speedup_vs_exact_implicit": median_exact_elapsed / median_elapsed if median_elapsed > 0.0 else np.nan,
                "evidence_band": _least_favorable_band(str(row["evidence_band"]) for row in rows),
                "case_count": len(rows),
            }
        )
    ranked.sort(key=lambda row: (float(row["max_ares_assoc_rel_error"]), float(row["median_elapsed_seconds"])))
    return ranked


def write_closure_sensitivity_csv(rows: list[dict[str, object]], output_path: Path = DEFAULT_OUTPUT) -> Path:
    if not rows:
        raise ValueError("closure sensitivity rows are required.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def generate_closure_sensitivity(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_closure_sensitivity_csv(rank_closure_sensitivity(), output_path)


def _evaluate_variant(
    variant: Mapping[str, object],
    *,
    system,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> ClosureResult:
    x_assoc = system.x_assoc(composition)
    xa = _picard(
        density,
        x_assoc,
        delta,
        steps=int(variant["picard_steps"]),
        damping=float(variant["damping"]),
    )
    if bool(variant["diagonal_polish"]):
        xa = _diagonal_polish(xa, density, x_assoc, delta, damping=0.5)
    residual = mass_action_residual(xa, density=density, x_assoc=x_assoc, delta=delta)
    if not np.all(np.isfinite(residual)):
        raise ValueError(f"closure sensitivity variant produced nonfinite residuals: {variant['closure_variant']}")
    return ClosureResult(
        name=str(variant["closure_variant"]),
        xa=xa,
        association_model="explicit_approx",
        association_closure=str(variant["closure_variant"]),
        exact_derivative_of="approximate_association_closure",
        information_loss="none",
    )


def _validate_variant(raw: Mapping[str, object]) -> dict[str, object]:
    required = {"closure_variant", "picard_steps", "damping", "diagonal_polish"}
    missing = required - set(raw)
    if missing:
        raise ValueError(f"closure sensitivity variant is missing required fields: {sorted(missing)}")
    steps = int(raw["picard_steps"])
    damping = float(raw["damping"])
    if steps <= 0:
        raise ValueError("closure sensitivity picard_steps must be positive.")
    if not 0.0 < damping <= 1.0:
        raise ValueError("closure sensitivity damping must be in (0, 1].")
    return {
        "closure_variant": str(raw["closure_variant"]),
        "picard_steps": steps,
        "damping": damping,
        "diagonal_polish": bool(raw["diagonal_polish"]),
    }


def _least_favorable_band(values: Iterable[str]) -> str:
    rank = {
        "exact_reduction_verified": 0,
        "promising_eos_approximation": 1,
        "diagnostic_only": 2,
        "reject_for_provider_path": 3,
    }
    return max(values, key=lambda value: rank.get(value, 2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank explicit association closure sensitivity variants.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_closure_sensitivity(args.output))


if __name__ == "__main__":
    main()
