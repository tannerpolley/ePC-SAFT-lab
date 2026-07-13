from __future__ import annotations

import copy
from collections.abc import Mapping

import epcsaft_regression
import epcsaft_regression.workflow as workflow_module
import pytest
from api.test_problem_compiler import _controls, _dataset, _mixture, _parameters
from epcsaft import InputError
from epcsaft_regression import (
    FitProblem,
    FitResult,
    Regression,
    RegressionEvaluation,
    RegressionReceipt,
)
from epcsaft_regression.native_adapter import _native_problem_from_compiled
from epcsaft_regression.problem import CompiledRegressionProblem


def _native_result(
    problem: CompiledRegressionProblem,
    parameter_values: tuple[float, ...],
    *,
    evaluation_only: bool,
) -> dict[str, object]:
    native_problem = _native_problem_from_compiled(problem)
    row_diagnostics = [
        {
            "row_id": row_id,
            "source_id": source_id,
            "raw_residual": float(index + 1) / 100.0,
            "weighted_residual": float(index + 1) / 100.0,
        }
        for index, (row_id, source_id) in enumerate(
            zip(problem.row_ids, problem.source_ids, strict=True)
        )
    ]
    result: dict[str, object] = {
        "receipt_schema_version": 1,
        "problem_receipt": native_problem.problem_receipt,
        "problem_fingerprint": native_problem.problem_fingerprint,
        "termination_type": "EVALUATION_ONLY" if evaluation_only else "CONVERGENCE",
        "solution_usable": True,
        "effective_ceres_options": (
            {}
            if evaluation_only
            else {
                "max_num_iterations": problem.controls.max_num_iterations,
                "function_tolerance": problem.controls.function_tolerance,
                "gradient_tolerance": problem.controls.gradient_tolerance,
                "parameter_tolerance": problem.controls.parameter_tolerance,
            }
        ),
        "parameter_values": parameter_values,
        "row_diagnostics": row_diagnostics,
        "objective": 0.5,
        "jacobian_row_major": tuple(
            0.0 for _ in range(len(problem.rows) * len(problem.parameters))
        ),
        "jacobian_shape": (len(problem.rows), len(problem.parameters)),
        "derivative_metadata": {
            "complete": True,
            "parameter_keys": list(problem.parameter_keys),
            "column_owners": [
                "resolved_input_overlay" for _ in problem.parameter_keys
            ],
        },
        "success": True,
    }
    if not evaluation_only:
        result.update(
            {
                "iterations": 3,
                "initial_cost": 2.0,
                "final_cost": 0.5,
                "message": "CONVERGENCE",
            }
        )
    return result


def test_configured_fit_and_evaluate_share_one_exact_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controls = _controls()
    regression = Regression(_mixture(), controls=controls)
    compile_calls: list[CompiledRegressionProblem] = []
    original_compile = workflow_module.compile_regression_problem

    def compile_once(**kwargs: object) -> CompiledRegressionProblem:
        compiled = original_compile(**kwargs)
        compile_calls.append(compiled)
        return compiled

    def solve(problem: CompiledRegressionProblem) -> dict[str, object]:
        values = tuple(parameter.start + 0.01 for parameter in problem.parameters)
        return _native_result(problem, values, evaluation_only=False)

    def evaluate(
        problem: CompiledRegressionProblem,
        parameter_values: tuple[float, ...],
    ) -> dict[str, object]:
        return _native_result(problem, parameter_values, evaluation_only=True)

    monkeypatch.setattr(workflow_module, "compile_regression_problem", compile_once)
    monkeypatch.setattr(workflow_module, "_solve_regression", solve)
    monkeypatch.setattr(workflow_module, "_evaluate_regression", evaluate)

    result = regression.fit(_dataset(), parameters=_parameters())
    evaluation = regression.evaluate(
        result.problem,
        parameter_values=result.final_parameters,
    )

    assert len(compile_calls) == 1
    assert isinstance(result, FitResult)
    assert isinstance(result.problem, FitProblem)
    assert isinstance(result.receipt, RegressionReceipt)
    assert isinstance(evaluation, RegressionEvaluation)
    assert result.problem.provider_definition_fingerprint == (
        regression.mixture.resolved_model_input.fingerprint_sha256
    )
    assert result.receipt.problem_fingerprint == evaluation.receipt.problem_fingerprint
    assert result.receipt.row_ids == _dataset().row_ids
    assert result.receipt.row_diagnostics == evaluation.receipt.row_diagnostics
    assert tuple(result.final_parameters) == result.problem.parameter_keys
    assert evaluation.parameter_values == result.final_parameters


