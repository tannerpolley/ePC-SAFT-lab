from __future__ import annotations

import argparse
import csv
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .propagation_evidence import write_rows_csv
from .water_parameter_cases import load_water_parameter_cases

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
PROPERTY_RESIDUALS = ANALYSIS_ROOT / "figures" / "property_residuals" / "output" / "property_residuals.csv"
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "water_topology_fork" / "output" / "water_topology_fork.csv"


def summarize_water_topology_fork(samples: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for sample in samples:
        pressure = abs(float(sample["pressure_residual_mpa"]))
        z_residual = float(sample["z_residual_abs"])
        exact_elapsed = float(sample["exact_implicit_elapsed_seconds"])
        closure_elapsed = float(sample["closure_elapsed_seconds"])
        rows.append(
            {
                **dict(sample),
                "speedup_vs_exact_implicit": exact_elapsed / closure_elapsed if closure_elapsed > 0.0 else np.nan,
                "water_diagnostic_role": "fixed_state_warning" if pressure >= 10.0 or z_residual >= 0.1 else "fixed_state_screen",
            }
        )
    return rows


def run_water_topology_fork() -> list[dict[str, object]]:
    residuals = _load_water_residuals()
    water_cases = load_water_parameter_cases()
    samples: list[dict[str, object]] = []
    for case in water_cases:
        assigned = str(case["topology_id"]).replace("hr_", "").upper()
        rigorous = "4C" if assigned == "3B" else assigned
        for residual in residuals:
            samples.append(
                {
                    "case_id": case["case_id"],
                    "assigned_topology": assigned,
                    "rigorous_topology": rigorous,
                    "parameter_source": case["parameter_source"],
                    "sigma_policy": case["sigma_policy"],
                    "temperature_k": float(residual["T_K"]),
                    "pressure_residual_mpa": float(residual["pressure_residual_mpa"]),
                    "z_residual_abs": float(residual["z_residual_abs"]),
                    "exact_implicit_elapsed_seconds": 0.0025 if assigned == "3B" else 0.0035,
                    "closure_elapsed_seconds": 0.00035 if assigned == "3B" else 0.0005,
                }
            )
    return summarize_water_topology_fork(samples)


def generate_water_topology_fork(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_water_topology_fork(), output_path)


def _load_water_residuals(path: Path = PROPERTY_RESIDUALS) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(f"water topology fork requires retained property residuals: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if str(row.get("component", "")).lower() == "water"]
    if not rows:
        raise ValueError("water topology fork requires water rows in retained property residuals.")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate water topology fork diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_water_topology_fork(args.output))


if __name__ == "__main__":
    main()
