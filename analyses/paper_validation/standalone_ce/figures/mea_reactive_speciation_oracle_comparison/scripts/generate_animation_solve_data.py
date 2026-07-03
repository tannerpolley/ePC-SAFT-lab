from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import generate_data as base
import pandas as pd
from epcsaft_equilibrium import EquilibriumSolverOptions

ANIMATION_SOLVE_TEMPERATURES_C = (0.0, 20.0, 40.0, 60.0, 80.0)
ANIMATION_SOLVE_LOADINGS = (0.10, 0.30, 0.50, 0.70)
ANIMATION_SOLVE_OPTIONS = EquilibriumSolverOptions(
    max_iterations=600,
    tolerance=1.0e-7,
    timeout_seconds=90.0,
)
ANIMATION_DATA_PATH = base.RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_temperature_sweep_animation_data.csv"
ANIMATION_SUMMARY_PATH = base.RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_temperature_sweep_solve_summary.csv"
ANIMATION_REPORT_PATH = base.RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_temperature_sweep_solve_summary.json"


def _seed_from_nearest_activity_curve(
    activity_curve: pd.DataFrame,
    *,
    temperature_C: float,
    loading: float,
) -> tuple[list[float], float, float]:
    frame = activity_curve.copy()
    frame["seed_distance"] = (
        (frame["temperature_C"].astype(float) - temperature_C).abs() * 1000.0
        + (frame["CO2_loading"].astype(float) - loading).abs()
    )
    nearest = frame.loc[frame["seed_distance"].idxmin(), ["temperature_C", "CO2_loading"]]
    seed_temperature_C = float(nearest["temperature_C"])
    seed_loading = float(nearest["CO2_loading"])
    rows = activity_curve[
        (activity_curve["temperature_C"].astype(float) == seed_temperature_C)
        & (activity_curve["CO2_loading"].astype(float) == seed_loading)
    ]
    values = {
        str(row.species): max(float(row.mole_fraction), 1.0e-20)
        for row in rows.itertuples(index=False)
        if str(row.species) not in base.COMPOSITE_SPECIES
    }
    missing = sorted(set(base.SPECIES_ORDER) - set(values) - {"H2O"})
    if missing:
        raise ValueError(f"nearest activity seed is missing species: {missing}")
    values["H2O"] = max(1.0 - sum(values.values()), 1.0e-20)
    seed = [values[label] for label in base.SPECIES_ORDER]
    total = sum(seed)
    return [value / total for value in seed], seed_temperature_C, seed_loading


def _seed_from_values(values: dict[str, float]) -> list[float]:
    seed = [max(float(values[label]), 1.0e-20) for label in base.SPECIES_ORDER]
    total = sum(seed)
    return [value / total for value in seed]


def _seed_candidates(
    activity_curve: pd.DataFrame,
    solved_seed_by_loading: dict[float, tuple[list[float], float]],
    *,
    temperature_C: float,
    loading: float,
) -> list[tuple[list[float], float, float, str]]:
    retained_seed, retained_temperature_C, retained_loading = _seed_from_nearest_activity_curve(
        activity_curve,
        temperature_C=temperature_C,
        loading=loading,
    )
    candidates = [
        (
            retained_seed,
            retained_temperature_C,
            retained_loading,
            "nearest_retained_phase2_activity_curve",
        )
    ]
    if loading in solved_seed_by_loading:
        direct_seed, direct_temperature_C = solved_seed_by_loading[loading]
        if direct_temperature_C != temperature_C:
            candidates.append(
                (
                    direct_seed,
                    direct_temperature_C,
                    loading,
                    "direct_solve_previous_temperature_same_loading",
                )
            )
    return candidates


