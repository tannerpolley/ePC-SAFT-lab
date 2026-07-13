"""Stage 4 gate for the separately approved M5 Tasks 1-3 contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import epcsaft_regression
import epcsaft_regression.workflow as workflow_module
import pytest
import yaml
from api.test_problem_compiler import (
    _binary_dataset,
    _binary_mixture,
    _controls,
    _dataset,
    _mixture,
    _parameters,
)
from epcsaft import InputError
from epcsaft.model.resolved_input import EvaluatedModelInput
from epcsaft_regression import (
    FittedParameter,
    Regression,
    TargetDataset,
    compile_regression_problem,
)
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

PLAN_OVERLAY_TARGET_KINDS = (
    "m",
    "s",
    "e",
    "e_assoc",
    "vol_a",
    "d_born",
    "k_ij",
    "l_ij",
    "k_hb_ij",
    "f_solv",
    "dielc",
)
TARGET_PARAMETER_CASES = {
    "m": ("Methane.m", 1.0, 0.5, 2.0),
    "s": ("Methane.sigma", 3.5, 2.0, 5.0),
    "e": ("Methane.epsilon_k", 150.0, 50.0, 400.0),
    "e_assoc": ("Methane.epsilon_k_ab", 100.0, 0.0, 500.0),
    "vol_a": ("Methane.kappa_ab", 0.01, 0.0, 0.1),
    "d_born": ("Methane.born_diameter", 3.0, 2.0, 4.0),
    "k_ij": ("Methane:Ethane.k_ij", 0.0, -0.2, 0.2),
    "l_ij": ("Methane:Ethane.l_ij", 0.0, -0.2, 0.2),
    "k_hb_ij": ("Methane:Ethane.k_hb_ij", 0.0, -0.2, 0.2),
    "f_solv": ("Methane.solvation_factor", 1.0, 0.5, 2.0),
    "dielc": ("Methane.relative_permittivity", 1.0, 0.5, 100.0),
}

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


def _plan_target_compiler_report() -> dict[str, object]:
    fixtures = {
        "pure_neutral": _dataset(),
        "constant_binary_interaction": _binary_dataset(),
    }
    compiled: list[str] = []
    requires_new_compiler_meaning: list[str] = []
    incompatibility_reasons: dict[str, str] = {}
    unexpected_rejections: dict[str, str] = {}
    source_backed_strict_target_kinds: list[str] = []
    component_test_only_strict_target_kinds: list[str] = []
    unclassified_compiled_target_sources: list[str] = []
    for target_kind in PLAN_OVERLAY_TARGET_KINDS:
        parameter = FittedParameter(*TARGET_PARAMETER_CASES[target_kind])
        interaction = ":" in parameter.key
        fixture_name = (
            "constant_binary_interaction" if interaction else "pure_neutral"
        )
        dataset = fixtures[fixture_name]
        try:
            compile_regression_problem(
                mixture=_binary_mixture() if interaction else _mixture(),
                dataset=dataset,
                parameters=(parameter,),
                controls=_controls(),
            )
        except InputError as exc:
            reason = str(exc)
            expected_reason = (
                f"fitted parameter {parameter.key!r} is not compatible with target "
                f"family {dataset.rows[0].target_family.value!r}."
            )
            if reason == expected_reason:
                requires_new_compiler_meaning.append(target_kind)
                incompatibility_reasons[target_kind] = reason
            else:
                unexpected_rejections[target_kind] = reason
        else:
            compiled.append(target_kind)
            source_kinds = {
                row.source.source_kind.value for row in dataset.rows
            }
            if source_kinds == {"literature"}:
                source_backed_strict_target_kinds.append(target_kind)
            elif source_kinds == {"component_test"}:
                component_test_only_strict_target_kinds.append(target_kind)
            else:
                unclassified_compiled_target_sources.append(target_kind)
    return {
        "plan_target_kinds": PLAN_OVERLAY_TARGET_KINDS,
        "compiled_target_kinds": tuple(compiled),
        "requires_new_compiler_meaning": tuple(requires_new_compiler_meaning),
        "compiler_incompatibility_reasons": incompatibility_reasons,
        "unexpected_rejections": unexpected_rejections,
        "source_backed_strict_target_kinds": tuple(
            source_backed_strict_target_kinds
        ),
        "component_test_only_strict_target_kinds": tuple(
            component_test_only_strict_target_kinds
        ),
        "unclassified_compiled_target_sources": tuple(
            unclassified_compiled_target_sources
        ),
        "missing_strict_target_family_kinds": tuple(
            requires_new_compiler_meaning
        ),
        "fixture_evidence": {
            name: _target_dataset_evidence(dataset)
            for name, dataset in fixtures.items()
        },
    }


def _target_dataset_evidence(dataset: TargetDataset) -> dict[str, object]:
    return {
        "dataset_id": dataset.dataset_id,
        "rows": [
            {
                "row_id": row.row_id,
                "target_family": row.target_family.value,
                "source": row.source.to_dict(),
            }
            for row in dataset.rows
        ],
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
        "blocked_before_immutable_overlay_adapter"
    )
    assert receipt["decisive_gate"]["native_overlay_adapter_created"] is False
    step_5 = receipt["task_5_step_5_evidence"]
    assert step_5["regression_profile_build"] == {
        "command": (
            "uv run --no-sync python scripts/dev/build_epcsaft.py "
            "--profile regression --parallel 1"
        ),
        "result": "failed_before_feasibility_red_slice",
        "first_failure": (
            "packages/epcsaft-regression/src/epcsaft_regression/native/regression/"
            "ceres_regression.cpp:176: 'add_args' does not name a type"
        ),
        "interpretation": (
            "The retained native regression characterization owner still consumes "
            "the retired mutable add_args carrier, so the required regression profile "
            "is not buildable from the configured-workflow revision."
        ),
    }
    combined_red = step_5["combined_red_slice"]
    assert combined_red["command"] == (
        "uv run --no-sync python run_pytest.py "
        "packages/epcsaft-regression/tests/contracts/"
        "test_provider_resolved_input_feasibility.py "
        "packages/epcsaft-regression/tests/api/test_regression.py "
        "packages/epcsaft-regression/tests/native/test_pure.py "
        "packages/epcsaft-regression/tests/native/test_binary.py "
        "packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py -q"
    )
    assert combined_red["result"] == "collection_failed_with_2_errors"
    assert combined_red["scientific_regressions_green"] is False
    assert combined_red["adapter_absence_red_reached"] is False
    assert receipt["push_performed"] is False


def test_stage4_plan_target_surface_records_exact_pre_adapter_blocker() -> None:
    report = _plan_target_compiler_report()

    assert report == {
        "plan_target_kinds": PLAN_OVERLAY_TARGET_KINDS,
        "compiled_target_kinds": ("m", "s", "e", "k_ij"),
        "requires_new_compiler_meaning": (
            "e_assoc",
            "vol_a",
            "d_born",
            "l_ij",
            "k_hb_ij",
            "f_solv",
            "dielc",
        ),
        "compiler_incompatibility_reasons": {
            "e_assoc": (
                "fitted parameter 'Methane.epsilon_k_ab' is not compatible with "
                "target family 'pure_saturation_fugacity_balance'."
            ),
            "vol_a": (
                "fitted parameter 'Methane.kappa_ab' is not compatible with target "
                "family 'pure_saturation_fugacity_balance'."
            ),
            "d_born": (
                "fitted parameter 'Methane.born_diameter' is not compatible with "
                "target family 'pure_saturation_fugacity_balance'."
            ),
            "l_ij": (
                "fitted parameter 'Methane:Ethane.l_ij' is not compatible with "
                "target family 'binary_vle'."
            ),
            "k_hb_ij": (
                "fitted parameter 'Methane:Ethane.k_hb_ij' is not compatible with "
                "target family 'binary_vle'."
            ),
            "f_solv": (
                "fitted parameter 'Methane.solvation_factor' is not compatible with "
                "target family 'pure_saturation_fugacity_balance'."
            ),
            "dielc": (
                "fitted parameter 'Methane.relative_permittivity' is not compatible "
                "with target family 'pure_saturation_fugacity_balance'."
            ),
        },
        "unexpected_rejections": {},
        "source_backed_strict_target_kinds": ("m", "s", "e"),
        "component_test_only_strict_target_kinds": ("k_ij",),
        "unclassified_compiled_target_sources": (),
        "missing_strict_target_family_kinds": (
            "e_assoc",
            "vol_a",
            "d_born",
            "l_ij",
            "k_hb_ij",
            "f_solv",
            "dielc",
        ),
        "fixture_evidence": {
            "pure_neutral": {
                "dataset_id": "methane-contract-targets",
                "rows": [
                    {
                        "row_id": "methane-fugacity-130K",
                        "target_family": "pure_saturation_fugacity_balance",
                        "source": {
                            "source_id": "NIST_methane_saturation",
                            "source_kind": "literature",
                            "citation": "NIST Chemistry WebBook SRD 69",
                            "locator": "Methane saturation table, 130 K",
                        },
                    },
                    {
                        "row_id": "methane-density-130K",
                        "target_family": "pure_liquid_density_at_pressure",
                        "source": {
                            "source_id": "NIST_methane_saturation",
                            "source_kind": "literature",
                            "citation": "NIST Chemistry WebBook SRD 69",
                            "locator": "Methane saturation table, 130 K",
                        },
                    },
                ],
            },
            "constant_binary_interaction": {
                "dataset_id": "binary-contract-targets",
                "rows": [
                    {
                        "row_id": "methane-ethane-vle-001",
                        "target_family": "binary_vle",
                        "source": {
                            "source_id": "binary-component-contract",
                            "source_kind": "component_test",
                            "citation": "",
                            "locator": "test_problem_compiler.py binary row",
                        },
                    }
                ],
            },
        },
    }
    assert not (PACKAGE_ROOT / "native/regression/resolved_input_adapter.h").exists()
    assert not (PACKAGE_ROOT / "native/regression/resolved_input_adapter.cpp").exists()
    receipt = yaml.safe_load(BLOCKER_RECEIPT.read_text(encoding="utf-8"))
    gate = receipt["overlay_feasibility_gate"]
    for key in (
        "plan_target_kinds",
        "compiled_target_kinds",
        "requires_new_compiler_meaning",
        "compiler_incompatibility_reasons",
        "unexpected_rejections",
        "source_backed_strict_target_kinds",
        "component_test_only_strict_target_kinds",
        "unclassified_compiled_target_sources",
        "missing_strict_target_family_kinds",
        "fixture_evidence",
    ):
        expected = report[key]
        if isinstance(expected, tuple):
            expected = list(expected)
        assert gate[key] == expected
