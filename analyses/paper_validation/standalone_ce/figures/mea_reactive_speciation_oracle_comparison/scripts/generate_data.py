from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[6]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    EquilibriumConstantRecord,
    EquilibriumSolverOptions,
    StandardStateRecord,
    reactive_speciation,
)

FIGURE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SOURCE_CURVE_PATH = SOURCE_DIR / "phase1_speciation_curve.csv"

MEA_WEIGHT_FRACTION = 0.3
WATER_PER_AMINE_30WT = 7.909507954125047
MIN_EFFECTIVE_LOADING = 1.0e-6
PRESSURE_PA = 101_325.0
TEMPERATURES_C = (20.0, 40.0)

SPECIES_ORDER = (
    "CO2",
    "MEA",
    "H2O",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
)
COMPOSITE_SPECIES = ("MEA + MEAH+",)
PLOT_SPECIES = (
    "CO2",
    "MEA",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
    "MEA + MEAH+",
)

REACTION_CONSTANT_COEFFICIENTS = {
    "R1_water_autoionization": (132.899, -13445.9, -22.4773, 0.0),
    "R2_CO2_to_HCO3": (231.465, -12092.10, -36.7816, 0.0),
    "R3_HCO3_to_CO3": (216.049, -12431.70, -35.4819, 0.0),
    "R4_MEACOO_hydrolysis": (-1.8652, -1545.3, 0.0, 0.0),
    "R5_MEAH_dissociation": (2.1211, -8189.38, 0.0, -0.007484),
}


def _species() -> list[ChemicalSpecies]:
    return [
        ChemicalSpecies("CO2", {"C": 1.0, "O": 2.0}),
        ChemicalSpecies("MEA", {"C": 2.0, "H": 7.0, "N": 1.0, "O": 1.0}),
        ChemicalSpecies("H2O", {"H": 2.0, "O": 1.0}),
        ChemicalSpecies("MEAH+", {"C": 2.0, "H": 8.0, "N": 1.0, "O": 1.0}, charge=1.0),
        ChemicalSpecies("MEACOO-", {"C": 3.0, "H": 6.0, "N": 1.0, "O": 3.0}, charge=-1.0),
        ChemicalSpecies("HCO3-", {"H": 1.0, "C": 1.0, "O": 3.0}, charge=-1.0),
        ChemicalSpecies("CO3^2-", {"C": 1.0, "O": 3.0}, charge=-2.0),
        ChemicalSpecies("H3O+", {"H": 3.0, "O": 1.0}, charge=1.0),
        ChemicalSpecies("OH-", {"H": 1.0, "O": 1.0}, charge=-1.0),
    ]


def _reactions() -> list[ChemicalReaction]:
    return [
        ChemicalReaction("R1_water_autoionization", {"H2O": -2.0, "H3O+": 1.0, "OH-": 1.0}),
        ChemicalReaction("R2_CO2_to_HCO3", {"CO2": -1.0, "H2O": -2.0, "HCO3-": 1.0, "H3O+": 1.0}),
        ChemicalReaction("R3_HCO3_to_CO3", {"H2O": -1.0, "HCO3-": -1.0, "CO3^2-": 1.0, "H3O+": 1.0}),
        ChemicalReaction("R4_MEACOO_hydrolysis", {"MEA": 1.0, "H2O": -1.0, "MEACOO-": -1.0, "HCO3-": 1.0}),
        ChemicalReaction("R5_MEAH_dissociation", {"MEA": 1.0, "H2O": -1.0, "MEAH+": -1.0, "H3O+": 1.0}),
    ]


def _source_state(rows: pd.DataFrame) -> dict[str, float]:
    values = {
        str(row.species): float(row.mole_fraction)
        for row in rows.itertuples(index=False)
        if str(row.species) not in COMPOSITE_SPECIES
    }
    missing = sorted(set(SPECIES_ORDER) - set(values) - {"H2O"})
    if missing:
        raise ValueError(f"source oracle rows are missing required species: {missing}")
    values["H2O"] = 1.0 - sum(values.values())
    if values["H2O"] <= 0.0:
        raise ValueError("computed source-oracle H2O mole fraction is not positive")
    values["MEA + MEAH+"] = values["MEA"] + values["MEAH+"]
    return values


def _ln_k(reaction_label: str, temperature_K: float) -> float:
    a, b, c, d = REACTION_CONSTANT_COEFFICIENTS[reaction_label]
    return a + b / temperature_K + c * math.log(temperature_K) + d * temperature_K