def test_receipt_and_result_mappings_are_deeply_detached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regression = Regression(_mixture(), controls=_controls())
    monkeypatch.setattr(
        workflow_module,
        "_solve_regression",
        lambda problem: _native_result(
            problem,
            tuple(parameter.start for parameter in problem.parameters),
            evaluation_only=False,
        ),
    )

    result = regression.fit(_dataset(), parameters=_parameters())
    detached = result.receipt.to_dict()
    detached["problem_receipt"]["row_ids"][0] = "mutated"
    detached["row_diagnostics"][0]["raw_residual"] = 999.0
    final_parameters = result.final_parameters
    final_parameters[next(iter(final_parameters))] = 999.0

    assert result.receipt.to_dict()["problem_receipt"]["row_ids"] == list(
        _dataset().row_ids
    )
    assert result.receipt.row_diagnostics[0]["raw_residual"] == 0.01
    assert 999.0 not in result.final_parameters.values()


def test_public_workflow_rejects_unconfigured_and_bypass_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regression = Regression(_mixture(), controls=_controls())
    monkeypatch.setattr(
        workflow_module,
        "_solve_regression",
        lambda problem: _native_result(
            problem,
            tuple(parameter.start for parameter in problem.parameters),
            evaluation_only=False,
        ),
    )

    with pytest.raises(InputError, match="TargetDataset"):
        regression.fit(_dataset().to_dict(), parameters=_parameters())
    with pytest.raises(TypeError, match="unexpected keyword"):
        regression.fit(_dataset(), parameters=_parameters(), controls=_controls())
    with pytest.raises(TypeError, match="unexpected keyword"):
        regression.fit(_dataset(), parameters=_parameters(), mixture=_mixture())
    with pytest.raises(TypeError, match="controls"):
        Regression(_mixture())
    with pytest.raises(InputError, match="RegressionControls"):
        Regression(_mixture(), controls=_controls().to_dict())

    result = regression.fit(_dataset(), parameters=_parameters())
    other = Regression(_mixture(epsilon_k=151.0), controls=_controls())
    with pytest.raises(InputError, match="configured mixture"):
        other.evaluate(result.problem, parameter_values=result.final_parameters)
    with pytest.raises(InputError, match="FitProblem"):
        regression.evaluate(
            object(),
            parameter_values=result.final_parameters,
        )
    with pytest.raises(InputError, match="parameter key"):
        regression.evaluate(
            result.problem,
            parameter_values={"Methane.m": 1.0},
        )


def test_receipt_parser_rejects_unknown_versions_and_missing_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regression = Regression(_mixture(), controls=_controls())

    def malformed(
        problem: CompiledRegressionProblem,
        *,
        version: int = 1,
        missing: str | None = None,
    ) -> Mapping[str, object]:
        result = _native_result(
            problem,
            tuple(parameter.start for parameter in problem.parameters),
            evaluation_only=False,
        )
        result["receipt_schema_version"] = version
        if missing is not None:
            del result[missing]
        return result

    monkeypatch.setattr(
        workflow_module,
        "_solve_regression",
        lambda problem: malformed(problem, version=2),
    )
    with pytest.raises(InputError, match="receipt schema version"):
        regression.fit(_dataset(), parameters=_parameters())

    monkeypatch.setattr(
        workflow_module,
        "_solve_regression",
        lambda problem: malformed(problem, missing="row_diagnostics"),
    )
    with pytest.raises(InputError, match=r"missing native receipt field.*row_diagnostics"):
        regression.fit(_dataset(), parameters=_parameters())

    def missing_effective_option(
        problem: CompiledRegressionProblem,
    ) -> Mapping[str, object]:
        result = dict(malformed(problem))
        del result["effective_ceres_options"]["gradient_tolerance"]
        return result

    monkeypatch.setattr(
        workflow_module,
        "_solve_regression",
        missing_effective_option,
    )
    with pytest.raises(InputError, match=r"invalid effective Ceres options.*gradient_tolerance"):
        regression.fit(_dataset(), parameters=_parameters())