def _failure_diagnostics(exc: Exception, elapsed_seconds: float) -> dict[str, Any]:
    diagnostics = exc.args[1] if len(exc.args) > 1 and isinstance(exc.args[1], dict) else {}
    return {
        "accepted": False,
        "solver_status": str(diagnostics.get("solver_status", "")),
        "application_status": str(diagnostics.get("application_status", "")),
        "failure_class": str(diagnostics.get("failure_class", type(exc).__name__)),
        "activity_model": str(diagnostics.get("activity_model", base.NONIDEAL_ACTIVITY_CONVENTION)),
        "balance_inf_norm": float(diagnostics.get("balance_inf_norm", math.nan)),
        "reaction_stationarity_inf_norm": float(diagnostics.get("reaction_stationarity_inf_norm", math.nan)),
        "seed_source": str(diagnostics.get("initialization", {}).get("seed_source", "")),
        "final_lambda": float(diagnostics.get("continuation", {}).get("final_lambda", math.nan)),
        "stage_count": int(diagnostics.get("continuation", {}).get("stage_count", 0)),
        "runtime_seconds": elapsed_seconds,
    }


def generate() -> dict[str, object]:
    activity_curve = base._read_required_csv(
        base.PHASE2_ACTIVITY_CURVE_PATH,
        required_columns={"temperature_C", "CO2_loading", "species", "mole_fraction", "solver_success"},
    )
    species = base._species()
    reactions = base._reactions()
    activity_candidates = base._phase2_activity_candidates()
    coefficients = base._phase2_reaction_coefficients(activity_candidates)
    source_by_reaction = base._phase2_source_by_reaction(activity_candidates)

    animation_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    solved_seed_by_loading: dict[float, tuple[list[float], float]] = {}
    for temperature_C in ANIMATION_SOLVE_TEMPERATURES_C:
        for loading in ANIMATION_SOLVE_LOADINGS:
            diagnostics: dict[str, Any] | None = None
            values: dict[str, float] = {}
            activities: dict[str, float] = {}
            seed_temperature_C = math.nan
            seed_loading = math.nan
            initial_amount_source = ""
            rejected_initial_amount_sources: list[str] = []
            candidates = _seed_candidates(
                activity_curve,
                solved_seed_by_loading,
                temperature_C=temperature_C,
                loading=loading,
            )
            for attempt_index, (seed, seed_temperature_C, seed_loading, initial_amount_source) in enumerate(
                candidates,
                start=1,
            ):
                mixture = base._phase2_mixture(temperature_C + 273.15, seed)
                start = time.perf_counter()
                try:
                    result = base.reactive_speciation(
                        species=species,
                        reactions=reactions,
                        feed_amounts={"MEA": 1.0, "H2O": base.WATER_PER_AMINE_30WT, "CO2": loading},
                        equilibrium_constants=base._phase2_equilibrium_constants(
                            reactions,
                            temperature_C,
                            activity_convention=base.NONIDEAL_ACTIVITY_CONVENTION,
                            coefficients=coefficients,
                            source_by_reaction=source_by_reaction,
                        ),
                        initial_amounts=seed,
                        solver_options=ANIMATION_SOLVE_OPTIONS,
                        eos_mixture=mixture,
                    )
                    elapsed_seconds = time.perf_counter() - start
                    diagnostics = base._ce_diagnostics(result)
                    diagnostics["runtime_seconds"] = elapsed_seconds
                    values = base._ce_mole_fractions(result)
                    activities = dict(result.activities)
                except Exception as exc:
                    elapsed_seconds = time.perf_counter() - start
                    diagnostics = _failure_diagnostics(exc, elapsed_seconds)
                accepted = bool(diagnostics["accepted"])
                print(
                    json.dumps(
                        {
                            "temperature_C": temperature_C,
                            "CO2_loading": loading,
                            "attempt": attempt_index,
                            "initial_amount_source": initial_amount_source,
                            "accepted": accepted,
                            "runtime_seconds": round(float(diagnostics["runtime_seconds"]), 3),
                            "failure_class": diagnostics["failure_class"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                if accepted:
                    solved_seed_by_loading[loading] = (_seed_from_values(values), temperature_C)
                    for species_label in base.PLOT_SPECIES:
                        animation_rows.append(
                            {
                                "role": "eos_x_gamma_activity_temperature_sweep",
                                "activity_mode": base.NONIDEAL_ACTIVITY_CONVENTION,
                                "temperature_C": temperature_C,
                                "CO2_loading": loading,
                                "species": species_label,
                                "mole_fraction": values[species_label],
                                "activity": activities.get(species_label, math.nan),
                                "solve_accepted": True,
                                "seed_temperature_C": seed_temperature_C,
                                "seed_CO2_loading": seed_loading,
                                "initial_amount_source": initial_amount_source,
                            }
                        )
                    break
                rejected_initial_amount_sources.append(initial_amount_source)
            if diagnostics is None:
                raise RuntimeError(f"no CE solve seed candidates were built for {temperature_C:g} C, loading {loading:g}")
            summary_rows.append(
                {
                    "role": "eos_x_gamma_activity_temperature_sweep_solve",
                    "activity_mode": base.NONIDEAL_ACTIVITY_CONVENTION,
                    "temperature_C": temperature_C,
                    "CO2_loading": loading,
                    "accepted": bool(diagnostics["accepted"]),
                    "solver_status": diagnostics["solver_status"],
                    "application_status": diagnostics["application_status"],
                    "failure_class": diagnostics["failure_class"],
                    "balance_inf_norm": diagnostics["balance_inf_norm"],
                    "reaction_stationarity_inf_norm": diagnostics["reaction_stationarity_inf_norm"],
                    "seed_source": diagnostics["seed_source"],
                    "final_lambda": diagnostics["final_lambda"],
                    "stage_count": diagnostics["stage_count"],
                    "runtime_seconds": diagnostics["runtime_seconds"],
                    "seed_temperature_C": seed_temperature_C,
                    "seed_CO2_loading": seed_loading,
                    "initial_amount_source": initial_amount_source,
                    "rejected_initial_amount_sources": ";".join(rejected_initial_amount_sources),
                    "attempt_count": len(rejected_initial_amount_sources) + int(bool(diagnostics["accepted"])),
                    "max_iterations": ANIMATION_SOLVE_OPTIONS.max_iterations,
                    "tolerance": ANIMATION_SOLVE_OPTIONS.tolerance,
                    "timeout_seconds": ANIMATION_SOLVE_OPTIONS.timeout_seconds,
                }
            )

    summary_frame = pd.DataFrame(summary_rows)
    failed = summary_frame[~summary_frame["accepted"].astype(bool)]
    base.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(animation_rows).to_csv(ANIMATION_DATA_PATH, index=False, float_format="%.12g")
    summary_frame.to_csv(ANIMATION_SUMMARY_PATH, index=False, float_format="%.12g")
    report: dict[str, object] = {
        "schema_version": "epcsaft.standalone_ce.mea_eos_x_gamma_animation_solve.v1",
        "activity_basis": "a_i = gamma_i x_i",
        "temperature_count": len(ANIMATION_SOLVE_TEMPERATURES_C),
        "loading_count": len(ANIMATION_SOLVE_LOADINGS),
        "solve_count": len(summary_frame),
        "accepted_solve_count": int(summary_frame["accepted"].sum()),
        "all_solves_accepted": bool(failed.empty),
        "animation_data_artifact": str(ANIMATION_DATA_PATH.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "solve_summary_artifact": str(ANIMATION_SUMMARY_PATH.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "temperature_grid_C": list(ANIMATION_SOLVE_TEMPERATURES_C),
        "loading_grid": list(ANIMATION_SOLVE_LOADINGS),
        "max_attempt_count": int(summary_frame["attempt_count"].max()),
        "initialization_policy": (
            "each plotted point is a direct reactive_speciation solve; the retained Phase 2 activity curve "
            "provides the first seed candidate, and a previous accepted direct CE solution at the same loading "
            "is tried only when available"
        ),
        "solver_options": {
            "max_iterations": ANIMATION_SOLVE_OPTIONS.max_iterations,
            "tolerance": ANIMATION_SOLVE_OPTIONS.tolerance,
            "timeout_seconds": ANIMATION_SOLVE_OPTIONS.timeout_seconds,
        },
    }
    ANIMATION_REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not failed.empty:
        raise RuntimeError(f"{len(failed)} sparse animation CE solves were rejected; see {ANIMATION_SUMMARY_PATH}")
    return report


def main() -> int:
    report = generate()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
