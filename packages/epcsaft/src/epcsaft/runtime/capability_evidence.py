"""Registered provider capability evidence."""

from __future__ import annotations

from typing import Final

DERIVATIVE_COVERAGE_ROWS: Final[tuple[dict[str, object], ...]] = (
    {
        "row_family": "electrolyte_property",
        "subsystem": "electrolyte",
        "quantity": "born_parameter_liquid",
        "derivative": "parameter_sensitivity",
        "backend": "cppad",
        "supported": True,
        "classification": "production_supported",
        "reason": "public Born parameter derivative reporting is CppAD-backed for d_born and f_solv",
        "tests": ("packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py",),
    },
)
