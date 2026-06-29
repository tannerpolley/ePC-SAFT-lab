from __future__ import annotations

import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()

pytestmark = pytest.mark.native_contract


def _require_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def _payload(
    conservation_matrix: list[list[float]],
    conservation_totals: list[float],
) -> dict[str, object]:
    species_count = len(conservation_matrix[0])
    return {
        "species_labels": [f"S{index}" for index in range(species_count)],
        "conservation_labels": [f"C{index}" for index in range(len(conservation_matrix))],
        "conservation_matrix": conservation_matrix,
        "conservation_totals": conservation_totals,
    }


def test_feasible_initializer_finds_strict_positive_total_conservation_seed() -> None:
    _require_ipopt()

    result = _core._native_ce_feasible_initialization(
        _payload([[1.0, 1.0, 1.0]], [1.0])
    )

    assert result["initializer"] == "max_min_feasible_interior"
    assert result["accepted"] is True
    assert result["solver_ran"] is True
    assert result["rejection_reason"] == ""
    assert result["amounts"] == pytest.approx([1.0 / 3.0] * 3, abs=1.0e-8)
    assert result["margin"] == pytest.approx(result["minimum_amount"], abs=1.0e-9)
    assert result["margin"] > 0.0
    assert result["balance_inf_norm"] <= 1.0e-9
    assert result["active_margin_constraint_count"] == 3


def test_feasible_initializer_handles_charged_conservation_rows() -> None:
    _require_ipopt()

    result = _core._native_ce_feasible_initialization(
        _payload(
            [
                [1.0, 1.0, 1.0],
                [1.0, -1.0, 0.0],
            ],
            [1.0, 0.0],
        )
    )

    assert result["accepted"] is True
    assert result["amounts"][0] == pytest.approx(result["amounts"][1], abs=1.0e-9)
    assert sum(result["amounts"]) == pytest.approx(1.0, abs=1.0e-9)
    assert result["balance_inf_norm"] <= 1.0e-9
    assert result["minimum_amount"] > 0.0


def test_feasible_initializer_preserves_tiny_feasible_species() -> None:
    _require_ipopt()

    result = _core._native_ce_feasible_initialization(
        _payload(
            [
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 0.0],
            ],
            [1.0, 1.0e-8],
        ),
        amount_floor=1.0e-15,
    )

    assert result["accepted"] is True
    assert result["amounts"][1] == pytest.approx(1.0e-8, rel=1.0e-6, abs=1.0e-12)
    assert result["minimum_amount"] == pytest.approx(result["amounts"][1], rel=1.0e-6, abs=1.0e-12)
    assert 0.0 < result["margin"] <= 1.1e-8
    assert result["balance_inf_norm"] <= 1.0e-9


def test_feasible_initializer_rejects_infeasible_totals() -> None:
    _require_ipopt()

    result = _core._native_ce_feasible_initialization(
        _payload([[1.0, 1.0]], [-1.0])
    )

    assert result["accepted"] is False
    assert result["solver_ran"] is True
    assert result["rejection_reason"] == "initializer_solve_rejected"
    assert result["balance_inf_norm"] > 1.0e-9


def test_feasible_initializer_accepts_consistent_redundant_conservation_rows() -> None:
    _require_ipopt()

    result = _core._native_ce_feasible_initialization(
        _payload(
            [
                [1.0, 1.0],
                [1.0, 1.0],
            ],
            [1.0, 1.0],
        )
    )

    assert result["accepted"] is True
    assert result["solver_ran"] is True
    assert result["amounts"] == pytest.approx([0.5, 0.5], abs=1.0e-8)
    assert result["balance_inf_norm"] <= 1.0e-9


def test_feasible_initializer_rejects_inconsistent_dependent_conservation_rows() -> None:
    _require_ipopt()

    result = _core._native_ce_feasible_initialization(
        _payload(
            [
                [1.0, 1.0],
                [1.0, 1.0],
            ],
            [1.0, 2.0],
        )
    )

    assert result["accepted"] is False
    assert result["solver_ran"] is True
    assert result["rejection_reason"] == "initializer_solve_rejected"
    assert result["balance_inf_norm"] > 1.0e-9
