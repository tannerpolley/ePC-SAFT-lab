from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.run_topology_matrix import (
    DEFAULT_OUTPUT as TOPOLOGY_MATRIX,
)
from analyses.package_validation.explicit_association_toybox.scripts.run_topology_matrix import (
    run_topology_matrix,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "timing_pareto" / "output"
PARETO = OUTPUT / "timing_pareto.csv"


def main() -> None:
    if not TOPOLOGY_MATRIX.exists():
        run_topology_matrix(output_path=TOPOLOGY_MATRIX)
    with TOPOLOGY_MATRIX.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["closure"], []).append(row)
    pareto_rows = []
    for closure, closure_rows in sorted(grouped.items()):
        elapsed_values = [float(row["closure_elapsed_seconds"]) for row in closure_rows]
        error_values = [abs(float(row["assoc_helmholtz_rel_error"])) for row in closure_rows]
        pareto_rows.append(
            {
                "closure": closure,
                "comparison_role": closure_rows[0]["comparison_role"],
                "median_elapsed_seconds": statistics.median(elapsed_values),
                "max_abs_assoc_helmholtz_rel_error": max(error_values),
            }
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PARETO.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pareto_rows[0]))
        writer.writeheader()
        writer.writerows(pareto_rows)
    print(PARETO)


if __name__ == "__main__":
    main()
