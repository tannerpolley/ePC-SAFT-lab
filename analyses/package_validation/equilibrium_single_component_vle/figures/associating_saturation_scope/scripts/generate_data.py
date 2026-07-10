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
from epcsaft.model.parameters import PureRecord

FIGURE_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_ROOT / "results"
REFERENCE_SOURCE = (
    REPO_ROOT
    / "data"
    / "reference"
    / "pure_component"
    / "saturation_properties"
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
    parameter_set = epcsaft.ParameterSet.from_records(
        [
            PureRecord(
                component=COMPONENT_LABELS[component],
                molar_mass=float(row["MW"]),
                m=float(row["m"]),
                sigma=float(row["s"]),
                epsilon_k=float(row["e"]),
                charge=float(row["z"]),
                epsilon_k_ab=float(row["e_assoc"]),
                kappa_ab=float(row["vol_a"]),
                association_scheme=row["assoc_scheme"],
                relative_permittivity=float(row["dielc"]),
                born_diameter=float(row["d_born"]),
                solvation_factor=float(row["f_solv"]),
            )
        ],
        metadata={
            "source": row["source"],
            "source_backed": True,
        },
    )
    return epcsaft.Mixture(parameter_set), row


def _route_probe(component: str, temperature: float) -> dict[str, object]:
    mixture, _row = _mixture_for_component(component)
    try:
        epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=temperature).solve()
    except epcsaft.InputError as exc:
        return {
            "route_eligible": False,
            "route_status": "input_rejected_associating_component",
            "route_message": str(exc),
        }
    return {
        "route_eligible": True,
        "route_status": "accepted_associating_component",
        "route_message": "Production single_component_vle accepted the associating pure-component input.",
    }


def _load_source_rows() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    missing: list[Path] = []
    for component in COMPONENT_LABELS:
        path = REFERENCE_SOURCE / component / "saturation_properties.csv"
        if not path.exists():
            missing.append(path)
            continue
        frames.append(pd.read_csv(path))
    if missing:
        raise RuntimeError(
            "Missing pure-component saturation-properties files: "
            + ", ".join(str(path) for path in missing)
        )
    return pd.concat(frames, ignore_index=True)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    source = _load_source_rows()
    source = source[source["component"].isin(COMPONENT_LABELS)].copy()
    if source.empty:
        raise RuntimeError(f"{REFERENCE_SOURCE} contains no water or methanol rows.")

    route_by_component: dict[str, dict[str, object]] = {}
    parameter_rows = {component: _load_parameter_row(component) for component in COMPONENT_LABELS}
    for component, subset in source.groupby("component"):
        first_temperature = float(subset.sort_values("T_K").iloc[0]["T_K"])
        route_by_component[component] = _route_probe(component, first_temperature)

    rows: list[dict[str, object]] = []
    for raw in source.sort_values(["component", "T_K"]).to_dict("records"):
        component = str(raw["component"])
        parameter = parameter_rows[component]
        route = route_by_component[component]
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
                "route_eligible": route["route_eligible"],
                "route_status": route["route_status"],
                "route_message": route["route_message"],
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
