from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_evidence import (
    generate_picard_stress_report,
)


def main() -> None:
    print(generate_picard_stress_report(repeat_count=1))


if __name__ == "__main__":
    main()
