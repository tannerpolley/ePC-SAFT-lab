"""Stage 4 gate for the separately approved M5 Tasks 1-3 contracts."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPO_ROOT / "packages" / "epcsaft-regression" / "src" / "epcsaft_regression"

REQUIRED_FILES = (
    "targets.py",
    "controls.py",
    "parameters.py",
    "problem.py",
    "native/regression/regression_problem.h",
)
REQUIRED_PYTHON_SYMBOLS = {
    "targets.py": ("TargetDataset",),
    "controls.py": ("RegressionControls",),
    "parameters.py": ("FittedParameter",),
    "problem.py": ("CompiledRegressionProblem", "compile_regression_problem"),
}
REQUIRED_PROBLEM_MARKERS = (
    "EvaluatedModelInput",
    "native_handle",
)
REQUIRED_NATIVE_SYMBOLS = (
    "NativeRegressionProblem",
)

EXPECTED_ABSENT_FILES = REQUIRED_FILES
EXPECTED_ABSENT_SYMBOLS = (
    "controls.py:RegressionControls",
    "native/regression/regression_problem.h:NativeRegressionProblem",
    "parameters.py:FittedParameter",
    "problem.py:CompiledRegressionProblem",
    "problem.py:EvaluatedModelInput",
    "problem.py:compile_regression_problem",
    "problem.py:native_handle",
    "targets.py:TargetDataset",
)


def _python_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _prerequisite_report() -> dict[str, object]:
    absent_files = tuple(
        relative_path
        for relative_path in REQUIRED_FILES
        if not (PACKAGE_ROOT / relative_path).is_file()
    )
    absent_symbols: list[str] = []
    for relative_path, symbols in REQUIRED_PYTHON_SYMBOLS.items():
        path = PACKAGE_ROOT / relative_path
        defined = _python_symbols(path) if path.is_file() else set()
        absent_symbols.extend(
            f"{relative_path}:{symbol}"
            for symbol in symbols
            if symbol not in defined
        )
    problem_path = PACKAGE_ROOT / "problem.py"
    problem_text = problem_path.read_text(encoding="utf-8") if problem_path.is_file() else ""
    absent_symbols.extend(
        f"problem.py:{marker}"
        for marker in REQUIRED_PROBLEM_MARKERS
        if marker not in problem_text
    )
    native_path = PACKAGE_ROOT / "native/regression/regression_problem.h"
    native_text = native_path.read_text(encoding="utf-8") if native_path.is_file() else ""
    absent_symbols.extend(
        f"native/regression/regression_problem.h:{symbol}"
        for symbol in REQUIRED_NATIVE_SYMBOLS
        if symbol not in native_text
    )
    missing = absent_files or absent_symbols
    return {
        "classification": (
            "requires_approved_m5_tasks_1_to_3"
            if missing
            else "ready_for_stage4_overlay_gate"
        ),
        "absent_files": absent_files,
        "absent_symbols": tuple(sorted(absent_symbols)),
    }


def test_stage4_gate_records_exact_current_m5_prerequisite_absence() -> None:
    report = _prerequisite_report()
    legacy_core = (PACKAGE_ROOT / "core.py").read_text(encoding="utf-8")

    assert report == {
        "classification": "requires_approved_m5_tasks_1_to_3",
        "absent_files": EXPECTED_ABSENT_FILES,
        "absent_symbols": EXPECTED_ABSENT_SYMBOLS,
    }
    assert "class TargetDataset" in legacy_core
    assert "targets.py:TargetDataset" in report["absent_symbols"]
