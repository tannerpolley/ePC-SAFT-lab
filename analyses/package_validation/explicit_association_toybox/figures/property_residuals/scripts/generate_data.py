from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.fixed_state_property_residuals import (
    DEFAULT_OUTPUT,
    generate_property_residuals,
)


def main() -> None:
    output = generate_property_residuals(output_path=DEFAULT_OUTPUT)
    print(output)


if __name__ == "__main__":
    main()
