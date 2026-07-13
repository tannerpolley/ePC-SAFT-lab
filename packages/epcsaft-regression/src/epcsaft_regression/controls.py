"""Typed controls for one compiled native regression problem."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from numbers import Real
from typing import Any

from epcsaft import InputError


class LossKind(str, Enum):
    """Closed loss functions admitted by the first native contract."""

    LINEAR = "linear"


@dataclass(frozen=True, slots=True)
class RegressionControls:
    """Complete explicit Ceres controls without inferred values."""

    loss: LossKind
    max_num_iterations: int
    function_tolerance: float
    gradient_tolerance: float
    parameter_tolerance: float

    def __post_init__(self) -> None:
        if not isinstance(self.loss, LossKind):
            raise InputError("loss must be a LossKind.")
        if type(self.max_num_iterations) is not int or self.max_num_iterations <= 0:
            raise InputError("max_num_iterations must be a positive integer.")
        for field_name in (
            "function_tolerance",
            "gradient_tolerance",
            "parameter_tolerance",
        ):
            value = _positive_float(getattr(self, field_name), field_name)
            object.__setattr__(self, field_name, value)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> RegressionControls:
        """Parse the complete strict control record."""

        values = _exact_mapping(
            payload,
            {
                "loss",
                "max_num_iterations",
                "function_tolerance",
                "gradient_tolerance",
                "parameter_tolerance",
            },
        )
        try:
            loss = LossKind(values["loss"])
        except (TypeError, ValueError) as exc:
            raise InputError("loss must be a LossKind admitted by the native contract.") from exc
        return cls(
            loss=loss,
            max_num_iterations=values["max_num_iterations"],
            function_tolerance=values["function_tolerance"],
            gradient_tolerance=values["gradient_tolerance"],
            parameter_tolerance=values["parameter_tolerance"],
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "loss": self.loss.value,
            "max_num_iterations": self.max_num_iterations,
            "function_tolerance": self.function_tolerance,
            "gradient_tolerance": self.gradient_tolerance,
            "parameter_tolerance": self.parameter_tolerance,
        }


def _positive_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"{field_name} must be finite and positive.")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise InputError(f"{field_name} must be finite and positive.")
    return result


def _exact_mapping(payload: Mapping[str, Any], expected: set[str]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise InputError("regression controls must be a mapping.")
    if any(type(key) is not str for key in payload):
        raise InputError("regression control keys must be strings.")
    unknown = sorted(set(payload) - expected)
    if unknown:
        raise InputError(f"unknown control key(s): {', '.join(unknown)}.")
    missing = sorted(expected - set(payload))
    if missing:
        raise InputError(f"missing control key(s): {', '.join(missing)}.")
    return dict(payload)