def test_receipt_parser_preserves_canonical_bytes_across_mapping_order() -> None:
    compiled = Regression(_mixture(), controls=_controls()).compile(
        _dataset(), parameters=_parameters()
    )
    payload = _native_result(
        compiled,
        tuple(parameter.start for parameter in compiled.parameters),
        evaluation_only=False,
    )
    reordered = dict(reversed(tuple(payload.items())))

    first = RegressionReceipt.from_native(payload, operation="fit")
    second = RegressionReceipt.from_native(reordered, operation="fit")

    assert first.canonical_json == second.canonical_json


def test_fit_problem_requires_the_complete_compiled_problem_receipt() -> None:
    compiled = Regression(_mixture(), controls=_controls()).compile(
        _dataset(), parameters=_parameters()
    )
    baseline = _native_result(
        compiled,
        tuple(parameter.start for parameter in compiled.parameters),
        evaluation_only=False,
    )
    mutations = (
        ("controls", lambda payload: payload["problem_receipt"]["controls"].__setitem__("max_num_iterations", 81)),
        ("bounds", lambda payload: payload["problem_receipt"]["parameters"][0].__setitem__("lower", 0.6)),
        ("row scale", lambda payload: payload["problem_receipt"]["rows"][0].__setitem__("residual_scale", 2.0)),
    )

    for _label, mutate in mutations:
        payload = copy.deepcopy(baseline)
        mutate(payload)
        receipt = RegressionReceipt.from_native(payload, operation="fit")
        with pytest.raises(InputError, match="exactly match the compiled problem"):
            FitProblem._from_receipt(compiled, receipt)


def test_evaluation_receipt_must_match_the_exact_fit_problem() -> None:
    compiled = Regression(_mixture(), controls=_controls()).compile(
        _dataset(), parameters=_parameters()
    )
    values = tuple(parameter.start for parameter in compiled.parameters)
    fit_receipt = RegressionReceipt.from_native(
        _native_result(compiled, values, evaluation_only=False),
        operation="fit",
    )
    problem = FitProblem._from_receipt(compiled, fit_receipt)
    payload = _native_result(compiled, values, evaluation_only=True)
    payload["problem_receipt"]["row_ids"][0] = "tampered-row"
    payload["problem_receipt"]["rows"][0]["row_id"] = "tampered-row"
    payload["row_diagnostics"][0]["row_id"] = "tampered-row"
    evaluation_receipt = RegressionReceipt.from_native(payload, operation="evaluate")

    with pytest.raises(InputError, match="exactly match its FitProblem"):
        RegressionEvaluation(problem=problem, receipt=evaluation_receipt)


def test_receipt_parser_rejects_contradictory_acceptance_and_boolean_versions() -> None:
    compiled = Regression(_mixture(), controls=_controls()).compile(
        _dataset(), parameters=_parameters()
    )
    values = tuple(parameter.start for parameter in compiled.parameters)
    baseline = _native_result(compiled, values, evaluation_only=False)

    contradictory = copy.deepcopy(baseline)
    contradictory["termination_type"] = "FAILURE"
    contradictory["solution_usable"] = False
    contradictory["derivative_metadata"]["complete"] = False
    with pytest.raises(InputError, match="success is inconsistent"):
        RegressionReceipt.from_native(contradictory, operation="fit")

    boolean_version = copy.deepcopy(baseline)
    boolean_version["problem_receipt"]["schema_version"] = True
    with pytest.raises(InputError, match="schema_version is unsupported"):
        RegressionReceipt.from_native(boolean_version, operation="fit")

    boolean_shape = copy.deepcopy(baseline)
    boolean_shape["jacobian_shape"] = (True, True)
    with pytest.raises(InputError, match="two integers"):
        RegressionReceipt.from_native(boolean_shape, operation="fit")


def test_public_package_exports_only_the_configured_fit_path() -> None:
    assert hasattr(epcsaft_regression, "Regression")
    assert hasattr(epcsaft_regression, "FitProblem")
    assert hasattr(epcsaft_regression, "RegressionReceipt")
    assert not hasattr(epcsaft_regression, "fit_pure_neutral")
    assert not hasattr(epcsaft_regression, "fit_binary_parameters")
    assert not hasattr(epcsaft_regression, "fit_liquid_electrolyte_parameters")
    with pytest.raises(TypeError, match="created only"):
        FitProblem()
    with pytest.raises(TypeError, match="authoritative native receipt"):
        RegressionReceipt()
