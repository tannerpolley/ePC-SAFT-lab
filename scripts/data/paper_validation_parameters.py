"""Paths for analysis-owned paper-validation parameter bundles."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_VALIDATION_ROOT = REPO_ROOT / "analyses" / "paper_validation"

_DATASET_TO_PARAMETER_ROOT = {
    "2001_Gross": PAPER_VALIDATION_ROOT / "2001_gross" / "parameters",
    "2002_Gross": PAPER_VALIDATION_ROOT / "2002_gross" / "parameters",
    "2005_Cameretti": PAPER_VALIDATION_ROOT / "2005_cameretti" / "parameters",
    "2008_Held": PAPER_VALIDATION_ROOT / "2008_held" / "parameters",
    "2009_Held": PAPER_VALIDATION_ROOT
    / "2014_held"
    / "figures"
    / "figure_03"
    / "source"
    / "parameters_2009_held",
    "2012_Held": PAPER_VALIDATION_ROOT / "2012_held" / "parameters",
    "2014_Held": PAPER_VALIDATION_ROOT / "2014_held" / "parameters",
    "2015_Baygi": PAPER_VALIDATION_ROOT / "2015_baygi" / "parameters",
    "2019_Bulow": PAPER_VALIDATION_ROOT / "2019_bulow" / "parameters",
    "2020_Bulow": PAPER_VALIDATION_ROOT / "2020_bulow" / "parameters",
    "2021_Bulow": PAPER_VALIDATION_ROOT / "2021_bulow" / "parameters",
    "2022_Ascani": PAPER_VALIDATION_ROOT / "2022_ascani" / "parameters",
    "2023_Ascani": PAPER_VALIDATION_ROOT / "2023_ascani" / "parameters",
    "2024_Hubach": PAPER_VALIDATION_ROOT / "2024_hubach" / "parameters",
    "2024_Yu": PAPER_VALIDATION_ROOT / "2024_yu" / "parameters",
    "2025_Figiel": PAPER_VALIDATION_ROOT / "2025_figiel" / "parameters",
    "2026_Khudaida": PAPER_VALIDATION_ROOT / "2026_khudaida" / "parameters",
    "2026_Rezaee": PAPER_VALIDATION_ROOT / "2026_rezaee" / "parameters",
}


def paper_validation_parameter_path(dataset_name: str | Path) -> Path:
    """Return the local parameter-folder path for a paper-validation dataset id."""
    if isinstance(dataset_name, Path):
        return dataset_name
    try:
        return _DATASET_TO_PARAMETER_ROOT[str(dataset_name)]
    except KeyError as exc:
        raise KeyError(f"No paper-validation parameter bundle is registered for {dataset_name!r}") from exc
