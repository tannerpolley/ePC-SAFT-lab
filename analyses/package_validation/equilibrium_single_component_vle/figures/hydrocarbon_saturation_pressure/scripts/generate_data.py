from __future__ import annotations

import csv
import math
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
from scripts.validation.nist_saturation_contract import (
    MAX_ITERATIONS,
    SOLVER_TOLERANCE,
    expected_source_url,
    load_canonical_source_rows,
)

apply_to_current_process()

import epcsaft
import epcsaft_equilibrium
from epcsaft.model.parameters import PureRecord

FIGURE_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_ROOT / "results"
REFERENCE_DIR = REPO_ROOT / "data" / "reference" / "pure_component"
PARAMETER_REFERENCE = REFERENCE_DIR / "hydrocarbon_basis_workbook_reference.csv"
SOLVER_OPTIONS = {"max_iterations": MAX_ITERATIONS, "tolerance": SOLVER_TOLERANCE}
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
    parameter_set = epcsaft.ParameterSet.from_records(
        (
            PureRecord(
                component=species,
                molar_mass=MOLECULAR_WEIGHTS_KG_PER_MOL[species],
                m=values["m"],
                sigma=values["s"],
                epsilon_k=values["e"],
                charge=0.0,
                epsilon_k_ab=0.0,
                kappa_ab=0.0,
                association_scheme=None,
                relative_permittivity=1.0,
                born_diameter=0.0,
                solvation_factor=1.0,
            ),
        ),
        metadata={
            "source": str(PARAMETER_REFERENCE.relative_to(REPO_ROOT)),
            "source_backed": True,
        },
    )
    return epcsaft.Mixture(parameter_set)


def _reference_rows(species: str) -> list[dict[str, str]]:
    return load_canonical_source_rows(species)


def _require_positive_finite(value: float, *, field: str, species: str, temperature: float) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{field} must be positive and finite for {species} at {temperature:g} K; got {value!r}")
    return value


def generate_validation_rows() -> list[dict[str, object]]:
    """Run the live NIST saturation campaign without writing retained artifacts."""

    parameters = _load_pcsaft_parameters()
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for species in ("Methane", "Ethane", "Propane"):
        mixture = _mixture_for_species(species, parameters)
        for reference in _reference_rows(species):
            reference_species = reference.get("species", "").strip()
            if reference_species != species:
                failures.append(f"{species}: reference species mismatch: expected {species}, got {reference_species!r}")
                continue
            source = reference.get("source", "").strip()
            if source != expected_source_url(species):
                failures.append(f"{species}: unexpected NIST source URL: {source!r}")
                continue
            temperature = float(reference["T_K"])
            reference_pressure = _require_positive_finite(
                float(reference["p_sat_Pa"]),
                field="reference saturation pressure",
                species=species,
                temperature=temperature,
            )
            reference_liquid_density_kg_m3 = _require_positive_finite(
                float(reference["rho_sat_liq_kg_m3"]),
                field="reference saturated liquid density",
                species=species,
                temperature=temperature,
            )
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
            route_pressure = _require_positive_finite(
                float(result.P_sat),
                field="model saturation pressure",
                species=species,
                temperature=temperature,
            )
            absolute_error = route_pressure - reference_pressure
            molecular_weight = MOLECULAR_WEIGHTS_KG_PER_MOL[species]
            route_vapor_density_kg_m3 = float(result.vapor_density) * molecular_weight
            route_liquid_density_kg_m3 = _require_positive_finite(
                float(result.liquid_density) * molecular_weight,
                field="model saturated liquid density",
                species=species,
                temperature=temperature,
            )
            density_error = route_liquid_density_kg_m3 - reference_liquid_density_kg_m3
            rows.append(
                {
                    "species": reference_species,
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
                    "exact_hessian_available": diagnostics.get("exact_hessian_available", False),
                    "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                    "jacobian_approximation": diagnostics.get("jacobian_approximation", ""),
                    "hessian_backend": diagnostics.get("hessian_backend", ""),
                    "eval_h_calls": diagnostics.get("eval_h_calls", 0),
                    "solver_tolerance": SOLVER_OPTIONS["tolerance"],
                    "max_iterations": SOLVER_OPTIONS["max_iterations"],
                    "source": source,
                }
            )
    if failures:
        raise RuntimeError("Single-component VLE validation rows failed:\n" + "\n".join(failures))
    return sorted(rows, key=lambda row: (str(row["species"]), float(row["T_K"])))


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = generate_validation_rows()

    frame = pd.DataFrame(rows)
    output = RESULTS_DIR / "hydrocarbon_saturation_pressure.csv"
    frame.to_csv(output, index=False)
    summary = frame.groupby("species", as_index=False).agg(
        rows=("T_K", "count"),
        mape_percent=("absolute_relative_error_percent", "mean"),
        max_ape_percent=("absolute_relative_error_percent", "max"),
        liquid_density_mape_percent=("rho_sat_liq_absolute_relative_error_percent", "mean"),
        liquid_density_max_ape_percent=("rho_sat_liq_absolute_relative_error_percent", "max"),
        min_temperature_K=("T_K", "min"),
        max_temperature_K=("T_K", "max"),
    )
    summary.to_csv(RESULTS_DIR / "hydrocarbon_saturation_pressure_summary.csv", index=False)
    endpoint_summary = (
        frame.sort_values("T_K")
        .groupby("species", as_index=False)
        .tail(1)
        .sort_values("species")[
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
