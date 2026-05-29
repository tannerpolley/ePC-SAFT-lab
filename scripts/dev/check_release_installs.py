from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROOT = REPO_ROOT / "build" / "release-install-proof"
DEFAULT_COMBINATIONS: tuple[tuple[str, ...], ...] = (
    ("epcsaft",),
    ("epcsaft", "epcsaft-equilibrium"),
    ("epcsaft", "epcsaft-regression"),
    ("epcsaft", "epcsaft-equilibrium", "epcsaft-regression"),
)
IMPORTS_BY_DISTRIBUTION = {
    "epcsaft": ("epcsaft", "epcsaft._core"),
    "epcsaft-equilibrium": ("epcsaft_equilibrium", "epcsaft_equilibrium._native_core"),
    "epcsaft-regression": ("epcsaft_regression", "epcsaft_regression._native_core"),
}
ARTIFACT_PREFIXES = {
    "epcsaft": ("epcsaft-",),
    "epcsaft-equilibrium": ("epcsaft_equilibrium-",),
    "epcsaft-regression": ("epcsaft_regression-",),
}


def _env() -> dict[str, str]:
    temp_root = BUILD_ROOT / "temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    env["EPCSAFT_SANDBOX_SAFE_TEMPFILE"] = "1"
    return env


def _has_artifact(dist_dir: Path, distribution: str) -> bool:
    prefixes = ARTIFACT_PREFIXES[distribution]
    return any(
        path.is_file()
        for path in dist_dir.iterdir()
        if path.suffix.lower() in {".whl", ".gz"} and path.name.startswith(prefixes)
    )


def _assert_artifacts(dist_dir: Path, distributions: tuple[str, ...]) -> None:
    missing = [distribution for distribution in distributions if not _has_artifact(dist_dir, distribution)]
    if missing:
        raise RuntimeError(
            "release install proof requires built dist artifacts for: "
            + ", ".join(missing)
            + f". Build them into {dist_dir} first."
        )


def _run(command: list[str], *, env: dict[str, str]) -> None:
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPO_ROOT, env=env, check=True)


def _smoke_code(target: Path, distributions: tuple[str, ...]) -> str:
    import_lines: list[str] = []
    for distribution in distributions:
        import_lines.extend(f"import {module}" for module in IMPORTS_BY_DISTRIBUTION[distribution])
    return f"""
import sys
sys.path.insert(0, {str(target)!r})
{chr(10).join(import_lines)}
import epcsaft
sdk = epcsaft.provider_native_sdk()
assert sdk["contract_id"] == "provider_native_sdk_v1"
assert sdk["provider_only_core"] is True
print("release install smoke ok: {' '.join(distributions)}")
"""


def _prove_combination(dist_dir: Path, distributions: tuple[str, ...], env: dict[str, str]) -> None:
    _assert_artifacts(dist_dir, distributions)
    target = BUILD_ROOT / ("target-" + "-".join(distributions))
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "uv",
            "pip",
            "install",
            "--target",
            str(target),
            "--no-index",
            "--find-links",
            str(dist_dir.resolve()),
            "--no-deps",
            *distributions,
        ],
        env=env,
    )
    _run([sys.executable, "-c", _smoke_code(target, distributions)], env=env)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prove local release artifacts install in supported provider/extension combinations.",
    )
    parser.add_argument("--dist-dir", type=Path, default=REPO_ROOT / "dist")
    parser.add_argument(
        "--combination",
        choices=("provider", "equilibrium", "regression", "all"),
        action="append",
        help="Limit proof to one or more named combinations. Defaults to all combinations.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    dist_dir = args.dist_dir.expanduser().resolve()
    if not dist_dir.is_dir():
        raise RuntimeError(f"dist directory does not exist: {dist_dir}")
    selected = args.combination or ["provider", "equilibrium", "regression", "all"]
    combination_map = {
        "provider": DEFAULT_COMBINATIONS[0],
        "equilibrium": DEFAULT_COMBINATIONS[1],
        "regression": DEFAULT_COMBINATIONS[2],
        "all": DEFAULT_COMBINATIONS[3],
    }
    env = _env()
    for name in selected:
        _prove_combination(dist_dir, combination_map[name], env)
    print("release_install_proof: current", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
