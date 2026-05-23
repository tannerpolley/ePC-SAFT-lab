"""Curate paper-validation ePC-SAFT parameter bundles.

The script builds canonical datasets under ``data/reference/epcsaft_parameters``
and snapshots those datasets into ``analyses/paper_validation/<paper>/parameters``.
It is intentionally strict: generated pure CSVs include row-level source metadata,
and every binary matrix is explicit and zero-filled.
"""

from __future__ import annotations

import argparse
import csv
import filecmp
import json
import re
import shutil
import sys
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from epcsaft.model.templates import create_parameter_template

REFERENCE_ROOT = REPO_ROOT / "data" / "reference" / "epcsaft_parameters"
PAPER_ROOT = REPO_ROOT / "analyses" / "paper_validation"

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
BINARY_PARAMETER_FILES = {
    "k_ij": "k_ij.csv",
    "l_ij": "l_ij.csv",
    "k_hb_ij": "k_hb_ij.csv",
}
SNAPSHOTS = {
    "2001_gross": "2001_Gross",
    "2002_gross": "2002_Gross",
    "2005_cameretti": "2005_Cameretti",
    "2008_held": "2008_Held",
    "2012_held": "2012_Held",
    "2014_held": "2014_Held",
    "2015_baygi": "2015_Baygi",
    "2019_bulow": "2019_Bulow",
    "2020_bulow": "2020_Bulow",
    "2021_bulow": "2021_Bulow",
    "2022_ascani": "2022_Ascani",
    "2023_ascani": "2023_Ascani",
    "2024_hubach": "2024_Hubach",
    "2024_yu": "2024_Yu",
    "2025_figiel": "2025_Figiel",
    "2026_khudaida": "2026_Khudaida",
    "2026_rezaee": "2026_Rezaee",
}
EXISTING_REFERENCE_DATASETS = {
    "2005_Cameretti",
    "2008_Held",
    "2012_Held",
    "2014_Held",
    "2019_Bulow",
    "2020_Bulow",
    "2021_Bulow",
    "2022_Ascani",
    "2024_Hubach",
    "2025_Figiel",
    "2026_Khudaida",
}
WATER_SIGMA_EXPR = "2.7927+(10.11*exp(-0.01775*T)-1.417*exp(-0.01146*T))"

