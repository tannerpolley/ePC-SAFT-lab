from __future__ import annotations

import math
from dataclasses import fields

import numpy as np
import pytest

import epcsaft
from tests.api.reactive.reactive_speciation_cases import (
    _assert_reactive_speciation_native_ipopt_dependency_required,
    _native_ipopt_compiled,
    _salt_speciation_mixture,
)


def test_reactive_speciation_builds_native_request_with_ipopt_tranche_options(monkeypatch) -> None:
    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0, 1.0]),
            "s": np.asarray([3.0, 3.0]),
            "e": np.asarray([200.0, 200.0]),
        },
        species=["A", "B"],
    )
    recorded: dict[str, object] = {}

    def fake_native(_native, request):
        recorded["request"] = request
        return {
            "success": True,
            "message": "converged",
            "composition": [0.25, 0.75],
            "activity_coefficients": [1.0, 1.0],
            "mass_balance_residuals": [0.0],
            "charge_residual": 0.0,
            "reaction_residuals": [0.0],
            "diagnostics": {
                "derivative_backend": "analytic",
                "selected_solver_backend": "native_ipopt",
                "solver_selection_reason": "explicit_request",
                "hessian_approximation": "exact",
                "hessian_backend": "analytic",
                "iteration_history_limit": 4,
                "linear_solver_requested": "mumps",
                "linear_solver_selected": "mumps",
                "acceptable_tolerance": 9.0e-7,
                "constraint_violation_tolerance": 8.0e-8,
                "dual_infeasibility_tolerance": 7.0e-8,
                "complementarity_tolerance": 6.0e-8,
                "iteration_history": [],
                "continuation_state": {
                    "variables": [0.25, 0.75],
                    "bound_lower_multipliers": [0.0, 0.0],
                    "bound_upper_multipliers": [0.0, 0.0],
                    "constraint_multipliers": [0.0],
                },
            },
        }

    monkeypatch.setattr(epcsaft._core, "_solve_chemical_equilibrium_native", fake_native)

    result = epcsaft.solve_reactive_speciation(
        species=["A", "B"],
        mixture_factory=lambda x, T, P: mix,
        T=298.15,
        P=1.0e5,
        balances={"total": {"A": 1.0, "B": 1.0}},
        totals={"total": 1.0},
        reactions=[
            epcsaft.ReactionDefinition(
                {"A": -1.0, "B": 1.0},
                log_equilibrium_constant=math.log(3.0),
                standard_state="ideal_mole_fraction",
            )
        ],
        initial_x=[0.5, 0.5],
        options=epcsaft.ReactiveSpeciationOptions(
            solver_backend="ipopt",
            hessian_mode="exact",
            ipopt_iteration_history_limit=4,
            ipopt_linear_solver="mumps",
            ipopt_acceptable_tolerance=9.0e-7,
            ipopt_constraint_violation_tolerance=8.0e-8,
            ipopt_dual_infeasibility_tolerance=7.0e-8,
            ipopt_complementarity_tolerance=6.0e-8,
            continuation_state={
                "variables": [0.5, 0.5],
                "bound_lower_multipliers": [0.0, 0.0],
                "bound_upper_multipliers": [0.0, 0.0],
                "constraint_multipliers": [0.0],
                "route_kind": "reactive_speciation",
                "species_order": ["A", "B"],
                "fixed_specs": {"fixed": ["T", "P", "totals"], "phase": "liq"},
            },
        ),
    )

    request = recorded["request"]
    assert request["options"]["hessian_mode"] == "exact"
    assert request["options"]["iteration_history_limit"] == 4
    assert request["options"]["linear_solver"] == "mumps"
    assert request["options"]["acceptable_tolerance"] == pytest.approx(9.0e-7)
    assert request["options"]["constraint_violation_tolerance"] == pytest.approx(8.0e-8)
    assert request["options"]["dual_infeasibility_tolerance"] == pytest.approx(7.0e-8)
    assert request["options"]["complementarity_tolerance"] == pytest.approx(6.0e-8)
    assert request["options"]["continuation_state"]["variables"] == pytest.approx([0.5, 0.5])
    assert result.success is True
    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["linear_solver_requested"] == "mumps"
    assert result.diagnostics["linear_solver_selected"] == "mumps"
    assert result.diagnostics["acceptable_tolerance"] == pytest.approx(9.0e-7)
    assert result.diagnostics["constraint_violation_tolerance"] == pytest.approx(8.0e-8)
    assert result.diagnostics["dual_infeasibility_tolerance"] == pytest.approx(7.0e-8)
    assert result.diagnostics["complementarity_tolerance"] == pytest.approx(6.0e-8)
    assert result.diagnostics["continuation_state"]["route_kind"] == "reactive_speciation"
    assert result.diagnostics["continuation_state"]["species_order"] == ["A", "B"]

