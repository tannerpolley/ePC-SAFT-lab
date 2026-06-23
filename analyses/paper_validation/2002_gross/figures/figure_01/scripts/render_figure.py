from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("generate_data.py")
    completed = subprocess.run([sys.executable, str(script), "--render-only"], check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
