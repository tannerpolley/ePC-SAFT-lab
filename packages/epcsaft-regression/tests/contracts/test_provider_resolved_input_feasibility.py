"""Stage 4 gate for the separately approved M5 Tasks 1-3 contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import epcsaft_regression
import yaml
from api.test_problem_compiler import _compile
from epcsaft.model.resolved_input import EvaluatedModelInput
from epcsaft_regression.native_adapter import _native_problem_from_compiled

REPO_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPO_ROOT / "packages" / "epcsaft-regression" / "src" / "epcsaft_regression"
CAPABILITY_BASELINE = Path(__file__).with_name("fixtures") / "stage4_capability_baseline.json"
BLOCKER_RECEIPT = (
    REPO_ROOT
    / "docs/superpowers/milestones/M5-regression/"
    "stage-4-provider-input-prerequisite-blocker.yaml"
)

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


def _function_node(path: Path, function_name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return node
    raise AssertionError(f"missing function {function_name!r} in {path}")


def _public_entrypoint_ownership_report() -> dict[str, object]:
    workflow_path = PACKAGE_ROOT / "workflow.py"
    core_path = PACKAGE_ROOT / "core.py"
    workflow_fit = _function_node(workflow_path, "fit_pure_neutral")
    workflow_source = ast.get_source_segment(
        workflow_path.read_text(encoding="utf-8"), workflow_fit
    )
    assert workflow_source is not None

    statuses: dict[str, str] = {}
    statuses["Regression.fit_pure_neutral"] = (
        "configured_mixture_not_consumed_by_compiler"
        if "self.compile(" not in workflow_source
        and "compile_regression_problem(" not in workflow_source
        else "configured_compiler_owned"
    )
    for function_name in (
        "fit_binary_parameters",
        "fit_liquid_electrolyte_parameters",
    ):
        function = _function_node(core_path, function_name)
        argument_names = {
            argument.arg
            for argument in (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs)
        }
        statuses[function_name] = (
            "public_free_function_has_no_configured_mixture"
            if "mixture" not in argument_names
            else "configured_compiler_owned"
        )
    return {
        "classification": "blocked_before_immutable_baseline_overlay",
        "entrypoints": statuses,
        "all_production_entrypoints_configured": all(
            status == "configured_compiler_owned" for status in statuses.values()
        ),
    }


def test_stage4_gate_confirms_the_approved_m5_prerequisites_are_ready() -> None:
    report = _prerequisite_report()

    assert report == {
        "classification": "ready_for_stage4_overlay_gate",
        "absent_files": (),
        "absent_symbols": (),
    }
    assert "NativeRegressionProblem" in (
        PACKAGE_ROOT / "native/regression/regression_problem.h"
    ).read_text(encoding="utf-8")


def test_stage4_regression_capability_baseline_is_exact() -> None:
    baseline = json.loads(CAPABILITY_BASELINE.read_text(encoding="utf-8"))

    current = json.loads(json.dumps(epcsaft_regression.capabilities(), sort_keys=True))
    assert current == baseline


def test_stage4_gate_records_exact_public_entrypoint_ownership_blocker() -> None:
    compiled = _compile()
    native_problem = _native_problem_from_compiled(compiled)

    assert compiled.evaluated_inputs
    assert all(isinstance(item, EvaluatedModelInput) for item in compiled.evaluated_inputs)
    assert compiled.native_handles == tuple(item.native_handle for item in compiled.evaluated_inputs)
    assert native_problem.snapshot_fingerprints == compiled.snapshot_fingerprints
    assert _public_entrypoint_ownership_report() == {
        "classification": "blocked_before_immutable_baseline_overlay",
        "entrypoints": {
            "Regression.fit_pure_neutral": (
                "configured_mixture_not_consumed_by_compiler"
            ),
            "fit_binary_parameters": "public_free_function_has_no_configured_mixture",
            "fit_liquid_electrolyte_parameters": (
                "public_free_function_has_no_configured_mixture"
            ),
        },
        "all_production_entrypoints_configured": False,
    }
    assert not (
        PACKAGE_ROOT / "native/regression/resolved_input_adapter.h"
    ).exists()


def test_stage4_blocker_receipt_matches_the_live_entrypoint_gate() -> None:
    receipt = yaml.safe_load(BLOCKER_RECEIPT.read_text(encoding="utf-8"))
    report = _public_entrypoint_ownership_report()

    assert receipt["prerequisite_contracts"]["classification"] == (
        "ready_for_stage4_overlay_gate"
    )
    assert receipt["public_entrypoint_ownership_gate"] == {
        "classification": report["classification"],
        "all_production_entrypoints_configured": False,
        "blocking_entrypoints": receipt["public_entrypoint_ownership_gate"][
            "blocking_entrypoints"
        ],
    }
    assert {
        row["entrypoint"]: row["reason"]
        for row in receipt["public_entrypoint_ownership_gate"]["blocking_entrypoints"]
    } == report["entrypoints"]
    assert receipt["decisive_gate"]["stage_4_status"] == (
        "blocked_before_immutable_baseline_overlay"
    )
    assert receipt["decisive_gate"]["native_overlay_adapter_created"] is False
    assert receipt["push_performed"] is False
