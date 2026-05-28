from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROVIDER_ROOT / "src"
PACKAGE_SRC_ROOT = PACKAGE_ROOT / "src"

for import_root in (PROVIDER_ROOT, SRC_ROOT, PACKAGE_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)
