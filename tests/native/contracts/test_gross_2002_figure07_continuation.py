from __future__ import annotations

import importlib
from pathlib import Path

import pytest

figure07 = importlib.import_module(
    "analyses.paper_validation.2002_gross.figures.figure_07.scripts.generate_data"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
RETAINED_PLOT = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_07"
    / "results"
    / "figure_07.png"
)


def test_figure07_source_anchor_gap_uses_adaptive_primal_continuation() -> None:
    source_rows = [
        row
        for row in figure07._load_source_rows()
        if row["series"] == "T_100C" and float(row["x_butane"]) <= 0.7478134110787172
    ]

    model_rows = figure07._solve_series(source_rows, "T_100C")

    assert len(model_rows) == 9
    endpoint = max(model_rows, key=lambda row: float(row["x_butane"]))
    assert endpoint["x_butane"] == pytest.approx(0.7478134110787172)
    assert 14.0 < endpoint["P_bar"] < 16.0
    assert endpoint["continuation_bridge_count"] >= 1
    assert endpoint["maximum_continuation_gap"] <= figure07.MAX_CONTINUATION_GAP
    assert endpoint["hessian_approximation"] == "exact"
    assert endpoint["exact_hessian_available"] is True
    assert endpoint["postsolve_accepted"] is True
    assert RETAINED_PLOT.is_file()


def test_figure07_supercritical_series_retargets_fixed_composition() -> None:
    source_rows = [
        row
        for row in figure07._load_source_rows()
        if row["series"] == "T_190C"
    ]

    model_rows = figure07._solve_series(source_rows, "T_190C")

    assert len(model_rows) == 4
    endpoint = max(model_rows, key=lambda row: float(row["x_butane"]))
    assert endpoint["x_butane"] == pytest.approx(0.33527696793002915)
    assert 52.0 < endpoint["P_bar"] < 54.0
    assert any(row["continuation_bridge_count"] >= 1 for row in model_rows)
    assert all(
        row["maximum_continuation_gap"] <= figure07.MAX_CONTINUATION_GAP
        for row in model_rows
    )
    assert endpoint["hessian_approximation"] == "exact"
    assert endpoint["exact_hessian_available"] is True
    assert endpoint["postsolve_accepted"] is True
    assert RETAINED_PLOT.is_file()


def test_figure07_subcritical_branch_preserves_previous_primal_predictor() -> None:
    source_rows = [
        row
        for row in figure07._load_source_rows()
        if row["series"] == "T_140C" and float(row["x_butane"]) <= 0.2463556852
    ]

    model_rows = figure07._solve_series(source_rows, "T_140C")

    assert len(model_rows) == 3
    endpoint = max(model_rows, key=lambda row: float(row["x_butane"]))
    assert endpoint["x_butane"] == pytest.approx(0.24635568513119535)
    assert 22.0 < endpoint["P_bar"] < 25.0
    assert endpoint["y_butane"] > endpoint["x_butane"]
    assert endpoint["hessian_approximation"] == "exact"
    assert endpoint["exact_hessian_available"] is True
    assert endpoint["postsolve_accepted"] is True
    assert RETAINED_PLOT.is_file()
