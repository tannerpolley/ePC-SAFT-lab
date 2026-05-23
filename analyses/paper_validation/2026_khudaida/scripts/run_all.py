from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(path: Path) -> None:
    print(f"[run] {path}")
    subprocess.run([sys.executable, str(path)], check=True)


def main() -> None:
    for idx in range(1, 10):
        figure_scripts = ROOT.parent / "figures" / f"figure_{idx:02d}" / "scripts"
        _run(figure_scripts / "generate_data.py")
        _run(figure_scripts / f"plot_figure_{idx}.py")
    table_scripts = ROOT / "tables_009_010"
    _run(table_scripts / "generate_data.py")
    _run(table_scripts / "plot_tables_9_10.py")
    for figure_id, paper_suffix in (("figure_11", 2), ("figure_12", 3)):
        supporting_scripts = ROOT.parent / "figures" / figure_id / "scripts"
        _run(supporting_scripts / "generate_data.py")
        _run(supporting_scripts / f"plot_figure_s{paper_suffix}.py")
    print("[done] 2026 Khudaida analysis complete.")


if __name__ == "__main__":
    main()
