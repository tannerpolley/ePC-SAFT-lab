from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from analyses.package_validation.explicit_association_toybox.scripts.run_grid import DEFAULT_OUTPUT
else:
    from .run_grid import DEFAULT_OUTPUT


def summarize(path: Path = DEFAULT_OUTPUT) -> dict[str, int]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return dict(Counter(row["evidence_band"] for row in rows))


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize explicit association closure evidence bands.")
    parser.add_argument("--input", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for band, count in sorted(summarize(args.input).items()):
        print(f"{band}: {count}")


if __name__ == "__main__":
    main()
