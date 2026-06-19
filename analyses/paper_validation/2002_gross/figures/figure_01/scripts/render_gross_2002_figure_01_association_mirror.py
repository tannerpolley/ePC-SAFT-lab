from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validation import check_gross_2002_association_acceptance as campaign


def main() -> int:
    campaign.render_figure("figure_01")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
