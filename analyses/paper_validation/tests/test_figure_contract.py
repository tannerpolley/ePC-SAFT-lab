from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "analyses" / "paper_validation" / "scripts" / "check_figure_contract.py"
spec = importlib.util.spec_from_file_location("paper_validation_figure_contract", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_gross_2002_figure_01_matches_paper_validation_contract() -> None:
    figure_root = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / "figure_01"

    assert checker.check_figure_root(figure_root) == []


def test_reference_data_is_not_paper_validation_scoped() -> None:
    assert not (REPO_ROOT / "data" / "reference" / "paper_validation").exists()


def test_contract_rejects_bar_plot_scripts(tmp_path: Path) -> None:
    figure_root = tmp_path / "analyses" / "paper_validation" / "demo_paper" / "figures" / "figure_01"
    for folder in ("source", "scripts", "results"):
        (figure_root / folder).mkdir(parents=True, exist_ok=True)
    for name in ("figure_01.png", "source_points.csv", "source_notes.csv"):
        (figure_root / "source" / name).write_text("x\n", encoding="utf-8")
    (figure_root / "scripts" / "generate_data.py").write_text("print('generate')\n", encoding="utf-8")
    (figure_root / "scripts" / "render_figure.py").write_text("ax.bar([1], [2])\n", encoding="utf-8")
    for name in ("model_curve.csv", "plotted_data.csv", "fit_statistics.csv", "figure_01.svg", "figure_01.png", "figure_01.pdf"):
        (figure_root / "results" / name).write_text("x\n", encoding="utf-8")

    blockers = checker.check_figure_root(figure_root)

    assert any("bar_plot_not_allowed_for_replication_evidence" in blocker for blocker in blockers)


def test_contract_rejects_extra_image_stems(tmp_path: Path) -> None:
    figure_root = tmp_path / "analyses" / "paper_validation" / "demo_paper" / "figures" / "figure_01"
    for folder in ("source", "scripts", "results"):
        (figure_root / folder).mkdir(parents=True, exist_ok=True)
    for name in ("figure_01.png", "source_points.csv", "source_notes.csv"):
        (figure_root / "source" / name).write_text("x\n", encoding="utf-8")
    (figure_root / "source" / "paper.png").write_text("x\n", encoding="utf-8")
    (figure_root / "scripts" / "generate_data.py").write_text("print('generate')\n", encoding="utf-8")
    (figure_root / "scripts" / "render_figure.py").write_text("print('render')\n", encoding="utf-8")
    for name in ("model_curve.csv", "plotted_data.csv", "fit_statistics.csv", "figure_01.svg", "figure_01.png", "figure_01.pdf"):
        (figure_root / "results" / name).write_text("x\n", encoding="utf-8")

    blockers = checker.check_figure_root(figure_root)

    assert any("image_file_must_use_figure_id_stem" in blocker for blocker in blockers)
