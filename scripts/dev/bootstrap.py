from __future__ import annotations

import argparse
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
PROVIDER_BUILD_BACKEND_DIR = REPO_ROOT / "packages" / "epcsaft" / "build_backend"
if str(PROVIDER_BUILD_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(PROVIDER_BUILD_BACKEND_DIR))

from native_dependency_policy import (
    default_system_ceres_config_dir,
    resolve_default_linux_ipopt_root_with_source,
    resolve_default_system_ceres_config_dir,
    validate_ipopt_root,
)

from scripts.dev.native_runtime_env import ipopt_runtime_lib_dir

Command = tuple[str, ...]
SOURCE_DIRS = (
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
    REPO_ROOT / "packages" / "epcsaft-regression" / "src",
)

SYNC_COMMAND: Command = ("uv", "sync", "--no-install-workspace")
UV_RUN_PYTHON: Command = ("uv", "run", "--no-sync", "python")
CERES_BUILD_COMMAND: Command = (*UV_RUN_PYTHON, "scripts/dev/build_system_ceres.py", "--parallel", "2")
BASE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
)
PROVIDER_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-provider-native",
)
EQUILIBRIUM_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-equilibrium-native",
)
REGRESSION_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-regression-native",
)
FULL_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-extension-native",
)
VALIDATE_QUICK_COMMAND: Command = (*UV_RUN_PYTHON, "scripts/dev/validate_project.py", "quick")
VALIDATE_CONFIDENCE_COMMAND: Command = (*UV_RUN_PYTHON, "scripts/dev/validate_project.py", "confidence")
VALIDATE_DOCS_COMMAND: Command = (*UV_RUN_PYTHON, "scripts/dev/validate_project.py", "docs")
BUILD_DIST_COMMAND: Command = (*UV_RUN_PYTHON, "scripts/dev/build_dist.py")
NEXT_COMMAND = "uv run --no-sync python scripts/dev/validate_project.py quick"
IPOPT_CHANGE_COMMAND = 'export EPCSAFT_IPOPT_ROOT="/path/to/ipopt"'
BOOTSTRAP_CURRENT_STATE = "bootstrap_state: current"
SETUP_COMMAND_SUMMARY = (
    "uv sync --no-install-workspace",
    "uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2",
    "uv run --no-sync python scripts/dev/build_epcsaft.py",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-provider-native",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-equilibrium-native",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-regression-native",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native",
    NEXT_COMMAND,
)


def _format_command(command: Command) -> str:
    return " ".join(str(part) for part in command)


def _prepend_env_path(env: dict[str, str], name: str, path: Path) -> None:
    entry = str(path.resolve())
    normalized_entry = os.path.normcase(os.path.normpath(entry))
    current = [part for part in env.get(name, "").split(os.pathsep) if part]
    kept = [part for part in current if os.path.normcase(os.path.normpath(part)) != normalized_entry]
    env[name] = os.pathsep.join([entry, *kept])


def _bootstrap_env() -> dict[str, str]:
    env = os.environ.copy()
    for src_dir in SOURCE_DIRS:
        _prepend_env_path(env, "PYTHONPATH", src_dir)
    explicit_name = next(
        (name for name in ("EPCSAFT_IPOPT_ROOT", "EPCSAFT_PEP517_IPOPT_ROOT") if env.get(name)),
        None,
    )
    if explicit_name is not None:
        ipopt_root = validate_ipopt_root(env[explicit_name], env_name=explicit_name)
        ipopt_root_source = f"environment:{explicit_name}"
    else:
        ipopt_resolution = resolve_default_linux_ipopt_root_with_source()
        ipopt_root = ipopt_resolution.root
        ipopt_root_source = ipopt_resolution.source

    print(f"ipopt_root: {ipopt_root if ipopt_root else '<missing>'}", flush=True)
    print(f"ipopt_root_source: {ipopt_root_source}", flush=True)
    print(f"ipopt_change_command: {IPOPT_CHANGE_COMMAND}", flush=True)
    if ipopt_root is not None:
        env["EPCSAFT_IPOPT_ROOT"] = str(ipopt_root)
        ipopt_lib = ipopt_runtime_lib_dir(ipopt_root)
        if ipopt_lib is not None:
            _prepend_env_path(env, "LD_LIBRARY_PATH", ipopt_lib)
            print(f"ipopt_runtime_lib_dir: {ipopt_lib}", flush=True)
    return env


