from __future__ import annotations

import csv
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import numpy as np

from epcsaft.state.native_adapter import ePCSAFTMixture

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NEUTRAL_TP_FLASH_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_tp_flash"
    / "hydrocarbon_workbook_flash"
)


def neutral_lle_synthetic_parameters() -> dict[str, np.ndarray]:
    return {
        "m": np.asarray([1.0, 2.0], dtype=float),
        "s": np.asarray([3.5, 4.0], dtype=float),
        "e": np.asarray([150.0, 250.0], dtype=float),
        "k_ij": np.asarray([[0.0, 0.5], [0.5, 0.0]], dtype=float),
    }


def neutral_lle_synthetic_mixture() -> ePCSAFTMixture:
    return ePCSAFTMixture.from_params(neutral_lle_synthetic_parameters(), species=["A", "B"])


def neutral_lle_synthetic_case() -> dict[str, object]:
    return {
        "case_label": "Synthetic neutral binary LLE phase-discovery case",
        "family_label": "PE-Neutral TP Flash",
        "route": "neutral_lle",
        "temperature": 225.0,
        "pressure": 1.0e6,
        "composition": [0.5, 0.5],
        "composition_role": "feed",
        "evidence_scope": "synthetic_neutral_lle_algorithm",
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def indexed_columns(row: dict[str, str], prefix: str) -> list[str]:
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    return sorted(
        [key for key in row if pattern.match(key) is not None],
        key=lambda item: int(pattern.match(item).group(1)),  # type: ignore[union-attr]
    )


def composition(row: dict[str, str]) -> list[float]:
    columns = indexed_columns(row, "x")
    if not columns:
        raise ValueError("phase split row does not define x1, x2, ... composition columns")
    return [float(row[column]) for column in columns]


def case_rows(case_dir: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(case_dir / "phase_splits.csv")
    case_keys = {row["case_key"] for row in rows}
    if len(case_keys) != 1:
        raise ValueError(f"neutral TP flash fixture expects exactly one case_key, got {sorted(case_keys)}")
    return {row["phase"]: row for row in rows}


def species(case_rows_by_phase: dict[str, dict[str, str]], metadata: dict[str, Any]) -> list[str]:
    if isinstance(metadata.get("species"), list) and metadata["species"]:
        return [str(item) for item in metadata["species"]]
    feed = case_rows_by_phase["feed"]
    return [feed[column] for column in indexed_columns(feed, "component_")]


def mixture(case_dir: Path, species_names: list[str]) -> ePCSAFTMixture:
    parameter_rows = {row["species"]: row for row in read_csv(case_dir / "pc_saft_parameters.csv")}
    if set(parameter_rows) != set(species_names):
        raise ValueError("pc_saft_parameters.csv species do not match phase_splits.csv species")
    index = {name: position for position, name in enumerate(species_names)}
    k_ij = np.zeros((len(species_names), len(species_names)), dtype=float)
    for row in read_csv(case_dir / "binary_interactions.csv"):
        i = index[row["component_i"]]
        j = index[row["component_j"]]
        value = float(row["k_ij"])
        k_ij[i, j] = value
        k_ij[j, i] = value
    return ePCSAFTMixture.from_params(
        {
            "m": np.asarray([float(parameter_rows[name]["m"]) for name in species_names], dtype=float),
            "s": np.asarray([float(parameter_rows[name]["s_A"]) for name in species_names], dtype=float),
            "e": np.asarray([float(parameter_rows[name]["e_over_k_K"]) for name in species_names], dtype=float),
            "k_ij": k_ij,
        },
        species=species_names,
    )


def material_balance_row(case_dir: Path) -> dict[str, str]:
    rows = read_csv(case_dir / "material_balance_check.csv")
    if len(rows) != 1:
        raise ValueError("neutral TP flash fixture expects exactly one material-balance check row")
    return rows[0]


def expected_phase_fractions(case_dir: Path) -> dict[str, float]:
    row = material_balance_row(case_dir)
    return {
        "vapor": float(row["vapor_fraction"]),
        "liquid": float(row["liquid_fraction"]),
    }


@contextmanager
def suppress_native_stdout():
    sys.stdout.flush()
    saved_stdout = os.dup(1)
    try:
        with tempfile.TemporaryFile(mode="w+b") as sink:
            os.dup2(sink.fileno(), 1)
            yield
            sys.stdout.flush()
    finally:
        os.dup2(saved_stdout, 1)
        os.close(saved_stdout)


@contextmanager
def redirect_native_stdout_to_stderr():
    sys.stdout.flush()
    sys.stderr.flush()
    saved_stdout = os.dup(1)
    try:
        os.dup2(2, 1)
        yield
        sys.stdout.flush()
    finally:
        os.dup2(saved_stdout, 1)
        os.close(saved_stdout)
