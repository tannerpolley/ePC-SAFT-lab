"""Validate paper-validation ePC-SAFT parameter bundles.

The canonical bundles now live under
``analyses/paper_validation/<paper_id>/parameters``. The retired
``data/reference/epcsaft_parameters`` path is pointer-only and must not contain
dataset folders.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_ROOT = REPO_ROOT / "analyses" / "paper_validation"
LEGACY_ROOT = REPO_ROOT / "data" / "reference" / "epcsaft_parameters"
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

PURE_COLUMNS = [
    "component",
    "m",
    "s",
    "e",
    "e_assoc",
    "vol_a",
    "assoc_scheme",
    "z",
    "dielc",
    "d_born",
    "f_solv",
    "MW",
    "source",
]
REQUIRED_VALUE_COLUMNS = ["m", "s", "e", "e_assoc", "vol_a", "z", "dielc", "d_born", "f_solv", "MW"]
BINARY_FILES = ["k_ij.csv", "l_ij.csv", "k_hb_ij.csv"]
DATASET_SUFFIXES = (
    "_Gross",
    "_Held",
    "_Baygi",
    "_Ascani",
    "_Yu",
    "_Rezaee",
    "_Cameretti",
    "_Bulow",
    "_Figiel",
    "_Khudaida",
    "_Hubach",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Retained for compatibility; validation is read-only.")
    parser.parse_args(argv)

    errors = validate_legacy_root() + validate_parameter_bundles()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("paper validation parameter bundles are current")
    return 0


def validate_legacy_root() -> list[str]:
    if not LEGACY_ROOT.is_dir():
        return [f"missing pointer directory: {rel(LEGACY_ROOT)}"]
    children = {path.name for path in LEGACY_ROOT.iterdir()}
    if children != {"README.md"}:
        return [f"legacy parameter root must contain only README.md, found: {sorted(children)}"]
    text = (LEGACY_ROOT / "README.md").read_text(encoding="utf-8")
    if "analyses/paper_validation/<paper_id>/parameters" not in text:
        return [f"legacy pointer README does not mention the new paper-validation parameter path: {rel(LEGACY_ROOT)}"]
    return []


def validate_parameter_bundles() -> list[str]:
    errors: list[str] = []
    parameter_roots = sorted(path for path in PAPER_ROOT.iterdir() if (path / "parameters").is_dir())
    if not parameter_roots:
        return [f"no paper-validation parameter bundles found under {rel(PAPER_ROOT)}"]

    for analysis_root in parameter_roots:
        parameter_root = analysis_root / "parameters"
        prefix = rel(parameter_root)
        errors.extend(validate_parameter_root(parameter_root, prefix))
    return errors


def validate_parameter_root(parameter_root: Path, prefix: str) -> list[str]:
    errors: list[str] = []
    for required in ("pure", "mixed", "user_options.json"):
        path = parameter_root / required
        if required.endswith(".json"):
            if not path.is_file():
                errors.append(f"missing {required}: {prefix}")
        elif not path.is_dir():
            errors.append(f"missing {required}/: {prefix}")

    errors.extend(validate_no_nested_dataset_dirs(parameter_root, prefix))
    errors.extend(validate_user_options(parameter_root / "user_options.json", prefix))
    errors.extend(validate_pure_files(parameter_root / "pure", prefix))
    errors.extend(validate_binary_files(parameter_root / "mixed" / "binary_interaction", prefix))
    errors.extend(validate_khudaida_runtime_payload(parameter_root, prefix))
    return errors


def validate_no_nested_dataset_dirs(parameter_root: Path, prefix: str) -> list[str]:
    return [
        f"nested dataset folder is not allowed in paper-validation parameters: {rel(child)}"
        for child in parameter_root.iterdir()
        if child.is_dir() and child.name.endswith(DATASET_SUFFIXES)
    ]


def validate_user_options(path: Path, prefix: str) -> list[str]:
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid user_options.json in {prefix}: {exc}"]
    if not isinstance(payload, dict):
        return [f"user_options.json must contain a JSON object: {prefix}"]
    return []


def validate_pure_files(pure_root: Path, prefix: str) -> list[str]:
    if not pure_root.is_dir():
        return []
    errors: list[str] = []
    pure_files = sorted(pure_root.glob("*.csv"))
    if not pure_files:
        return [f"missing pure CSV files: {prefix}"]
    for pure_file in pure_files:
        with pure_file.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        if reader.fieldnames != PURE_COLUMNS:
            errors.append(f"unexpected pure CSV columns: {rel(pure_file)}")
            continue
        if not rows:
            errors.append(f"empty pure CSV: {rel(pure_file)}")
            continue
        for row_number, row in enumerate(rows, start=2):
            component = row.get("component", "").strip()
            if not component:
                errors.append(f"blank component in {rel(pure_file)}:{row_number}")
            if not row.get("source", "").strip():
                errors.append(f"blank source for {component or '<blank>'} in {rel(pure_file)}:{row_number}")
            for column in REQUIRED_VALUE_COLUMNS:
                value = row.get(column, "").strip()
                if not value:
                    errors.append(f"blank {column} for {component or '<blank>'} in {rel(pure_file)}:{row_number}")
                if "=" in value:
                    errors.append(f"label-prefixed value in {rel(pure_file)}:{row_number} column {column}: {value}")
    return errors


def validate_binary_files(binary_root: Path, prefix: str) -> list[str]:
    if not binary_root.is_dir():
        return [f"missing mixed/binary_interaction/: {prefix}"]
    errors: list[str] = []
    for filename in BINARY_FILES:
        path = binary_root / filename
        if not path.is_file():
            errors.append(f"missing binary matrix {filename}: {prefix}")
            continue
        errors.extend(validate_square_matrix(path))
    if not (binary_root / "source_manifest.csv").is_file():
        errors.append(f"missing binary source_manifest.csv: {prefix}")
    return errors


def validate_khudaida_runtime_payload(parameter_root: Path, prefix: str) -> list[str]:
    if parameter_root.parent.name != "2026_khudaida":
        return []
    try:
        from epcsaft.model.parameters import ParameterSource

        species = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
        composition = [
            0.7295582904360921,
            0.013336215598851259,
            0.20495308450174898,
            0.026076204731653927,
            0.026076204731653927,
        ]
        ParameterSource(parameter_root, species=species).to_runtime_dict(
            x=composition,
            T=293.15,
        )
    except Exception as exc:
        return [f"Khudaida runtime parameter payload does not normalize: {prefix}: {exc}"]
    return []


def validate_square_matrix(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return [f"empty binary matrix: {rel(path)}"]
        rows = list(reader)

    if not header or header[0] != "component":
        errors.append(f"binary matrix first header must be component: {rel(path)}")
    components = header[1:]
    if len(rows) != len(components):
        errors.append(f"binary matrix is not square: {rel(path)}")
    if [row[0] for row in rows if row] != components:
        errors.append(f"binary matrix row labels do not match header: {rel(path)}")
    for row_number, row in enumerate(rows, start=2):
        if len(row) != len(header):
            errors.append(f"binary matrix row width mismatch in {rel(path)}:{row_number}")
            continue
        if any(not cell.strip() for cell in row[1:]):
            errors.append(f"blank binary matrix value in {rel(path)}:{row_number}")
    return errors


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