def test_reactive_speciation_requested_ipopt_routes_ideal_speciation_when_compiled() -> None:
    from epcsaft import _core

    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0, 1.0]),
            "s": np.asarray([3.0, 3.0]),
            "e": np.asarray([200.0, 200.0]),
        },
        species=["A", "B"],
    )
    kwargs = {
        "species": ["A", "B"],
        "mixture_factory": lambda x, T, P: mix,
        "T": 298.15,
        "P": 1.0e5,
        "balances": {"total": {"A": 1.0, "B": 1.0}},
        "totals": {"total": 1.0},
        "reactions": [
            epcsaft.ReactionDefinition(
                {"A": -1.0, "B": 1.0},
                log_equilibrium_constant=math.log(3.0),
                standard_state="ideal_mole_fraction",
            )
        ],
        "initial_x": [0.5, 0.5],
        "options": epcsaft.ReactiveSpeciationOptions(solver_backend="ipopt", tolerance=1.0e-9),
    }

    if not _core._native_ipopt_smoke()["compiled"]:
        with pytest.raises(epcsaft.SolutionError, match=r"EPCSAFT_ENABLE_IPOPT=ON"):
            epcsaft.solve_reactive_speciation(**kwargs)
        return

    result = epcsaft.solve_reactive_speciation(**kwargs)

    assert result.success is True
    assert result.x["B"] / result.x["A"] == pytest.approx(3.0, rel=1.0e-7)
    assert result.diagnostics["selected_solver_backend"] == "native_ipopt"
    assert result.diagnostics["problem_class"] == "homogeneous_ideal_gibbs_speciation"
    assert result.diagnostics["jacobian_backend"] == "analytic"

def test_reactive_speciation_requested_ipopt_handles_charged_ideal_constraint_when_compiled() -> None:
    from epcsaft import _core

    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0, 1.0, 1.0]),
            "s": np.asarray([3.0, 3.0, 3.0]),
            "e": np.asarray([200.0, 200.0, 200.0]),
            "z": np.asarray([1.0, -1.0, 0.0]),
            "dielc": np.asarray([78.0, 78.0, 78.0]),
            "d_born": np.asarray([3.0, 3.0, 0.0]),
            "MW": np.asarray([20.0e-3, 20.0e-3, 40.0e-3]),
        },
        species=["C+", "A-", "N"],
    )
    kwargs = {
        "species": ["C+", "A-", "N"],
        "mixture_factory": lambda x, T, P: mix,
        "T": 298.15,
        "P": 1.0e5,
        "balances": {"formula_units": {"C+": 0.5, "A-": 0.5, "N": 1.0}},
        "totals": {"formula_units": 0.75},
        "reactions": [
            epcsaft.ReactionDefinition(
                {"C+": -1.0, "A-": -1.0, "N": 1.0},
                log_equilibrium_constant=math.log(8.0),
                standard_state="ideal_mole_fraction",
            )
        ],
        "initial_x": [0.3, 0.3, 0.4],
        "options": epcsaft.ReactiveSpeciationOptions(solver_backend="ipopt", tolerance=1.0e-9),
    }

    if not _core._native_ipopt_smoke()["compiled"]:
        with pytest.raises(epcsaft.SolutionError, match=r"EPCSAFT_ENABLE_IPOPT=ON"):
            epcsaft.solve_reactive_speciation(**kwargs)
        return

    result = epcsaft.solve_reactive_speciation(**kwargs)

    assert result.success is True
    assert result.x["C+"] == pytest.approx(0.25, rel=1.0e-7)
    assert result.x["A-"] == pytest.approx(0.25, rel=1.0e-7)
    assert result.x["N"] == pytest.approx(0.5, rel=1.0e-7)
    assert result.charge_residual == pytest.approx(0.0, abs=1.0e-10)
    assert result.diagnostics["charge_constraint_in_nlp"] is True

