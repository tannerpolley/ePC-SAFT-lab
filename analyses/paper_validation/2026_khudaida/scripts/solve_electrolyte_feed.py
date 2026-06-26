from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import _common as common


def main() -> None:
    payload = json.loads(sys.stdin.read())
    result = common._solve_formula_feed_direct(
        float(payload["temperature_K"]),
        np.asarray(payload["feed_formula"], dtype=float),
    )
    print(json.dumps(common._json_ready_solve_result(result), sort_keys=True))


if __name__ == "__main__":
    main()
