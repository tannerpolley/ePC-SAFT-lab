import argparse
import os
import shutil
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft.runtime.capability_evidence import TEST_SLICES, registry_targets

GENERIC_TEST_TARGETS = registry_targets("generic")
FAST_TEST_TARGETS = GENERIC_TEST_TARGETS
CONFIDENCE_TEST_TARGETS = registry_targets("confidence")
EQUILIBRIUM_CONFIDENCE_TEST_TARGETS = registry_targets("equilibrium-confidence")
EQUILIBRIUM_API_TEST_TARGETS = registry_targets("equilibrium-api")
ALL_TEST_TARGETS = registry_targets("all")
RUNTIME_TEST_TARGETS = registry_targets("runtime")
API_TEST_TARGETS = registry_targets("api")
NATIVE_TEST_TARGETS = registry_targets("native")
NATIVE_CONTRACT_TEST_TARGETS = registry_targets("native-contracts")
SLICE_TARGETS = {name: registry_targets(name) for name in TEST_SLICES}
PREDEFINED_TARGETS = {
    "all_tests": ALL_TEST_TARGETS,
    "confidence": CONFIDENCE_TEST_TARGETS,
    "equilibrium_confidence": EQUILIBRIUM_CONFIDENCE_TEST_TARGETS,
    "equilibrium_api": EQUILIBRIUM_API_TEST_TARGETS,
    "generic": GENERIC_TEST_TARGETS,
    "runtime": RUNTIME_TEST_TARGETS,
    "api": API_TEST_TARGETS,
    "native": NATIVE_TEST_TARGETS,
    "native_contracts": NATIVE_CONTRACT_TEST_TARGETS,
}
LONG_NATIVE_TARGETS = {
    "tests/native/equilibrium",
}
LONG_EQUILIBRIUM_ROUTE_TARGETS = {
    "tests/api/frontend/test_equilibrium.py",
    "tests/native/equilibrium/results",
    "tests/native/equilibrium/results/test_neutral_vle_reference_values.py",
    "tests/native/equilibrium/results/test_neutral_lle_reference_values.py",
}
EQUILIBRIUM_DEBUG_TARGET_PREFIXES = (
    "tests/api/frontend/test_equilibrium.py",
    "tests/native/equilibrium/",
)
LONG_NATIVE_TARGETS_NOTE = (
    "Broad native equilibrium route-builder targets are intentionally guarded because they can take a long time. "
    "Use `uv run python run_pytest.py --native-contracts -q` for metadata/result-contract checks, "
    "or target a single test node. Pass `--allow-long-native-tests` only when you intentionally need the broad route suite."
)
LONG_EQUILIBRIUM_ROUTE_TARGETS_NOTE = (
    "Broad equilibrium route-solve/result targets are intentionally guarded because they can run multiple Ipopt or TPD solves. "
    "Use `uv run python run_pytest.py --equilibrium-confidence -q -s` for the focused convergence fixture, "
    "or target a single test node. Pass `--allow-long-equilibrium-tests` only when you intentionally need the broad file."
)
PYTEST_OPTIONS_WITH_SEPARATE_VALUE = {
    "-k",
    "-m",
    "--basetemp",
    "--capture",
    "--color",
    "--cov",
    "--cov-report",
    "--deselect",
    "--ignore",
    "--ignore-glob",
    "--junit-xml",
    "--log-cli-level",
    "--log-file",
    "--log-file-level",
    "--maxfail",
    "--rootdir",
    "--tb",
}
SLICE_SELECTION_NOTE = (
    "Slice flags are mutually exclusive. Developers should normally start with "
    "`uv run python scripts/dev/validate_project.py quick` or `uv run python run_pytest.py -q`. "
    "Use `--all` only when you explicitly need every retained pytest contract. "
    "Extra positional pytest targets after a slice are appended and will run in addition to that slice. "
    "Use `--equilibrium-debug -s` only with one explicit equilibrium test node."
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _pytest_temp(repo_root: Path) -> Path:
    configured_root = os.environ.get("EPCSAFT_PYTEST_TEMP_ROOT")
    if configured_root is not None:
        root = Path(configured_root).expanduser()
        if not root.is_absolute():
            root = (repo_root / root).resolve()
        root = root / "pytest-temp"
    else:
        root = repo_root / "build" / "pytest-temp"

    path = root / f"run-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _pytest_env(pytest_temp: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["TMP"] = str(pytest_temp.resolve())
    env["TEMP"] = str(pytest_temp.resolve())
    env["TMPDIR"] = str(pytest_temp.resolve())
    try:
        from scripts.dev.native_runtime_env import apply_native_runtime_env
    except ModuleNotFoundError:
        apply_native_runtime_env = None
    if apply_native_runtime_env is not None:
        apply_native_runtime_env(env)
    return env


def _apply_equilibrium_debug_env(env: dict[str, str], enabled: bool) -> None:
    if enabled:
        env["EPCSAFT_EQUILIBRIUM_DEBUG"] = "1"


def _pytest_args(
    pytest_args: list[str],
    pytest_temp: Path,
    generic: bool = False,
    confidence: bool = False,
    equilibrium_confidence: bool = False,
    equilibrium_api: bool = False,
    runtime: bool = False,
    api: bool = False,
    native: bool = False,
    native_contracts: bool = False,
    all_tests: bool = False,
    allow_long_native_tests: bool = False,
    allow_long_equilibrium_tests: bool = False,
    equilibrium_debug: bool = False,
) -> list[str]:
    (
        generic,
        confidence,
        equilibrium_confidence,
        equilibrium_api,
        runtime,
        api,
        native,
        native_contracts,
        all_tests,
    ) = _normalize_equilibrium_debug_selection(
        pytest_args,
        generic=generic,
        confidence=confidence,
        equilibrium_confidence=equilibrium_confidence,
        equilibrium_api=equilibrium_api,
        runtime=runtime,
        api=api,
        native=native,
        native_contracts=native_contracts,
        all_tests=all_tests,
        equilibrium_debug=equilibrium_debug,
    )
    _reject_unbounded_native_targets(
        pytest_args,
        all_tests=all_tests,
        allow_long_native_tests=allow_long_native_tests,
    )
    _reject_unbounded_equilibrium_route_targets(
        pytest_args,
        all_tests=all_tests,
        allow_long_equilibrium_tests=allow_long_equilibrium_tests,
    )
    selected_targets = _selected_predefined_targets(
        generic=generic,
        confidence=confidence,
        equilibrium_confidence=equilibrium_confidence,
        equilibrium_api=equilibrium_api,
        runtime=runtime,
        api=api,
        native=native,
        native_contracts=native_contracts,
        all_tests=all_tests,
    )
    cmd: list[str] = list(selected_targets)
    if selected_targets:
        cmd.extend(pytest_args)
    else:
        has_positional_target = any(not arg.startswith("-") for arg in pytest_args)
        if has_positional_target:
            cmd.extend(pytest_args)
        else:
            cmd.extend(FAST_TEST_TARGETS)
            cmd.extend(pytest_args)

    if not any(arg == "--basetemp" or arg.startswith("--basetemp=") for arg in cmd):
        cmd.extend(["--basetemp", str(pytest_temp)])
    return cmd


def _selected_predefined_targets(**flags: bool) -> tuple[str, ...]:
    selected = [name for name, enabled in flags.items() if enabled]
    if len(selected) > 1:
        raise ValueError(f"pytest slice flags must be mutually exclusive; got {selected}.")
    if not selected:
        return ()
    return PREDEFINED_TARGETS[selected[0]]


def _positional_targets(pytest_args: list[str]) -> list[str]:
    targets: list[str] = []
    skip_next = False
    after_separator = False
    for arg in pytest_args:
        if skip_next:
            skip_next = False
            continue
        if after_separator:
            targets.append(arg)
            continue
        if arg == "--":
            after_separator = True
            continue
        if arg.startswith("-"):
            option = arg.split("=", 1)[0]
            if "=" not in arg and option in PYTEST_OPTIONS_WITH_SEPARATE_VALUE:
                skip_next = True
            continue
        targets.append(arg)
    return targets


def _normalize_equilibrium_debug_selection(
    pytest_args: list[str],
    *,
    generic: bool,
    confidence: bool,
    equilibrium_confidence: bool,
    equilibrium_api: bool,
    runtime: bool,
    api: bool,
    native: bool,
    native_contracts: bool,
    all_tests: bool,
    equilibrium_debug: bool,
) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool]:
    if not equilibrium_debug:
        return (
            generic,
            confidence,
            equilibrium_confidence,
            equilibrium_api,
            runtime,
            api,
            native,
            native_contracts,
            all_tests,
        )
    if (
        generic
        or confidence
        or equilibrium_confidence
        or equilibrium_api
        or runtime
        or api
        or native
        or native_contracts
        or all_tests
    ):
        raise SystemExit(
            "--equilibrium-debug requires one explicit equilibrium test node; do not use it with pytest slices."
        )
    positional_targets = _positional_targets(pytest_args)
    if not positional_targets:
        raise SystemExit(
            "--equilibrium-debug requires one explicit equilibrium test node. "
            "Do not run debug mode without a bounded target."
        )
    _validate_equilibrium_debug_targets(positional_targets)
    return (
        generic,
        confidence,
        equilibrium_confidence,
        equilibrium_api,
        runtime,
        api,
        native,
        native_contracts,
        all_tests,
    )