def _equilibrium_constants(
    reactions: list[ChemicalReaction],
    temperature_C: float,
) -> list[EquilibriumConstantRecord]:
    temperature_K = temperature_C + 273.15
    standard_state = StandardStateRecord(
        label="smith_missen_mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=temperature_K,
        pressure_Pa=PRESSURE_PA,
        metadata={
            "source_project": "MEA-Thermodynamics",
            "source_module": "MEA.smith_missen.ideal_speciation",
            "temperature_C": temperature_C,
        },
    )
    return [
        EquilibriumConstantRecord(
            reaction_label=reaction.label,
            value=_ln_k(reaction.label, temperature_K),
            form="ln_K",
            units="dimensionless",
            standard_state=standard_state,
            source="MEA-Thermodynamics Smith-Missen Phase 1 retained fixture",
            source_constant_label=reaction.label,
            metadata={"basis": "mole fraction", "temperature_K": temperature_K},
        )
        for reaction in reactions
    ]


def _initial_amounts(species: list[ChemicalSpecies], source_mole_fractions: dict[str, float]) -> list[float]:
    amine_fraction = (
        source_mole_fractions["MEA"]
        + source_mole_fractions["MEAH+"]
        + source_mole_fractions["MEACOO-"]
    )
    if amine_fraction <= 0.0:
        raise ValueError("source-oracle amine fraction is not positive")
    scale = 1.0 / amine_fraction
    return [source_mole_fractions[item.label] * scale for item in species]


def _max_abs(values: dict[str, float]) -> float:
    return max((abs(float(value)) for value in values.values()), default=0.0)


