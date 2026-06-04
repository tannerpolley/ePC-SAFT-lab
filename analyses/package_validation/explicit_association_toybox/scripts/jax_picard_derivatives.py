from __future__ import annotations

import argparse
import csv
import json
import subprocess
from functools import lru_cache
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "jax_picard_derivatives" / "output" / "jax_picard_derivatives.csv"
BACKEND_MODULE = "analyses.package_validation.explicit_association_toybox.scripts.jax_picard_autodiff_backend"


def run_jax_picard_derivative_cases() -> list[dict[str, object]]:
    return [dict(row) for row in _backend_rows()]


def generate_jax_picard_derivatives(output_path: Path = DEFAULT_OUTPUT) -> Path:
    rows = run_jax_picard_derivative_cases()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


@lru_cache(maxsize=1)
def _backend_rows() -> tuple[dict[str, object], ...]:
    command = [
        "uv",
        "run",
        "--group",
        "autodiff",
        "python",
        "-m",
        BACKEND_MODULE,
        "--json",
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError("JAX autodiff backend returned no rows.")
    return tuple(json.loads(stdout))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate JAX Picard derivative comparison diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_jax_picard_derivatives(args.output))


if __name__ == "__main__":
    main()
