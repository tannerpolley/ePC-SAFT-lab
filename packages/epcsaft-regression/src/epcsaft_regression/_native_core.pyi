from __future__ import annotations

from collections.abc import Sequence
from typing import Any

class NativeFittedParameter:
    def __init__(
        self,
        key: str,
        target_kind: str,
        first_index: int,
        second_index: int,
        start: float,
        lower: float,
        upper: float,
    ) -> None: ...
    key: str
    target_kind: str
    first_index: int
    second_index: int
    start: float
    lower: float
    upper: float


class NativeRegressionControls:
    def __init__(
        self,
        loss: str,
        max_num_iterations: int,
        function_tolerance: float,
        gradient_tolerance: float,
        parameter_tolerance: float,
    ) -> None: ...
    loss: str
    max_num_iterations: int
    function_tolerance: float
    gradient_tolerance: float
    parameter_tolerance: float


class NativeRegressionRow:
    def __init__(
        self,
        row_id: str,
        source_id: str,
        source_kind: str,
        target_family: str,
        provider_handle_indices: Sequence[int],
        pressure_Pa: float,
        weight: float,
        residual_scale: float,
        target_value: float,
        model_intercept: float,
        parameter_coefficients: Sequence[float],
        derivative_owner: str,
    ) -> None: ...
    row_id: str
    source_id: str
    source_kind: str
    target_family: str
    provider_handle_indices: tuple[int, ...]
    pressure_Pa: float
    weight: float
    residual_scale: float
    target_value: float
    model_intercept: float
    parameter_coefficients: tuple[float, ...]
    derivative_owner: str


class NativeRegressionProblem:
    def __init__(
        self,
        dataset_id: str,
        provider_definition_fingerprint: str,
        provider_handles: Sequence[Any],
        fixed_parameter_fingerprints: Sequence[tuple[str, str]],
        rows: Sequence[NativeRegressionRow],
        parameters: Sequence[NativeFittedParameter],
        controls: NativeRegressionControls,
    ) -> None: ...
    dataset_id: str
    provider_definition_fingerprint: str
    provider_handles: tuple[Any, ...]
    fixed_parameter_fingerprints: tuple[tuple[str, str], ...]
    rows: tuple[NativeRegressionRow, ...]
    parameters: tuple[NativeFittedParameter, ...]
    controls: NativeRegressionControls
    problem_fingerprint: str
    problem_receipt: dict[str, Any]
    row_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    snapshot_fingerprints: tuple[str, ...]
    parameter_keys: tuple[str, ...]


def _evaluate_regression(
    problem: NativeRegressionProblem,
    parameter_values: Sequence[float],
) -> dict[str, Any]: ...
def _solve_regression(problem: NativeRegressionProblem) -> dict[str, Any]: ...
def _regression_acceptance_from_summary(
    termination_type: str,
    solution_usable: bool,
    initial_cost: float,
    final_cost: float,
    finite_outputs: bool,
    derivative_complete: bool,
) -> bool: ...
def _native_ceres_smoke() -> dict[str, Any]: ...
def _native_provider_resolved_input_handle_probe(handle: Any) -> dict[str, Any]: ...
