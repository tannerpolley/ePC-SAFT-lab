from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_VALIDATION_ROOT = REPO_ROOT / "analyses" / "paper_validation"
FORBIDDEN_REFERENCE_ROOT = REPO_ROOT / "data" / "reference" / "paper_validation"
FIGURE_ID_RE = re.compile(r"^figure_\d{2}$")
ALLOWED_TOP_LEVEL = {"source", "scripts", "results"}
REQUIRED_SOURCE_FILES = {"source_points.csv", "source_notes.csv"}
REQUIRED_SCRIPT_FILES = {"generate_data.py", "render_figure.py"}
REQUIRED_RESULT_FILES = {"model_curve.csv", "plotted_data.csv", "fit_statistics.csv"}
FORBIDDEN_SUFFIXES = {".json", ".mpl.yaml"}
IMAGE_SUFFIXES = {".svg", ".png", ".pdf"}
FORBIDDEN_NAME_FRAGMENTS = ("digitization", "digitized")
BAR_PLOT_PATTERNS = (".bar(", "ax.bar(", "plt.bar(")


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _paper_id_for_figure(figure_root: Path) -> str:
    try:
        return figure_root.resolve().parents[1].name
    except IndexError:
        return ""


def _check_required_files(root: Path, folder: str, required: set[str]) -> list[str]:
    base = root / folder
    blockers: list[str] = []
    for name in sorted(required):
        if not (base / name).is_file():
            blockers.append(f"{_relative(root)}:{folder}/{name}:missing")
    return blockers


def _contains_bar_plot(script: Path) -> bool:
    try:
        text = script.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return any(pattern in text for pattern in BAR_PLOT_PATTERNS)


def check_figure_root(figure_root: Path) -> list[str]:
    root = figure_root.resolve()
    blockers: list[str] = []
    if FORBIDDEN_REFERENCE_ROOT.exists():
        blockers.append(f"{_relative(FORBIDDEN_REFERENCE_ROOT)}:paper_scoped_reference_data_not_allowed")
    if not root.is_dir():
        return [f"{_relative(root)}:figure_root_missing"]
    if not FIGURE_ID_RE.match(root.name):
        blockers.append(f"{_relative(root)}:figure_folder_name_must_be_figure_NN")

    direct_children = {path.name for path in root.iterdir()}
    for required in sorted(ALLOWED_TOP_LEVEL):
        if required not in direct_children:
            blockers.append(f"{_relative(root)}:{required}:missing_folder")
    for name in sorted(direct_children - ALLOWED_TOP_LEVEL):
        blockers.append(f"{_relative(root)}:{name}:unexpected_top_level_entry")

    blockers.extend(_check_required_files(root, "source", REQUIRED_SOURCE_FILES))
    source_image = root / "source" / f"{root.name}.png"
    if not source_image.is_file():
        blockers.append(f"{_relative(root)}:source/{root.name}.png:missing")
    blockers.extend(_check_required_files(root, "scripts", REQUIRED_SCRIPT_FILES))
    blockers.extend(_check_required_files(root, "results", REQUIRED_RESULT_FILES))
    for suffix in IMAGE_SUFFIXES:
        expected = root / "results" / f"{root.name}{suffix}"
        if not expected.is_file():
            blockers.append(f"{_relative(root)}:results/{root.name}{suffix}:missing")

    paper_id = _paper_id_for_figure(root)
    for path in root.rglob("*"):
        if "__pycache__" in path.parts:
            blockers.append(f"{_relative(path)}:pycache_not_allowed")
            continue
        if path.is_dir():
            continue
        name = path.name
        lower_name = name.lower()
        if any(fragment in lower_name for fragment in FORBIDDEN_NAME_FRAGMENTS):
            blockers.append(f"{_relative(path)}:tool_named_file_not_allowed")
        if any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            blockers.append(f"{_relative(path)}:forbidden_file_type")
        if paper_id and paper_id in name:
            blockers.append(f"{_relative(path)}:paper_id_prefix_not_allowed")
        if path.suffix.lower() in IMAGE_SUFFIXES and path.stem != root.name:
            blockers.append(f"{_relative(path)}:image_file_must_use_figure_id_stem")
        if path.suffix == ".py" and _contains_bar_plot(path):
            blockers.append(f"{_relative(path)}:bar_plot_not_allowed_for_replication_evidence")

    return sorted(set(blockers))


def _all_figure_roots() -> list[Path]:
    return sorted(PAPER_VALIDATION_ROOT.glob("*/figures/figure_*"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check paper-validation figure folder contracts.")
    parser.add_argument("figure_roots", nargs="*", type=Path)
    parser.add_argument("--all", action="store_true", help="check every analyses/paper_validation/**/figures/figure_* folder")
    args = parser.parse_args(argv)

    roots = _all_figure_roots() if args.all else [Path(path) for path in args.figure_roots]
    if not roots:
        parser.error("provide one or more figure roots, or pass --all")

    blockers: list[str] = []
    for root in roots:
        blockers.extend(check_figure_root(REPO_ROOT / root if not root.is_absolute() else root))

    if blockers:
        for blocker in blockers:
            print(blocker)
        return 2
    print("paper_validation_figure_contract_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
