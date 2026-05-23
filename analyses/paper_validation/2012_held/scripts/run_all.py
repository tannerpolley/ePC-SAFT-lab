from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(path: Path) -> None:
    if not path.exists():
        print(f"[skip] missing script: {path}")
        return
    cmd = [sys.executable, str(path)]
    print(f"[run] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    workflows = (
        ("figure_02", "panel_d", "plot_figure_2d.py"),
        ("figure_03", "", "plot_figure_3.py"),
        ("figure_05", "", "plot_figure_5.py"),
        ("figure_06", "", "plot_figure_6.py"),
        ("figure_07", "", "plot_figure_7.py"),
    )
    for figure_id, script_subdir, plot_script in workflows:
        figure_scripts = ROOT.parent / "figures" / figure_id / "scripts"
        if script_subdir:
            figure_scripts = figure_scripts / script_subdir
        run_script(figure_scripts / "generate_data.py")
        run_script(figure_scripts / plot_script)
    print("[done] 2012 figure scripts completed.")
    print(f"[note] Data-gap report: {ROOT / 'data_gap_report.md'}")


if __name__ == "__main__":
    main()
