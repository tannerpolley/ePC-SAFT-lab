from __future__ import annotations

import json
import math
import os
import random
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
SHUFFLED_SUBSET_COUNT_PER_TEMPERATURE = 17
SHUFFLED_SUBSET_SEED = 20260629
SOLVER_OPTIONS = EquilibriumSolverOptions(max_iterations=1000, tolerance=1.0e-8)

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

    source_curve = pd.read_csv(SOURCE_CURVE_PATH)
    required_columns = {"temperature_C", "MEA_weight_fraction", "CO2_loading", "species", "mole_fraction"}
    missing_columns = sorted(required_columns - set(source_curve.columns))
    if missing_columns:
        raise ValueError(f"source oracle curve is missing required columns: {missing_columns}")

    species = _species()
    reactions = _reactions()
    groups = _source_groups(source_curve)
    source_state_by_key = {
        (temperature_C, loading): _source_state(rows)
        for temperature_C, loading, rows in groups
    }

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