def _validate_equilibrium_debug_targets(positional_targets: list[str]) -> None:
    if len(positional_targets) != 1:
        raise SystemExit(
            "--equilibrium-debug accepts exactly one explicit equilibrium test node."
        )
    target = positional_targets[0].replace("\\", "/")
    target_path = target.split("::", 1)[0].rstrip("/")
    if "::" not in target:
        raise SystemExit(
            "--equilibrium-debug explicit targets must name one test node with `::`; broad files and directories "
            "are intentionally blocked."
        )
    if not any(target_path.startswith(prefix) for prefix in EQUILIBRIUM_DEBUG_TARGET_PREFIXES):
        raise SystemExit(
            "--equilibrium-debug explicit targets must be equilibrium tests under tests/api/frontend/test_equilibrium.py "
            "or tests/native/equilibrium/."
        )


def _reject_unbounded_native_targets(
    pytest_args: list[str],
    *,
    all_tests: bool,
    allow_long_native_tests: bool,
) -> None:
    if all_tests or allow_long_native_tests or os.environ.get("EPCSAFT_ALLOW_LONG_NATIVE_TESTS") == "1":
        return
    for arg in _positional_targets(pytest_args):
        target_path = arg.split("::", 1)[0].replace("\\", "/").rstrip("/")
        if "::" in arg:
            continue
        if target_path in LONG_NATIVE_TARGETS:
            raise SystemExit(LONG_NATIVE_TARGETS_NOTE)


