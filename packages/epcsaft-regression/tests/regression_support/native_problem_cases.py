from __future__ import annotations

from typing import Any

from api.test_problem_compiler import _compile


def native_core() -> Any:
    from epcsaft_regression import _native_core

    return _native_core


def native_problem(
    *,
    weight: float = 9.0,
    residual_scale: float = 2.0,
    start: float = 8.0,
    lower: float = -10.0,
    upper: float = 10.0,
    max_num_iterations: int = 50,
    function_tolerance: float = 1.0e-12,
    gradient_tolerance: float = 1.0e-12,
    parameter_tolerance: float = 1.0e-12,
):
    core = native_core()
    compiled = _compile()
    baseline = compiled.native_handles[0]
    parameter = core.NativeFittedParameter(
        "Methane.m",
        "segment_count",
        0,
        -1,
        start,
        lower,
        upper,
    )
    row = core.NativeRegressionRow(
        "quadratic-row",
        "quadratic-component-contract",
        "component_test",
        "component_test_quadratic",
        (0,),
        101325.0,
        weight,
        residual_scale,
        2.0,
        0.0,
        (1.0,),
        "exact_component_test",
    )
    controls = core.NativeRegressionControls(
        "linear",
        max_num_iterations,
        function_tolerance,
        gradient_tolerance,
        parameter_tolerance,
    )
    return core.NativeRegressionProblem(
        "quadratic-native-contract",
        baseline.definition_fingerprint_sha256,
        (baseline,),
        compiled.fixed_parameter_fingerprints,
        (row,),
        (parameter,),
        controls,
    )
