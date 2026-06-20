from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[6]
for import_root in (
    REPO_ROOT,
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from scripts.dev.native_runtime_env import apply_to_current_process
from scripts.validation import native_freshness

apply_to_current_process()

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import epcsaft
import epcsaft_equilibrium
from epcsaft_equilibrium._native import extension_native_core

FIGURE_ID = "figure_05"
STEM = "gross_2002_figure_05_replication"
TEMPERATURE_K = 313.15
MIN_COMPOSITION = 1.0e-6
SERIES_ORDER = ("1-propanol-benzene", "2-propanol-benzene")
SYSTEM_CONFIG = {
    "1-propanol-benzene": {
        "species": ["1-Propanol", "Benzene"],
        "system": "1-propanol/benzene",
        "k_ij": 0.020,
        "m": [2.9997, 2.4653],
        "s": [3.2522, 3.6478],
        "e": [233.40, 287.35],
        "e_assoc": [2276.8, 0.0],
        "vol_a": [0.015268, 0.0],
        "MW": [60.096e-3, 78.114e-3],
        "curve_color": "#2c7fb8",
    },
    "2-propanol-benzene": {
        "species": ["2-Propanol", "Benzene"],
        "system": "2-propanol/benzene",
        "k_ij": 0.021,
        "m": [3.0929, 2.4653],
        "s": [3.2085, 3.6478],
        "e": [208.42, 287.35],
        "e_assoc": [2253.9, 0.0],
        "vol_a": [0.024675, 0.0],
        "MW": [60.096e-3, 78.114e-3],
        "curve_color": "#111111",
    },
}

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_CSV = SOURCE_DIR / f"{STEM}_source_points.csv"
SOURCE_METADATA_JSON = SOURCE_DIR / f"{STEM}_digitization_metadata.json"
QA_OVERLAY = SOURCE_DIR / f"{STEM}_digitization_qa_overlay.png"
MODEL_CSV = RESULTS_DIR / f"{STEM}_model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / f"{STEM}_plotted_data.csv"
SCORE_JSON = RESULTS_DIR / f"{STEM}_score.json"
SUMMARY_JSON = RESULTS_DIR / f"{STEM}_summary.json"
PNG = RESULTS_DIR / f"{STEM}.png"
SVG = RESULTS_DIR / f"{STEM}.svg"
SIDECAR = RESULTS_DIR / f"{STEM}.mpl.yaml"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return _relative(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _load_source_rows() -> list[dict[str, Any]]:
    with SOURCE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError("Gross 2002 Figure 5 source CSV is empty.")
    return rows


def _mixture(series: str) -> epcsaft.Mixture:
    config = SYSTEM_CONFIG[series]
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            {
                "MW": np.asarray(config["MW"]),
                "m": np.asarray(config["m"]),
                "s": np.asarray(config["s"]),
                "e": np.asarray(config["e"]),
                "e_assoc": np.asarray(config["e_assoc"]),
                "vol_a": np.asarray(config["vol_a"]),
                "assoc_scheme": ["2B", None],
                "k_ij": np.asarray([[0.0, config["k_ij"]], [config["k_ij"], 0.0]]),
                "z": np.asarray([0.0, 0.0]),
                "dielc": np.asarray([1.0, 1.0]),
            },
            species=config["species"],
            metadata={
                "source": "Gross/Sadowski 2002 Figure 5",
                "paper": "Gross and Sadowski 2002",
                "table": "Gross 2002 figure caption plus Gross 2001 pure-component table",
                "figure": "Figure 5",
                "source_path": "analyses/paper_validation/2002_gross",
                "source_backed": True,
                "reference_system": config["system"],
            },
        )
    )


