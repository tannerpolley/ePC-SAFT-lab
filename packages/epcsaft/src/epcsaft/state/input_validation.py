"""Strict validation for already-canonical provider state inputs."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from .._types import InputError


def validate_canonical_composition(
    composition: Sequence[float],
    component_count: int,
) -> np.ndarray:
    """Copy and validate a mole-fraction vector without changing its values."""

    if type(component_count) is not int or component_count <= 0:
        raise InputError("canonical composition requires a positive component count.")
    try:
        canonical = np.array(composition, dtype=float, copy=True)
    except (TypeError, ValueError) as exc:
        raise InputError("canonical composition must contain finite numeric values.") from exc
    if canonical.ndim != 1:
        raise InputError("canonical composition must be one-dimensional.")
    if canonical.size != component_count:
        raise InputError(
            "canonical composition length must exactly match the resolved component order."
        )
    if not np.all(np.isfinite(canonical)):
        raise InputError("canonical composition must contain only finite values.")
    if np.any(canonical < 0.0):
        raise InputError("canonical composition must contain only non-negative values.")
    if abs(math.fsum(float(value) for value in canonical) - 1.0) > 1.0e-7:
        raise InputError("canonical composition must sum to one without normalization.")
    canonical.setflags(write=False)
    return canonical
