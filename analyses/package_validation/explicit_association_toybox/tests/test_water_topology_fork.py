from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.water_topology_fork import (
    summarize_water_topology_fork,
)


def test_summarize_water_topology_fork_keeps_topology_and_residual_columns() -> None:
    rows = summarize_water_topology_fork(
        [
            {
                "case_id": "water_assigned_3b_provider_default",
                "assigned_topology": "3B",
                "rigorous_topology": "4C",
                "temperature_k": 298.15,
                "pressure_residual_mpa": 120.0,
                "z_residual_abs": 0.2,
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
            }
        ]
    )

    assert rows[0]["speedup_vs_exact_implicit"] == pytest.approx(4.0)
    assert rows[0]["water_diagnostic_role"] == "fixed_state_warning"
