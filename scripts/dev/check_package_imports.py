from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (
    REPO_ROOT / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
    REPO_ROOT / "packages" / "epcsaft-regression" / "src",
)
EXPECTED_MODULE_ROOTS = {
    "epcsaft": REPO_ROOT / "src" / "epcsaft",
    "epcsaft_equilibrium": REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src" / "epcsaft_equilibrium",
    "epcsaft_regression": REPO_ROOT / "packages" / "epcsaft-regression" / "src" / "epcsaft_regression",
}

for source_root in reversed(SOURCE_ROOTS):
    sys.path.insert(0, str(source_root))


def _module_file(module_name: str) -> Path:
    module = importlib.import_module(module_name)
    module_file = getattr(module, "__file__", None)
    if not module_file:
        raise RuntimeError(f"{module_name}: imported module has no __file__")
    return Path(module_file).resolve()


def _assert_module_location(module_name: str, expected_root: Path) -> None:
    module_file = _module_file(module_name)
    if expected_root.resolve() not in (module_file, *module_file.parents):
        raise RuntimeError(f"{module_name}: expected import under {expected_root}, got {module_file}")


def _assert_capabilities(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    capabilities = getattr(module, "capabilities")
    result = capabilities()
    if not isinstance(result, dict):
        raise RuntimeError(f"{module_name}.capabilities() returned {type(result).__name__}, expected dict")
    return result


def main() -> int:
    for module_name, expected_root in EXPECTED_MODULE_ROOTS.items():
        _assert_module_location(module_name, expected_root)
        report = _assert_capabilities(module_name)
        print(f"{module_name}: {Path(importlib.import_module(module_name).__file__).resolve()}")
        print(f"{module_name}.capabilities.package: {report.get('package', '<missing>')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
