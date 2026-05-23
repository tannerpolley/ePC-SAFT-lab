from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(path: Path) -> None:
    cmd = [sys.executable, str(path)]
    print(f"[run] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    workflows = (
        ("figure_02", "", "plot_figure_2.py"),
        ("figure_03", "", "plot_figure_3.py"),
        ("figure_04", "", "plot_figure_4.py"),
        ("figure_05", "", "plot_figure_5.py"),
        ("figure_06", "panel_a", "plot_figure_6a.py"),
        ("figure_06", "panel_b", "plot_figure_6b.py"),
        ("figure_07", "", "plot_figure_7.py"),
    )
    for figure_id, script_subdir, plot_script in workflows:
        figure_scripts = ROOT.parent / "figures" / figure_id / "scripts"
        if script_subdir:
            figure_scripts = figure_scripts / script_subdir
        run_script(figure_scripts / "generate_data.py")
        run_script(figure_scripts / plot_script)
    print("[done] 2020 figure scripts completed.")
    print(f"[note] Diagnostics: {ROOT / 'diagnostics'}")


if __name__ == "__main__":
    main()
