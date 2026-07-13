"""Stage 4 gate for the separately approved M5 Tasks 1-3 contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import epcsaft_regression
import epcsaft_regression.workflow as workflow_module
import pytest
import yaml
from api.test_problem_compiler import _controls, _dataset, _mixture, _parameters
from epcsaft.model.resolved_input import EvaluatedModelInput
from epcsaft_regression import Regression
from epcsaft_regression.native_adapter import _native_problem_from_compiled
from epcsaft_regression.problem import CompiledRegressionProblem

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
    workflow_fit = _function_node(workflow_path, "fit")
    workflow_source = ast.get_source_segment(
        workflow_path.read_text(encoding="utf-8"), workflow_fit
    )
    assert workflow_source is not None

    status = (
        "configured_compiler_owned"
        if "self.compile(" in workflow_source
        and "_solve_regression(" in workflow_source
        else "configured_compiler_not_owned"
    )
    removed_free_exports = (
        "fit_binary_pair",
        "fit_binary_parameters",
        "fit_liquid_electrolyte_parameters",
        "fit_pure_ion",
        "fit_pure_neutral",
        "fit_pure_parameters",
    )
    if any(
        name in epcsaft_regression.__all__ or hasattr(epcsaft_regression, name)
        for name in removed_free_exports
    ):
        status = "loose_record_fit_export_remains"
    constructor = _function_node(workflow_path, "__init__")
    constructor_arguments = {
        argument.arg
        for argument in (
            *constructor.args.posonlyargs,
            *constructor.args.args,
            *constructor.args.kwonlyargs,
        )
    }
    if "controls" not in constructor_arguments:
        status = "configured_controls_not_owned"
    return {
        "classification": (
            "ready_for_immutable_baseline_overlay"
            if status == "configured_compiler_owned"
            else "blocked_before_immutable_baseline_overlay"
        ),
        "entrypoints": {"Regression.fit": status},
        "all_production_entrypoints_configured": status
        == "configured_compiler_owned",
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


def test_stage4_gate_records_exact_public_entrypoint_ownership(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[CompiledRegressionProblem] = []

    class CapturedSolve(RuntimeError):
        pass

    def capture(problem: CompiledRegressionProblem) -> dict[str, object]:
        captured.append(problem)
        raise CapturedSolve

    monkeypatch.setattr(workflow_module, "_solve_regression", capture)
    workflow = Regression(_mixture(), controls=_controls())

    with pytest.raises(CapturedSolve):
        workflow.fit(_dataset(), parameters=_parameters())

    assert len(captured) == 1
    compiled = captured[0]
    native_problem = _native_problem_from_compiled(compiled)

    assert compiled.evaluated_inputs
    assert all(isinstance(item, EvaluatedModelInput) for item in compiled.evaluated_inputs)
    assert compiled.native_handles == tuple(item.native_handle for item in compiled.evaluated_inputs)
    assert native_problem.snapshot_fingerprints == compiled.snapshot_fingerprints
    assert compiled.provider_definition_fingerprint == (
        workflow.mixture.resolved_model_input.fingerprint_sha256
    )
    assert not hasattr(compiled, "provider_payload")
    assert _public_entrypoint_ownership_report() == {
        "classification": "ready_for_immutable_baseline_overlay",
        "entrypoints": {"Regression.fit": "configured_compiler_owned"},
        "all_production_entrypoints_configured": True,
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
    ownership_gate = receipt["public_entrypoint_ownership_gate"]
    assert ownership_gate["classification"] == report["classification"]
    assert ownership_gate["all_production_entrypoints_configured"] is True
    assert {
        row["entrypoint"]: row["ownership"]
        for row in ownership_gate["configured_entrypoints"]
    } == report["entrypoints"]
    assert ownership_gate["removed_free_exports"] == [
        "fit_binary_pair",
        "fit_binary_parameters",
        "fit_liquid_electrolyte_parameters",
        "fit_pure_ion",
        "fit_pure_neutral",
        "fit_pure_parameters",
    ]
    assert receipt["decisive_gate"]["stage_4_status"] == (
        "ready_for_immutable_baseline_overlay_feasibility"
    )
    assert receipt["decisive_gate"]["native_overlay_adapter_created"] is False
    assert receipt["push_performed"] is False
