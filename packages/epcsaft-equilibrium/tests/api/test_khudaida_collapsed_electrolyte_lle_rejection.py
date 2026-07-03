from __future__ import annotations

import csv
import math
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
FIGURE_ROOT = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2026_khudaida"
    / "figures"
    / "figure_02"
)
MODEL_TIELINES = FIGURE_ROOT / "results" / "data" / "model_tielines.csv"

KHUDAIDA_MIN_PHASE_DISTANCE = 1.0e-3
KHUDAIDA_MINOR_BETA_REVIEW = 1.0e-4
FORMULA_COMPONENTS = ("x_water", "x_ethanol", "x_isobutanol", "x_nacl")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "pass", "passed"}


def _finite_float(value: str) -> float:
    parsed = float(value)
    assert math.isfinite(parsed)
    return parsed


def _component_distance(first: dict[str, str], second: dict[str, str]) -> float:
    return max(abs(_finite_float(first[name]) - _finite_float(second[name])) for name in FORMULA_COMPONENTS)


def test_khudaida_figure_02_rejects_accepted_collapsed_public_lle_rows() -> None:
    rows = _rows(MODEL_TIELINES)
    by_tie: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_tie.setdefault(row["tie_line"], []).append(row)

    collapsed: list[str] = []
    trace_beta_ties: list[str] = []
    for tie_line, tie_rows in sorted(by_tie.items(), key=lambda item: int(item[0])):
        if {row["phase"] for row in tie_rows} != {"organic", "aqueous"}:
            continue
        if not all(_truthy(row["converged"]) and row["status"] == "accepted" for row in tie_rows):
            continue

        organic = next(row for row in tie_rows if row["phase"] == "organic")
        aqueous = next(row for row in tie_rows if row["phase"] == "aqueous")
        phase_distance = _finite_float(organic["phase_distance"])
        component_distance = _component_distance(organic, aqueous)
        if phase_distance < KHUDAIDA_MIN_PHASE_DISTANCE or component_distance < KHUDAIDA_MIN_PHASE_DISTANCE:
            collapsed.append(tie_line)

        minor_beta = min(_finite_float(row["beta"]) for row in tie_rows)
        if minor_beta < KHUDAIDA_MINOR_BETA_REVIEW:
            trace_beta_ties.append(tie_line)

    assert not collapsed, f"accepted Khudaida Figure 2 rows are collapsed: {collapsed}"
    assert not trace_beta_ties, f"accepted Khudaida Figure 2 rows have trace minor phase fractions: {trace_beta_ties}"
