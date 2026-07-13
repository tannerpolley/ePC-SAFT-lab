"""Public configured regression workflow."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Real
from typing import Any

from epcsaft import InputError, Mixture

from .controls import RegressionControls
from .native_adapter import _evaluate_regression, _solve_regression
from .parameters import FittedParameter
from .problem import CompiledRegressionProblem, compile_regression_problem
from .results import FitProblem, FitResult, RegressionEvaluation, RegressionReceipt
from .targets import TargetDataset


@dataclass(slots=True)
class Regression:
    """A regression workflow configured by one mixture and one control record."""

    mixture: Mixture
    controls: RegressionControls

    def __init__(self, mixture: Mixture, *, controls: RegressionControls) -> None:
        if not isinstance(mixture, Mixture):
            raise InputError("Regression requires a Mixture.")
        if not isinstance(controls, RegressionControls):
            raise InputError("Regression requires configured RegressionControls.")
        self.mixture = mixture
        self.controls = controls

    def compile(
        self,
        dataset: TargetDataset,
        *,
        parameters: tuple[FittedParameter, ...],
    ) -> CompiledRegressionProblem:
        """Compile this workflow's exact configured inputs without solving."""

        return compile_regression_problem(
            mixture=self.mixture,
            dataset=dataset,
            parameters=parameters,
            controls=self.controls,
        )

    def fit(
        self,
        dataset: TargetDataset,
        *,
        parameters: tuple[FittedParameter, ...],
    ) -> FitResult:
        """Compile and solve one strict dataset through the native receipt path."""

        if not isinstance(dataset, TargetDataset):
            raise InputError("Regression.fit requires a TargetDataset.")
        compiled = self.compile(dataset, parameters=parameters)
        native_result = _solve_regression(compiled)
        receipt = RegressionReceipt.from_native(native_result, operation="fit")
        problem = FitProblem._from_receipt(compiled, receipt)
        return FitResult(problem=problem, receipt=receipt)

    def evaluate(
        self,
        problem: FitProblem,
        *,
        parameter_values: Mapping[str, float],
    ) -> RegressionEvaluation:
        """Evaluate an exact fitted problem at an explicit keyed parameter vector."""

        if not isinstance(problem, FitProblem):
            raise InputError("Regression.evaluate requires a FitProblem.")
        if (
            problem.provider_definition_fingerprint
            != self.mixture.resolved_model_input.fingerprint_sha256
        ):
            raise InputError("FitProblem does not belong to this configured mixture.")
        if problem.controls != self.controls.to_dict():
            raise InputError("FitProblem does not use this workflow's configured controls.")
        values = _ordered_parameter_values(parameter_values, problem.parameter_keys)
        native_result = _evaluate_regression(problem._compiled, values)
        receipt = RegressionReceipt.from_native(native_result, operation="evaluate")
        return RegressionEvaluation(problem=problem, receipt=receipt)


def _ordered_parameter_values(
    parameter_values: Mapping[str, float],
    parameter_keys: tuple[str, ...],
) -> tuple[float, ...]:
    if not isinstance(parameter_values, Mapping) or any(
        type(key) is not str for key in parameter_values
    ):
        raise InputError("parameter_values must be a string-keyed mapping.")
    provided = set(parameter_values)
    expected = set(parameter_keys)
    missing = sorted(expected - provided)
    unknown = sorted(provided - expected)
    if missing or unknown:
        details = []
        if missing:
            details.append("missing parameter key(s): " + ", ".join(missing))
        if unknown:
            details.append("unknown parameter key(s): " + ", ".join(unknown))
        raise InputError("; ".join(details) + ".")
    ordered = tuple(
        _finite_parameter_value(parameter_values[key], key) for key in parameter_keys
    )
    return ordered


def _finite_parameter_value(value: Any, key: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"parameter value for {key!r} must be finite.")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"parameter value for {key!r} must be finite.")
    return result


__all__ = ["Regression"]
