from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from analyses.package_validation.explicit_association_toybox.scripts.run_grid import DEFAULT_OUTPUT
else:
    from .run_grid import DEFAULT_OUTPUT


def summarize(path: Path = DEFAULT_OUTPUT) -> dict[str, int]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return dict(Counter(row["evidence_band"] for row in rows))


def summarize_rows(path: Path = DEFAULT_OUTPUT) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["closure"], []).append(row)
    summaries: list[dict[str, object]] = []
    for closure, closure_rows in sorted(grouped.items()):
        summaries.append(
            {
                "closure": closure,
                "row_count": len(closure_rows),
                "evidence_band_counts": _band_counts(closure_rows),
                "max_ares_hc": _max_float(closure_rows, "ares_hc"),
                "max_ares_disp": _max_float(closure_rows, "ares_disp"),
                "max_ares_total_abs_error": _max_float(closure_rows, "ares_total_abs_error"),
                "max_ares_total_rel_error": _max_float(closure_rows, "ares_total_rel_error"),
            }
        )
    return summaries


def _band_counts(rows: Iterable[dict[str, str]]) -> str:
    counts = Counter(row["evidence_band"] for row in rows)
    return ";".join(f"{band}:{count}" for band, count in sorted(counts.items()))


def _max_float(rows: Iterable[dict[str, str]], key: str) -> float:
    values = [abs(float(row[key])) for row in rows if key in row and str(row[key]).strip()]
    if not values:
        return float("nan")
    return max(values)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize explicit association closure evidence bands.")
    parser.add_argument("--input", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for band, count in sorted(summarize(args.input).items()):
        print(f"{band}: {count}")


if __name__ == "__main__":
    main()
