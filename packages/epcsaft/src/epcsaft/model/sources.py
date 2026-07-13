"""Shared helpers for parameter source identity, copies, and option loading."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

import numpy as np


def copy_parameter_value(value: Any) -> Any:
    """Copy parameter payload values without aliasing mutable arrays or containers."""

    if isinstance(value, np.ndarray):
        return np.asarray(value).copy()
    if isinstance(value, Mapping):
        return {str(key): copy_parameter_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [copy_parameter_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(copy_parameter_value(item) for item in value)
    return copy.deepcopy(value)


def copy_parameter_mapping(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    return {str(key): copy_parameter_value(value) for key, value in payload.items()}
