from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.equilibrium_style_objective_sensitivity import (
    generate_objective_sensitivity,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "equilibrium_relevance_probe" / "output"
RAW_OUTPUT = OUTPUT / "equilibrium_relevance_probe.csv"


def main() -> None:
    print(generate_objective_sensitivity(RAW_OUTPUT))


if __name__ == "__main__":
    main()
