from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages"

PROVIDER_PACKAGE_DIR = PACKAGES_DIR / "epcsaft"
PROVIDER_SRC_ROOT = PROVIDER_PACKAGE_DIR / "src"
PROVIDER_MODULE_DIR = PROVIDER_SRC_ROOT / "epcsaft"
PROVIDER_NATIVE_DIR = PROVIDER_MODULE_DIR / "native"
PROVIDER_PYPROJECT = PROVIDER_PACKAGE_DIR / "pyproject.toml"
PROVIDER_BUILD_BACKEND_DIR = PROVIDER_PACKAGE_DIR / "build_backend"

EQUILIBRIUM_PACKAGE_DIR = PACKAGES_DIR / "epcsaft-equilibrium"
REGRESSION_PACKAGE_DIR = PACKAGES_DIR / "epcsaft-regression"
