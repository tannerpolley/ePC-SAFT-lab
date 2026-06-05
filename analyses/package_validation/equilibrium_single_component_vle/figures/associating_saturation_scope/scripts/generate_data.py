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
REFERENCE_SOURCE = (
    REPO_ROOT
    / "data"
    / "reference"
    / "pure_component"
    / "saturation_density"
    / "water_methanol_nist_saturation.csv"
)
HELD_PARAMETERS = REPO_ROOT / "analyses" / "paper_validation" / "2012_held" / "parameters" / "pure" / "water.csv"
COMPONENT_LABELS = {"methanol": "Methanol", "water": "Water"}
PARAMETER_ROWS = {"methanol": "Methanol", "water": "H2O"}


def _load_parameter_row(component: str) -> dict[str, str]:
    target = PARAMETER_ROWS[component]
    with HELD_PARAMETERS.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["component"] == target:
                return row
    raise RuntimeError(f"Could not find {target} in {HELD_PARAMETERS}.")


def _mixture_for_component(component: str) -> tuple[Any, dict[str, str]]:
    row = _load_parameter_row(component)
    parameter_set = epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([float(row["MW"])], dtype=float),
            "m": np.asarray([float(row["m"])], dtype=float),
            "s": np.asarray([float(row["s"])], dtype=float),
            "e": np.asarray([float(row["e"])], dtype=float),
            "e_assoc": np.asarray([float(row["e_assoc"])], dtype=float),
            "vol_a": np.asarray([float(row["vol_a"])], dtype=float),
            "assoc_scheme": [row["assoc_scheme"]],
        },
        species=[COMPONENT_LABELS[component]],
    )
    return epcsaft.Mixture(parameter_set), row


def _route_rejection(component: str, temperature: float) -> str:
    mixture, _row = _mixture_for_component(component)
    try:
        epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=temperature).solve()
    except epcsaft.InputError as exc:
        return str(exc)
    raise RuntimeError(
        "Production single_component_vle unexpectedly accepted an associating component; "
        "update this scope artifact before retaining a fit plot."
    )


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    source = pd.read_csv(REFERENCE_SOURCE)
    source = source[source["component"].isin(COMPONENT_LABELS)].copy()
    if source.empty:
        raise RuntimeError(f"{REFERENCE_SOURCE} contains no water or methanol rows.")

    rejection_by_component: dict[str, str] = {}
    parameter_rows = {component: _load_parameter_row(component) for component in COMPONENT_LABELS}
    for component, subset in source.groupby("component"):
        first_temperature = float(subset.sort_values("T_K").iloc[0]["T_K"])
        rejection_by_component[component] = _route_rejection(component, first_temperature)

    rows: list[dict[str, object]] = []
    for raw in source.sort_values(["component", "T_K"]).to_dict("records"):
        component = str(raw["component"])
        parameter = parameter_rows[component]
        rows.append(
            {
                "component": component,
                "label": COMPONENT_LABELS[component],
                "T_K": float(raw["T_K"]),
                "p_sat_nist_Pa": float(raw["p_sat_Pa"]),
                "rho_sat_liq_nist_mol_m3": float(raw["rho_sat_liq_mol_m3"]),
                "rho_sat_liq_nist_kg_m3": float(raw["rho_sat_liq_mol_m3"]) * float(parameter["MW"]),
                "phase": raw["phase"],
                "source_name": raw["source_name"],
                "source_url": raw["source_url"],
                "parameter_source": parameter["source"],
                "assoc_scheme": parameter["assoc_scheme"],
                "e_assoc_over_k_K": float(parameter["e_assoc"]),
                "route_eligible": False,
                "route_status": "input_rejected_associating_component",
                "route_rejection_message": rejection_by_component[component],
            }
        )

    frame = pd.DataFrame(rows)
    output = RESULTS_DIR / "associating_saturation_scope.csv"
    frame.to_csv(output, index=False)
    summary = (
        frame.groupby("component", as_index=False)
        .agg(
            rows=("T_K", "count"),
            min_temperature_K=("T_K", "min"),
            max_temperature_K=("T_K", "max"),
            min_p_sat_Pa=("p_sat_nist_Pa", "min"),
            max_p_sat_Pa=("p_sat_nist_Pa", "max"),
            min_liquid_density_mol_m3=("rho_sat_liq_nist_mol_m3", "min"),
            max_liquid_density_mol_m3=("rho_sat_liq_nist_mol_m3", "max"),
            route_status=("route_status", "first"),
        )
        .sort_values("component")
    )
    summary.to_csv(RESULTS_DIR / "associating_saturation_scope_summary.csv", index=False)
    print(f"wrote {output}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
