from __future__ import annotations

import importlib
from pathlib import Path

import pytest

figure05 = importlib.import_module(
    "analyses.paper_validation.2002_gross.figures.figure_05.scripts.generate_data"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
RETAINED_PLOT = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_05"
    / "results"
    / "figure_05.png"
)


def test_figure05_alcohol_endpoint_uses_public_finite_binary_dew_limit() -> None:
    source_row = next(
        row
        for row in figure05._load_source_rows()
        if row["series"] == "1-propanol-benzene"
        and row["source_role"] == "bubble_curve"
        and float(row["x_alcohol"]) == 1.0
    )

    model_row = figure05._solve_series([source_row], "1-propanol-benzene")[0]

    assert model_row["route"] == "dew_pressure"
    assert model_row["endpoint_limit_basis"] == "finite_binary_dew_pressure_limit"
    assert model_row["requested_coordinate"] == pytest.approx(1.0 - figure05.MIN_COMPOSITION)
    assert model_row["requested_coordinate_role"] == "y_alcohol"
    assert model_row["y_alcohol"] == pytest.approx(1.0 - figure05.MIN_COMPOSITION)
    assert model_row["P_bar"] == pytest.approx(0.06970781029, rel=2.0e-8)
    assert model_row["hessian_approximation"] == "exact"
    assert model_row["exact_hessian_available"] is True
    assert model_row["postsolve_accepted"] is True
    assert RETAINED_PLOT.is_file()
