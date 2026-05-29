from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2025_figiel"


EXPECTED_FIGURE_IDS = tuple(f"figure_{index:02d}" for index in range(1, 10))
EXPECTED_GENERATOR_KEYS = tuple(f"figure_{index}" for index in range(1, 10))


def _generator_keys() -> tuple[str, ...]:
    path = ANALYSIS_ROOT / "shared" / "figure_data.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "GENERATORS" for target in node.targets):
            continue
        assert isinstance(node.value, ast.Dict)
        keys = []
        for key_node in node.value.keys:
            key = ast.literal_eval(key_node)
            assert isinstance(key, str)
            keys.append(key)
        return tuple(keys)
    raise AssertionError("GENERATORS registry not found in figure_data.py")


def _rendered_figure_paths(figure_root: Path) -> list[Path]:
    return sorted(path for path in (figure_root / "results").glob("*.png") if path.is_file())


def test_figiel_generators_cover_all_nine_figures() -> None:
    assert _generator_keys() == EXPECTED_GENERATOR_KEYS


def test_figiel_figure_folders_have_full_workflow_files() -> None:
    for figure_id in EXPECTED_FIGURE_IDS:
        figure_root = ANALYSIS_ROOT / "figures" / figure_id
        figure_number = int(figure_id.rsplit("_", 1)[1])
        assert (figure_root / "source").is_dir()
        assert (figure_root / "scripts" / "generate_data.py").is_file()
        assert (figure_root / "scripts" / f"plot_figure_{figure_number}.py").is_file()
        assert (figure_root / "results" / f"figure_{figure_number}_series.csv").is_file()


def test_figiel_analysis_contains_no_placeholder_files() -> None:
    placeholders = sorted(path.relative_to(REPO_ROOT).as_posix() for path in ANALYSIS_ROOT.rglob("_placeholder.md"))
    assert placeholders == []


def test_figiel_results_keep_one_canonical_png_per_figure() -> None:
    expected = {f"figure_{int(figure_id.rsplit('_', 1)[1])}.png" for figure_id in EXPECTED_FIGURE_IDS}
    seen: set[str] = set()

    for figure_id in EXPECTED_FIGURE_IDS:
        figure_root = ANALYSIS_ROOT / "figures" / figure_id
        rendered = _rendered_figure_paths(figure_root)
        assert len(rendered) == 1
        seen.add(rendered[0].name)
        assert not list((figure_root / "results").glob("*.svg"))

    assert seen == expected


def test_figiel_results_sidecars_reference_png_outputs() -> None:
    for figure_id in EXPECTED_FIGURE_IDS:
        figure_root = ANALYSIS_ROOT / "figures" / figure_id
        figure_number = int(figure_id.rsplit("_", 1)[1])
        style_path = figure_root / "results" / f"figure_{figure_number}.mpl.yaml"
        data_path = figure_root / "results" / f"figure_{figure_number}.csv"
        style_text = style_path.read_text(encoding="utf-8")
        data_text = data_path.read_text(encoding="utf-8")
        assert f'file: "figure_{figure_number}.png"' in style_text
        assert 'format: "png"' in style_text
        assert f"figure_{figure_number}.svg" not in style_text
        assert f"figure_{figure_number}.svg" not in data_text


def test_figiel_visual_qc_report_tracks_all_figures() -> None:
    report = ANALYSIS_ROOT / "docs" / "visual_qc.md"
    assert report.is_file()
    text = report.read_text(encoding="utf-8")
    for figure_id in EXPECTED_FIGURE_IDS:
        figure_number = int(figure_id.rsplit("_", 1)[1])
        assert f"Figure {figure_number}" in text
        assert f"source/paper_source_01_figiel_2025_figure_{figure_number + 1:03d}.png" in text
