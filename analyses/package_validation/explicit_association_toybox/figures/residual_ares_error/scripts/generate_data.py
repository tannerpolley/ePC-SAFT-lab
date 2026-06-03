from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.run_grid import run_grid

OUTPUT = ANALYSIS_ROOT / "figures" / "residual_ares_error" / "output" / "residual_ares_metrics.csv"


def main() -> None:
    output = run_grid(output_path=OUTPUT)
    print(output)


if __name__ == "__main__":
    main()