COMPONENT_DEFAULTS: dict[str, dict[str, str]] = {
    "H+": {"MW": "0.001008", "z": "1", "dielc": "8", "d_born": "1.0", "f_solv": "1"},
    "H2O": {
        "m": "1.2047",
        "s": WATER_SIGMA_EXPR,
        "e": "353.95",
        "e_assoc": "2425.7",
        "vol_a": "0.04509",
        "assoc_scheme": "2B",
        "MW": "0.01801528",
        "z": "0",
        "dielc": "78.09",
        "d_born": "0",
        "f_solv": "1.5",
        "source": "Ascani2023 Table1 default fill",
    },
    "Methanol": {
        "m": "1.5255",
        "s": "3.2300",
        "e": "188.90",
        "e_assoc": "2899.5",
        "vol_a": "0.035176",
        "assoc_scheme": "2B",
        "MW": "0.032042",
        "z": "0",
        "dielc": "33.05",
        "d_born": "0",
        "f_solv": "1.4",
        "source": "Gross2002 Table1 default fill",
    },
    "Ethanol": {
        "m": "2.3827",
        "s": "3.1771",
        "e": "198.24",
        "e_assoc": "2653.4",
        "vol_a": "0.032384",
        "assoc_scheme": "2B",
        "MW": "0.046069",
        "z": "0",
        "dielc": "24.88",
        "d_born": "0",
        "f_solv": "1.6",
        "source": "Gross2002 Table1 default fill",
    },
    "OH-": {"MW": "0.017007", "z": "-1", "dielc": "8", "d_born": "3.0", "f_solv": "1"},
    "Li+": {"m": "1", "MW": "0.00694", "z": "1", "dielc": "8", "d_born": "2.784", "f_solv": "1"},
    "Na+": {"m": "1", "MW": "0.02298", "z": "1", "dielc": "8", "d_born": "3.445", "f_solv": "1"},
    "K+": {"m": "1", "MW": "0.0391", "z": "1", "dielc": "8", "d_born": "4.15", "f_solv": "1"},
    "NH4+": {"m": "1", "MW": "0.018038", "z": "1", "dielc": "8", "d_born": "3.0", "f_solv": "1"},
    "Mg2+": {"m": "1", "MW": "0.024305", "z": "2", "dielc": "8", "d_born": "4.0", "f_solv": "1"},
    "Cl-": {"m": "1", "MW": "0.03545", "z": "-1", "dielc": "8", "d_born": "4.1", "f_solv": "1"},
    "Br-": {"m": "1", "MW": "0.0799", "z": "-1", "dielc": "8", "d_born": "4.48", "f_solv": "1"},
    "I-": {"m": "1", "MW": "0.1269", "z": "-1", "dielc": "8", "d_born": "4.985", "f_solv": "1"},
    "CO2": {"MW": "0.04401", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "MEA": {"MW": "0.061083", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "Acetic acid": {"MW": "0.060052", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "1-Pentanol": {"MW": "0.08815", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "1-Hexanol": {"MW": "0.102177", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "Pentyl Acetate": {"MW": "0.13019", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "Hexyl Acetate": {"MW": "0.14421", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "TOP": {"MW": "0.38664", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "[HOEMIM][Tf2N]": {"MW": "0.40731", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "DES": {"MW": "0.62246", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "TOPO": {"MW": "0.38664", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "RLi": {"MW": "0.100", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "RNa": {"MW": "0.100", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "A": {"MW": "0.100", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "B": {"MW": "0.100", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
    "C": {"MW": "0.100", "z": "0", "dielc": "1", "d_born": "0", "f_solv": "1"},
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated datasets match the working tree.")
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="epcsaft-paper-params-") as tmp:
        desired_reference = Path(tmp) / "reference"
        desired_reference.mkdir(parents=True)
        build_all(desired_reference)

        if args.check:
            mismatches = compare_expected(desired_reference)
            if mismatches:
                for mismatch in mismatches:
                    print(mismatch)
                return 1
            print("paper validation parameter bundles are current")
            return 0

        write_all(desired_reference)
        print(f"curated {len(SNAPSHOTS)} paper-validation parameter bundles")
        return 0


def build_all(out_reference: Path) -> None:
    gross_2001_records = build_gross_2001(out_reference / "2001_Gross")
    build_gross_2002(out_reference / "2002_Gross", gross_2001_records)
    for dataset in sorted(EXISTING_REFERENCE_DATASETS):
        normalize_existing_dataset(REFERENCE_ROOT / dataset, out_reference / dataset, dataset)
    build_baygi_2015(out_reference / "2015_Baygi")
    build_ascani_2023(out_reference / "2023_Ascani")
    build_yu_2024(out_reference / "2024_Yu")
    build_rezaee_2026(out_reference / "2026_Rezaee")


def write_all(desired_reference: Path) -> None:
    for _paper_id, dataset in SNAPSHOTS.items():
        replace_tree(desired_reference / dataset, REFERENCE_ROOT / dataset)
    for paper_id, dataset in SNAPSHOTS.items():
        replace_tree(desired_reference / dataset, PAPER_ROOT / paper_id / "parameters")


def compare_expected(desired_reference: Path) -> list[str]:
    mismatches: list[str] = []
    for paper_id, dataset in SNAPSHOTS.items():
        for expected_root, actual_root in (
            (desired_reference / dataset, REFERENCE_ROOT / dataset),
            (desired_reference / dataset, PAPER_ROOT / paper_id / "parameters"),
        ):
            mismatches.extend(compare_trees(expected_root, actual_root))
    return mismatches


def compare_trees(expected: Path, actual: Path) -> list[str]:
    if not actual.exists():
        return [f"missing directory: {actual.relative_to(REPO_ROOT)}"]
    mismatches: list[str] = []
    expected_files = {p.relative_to(expected).as_posix(): p for p in expected.rglob("*") if p.is_file()}
    actual_files = {p.relative_to(actual).as_posix(): p for p in actual.rglob("*") if p.is_file()}
    for relpath in sorted(set(expected_files) - set(actual_files)):
        mismatches.append(f"missing file: {(actual / relpath).relative_to(REPO_ROOT)}")
    for relpath in sorted(set(actual_files) - set(expected_files)):
        mismatches.append(f"unexpected file: {(actual / relpath).relative_to(REPO_ROOT)}")
    for relpath in sorted(set(expected_files) & set(actual_files)):
        if not filecmp.cmp(expected_files[relpath], actual_files[relpath], shallow=False):
            mismatches.append(f"stale file: {actual_files[relpath].relative_to(REPO_ROOT)}")
    return mismatches


def replace_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def normalize_existing_dataset(source: Path, target: Path, dataset: str) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    pure_sets: dict[str, list[dict[str, str]]] = {}
    for pure_file in sorted((source / "pure").glob("*.csv")):
        rows = [normalize_pure_row(row, f"{dataset} reference dataset") for row in read_dicts(pure_file)]
        pure_sets[pure_file.name] = rows
    if not pure_sets:
        raise ValueError(f"{dataset} has no pure/*.csv files")
    components = [row["component"] for row in next(iter(pure_sets.values()))]
    matrix_values: dict[str, dict[tuple[str, str], str]] = {}
    source_rows: list[dict[str, str]] = []
    binary_root = source / "mixed" / "binary_interaction"
    for parameter, filename in BINARY_PARAMETER_FILES.items():
        matrix_path = binary_root / filename
        if matrix_path.exists():
            matrix_values[parameter] = read_matrix(matrix_path)
            source_rows.extend(source_rows_for_matrix(parameter, matrix_values[parameter], f"{dataset} {filename}"))
        else:
            matrix_values[parameter] = {}
            source_rows.append(default_binary_source_row(parameter))
    rel_perm_files = sorted((source / "mixed" / "rel_perm").glob("*.csv"))
    user_options = read_json(source / "user_options.json") if (source / "user_options.json").exists() else {}
    write_dataset(target, dataset, pure_sets, components, matrix_values, source_rows, user_options, rel_perm_files)


def build_gross_2001(target: Path) -> dict[str, dict[str, str]]:
    pure_rows = parse_gross_2001_pure()
    components = [row["component"] for row in pure_rows]
    k_values: dict[tuple[str, str], str] = {}
    source_rows: list[dict[str, str]] = [default_binary_source_row("l_ij"), default_binary_source_row("k_hb_ij")]
    for row in read_dicts(PAPER_ROOT / "2001_gross" / "tables" / "table_005" / "table_005.csv"):
        system = clean_text(row.get("system", ""))
        kij = clean_scalar(row.get("PC-SAFT", ""))
        if not system or kij == "0":
            continue
        left, right = split_binary_system(system, components)
        add_symmetric(k_values, left, right, kij)
        source_rows.append(binary_source_row("k_ij", left, right, kij, "Gross2001 Table4"))
    write_dataset(
        target,
        "2001_Gross",
        {"any_solvent.csv": pure_rows},
        components,
        {"k_ij": k_values, "l_ij": {}, "k_hb_ij": {}},
        source_rows,
        {},
        [],
    )
    return {row["component"]: row for row in pure_rows}


def parse_gross_2001_pure() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for table_id in ("table_002", "table_003"):
        for row in read_dicts(PAPER_ROOT / "2001_gross" / "tables" / table_id / f"{table_id}.csv"):
            name = clean_component(row.get("substance", ""))
            if not name or not is_number(row.get("M [g/mol]")):
                continue
            rows.append(
                pure_record(
                    name,
                    m=row["m [-]"],
                    s=row[r"$\sigma$ [Å]"],
                    e=row[r"$\epsilon / \mathrm{k}$ [K]"],
                    mw_g=row["M [g/mol]"],
                    source=f"Gross2001 {table_id.replace('_', ' ')}",
                )
            )
    return dedupe_pure_rows(rows)


def build_gross_2002(target: Path, gross_2001_records: Mapping[str, dict[str, str]]) -> None:
    pure_rows = []
    for row in read_dicts(PAPER_ROOT / "2002_gross" / "tables" / "table_001" / "table_001.csv"):
        name = clean_component(row.get(r"component $\mathrm{i}^{\mathrm{a}}$", ""))
        if not name or not is_number(row.get(r"$\mathrm{M}_{\mathrm{i}}$ (g/mol)")):
            continue
        pure_rows.append(
            pure_record(
                name,
                m=row[r"$\mathrm{m}_{\mathrm{i}}$"],
                s=row[r"$\sigma_{\mathrm{i}}$ (Å)"],
                e=row[r"$\epsilon_{\mathrm{i}} / \mathrm{k}$ (K)"],
                e_assoc=row[r"$\epsilon^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{\mathrm{i}}} / \mathrm{k}$ (K)"],
                vol_a=row[r"$\kappa^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{\mathrm{i}}}$"],
                assoc_scheme="2B",
                mw_g=row[r"$\mathrm{M}_{\mathrm{i}}$ (g/mol)"],
                source="Gross2002 Table1",
            )
        )
    components = [row["component"] for row in pure_rows]
    k_values: dict[tuple[str, str], str] = {}
    source_rows: list[dict[str, str]] = [default_binary_source_row("l_ij"), default_binary_source_row("k_hb_ij")]
    for row in read_dicts(PAPER_ROOT / "2002_gross" / "tables" / "table_002" / "table_002.csv"):
        system = clean_text(row.get("binary system", ""))
        kij = clean_scalar(row.get(r"$\mathrm{k}_{\mathrm{ij}}{ }^{\mathrm{a}}$", ""))
        if not system or kij == "0":
            continue
        left, right = split_binary_system(system, components + list(gross_2001_records))
        for component in (left, right):
            if component not in components:
                if component not in gross_2001_records:
                    raise ValueError(f"Gross2002 binary component lacks pure parameters: {component}")
                pure_rows.append(gross_2001_records[component] | {"source": "Gross2001 Table2; Gross2002 Table2"})
                components.append(component)
        add_symmetric(k_values, left, right, kij)
        source_rows.append(binary_source_row("k_ij", left, right, kij, "Gross2002 Table2"))
    write_dataset(
        target,
        "2002_Gross",
        {"any_solvent.csv": pure_rows},
        components,
        {"k_ij": k_values, "l_ij": {}, "k_hb_ij": {}},
        source_rows,
        {},
        [],
    )


def build_baygi_2015(target: Path) -> None:
    pure_rows: list[dict[str, str]] = []
    last_species = ""
    for row in read_dicts(PAPER_ROOT / "2015_baygi" / "tables" / "table_003" / "table_003.csv"):
        raw_species = clean_component(row.get("Species", ""))
        if raw_species:
            last_species = raw_species
        if not last_species or not is_number(row.get("$m$")):
            continue
        scheme = clean_assoc_scheme(row.get("Association scheme", ""))
        base = last_species
        component = f"{base}-{scheme}" if scheme and scheme != "Nonassociating" else base
        pure_rows.append(
            pure_record(
                component,
                m=row["$m$"],
                s=row[r"$\sigma$"],
                e=row[r"$\varepsilon / k_{\mathrm{B}}$"],
                e_assoc=row[r"$\varepsilon^{\mathrm{AB}} / \mathrm{k}_{\mathrm{B}}$"],
                vol_a=row[r"$\kappa{ }^{\text {AB }}$"],
                assoc_scheme="" if scheme == "Nonassociating" else scheme,
                mw=default_field(base, "MW"),
                source="Baygi2015 Table2",
            )
        )
    components = [row["component"] for row in pure_rows]
    k_values: dict[tuple[str, str], str] = {}
    source_rows: list[dict[str, str]] = [default_binary_source_row("l_ij"), default_binary_source_row("k_hb_ij")]
    h2o_scheme = ""
    for row in read_dicts(PAPER_ROOT / "2015_baygi" / "tables" / "table_004" / "table_004.csv"):
        mea_scheme = clean_assoc_scheme(row.get("Association schemes", ""))
        maybe_h2o = clean_assoc_scheme(row.get("", ""))
        if maybe_h2o:
            h2o_scheme = maybe_h2o
        kij = clean_scalar(row.get(r"$k_{i j}$", ""))
        if not mea_scheme or not h2o_scheme or kij == "0":
            continue
        left = f"MEA-{mea_scheme}"
        right = f"H2O-{h2o_scheme}"
        add_symmetric(k_values, left, right, kij)
        source_rows.append(binary_source_row("k_ij", left, right, kij, "Baygi2015 Table3"))
    write_dataset(
        target,
        "2015_Baygi",
        {"any_solvent.csv": pure_rows},
        components,
        {"k_ij": k_values, "l_ij": {}, "k_hb_ij": {}},
        source_rows,
        {},
        [],
    )


def build_ascani_2023(target: Path) -> None:
    pure_rows: list[dict[str, str]] = []
    for row in read_dicts(PAPER_ROOT / "2023_ascani" / "tables" / "table_001" / "table_001.csv"):
        component = clean_component(row.get("Component", ""))
        if not component or not is_number(row.get(r"$m_{i}^{\text {seg }} /-$")):
            continue
        pure_rows.append(
            pure_record(
                component,
                m=row[r"$m_{i}^{\text {seg }} /-$"],
                s=WATER_SIGMA_EXPR if row.get(r"$\sigma_{i} /$") == "*" else row.get(r"$\sigma_{i} /$", ""),
                e=row[
                    r"$\boldsymbol{u}_{\boldsymbol{i}} \boldsymbol{k}_{\boldsymbol{B}}^{\boldsymbol{-} \mathbf{1}} \boldsymbol{/} \mathbf{K}$"
                ],
                e_assoc=row[r"$\varepsilon^{A_{i} B_{i}} k_{B}^{-1} / K$"],
                vol_a=row[r"$\boldsymbol{\kappa}^{A_{i} B_{i} /-}$"],
                assoc_scheme=assoc_scheme_from_sites(row.get(r"$N_{i}$")),
                mw=default_field(component, "MW"),
                source="Ascani2023 Table1",
            )
        )
    for row in read_dicts(PAPER_ROOT / "2023_ascani" / "tables" / "table_003" / "table_003.csv"):
        component = clean_component(row.get("Component", ""))
        if not component or not is_number(row.get(r"$m_{i}^{\text {seg }} /-$")):
            continue
        pure_rows.append(
            pure_record(
                component,
                m=row[r"$m_{i}^{\text {seg }} /-$"],
                s=row[r"$\sigma_{i} / \AA$"],
                e=row[
                    r"$\boldsymbol{u}_{\boldsymbol{i}} \boldsymbol{k}_{\boldsymbol{B}}^{\boldsymbol{-} \mathbf{1}} \boldsymbol{/} \boldsymbol{K}$"
                ],
                e_assoc=row[r"$\varepsilon^{A_{i} B_{i}} k_{B}^{-1} / K$"],
                vol_a=row[r"$\kappa^{A_{i} B_{i}} \boldsymbol{/}$"],
                assoc_scheme=assoc_scheme_from_sites(row.get(r"$N_{i}$")),
                mw=default_field(component, "MW"),
                source="Ascani2023 Table3",
            )
        )
    components = [row["component"] for row in pure_rows]
    k_values: dict[tuple[str, str], str] = {}
    source_rows: list[dict[str, str]] = [default_binary_source_row("l_ij"), default_binary_source_row("k_hb_ij")]
    for row in read_dicts(PAPER_ROOT / "2023_ascani" / "tables" / "table_002" / "table_002.csv"):
        left = clean_component(row.get("Component 1", ""))
        right = clean_component(row.get("Component 2", ""))
        if not left or not right:
            continue
        kij = temperature_adjusted_kij(
            row.get(r"$\boldsymbol{k}_{\boldsymbol{i j}, \mathbf{2 9 8 . 1 5}} \boldsymbol{/} \boldsymbol{-}$", ""),
            row.get(r"$k_{i j, T} / K$", ""),
        )
        add_symmetric(k_values, left, right, kij)
        source_rows.append(binary_source_row("k_ij", left, right, kij, "Ascani2023 Table2"))
    write_dataset(
        target,
        "2023_Ascani",
        {"any_solvent.csv": pure_rows},
        components,
        {"k_ij": k_values, "l_ij": {}, "k_hb_ij": {}},
        source_rows,
        {},
        [],
    )


def build_yu_2024(target: Path) -> None:
    pure_rows = [
        pure_record("H2O", m="1.2047", s=WATER_SIGMA_EXPR, e="353.95", e_assoc="2425.7", vol_a="0.0451", assoc_scheme="2B", source="Yu2024 Table2"),
        pure_record("TOP", m="4.2032", s="5.4506", e="280.4777", e_assoc="6393.5", vol_a="0.0001", assoc_scheme="2B", source="Yu2024 Table2"),
        pure_record(
            "[HOEMIM][Tf2N]",
            m="4.073",
            s="4.6432",
            e="434.6120",
            e_assoc="5000",
            vol_a="0.1",
            assoc_scheme="2B",
            source="Yu2024 Table2",
        ),
        pure_record("Li+", m="1", s="2.8449", e="360.00", e_assoc="0", vol_a="100", assoc_scheme="2B", source="Yu2024 Table2"),
        pure_record("Mg2+", m="1", s="3.1327", e="1500", e_assoc="0", vol_a="0", assoc_scheme="", source="Yu2024 Table2"),
        pure_record("Cl-", m="1", s="2.7560", e="170.00", e_assoc="0", vol_a="0", assoc_scheme="", source="Yu2024 Table2"),
    ]
    components = [row["component"] for row in pure_rows]
    k_values: dict[tuple[str, str], str] = {}
    khb_values: dict[tuple[str, str], str] = {}
    source_rows: list[dict[str, str]] = [default_binary_source_row("l_ij")]
    for left, right, kij, khb in (
        ("H2O", "[HOEMIM][Tf2N]", "0.007", "0"),
        ("Li+", "TOP", "0.3", "0.3"),
        ("H2O", "TOP", "1", "0"),
        ("Li+", "[HOEMIM][Tf2N]", "1", "1"),
        ("Li+", "H2O", "0", "1"),
        ("Li+", "Cl-", "0.669", "0"),
    ):
        add_symmetric(k_values, left, right, kij)
        source_rows.append(binary_source_row("k_ij", left, right, kij, "Yu2024 Table3"))
        if khb != "0":
            add_symmetric(khb_values, left, right, khb)
            source_rows.append(binary_source_row("k_hb_ij", left, right, khb, "Yu2024 Table3"))
    write_dataset(
        target,
        "2024_Yu",
        {"any_solvent.csv": pure_rows},
        components,
        {"k_ij": k_values, "l_ij": {}, "k_hb_ij": khb_values},
        source_rows,
        {},
        [],
    )


def build_rezaee_2026(target: Path) -> None:
    source_dir = PAPER_ROOT / "2026_rezaee" / "shared" / "source"
    pure_rows = [
        pure_record("H2O", m="1.2047", s=WATER_SIGMA_EXPR, e="353.95", e_assoc="2425.7", vol_a="0.04509", assoc_scheme="2B", source="Rezaee2026 aqueous context"),
        pure_record("Li+", m="1", s="2.8449", e="360.0", e_assoc="0", vol_a="0", assoc_scheme="", source="Rezaee2026 species manifest"),
        pure_record("Na+", m="1", s="2.41", e="646.1", e_assoc="0", vol_a="0", assoc_scheme="", source="Rezaee2026 species manifest"),
        pure_record("Cl-", m="1", s="3.06", e="47.3", e_assoc="0", vol_a="0", assoc_scheme="", source="Rezaee2026 species manifest"),
        pure_record("H+", m="1", s="1.0", e="100.0", e_assoc="0", vol_a="0", assoc_scheme="", source="Rezaee2026 species manifest"),
        pure_record("OH-", m="1", s="3.0", e="100.0", e_assoc="0", vol_a="0", assoc_scheme="", source="Rezaee2026 species manifest"),
        pure_record("NH4+", m="1", s="3.5740", e="230.0", e_assoc="0", vol_a="0", assoc_scheme="", source="Rezaee2026 species manifest"),
    ]
    for row in read_dicts(source_dir / "rezaee_2026_organic_pcsaft_parameters.csv"):
        component = clean_component(row["component"])
        pure_rows.append(
            pure_record(
                component,
                m=row["m"],
                s=row["sigma_A"],
                e=row["epsilon_over_k_K"],
                e_assoc=row["epsilon_assoc_over_k_K"],
                vol_a=row["kappa_assoc"],
                assoc_scheme=assoc_scheme_from_sites(row.get("association_sites")),
                source=row["source"],
            )
        )
    components = [row["component"] for row in pure_rows]
    k_values: dict[tuple[str, str], str] = {}
    source_rows: list[dict[str, str]] = [default_binary_source_row("l_ij"), default_binary_source_row("k_hb_ij")]
    for row in read_dicts(source_dir / "rezaee_2026_organic_binary_interactions.csv"):
        left = clean_component(row["component_i"])
        right = clean_component(row["component_j"])
        value = clean_scalar(row["kij"])
        add_symmetric(k_values, left, right, value)
        source_rows.append(binary_source_row("k_ij", left, right, value, row["source"]))
    write_dataset(
        target,
        "2026_Rezaee",
        {"any_solvent.csv": pure_rows},
        components,
        {"k_ij": k_values, "l_ij": {}, "k_hb_ij": {}},
        source_rows,
        {},
        [],
    )


def write_dataset(
    target: Path,
    dataset: str,
    pure_sets: Mapping[str, list[dict[str, str]]],
    components: list[str],
    matrix_values: Mapping[str, Mapping[tuple[str, str], str]],
    source_rows: list[dict[str, str]],
    user_options: Mapping[str, Any],
    rel_perm_files: Iterable[Path],
) -> None:
    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target_parent) as tmp:
        created = create_parameter_template(tmp, target.name, species=components)
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(created), target)
    pure_root = target / "pure"
    shutil.rmtree(pure_root)
    pure_root.mkdir()
    for filename, rows in pure_sets.items():
        write_dicts(pure_root / filename, PURE_COLUMNS, rows)

    binary_root = target / "mixed" / "binary_interaction"
    binary_root.mkdir(parents=True, exist_ok=True)
    for parameter, filename in BINARY_PARAMETER_FILES.items():
        write_matrix(binary_root / filename, components, matrix_values.get(parameter, {}))
    if not any(row["parameter"] == "k_ij" for row in source_rows):
        source_rows.append(default_binary_source_row("k_ij"))
    write_dicts(
        binary_root / "source_manifest.csv",
        ["parameter", "component_i", "component_j", "value", "source"],
        source_rows,
    )

    rel_perm_root = target / "mixed" / "rel_perm"
    if rel_perm_root.exists():
        shutil.rmtree(rel_perm_root)
    rel_perm_root.mkdir(parents=True)
    copied = False
    for rel_perm_file in rel_perm_files:
        shutil.copy2(rel_perm_file, rel_perm_root / rel_perm_file.name)
        copied = True
    if not copied:
        write_dicts(rel_perm_root / "parameters.csv", ["organic", "a", "b", "c"], [])

    (target / "user_options.json").write_text(json.dumps(user_options, indent=2) + "\n", encoding="utf-8")


def normalize_pure_row(row: Mapping[str, str], default_source: str) -> dict[str, str]:
    component = clean_component(row.get("component", ""))
    if not component:
        raise ValueError(f"pure row missing component in {default_source}")
    return pure_record(
        component,
        m=row.get("m", ""),
        s=row.get("s", ""),
        e=row.get("e", ""),
        e_assoc=row.get("e_assoc", ""),
        vol_a=row.get("vol_a", ""),
        assoc_scheme=row.get("assoc_scheme", ""),
        z=row.get("z", ""),
        dielc=row.get("dielc", ""),
        d_born=row.get("d_born", ""),
        f_solv=row.get("f_solv", ""),
        mw=row.get("MW", ""),
        source=row.get("source") or default_source,
    )


def pure_record(
    component: str,
    *,
    m: str,
    s: str,
    e: str,
    e_assoc: str = "0",
    vol_a: str = "0",
    assoc_scheme: str = "",
    z: str = "",
    dielc: str = "",
    d_born: str = "",
    f_solv: str = "",
    mw: str = "",
    mw_g: str = "",
    source: str,
) -> dict[str, str]:
    component = clean_component(component)
    if not component:
        raise ValueError(f"empty component for {source}")
    base = base_component(component)
    if is_placeholder_core(base, m, s, e, mw):
        m = s = e = e_assoc = vol_a = dielc = f_solv = mw = ""
    used_default_source = any(not clean_text(value) for value in (m, s, e, mw or mw_g))
    source_text = clean_text(source)
    if used_default_source and COMPONENT_DEFAULTS.get(base, {}).get("source"):
        source_text = f"{source_text}; {COMPONENT_DEFAULTS[base]['source']}"
    force_defaults = COMPONENT_DEFAULTS.get(base, {}).get("source", "") in source_text
    mw_value = clean_scalar(mw) if mw else (format_float(float(clean_scalar(mw_g)) / 1000.0) if mw_g else default_field(base, "MW"))
    e_assoc_value = clean_scalar(e_assoc, default=default_field(base, "e_assoc", "0"))
    vol_a_value = clean_scalar(vol_a, default=default_field(base, "vol_a", "0"))
    dielc_value = clean_scalar(dielc, default=default_field(base, "dielc"))
    f_solv_value = clean_scalar(f_solv, default=default_field(base, "f_solv"))
    if force_defaults:
        e_assoc_value = default_if_generic(base, "e_assoc", e_assoc_value, "0")
        vol_a_value = default_if_generic(base, "vol_a", vol_a_value, "0")
        dielc_value = default_if_generic(base, "dielc", dielc_value, "1")
        f_solv_value = default_if_generic(base, "f_solv", f_solv_value, "1")
    return {
        "component": component,
        "m": clean_scalar(m, default=default_field(base, "m", "1")),
        "s": clean_scalar(s, default=default_field(base, "s", "1")),
        "e": clean_scalar(e, default=default_field(base, "e", "0")),
        "e_assoc": e_assoc_value,
        "vol_a": vol_a_value,
        "assoc_scheme": clean_assoc_scheme(assoc_scheme or default_field(base, "assoc_scheme", "")),
        "z": clean_scalar(z, default=default_field(base, "z")),
        "dielc": dielc_value,
        "d_born": clean_scalar(d_born, default=default_field(base, "d_born")),
        "f_solv": f_solv_value,
        "MW": mw_value,
        "source": source_text,
    }


def default_field(component: str, field: str, default_value: str = "1") -> str:
    base = base_component(clean_component(component))
    if base in COMPONENT_DEFAULTS and field in COMPONENT_DEFAULTS[base]:
        return COMPONENT_DEFAULTS[base][field]
    if field == "z":
        if base.endswith("+"):
            return "1"
        if base.endswith("-"):
            return "-1"
        return "0"
    if field in {"d_born", "f_solv"}:
        return "0" if field == "d_born" else "1"
    if field == "dielc":
        return "1"
    if field == "MW":
        return "0.100"
    return default_value


def default_if_generic(component: str, field: str, value: str, generic: str) -> str:
    if value == generic and field in COMPONENT_DEFAULTS.get(component, {}):
        return COMPONENT_DEFAULTS[component][field]
    return value


def is_placeholder_core(component: str, m: str, s: str, e: str, mw: str) -> bool:
    defaults = COMPONENT_DEFAULTS.get(component)
    if not defaults or "m" not in defaults:
        return False
    return (
        clean_scalar(m, default="") == "1"
        and clean_scalar(s, default="") == "1"
        and clean_scalar(e, default="") == "0"
        and clean_scalar(mw, default="") in {"0.100", "0.1"}
    )


def base_component(component: str) -> str:
    for suffix in ("-2B", "-3B", "-4C"):
        if component.endswith(suffix):
            return component[: -len(suffix)]
    return component


def clean_component(raw: Any) -> str:
    text = clean_text(raw)
    if not text:
        return ""
    replacements = {
        r"$\mathrm{H}_{2} \mathrm{O}$": "H2O",
        r"$\mathrm{CO}_{2}$": "CO2",
        "Water": "H2O",
        "water": "H2O",
        "carbon dioxide": "CO2",
        r"$\mathrm{Li}^{+}$": "Li+",
        r"$\mathrm{Mg}^{2+}$": "Mg2+",
        r"$\mathrm{Cl}^{-}$": "Cl-",
        r"[HOEMIM][ $\mathrm{Tf}_{2} \mathrm{~N}$ ]": "[HOEMIM][Tf2N]",
        r"$[\mathrm{HOEMIM}]\left[\mathrm{Tf}_{2} \mathrm{~N}\right]$": "[HOEMIM][Tf2N]",
    }
    if text in replacements:
        return replacements[text]
    text = text.replace("$", "")
    text = text.replace(r"\left", "").replace(r"\right", "")
    text = text.replace(r"\mathrm", "")
    text = text.replace(r"\text", "")
    text = text.replace("{", "").replace("}", "")
    text = text.replace("~", "").replace("\\", "")
    text = text.replace("H_2 O", "H2O").replace("CO_2", "CO2")
    text = text.replace("^+", "+").replace("^-", "-").replace("^2+", "2+")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_text(raw: Any) -> str:
    return str(raw or "").strip()


def clean_assoc_scheme(raw: Any) -> str:
    text = clean_text(raw).replace("-", "")
    if text in {"", "0", "None", "Nonassociating", "nonassociating"}:
        return "" if text != "Nonassociating" else "Nonassociating"
    return text


def assoc_scheme_from_sites(raw: Any) -> str:
    value = clean_scalar(raw, default="0")
    try:
        sites = int(float(value))
    except ValueError:
        return ""
    return "2B" if sites > 0 else ""


def clean_scalar(raw: Any, default: str = "0") -> str:
    text = clean_text(raw)
    if not text or text in {"-", "dash", "nan", "NaN", "None", "*"}:
        return default
    if "=" in text:
        text = text.split("=")[-1].strip()
    if text == WATER_SIGMA_EXPR or "ln(T)" in text or re.search(r"\bT\b", text):
        return text.replace(" ", "")
    text = text.replace("$", "").replace(",", "")
    text = re.sub(r"\{ \}\^\{\\text \{[^}]+\}\}", "", text)
    text = re.sub(r"\^\{\\text \{[^}]+\}\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("{", "").replace("}", "").strip()
    if text in {"-", ""}:
        return default
    match = re.search(r"[+\-]?\d*\.?\d+(?:[eE][+\-]?\d+)?", text)
    return match.group(0) if match else default


def is_number(raw: Any) -> bool:
    try:
        float(clean_scalar(raw, default=""))
        return True
    except ValueError:
        return False


def format_float(value: float) -> str:
    return f"{value:.12g}"


def temperature_adjusted_kij(k298: Any, slope: Any) -> str:
    base = float(clean_scalar(k298))
    slope_text = clean_scalar(slope, default="0")
    slope_value = float(slope_text)
    if abs(slope_value) < 1.0e-15:
        return format_float(base)
    intercept = base - slope_value * 298.15
    return f"{format_float(slope_value)}*T{intercept:+.12g}"


def read_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_dicts(path: Path, fieldnames: list[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_matrix(path: Path, components: list[str], values: Mapping[tuple[str, str], str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["component", *components])
        for row_component in components:
            writer.writerow([row_component, *[values.get((row_component, col_component), "0") for col_component in components]])


def read_matrix(path: Path) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        columns = header[1:]
        for row in reader:
            if not row:
                continue
            component = clean_component(row[0])
            for column, value in zip(columns, row[1:]):
                values[(component, clean_component(column))] = clean_scalar(value)
    return values


def add_symmetric(values: dict[tuple[str, str], str], left: str, right: str, value: str) -> None:
    values[(left, right)] = value
    values[(right, left)] = value


def split_binary_system(system: str, components: Iterable[str]) -> tuple[str, str]:
    normalized_components = sorted({clean_component(item) for item in components if clean_component(item)}, key=len, reverse=True)
    system_text = clean_component(system)
    aliases = {"water": "H2O", "n-butane": "butane", "isobutanol": "2-methyl-2-butanol"}
    for left in normalized_components:
        prefix = f"{left}-"
        if system_text.startswith(prefix):
            right = aliases.get(system_text[len(prefix) :], system_text[len(prefix) :])
            left_alias = aliases.get(left, left)
            if right in normalized_components or right in aliases.values():
                return left_alias, right
    parts = system_text.split("-", 1)
    if len(parts) == 2:
        return aliases.get(parts[0], parts[0]), aliases.get(parts[1], parts[1])
    raise ValueError(f"cannot split binary system '{system}'")


def source_rows_for_matrix(parameter: str, values: Mapping[tuple[str, str], str], source: str) -> list[dict[str, str]]:
    rows = [default_binary_source_row(parameter)]
    seen: set[frozenset[str]] = set()
    for (left, right), value in sorted(values.items()):
        if left == right or clean_scalar(value) == "0":
            continue
        key = frozenset((left, right))
        if key in seen:
            continue
        seen.add(key)
        rows.append(binary_source_row(parameter, left, right, clean_scalar(value), source))
    return rows


def default_binary_source_row(parameter: str) -> dict[str, str]:
    return {
        "parameter": parameter,
        "component_i": "*",
        "component_j": "*",
        "value": "0",
        "source": "default zero for unpublished values",
    }


def binary_source_row(parameter: str, left: str, right: str, value: str, source: str) -> dict[str, str]:
    return {
        "parameter": parameter,
        "component_i": left,
        "component_j": right,
        "value": clean_scalar(value),
        "source": clean_text(source),
    }


def dedupe_pure_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        component = row["component"]
        if component in seen:
            continue
        seen.add(component)
        deduped.append(row)
    return deduped


if __name__ == "__main__":
    raise SystemExit(main())
