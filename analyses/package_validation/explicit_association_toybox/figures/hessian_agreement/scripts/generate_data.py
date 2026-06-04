from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.hessian_agreement import (
    DEFAULT_OUTPUT,
    generate_hessian_agreement,
    load_committed_jax_rows,
)


def main() -> None:
    print(generate_hessian_agreement(DEFAULT_OUTPUT, jax_rows=load_committed_jax_rows()))


if __name__ == "__main__":
    main()
