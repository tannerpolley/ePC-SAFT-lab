from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2025_figiel"
    / "scripts"
    / "validate_figure_data.py"
)


def test_figiel_validator_defers_native_backend_import_until_after_build_gate() -> None:
    probe = f"""
import importlib.util
import sys
from pathlib import Path

validator = Path(r"{VALIDATOR}")
spec = importlib.util.spec_from_file_location("figiel_validate_figure_data_probe", validator)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

eager = [
    name
    for name in ("shared.figure_data", "scripts._epcsaft_oop", "epcsaft._core")
    if name in sys.modules
]
if eager:
    raise SystemExit("validator imported backend modules before the backend gate: " + ", ".join(eager))
"""
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
