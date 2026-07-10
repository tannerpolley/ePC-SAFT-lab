from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_08"
    / "scripts"
    / "generate_data.py"
)
spec = importlib.util.spec_from_file_location("gross_2002_figure08_generator", GENERATOR_PATH)
assert spec is not None and spec.loader is not None
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def _source_row(series: str, coordinate: float) -> dict[str, object]:
    return {
        "series": series,
        "x_methanol": coordinate if series != "vle_dew_right" else "",
        "y_methanol": coordinate if series == "vle_dew_right" else "",
        "T_C": 40.0,
        "uncertainty_x": 0.015,
    }


def _model_row(series: str, coordinate: float) -> dict[str, object]:
    return {
        "series": series,
        "x_methanol": coordinate if series != "vle_dew_right" else "",
        "y_methanol": coordinate if series == "vle_dew_right" else "",
        "T_C": 40.0,
    }


def test_figure08_score_rejects_clamped_out_of_range_branch_endpoint() -> None:
    source_rows = [
        _source_row("vle_bubble_left", 0.2),
        _source_row("vle_dew_right", 0.8),
        _source_row("lle_methanol_lean", 0.45),
        _source_row("lle_methanol_rich", 0.55),
    ]
    model_rows = [
        _model_row("vle_bubble_left", 0.2),
        _model_row("vle_dew_right", 0.8),
        _model_row("lle_methanol_lean", 0.30),
        _model_row("lle_methanol_rich", 0.55),
    ]

    score = generator._score(source_rows, model_rows, {})

    lean_score = score["series_scores"]["lle_methanol_lean"]
    assert lean_score["branch_coverage_score"] == 0.0
    assert lean_score["pass"] is False
    assert score["branch_coverage_score"] == 0.0
    assert score["pass"] is False
