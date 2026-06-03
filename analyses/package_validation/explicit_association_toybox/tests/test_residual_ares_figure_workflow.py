from __future__ import annotations

from pathlib import Path

from analyses.package_validation.explicit_association_toybox.figures.residual_ares_error.scripts import (
    generate_data,
    render_figure,
)


def test_residual_ares_figure_workflow_writes_retained_outputs(tmp_path: Path, monkeypatch) -> None:
    metrics = tmp_path / "residual_ares_metrics.csv"
    plotted = tmp_path / "residual_ares_error_summary_plotted_data.csv"
    figure = tmp_path / "residual_ares_error_summary.png"
    sidecar = tmp_path / "residual_ares_error_summary.mpl.yaml"

    monkeypatch.setattr(generate_data, "OUTPUT", metrics)
    monkeypatch.setattr(render_figure, "OUTPUT", tmp_path)
    monkeypatch.setattr(render_figure, "METRICS", metrics)
    monkeypatch.setattr(render_figure, "PLOTTED", plotted)
    monkeypatch.setattr(render_figure, "FIGURE", figure)
    monkeypatch.setattr(render_figure, "SIDECAR", sidecar)

    generate_data.main()
    render_figure.main()

    assert metrics.is_file()
    assert plotted.is_file()
    assert figure.is_file()
    assert sidecar.is_file()
    assert "ares_total_rel_error" in metrics.read_text(encoding="utf-8")
    assert "max_ares_total_rel_error" in plotted.read_text(encoding="utf-8")
