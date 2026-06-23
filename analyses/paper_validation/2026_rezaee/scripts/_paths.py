from __future__ import annotations

import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        package_src = candidate / "packages" / "epcsaft" / "src" / "epcsaft"
        legacy_src = candidate / "src" / "epcsaft"
        if (candidate / "pyproject.toml").is_file() and (package_src.is_dir() or legacy_src.is_dir()):
            return candidate
    raise RuntimeError(f"Could not find ePC-SAFT repo root from {start}")


SCRIPT_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = SCRIPT_DIR.parent
REPO_ROOT = find_repo_root(SCRIPT_DIR)
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
if not (SRC_ROOT / "epcsaft").is_dir():
    SRC_ROOT = REPO_ROOT / "src"

for path in (SRC_ROOT, REPO_ROOT):
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)
