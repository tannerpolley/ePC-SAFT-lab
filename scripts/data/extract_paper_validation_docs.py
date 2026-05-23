"""Populate paper-validation source docs and strict figure artifacts.

The script copies matched paper Markdown/PDF sources into each validation
folder, extracts Markdown image references as PNG source artifacts under the
owning figure folders, and extracts Markdown table blocks into shared source
tables as exact snippets plus best-effort CSVs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_VALIDATION_ROOT = REPO_ROOT / "analyses" / "paper_validation"
PAPERS_MD_ROOT = REPO_ROOT / "docs" / "papers" / "md"
PAPERS_PDF_ROOT = REPO_ROOT / "docs" / "papers" / "pdf"
DOC_SUBDIRS = ("md", "pdf")
FIGURE_SUBDIRS = ("source", "scripts", "results")
TEXT_EXTENSIONS = {".csv", ".json", ".md", ".py", ".rst", ".toml", ".txt", ".yaml", ".yml", ".ps1"}
PLACEHOLDER_NAME = "_placeholder.md"
ROOT_MARKDOWN_ALLOWLIST = {"README.md"}
ROOT_DIRS = {"docs", "figures", "parameters", "scripts", "shared", "tables"}


@dataclass(frozen=True)
class PaperSource:
    key: str
    md_tokens: tuple[str, ...]
    pdf_tokens: tuple[str, ...] | None = None
    md_exclude_tokens: tuple[str, ...] = ()
    pdf_exclude_tokens: tuple[str, ...] = ()


SOURCE_MAP: dict[str, tuple[PaperSource, ...]] = {
    "2015_baygi": (
        PaperSource("baygi_2015", ("baygi", "2015")),
    ),
    "2001_gross": (
        PaperSource("gross_2001", ("gross", "sadowski", "2001")),
    ),
    "2002_gross": (
        PaperSource("gross_2002", ("gross", "sadowski", "2002")),
    ),
    "2005_cameretti": (
        PaperSource("cameretti_2005", ("cameretti", "2005")),
    ),
    "2008_held": (
        PaperSource("held_2008", ("held", "cameretti", "2008")),
    ),
    "2012_held": (
        PaperSource("held_2012", ("held", "prinz", "2012")),
    ),
    "2014_held": (
        PaperSource("held_2014", ("held", "2014")),
    ),
    "2019_bulow": (
        PaperSource("bulow_2019", ("bulow", "2019")),
    ),
    "2020_bulow": (
        PaperSource("bulow_2020", ("bulow", "2020")),
    ),
    "2021_bulow": (
        PaperSource("bulow_2021", ("bulow", "2021")),
    ),
    "2025_figiel": (
        PaperSource("figiel_2025", ("figiel", "2025")),
    ),
    "2022_ascani": (
        PaperSource(
            "ascani_2022_main",
            ("ascani", "2022", "calculation", "multiphase"),
            md_exclude_tokens=("supporting",),
            pdf_exclude_tokens=("supporting",),
        ),
        PaperSource(
            "ascani_2022_supporting",
            ("ascani", "2022", "supporting", "information", "multiphase"),
            ("supporting", "information", "calculation", "multiphase"),
        ),
    ),
    "2023_ascani": (
        PaperSource("ascani_2023", ("ascani", "2023")),
    ),
    "2026_khudaida": (
        PaperSource(
            "khudaida_2026_main",
            ("khudaida", "2026", "upgrading"),
            md_exclude_tokens=("supporting",),
            pdf_exclude_tokens=("supporting",),
        ),
        PaperSource("khudaida_2026_supporting", ("khudaida", "2026", "supporting")),
    ),
    "2024_hubach": (
        PaperSource(
            "hubach_2024_main",
            ("hubach", "2024", "li", "extraction"),
            md_exclude_tokens=("supporting",),
            pdf_exclude_tokens=("supporting",),
        ),
        PaperSource("hubach_2024_supporting", ("hubach", "2024", "supporting")),
    ),
    "2024_yu": (
        PaperSource(
            "yu_2024_main",
            ("yu", "2024", "highly", "efficient"),
            md_exclude_tokens=("supplemental", "supplementary", "supporting"),
            pdf_exclude_tokens=("supplemental", "supplementary", "supporting"),
        ),
        PaperSource("yu_2024_supplemental", ("yu", "2024", "supplemental")),
    ),
    "2026_rezaee": (
        PaperSource(
            "rezaee_2025_main",
            ("rezaee", "2025", "response", "surface"),
            md_exclude_tokens=("supporting",),
            pdf_exclude_tokens=("supporting",),
        ),
        PaperSource("rezaee_2025_supporting", ("rezaee", "2025", "supporting")),
        PaperSource(
            "rezaee_2026_main",
            ("rezaee", "2026", "thermodynamic", "modeling"),
            md_exclude_tokens=("supplementary", "supplemental", "supporting"),
            pdf_exclude_tokens=("supplementary", "supplemental", "supporting"),
        ),
        PaperSource("rezaee_2026_supplementary", ("rezaee", "2026", "supplementary")),
    ),
}

_OLD_PAPER_VALIDATION_ROOT = "analyses/paper_validation"
_OLD_APPLICATION_ROOT = f"{_OLD_PAPER_VALIDATION_ROOT}/application"
_OLD_NATIVE_ROOT = f"{_OLD_PAPER_VALIDATION_ROOT}/native"

PATH_REWRITES = {
    f"{_OLD_APPLICATION_ROOT}/2015_baygi": "analyses/paper_validation/2015_baygi",
    f"{_OLD_APPLICATION_ROOT}/2024_hubach_li_tcb": "analyses/paper_validation/2024_hubach",
    f"{_OLD_APPLICATION_ROOT}/2024_yu_li_mg_il": "analyses/paper_validation/2024_yu",
    f"{_OLD_APPLICATION_ROOT}/2026_khudaida": "analyses/paper_validation/2026_khudaida",
    f"{_OLD_APPLICATION_ROOT}/2026_rezaee": "analyses/paper_validation/2026_rezaee",
    f"{_OLD_NATIVE_ROOT}/2001_gross": "analyses/paper_validation/2001_gross",
    f"{_OLD_NATIVE_ROOT}/2002_gross": "analyses/paper_validation/2002_gross",
    f"{_OLD_NATIVE_ROOT}/2005_cameretti": "analyses/paper_validation/2005_cameretti",
    f"{_OLD_NATIVE_ROOT}/2008_held": "analyses/paper_validation/2008_held",
    f"{_OLD_NATIVE_ROOT}/2012_held": "analyses/paper_validation/2012_held",
    f"{_OLD_NATIVE_ROOT}/2014_held": "analyses/paper_validation/2014_held",
    f"{_OLD_NATIVE_ROOT}/2019_bulow": "analyses/paper_validation/2019_bulow",
    f"{_OLD_NATIVE_ROOT}/2020_bulow": "analyses/paper_validation/2020_bulow",
    f"{_OLD_NATIVE_ROOT}/2021_bulow": "analyses/paper_validation/2021_bulow",
    f"{_OLD_NATIVE_ROOT}/2022_ascani": "analyses/paper_validation/2022_ascani",
    f"{_OLD_NATIVE_ROOT}/2023_ascani": "analyses/paper_validation/2023_ascani",
    f"{_OLD_NATIVE_ROOT}/2025_figiel": "analyses/paper_validation/2025_figiel",
    "analyses/paper_validation/co2_solubility/2015_baygi": "analyses/paper_validation/2015_baygi",
    "analyses/paper_validation/eos/2001_gross": "analyses/paper_validation/2001_gross",
    "analyses/paper_validation/eos/2002_gross": "analyses/paper_validation/2002_gross",
    "analyses/paper_validation/eos/2005_cameretti": "analyses/paper_validation/2005_cameretti",
    "analyses/paper_validation/eos/2008_held": "analyses/paper_validation/2008_held",
    "analyses/paper_validation/eos/2012_held": "analyses/paper_validation/2012_held",
    "analyses/paper_validation/eos/2014_held": "analyses/paper_validation/2014_held",
    "analyses/paper_validation/eos/2019_bulow": "analyses/paper_validation/2019_bulow",
    "analyses/paper_validation/eos/2020_bulow": "analyses/paper_validation/2020_bulow",
    "analyses/paper_validation/eos/2021_bulow": "analyses/paper_validation/2021_bulow",
    "analyses/paper_validation/eos/2025_figiel": "analyses/paper_validation/2025_figiel",
    "analyses/paper_validation/equilibrium/2022_ascani": "analyses/paper_validation/2022_ascani",
    "analyses/paper_validation/equilibrium/2023_ascani": "analyses/paper_validation/2023_ascani",
    "analyses/paper_validation/equilibrium/2026_khudaida": "analyses/paper_validation/2026_khudaida",
    "analyses/paper_validation/extraction/2024_hubach": "analyses/paper_validation/2024_hubach",
    "analyses/paper_validation/extraction/2024_yu": "analyses/paper_validation/2024_yu",
    "analyses/paper_validation/extraction/2026_rezaee": "analyses/paper_validation/2026_rezaee",
}


def _normalize(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _analysis_dirs() -> list[Path]:
    return sorted(path for path in PAPER_VALIDATION_ROOT.iterdir() if path.is_dir())


def _match_one(root: Path, tokens: Sequence[str], exclude_tokens: Sequence[str], label: str) -> Path | None:
    normalized_tokens = tuple(_normalize(token) for token in tokens)
    normalized_excludes = tuple(_normalize(token) for token in exclude_tokens)
    candidates = [
        path
        for path in sorted(root.glob("*"))
        if path.is_file()
        and all(token in _normalize(path.name) for token in normalized_tokens)
        and not any(token in _normalize(path.name) for token in normalized_excludes)
    ]
    if len(candidates) > 1:
        rels = ", ".join(_rel(path) for path in candidates)
        raise RuntimeError(f"Ambiguous {label} match for tokens {tokens!r}: {rels}")
    return candidates[0] if candidates else None


def _source_matches(source: PaperSource) -> tuple[Path, Path | None]:
    md = _match_one(PAPERS_MD_ROOT, source.md_tokens, source.md_exclude_tokens, f"{source.key} markdown")
    if md is None:
        raise RuntimeError(f"No Markdown source matched {source.key}: {source.md_tokens!r}")
    pdf_tokens = source.pdf_tokens if source.pdf_tokens is not None else source.md_tokens
    pdf = _match_one(PAPERS_PDF_ROOT, pdf_tokens, source.pdf_exclude_tokens, f"{source.key} PDF")
    return md, pdf


def _write_csv(path: Path, rows: Iterable[dict[str, str]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_placeholder(directory: Path, message: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / PLACEHOLDER_NAME).write_text(message.rstrip() + "\n", encoding="utf-8")


def _remove_placeholder_if_content_exists(directory: Path) -> None:
    marker = directory / PLACEHOLDER_NAME
    if not marker.exists():
        return
    content = [path for path in directory.iterdir() if path.name != PLACEHOLDER_NAME]
    if content:
        marker.unlink()


def _ensure_required_folder(directory: Path, message: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    content = [path for path in directory.iterdir() if path.name != PLACEHOLDER_NAME]
    if content:
        _remove_placeholder_if_content_exists(directory)
    else:
        _write_placeholder(directory, message)


def _remove_if_empty(path: Path, stop_at: Path) -> None:
    current = path
    while current != stop_at and current.exists() and current.is_dir():
        try:
            current.rmdir()
        except OSError:
            return
        current = current.parent


def _merge_tree(source: Path, target: Path) -> None:
    if not source.exists():
        return
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.is_file() and target.read_bytes() == source.read_bytes():
                source.unlink()
                return
            raise RuntimeError(f"Refusing to overwrite different file while moving {_rel(source)} to {_rel(target)}")
        shutil.move(str(source), str(target))
        return

    target.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        _merge_tree(child, target / child.name)
    _remove_if_empty(source, source.parent)


def _prepare_docs_root(analysis_root: Path) -> None:
    docs_root = analysis_root / "docs"
    docs_root.mkdir(parents=True, exist_ok=True)
    for removed in ("figures", "tables"):
        path = docs_root / removed
        if path.exists():
            shutil.rmtree(path)
    for subdir in DOC_SUBDIRS:
        (docs_root / subdir).mkdir(parents=True, exist_ok=True)
    for generated in (docs_root / "md").glob("source_*.md"):
        generated.unlink()
    for generated in (docs_root / "pdf").glob("source_*.pdf"):
        generated.unlink()
    no_pdf = docs_root / "pdf" / "_no_source_pdf.md"
    if no_pdf.exists():
        no_pdf.unlink()


def _move_root_markdown_notes(analysis_root: Path) -> None:
    docs_md = analysis_root / "docs" / "md"
    docs_md.mkdir(parents=True, exist_ok=True)
    for path in sorted(analysis_root.glob("*.md")):
        if path.name in ROOT_MARKDOWN_ALLOWLIST:
            continue
        target = docs_md / path.name
        _merge_tree(path, target)


def _migrate_shared_roots(analysis_root: Path) -> None:
    data_root = analysis_root / "data"
    if data_root.exists():
        allowed = {"input", "processed"}
        unexpected = sorted(path.name for path in data_root.iterdir() if path.name not in allowed)
        if unexpected:
            raise RuntimeError(f"Unexpected data subfolders in {_rel(data_root)}: {unexpected}")
        _merge_tree(data_root / "input", analysis_root / "shared" / "source")
        _merge_tree(data_root / "processed", analysis_root / "shared" / "results" / "processed")
        _remove_if_empty(data_root, analysis_root)

    _merge_tree(analysis_root / "results", analysis_root / "shared" / "results")
    _merge_tree(analysis_root / "diagnostics", analysis_root / "shared" / "results" / "diagnostics")


def _figure_roots(analysis_root: Path) -> list[Path]:
    figures_root = analysis_root / "figures"
    if not figures_root.exists():
        return []
    return sorted(path for path in figures_root.iterdir() if path.is_dir())


def _migrate_figure_layout(analysis_root: Path) -> None:
    figures_root = analysis_root / "figures"
    if figures_root.exists():
        for path in sorted(figures_root.iterdir()):
            if path.is_file():
                target = analysis_root / "docs" / "md" / f"figures_{path.name}"
                _merge_tree(path, target)
    for figure_root in _figure_roots(analysis_root):
        _merge_tree(figure_root / "input", figure_root / "source")
        _merge_tree(figure_root / "output", figure_root / "results")
        for path in sorted(figure_root.iterdir()):
            if path.is_file():
                _merge_tree(path, figure_root / "results" / path.name)


def _convert_jpeg_sources_to_png(analysis_root: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to convert source paper images to PNG.") from exc

    for source_dir in sorted((analysis_root / "figures").glob("*/source")):
        for image_path in sorted(source_dir.glob("*.jp*g")):
            target = image_path.with_suffix(".png")
            if target.exists():
                if target.read_bytes() != image_path.read_bytes():
                    raise RuntimeError(f"Refusing to overwrite existing PNG while converting {_rel(image_path)}")
                image_path.unlink()
                continue
            with Image.open(image_path) as image:
                if image.mode not in {"RGB", "RGBA"}:
                    image = image.convert("RGBA")
                image.save(target, format="PNG")
            image_path.unlink()


def _clean_generated_source_figures(analysis_root: Path) -> None:
    for source_dir in sorted((analysis_root / "figures").glob("*/source")):
        for path in source_dir.glob("paper_source_*"):
            if path.is_file():
                path.unlink()
        _remove_placeholder_if_content_exists(source_dir)


def _prepare_shared_source(analysis_root: Path) -> None:
    shared_source = analysis_root / "shared" / "source"
    stale_tables = shared_source / "tables"
    if stale_tables.exists():
        shutil.rmtree(stale_tables)
    for filename in ("figures_manifest.csv",):
        path = shared_source / filename
        if path.exists():
            path.unlink()


def _prepare_tables_root(analysis_root: Path) -> None:
    tables_root = analysis_root / "tables"
    tables_root.mkdir(parents=True, exist_ok=True)
    for child in sorted(tables_root.iterdir()):
        if child.is_dir() and re.fullmatch(r"table_\d{3}", child.name):
            shutil.rmtree(child)
    for filename in ("tables_manifest.csv", PLACEHOLDER_NAME):
        path = tables_root / filename
        if path.exists():
            path.unlink()


def _migrate_analysis_layout(analysis_root: Path) -> None:
    _prepare_docs_root(analysis_root)
    _move_root_markdown_notes(analysis_root)
    _migrate_shared_roots(analysis_root)
    _migrate_figure_layout(analysis_root)
    _convert_jpeg_sources_to_png(analysis_root)
    _clean_generated_source_figures(analysis_root)
    _prepare_shared_source(analysis_root)
    _prepare_tables_root(analysis_root)


def _copy_sources(analysis_root: Path, sources: Sequence[PaperSource]) -> list[dict[str, str]]:
    source_rows: list[dict[str, str]] = []
    md_dir = analysis_root / "docs" / "md"
    pdf_dir = analysis_root / "docs" / "pdf"
    for index, source in enumerate(sources, start=1):
        md_path, pdf_path = _source_matches(source)
        md_target = md_dir / f"source_{index:02d}_{source.key}.md"
        md_text = md_path.read_text(encoding="utf-8")
        md_lines = [line.rstrip() for line in md_text.splitlines()]
        while md_lines and md_lines[-1] == "":
            md_lines.pop()
        md_target.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        row = {
            "source_key": source.key,
            "markdown_source": _rel(md_path),
            "markdown_local": _rel(md_target),
            "pdf_source": "",
            "pdf_local": "",
        }
        if pdf_path is not None:
            pdf_target = pdf_dir / f"source_{index:02d}_{source.key}.pdf"
            shutil.copy2(pdf_path, pdf_target)
            row["pdf_source"] = _rel(pdf_path)
            row["pdf_local"] = _rel(pdf_target)
        source_rows.append(row)
    return source_rows


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _caption_after(lines: Sequence[str], start_index: int) -> str:
    for line in lines[start_index + 1 : min(len(lines), start_index + 5)]:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^(fig\.?|figure)\s*[A-Za-z]?\s*\d+", stripped, re.IGNORECASE):
            return stripped
        return ""
    return ""


def _clean_markdown_url(url: str) -> str:
    return url.replace(r"\&", "&").replace(r"\_", "_")


def _download_png_bytes(url: str) -> tuple[bytes, str]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to convert source paper images to PNG.") from exc

    request = urllib.request.Request(url, headers={"User-Agent": "epcsaft-paper-validation-docs/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download figure URL {url}: {exc}") from exc

    with Image.open(io.BytesIO(data)) as image:
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
    png_data = buffer.getvalue()
    return png_data, hashlib.sha256(png_data).hexdigest()


def _caption_figure_id(caption: str, captionless_index: int) -> str:
    match = re.search(r"\b(?:fig\.?|figure)\s*([Ss]?)\s*(\d+)([a-z])?", caption, re.IGNORECASE)
    if not match:
        return f"figure_source_{captionless_index:03d}"
    prefix = "figure_s" if match.group(1) else "figure_"
    return f"{prefix}{match.group(2).lower()}{(match.group(3) or '').lower()}"


def _matching_figure_ids(analysis_root: Path, figure_id: str) -> list[str]:
    existing = {path.name.lower(): path.name for path in _figure_roots(analysis_root)}
    if figure_id.startswith("figure_source_"):
        return [figure_id]
    if re.fullmatch(r"figure_s?\d+", figure_id):
        pattern = re.compile(rf"^{re.escape(figure_id)}(?:[a-z])?(?:_.+)?$", re.IGNORECASE)
    else:
        pattern = re.compile(rf"^{re.escape(figure_id)}(?:_.+)?$", re.IGNORECASE)
    matches = sorted(original for lower, original in existing.items() if pattern.fullmatch(lower))
    return matches or [figure_id]


def _ensure_figure_skeleton(figure_root: Path) -> None:
    messages = {
        "source": "No figure-specific source artifacts are tracked yet.",
        "scripts": "No figure-specific scripts are tracked yet.",
        "results": "No figure-specific package results are tracked yet.",
    }
    for subdir in FIGURE_SUBDIRS:
        _ensure_required_folder(figure_root / subdir, messages[subdir])
    for child in figure_root.iterdir():
        if child.is_dir() and child.name not in FIGURE_SUBDIRS:
            raise RuntimeError(f"Unexpected figure subfolder remains: {_rel(child)}")


def _extract_figures(analysis_root: Path, sources: Sequence[PaperSource]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(r"!\[[^\]]*\]\((?P<url>[^)]+)\)")
    captionless_index = 0
    for source_index, source in enumerate(sources, start=1):
        md_path, _pdf_path = _source_matches(source)
        text = md_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        matches = list(pattern.finditer(text))
        for figure_index, match in enumerate(matches, start=1):
            url = _clean_markdown_url(match.group("url").strip())
            if not re.match(r"https?://", url):
                raise RuntimeError(f"Local Markdown image paths are not supported yet: {_rel(md_path)} -> {url}")
            line_number = _line_number(text, match.start())
            caption = _caption_after(lines, line_number - 1)
            if not caption:
                captionless_index += 1
            requested_figure_id = _caption_figure_id(caption, captionless_index)
            target_figure_ids = _matching_figure_ids(analysis_root, requested_figure_id)
            png_data, digest = _download_png_bytes(url)
            filename = f"paper_source_{source_index:02d}_{source.key}_figure_{figure_index:03d}.png"
            for figure_id in target_figure_ids:
                figure_root = analysis_root / "figures" / figure_id
                source_dir = figure_root / "source"
                source_dir.mkdir(parents=True, exist_ok=True)
                target = source_dir / filename
                target.write_bytes(png_data)
                digest_target = target.with_suffix(target.suffix + ".sha256")
                digest_target.write_text(f"{digest}  {target.name}\n", encoding="utf-8")
                rows.append(
                    {
                        "source_key": source.key,
                        "source_markdown": _rel(md_path),
                        "line": str(line_number),
                        "url": url,
                        "caption": caption,
                        "figure_id": figure_id,
                        "local_file": _rel(target),
                        "sha256_file": _rel(digest_target),
                    }
                )
    return rows


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def _is_separator_row(cells: Sequence[str]) -> bool:
    return all(re.fullmatch(r":?-{2,}:?", cell.strip().replace(" ", "")) for cell in cells)


def _parse_table_rows(lines: Sequence[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if _is_separator_row(cells):
            continue
        rows.append(cells)
    return rows


def _table_caption(lines: Sequence[str], start_index: int) -> str:
    previous = ""
    for line in reversed(lines[max(0, start_index - 3) : start_index]):
        stripped = line.strip()
        if stripped:
            previous = stripped
            break
    first = lines[start_index].strip() if start_index < len(lines) else ""
    if re.match(r"^table\s+[A-Za-z0-9.\-]+", previous, re.IGNORECASE):
        return previous
    if re.match(r"^\|\s*table\s+[A-Za-z0-9.\-]+", first, re.IGNORECASE):
        return first.strip("|").strip()
    return ""


def _extract_tables(analysis_root: Path, sources: Sequence[PaperSource]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    tables_root = analysis_root / "tables"
    tables_root.mkdir(parents=True, exist_ok=True)
    global_table_number = 0
    for source_index, source in enumerate(sources, start=1):
        md_path, _pdf_path = _source_matches(source)
        lines = md_path.read_text(encoding="utf-8").splitlines()
        source_table_number = 0
        index = 0
        while index < len(lines):
            if not _is_table_line(lines[index]):
                index += 1
                continue
            start = index
            while index < len(lines) and _is_table_line(lines[index]):
                index += 1
            end = index
            block = lines[start:end]
            if len(block) < 2:
                continue
            source_table_number += 1
            global_table_number += 1
            caption = _table_caption(lines, start)
            table_id = f"table_{global_table_number:03d}"
            table_dir = tables_root / table_id
            table_dir.mkdir(parents=True, exist_ok=True)
            md_target = table_dir / f"{table_id}.md"
            csv_target = table_dir / f"{table_id}.csv"
            snippet = [
                f"<!-- source: {_rel(md_path)} lines {start + 1}-{end} -->",
            ]
            if caption:
                snippet.extend(["", caption])
            snippet.extend(["", *block, ""])
            md_target.write_text("\n".join(snippet), encoding="utf-8")
            parsed_rows = _parse_table_rows(block)
            max_width = max((len(row) for row in parsed_rows), default=0)
            with csv_target.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                for row in parsed_rows:
                    writer.writerow(row + [""] * (max_width - len(row)))
            rows.append(
                {
                    "source_key": source.key,
                    "source_markdown": _rel(md_path),
                    "start_line": str(start + 1),
                    "end_line": str(end),
                    "caption": caption,
                    "table_id": table_id,
                    "source_table": str(source_table_number),
                    "markdown_file": _rel(md_target),
                    "csv_file": _rel(csv_target),
                }
            )
    return rows


def _ensure_all_figure_skeletons(analysis_root: Path) -> None:
    figures_root = analysis_root / "figures"
    figures_root.mkdir(parents=True, exist_ok=True)
    figure_roots = _figure_roots(analysis_root)
    if figure_roots:
        placeholder = figures_root / PLACEHOLDER_NAME
        if placeholder.exists():
            placeholder.unlink()
    else:
        _write_placeholder(figures_root, "No figure-specific workflows or source figures are tracked yet.")
    for figure_root in figure_roots:
        _ensure_figure_skeleton(figure_root)


def _ensure_analysis_skeleton(analysis_root: Path) -> None:
    _ensure_required_folder(analysis_root / "scripts", "No root-level validation scripts are tracked yet.")
    _ensure_required_folder(analysis_root / "parameters", "No local parameter snapshot is required for this validation yet.")


def _populate_one(analysis_root: Path) -> dict[str, object]:
    rel = analysis_root.relative_to(PAPER_VALIDATION_ROOT).as_posix()
    if rel not in SOURCE_MAP:
        raise RuntimeError(f"No paper-source mapping for validation folder: {_rel(analysis_root)}")

    _migrate_analysis_layout(analysis_root)

    sources = SOURCE_MAP[rel]
    source_rows = _copy_sources(analysis_root, sources)
    figure_rows = _extract_figures(analysis_root, sources)
    table_rows = _extract_tables(analysis_root, sources)
    _ensure_all_figure_skeletons(analysis_root)
    _ensure_analysis_skeleton(analysis_root)

    docs_root = analysis_root / "docs"
    shared_source = analysis_root / "shared" / "source"
    tables_root = analysis_root / "tables"

    _write_csv(
        docs_root / "source_manifest.csv",
        source_rows,
        ("source_key", "markdown_source", "markdown_local", "pdf_source", "pdf_local"),
    )
    _write_csv(
        shared_source / "figures_manifest.csv",
        figure_rows,
        ("source_key", "source_markdown", "line", "url", "caption", "figure_id", "local_file", "sha256_file"),
    )
    _write_csv(
        tables_root / "tables_manifest.csv",
        table_rows,
        (
            "source_key",
            "source_markdown",
            "start_line",
            "end_line",
            "caption",
            "table_id",
            "source_table",
            "markdown_file",
            "csv_file",
        ),
    )

    if not any(row["pdf_local"] for row in source_rows):
        _write_placeholder(docs_root / "pdf", "No matching source PDF exists under docs/papers/pdf.")
    if not table_rows:
        _write_placeholder(tables_root, "No Markdown table blocks were found in the matched source Markdown files.")
    _remove_placeholder_if_content_exists(shared_source)

    return {
        "analysis": rel,
        "source_count": len(source_rows),
        "pdf_count": sum(1 for row in source_rows if row["pdf_local"]),
        "figure_count": len(figure_rows),
        "table_count": len(table_rows),
    }


def _check_manifest_targets(analysis_root: Path, errors: list[str]) -> None:
    rel = _rel(analysis_root)
    manifests = (
        analysis_root / "docs" / "source_manifest.csv",
        analysis_root / "shared" / "source" / "figures_manifest.csv",
        analysis_root / "tables" / "tables_manifest.csv",
    )
    for manifest in manifests:
        if not manifest.is_file():
            errors.append(f"{rel}: missing {_rel(manifest)}")
            continue
        with manifest.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                for field in ("markdown_local", "pdf_local", "local_file", "sha256_file", "markdown_file", "csv_file"):
                    value = row.get(field)
                    if value and not (REPO_ROOT / value).is_file():
                        errors.append(f"{rel}: manifest target missing: {value}")


def _check_one(analysis_root: Path) -> list[str]:
    errors: list[str] = []
    rel = _rel(analysis_root)
    docs_root = analysis_root / "docs"
    if not docs_root.is_dir():
        errors.append(f"{rel}: missing docs")
    else:
        actual_docs = {path.name for path in docs_root.iterdir() if path.is_dir()}
        if actual_docs != set(DOC_SUBDIRS):
            errors.append(f"{rel}: docs subfolders are {sorted(actual_docs)}, expected {sorted(DOC_SUBDIRS)}")
    for forbidden in ("data", "results", "diagnostics"):
        if (analysis_root / forbidden).exists():
            errors.append(f"{rel}: root {forbidden}/ must move under shared/")
    for markdown in sorted(analysis_root.glob("*.md")):
        if markdown.name not in ROOT_MARKDOWN_ALLOWLIST:
            errors.append(f"{rel}: root Markdown note must move to docs/md: {markdown.name}")
    for child in sorted(analysis_root.iterdir()):
        if child.is_dir() and child.name not in ROOT_DIRS:
            errors.append(f"{rel}: unexpected root folder: {child.name}")
        if child.is_file() and child.name not in {"analysis.yaml", "README.md"}:
            errors.append(f"{rel}: unexpected root file: {child.name}")
    figures_root = analysis_root / "figures"
    if figures_root.exists():
        for child in sorted(figures_root.iterdir()):
            if child.is_file() and child.name != PLACEHOLDER_NAME:
                errors.append(f"{rel}: figures root file must move to docs/md: {child.name}")
    for figure_root in _figure_roots(analysis_root):
        actual = {path.name for path in figure_root.iterdir() if path.is_dir()}
        if actual != set(FIGURE_SUBDIRS):
            errors.append(f"{rel}: {figure_root.name} subfolders are {sorted(actual)}, expected {sorted(FIGURE_SUBDIRS)}")
        direct_files = [path.name for path in figure_root.iterdir() if path.is_file()]
        if direct_files:
            errors.append(f"{rel}: {figure_root.name} direct files must move under results/: {direct_files}")
        for image in (figure_root / "source").glob("paper_source_*"):
            if image.suffix.lower() != ".png" and not image.name.endswith(".sha256"):
                errors.append(f"{rel}: extracted source figure is not PNG: {_rel(image)}")
        if list((figure_root / "source").glob("*.jp*g")):
            errors.append(f"{rel}: source JPEG remains under {_rel(figure_root / 'source')}")
    tables_root = analysis_root / "tables"
    if not tables_root.is_dir():
        errors.append(f"{rel}: missing tables")
    else:
        stale_shared_tables = analysis_root / "shared" / "source" / "tables"
        if stale_shared_tables.exists():
            errors.append(f"{rel}: shared/source/tables must move to top-level tables/")
        for child in sorted(tables_root.iterdir()):
            if child.is_dir():
                if not re.fullmatch(r"table_\d{3}", child.name):
                    errors.append(f"{rel}: unexpected table folder: {child.name}")
                    continue
                if not any(child.glob("*.md")):
                    errors.append(f"{rel}: {child.name} missing Markdown table snippet")
                if not any(child.glob("*.csv")):
                    errors.append(f"{rel}: {child.name} missing CSV table extraction")
            elif child.name not in {"tables_manifest.csv", PLACEHOLDER_NAME}:
                errors.append(f"{rel}: unexpected tables root file: {child.name}")
    _check_manifest_targets(analysis_root, errors)
    return errors


def _iter_rewrite_files() -> Iterable[Path]:
    roots = ("analyses", "docs", "scripts", "tests")
    for root_name in roots:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if path.resolve() == Path(__file__).resolve():
                continue
            rel = _rel(path)
            if rel.startswith("docs/papers/"):
                continue
            yield path


def _apply_replacements(text: str, replacements: Sequence[tuple[str, str]]) -> str:
    new_text = text
    for old, new in replacements:
        new_text = new_text.replace(old, new)
    return new_text


def _apply_paper_validation_replacements(text: str) -> str:
    new_text = text
    new_text = re.sub(r"(figures[/\\][^/\\\s\"'`,]+)[/\\]input\b", r"\1/source", new_text)
    new_text = re.sub(r"(figures[/\\][^/\\\s\"'`,]+)[/\\]output\b", r"\1/results", new_text)
    new_text = re.sub(r"(figures[/\\]\{[^}]+\})[/\\]input\b", r"\1/source", new_text)
    new_text = re.sub(r"(figures[/\\]\{[^}]+\})[/\\]output\b", r"\1/results", new_text)
    literal_pairs = {
        'figures: figures/<figure_id>/output': 'figures: figures/<figure_id>/results',
        'runs: figures/<figure_id>/output/runs': 'runs: figures/<figure_id>/results/runs',
        'figure-owned `input/`': 'figure-owned `source/`',
        '`figures/<figure_id>/input/`': '`figures/<figure_id>/source/`',
        '`figures/<figure_id>/output/`': '`figures/<figure_id>/results/`',
        '`docs/figures/`': '`shared/source/`',
        '`docs/tables/`': '`tables/`',
        '`shared/source/tables/`': '`tables/`',
        'docs/figures/': 'shared/source/',
        'docs/tables/': 'tables/',
        'shared/source/tables/': 'tables/',
        'data/input/': 'shared/source/',
        'data/processed/': 'shared/results/processed/',
        'data\\input\\': 'shared\\source\\',
        'data\\processed\\': 'shared\\results\\processed\\',
        'data/input': 'shared/source',
        'data/processed': 'shared/results/processed',
        'data\\input': 'shared\\source',
        'data\\processed': 'shared\\results\\processed',
        '`data/input`': '`shared/source`',
        '`data/processed`': '`shared/results/processed`',
        '`data\\input`': '`shared\\source`',
        '`data\\processed`': '`shared\\results\\processed`',
        '`output/data/': '`results/data/',
        '/output/data/': '/results/data/',
        '\\output\\data\\': '\\results\\data\\',
        'kind="input"': 'kind="source"',
        "kind='input'": "kind='source'",
        'kind="output"': 'kind="results"',
        "kind='output'": "kind='results'",
        ' / "data" / "input"': ' / "shared" / "source"',
        " / 'data' / 'input'": " / 'shared' / 'source'",
        ' / "data" / "processed"': ' / "shared" / "results" / "processed"',
        " / 'data' / 'processed'": " / 'shared' / 'results' / 'processed'",
        ' / "input"': ' / "source"',
        " / 'input'": " / 'source'",
        ' / "output"': ' / "results"',
        " / 'output'": " / 'results'",
        "source_image.jpg": "source_image.png",
    }
    return _apply_replacements(new_text, list(literal_pairs.items()))


def _uses_paper_validation_contract(relpath: str, text: str) -> bool:
    contract_files = {
        "analyses/package_validation/package_plot_smokes/tests/plots/test_2015_baygi_outputs.py",
        "scripts/plot_outputs.py",
    }
    return relpath.startswith("analyses/paper_validation/") or relpath in contract_files


def _path_replacements() -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    for old, new in PATH_REWRITES.items():
        replacements.append((old, new))
        replacements.append((old.replace("/", "\\"), new.replace("/", "\\")))
    for rel in sorted(SOURCE_MAP):
        analysis_rel = f"analyses/paper_validation/{rel}"
        pairs = {
            f"{analysis_rel}/data/input": f"{analysis_rel}/shared/source",
            f"{analysis_rel}/data/processed": f"{analysis_rel}/shared/results/processed",
            f"{analysis_rel}/data": f"{analysis_rel}/shared/source",
            f"{analysis_rel}/diagnostics": f"{analysis_rel}/shared/results/diagnostics",
            f"{analysis_rel}/results": f"{analysis_rel}/shared/results",
            f"{analysis_rel}/docs/figures": f"{analysis_rel}/shared/source",
            f"{analysis_rel}/docs/tables": f"{analysis_rel}/tables",
            f"{analysis_rel}/shared/source/tables": f"{analysis_rel}/tables",
        }
        for old, new in pairs.items():
            replacements.append((old, new))
            replacements.append((old.replace("/", "\\"), new.replace("/", "\\")))
    return replacements


def _rewrite_text_paths(check: bool) -> list[str]:
    changed: list[str] = []
    replacements = _path_replacements()
    for path in _iter_rewrite_files():
        rel = _rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        new_text = _apply_replacements(text, replacements)
        if _uses_paper_validation_contract(rel, new_text):
            new_text = _apply_paper_validation_replacements(new_text)
        if new_text != text:
            changed.append(rel)
            if not check:
                path.write_text(new_text, encoding="utf-8")
    return changed


def _populate_all() -> list[dict[str, object]]:
    discovered = {path.relative_to(PAPER_VALIDATION_ROOT).as_posix() for path in _analysis_dirs()}
    expected = set(SOURCE_MAP)
    missing_dirs = sorted(expected - discovered)
    unmapped_dirs = sorted(discovered - expected)
    if missing_dirs:
        raise RuntimeError(f"Missing validation folders for mapped sources: {missing_dirs}")
    if unmapped_dirs:
        raise RuntimeError(f"Validation folders missing paper-source mappings: {unmapped_dirs}")
    return [_populate_one(PAPER_VALIDATION_ROOT / rel) for rel in sorted(SOURCE_MAP)]


def _check_all() -> list[str]:
    errors: list[str] = []
    discovered = {path.relative_to(PAPER_VALIDATION_ROOT).as_posix() for path in _analysis_dirs()}
    expected = set(SOURCE_MAP)
    for missing_dir in sorted(expected - discovered):
        errors.append(f"mapped validation folder is missing: {missing_dir}")
    for unmapped_dir in sorted(discovered - expected):
        errors.append(f"validation folder is missing a paper-source mapping: {unmapped_dir}")
    for rel in sorted(SOURCE_MAP):
        errors.extend(_check_one(PAPER_VALIDATION_ROOT / rel))
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify extracted docs without writing.")
    parser.add_argument(
        "--rewrite-stale-paths",
        action="store_true",
        help="Rewrite old paper_validation application/native text paths and legacy artifact folder paths.",
    )
    args = parser.parse_args(argv)

    if args.check:
        errors = _check_all()
        changed = _rewrite_text_paths(check=True) if args.rewrite_stale_paths else []
        if changed:
            errors.append("stale text paths remain in: " + ", ".join(changed))
        if errors:
            print(json.dumps({"status": "failed", "errors": errors}, indent=2))
            return 1
        print(json.dumps({"status": "ok", "checked": len(SOURCE_MAP)}, indent=2))
        return 0

    summary = _populate_all()
    changed = _rewrite_text_paths(check=False) if args.rewrite_stale_paths else []
    print(json.dumps({"status": "ok", "docs": summary, "rewritten_text_files": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
