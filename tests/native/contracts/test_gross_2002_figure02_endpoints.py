from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from epcsaft_equilibrium import Equilibrium

figure02 = importlib.import_module(
    "analyses.paper_validation.2002_gross.figures.figure_02.scripts.generate_data"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
RETAINED_PLOT = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_02"
    / "results"
    / "figure_02.png"
)


def test_figure02_methanol_endpoint_uses_public_finite_binary_dew_limit() -> None:
    source_row = next(
        row
        for row in figure02._source_curve_rows(figure02._load_source_rows())
        if row["series"] == "bubble_line" and float(row["x_component_1"]) == 0.0
    )

    model_rows = figure02._boundary_limit_rows(figure02._mixture(), [source_row])

    assert len(model_rows) == 1
    model_row = model_rows[0]
    assert model_row["route"] == "dew_pressure"
    assert model_row["endpoint_limit_basis"] == "finite_binary_dew_pressure_limit"
    assert model_row["requested_coordinate"] == pytest.approx(figure02.MIN_COMPOSITION)
    assert model_row["requested_coordinate_role"] == "y_component_1"
    assert model_row["y_component_1"] == pytest.approx(figure02.MIN_COMPOSITION)
    assert model_row["x_component_1"] == pytest.approx(2.4543734e-8, rel=2.0e-7)
    assert model_row["P_bar"] == pytest.approx(3.4698556768, rel=2.0e-8)
    assert model_row["hessian_approximation"] == "exact"
    assert model_row["exact_hessian_available"] is True
    assert model_row["postsolve_accepted"] is True
    assert model_row["source_anchor_id"] == "binary_limit:methanol"
    assert RETAINED_PLOT.is_file()


def test_figure02_public_pressure_continuation_retargets_changed_composition() -> None:
    source_row = next(
        row
        for row in figure02._source_curve_rows(figure02._load_source_rows())
        if row["series"] == "bubble_line" and float(row["x_component_1"]) == pytest.approx(0.99125)
    )
    mixture = figure02._mixture()
    solver_options = dict(figure02.EQUILIBRIUM_SOLVER_OPTIONS)

    first = Equilibrium(
        mixture,
        route="bubble_pressure",
        T=figure02.TEMPERATURE_K,
        x=[0.01, 0.99],
    ).solve(solver_options=solver_options)
    solver_options["continuation_state"] = first.diagnostics["continuation_state"]
    second = Equilibrium(
        mixture,
        route="bubble_pressure",
        T=figure02.TEMPERATURE_K,
        x=[0.0095, 0.9905],
    ).solve(solver_options=solver_options)
    solver_options["continuation_state"] = second.diagnostics["continuation_state"]
    endpoint = Equilibrium(
        mixture,
        route="bubble_pressure",
        T=figure02.TEMPERATURE_K,
        x=[0.00875, 0.99125],
    ).solve(solver_options=solver_options)

    assert second.diagnostics["postsolve_accepted"] is True
    assert endpoint.diagnostics["postsolve_accepted"] is True
    assert endpoint.diagnostics["hessian_approximation"] == "exact"
    assert endpoint.pressure / 1.0e5 == pytest.approx(float(source_row["P_bar"]), abs=2.0e-3)
    assert endpoint.y[1] == pytest.approx(0.9740281218, rel=2.0e-8)
    assert RETAINED_PLOT.is_file()


def test_figure02_production_score_uses_retained_literature_points() -> None:
    source_rows = figure02._load_source_rows()
    literature_rows = figure02._load_literature_rows()
    model_rows = figure02._read_csv(figure02.MODEL_CSV)

    score = figure02._score(source_rows, model_rows, scoring_rows=literature_rows)

    assert score["source_point_count"] == len(literature_rows) == 14
    assert score["source_point_count"] != len(figure02._source_curve_rows(source_rows))
    assert score["series_scores"]["bubble_line"]["source_point_count"] == 7
    assert score["series_scores"]["dew_line"]["source_point_count"] == 7
    assert score["score_basis"] == (
        "pressure-coordinate RMSE against Leu and Robinson 1992 Table I "
        "literature P-x/y points retained for Gross 2002 Figure 2"
    )


def test_figure02_plotted_data_retains_the_literature_points_used_for_scoring() -> None:
    plotted_rows = figure02._read_csv(figure02.PLOTTED_CSV)
    literature_rows = [row for row in plotted_rows if row["dataset"] == "literature_experimental"]

    assert len(literature_rows) == 14
    assert len([row for row in plotted_rows if row["dataset"] == "package_model"]) == 45
    assert {row["source_reference"] for row in literature_rows} == {"Leu and Robinson 1992 Table I"}