def _pure_mixture(component: str, source_label: str, config: dict[str, Any]) -> epcsaft.Mixture:
    if component not in config["species"]:
        raise ValueError(component)
    index = config["species"].index(component)
    payload = {
        "MW": np.asarray([config["MW"][index]]),
        "m": np.asarray([config["m"][index]]),
        "s": np.asarray([config["s"][index]]),
        "e": np.asarray([config["e"][index]]),
        "e_assoc": np.asarray([config["e_assoc"][index]]),
        "vol_a": np.asarray([config["vol_a"][index]]),
        "assoc_scheme": ["2B" if config["e_assoc"][index] else None],
    }
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            payload,
            species=[component],
            metadata={"source": source_label, "source_backed": True},
        )
    )


def _role_coordinate_key(role: str) -> str:
    return "x_alcohol" if role == "bubble_curve" else "y_alcohol"


def _solve_route_point(
    mixture: epcsaft.Mixture,
    route: str,
    composition: float,
    continuation_state: dict[str, Any] | None = None,
) -> epcsaft_equilibrium.EquilibriumResult:
    comp = min(1.0 - MIN_COMPOSITION, max(MIN_COMPOSITION, composition))
    solver_options: dict[str, Any] = {
        "max_iterations": 320,
        "tolerance": 1.0e-6,
        "ipopt_iteration_history_limit": 12,
        "ipopt_acceptable_tolerance": 1.0e-7,
        "ipopt_constraint_violation_tolerance": 1.0e-7,
        "ipopt_dual_infeasibility_tolerance": 1.0e-8,
        "ipopt_complementarity_tolerance": 1.0e-8,
    }
    if continuation_state is not None:
        solver_options["continuation_state"] = continuation_state
    if route == "bubble_pressure":
        return epcsaft_equilibrium.Equilibrium(
            mixture,
            route=route,
            T=TEMPERATURE_K,
            x=[comp, 1.0 - comp],
        ).solve(solver_options=solver_options)
    return epcsaft_equilibrium.Equilibrium(
        mixture,
        route=route,
        T=TEMPERATURE_K,
        y=[comp, 1.0 - comp],
    ).solve(solver_options=solver_options)


def _solve_series(source_rows: list[dict[str, Any]], series: str) -> list[dict[str, Any]]:
    config = SYSTEM_CONFIG[series]
    mixture = _mixture(series)
    output_rows: list[dict[str, Any]] = []
    pure_cache: dict[str, epcsaft_equilibrium.EquilibriumResult] = {}
    for role, route in (("bubble_curve", "bubble_pressure"), ("dew_curve", "dew_pressure")):
        continuation_state: dict[str, Any] | None = None
        curve_rows = [row for row in source_rows if row["series"] == series and row["source_role"] == role]
        coordinate_key = _role_coordinate_key(role)
        for row in sorted(curve_rows, key=lambda item: float(item[coordinate_key])):
            composition = float(row[coordinate_key])
            if composition <= 1.0e-9 or composition >= 1.0 - 1.0e-9:
                pure_component = config["species"][0] if composition >= 1.0 - 1.0e-9 else config["species"][1]
                if pure_component not in pure_cache:
                    pure_cache[pure_component] = epcsaft_equilibrium.Equilibrium(
                        _pure_mixture(pure_component, f"Gross/Sadowski 2002 Figure 5 pure {pure_component}", config),
                        route="single_component_vle",
                        T=TEMPERATURE_K,
                    ).solve(solver_options={"max_iterations": 220, "tolerance": 1.0e-8, "ipopt_print_level": 0})
                result = pure_cache[pure_component]
                diagnostics = result.diagnostics
                output_rows.append(
                    {
                        "series": series,
                        "source_role": role,
                        "system": config["system"],
                        "x_alcohol": composition,
                        "y_alcohol": composition,
                        "T_K": TEMPERATURE_K,
                        "P_bar": float(result.P_sat) / 1.0e5,
                        "route": "single_component_vle",
                        "problem_kind": result.problem_kind,
                        "route_status": diagnostics.get("route_status", ""),
                        "solver_status": diagnostics.get("solver_status", ""),
                        "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                        "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
                        "postsolve_accepted": bool(diagnostics.get("postsolve_accepted")),
                        "hessian_backend": diagnostics.get("hessian_backend", ""),
                        "iteration_count": diagnostics.get("iteration_count", ""),
                    }
                )
                continue
            result = _solve_route_point(mixture, route, composition, continuation_state)
            diagnostics = result.diagnostics
            continuation_state = diagnostics.get("continuation_state")
            if diagnostics.get("hessian_approximation") != "exact" or diagnostics.get("exact_hessian_available") is not True:
                raise RuntimeError(f"{series} {role} at composition={composition:.3f} did not report exact Hessian support.")
            if diagnostics.get("postsolve_accepted") is not True:
                raise RuntimeError(f"{series} {role} at composition={composition:.3f} was not postsolve accepted.")
            output_rows.append(
                {
                    "series": series,
                    "source_role": role,
                    "system": config["system"],
                    "x_alcohol": float(result.x[0]),
                    "y_alcohol": float(result.y[0]),
                    "T_K": TEMPERATURE_K,
                    "P_bar": float(result.pressure) / 1.0e5,
                    "route": result.route,
                    "problem_kind": result.problem_kind,
                    "route_status": diagnostics.get("route_status", ""),
                    "solver_status": diagnostics.get("solver_status", ""),
                    "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                    "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
                    "postsolve_accepted": bool(diagnostics.get("postsolve_accepted")),
                    "hessian_backend": diagnostics.get("hessian_backend", ""),
                    "iteration_count": diagnostics.get("iteration_count", ""),
                }
            )
    return output_rows


