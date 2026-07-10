from __future__ import annotations

import importlib
from pathlib import Path

import pytest

figure03 = importlib.import_module(
    "analyses.paper_validation.2002_gross.figures.figure_03.scripts.generate_data"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
RETAINED_PLOT = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_03"
    / "results"
    / "figure_03.png"
)


def test_figure03_endpoint_inversion_uses_public_finite_binary_dew_limit() -> None:
    source_row = next(
        row
        for row in figure03._load_source_rows()
        if row["series"] == "pressure_series_high"
        and row["source_role"] == "bubble_curve"
        and float(row["x_1_propanol"]) == 0.0
    )

    model_row = figure03._solve_temperature_for_row(figure03._mixture(), source_row)

    assert model_row["route"] == "dew_pressure"
    assert model_row["endpoint_limit_basis"] == "finite_binary_dew_pressure_limit"
    assert model_row["requested_coordinate"] == pytest.approx(figure03.MIN_COMPOSITION)
    assert model_row["requested_coordinate_role"] == "y_1_propanol"
    assert model_row["y_1_propanol"] == pytest.approx(figure03.MIN_COMPOSITION)
    assert 0.0 < model_row["x_1_propanol"] < figure03.MIN_COMPOSITION
    assert model_row["solved_pressure_bar"] == pytest.approx(float(source_row["P_bar"]), abs=2.5e-3)
    assert model_row["hessian_approximation"] == "exact"
    assert model_row["exact_hessian_available"] is True
    assert model_row["postsolve_accepted"] is True
    assert RETAINED_PLOT.is_file()