def _rows_for_state(
    *,
    role: str,
    temperature_C: float,
    loading: float,
    effective_feed_loading: float,
    mole_fractions: dict[str, float],
    diagnostics: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for species in (*SPECIES_ORDER, *COMPOSITE_SPECIES):
        rows.append(
            {
                "role": role,
                "temperature_C": temperature_C,
                "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                "CO2_loading": loading,
                "effective_feed_loading": effective_feed_loading,
                "species": species,
                "mole_fraction": mole_fractions[species],
                **diagnostics,
            }
        )
    return rows


def generate() -> dict[str, Any]:
    if not SOURCE_CURVE_PATH.is_file():
        raise FileNotFoundError(f"required source oracle curve is missing: {SOURCE_CURVE_PATH}")

    source_curve = pd.read_csv(SOURCE_CURVE_PATH)
    required_columns = {"temperature_C", "MEA_weight_fraction", "CO2_loading", "species", "mole_fraction"}
    missing_columns = sorted(required_columns - set(source_curve.columns))
    if missing_columns:
        raise ValueError(f"source oracle curve is missing required columns: {missing_columns}")

    species = _species()
    reactions = _reactions()
    solver_options = EquilibriumSolverOptions(max_iterations=300, tolerance=1.0e-6)

    ce_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    reaction_constant_rows: list[dict[str, Any]] = []

    for temperature_C in TEMPERATURES_C:
        constants = _equilibrium_constants(reactions, temperature_C)
        for record in constants:
            reaction_constant_rows.append(
                {
                    "temperature_C": temperature_C,
                    "temperature_K": temperature_C + 273.15,
                    "reaction_label": record.reaction_label,
                    "ln_K": record.value,
                    "source": record.source,
                    "source_constant_label": record.source_constant_label,
                }
            )

    grouped = source_curve[
        source_curve["temperature_C"].isin(TEMPERATURES_C)
        & (source_curve["MEA_weight_fraction"].astype(float) == MEA_WEIGHT_FRACTION)
    ].groupby(["temperature_C", "CO2_loading"], sort=True)

    for (temperature_C, loading), rows in grouped:
        temperature_C = float(temperature_C)
        loading = float(loading)
        source_mole_fractions = _source_state(rows)
        effective_feed_loading = max(loading, MIN_EFFECTIVE_LOADING)
        result = reactive_speciation(
            species=species,
            reactions=reactions,
            feed_amounts={"MEA": 1.0, "H2O": WATER_PER_AMINE_30WT, "CO2": effective_feed_loading},
            equilibrium_constants=_equilibrium_constants(reactions, temperature_C),
            initial_amounts=_initial_amounts(species, source_mole_fractions),
            solver_options=solver_options,
        )
        ce_mole_fractions = {
            label: float(value)
            for label, value in zip(result.species_labels, result.mole_fractions.tolist())
        }
        ce_mole_fractions["MEA + MEAH+"] = ce_mole_fractions["MEA"] + ce_mole_fractions["MEAH+"]
        ce_diagnostics = {
            "solver_status": str(result.diagnostics["solver_status"]),
            "application_status": str(result.diagnostics["application_status"]),
            "accepted": bool(result.diagnostics["accepted"]),
            "balance_inf_norm": _max_abs(result.balances),
            "reaction_stationarity_inf_norm": _max_abs(result.affinities),
            "native_binding": str(result.diagnostics["native_binding"]),
        }
        source_diagnostics = {
            "solver_status": "source_oracle",
            "application_status": "source_oracle",
            "accepted": True,
            "balance_inf_norm": math.nan,
            "reaction_stationarity_inf_norm": math.nan,
            "native_binding": "MEA.smith_missen.ideal_speciation",
        }
        ce_rows.extend(
            _rows_for_state(
                role="ce_reactive_speciation",
                temperature_C=temperature_C,
                loading=loading,
                effective_feed_loading=effective_feed_loading,
                mole_fractions=ce_mole_fractions,
                diagnostics=ce_diagnostics,
            )
        )
        source_rows.extend(
            _rows_for_state(
                role="source_oracle",
                temperature_C=temperature_C,
                loading=loading,
                effective_feed_loading=effective_feed_loading,
                mole_fractions=source_mole_fractions,
                diagnostics=source_diagnostics,
            )
        )
        for species_label in (*SPECIES_ORDER, *COMPOSITE_SPECIES):
            source_value = float(source_mole_fractions[species_label])
            ce_value = float(ce_mole_fractions[species_label])
            comparison_rows.append(
                {
                    "temperature_C": temperature_C,
                    "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                    "CO2_loading": loading,
                    "effective_feed_loading": effective_feed_loading,
                    "species": species_label,
                    "source_mole_fraction": source_value,
                    "ce_mole_fraction": ce_value,
                    "signed_error": ce_value - source_value,
                    "abs_error": abs(ce_value - source_value),
                    "balance_inf_norm": ce_diagnostics["balance_inf_norm"],
                    "reaction_stationarity_inf_norm": ce_diagnostics["reaction_stationarity_inf_norm"],
                    "solver_status": ce_diagnostics["solver_status"],
                    "application_status": ce_diagnostics["application_status"],
                    "accepted": ce_diagnostics["accepted"],
                }
            )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    source_frame = pd.DataFrame(source_rows)
    ce_frame = pd.DataFrame(ce_rows)
    comparison_frame = pd.DataFrame(comparison_rows)
    overlay_plot_frame = pd.concat(
        [
            source_frame[source_frame["species"].isin(PLOT_SPECIES)],
            ce_frame[ce_frame["species"].isin(PLOT_SPECIES)],
        ],
        ignore_index=True,
    ).sort_values(["temperature_C", "species", "role", "CO2_loading"])
    summary_frame = (
        comparison_frame.groupby(["temperature_C", "species"], sort=True)
        .agg(
            loading_count=("CO2_loading", "nunique"),
            max_abs_error=("abs_error", "max"),
            mean_abs_error=("abs_error", "mean"),
            max_balance_inf_norm=("balance_inf_norm", "max"),
            max_reaction_stationarity_inf_norm=("reaction_stationarity_inf_norm", "max"),
        )
        .reset_index()
    )

    source_frame.to_csv(RESULTS_DIR / "source_oracle_speciation_curve.csv", index=False)
    ce_frame.to_csv(RESULTS_DIR / "ce_reactive_speciation_curve.csv", index=False)
    overlay_plot_frame.to_csv(RESULTS_DIR / "mea_ce_oracle_speciation_plot_data.csv", index=False)
    comparison_frame.to_csv(RESULTS_DIR / "mea_ce_oracle_speciation_errors.csv", index=False)
    summary_frame.to_csv(RESULTS_DIR / "mea_ce_oracle_speciation_error_summary.csv", index=False)
    pd.DataFrame(reaction_constant_rows).to_csv(RESULTS_DIR / "smith_missen_reaction_constants.csv", index=False)

    report = {
        "schema_version": "epcsaft.standalone_ce.mea_speciation_oracle_comparison.v1",
        "source_oracle": str(SOURCE_CURVE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "public_route": "reactive_speciation",
        "ce_workflow": "epcsaft_equilibrium.reactive_speciation",
        "temperature_C": list(TEMPERATURES_C),
        "loading_count": int(comparison_frame["CO2_loading"].nunique()),
        "species": list(SPECIES_ORDER),
        "plot_species": list(PLOT_SPECIES),
        "initialization": "source-oracle mole fractions scaled to one mole total amine for each loading",
        "zero_loading_note": "source-oracle loading 0.0 is solved with effective CE feed loading 1e-6 to match the Smith-Missen source solver's minimum loading convention",
        "max_abs_error": float(comparison_frame["abs_error"].max()),
        "max_balance_inf_norm": float(comparison_frame["balance_inf_norm"].max()),
        "max_reaction_stationarity_inf_norm": float(comparison_frame["reaction_stationarity_inf_norm"].max()),
        "all_solver_status_success": bool((comparison_frame["solver_status"] == "success").all()),
        "all_application_status_succeeded": bool((comparison_frame["application_status"] == "solve_succeeded").all()),
        "all_accepted": bool(comparison_frame["accepted"].all()),
    }
    (RESULTS_DIR / "mea_ce_oracle_speciation_comparison_summary.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    report = generate()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
