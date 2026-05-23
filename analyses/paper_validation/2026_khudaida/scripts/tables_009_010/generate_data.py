from __future__ import annotations

from pathlib import Path
import sys


import sys as _bootstrap_sys
from pathlib import Path as _BootstrapPath

for _candidate in _BootstrapPath(__file__).resolve().parents:
    if (_candidate / "scripts" / "plot_outputs.py").is_file():
        if str(_candidate) not in _bootstrap_sys.path:
            _bootstrap_sys.path.insert(0, str(_candidate))
        break
else:
    raise ModuleNotFoundError("Could not locate repo root containing scripts/plot_outputs.py")
def main() -> None:
    analysis_root = Path(__file__).resolve().parents[2]
    for table_id in ("table_009", "table_010"):
        table_root = analysis_root / "tables" / table_id
        (table_root / "source").mkdir(parents=True, exist_ok=True)
        (table_root / "results").mkdir(parents=True, exist_ok=True)
    print("[skip] no standalone data-generation step for Khudaida tables 9 and 10.")


if __name__ == "__main__":
    main()
