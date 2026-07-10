from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(path: Path, *, allow_force_recompute: bool) -> None:
    print(f"[run] {path}")
    env = os.environ.copy()
    if not allow_force_recompute:
        env.pop("KHUDAIDA_FORCE_RECOMPUTE", None)
    subprocess.run([sys.executable, str(path)], check=True, env=env)


def main() -> None:
    for idx in range(1, 11):
        figure_scripts = ROOT.parent / "figures" / f"figure_{idx:02d}" / "scripts"
        _run(figure_scripts / "generate_data.py", allow_force_recompute=True)
        _run(figure_scripts / "render_figure.py", allow_force_recompute=False)
    table_scripts = ROOT / "tables_009_010"
    _run(table_scripts / "generate_data.py", allow_force_recompute=True)
    _run(table_scripts / "plot_tables_9_10.py", allow_force_recompute=False)
    for figure_id, _paper_suffix in (("figure_11", 2), ("figure_12", 3)):
        supporting_scripts = ROOT.parent / "figures" / figure_id / "scripts"
        _run(supporting_scripts / "generate_data.py", allow_force_recompute=True)
        _run(supporting_scripts / "render_figure.py", allow_force_recompute=False)
    print("[done] 2026 Khudaida analysis complete.")


if __name__ == "__main__":
    main()