def _score(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> dict[str, Any]:
    series_scores: dict[str, dict[str, Any]] = {}
    all_errors: list[float] = []
    for series in SERIES_ORDER:
        source_curve_rows = [row for row in source_rows if row["series"] == series]
        model_curve_rows = [row for row in model_rows if row["series"] == series]
        series_errors: list[float] = []
        for role in ("bubble_curve", "dew_curve"):
            source_branch = [row for row in source_curve_rows if row["source_role"] == role]
            model_branch = [row for row in model_curve_rows if row["source_role"] == role]
            coordinate_key = _role_coordinate_key(role)
            x = np.asarray([float(row[coordinate_key]) for row in model_branch], dtype=float)
            p = np.asarray([float(row["P_bar"]) for row in model_branch], dtype=float)
            order = np.argsort(x)
            for source_row in source_branch:
                composition = float(source_row[coordinate_key])
                source_pressure = float(source_row["P_bar"])
                model_pressure = float(np.interp(composition, x[order], p[order]))
                series_errors.append(model_pressure - source_pressure)
        rmse = math.sqrt(sum(value * value for value in series_errors) / len(series_errors))
        max_error = max(abs(value) for value in series_errors)
        score = max(0.0, min(10.0, 10.0 - rmse / 0.01))
        series_scores[series] = {
            "source_point_count": len(source_curve_rows),
            "model_point_count": len(model_curve_rows),
            "rmse_axis": {"P_bar": rmse, "composition_component_1": 0.0},
            "max_axis_error": {"P_bar": max_error, "composition_component_1": 0.0},
            "normalized_plot_score": score,
            "branch_coverage_score": 1.0,
            "derivative_status": "verified_exact",
            "pass": score >= 8.0,
        }
        all_errors.extend(series_errors)
    all_rmse = math.sqrt(sum(value * value for value in all_errors) / len(all_errors))
    all_max = max(abs(value) for value in all_errors)
    normalized_score = min(item["normalized_plot_score"] for item in series_scores.values())
    return {
        "source_point_count": len(source_rows),
        "model_point_count": len(model_rows),
        "rmse_axis": {"P_bar": all_rmse, "composition_component_1": 0.0},
        "max_axis_error": {"P_bar": all_max, "composition_component_1": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": 1.0,
        "derivative_status": "verified_exact",
        "pass": normalized_score >= 8.0,
        "series_scores": series_scores,
        "score_basis": "pressure-coordinate RMSE against calibrated Gross 2002 Figure 5 digitized PC-SAFT curve traces",
    }


def _write_plot(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], score_payload: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
    for series in SERIES_ORDER:
        config = SYSTEM_CONFIG[series]
        model_series = [row for row in model_rows if row["series"] == series]
        bubble_model = sorted([row for row in model_series if row["source_role"] == "bubble_curve"], key=lambda row: float(row["x_alcohol"]))
        dew_model = sorted([row for row in model_series if row["source_role"] == "dew_curve"], key=lambda row: float(row["y_alcohol"]))
        source_bubble = [row for row in source_rows if row["series"] == series and row["source_role"] == "bubble_curve"]
        ax.plot(
            [1.0 - float(row["x_alcohol"]) for row in bubble_model],
            [float(row["P_bar"]) for row in bubble_model],
            color=config["curve_color"],
            linewidth=2.0,
            label=f"PC-SAFT {series} bubble",
        )
        ax.plot(
            [1.0 - float(row["y_alcohol"]) for row in dew_model],
            [float(row["P_bar"]) for row in dew_model],
            color=config["curve_color"],
            linewidth=1.8,
            alpha=0.78,
            label=f"PC-SAFT {series} dew",
        )
        ax.scatter(
            [1.0 - float(row["x_alcohol"]) for row in source_bubble],
            [float(row["P_bar"]) for row in source_bubble],
            s=42,
            marker="o" if series == "1-propanol-benzene" else "D",
            facecolors="none",
            edgecolors=config["curve_color"],
            linewidths=1.3,
            label=f"Retained {series} curve trace",
            zorder=3,
        )
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.06, 0.31)
    ax.set_xlabel(r"$x_{\mathrm{Benzene}}$ or $y_{\mathrm{Benzene}}$")
    ax.set_ylabel("P / bar")
    ax.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.legend(loc="lower left", fontsize=7, frameon=False)
    ax.set_title("Gross/Sadowski 2002 Figure 5 PC-SAFT VLE replication", fontsize=11)
    fig.text(0.02, 0.01, f"minimum system score: {score_payload['normalized_plot_score']:.2f}; exact Hessian route verified", fontsize=8)
    fig.savefig(PNG, dpi=180)
    fig.savefig(SVG)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            [
                "figure_id: figure_05",
                f"png: {_relative(PNG)}",
                f"svg: {_relative(SVG)}",
                "x_axis: composition_component_1",
                "y_axis: pressure_bar",
                "matplotlib_backend: Agg",
                "style: paper-scale P-x/y overlay for both propanol isomers with retained source traces and public-route PC-SAFT curves",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_plotted_csv(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        rows.append(
            {
                "dataset": "paper_curve",
                "series": row["series"],
                "source_role": row["source_role"],
                "system": row["system"],
                "T_K": row["T_K"],
                "P_bar": row["P_bar"],
                "x_alcohol": row["x_alcohol"],
                "y_alcohol": row["y_alcohol"],
                "paper_x_benzene": 1.0 - float(row[_role_coordinate_key(row["source_role"])]),
                "source_reference": row["source_reference"],
            }
        )
    for row in model_rows:
        rows.append(
            {
                "dataset": "package_model",
                "series": row["series"],
                "source_role": row["source_role"],
                "system": row["system"],
                "T_K": row["T_K"],
                "P_bar": row["P_bar"],
                "x_alcohol": row["x_alcohol"],
                "y_alcohol": row["y_alcohol"],
                "paper_x_benzene": 1.0 - float(row["x_alcohol"] if row["source_role"] == "bubble_curve" else row["y_alcohol"]),
                "source_reference": "epcsaft_equilibrium public bubble/dew exact Hessian route",
            }
        )
    _write_csv(
        PLOTTED_CSV,
        rows,
        ["dataset", "series", "source_role", "system", "T_K", "P_bar", "x_alcohol", "y_alcohol", "paper_x_benzene", "source_reference"],
    )


def _native_receipt() -> dict[str, Any]:
    receipt = native_freshness.build_receipt(
        native_module=extension_native_core(),
        checker_command=[
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_gross_2002_full_replication.py",
            "--json",
            "--require-exact-association-hessian",
            "--require-fresh-native",
        ],
    )
    return native_freshness.receipt_to_jsonable(receipt)


def _update_manifest(score_payload: dict[str, Any], receipt: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["native_freshness_receipt"] = receipt
    artifacts = {
        "source_csv": _relative(SOURCE_CSV),
        "source_metadata_json": _relative(SOURCE_METADATA_JSON),
        "digitization_qa_overlay": _relative(QA_OVERLAY),
        "model_csv": _relative(MODEL_CSV),
        "plotted_csv": _relative(PLOTTED_CSV),
        "score_json": _relative(SCORE_JSON),
        "summary_json": _relative(SUMMARY_JSON),
        "png": _relative(PNG),
        "svg": _relative(SVG),
        "sidecar": _relative(SIDECAR),
    }
    for record in manifest["figures"]:
        if record.get("figure_id") != FIGURE_ID:
            continue
        record.update(
            {
                "replication_status": "accepted" if score_payload["pass"] else "planned",
                "counts_toward_completion": bool(score_payload["pass"]),
                "requires_exact_association_hessian": True,
                "artifacts": artifacts,
                "remaining_work": [] if score_payload["pass"] else ["improve Figure 5 replication score to the acceptance threshold"],
                "source_data_basis": "calibrated Gross 2002 Figure 5 solid-curve source traces retained separately for 1-propanol/benzene and 2-propanol/benzene",
                "score": {
                    "normalized_plot_score": score_payload["normalized_plot_score"],
                    "branch_coverage_score": score_payload["branch_coverage_score"],
                    "derivative_status": score_payload["derivative_status"],
                    "pass": score_payload["pass"],
                },
            }
        )
        break
    _write_json(MANIFEST_PATH, manifest)


def main() -> int:
    source_rows = _load_source_rows()
    model_rows: list[dict[str, Any]] = []
    for series in SERIES_ORDER:
        model_rows.extend(_solve_series(source_rows, series))
    score_payload = _score(source_rows, model_rows)
    receipt = _native_receipt()
    _write_csv(
        MODEL_CSV,
        model_rows,
        [
            "series",
            "source_role",
            "system",
            "x_alcohol",
            "y_alcohol",
            "T_K",
            "P_bar",
            "route",
            "problem_kind",
            "route_status",
            "solver_status",
            "hessian_approximation",
            "exact_hessian_available",
            "postsolve_accepted",
            "hessian_backend",
            "iteration_count",
        ],
    )
    _write_plotted_csv(source_rows, model_rows)
    _write_json(SCORE_JSON, score_payload)
    _write_plot(source_rows, model_rows, score_payload)
    summary = {
        "figure_id": FIGURE_ID,
        "status": "accepted" if score_payload["pass"] else "blocked",
        "artifacts": {
            "source_csv": SOURCE_CSV,
            "source_metadata_json": SOURCE_METADATA_JSON,
            "digitization_qa_overlay": QA_OVERLAY,
            "model_csv": MODEL_CSV,
            "plotted_csv": PLOTTED_CSV,
            "score_json": SCORE_JSON,
            "summary_json": SUMMARY_JSON,
            "png": PNG,
            "svg": SVG,
            "sidecar": SIDECAR,
        },
        "source_point_count": len(source_rows),
        "model_point_count": len(model_rows),
        "score": score_payload,
        "native_route": {
            "public_entrypoint": "epcsaft_equilibrium.Equilibrium(mixture, route='bubble_pressure'/'dew_pressure', T=..., x=.../y=...).solve()",
            "derivative_status": score_payload["derivative_status"],
            "model_csv": MODEL_CSV,
            "native_freshness_receipt": receipt,
        },
    }
    _write_json(SUMMARY_JSON, summary)
    _update_manifest(score_payload, receipt)
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0 if score_payload["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
