from __future__ import annotations

import importlib
from pathlib import Path

import pytest

figure04 = importlib.import_module(
    "analyses.paper_validation.2002_gross.figures.figure_04.scripts.generate_data"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
RETAINED_PLOT = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_04"
    / "results"
    / "figure_04.png"
)


def test_figure04_bubble_endpoint_uses_public_finite_binary_dew_limit() -> None:
    source_row = next(
        row
        for row in figure04._source_curve_rows(figure04._load_source_rows())
        if row["series"] == "bubble_line" and float(row["x_1_pentanol"]) == 1.0
    )

    model_row = figure04._solve_series(figure04._mixture(), [source_row], "bubble_line")[0]

    assert model_row["route"] == "dew_pressure"
    assert model_row["endpoint_limit_basis"] == "finite_binary_dew_pressure_limit"
    assert model_row["requested_coordinate"] == pytest.approx(1.0 - figure04.MIN_COMPOSITION)
    assert model_row["requested_coordinate_role"] == "y_1_pentanol"
    assert model_row["y_1_pentanol"] == pytest.approx(1.0 - figure04.MIN_COMPOSITION, rel=2.0e-7)
    assert model_row["P_bar"] == pytest.approx(0.00976661993, rel=2.0e-8)
    assert model_row["hessian_approximation"] == "exact"
    assert model_row["exact_hessian_available"] is True
    assert model_row["postsolve_accepted"] is True
    assert RETAINED_PLOT.is_file()
