from __future__ import annotations

import json
import os
import sys

import generate_data as base
import pandas as pd


def generate() -> dict[str, object]:
    if not base.SOURCE_CURVE_PATH.is_file():
        raise FileNotFoundError(f"required source oracle curve is missing: {base.SOURCE_CURVE_PATH}")
    if not base.PHASE2_PARAMETER_DATASET_DIR.is_dir():
        raise FileNotFoundError(f"required Phase 2 parameter snapshot is missing: {base.PHASE2_PARAMETER_DATASET_DIR}")

    source_curve = pd.read_csv(base.SOURCE_CURVE_PATH)
    required_columns = {"temperature_C", "MEA_weight_fraction", "CO2_loading", "species", "mole_fraction"}
    missing_columns = sorted(required_columns - set(source_curve.columns))
    if missing_columns:
        raise ValueError(f"source oracle curve is missing required columns: {missing_columns}")

    species = base._species()
    reactions = base._reactions()
    activity_candidates = base._phase2_activity_candidates()
    coefficients = base._phase2_reaction_coefficients(activity_candidates)
    source_by_reaction = base._phase2_source_by_reaction(activity_candidates)
    groups = base._source_groups(source_curve)
    source_state_by_key = {
        (temperature_C, loading): base._source_state(rows)
        for temperature_C, loading, rows in groups
    }

    plot_frame = base._nonideal_plot_rows(source_curve)
    summary_frame = pd.DataFrame(base._nonideal_curve_summary_rows(plot_frame))
    probe_frame, probe_summary_frame = base._nonideal_ce_probe_rows(
        species=species,
        reactions=reactions,
        source_state_by_key=source_state_by_key,
        coefficients=coefficients,
        source_by_reaction=source_by_reaction,
    )
    reaction_constant_rows = base._reaction_constant_rows(
        reactions=reactions,
        coefficients=coefficients,
        source_by_reaction=source_by_reaction,
    )
    parameter_manifest_frame = base._read_required_csv(
        base.PHASE2_PARAMETER_DATASET_DIR / "phase2_parameter_artifact_manifest.csv",
        required_columns={"path", "source_path", "role", "policy"},
    )
    parameter_manifest_frame = parameter_manifest_frame.assign(
        snapshot_root=str(base.PHASE2_PARAMETER_DATASET_DIR.relative_to(base.REPO_ROOT)).replace("\\", "/")
    )

    base.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_data_path = base.RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_plot_data.csv"
    summary_path = base.RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_summary.csv"
    probe_path = base.RESULTS_DIR / "mea_ce_eos_x_gamma_source_seeded_probe.csv"
    probe_summary_path = base.RESULTS_DIR / "mea_ce_eos_x_gamma_source_seeded_probe_summary.csv"
    reaction_constants_path = base.RESULTS_DIR / "phase2_eos_x_gamma_reaction_constants.csv"
    parameter_manifest_path = base.RESULTS_DIR / "mea_ce_nonideal_parameter_snapshot_manifest.csv"
    report_path = base.RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_summary.json"

    plot_frame.to_csv(plot_data_path, index=False)
    summary_frame.to_csv(summary_path, index=False)
    probe_frame.to_csv(probe_path, index=False)
    probe_summary_frame.to_csv(probe_summary_path, index=False)
    pd.DataFrame(reaction_constant_rows).to_csv(reaction_constants_path, index=False)
    parameter_manifest_frame.to_csv(parameter_manifest_path, index=False)

    activity_rows = plot_frame[plot_frame["role"] == "eos_x_gamma_activity"]
    report: dict[str, object] = {
        "schema_version": "epcsaft.standalone_ce.mea_eos_x_gamma_speciation.v1",
        "activity_basis": "a_i = gamma_i x_i",
        "source_activity_curve": str(base.PHASE2_ACTIVITY_CURVE_PATH.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "source_reference_points": str(base.PHASE2_REFERENCE_POINTS_PATH.relative_to(base.REPO_ROOT)).replace(
            "\\",
            "/",
        ),
        "source_target_roles": str(base.PHASE2_TARGET_ROLES_PATH.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "parameter_snapshot": str(base.PHASE2_PARAMETER_DATASET_DIR.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "reaction_constant_source": str(base.PHASE2_ACTIVITY_CONSTANTS_PATH.relative_to(base.REPO_ROOT)).replace(
            "\\",
            "/",
        ),
        "plot_data_artifact": str(plot_data_path.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "summary_artifact": str(summary_path.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "probe_artifact": str(probe_summary_path.relative_to(base.REPO_ROOT)).replace("\\", "/"),
        "all_activity_curve_solver_success": bool(activity_rows["solver_success"].all()),
        "activity_curve_loading_count_by_temperature": {
            str(float(temperature_C)): int(group["CO2_loading"].nunique())
            for temperature_C, group in activity_rows.groupby("temperature_C", sort=True)
        },
        "reference_point_count_by_temperature": {
            str(float(temperature_C)): len(group)
            for temperature_C, group in plot_frame[plot_frame["role"] == "real_speciation_data"].groupby(
                "temperature_C",
                sort=True,
            )
        },
        "ce_probe": {
            "accepted": bool(probe_summary_frame["accepted"].iloc[0]),
            "temperature_C": float(probe_summary_frame["temperature_C"].iloc[0]),
            "CO2_loading": float(probe_summary_frame["CO2_loading"].iloc[0]),
            "balance_inf_norm": float(probe_summary_frame["balance_inf_norm"].iloc[0]),
            "reaction_stationarity_inf_norm": float(probe_summary_frame["reaction_stationarity_inf_norm"].iloc[0]),
            "runtime_seconds": float(probe_summary_frame["runtime_seconds"].iloc[0]),
            "initial_amount_source": str(probe_summary_frame["initial_amount_source"].iloc[0]),
        },
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    base.apply_native_runtime_env(os.environ)
    report = generate()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    if str(base.REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(base.REPO_ROOT))
    raise SystemExit(main())