def _install_workspace_source_pth() -> None:
    site_packages = Path(sysconfig.get_paths()["purelib"])
    site_packages.mkdir(parents=True, exist_ok=True)
    pth_path = site_packages / "epcsaft_workspace_sources.pth"
    content = "".join(f"{src_dir}\n" for src_dir in SOURCE_DIRS)
    if pth_path.exists() and pth_path.read_text(encoding="utf-8", errors="replace") == content:
        print(f"workspace_source_pth: current {pth_path}", flush=True)
        return
    pth_path.write_text(content, encoding="utf-8")
    print(f"workspace_source_pth: wrote {pth_path}", flush=True)


def _run(command: Command, *, dry_run: bool, env: dict[str, str]) -> int:
    print("Running:", _format_command(command), flush=True)
    if dry_run:
        return 0
    completed = subprocess.run(command, cwd=REPO_ROOT, env=env, check=False)
    return int(completed.returncode)


def _ensure_ceres(*, dry_run: bool, env: dict[str, str]) -> tuple[int, Path]:
    ceres_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)
    if ceres_dir is not None:
        print(f"ceres_dir: {ceres_dir}", flush=True)
        return 0, ceres_dir

    exit_code = _run(CERES_BUILD_COMMAND, dry_run=dry_run, env=env)
    if exit_code != 0:
        return exit_code, default_system_ceres_config_dir(REPO_ROOT)
    if dry_run:
        return 0, default_system_ceres_config_dir(REPO_ROOT)

    ceres_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)
    if ceres_dir is None:
        print("bootstrap_state: failed", flush=True)
        print("failed_command: uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2", flush=True)
        print(
            "failure_reason: reusable Ceres build did not produce CeresConfig.cmake under build/system-ceres/2.2.0",
            flush=True,
        )
        return 1, default_system_ceres_config_dir(REPO_ROOT)
    print(f"ceres_dir: {ceres_dir}", flush=True)
    return 0, ceres_dir


def _native_build_command(ceres_dir: Path) -> Command:
    return (
        *UV_RUN_PYTHON,
        "scripts/dev/build_epcsaft.py",
        "--use-system-ceres",
        "--ceres-dir",
        str(ceres_dir),
    )


def _profile_build_command(profile: str) -> Command:
    return (*UV_RUN_PYTHON, "scripts/dev/build_epcsaft.py", "--clean", "--profile", profile)


def _provider_native_build_command() -> Command:
    return (*UV_RUN_PYTHON, "scripts/dev/build_epcsaft.py", "--clean", "--profile", "provider")


def _regression_native_build_command(ceres_dir: Path) -> Command:
    return (
        *UV_RUN_PYTHON,
        "scripts/dev/build_epcsaft.py",
        "--clean",
        "--profile",
        "regression",
        "--use-system-ceres",
        "--ceres-dir",
        str(ceres_dir),
    )


def _run_commands(commands: tuple[Command, ...], *, dry_run: bool, env: dict[str, str]) -> int:
    for command in commands:
        exit_code = _run(command, dry_run=dry_run, env=env)
        if exit_code != 0:
            print("bootstrap_state: failed", flush=True)
            print(f"failed_command: {_format_command(command)}", flush=True)
            print(f"next_command: {_format_command(command)}", flush=True)
            return exit_code
    return 0


def _run_build(*, dry_run: bool, env: dict[str, str]) -> int:
    exit_code, ceres_dir = _ensure_ceres(dry_run=dry_run, env=env)
    if exit_code != 0:
        return exit_code
    return _run_commands((_native_build_command(ceres_dir),), dry_run=dry_run, env=env)


