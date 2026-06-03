from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.run_topology_matrix import run_topology_matrix

OUTPUT = ANALYSIS_ROOT / "figures" / "topology_error_heatmaps" / "output"
HEATMAP = OUTPUT / "topology_error_heatmap.csv"


def main() -> None:
    output = run_topology_matrix(output_path=HEATMAP)
    print(output)


if __name__ == "__main__":
    main()