def _reject_unbounded_equilibrium_route_targets(
    pytest_args: list[str],
    *,
    all_tests: bool,
    allow_long_equilibrium_tests: bool,
) -> None:
    if all_tests or allow_long_equilibrium_tests or os.environ.get("EPCSAFT_ALLOW_LONG_EQUILIBRIUM_TESTS") == "1":
        return
    for arg in _positional_targets(pytest_args):
        target_path = arg.split("::", 1)[0].replace("\\", "/").rstrip("/")
        if "::" in arg:
            continue
        if target_path in LONG_EQUILIBRIUM_ROUTE_TARGETS:
            raise SystemExit(LONG_EQUILIBRIUM_ROUTE_TARGETS_NOTE)


def _slice_listing_text() -> str:
    lines = [SLICE_SELECTION_NOTE, "", "Available slices:"]
    for name, targets in SLICE_TARGETS.items():
        lines.append(f"{name}:")
        for target in targets:
            lines.append(f"  {target}")
    return "\n".join(lines)


def _patch_windows_pytest_temp_acl() -> None:
    if os.name != "nt":
        return

    original_mkdir = Path.mkdir

    def sandbox_safe_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        return original_mkdir(self, mode=0o777, parents=parents, exist_ok=exist_ok)

    Path.mkdir = sandbox_safe_mkdir


