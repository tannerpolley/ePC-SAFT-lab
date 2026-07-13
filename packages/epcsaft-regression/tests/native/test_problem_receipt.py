from __future__ import annotations

import math

import pytest
from api.test_problem_compiler import _compile
from epcsaft_regression.native_adapter import _native_problem_from_compiled
from regression_support.native_problem_cases import native_core, native_problem


def test_compiled_problem_becomes_one_typed_native_problem_without_mapping_round_trip() -> None:
    core = native_core()
    compiled = _compile()

    problem = _native_problem_from_compiled(compiled)

    assert isinstance(problem, core.NativeRegressionProblem)
    assert problem.dataset_id == compiled.dataset_id
    assert problem.provider_definition_fingerprint == compiled.provider_definition_fingerprint
    assert problem.row_ids == compiled.row_ids
    assert problem.source_ids == compiled.source_ids
    assert problem.snapshot_fingerprints == compiled.snapshot_fingerprints
    assert problem.parameter_keys == compiled.parameter_keys


def test_native_evaluation_emits_authoritative_ordered_receipt_and_exact_derivatives() -> None:
    core = native_core()
    problem = native_problem()
    baseline_fingerprint = problem.snapshot_fingerprints

    result = core._evaluate_regression(problem, (1.5,))

    assert result["receipt_schema_version"] == 1
    assert result["problem_fingerprint"] == problem.problem_fingerprint
    assert result["problem_receipt"] == problem.problem_receipt
    assert result["problem_receipt"]["row_ids"] == ["quadratic-row"]
    assert result["problem_receipt"]["source_ids"] == ["quadratic-component-contract"]
    assert result["problem_receipt"]["snapshot_fingerprints"] == list(baseline_fingerprint)
    assert problem.snapshot_fingerprints == baseline_fingerprint
    assert result["termination_type"] == "EVALUATION_ONLY"
    assert result["solution_usable"] is True

    raw = 1.5**2 - 2.0
    packed = math.sqrt(9.0) * raw / 2.0
    assert result["row_diagnostics"] == [
        {
            "row_id": "quadratic-row",
            "source_id": "quadratic-component-contract",
            "raw_residual": pytest.approx(raw),
            "weighted_residual": pytest.approx(packed),
        }
    ]
    assert result["objective"] == pytest.approx(0.5 * packed**2)
    assert result["jacobian_shape"] == (1, 1)
    assert result["jacobian_row_major"] == pytest.approx((4.5,))
    assert result["derivative_metadata"] == {
        "complete": True,
        "parameter_keys": ["Methane.m"],
        "column_owners": ["exact_component_test"],
    }


def test_native_constructor_rejects_invalid_sizes_and_bounds() -> None:
    core = native_core()
    with pytest.raises(ValueError, match=r"start.*bounds"):
        native_problem(start=20.0)
    with pytest.raises(ValueError, match="parameter coefficient"):
        compiled = _compile()
        baseline = compiled.native_handles[0]
        core.NativeRegressionProblem(
            "invalid",
            baseline.definition_fingerprint_sha256,
            (baseline,),
            compiled.fixed_parameter_fingerprints,
            (
                core.NativeRegressionRow(
                    "row",
                    "source",
                    "component_test",
                    "component_test_quadratic",
                    (0,),
                    101325.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    (),
                    "exact_component_test",
                ),
            ),
            (core.NativeFittedParameter("Methane.m", "segment_count", 0, -1, 1.0, 0.5, 2.0),),
            core.NativeRegressionControls("linear", 10, 1.0e-8, 1.0e-8, 1.0e-8),
        )
