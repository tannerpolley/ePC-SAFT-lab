from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROVIDER_ROOT / "src"
PACKAGE_SRC_ROOT = PACKAGE_ROOT / "src"
PACKAGE_TEST_ROOT = PACKAGE_ROOT / "tests"
EQUILIBRIUM_NATIVE_TRANSITION_FILES = {
    "packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_native_contracts.py",
}

for import_root in (PACKAGE_TEST_ROOT, PROVIDER_ROOT, SRC_ROOT, PACKAGE_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        try:
            relpath = Path(str(item.path)).resolve().relative_to(PROVIDER_ROOT).as_posix()
        except ValueError:
            continue
        if relpath.startswith("packages/epcsaft-equilibrium/tests/native/") or relpath in EQUILIBRIUM_NATIVE_TRANSITION_FILES:
            item.add_marker(pytest.mark.equilibrium_native_transition)