def _patch_pytest_cleanup() -> None:
    # Pytest's Windows cleanup hook can trip over restricted ACLs after
    # tmp_path tests pass. Keep the per-run basetemp, but skip that hook.
    try:
        import _pytest.pathlib as pytest_pathlib
        import _pytest.tmpdir as pytest_tmpdir

        pytest_pathlib.cleanup_dead_symlinks = lambda root: None
        pytest_tmpdir.cleanup_dead_symlinks = lambda root: None
    except Exception:
        pass


def _failure_message(pytest_temp: Path) -> str:
    cleanup_path = str(pytest_temp.resolve())
    return (
        "Pytest failed; keeping temp directory for triage: "
        f"{cleanup_path}\n"
        "Cleanup with: "
        f"Remove-Item -Recurse -Force '{cleanup_path}' (PowerShell)\n"
        f"or rm -rf {cleanup_path} (POSIX shells)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=SLICE_SELECTION_NOTE)
    predefined = parser.add_mutually_exclusive_group()
    predefined.add_argument("--generic", action="store_true", help="Run the core generic test slice")
    predefined.add_argument(
        "--confidence",
        action="store_true",
        help="Run generic fast contracts plus native runtime contract tests",
    )
    predefined.add_argument(
        "--equilibrium-confidence",
        action="store_true",
        help="Run trusted equilibrium route-contract checks anchored on exact-Hessian native Ipopt solves",
    )
    predefined.add_argument(
        "--equilibrium-api",
        action="store_true",
        help="Run fast equilibrium/speciation API tests for downstream-agent workflows",
    )
    predefined.add_argument("--runtime", action="store_true", help="Run runtime API and native contract tests")
    predefined.add_argument("--api", action="store_true", help="Run public API and regression API tests")
    predefined.add_argument("--native", action="store_true", help="Run native runtime contract tests")
    predefined.add_argument(
        "--native-contracts",
        action="store_true",
        help="Run fast native route metadata/result contract tests without broad solver route suites",
    )
    predefined.add_argument(
        "--all",
        dest="all_tests",
        action="store_true",
        help="Run every retained pytest contract under tests/; this is intentionally opt-in",
    )
    parser.add_argument(
        "--list-slices", action="store_true", help="Print named test slices and exit without running pytest"
    )
    parser.add_argument(
        "--allow-long-native-tests",
        action="store_true",
        help="Allow broad known-slow native route-builder file targets",
    )
    parser.add_argument(
        "--allow-long-equilibrium-tests",
        action="store_true",
        help="Allow broad known-slow frontend equilibrium route-solve file targets",
    )
    parser.add_argument(
        "--equilibrium-debug",
        action="store_true",
        help="Enable opt-in equilibrium debug settings in tests, including verbose Ipopt print/history controls.",
    )
    args, pytest_args = parser.parse_known_args()

    if args.list_slices:
        print(_slice_listing_text())
        return 0

    repo_root = _repo_root()
    pytest_temp = _pytest_temp(repo_root)
    env = _pytest_env(pytest_temp)
    _apply_equilibrium_debug_env(env, args.equilibrium_debug)
    src_root = repo_root / "src"
    sys.path.insert(0, str(src_root))
    env["PYTHONPATH"] = str(src_root)

    cmd = _pytest_args(
        pytest_args,
        pytest_temp,
        args.generic,
        confidence=args.confidence,
        equilibrium_confidence=args.equilibrium_confidence,
        equilibrium_api=args.equilibrium_api,
        runtime=args.runtime,
        api=args.api,
        native=args.native,
        native_contracts=args.native_contracts,
        all_tests=args.all_tests,
        allow_long_native_tests=args.allow_long_native_tests,
        allow_long_equilibrium_tests=args.allow_long_equilibrium_tests,
        equilibrium_debug=args.equilibrium_debug,
    )
    print("Running:", f"{sys.executable} -m pytest", " ".join(cmd), flush=True)
    os.environ.update(env)

    _patch_windows_pytest_temp_acl()
    _patch_pytest_cleanup()

    import pytest

    exit_code = int(pytest.main(cmd))
    if exit_code == 0:
        shutil.rmtree(pytest_temp, ignore_errors=True)
    else:
        print(_failure_message(pytest_temp), flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
