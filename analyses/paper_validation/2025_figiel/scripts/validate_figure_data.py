from __future__ import annotations

import argparse
import csv
import math
import subprocess
import sys
import sys as _bootstrap_sys
from pathlib import Path
from pathlib import Path as _BootstrapPath
from types import ModuleType

for _candidate in _BootstrapPath(__file__).resolve().parents:
    if (_candidate / "scripts" / "plot_outputs.py").is_file():
        if str(_candidate) not in _bootstrap_sys.path:
            _bootstrap_sys.path.insert(0, str(_candidate))
        break
else:
    raise ModuleNotFoundError("Could not locate repo root containing scripts/plot_outputs.py")
from scripts.plot_outputs import REPO_ROOT

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

PLOT_SCRIPTS = [
    ROOT.parent / "figures" / f"figure_{index:02d}" / "scripts" / f"plot_figure_{index}.py"
    for index in range(1, 10)
]


def _load_figure_data() -> ModuleType:
    from shared import figure_data

    return figure_data


def _validate_visual_qc_report() -> list[str]:
    report = ROOT.parent / "docs" / "visual_qc.md"
    if not report.exists():
        return [f"missing visual QA report {report}"]
    text = report.read_text(encoding="utf-8")
    failures: list[str] = []
    for index in range(1, 10):
        if f"Figure {index}" not in text:
            failures.append(f"visual_qc.md missing Figure {index} section")
        image_rel = (
            "analyses/paper_validation/2025_figiel/figures/"
            f"figure_{index:02d}/source/paper_source_01_figiel_2025_figure_{index + 1:03d}.png"
        )
        if image_rel not in text:
            failures.append(f"visual_qc.md missing source image reference for Figure {index}")
    return failures


def _numeric_series(rows: list[dict[str, str]], series_id: str) -> tuple[list[float], list[float]]:
    points: list[tuple[float, float]] = []
    for row in rows:
        if row.get("series_id") != series_id:
            continue
        try:
            x_value = float(row["x_value"])
            y_value = float(row["y_value"])
        except (KeyError, ValueError):
            continue
        if math.isfinite(x_value) and math.isfinite(y_value):
            points.append((x_value, y_value))
    points.sort()
    return [point[0] for point in points], [point[1] for point in points]


def _interp(x_grid: list[float], y_grid: list[float], x_value: float) -> float:
    if x_value < x_grid[0] or x_value > x_grid[-1]:
        raise ValueError(f"x={x_value} lies outside model range [{x_grid[0]}, {x_grid[-1]}]")
    upper = 1
    while upper < len(x_grid) and x_grid[upper] < x_value:
        upper += 1
    if upper >= len(x_grid):
        return y_grid[-1]
    lower = max(0, upper - 1)
    x0, x1 = x_grid[lower], x_grid[upper]
    y0, y1 = y_grid[lower], y_grid[upper]
    if x1 == x0:
        return y0
    fraction = (x_value - x0) / (x1 - x0)
    return y0 + fraction * (y1 - y0)


def _validate_model_fit_quality(figure_data: ModuleType) -> list[str]:
    gates = {
        "figure_5": {"rmse": 0.35, "max_abs": 1.25, "first_nonzero_max": 0.98},
        "figure_9": {"rmse": 0.12, "max_abs": 0.30, "first_nonzero_max": 0.98},
    }
    failures: list[str] = []
    for figure_id, limits in gates.items():
        payload = figure_data.payload_path(figure_id)
        with payload.open("r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        model_ids = sorted(
            {row["series_id"] for row in rows if row.get("source_type") == "model" and row.get("series_id", "").startswith("model_")}
        )
        for model_id in model_ids:
            data_id = "data_" + model_id.removeprefix("model_")
            model_x, model_y = _numeric_series(rows, model_id)
            data_x, data_y = _numeric_series(rows, data_id)
            if len(model_x) < 2:
                failures.append(f"{figure_id}:{model_id}: model curve has fewer than two numeric points")
                continue
            if not data_x:
                failures.append(f"{figure_id}:{model_id}: missing matching literature series {data_id}")
                continue
            overlap_errors: list[float] = []
            for x_value, y_value in zip(data_x, data_y):
                if model_x[0] <= x_value <= model_x[-1]:
                    overlap_errors.append(_interp(model_x, model_y, x_value) - y_value)
            if len(overlap_errors) < 5:
                failures.append(f"{figure_id}:{model_id}: fewer than five data points overlap the model domain")
                continue
            rmse = math.sqrt(sum(error * error for error in overlap_errors) / len(overlap_errors))
            max_abs = max(abs(error) for error in overlap_errors)
            first_nonzero = next((y for x, y in zip(model_x, model_y) if x > 0.0), model_y[0])
            if rmse > limits["rmse"]:
                failures.append(f"{figure_id}:{model_id}: RMSE {rmse:.3g} exceeds {limits['rmse']:.3g}")
            if max_abs > limits["max_abs"]:
                failures.append(f"{figure_id}:{model_id}: max abs error {max_abs:.3g} exceeds {limits['max_abs']:.3g}")
            if first_nonzero > limits["first_nonzero_max"]:
                failures.append(
                    f"{figure_id}:{model_id}: first nonzero model point {first_nonzero:.3g} does not show the expected initial activity-coefficient depression"
                )
    return failures


def _run(args: list[str]) -> None:
    print("+ " + " ".join(args))
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate 2025 Figiel CSV-backed plot payloads.")
    parser.add_argument(
        "--skip-backend", action="store_true", help="Skip native build, doctor, and runtime smoke tests."
    )
    parser.add_argument("--skip-plots", action="store_true", help="Skip PNG regeneration.")
    parser.add_argument("--rtol", type=float, default=1e-9)
    parser.add_argument("--atol", type=float, default=1e-10)
    args = parser.parse_args()

    if not args.skip_backend:
        _run([sys.executable, "scripts/dev/build_epcsaft.py"])
        _run([sys.executable, "scripts/dev/doctor.py"])
        _run([sys.executable, "run_pytest.py", "--runtime", "-q"])

    figure_data = _load_figure_data()
    failures = figure_data.compare_all(rtol=args.rtol, atol=args.atol)
    failures.extend(_validate_visual_qc_report())
    failures.extend(_validate_model_fit_quality(figure_data))
    if failures:
        print("2025 Figiel figure-data validation failed:")
        for failure in failures[:40]:
            print(f"  - {failure}")
        if len(failures) > 40:
            print(f"  - ... {len(failures) - 40} more")
        raise SystemExit(1)

    if not args.skip_plots:
        for script in PLOT_SCRIPTS:
            _run([sys.executable, str(script.relative_to(REPO_ROOT))])

    print("2025 Figiel CSV-backed figure data validated.")


if __name__ == "__main__":
    main()
