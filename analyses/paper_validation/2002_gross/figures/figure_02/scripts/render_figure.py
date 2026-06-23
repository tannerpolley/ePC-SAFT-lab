from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).resolve().parents[3] / "scripts" / "generate_clean_literature_overlays.py"
    completed = subprocess.run([sys.executable, str(script)], check=False)
    return int(completed.returncode)


if __name__ == '__main__':
    raise SystemExit(main())
