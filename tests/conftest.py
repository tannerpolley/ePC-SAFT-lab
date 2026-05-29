from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
EQUILIBRIUM_NATIVE_TRANSITION_FILES = {
    "tests/native/contracts/test_equilibrium_benchmark_registry.py",
    "tests/native/contracts/test_generalized_equilibrium_registry.py",
}

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        try:
            relpath = Path(str(item.path)).resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            continue
        if relpath in EQUILIBRIUM_NATIVE_TRANSITION_FILES:
            item.add_marker(pytest.mark.equilibrium_native_transition)