def test_reactive_speciation_auto_routes_ideal_speciation_to_native_ipopt_when_compiled() -> None:
    from epcsaft import _core

    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0, 1.0]),
            "s": np.asarray([3.0, 3.0]),
            "e": np.asarray([200.0, 200.0]),
        },
        species=["A", "B"],
    )
    kwargs = {
        "species": ["A", "B"],
        "mixture_factory": lambda x, T, P: mix,
        "T": 298.15,
        "P": 1.0e5,
        "balances": {"total": {"A": 1.0, "B": 1.0}},
        "totals": {"total": 1.0},
        "reactions": [
            epcsaft.ReactionDefinition(
                {"A": -1.0, "B": 1.0},
                log_equilibrium_constant=math.log(3.0),
                standard_state="ideal_mole_fraction",
            )
        ],
        "initial_x": [0.5, 0.5],
    }

    if not _core._native_ipopt_smoke()["compiled"]:
        with pytest.raises(epcsaft.SolutionError, match=r"EPCSAFT_ENABLE_IPOPT=ON"):
            epcsaft.solve_reactive_speciation(**kwargs)
        return

    result = epcsaft.solve_reactive_speciation(**kwargs)

    assert result.success is True
    assert result.diagnostics["requested_solver_backend"] == "auto"
    assert result.diagnostics["selected_solver_backend"] == "native_ipopt"
    assert result.diagnostics["solver_selection_reason"] == "auto_selected_native_ipopt"
    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["hessian_backend"] == "analytic"
    assert result.diagnostics["exact_hessian_available"] is True
    assert result.diagnostics["eval_h_calls"] > 0

def test_reactive_speciation_requested_ipopt_routes_nonideal_speciation_when_compiled() -> None:
    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0, 1.0]),
            "s": np.asarray([3.0, 3.0]),
            "e": np.asarray([200.0, 200.0]),
        },
        species=["A", "B"],
    )
    kwargs = {
        "species": ["A", "B"],
        "mixture_factory": lambda x, T, P: mix,
        "T": 298.15,
        "P": 1.0e5,
        "balances": {"total": {"A": 1.0, "B": 1.0}},
        "totals": {"total": 1.0},
        "reactions": [
            epcsaft.ReactionDefinition(
                {"A": -1.0, "B": 1.0},
                log_equilibrium_constant=math.log(3.0),
                standard_state="mole_fraction_activity",
            )
        ],
        "initial_x": [0.5, 0.5],
        "options": epcsaft.ReactiveSpeciationOptions(solver_backend="ipopt", tolerance=1.0e-9),
    }

    if not _native_ipopt_compiled():
        with pytest.raises(epcsaft.SolutionError) as excinfo:
            epcsaft.solve_reactive_speciation(**kwargs)
        _assert_reactive_speciation_native_ipopt_dependency_required(excinfo)
        return

    result = epcsaft.solve_reactive_speciation(**kwargs)

    assert result.success is True
    assert result.x["B"] / result.x["A"] == pytest.approx(3.0, rel=1.0e-7)
    assert result.diagnostics["problem_class"] == "homogeneous_nonideal_residual_speciation"
    assert result.diagnostics["derivative_backend"] == "cppad_explicit_density"
    assert result.diagnostics["density_backend"] == "explicit_log_density_pressure_constraint"
    assert result.diagnostics["implicit_sensitivity_backend"] == "cppad_explicit_density_implicit"
    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["exact_hessian_available"] is True
    assert result.diagnostics["hessian_backend"] != "limited-memory"
    assert result.diagnostics["eval_h_calls"] > 0