def _run_regression_native(*, dry_run: bool, env: dict[str, str]) -> int:
    exit_code, ceres_dir = _ensure_ceres(dry_run=dry_run, env=env)
    if exit_code != 0:
        return exit_code
    return _run_commands(
        (_regression_native_build_command(ceres_dir), REGRESSION_NATIVE_DOCTOR_COMMAND),
        dry_run=dry_run,
        env=env,
    )


def _run_step(step: str, *, dry_run: bool, env: dict[str, str]) -> int:
    if step == "smoke":
        return _run_commands((BASE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "sync":
        return _run_commands((SYNC_COMMAND,), dry_run=dry_run, env=env)
    if step == "build":
        return _run_build(dry_run=dry_run, env=env)
    if step == "doctor":
        return _run_commands((BASE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "validate-quick":
        return _run_commands((VALIDATE_QUICK_COMMAND,), dry_run=dry_run, env=env)
    if step == "validate-confidence":
        return _run_commands((VALIDATE_CONFIDENCE_COMMAND,), dry_run=dry_run, env=env)
    if step == "validate-docs":
        return _run_commands((VALIDATE_DOCS_COMMAND,), dry_run=dry_run, env=env)
    if step == "build-dist":
        return _run_commands((BUILD_DIST_COMMAND,), dry_run=dry_run, env=env)
    if step == "provider-native":
        return _run_commands(
            (_provider_native_build_command(), PROVIDER_NATIVE_DOCTOR_COMMAND),
            dry_run=dry_run,
            env=env,
        )
    if step == "equilibrium-native":
        return _run_commands(
            (_profile_build_command("equilibrium"), EQUILIBRIUM_NATIVE_DOCTOR_COMMAND),
            dry_run=dry_run,
            env=env,
        )
    if step == "regression-native":
        return _run_regression_native(dry_run=dry_run, env=env)
    if step == "full-native":
        exit_code = _run_build(dry_run=dry_run, env=env)
        if exit_code != 0:
            return exit_code
        return _run_commands((FULL_NATIVE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "doctorfull":
        return _run_commands((FULL_NATIVE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "setup":
        return _run_step("full-native", dry_run=dry_run, env=env)
    raise AssertionError(f"unknown bootstrap step: {step}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap a source checkout through sync, native build, and doctor diagnostics.",
    )
    parser.add_argument(
        "--step",
        choices=(
            "setup",
            "smoke",
            "sync",
            "build",
            "doctor",
            "validate-quick",
            "validate-confidence",
            "validate-docs",
            "build-dist",
            "provider-native",
            "equilibrium-native",
            "regression-native",
            "full-native",
            "providernative",
            "equilibriumnative",
            "regressionnative",
            "fullnative",
            "doctorfull",
            "validatequick",
            "validateconfidence",
            "validatedocs",
            "builddist",
        ),
        default="setup",
        help="Run one bootstrap step instead of the full setup sequence.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would run without executing them.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    env = _bootstrap_env()
    step_aliases = {
        "providernative": "provider-native",
        "equilibriumnative": "equilibrium-native",
        "regressionnative": "regression-native",
        "fullnative": "full-native",
        "validatequick": "validate-quick",
        "validateconfidence": "validate-confidence",
        "validatedocs": "validate-docs",
        "builddist": "build-dist",
    }
    step = step_aliases.get(args.step, args.step)
    if not args.dry_run and step != "sync":
        _install_workspace_source_pth()
    exit_code = _run_step(step, dry_run=args.dry_run, env=env)
    if exit_code != 0:
        return exit_code
    if not args.dry_run:
        _install_workspace_source_pth()
    state = "bootstrap_state: dry-run" if args.dry_run else BOOTSTRAP_CURRENT_STATE
    print(state, flush=True)
    print(f"next_command: {NEXT_COMMAND}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
