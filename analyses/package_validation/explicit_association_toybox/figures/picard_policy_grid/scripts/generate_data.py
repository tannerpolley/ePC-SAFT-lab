from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.picard_policy_grid import (
    DEFAULT_HANDOFF,
    DEFAULT_OUTPUT,
    generate_picard_policy_grid,
)

if __name__ == "__main__":
    print(generate_picard_policy_grid(output_path=DEFAULT_OUTPUT, handoff_path=DEFAULT_HANDOFF))
