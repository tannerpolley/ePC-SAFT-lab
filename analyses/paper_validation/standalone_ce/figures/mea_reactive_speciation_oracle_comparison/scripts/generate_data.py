from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[6]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft.state.native_adapter import ePCSAFTMixture
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
PHASE2_ACTIVITY_CURVE_PATH = SOURCE_DIR / "phase2_speciation_activity_curves.csv"
PHASE2_PARAMETER_DATASET_DIR = SOURCE_DIR / "mea_thermodynamics_phase2_parameters"
PHASE2_ACTIVITY_CONSTANTS_PATH = SOURCE_DIR / "phase2_activity_constant_candidates.csv"
PHASE2_REACTION_BASIS_PATH = SOURCE_DIR / "phase2_reaction_constant_basis.csv"
PHASE2_SOURCE_VERIFICATION_PATH = SOURCE_DIR / "phase2_reaction_constant_source_verification.csv"

MEA_WEIGHT_FRACTION = 0.3
WATER_PER_AMINE_30WT = 7.909507954125047
MIN_EFFECTIVE_LOADING = 1.0e-6
PRESSURE_PA = 101_325.0
TEMPERATURES_C = (20.0, 40.0)
SHUFFLED_SUBSET_COUNT_PER_TEMPERATURE = 17
SHUFFLED_SUBSET_SEED = 20260629
SOLVER_OPTIONS = EquilibriumSolverOptions(max_iterations=1000, tolerance=1.0e-8)
NONIDEAL_ACTIVITY_CONVENTION = "eos_x_gamma"
NONIDEAL_PROBE_TEMPERATURE_C = 20.0
NONIDEAL_PROBE_LOADING = 0.3
NONIDEAL_PROBE_OPTIONS = EquilibriumSolverOptions(
    max_iterations=300,
    tolerance=1.0e-7,
    timeout_seconds=30.0,
)
PHASE2_RUNTIME_USER_OPTIONS = {
    "elec_model": {
        "rel_perm": {
            "rule": "empirical",
            "differential_mode": "auto",
        },
        "born_model": {
            "d_Born_mode": 3,
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {
                "differential_mode": "auto",
                "comp_dep_delta_d": True,
            },
        },
    },
}

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
PHASE2_REACTION_NAME_BY_ID = {
    "R1": "R1_water_autoionization",
    "R2": "R2_CO2_to_HCO3",
    "R3": "R3_HCO3_to_CO3",
    "R4": "R4_MEACOO_hydrolysis",
    "R5": "R5_MEAH_dissociation",
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


def _read_required_csv(path: Path, *, required_columns: set[str]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"required source snapshot is missing: {path}")
    frame = pd.read_csv(path)
    missing_columns = sorted(required_columns - set(frame.columns))
    if missing_columns:
        raise ValueError(f"{path} is missing required columns: {missing_columns}")
    return frame


def _phase2_activity_candidates() -> pd.DataFrame:
    frame = _read_required_csv(
        PHASE2_ACTIVITY_CONSTANTS_PATH,
        required_columns={"reaction_id", "candidate_source", "source_files", "c1", "c2", "c3", "c4"},
    )
    reaction_ids = frame["reaction_id"].astype(str).tolist()
    if reaction_ids != ["R1", "R2", "R3", "R4", "R5"]:
        raise ValueError(f"unexpected Phase 2 reaction IDs: {reaction_ids}")
    return frame


def _phase2_reaction_coefficients(candidates: pd.DataFrame) -> dict[str, tuple[float, float, float, float]]:
    coefficients: dict[str, tuple[float, float, float, float]] = {}
    for row in candidates.itertuples(index=False):
        reaction_label = PHASE2_REACTION_NAME_BY_ID[str(row.reaction_id)]
        coefficients[reaction_label] = (
            float(row.c1),
            float(row.c2),
            float(row.c3),
            float(row.c4),
        )
    missing = sorted(set(REACTION_CONSTANT_COEFFICIENTS) - set(coefficients))
    if missing:
        raise ValueError(f"missing Phase 2 activity coefficients for: {missing}")
    return coefficients


def _phase2_source_by_reaction(candidates: pd.DataFrame) -> dict[str, str]:
    source_by_reaction: dict[str, str] = {}
    for row in candidates.itertuples(index=False):
        reaction_label = PHASE2_REACTION_NAME_BY_ID[str(row.reaction_id)]
        source_by_reaction[reaction_label] = f"{row.candidate_source}|{row.source_files}"
    return source_by_reaction


def _phase2_ln_k(
    reaction_label: str,
    temperature_K: float,
    coefficients: dict[str, tuple[float, float, float, float]],
) -> float:
    a, b, c, d = coefficients[reaction_label]
    return a + b / temperature_K + c * math.log(temperature_K) + d * temperature_K


def _phase2_equilibrium_constants(
    reactions: list[ChemicalReaction],
    temperature_C: float,
    *,
    activity_convention: str,
    coefficients: dict[str, tuple[float, float, float, float]],
    source_by_reaction: dict[str, str],
) -> list[EquilibriumConstantRecord]:
    temperature_K = temperature_C + 273.15
    standard_state = StandardStateRecord(
        label=f"mea_phase2_{activity_convention}_standard_state",
        activity_convention=activity_convention,
        temperature_K=temperature_K,
        pressure_Pa=PRESSURE_PA,
        eos_reference_phase="liquid",
        metadata={
            "source_project": "MEA-Thermodynamics",
            "source_dataset": "MEA_CO2_H2O_phase2",
            "activity_basis": "a_i = gamma_i x_i",
            "temperature_C": temperature_C,
        },
    )
    return [
        EquilibriumConstantRecord(
            reaction_label=reaction.label,
            value=_phase2_ln_k(reaction.label, temperature_K, coefficients),
            form="ln_K",
            units="dimensionless",
            standard_state=standard_state,
            source="MEA-Thermodynamics Phase 2 source-verified Nasrifar activity constants",
            source_constant_label=source_by_reaction[reaction.label],
            metadata={
                "basis": "mole-fraction activity",
                "activity_convention": activity_convention,
                "temperature_K": temperature_K,
            },
        )
        for reaction in reactions
    ]


def _max_abs(values: dict[str, float]) -> float:
    return max((abs(float(value)) for value in values.values()), default=0.0)


def _json_list(values: Any) -> str:
    return json.dumps(values, separators=(",", ":"))


def _ce_mole_fractions(result: Any) -> dict[str, float]:
    values = {label: float(value) for label, value in zip(result.species_labels, result.mole_fractions.tolist())}
    values["MEA + MEAH+"] = values["MEA"] + values["MEAH+"]
    return values


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


def _ce_diagnostics(result: Any) -> dict[str, Any]:
    diagnostics = dict(result.diagnostics)
    initialization = dict(diagnostics.get("initialization", {}))
    feasible = dict(initialization.get("feasible_initialization", {}))
    continuation = dict(diagnostics.get("continuation", {}))
    trace = list(continuation.get("trace", []))
    corrector = dict(continuation.get("physical_proof_corrector", {}))
    final_stage = dict(trace[-1]) if trace else {}
    return {
        "solver_status": str(diagnostics["solver_status"]),
        "application_status": str(diagnostics["application_status"]),
        "accepted": bool(diagnostics["accepted"]),
        "failure_class": str(diagnostics.get("failure_class", "accepted" if diagnostics["accepted"] else "rejected")),
        "activity_model": str(diagnostics.get("activity_model", "mole_fraction_activity")),
        "balance_inf_norm": _max_abs(result.balances),
        "reaction_stationarity_inf_norm": _max_abs(result.affinities),
        "native_binding": str(diagnostics["native_binding"]),
        "seed_policy": "max_min_feasible_interior_no_oracle",
        "seed_source": str(initialization.get("seed_source", "")),
        "uses_source_oracle_initial_amounts": bool(initialization.get("source_oracle_initial_amounts", False)),
        "feasible_initialization_accepted": bool(feasible.get("accepted", False)),
        "feasible_initialization_rejection_reason": str(feasible.get("rejection_reason", "")),
        "feasible_initialization_margin": float(feasible.get("margin", math.nan)),
        "feasible_initialization_minimum_amount": float(feasible.get("minimum_amount", math.nan)),
        "feasible_initialization_balance_inf_norm": float(feasible.get("balance_inf_norm", math.nan)),
        "direct_final_proof_attempted": bool(continuation.get("direct_final_proof_attempted", False)),
        "direct_final_proof_accepted": bool(continuation.get("direct_final_proof_accepted", False)),
        "final_proof_status": str(continuation.get("final_proof_status", "")),
        "final_stage_id": str(continuation.get("final_stage_id", "")),
        "final_lambda": float(continuation.get("final_lambda", math.nan)),
        "stage_count": int(continuation.get("stage_count", 0)),
        "lambda_values": _json_list(continuation.get("lambda_values", [])),
        "final_stage_solver_status": str(final_stage.get("status", "")),
        "final_stage_application_status": str(final_stage.get("application_status", "")),
        "final_stage_acceptance_status": str(final_stage.get("acceptance_status", "")),
        "physical_proof_corrector_attempted": bool(corrector.get("attempted", False)),
        "physical_proof_corrector_accepted": bool(corrector.get("accepted", False)),
        "physical_proof_corrector_status": str(corrector.get("status", "")),
        "physical_proof_corrector_rejection_reason": str(corrector.get("rejection_reason", "")),
        "physical_proof_corrector_iteration_count": int(corrector.get("iteration_count", 0)),
        "physical_proof_corrector_initial_residual_inf_norm": float(
            corrector.get("initial_residual_inf_norm", math.nan)
        ),
        "physical_proof_corrector_initial_balance_inf_norm": float(
            corrector.get("initial_balance_inf_norm", math.nan)
        ),
        "physical_proof_corrector_initial_reaction_stationarity_inf_norm": float(
            corrector.get("initial_reaction_stationarity_inf_norm", math.nan)
        ),
        "physical_proof_corrector_residual_inf_norm": float(corrector.get("residual_inf_norm", math.nan)),
        "physical_proof_corrector_balance_inf_norm": float(corrector.get("balance_inf_norm", math.nan)),
        "physical_proof_corrector_reaction_stationarity_inf_norm": float(
            corrector.get("reaction_stationarity_inf_norm", math.nan)
        ),
        "physical_proof_corrector_final_residual_inf_norm": float(
            corrector.get("final_residual_inf_norm", math.nan)
        ),
        "physical_proof_corrector_final_balance_inf_norm": float(corrector.get("final_balance_inf_norm", math.nan)),
        "physical_proof_corrector_final_reaction_stationarity_inf_norm": float(
            corrector.get("final_reaction_stationarity_inf_norm", math.nan)
        ),
    }


def _source_diagnostics() -> dict[str, Any]:
    return {
        "solver_status": "source_oracle",
        "application_status": "source_oracle",
        "accepted": True,
        "balance_inf_norm": math.nan,
        "reaction_stationarity_inf_norm": math.nan,
        "native_binding": "MEA.smith_missen.ideal_speciation",
        "seed_policy": "source_oracle_comparison_curve",
        "seed_source": "source_oracle",
        "uses_source_oracle_initial_amounts": False,
    }


def _comparison_rows(
    *,
    role: str,
    temperature_C: float,
    loading: float,
    effective_feed_loading: float,
    source_mole_fractions: dict[str, float],
    ce_mole_fractions: dict[str, float],
    diagnostics: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for species_label in (*SPECIES_ORDER, *COMPOSITE_SPECIES):
        source_value = float(source_mole_fractions[species_label])
        ce_value = float(ce_mole_fractions[species_label])
        rows.append(
            {
                "role": role,
                "temperature_C": temperature_C,
                "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                "CO2_loading": loading,
                "effective_feed_loading": effective_feed_loading,
                "species": species_label,
                "source_mole_fraction": source_value,
                "ce_mole_fraction": ce_value,
                "signed_error": ce_value - source_value,
                "abs_error": abs(ce_value - source_value),
                **diagnostics,
            }
        )
    return rows


def _trace_summary_row(
    *,
    role: str,
    temperature_C: float,
    loading: float,
    effective_feed_loading: float,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    keys = (
        "solver_status",
        "application_status",
        "accepted",
        "balance_inf_norm",
        "reaction_stationarity_inf_norm",
        "seed_policy",
        "seed_source",
        "uses_source_oracle_initial_amounts",
        "feasible_initialization_accepted",
        "feasible_initialization_rejection_reason",
        "feasible_initialization_margin",
        "feasible_initialization_minimum_amount",
        "feasible_initialization_balance_inf_norm",
        "direct_final_proof_attempted",
        "direct_final_proof_accepted",
        "final_proof_status",
        "final_stage_id",
        "final_lambda",
        "stage_count",
        "lambda_values",
        "final_stage_solver_status",
        "final_stage_application_status",
        "final_stage_acceptance_status",
        "physical_proof_corrector_attempted",
        "physical_proof_corrector_accepted",
        "physical_proof_corrector_status",
        "physical_proof_corrector_rejection_reason",
        "physical_proof_corrector_iteration_count",
        "physical_proof_corrector_initial_residual_inf_norm",
        "physical_proof_corrector_initial_balance_inf_norm",
        "physical_proof_corrector_initial_reaction_stationarity_inf_norm",
        "physical_proof_corrector_residual_inf_norm",
        "physical_proof_corrector_balance_inf_norm",
        "physical_proof_corrector_reaction_stationarity_inf_norm",
        "physical_proof_corrector_final_residual_inf_norm",
        "physical_proof_corrector_final_balance_inf_norm",
        "physical_proof_corrector_final_reaction_stationarity_inf_norm",
    )
    return {
        "role": role,
        "temperature_C": temperature_C,
        "CO2_loading": loading,
        "effective_feed_loading": effective_feed_loading,
        "activity_model": str(diagnostics.get("activity_model", "mole_fraction_activity")),
        "failure_class": str(diagnostics["failure_class"]),
        **{key: diagnostics[key] for key in keys},
    }


def _solve_no_oracle(
    *,
    species: list[ChemicalSpecies],
    reactions: list[ChemicalReaction],
    temperature_C: float,
    loading: float,
) -> Any:
    effective_feed_loading = max(float(loading), MIN_EFFECTIVE_LOADING)
    return reactive_speciation(
        species=species,
        reactions=reactions,
        feed_amounts={"MEA": 1.0, "H2O": WATER_PER_AMINE_30WT, "CO2": effective_feed_loading},
        equilibrium_constants=_equilibrium_constants(reactions, temperature_C),
        initial_amounts=None,
        solver_options=SOLVER_OPTIONS,
    )


def _nonideal_plot_rows(source_curve: pd.DataFrame) -> pd.DataFrame:
    phase2_curve = _read_required_csv(
        PHASE2_ACTIVITY_CURVE_PATH,
        required_columns={
            "temperature_C",
            "CO2_loading",
            "effective_CO2_loading",
            "species",
            "mole_fraction",
            "curve_role",
            "solver_success",
        },
    )
    phase2_curve = phase2_curve[
        phase2_curve["temperature_C"].isin(TEMPERATURES_C)
        & phase2_curve["species"].isin(PLOT_SPECIES)
    ].copy()
    if phase2_curve.empty:
        raise ValueError("Phase 2 nonideal activity curve has no retained 20 C or 40 C plot rows.")

    ideal_rows: list[dict[str, Any]] = []
    for temperature_C, loading, rows in _source_groups(source_curve):
        source_mole_fractions = _source_state(rows)
        for species_label in PLOT_SPECIES:
            ideal_rows.append(
                {
                    "role": "ideal_smith_missen_reference",
                    "activity_mode": "mole_fraction_activity",
                    "temperature_C": temperature_C,
                    "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                    "CO2_loading": loading,
                    "effective_feed_loading": max(float(loading), MIN_EFFECTIVE_LOADING),
                    "species": species_label,
                    "mole_fraction": source_mole_fractions[species_label],
                    "solver_success": True,
                    "source_artifact": str(SOURCE_CURVE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "parameter_source": "",
                    "reaction_constant_source": "Smith-Missen Phase 1 retained fixture",
                }
            )

    activity_rows = []
    for row in phase2_curve.itertuples(index=False):
        activity_rows.append(
            {
                "role": "eos_x_gamma_activity",
                "activity_mode": NONIDEAL_ACTIVITY_CONVENTION,
                "temperature_C": float(row.temperature_C),
                "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                "CO2_loading": float(row.CO2_loading),
                "effective_feed_loading": float(row.effective_CO2_loading),
                "species": str(row.species),
                "mole_fraction": float(row.mole_fraction),
                "solver_success": bool(row.solver_success),
                "source_artifact": str(PHASE2_ACTIVITY_CURVE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
                "parameter_source": str(PHASE2_PARAMETER_DATASET_DIR.relative_to(REPO_ROOT)).replace("\\", "/"),
                "reaction_constant_source": str(PHASE2_ACTIVITY_CONSTANTS_PATH.relative_to(REPO_ROOT)).replace(
                    "\\",
                    "/",
                ),
            }
        )

    return (
        pd.DataFrame([*ideal_rows, *activity_rows])
        .sort_values(["temperature_C", "species", "role", "CO2_loading"])
        .reset_index(drop=True)
    )


def _nonideal_curve_summary_rows(plot_frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (role, activity_mode, temperature_C), group in plot_frame.groupby(
        ["role", "activity_mode", "temperature_C"],
        sort=True,
    ):
        rows.append(
            {
                "role": role,
                "activity_mode": activity_mode,
                "temperature_C": float(temperature_C),
                "loading_count": int(group["CO2_loading"].nunique()),
                "species_count": int(group["species"].nunique()),
                "min_CO2_loading": float(group["CO2_loading"].min()),
                "max_CO2_loading": float(group["CO2_loading"].max()),
                "all_solver_success": bool(group["solver_success"].all()),
                "min_mole_fraction": float(group["mole_fraction"].min()),
                "max_mole_fraction": float(group["mole_fraction"].max()),
            }
        )
    return rows


def _reaction_constant_rows(
    *,
    reactions: list[ChemicalReaction],
    coefficients: dict[str, tuple[float, float, float, float]],
    source_by_reaction: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for temperature_C in TEMPERATURES_C:
        for record in _phase2_equilibrium_constants(
            reactions,
            temperature_C,
            activity_convention=NONIDEAL_ACTIVITY_CONVENTION,
            coefficients=coefficients,
            source_by_reaction=source_by_reaction,
        ):
            rows.append(
                {
                    "temperature_C": temperature_C,
                    "temperature_K": temperature_C + 273.15,
                    "activity_mode": NONIDEAL_ACTIVITY_CONVENTION,
                    "reaction_label": record.reaction_label,
                    "ln_K": record.value,
                    "source": record.source,
                    "source_constant_label": record.source_constant_label,
                }
            )
    return rows


def _phase2_mixture(temperature_K: float, seed_mole_fractions: list[float]) -> ePCSAFTMixture:
    return ePCSAFTMixture.from_dataset(
        PHASE2_PARAMETER_DATASET_DIR,
        SPECIES_ORDER,
        seed_mole_fractions,
        temperature_K,
        user_options=PHASE2_RUNTIME_USER_OPTIONS,
    )


def _nearest_source_state(
    source_state_by_key: dict[tuple[float, float], dict[str, float]],
    *,
    temperature_C: float,
    loading: float,
) -> tuple[float, dict[str, float]]:
    candidates = [
        (candidate_loading, values)
        for (candidate_temperature_C, candidate_loading), values in source_state_by_key.items()
        if candidate_temperature_C == temperature_C
    ]
    if not candidates:
        raise ValueError(f"no source states are available for {temperature_C:g} C")
    return min(candidates, key=lambda item: abs(item[0] - loading))


def _nonideal_ce_probe_rows(
    *,
    species: list[ChemicalSpecies],
    reactions: list[ChemicalReaction],
    source_state_by_key: dict[tuple[float, float], dict[str, float]],
    coefficients: dict[str, tuple[float, float, float, float]],
    source_by_reaction: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    source_loading, source_state = _nearest_source_state(
        source_state_by_key,
        temperature_C=NONIDEAL_PROBE_TEMPERATURE_C,
        loading=NONIDEAL_PROBE_LOADING,
    )
    temperature_K = NONIDEAL_PROBE_TEMPERATURE_C + 273.15
    initial_mole_fractions = [max(float(source_state[label]), 1.0e-20) for label in SPECIES_ORDER]
    total = sum(initial_mole_fractions)
    initial_mole_fractions = [value / total for value in initial_mole_fractions]
    mixture = _phase2_mixture(temperature_K, initial_mole_fractions)

    start = time.perf_counter()
    result = reactive_speciation(
        species=species,
        reactions=reactions,
        feed_amounts={"MEA": 1.0, "H2O": WATER_PER_AMINE_30WT, "CO2": NONIDEAL_PROBE_LOADING},
        equilibrium_constants=_phase2_equilibrium_constants(
            reactions,
            NONIDEAL_PROBE_TEMPERATURE_C,
            activity_convention=NONIDEAL_ACTIVITY_CONVENTION,
            coefficients=coefficients,
            source_by_reaction=source_by_reaction,
        ),
        initial_amounts=initial_mole_fractions,
        solver_options=NONIDEAL_PROBE_OPTIONS,
        eos_mixture=mixture,
    )
    elapsed_seconds = time.perf_counter() - start
    diagnostics = _ce_diagnostics(result)
    diagnostics.update(
        {
            "activity_model": NONIDEAL_ACTIVITY_CONVENTION,
            "initial_amount_source": "phase1_smith_missen_nearest_loading",
            "initial_source_CO2_loading": source_loading,
            "runtime_seconds": elapsed_seconds,
        }
    )
    values = _ce_mole_fractions(result)
    species_rows = []
    for species_label in (*SPECIES_ORDER, *COMPOSITE_SPECIES):
        species_rows.append(
            {
                "role": "ce_eos_x_gamma_source_seeded_probe",
                "temperature_C": NONIDEAL_PROBE_TEMPERATURE_C,
                "CO2_loading": NONIDEAL_PROBE_LOADING,
                "effective_feed_loading": NONIDEAL_PROBE_LOADING,
                "species": species_label,
                "mole_fraction": values[species_label],
                "activity": float(result.activities.get(species_label, math.nan)),
                **diagnostics,
            }
        )
    summary = pd.DataFrame(
        [
            {
                "role": "ce_eos_x_gamma_source_seeded_probe",
                "temperature_C": NONIDEAL_PROBE_TEMPERATURE_C,
                "CO2_loading": NONIDEAL_PROBE_LOADING,
                "activity_mode": NONIDEAL_ACTIVITY_CONVENTION,
                "accepted": diagnostics["accepted"],
                "solver_status": diagnostics["solver_status"],
                "application_status": diagnostics["application_status"],
                "balance_inf_norm": diagnostics["balance_inf_norm"],
                "reaction_stationarity_inf_norm": diagnostics["reaction_stationarity_inf_norm"],
                "initial_amount_source": diagnostics["initial_amount_source"],
                "initial_source_CO2_loading": source_loading,
                "runtime_seconds": elapsed_seconds,
                "max_iterations": NONIDEAL_PROBE_OPTIONS.max_iterations,
                "tolerance": NONIDEAL_PROBE_OPTIONS.tolerance,
                "timeout_seconds": NONIDEAL_PROBE_OPTIONS.timeout_seconds,
            }
        ]
    )
    return pd.DataFrame(species_rows), summary


def _source_groups(source_curve: pd.DataFrame) -> list[tuple[float, float, pd.DataFrame]]:
    frame = source_curve[
        source_curve["temperature_C"].isin(TEMPERATURES_C)
        & (source_curve["MEA_weight_fraction"].astype(float) == MEA_WEIGHT_FRACTION)
    ]
    return [
        (float(temperature_C), float(loading), rows.copy())
        for (temperature_C, loading), rows in frame.groupby(["temperature_C", "CO2_loading"], sort=True)
    ]


def _shuffled_subset_keys(groups: list[tuple[float, float, pd.DataFrame]]) -> list[tuple[float, float]]:
    rng = random.Random(SHUFFLED_SUBSET_SEED)
    keys: list[tuple[float, float]] = []
    for temperature_C in TEMPERATURES_C:
        loadings = sorted(loading for temp, loading, _rows in groups if temp == temperature_C)
        middle = loadings[1:-1]
        rng.shuffle(middle)
        selected = sorted({loadings[0], loadings[-1], *middle[: SHUFFLED_SUBSET_COUNT_PER_TEMPERATURE - 2]})
        keys.extend((temperature_C, loading) for loading in selected)
    rng.shuffle(keys)
    return keys


def _strict_summary(frame: pd.DataFrame) -> dict[str, Any]:
    return {
        "row_count": len(frame),
        "loading_count": int(frame["CO2_loading"].nunique()),
        "all_accepted": bool(frame["accepted"].all()),
        "all_no_source_oracle_seed": bool(frame["uses_source_oracle_initial_amounts"].eq(False).all()),
        "all_final_lambda_one": bool((frame["final_lambda"] == 1.0).all()),
        "max_abs_error": float(frame["abs_error"].max()),
        "max_balance_inf_norm": float(frame["balance_inf_norm"].max()),
        "max_reaction_stationarity_inf_norm": float(frame["reaction_stationarity_inf_norm"].max()),
    }


def generate() -> dict[str, Any]:
    if not SOURCE_CURVE_PATH.is_file():
        raise FileNotFoundError(f"required source oracle curve is missing: {SOURCE_CURVE_PATH}")
    if not PHASE2_PARAMETER_DATASET_DIR.is_dir():
        raise FileNotFoundError(f"required Phase 2 parameter snapshot is missing: {PHASE2_PARAMETER_DATASET_DIR}")

    source_curve = pd.read_csv(SOURCE_CURVE_PATH)
    required_columns = {"temperature_C", "MEA_weight_fraction", "CO2_loading", "species", "mole_fraction"}
    missing_columns = sorted(required_columns - set(source_curve.columns))
    if missing_columns:
        raise ValueError(f"source oracle curve is missing required columns: {missing_columns}")

    species = _species()
    reactions = _reactions()
    phase2_activity_candidates = _phase2_activity_candidates()
    phase2_coefficients = _phase2_reaction_coefficients(phase2_activity_candidates)
    phase2_source_by_reaction = _phase2_source_by_reaction(phase2_activity_candidates)
    groups = _source_groups(source_curve)
    source_state_by_key = {
        (temperature_C, loading): _source_state(rows)
        for temperature_C, loading, rows in groups
    }
    nonideal_plot_frame = _nonideal_plot_rows(source_curve)
    nonideal_summary_frame = pd.DataFrame(_nonideal_curve_summary_rows(nonideal_plot_frame))
    phase2_reaction_constant_rows = _reaction_constant_rows(
        reactions=reactions,
        coefficients=phase2_coefficients,
        source_by_reaction=phase2_source_by_reaction,
    )
    parameter_manifest_frame = _read_required_csv(
        PHASE2_PARAMETER_DATASET_DIR / "phase2_parameter_artifact_manifest.csv",
        required_columns={"path", "source_path", "role", "policy"},
    )
    parameter_manifest_frame = parameter_manifest_frame.assign(
        snapshot_root=str(PHASE2_PARAMETER_DATASET_DIR.relative_to(REPO_ROOT)).replace("\\", "/")
    )

    ce_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    trace_summary_rows: list[dict[str, Any]] = []
    reaction_constant_rows: list[dict[str, Any]] = []

    for temperature_C in TEMPERATURES_C:
        for record in _equilibrium_constants(reactions, temperature_C):
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

    for temperature_C, loading, _rows in groups:
        source_mole_fractions = source_state_by_key[(temperature_C, loading)]
        effective_feed_loading = max(loading, MIN_EFFECTIVE_LOADING)
        result = _solve_no_oracle(
            species=species,
            reactions=reactions,
            temperature_C=temperature_C,
            loading=loading,
        )
        ce_mole_fractions = _ce_mole_fractions(result)
        ce_diagnostics = _ce_diagnostics(result)
        source_rows.extend(
            _rows_for_state(
                role="source_oracle",
                temperature_C=temperature_C,
                loading=loading,
                effective_feed_loading=effective_feed_loading,
                mole_fractions=source_mole_fractions,
                diagnostics=_source_diagnostics(),
            )
        )
        ce_rows.extend(
            _rows_for_state(
                role="ce_unassisted_pointwise",
                temperature_C=temperature_C,
                loading=loading,
                effective_feed_loading=effective_feed_loading,
                mole_fractions=ce_mole_fractions,
                diagnostics=ce_diagnostics,
            )
        )
        comparison_rows.extend(
            _comparison_rows(
                role="ce_unassisted_pointwise",
                temperature_C=temperature_C,
                loading=loading,
                effective_feed_loading=effective_feed_loading,
                source_mole_fractions=source_mole_fractions,
                ce_mole_fractions=ce_mole_fractions,
                diagnostics=ce_diagnostics,
            )
        )
        trace_summary_rows.append(
            _trace_summary_row(
                role="ce_unassisted_pointwise",
                temperature_C=temperature_C,
                loading=loading,
                effective_feed_loading=effective_feed_loading,
                diagnostics=ce_diagnostics,
            )
        )

    shuffled_rows: list[dict[str, Any]] = []
    for order_index, (temperature_C, loading) in enumerate(_shuffled_subset_keys(groups)):
        source_mole_fractions = source_state_by_key[(temperature_C, loading)]
        result = _solve_no_oracle(
            species=species,
            reactions=reactions,
            temperature_C=temperature_C,
            loading=loading,
        )
        ce_mole_fractions = _ce_mole_fractions(result)
        diagnostics = _ce_diagnostics(result)
        max_abs_error = max(
            abs(ce_mole_fractions[species_label] - source_mole_fractions[species_label])
            for species_label in (*SPECIES_ORDER, *COMPOSITE_SPECIES)
        )
        shuffled_rows.append(
            {
                "shuffle_seed": SHUFFLED_SUBSET_SEED,
                "shuffle_order_index": order_index,
                "temperature_C": temperature_C,
                "CO2_loading": loading,
                "effective_feed_loading": max(loading, MIN_EFFECTIVE_LOADING),
                "max_abs_error": max_abs_error,
                **_trace_summary_row(
                    role="ce_unassisted_shuffled_subset",
                    temperature_C=temperature_C,
                    loading=loading,
                    effective_feed_loading=max(loading, MIN_EFFECTIVE_LOADING),
                    diagnostics=diagnostics,
                ),
            }
        )

    nonideal_probe_frame, nonideal_probe_summary_frame = _nonideal_ce_probe_rows(
        species=species,
        reactions=reactions,
        source_state_by_key=source_state_by_key,
        coefficients=phase2_coefficients,
        source_by_reaction=phase2_source_by_reaction,
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    source_frame = pd.DataFrame(source_rows)
    ce_frame = pd.DataFrame(ce_rows)
    comparison_frame = pd.DataFrame(comparison_rows)
    trace_summary_frame = pd.DataFrame(trace_summary_rows)
    shuffled_audit = pd.DataFrame(shuffled_rows)
    overlay_plot_frame = pd.concat(
        [
            source_frame[source_frame["species"].isin(PLOT_SPECIES)],
            ce_frame[ce_frame["species"].isin(PLOT_SPECIES)],
        ],
        ignore_index=True,
    ).sort_values(["temperature_C", "species", "role", "CO2_loading"])
    summary_frame = (
        comparison_frame.groupby(["role", "temperature_C", "species"], sort=True)
        .agg(
            loading_count=("CO2_loading", "nunique"),
            max_abs_error=("abs_error", "max"),
            mean_abs_error=("abs_error", "mean"),
            max_balance_inf_norm=("balance_inf_norm", "max"),
            max_reaction_stationarity_inf_norm=("reaction_stationarity_inf_norm", "max"),
            max_stage_count=("stage_count", "max"),
        )
        .reset_index()
    )

    source_frame.to_csv(RESULTS_DIR / "source_oracle_speciation_curve.csv", index=False)
    ce_frame.to_csv(RESULTS_DIR / "ce_reactive_speciation_curve.csv", index=False)
    overlay_plot_frame.to_csv(RESULTS_DIR / "mea_ce_oracle_speciation_plot_data.csv", index=False)
    comparison_frame.to_csv(RESULTS_DIR / "mea_ce_oracle_speciation_errors.csv", index=False)
    summary_frame.to_csv(RESULTS_DIR / "mea_ce_oracle_speciation_error_summary.csv", index=False)
    trace_summary_frame.to_csv(RESULTS_DIR / "mea_ce_continuation_trace_summary.csv", index=False)
    trace_summary_frame.to_csv(RESULTS_DIR / "mea_ce_unassisted_seed_audit.csv", index=False)
    shuffled_audit.to_csv(RESULTS_DIR / "mea_ce_shuffled_subset_audit.csv", index=False)
    pd.DataFrame(reaction_constant_rows).to_csv(RESULTS_DIR / "smith_missen_reaction_constants.csv", index=False)
    nonideal_plot_frame.to_csv(RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_plot_data.csv", index=False)
    nonideal_summary_frame.to_csv(RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_summary.csv", index=False)
    nonideal_probe_frame.to_csv(RESULTS_DIR / "mea_ce_eos_x_gamma_source_seeded_probe.csv", index=False)
    nonideal_probe_summary_frame.to_csv(
        RESULTS_DIR / "mea_ce_eos_x_gamma_source_seeded_probe_summary.csv",
        index=False,
    )
    pd.DataFrame(phase2_reaction_constant_rows).to_csv(
        RESULTS_DIR / "phase2_eos_x_gamma_reaction_constants.csv",
        index=False,
    )
    parameter_manifest_frame.to_csv(RESULTS_DIR / "mea_ce_nonideal_parameter_snapshot_manifest.csv", index=False)

    strict = _strict_summary(comparison_frame)
    shuffled_strict = {
        "attempt_count": len(shuffled_audit),
        "all_accepted": bool(shuffled_audit["accepted"].all()),
        "all_no_source_oracle_seed": bool(
            shuffled_audit["uses_source_oracle_initial_amounts"].eq(False).all()
        ),
        "max_abs_error": float(shuffled_audit["max_abs_error"].max()),
        "artifact": str((RESULTS_DIR / "mea_ce_shuffled_subset_audit.csv").relative_to(REPO_ROOT)).replace(
            "\\",
            "/",
        ),
    }
    robustness_required_fields = [
        "activity_model",
        "solver_status",
        "application_status",
        "accepted",
        "failure_class",
        "balance_inf_norm",
        "reaction_stationarity_inf_norm",
        "seed_source",
        "uses_source_oracle_initial_amounts",
        "stage_count",
        "final_proof_status",
        "physical_proof_corrector_attempted",
        "physical_proof_corrector_rejection_reason",
        "physical_proof_corrector_initial_reaction_stationarity_inf_norm",
        "physical_proof_corrector_final_reaction_stationarity_inf_norm",
        "physical_proof_corrector_final_balance_inf_norm",
    ]
    robustness_diagnostics = {
        "artifact": str((RESULTS_DIR / "mea_ce_unassisted_seed_audit.csv").relative_to(REPO_ROOT)).replace(
            "\\",
            "/",
        ),
        "required_fields": robustness_required_fields,
        "activity_model": "mole_fraction_activity",
        "failure_classes": sorted(str(value) for value in trace_summary_frame["failure_class"].dropna().unique()),
        "accepted_state_point_count": int((trace_summary_frame["failure_class"] == "accepted").sum()),
        "state_point_count": len(trace_summary_frame),
    }
    corrected_stationarity = trace_summary_frame[
        trace_summary_frame["physical_proof_corrector_attempted"].eq(True)
        & (
            trace_summary_frame["physical_proof_corrector_initial_reaction_stationarity_inf_norm"]
            > 1.0e-6
        )
        & (
            trace_summary_frame["physical_proof_corrector_final_reaction_stationarity_inf_norm"]
            <= 1.0e-6
        )
        & (trace_summary_frame["physical_proof_corrector_final_balance_inf_norm"] <= 1.0e-8)
    ]
    report = {
        "schema_version": "epcsaft.standalone_ce.mea_speciation_oracle_comparison.v2",
        "source_oracle": str(SOURCE_CURVE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "public_route": "reactive_speciation",
        "ce_workflow": "epcsaft_equilibrium.reactive_speciation",
        "temperature_C": list(TEMPERATURES_C),
        "loading_count": int(comparison_frame["CO2_loading"].nunique()),
        "species": list(SPECIES_ORDER),
        "plot_species": list(PLOT_SPECIES),
        "initialization": "omitted initial_amounts; native max-min feasible initializer",
        "seed_policy": "max_min_feasible_interior_no_oracle",
        "uses_source_oracle_initial_amounts": False,
        "solver_options": {"max_iterations": SOLVER_OPTIONS.max_iterations, "tolerance": SOLVER_OPTIONS.tolerance},
        "zero_loading_note": "source-oracle loading 0.0 is solved with effective CE feed loading 1e-6 to match the Smith-Missen source solver's minimum loading convention",
        "pointwise_unassisted": {
            **strict,
            "artifact": str((RESULTS_DIR / "ce_reactive_speciation_curve.csv").relative_to(REPO_ROOT)).replace(
                "\\",
                "/",
            ),
        },
        "ce_owned_continuation_trace": {
            "artifact": str((RESULTS_DIR / "mea_ce_continuation_trace_summary.csv").relative_to(REPO_ROOT)).replace(
                "\\",
                "/",
            ),
            "max_stage_count": int(trace_summary_frame["stage_count"].max()),
            "homotopy_point_count": int((trace_summary_frame["stage_count"] > 1).sum()),
            "physical_proof_corrector_point_count": int(
                trace_summary_frame["physical_proof_corrector_accepted"].eq(True).sum()
            ),
            "corrected_stationarity_point_count": len(corrected_stationarity),
            "max_initial_physical_proof_corrector_reaction_stationarity_inf_norm": float(
                corrected_stationarity["physical_proof_corrector_initial_reaction_stationarity_inf_norm"].max()
            ),
            "max_final_physical_proof_corrector_reaction_stationarity_inf_norm": float(
                trace_summary_frame["physical_proof_corrector_final_reaction_stationarity_inf_norm"].max()
            ),
            "max_final_physical_proof_corrector_balance_inf_norm": float(
                trace_summary_frame["physical_proof_corrector_final_balance_inf_norm"].max()
            ),
            "all_physical_proof_corrector_rejection_reasons_empty": bool(
                (trace_summary_frame["physical_proof_corrector_rejection_reason"].fillna("") == "").all()
            ),
            "all_final_lambda_one": bool((trace_summary_frame["final_lambda"] == 1.0).all()),
            "all_final_proof_accepted": bool((trace_summary_frame["final_proof_status"] == "accepted").all()),
        },
        "robustness_diagnostics": robustness_diagnostics,
        "shuffled_subset": shuffled_strict,
        "nonideal_eos_x_gamma": {
            "activity_basis": "a_i = gamma_i x_i",
            "source_activity_curve": str(PHASE2_ACTIVITY_CURVE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "parameter_snapshot": str(PHASE2_PARAMETER_DATASET_DIR.relative_to(REPO_ROOT)).replace("\\", "/"),
            "reaction_constant_source": str(PHASE2_ACTIVITY_CONSTANTS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "reaction_constant_source_verification": str(
                PHASE2_SOURCE_VERIFICATION_PATH.relative_to(REPO_ROOT)
            ).replace("\\", "/"),
            "plot_data_artifact": str(
                (RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_plot_data.csv").relative_to(REPO_ROOT)
            ).replace("\\", "/"),
            "summary_artifact": str(
                (RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_summary.csv").relative_to(REPO_ROOT)
            ).replace("\\", "/"),
            "parameter_manifest_artifact": str(
                (RESULTS_DIR / "mea_ce_nonideal_parameter_snapshot_manifest.csv").relative_to(REPO_ROOT)
            ).replace("\\", "/"),
            "all_activity_curve_solver_success": bool(
                nonideal_plot_frame[nonideal_plot_frame["role"] == "eos_x_gamma_activity"]["solver_success"].all()
            ),
            "activity_curve_loading_count_by_temperature": {
                str(float(temperature_C)): int(group["CO2_loading"].nunique())
                for temperature_C, group in nonideal_plot_frame[
                    nonideal_plot_frame["role"] == "eos_x_gamma_activity"
                ].groupby("temperature_C", sort=True)
            },
            "ce_probe": {
                "artifact": str(
                    (RESULTS_DIR / "mea_ce_eos_x_gamma_source_seeded_probe_summary.csv").relative_to(REPO_ROOT)
                ).replace("\\", "/"),
                "accepted": bool(nonideal_probe_summary_frame["accepted"].iloc[0]),
                "temperature_C": float(nonideal_probe_summary_frame["temperature_C"].iloc[0]),
                "CO2_loading": float(nonideal_probe_summary_frame["CO2_loading"].iloc[0]),
                "balance_inf_norm": float(nonideal_probe_summary_frame["balance_inf_norm"].iloc[0]),
                "reaction_stationarity_inf_norm": float(
                    nonideal_probe_summary_frame["reaction_stationarity_inf_norm"].iloc[0]
                ),
                "runtime_seconds": float(nonideal_probe_summary_frame["runtime_seconds"].iloc[0]),
                "initial_amount_source": str(nonideal_probe_summary_frame["initial_amount_source"].iloc[0]),
            },
        },
        "max_abs_error": strict["max_abs_error"],
        "max_balance_inf_norm": strict["max_balance_inf_norm"],
        "max_reaction_stationarity_inf_norm": strict["max_reaction_stationarity_inf_norm"],
        "all_solver_status_success": bool((comparison_frame["solver_status"] == "success").all()),
        "all_application_status_succeeded": bool((comparison_frame["application_status"] == "solve_succeeded").all()),
        "all_accepted": strict["all_accepted"],
        "strict_gates_passed": bool(
            strict["all_accepted"]
            and strict["all_no_source_oracle_seed"]
            and strict["all_final_lambda_one"]
            and strict["max_abs_error"] <= 1.0e-8
            and strict["max_balance_inf_norm"] <= 1.0e-8
            and strict["max_reaction_stationarity_inf_norm"] <= 1.0e-6
            and shuffled_strict["all_accepted"]
            and shuffled_strict["all_no_source_oracle_seed"]
            and shuffled_strict["max_abs_error"] <= 1.0e-8
        ),
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
