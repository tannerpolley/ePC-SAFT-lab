from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file() and (parent / "data" / "reference").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root from the figure script path.")


REPO_ROOT = _repo_root()
sys.path.insert(0, str(REPO_ROOT))

from scripts.dev.native_runtime_env import apply_to_current_process

apply_to_current_process()

import epcsaft
import epcsaft_equilibrium


FIGURE_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_ROOT / "results"
REFERENCE_DIR = REPO_ROOT / "data" / "reference" / "pure_component"
SATURATION_REFERENCE_DIR = REFERENCE_DIR / "saturation_density"
PARAMETER_REFERENCE = REFERENCE_DIR / "hydrocarbon_basis_workbook_reference.csv"
SOLVER_OPTIONS = {"max_iterations": 500, "tolerance": 1.0e-7}
MOLECULAR_WEIGHTS_KG_PER_MOL = {
    "Methane": 16.043e-3,
    "Ethane": 30.070e-3,
    "Propane": 44.097e-3,
}


def _load_pcsaft_parameters() -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with PARAMETER_REFERENCE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["species"]] = {
                "m": float(row["m"]),
                "s": float(row["s_Angstrom"]),
                "e": float(row["e_over_k_K"]),
            }
    return rows


def _mixture_for_species(species: str, parameters: dict[str, dict[str, float]]) -> Any:
    values = parameters[species]
    parameter_set = epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([MOLECULAR_WEIGHTS_KG_PER_MOL[species]], dtype=float),
            "m": np.asarray([values["m"]], dtype=float),
            "s": np.asarray([values["s"]], dtype=float),
            "e": np.asarray([values["e"]], dtype=float),
        },
        species=[species],
    )
    return epcsaft.Mixture(parameter_set)


def _reference_rows(species: str) -> list[dict[str, str]]:
    path = SATURATION_REFERENCE_DIR / f"{species.lower()}_nist_saturation.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    parameters = _load_pcsaft_parameters()
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for species in ("Methane", "Ethane", "Propane"):
        mixture = _mixture_for_species(species, parameters)
        for reference in _reference_rows(species):
            temperature = float(reference["T_K"])
            reference_pressure = float(reference["p_sat_Pa"])
            try:
                result = epcsaft_equilibrium.Equilibrium(
                    mixture,
                    route="single_component_vle",
                    T=temperature,
                ).solve(solver_options=SOLVER_OPTIONS)
            except Exception as exc:
                failures.append(f"{species} {temperature:g} K: {type(exc).__name__}: {exc}")
                continue
            diagnostics = result.diagnostics
            route_pressure = float(result.P_sat)
            absolute_error = route_pressure - reference_pressure
            molecular_weight = MOLECULAR_WEIGHTS_KG_PER_MOL[species]
            route_vapor_density_kg_m3 = float(result.vapor_density) * molecular_weight
            route_liquid_density_kg_m3 = float(result.liquid_density) * molecular_weight
            reference_liquid_density_kg_m3 = float(reference["rho_sat_liq_kg_m3"])
            density_error = route_liquid_density_kg_m3 - reference_liquid_density_kg_m3
            rows.append(
                {
                    "species": species,
                    "T_K": temperature,
                    "p_sat_nist_Pa": reference_pressure,
                    "p_sat_route_Pa": route_pressure,
                    "absolute_error_Pa": absolute_error,
                    "relative_error_percent": 100.0 * absolute_error / reference_pressure,
                    "absolute_relative_error_percent": abs(100.0 * absolute_error / reference_pressure),
                    "rho_vapor_mol_m3": float(result.vapor_density),
                    "rho_liquid_mol_m3": float(result.liquid_density),
                    "rho_vapor_route_kg_m3": route_vapor_density_kg_m3,
                    "rho_liquid_route_kg_m3": route_liquid_density_kg_m3,
                    "rho_sat_liq_nist_kg_m3": reference_liquid_density_kg_m3,
                    "rho_sat_liq_absolute_error_kg_m3": density_error,
                    "rho_sat_liq_relative_error_percent": 100.0 * density_error / reference_liquid_density_kg_m3,
                    "rho_sat_liq_absolute_relative_error_percent": abs(
                        100.0 * density_error / reference_liquid_density_kg_m3
                    ),
                    "route_status": diagnostics.get("route_status", ""),
                    "solver_status": diagnostics.get("solver_status", ""),
                    "seed_name": diagnostics.get("seed_name", ""),
                    "phase_distance": diagnostics.get("phase_distance", np.nan),
                    "pressure_consistency_norm": diagnostics.get("pressure_consistency_norm", np.nan),
                    "chemical_potential_consistency_norm": diagnostics.get(
                        "chemical_potential_consistency_norm",
                        np.nan,
                    ),
                    "ln_fugacity_consistency_norm": diagnostics.get("ln_fugacity_consistency_norm", np.nan),
                    "solver_tolerance": SOLVER_OPTIONS["tolerance"],
                    "max_iterations": SOLVER_OPTIONS["max_iterations"],
                    "source": reference["source"],
                }
            )
    if failures:
        raise RuntimeError("Single-component VLE validation rows failed:\n" + "\n".join(failures))

    frame = pd.DataFrame(rows).sort_values(["species", "T_K"])
    output = RESULTS_DIR / "hydrocarbon_saturation_pressure.csv"
    frame.to_csv(output, index=False)
    summary = (
        frame
        .groupby("species", as_index=False)
        .agg(
            rows=("T_K", "count"),
            mape_percent=("absolute_relative_error_percent", "mean"),
            max_ape_percent=("absolute_relative_error_percent", "max"),
            liquid_density_mape_percent=("rho_sat_liq_absolute_relative_error_percent", "mean"),
            liquid_density_max_ape_percent=("rho_sat_liq_absolute_relative_error_percent", "max"),
            min_temperature_K=("T_K", "min"),
            max_temperature_K=("T_K", "max"),
        )
    )
    summary.to_csv(RESULTS_DIR / "hydrocarbon_saturation_pressure_summary.csv", index=False)
    endpoint_summary = (
        frame.sort_values("T_K")
        .groupby("species", as_index=False)
        .tail(1)
        .sort_values("species")
        [
            [
                "species",
                "T_K",
                "p_sat_nist_Pa",
                "p_sat_route_Pa",
                "absolute_relative_error_percent",
                "rho_sat_liq_nist_kg_m3",
                "rho_liquid_route_kg_m3",
                "rho_sat_liq_absolute_relative_error_percent",
                "phase_distance",
                "seed_name",
            ]
        ]
    )
    endpoint_summary.to_csv(RESULTS_DIR / "hydrocarbon_saturation_endpoint_summary.csv", index=False)
    print(f"wrote {output}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
