from __future__ import annotations

import inspect
import os
from types import MappingProxyType

import numpy as np
import pytest

import epcsaft
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
import epcsaft_equilibrium as equilibrium_module
from equilibrium_support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_FLASH_Z,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_RHO,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)
from equilibrium_support.equilibrium_cases import (
    GROSS_2002_LLE_FEED,
    GROSS_2002_METHANOL_LEAN_LIQUID,
    GROSS_2002_METHANOL_RICH_LIQUID,
    GROSS_2002_PRESSURE_PA,
    GROSS_2002_TEMPERATURE_K,
    gross_2002_associating_parameter_set,
)

GROSS_2002_FIGURE2_TEMPERATURE_K = 373.15
GROSS_2002_FIGURE2_LIQUID_X = [0.35, 0.65]
GROSS_2002_FIGURE2_VAPOR_Y = [0.35, 0.65]


def test_workflow_object_is_constructed_with_problem_spec() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(mixture, route="bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X)

    assert equilibrium.mixture is mixture
    assert equilibrium.problem.route == "bubble_pressure"


ROUTE_CONSTRUCTOR_CASES = (
    ("bubble_pressure", {"T": HYDROCARBON_T, "x": HYDROCARBON_LIQUID_X}, "neutral_bubble_p"),
    ("bubble_temperature", {"P": HYDROCARBON_BUBBLE_P, "x": HYDROCARBON_LIQUID_X}, "neutral_bubble_t"),
    ("dew_pressure", {"T": HYDROCARBON_T, "y": HYDROCARBON_VAPOR_Y}, "neutral_dew_p"),
    ("dew_temperature", {"P": HYDROCARBON_BUBBLE_P, "y": HYDROCARBON_VAPOR_Y}, "neutral_dew_t"),
    ("flash", {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": HYDROCARBON_FLASH_Z}, "neutral_tp_flash"),
)


@pytest.mark.parametrize(("route", "kwargs", "problem_kind"), ROUTE_CONSTRUCTOR_CASES)
def test_equilibrium_constructor_configures_route_before_solve(
    route: str, kwargs: dict[str, object], problem_kind: str
) -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(mixture, route=route, **kwargs)
    structure = equilibrium.structure()

    expected_selector_route = "neutral_tp_flash" if route == "flash" else route
    assert problem_kind.startswith("neutral_")
    assert equilibrium.problem.route == route
    assert equilibrium.problem.selector_route == expected_selector_route
    assert structure.route == route
    assert structure.selector_route == expected_selector_route
    assert structure.activation_key


def test_equilibrium_requires_constructor_route() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    with pytest.raises((TypeError, epcsaft.InputError), match="route"):
        equilibrium_module.Equilibrium(mixture)


@pytest.mark.parametrize(
    ("route", "valid_kwargs", "missing_key", "forbidden_key", "forbidden_value"),
    (
        ("bubble_pressure", {"T": HYDROCARBON_T, "x": HYDROCARBON_LIQUID_X}, "T", "P", HYDROCARBON_BUBBLE_P),
        (
            "bubble_temperature",
            {"P": HYDROCARBON_BUBBLE_P, "x": HYDROCARBON_LIQUID_X},
            "P",
            "T",
            HYDROCARBON_T,
        ),
        ("dew_pressure", {"T": HYDROCARBON_T, "y": HYDROCARBON_VAPOR_Y}, "y", "x", HYDROCARBON_LIQUID_X),
        (
            "dew_temperature",
            {"P": HYDROCARBON_BUBBLE_P, "y": HYDROCARBON_VAPOR_Y},
            "P",
            "T",
            HYDROCARBON_T,
        ),
        (
            "flash",
            {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": HYDROCARBON_FLASH_Z},
            "z",
            "x",
            HYDROCARBON_LIQUID_X,
        ),
        (
            "lle",
            {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": HYDROCARBON_FLASH_Z},
            "z",
            "x",
            HYDROCARBON_LIQUID_X,
        ),
    ),
)
def test_constructor_enforces_route_required_and_forbidden_specs(
    route: str,
    valid_kwargs: dict[str, object],
    missing_key: str,
    forbidden_key: str,
    forbidden_value: object,
) -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    missing_payload = dict(valid_kwargs)
    missing_payload.pop(missing_key)
    with pytest.raises(epcsaft.InputError, match=missing_key):
        equilibrium_module.Equilibrium(mixture, route=route, **missing_payload)

    forbidden_payload = dict(valid_kwargs)
    forbidden_payload[forbidden_key] = forbidden_value
    with pytest.raises(epcsaft.InputError, match=forbidden_key):
        equilibrium_module.Equilibrium(mixture, route=route, **forbidden_payload)


def test_solver_options_live_on_solve_not_constructor() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    with pytest.raises((TypeError, epcsaft.InputError), match="solver_options"):
        equilibrium_module.Equilibrium(
            mixture,
            route="bubble_pressure",
            T=HYDROCARBON_T,
            x=HYDROCARBON_LIQUID_X,
            solver_options={"max_iterations": 200},
        )

    assert hasattr(equilibrium_module, "EquilibriumSolverOptions")
    options = equilibrium_module.EquilibriumSolverOptions(
        max_iterations=200,
        tolerance=1.0e-8,
        ipopt_iteration_history_limit=4,
    )

    _skip_without_ipopt()
    result = equilibrium_module.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    ).solve(solver_options=options)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_p")


def test_solve_signature_rejects_legacy_route_specs() -> None:
    signature = inspect.signature(equilibrium_module.Equilibrium.solve)

    for removed in ("route", "T", "P", "x", "y", "z"):
        assert removed not in signature.parameters


def test_constructor_configured_result_exposes_named_phase_helpers() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    result = equilibrium_module.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    ).solve(solver_options={"max_iterations": 200, "tolerance": 1.0e-8, "ipopt_iteration_history_limit": 4})

    assert isinstance(result.phases, MappingProxyType)
    assert tuple(result.phases) == ("liquid", "vapor")
    assert result.phase_labels == ["liquid", "vapor"]
    assert result.phases["liquid"].composition == pytest.approx(HYDROCARBON_LIQUID_X, rel=1.0e-4, abs=5.0e-7)
    assert result.phases["vapor"].composition == pytest.approx(HYDROCARBON_VAPOR_Y, rel=1.0e-4, abs=5.0e-7)
    with pytest.raises((KeyError, TypeError)):
        _ = result.phases[0]

    assert result.pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
    assert result.x == pytest.approx(HYDROCARBON_LIQUID_X, rel=1.0e-4, abs=5.0e-7)
    assert result.y == pytest.approx(HYDROCARBON_VAPOR_Y, rel=1.0e-4, abs=5.0e-7)
    assert result.liquid_fraction == pytest.approx(result.phases["liquid"].phase_fraction)
    assert result.vapor_fraction == pytest.approx(result.phases["vapor"].phase_fraction)
    with pytest.raises(AttributeError):
        _ = result.z


def test_result_diagnostics_are_deeply_read_only() -> None:
    liquid = equilibrium_module.EquilibriumPhase(
        label="liquid",
        composition=[1.0],
        density=100.0,
        temperature=300.0,
        pressure=101325.0,
        phase_fraction=0.5,
        diagnostics={"inner": {"status": "accepted"}, "history": [{"iteration": 1}]},
    )
    vapor = equilibrium_module.EquilibriumPhase(
        label="vapor",
        composition=[1.0],
        density=1.0,
        temperature=300.0,
        pressure=101325.0,
        phase_fraction=0.5,
    )
    result = equilibrium_module.EquilibriumResult(
        backend="native",
        problem_kind="neutral_bubble_p",
        phases={"liquid": liquid, "vapor": vapor},
        stable=True,
        split_detected=True,
        diagnostics={"postsolve_certification": {"accepted": True}, "history": [{"iteration": 1}]},
        route="bubble_pressure",
        selector_route="bubble_pressure",
        composition_role="liquid",
    )

    assert isinstance(result.diagnostics, MappingProxyType)
    assert isinstance(result.diagnostics["postsolve_certification"], MappingProxyType)
    assert isinstance(result.diagnostics["history"], tuple)
    assert isinstance(result.diagnostics["history"][0], MappingProxyType)
    assert isinstance(result.phases["liquid"].diagnostics, MappingProxyType)
    assert isinstance(result.phases["liquid"].diagnostics["inner"], MappingProxyType)

    with pytest.raises(TypeError):
        result.diagnostics["mutated"] = True  # type: ignore[index]
    with pytest.raises(TypeError):
        result.diagnostics["postsolve_certification"]["accepted"] = False  # type: ignore[index]
    with pytest.raises(TypeError):
        result.diagnostics["history"][0]["iteration"] = 2  # type: ignore[index]
    with pytest.raises(AttributeError):
        result.diagnostics["history"].append({"iteration": 2})  # type: ignore[attr-defined]
    with pytest.raises(TypeError):
        result.phases["liquid"].diagnostics["mutated"] = True  # type: ignore[index]
    with pytest.raises(TypeError):
        result.phases["liquid"].diagnostics["inner"]["status"] = "mutated"  # type: ignore[index]


def test_flash_result_exposes_feed_composition_helper(hydrocarbon_flash_result) -> None:
    result = hydrocarbon_flash_result
    assert result.z == pytest.approx(HYDROCARBON_FLASH_Z)
    assert result.liquid_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
    assert result.vapor_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)


def test_equilibrium_problem_and_structure_are_read_only_metadata() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    equilibrium = equilibrium_module.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    )

    with pytest.raises(AttributeError):
        equilibrium.problem = object()  # type: ignore[misc]

    assert equilibrium.problem.route == "bubble_pressure"
    assert equilibrium.problem.selector_route == "bubble_pressure"
    structure = equilibrium.structure()

    with pytest.raises((AttributeError, TypeError)):
        structure.route = "dew_pressure"  # type: ignore[misc]

    payload = structure.to_dict()
    assert payload["route"] == "bubble_pressure"
    assert payload["selector_route"] == "bubble_pressure"
    assert payload["knowns"] == ["T", "x"]
    assert "P" in payload["unknowns"]
    assert "y" in payload["unknowns"]
    assert payload["composition_role"] == "liquid"
    assert payload["activation_key"] == "bubble_dew_derived_routes"
    assert payload["expected_phase_keys"] == ["liquid", "vapor"]
    assert "phase_equilibrium" in payload["residual_families"]
    assert "phase_volume_gap" in payload["hard_constraint_families"]
    assert payload["dof"]["available"] is False


def test_equilibrium_problem_fixed_specs_are_deeply_read_only() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    equilibrium = equilibrium_module.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    )

    fixed_x = equilibrium.problem.fixed_specs["x"]
    assert fixed_x.flags.writeable is False

    with pytest.raises(ValueError):
        fixed_x[0] = 0.9

    assert equilibrium.problem.fixed_specs["x"] == pytest.approx(HYDROCARBON_LIQUID_X)


def test_solver_options_reject_ignored_backend_selection_knobs() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    equilibrium = equilibrium_module.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    )

    for key in ("backend", "derivative_backend", "jacobian_backend", "solver_backend"):
        with pytest.raises(epcsaft.InputError, match=key):
            equilibrium.solve(solver_options={key: "auto"})

    solver_options_signature = inspect.signature(equilibrium_module.EquilibriumSolverOptions)
    assert "backend" not in solver_options_signature.parameters
    assert "derivative_backend" not in solver_options_signature.parameters
    assert "jacobian_backend" not in solver_options_signature.parameters
    assert "solver_backend" not in solver_options_signature.parameters
    assert "ipopt_print_level" in solver_options_signature.parameters
    with pytest.raises(epcsaft.InputError, match="ipopt_print_level"):
        equilibrium.solve(solver_options={"ipopt_print_level": -1})


def test_equilibrium_lle_route_configures_neutral_liquid_pair_structure() -> None:
    mixture = epcsaft.Mixture(_neutral_lle_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(mixture, route="lle", T=225.0, P=1.0e6, z=[0.5, 0.5])
    structure = equilibrium.structure()

    assert equilibrium.problem.route == "lle"
    assert equilibrium.problem.selector_route == "neutral_lle"
    assert equilibrium.problem.expected_phase_keys == ("liquid1", "liquid2")
    assert structure.activation_key == "neutral_lle"
    assert structure.expected_phase_keys == ("liquid1", "liquid2")
    assert structure.hard_constraint_families == (
        "material_balance",
        "phase_pressure_consistency",
        "phase_distance",
    )
    assert "phase_volume_gap" not in structure.hard_constraint_families


def test_equilibrium_multiphase_route_configures_explicit_phase_set_structure() -> None:
    mixture = epcsaft.Mixture(_symmetric_ternary_nonassociating_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(
        mixture,
        route="multiphase",
        T=200.0,
        P=1.0e6,
        z=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        phase_kinds=["liquid", "liquid", "liquid"],
    )
    structure = equilibrium.structure()

    assert equilibrium.problem.route == "multiphase"
    assert equilibrium.problem.selector_route == "neutral_multiphase_nonassoc"
    assert equilibrium.problem.activation_key == "neutral_multiphase_nonassoc"
    assert equilibrium.problem.expected_phase_keys == ("liquid1", "liquid2", "liquid3")
    assert equilibrium.problem.fixed_specs["phase_kinds"] == ("liquid", "liquid", "liquid")
    assert structure.route == "multiphase"
    assert structure.selector_route == "neutral_multiphase_nonassoc"
    assert structure.activation_key == "neutral_multiphase_nonassoc"
    assert structure.expected_phase_keys == ("liquid1", "liquid2", "liquid3")
    assert structure.residual_families == (
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    )
    assert structure.hard_constraint_families == ("material_balance", "phase_pressure_consistency")


def test_equilibrium_multiphase_route_requires_explicit_phase_kinds() -> None:
    mixture = epcsaft.Mixture(_symmetric_ternary_nonassociating_parameter_set())

    with pytest.raises(epcsaft.InputError, match="phase_kinds"):
        equilibrium_module.Equilibrium(
            mixture,
            route="multiphase",
            T=200.0,
            P=1.0e6,
            z=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        )


@pytest.mark.parametrize(
    "phase_kinds",
    (
        ["liquid", "liquid"],
        ["liquid", "solid", "liquid"],
        ["liquid", "", "liquid"],
        ["liquid", object(), "liquid"],
    ),
)
def test_equilibrium_multiphase_route_rejects_malformed_phase_kinds(phase_kinds: list[object]) -> None:
    mixture = epcsaft.Mixture(_symmetric_ternary_nonassociating_parameter_set())

    with pytest.raises(epcsaft.InputError, match="phase_kinds"):
        equilibrium_module.Equilibrium(
            mixture,
            route="multiphase",
            T=200.0,
            P=1.0e6,
            z=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
            phase_kinds=phase_kinds,
        )


def test_equilibrium_multiphase_route_requires_feed_composition_only() -> None:
    mixture = epcsaft.Mixture(_symmetric_ternary_nonassociating_parameter_set())

    with pytest.raises(epcsaft.InputError, match="z"):
        equilibrium_module.Equilibrium(
            mixture,
            route="multiphase",
            T=200.0,
            P=1.0e6,
            x=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
            phase_kinds=["liquid", "liquid", "liquid"],
        )


@pytest.mark.parametrize("route", ("flash", "lle"))
def test_equilibrium_fixed_shape_feed_routes_reject_phase_kinds(route: str) -> None:
    mixture = epcsaft.Mixture(_neutral_lle_parameter_set())

    with pytest.raises(epcsaft.InputError, match="phase_kinds"):
        equilibrium_module.Equilibrium(
            mixture,
            route=route,
            T=225.0,
            P=1.0e6,
            z=[0.5, 0.5],
            phase_kinds=["liquid", "liquid"],
        )


def test_equilibrium_lle_route_returns_named_liquid_phase_helpers() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(_neutral_lle_parameter_set())

    result = equilibrium_module.Equilibrium(mixture, route="lle", T=225.0, P=1.0e6, z=[0.5, 0.5]).solve(
        solver_options={
            "max_iterations": 260,
            "tolerance": 1.0e-6,
            "ipopt_iteration_history_limit": 8,
            "ipopt_acceptable_tolerance": 1.0e-7,
            "ipopt_constraint_violation_tolerance": 1.0e-7,
            "ipopt_dual_infeasibility_tolerance": 1.0e-8,
            "ipopt_complementarity_tolerance": 1.0e-8,
        }
    )

    assert result.problem_kind == "neutral_lle"
    assert result.phase_labels == ["liquid1", "liquid2"]
    assert tuple(result.phases) == ("liquid1", "liquid2")
    assert set(result.phase_compositions) == {"liquid1", "liquid2"}
    assert set(result.phase_fractions) == {"liquid1", "liquid2"}
    assert result.phase("liquid1") is result.phases["liquid1"]
    assert result.phase("liquid2") is result.phases["liquid2"]
    assert sum(result.phase_fractions.values()) == pytest.approx(1.0, rel=1.0e-8)
    assert np.max(np.abs(result.phase_compositions["liquid1"] - result.phase_compositions["liquid2"])) >= 1.0e-6
    assert result.z == pytest.approx([0.5, 0.5])
    with pytest.raises(AttributeError):
        _ = result.x
    with pytest.raises(AttributeError):
        _ = result.y
    with pytest.raises(AttributeError):
        _ = result.liquid_fraction
    with pytest.raises(AttributeError):
        _ = result.vapor_fraction
    payload = result.to_dict()
    assert payload["phase_labels"] == ["liquid1", "liquid2"]
    assert payload["x"] is None
    assert payload["y"] is None
    assert payload["liquid_fraction"] is None
    assert payload["vapor_fraction"] is None
    assert result.diagnostics["activation_plan"]["family_key"] == "neutral_lle"
    assert result.diagnostics["route_status"] == "production_accepted"
    assert result.diagnostics["solver_accepted"] is True
    assert result.diagnostics["solver_status"] == "success"
    assert result.diagnostics["application_status"] == "solve_succeeded"
    assert result.diagnostics["postsolve_accepted"] is True
    assert result.diagnostics["option_profile"] == "held_refinement"
    assert result.diagnostics["physical_evidence"]["phase_labels"] == ("liquid1", "liquid2")
    assert result.diagnostics["physical_evidence"]["phase_roles"] == ("liquid", "liquid")
    assert result.diagnostics["phase_labels"] == ("liquid1", "liquid2")
    assert result.diagnostics["phase_roles"] == ("liquid", "liquid")
    assert result.route_diagnostics.constraint_families == (
        "material_balance",
        "phase_pressure_consistency",
        "phase_distance",
    )


def test_equilibrium_lle_admits_source_backed_gross_2002_associating_fixture() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(gross_2002_associating_parameter_set())
    equilibrium = equilibrium_module.Equilibrium(
        mixture,
        route="lle",
        T=GROSS_2002_TEMPERATURE_K,
        P=GROSS_2002_PRESSURE_PA,
        z=GROSS_2002_LLE_FEED,
    )

    structure = equilibrium.structure()
    assert structure.activation_key == "neutral_lle"
    assert structure.expected_phase_keys == ("liquid1", "liquid2")

    result = equilibrium.solve(
        solver_options={
            "max_iterations": 320,
            "tolerance": 1.0e-6,
            "ipopt_iteration_history_limit": 12,
            "ipopt_acceptable_tolerance": 1.0e-7,
            "ipopt_constraint_violation_tolerance": 1.0e-7,
            "ipopt_dual_infeasibility_tolerance": 1.0e-8,
            "ipopt_complementarity_tolerance": 1.0e-8,
        }
    )

    diagnostics = result.diagnostics
    assert result.route == "lle"
    assert result.selector_route == "neutral_lle"
    assert result.problem_kind == "neutral_lle"
    assert result.phase_labels == ["liquid1", "liquid2"]
    assert result.z == pytest.approx(GROSS_2002_LLE_FEED)
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["postsolve_accepted"] is True
    assert diagnostics["activation_plan"]["family_key"] == "neutral_lle"

    phase_compositions = list(result.phase_compositions.values())
    methanol_values = sorted(float(composition[0]) for composition in phase_compositions)
    assert methanol_values[0] == pytest.approx(GROSS_2002_METHANOL_LEAN_LIQUID[0], abs=0.12)
    assert methanol_values[1] == pytest.approx(GROSS_2002_METHANOL_RICH_LIQUID[0], abs=0.12)
    assert abs(methanol_values[1] - methanol_values[0]) > 0.5


@pytest.mark.parametrize(
    ("route", "kwargs", "problem_kind"),
    (
        (
            "bubble_pressure",
            {"T": GROSS_2002_FIGURE2_TEMPERATURE_K, "x": GROSS_2002_FIGURE2_LIQUID_X},
            "neutral_bubble_p",
        ),
        (
            "dew_pressure",
            {"T": GROSS_2002_FIGURE2_TEMPERATURE_K, "y": GROSS_2002_FIGURE2_VAPOR_Y},
            "neutral_dew_p",
        ),
    ),
)
def test_equilibrium_vle_admits_source_backed_gross_2002_figure2_associating_binary(
    route: str,
    kwargs: dict[str, object],
    problem_kind: str,
) -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(_gross_2002_figure2_associating_vle_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(mixture, route=route, **kwargs)
    structure = equilibrium.structure()
    assert structure.activation_key == "bubble_dew_derived_routes"
    assert structure.expected_phase_keys == ("liquid", "vapor")

    result = equilibrium.solve(
        solver_options={
            "max_iterations": 320,
            "tolerance": 1.0e-6,
            "ipopt_iteration_history_limit": 12,
            "ipopt_acceptable_tolerance": 1.0e-7,
            "ipopt_constraint_violation_tolerance": 1.0e-7,
            "ipopt_dual_infeasibility_tolerance": 1.0e-8,
            "ipopt_complementarity_tolerance": 1.0e-8,
        }
    )

    diagnostics = result.diagnostics
    assert result.route == route
    assert result.selector_route == route
    assert result.problem_kind == problem_kind
    assert result.phase_labels == ["liquid", "vapor"]
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["postsolve_accepted"] is True


def test_equilibrium_multiphase_route_returns_public_three_phase_result() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(_symmetric_ternary_nonassociating_parameter_set())

    result = equilibrium_module.Equilibrium(
        mixture,
        route="multiphase",
        T=200.0,
        P=1.0e6,
        z=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        phase_kinds=["liquid", "liquid", "liquid"],
    ).solve(
        solver_options={
            "max_iterations": 320,
            "tolerance": 1.0e-8,
            "ipopt_iteration_history_limit": 12,
            "ipopt_acceptable_tolerance": 1.0e-8,
            "ipopt_constraint_violation_tolerance": 1.0e-8,
            "ipopt_dual_infeasibility_tolerance": 1.0e-8,
            "ipopt_complementarity_tolerance": 1.0e-8,
        }
    )

    diagnostics = result.diagnostics
    assert result.route == "multiphase"
    assert result.selector_route == "neutral_multiphase_nonassoc"
    assert result.problem_kind == "neutral_multiphase_nonassoc"
    assert result.phase_labels == ["liquid1", "liquid2", "liquid3"]
    assert tuple(result.phases) == ("liquid1", "liquid2", "liquid3")
    assert result.z == pytest.approx([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
    assert sum(result.phase_fractions.values()) == pytest.approx(1.0, rel=1.0e-8)
    assert all(value > 0.0 for value in result.phase_fractions.values())
    for composition in result.phase_compositions.values():
        assert float(np.sum(composition)) == pytest.approx(1.0, rel=1.0e-8)
        assert np.all(composition > 0.0)
    with pytest.raises(AttributeError):
        _ = result.x
    with pytest.raises(AttributeError):
        _ = result.y
    with pytest.raises(AttributeError):
        _ = result.liquid_fraction
    with pytest.raises(AttributeError):
        _ = result.vapor_fraction
    payload = result.to_dict()
    assert payload["phase_labels"] == ["liquid1", "liquid2", "liquid3"]
    assert payload["x"] is None
    assert payload["y"] is None
    assert payload["phase_fractions"] == pytest.approx(dict(result.phase_fractions))
    assert diagnostics["route_refinement_kind"] == "strict_fugacity_residual"
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["hessian_backend"] == "cppad_phase_system_plus_reduced_fugacity_residual"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["residual_exact_jacobian_available"] is True
    assert diagnostics["residual_exact_hessian_available"] is True
    assert diagnostics["postsolve_accepted"] is True
    assert diagnostics["postsolve_certification"]["accepted"] is True
    assert diagnostics["ln_fugacity_consistency_norm"] <= 1.0e-6
    assert diagnostics["material_balance_norm"] <= 1.0e-8
    assert diagnostics["pressure_consistency_norm"] <= 1.0e-3
    assert diagnostics["phase_distance"] > 0.0
    assert diagnostics["seed_name"] == "held_stage_ii_dual_loop_candidate_set"
    assert all(attempt["solver_status"] != "max_iterations_exceeded" for attempt in diagnostics["seed_attempts"])


@pytest.mark.parametrize(
    ("route", "kwargs"),
    (
        ("bubble_pressure", {"T": HYDROCARBON_T, "x": [0.35, 0.65]}),
        ("bubble_temperature", {"P": HYDROCARBON_BUBBLE_P, "x": [0.35, 0.65]}),
        ("dew_pressure", {"T": HYDROCARBON_T, "y": [0.35, 0.65]}),
        ("dew_temperature", {"P": HYDROCARBON_BUBBLE_P, "y": [0.35, 0.65]}),
        ("flash", {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": [0.35, 0.65]}),
        ("lle", {"T": 300.0, "P": 1.0e6, "z": [0.5, 0.5]}),
        (
            "multiphase",
            {
                "T": 200.0,
                "P": 1.0e6,
                "z": [0.5, 0.5],
                "phase_kinds": ["liquid", "liquid", "liquid"],
            },
        ),
    ),
)
def test_equilibrium_constructor_rejects_associating_inputs_before_selector_dispatch(
    route: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(epcsaft.InputError, match=r"associating GFPE"):
        equilibrium_module.Equilibrium(
            epcsaft.Mixture(_associating_parameter_set()),
            route=route,
            **kwargs,
        )


def test_equilibrium_lle_rejects_gross_2002_associating_fixture_without_source_proof() -> None:
    with pytest.raises(epcsaft.InputError, match=r"source-backed Gross/Sadowski 2002"):
        equilibrium_module.Equilibrium(
            epcsaft.Mixture(gross_2002_associating_parameter_set(source_backed=False)),
            route="lle",
            T=GROSS_2002_TEMPERATURE_K,
            P=GROSS_2002_PRESSURE_PA,
            z=GROSS_2002_LLE_FEED,
        )


@pytest.mark.parametrize(
    ("route", "kwargs"),
    (
        ("flash", {"T": GROSS_2002_TEMPERATURE_K, "P": GROSS_2002_PRESSURE_PA, "z": GROSS_2002_LLE_FEED}),
        (
            "multiphase",
            {
                "T": GROSS_2002_TEMPERATURE_K,
                "P": GROSS_2002_PRESSURE_PA,
                "z": GROSS_2002_LLE_FEED,
                "phase_kinds": ["liquid", "liquid", "liquid"],
            },
        ),
    ),
)
def test_equilibrium_rejects_source_backed_associating_scope_outside_two_phase_lle(
    route: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(epcsaft.InputError, match=r"neutral two-phase LLE"):
        equilibrium_module.Equilibrium(
            epcsaft.Mixture(gross_2002_associating_parameter_set()),
            route=route,
            **kwargs,
        )


def test_equilibrium_lle_rejects_ionic_associating_inputs_before_public_associating_gate() -> None:
    with pytest.raises(epcsaft.InputError, match="neutral mixtures"):
        equilibrium_module.Equilibrium(
            epcsaft.Mixture(_ionic_associating_parameter_set()),
            route="lle",
            T=300.0,
            P=1.0e5,
            z=[0.8, 0.1, 0.1],
        )


def test_equilibrium_lle_constructor_rejects_ionic_inputs() -> None:
    for route, kwargs in (
        ("lle", {"T": 300.0, "P": 1.0e5, "z": [0.8, 0.1, 0.1]}),
        (
            "multiphase",
            {
                "T": 200.0,
                "P": 1.0e6,
                "z": [0.8, 0.1, 0.1],
                "phase_kinds": ["liquid", "liquid", "liquid"],
            },
        ),
    ):
        with pytest.raises(epcsaft.InputError, match="neutral mixtures"):
            equilibrium_module.Equilibrium(
                epcsaft.Mixture(_ionic_parameter_set()),
                route=route,
                **kwargs,
            )


def _equilibrium() -> equilibrium_module.Equilibrium:
    return equilibrium_module.Equilibrium(
        epcsaft.Mixture(hydrocarbon_parameter_set()), route="bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X
    )


def _configured_equilibrium(route: str, **kwargs: object) -> equilibrium_module.Equilibrium:
    return equilibrium_module.Equilibrium(epcsaft.Mixture(hydrocarbon_parameter_set()), route=route, **kwargs)


def _solver_options() -> dict[str, object]:
    options = {"max_iterations": 200, "tolerance": 1.0e-8, "ipopt_iteration_history_limit": 4}
    if _equilibrium_debug_enabled():
        options["ipopt_print_level"] = 5
        options["ipopt_iteration_history_limit"] = 50
    return options


def _iteration_limit_solver_options() -> dict[str, object]:
    options = {
        "max_iterations": 1,
        "tolerance": 1.0e-8,
        "ipopt_iteration_history_limit": 4,
        "ipopt_print_level": 0,
    }
    if _equilibrium_debug_enabled():
        options["ipopt_print_level"] = 5
        options["ipopt_iteration_history_limit"] = 50
    return options


def _equilibrium_debug_enabled() -> bool:
    return os.environ.get("EPCSAFT_EQUILIBRIUM_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _assert_hydrocarbon_pair(result, *, problem_kind: str) -> None:
    diagnostics = result.diagnostics
    assert result.problem_kind == problem_kind
    assert result.phases["liquid"].composition == pytest.approx(HYDROCARBON_LIQUID_X, rel=1.0e-4, abs=5.0e-7)
    assert result.phases["vapor"].composition == pytest.approx(HYDROCARBON_VAPOR_Y, rel=1.0e-4, abs=5.0e-7)
    assert result.phases["liquid"].temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
    assert result.phases["vapor"].temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
    assert result.phases["liquid"].pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.phases["vapor"].pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
    assert result.phases["liquid"].density == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=1.0e-4)
    assert result.phases["vapor"].density == pytest.approx(HYDROCARBON_VAPOR_RHO, rel=1.0e-4)
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["solver_accepted"] is True
    assert diagnostics["max_iterations"] == 200
    assert diagnostics["solver_status"] != "max_iterations_exceeded"
    assert diagnostics["application_status"] != "maximum_iterations_exceeded"
    assert diagnostics["eval_h_calls"] > 0
    assert diagnostics["ipopt_print_level"] == (5 if _equilibrium_debug_enabled() else 0)
    assert diagnostics["iteration_count"] > 0
    assert 0 < diagnostics["iteration_history_size"] <= diagnostics["iteration_history_limit"]
    assert len(diagnostics["iteration_history"]) == diagnostics["iteration_history_size"]
    assert diagnostics["postsolve_certification"]["accepted"] is True
    assert diagnostics["physical_evidence"]["phase_labels"] == ("liquid", "vapor")
    assert diagnostics["physical_evidence"]["phase_roles"] == ("liquid", "vapor")
    assert diagnostics["phase_labels"] == ("liquid", "vapor")
    assert diagnostics["phase_roles"] == ("liquid", "vapor")
    if problem_kind == "neutral_tp_flash":
        assert diagnostics["solver_status"] == "success"
        assert diagnostics["application_status"] == "solve_succeeded"
        assert diagnostics["postsolve_certification"]["continuous_tpd_status"] == "not_requested"
        assert diagnostics["postsolve_certification"]["deterministic_candidate_count"] > 0
        assert diagnostics["postsolve_certification"]["continuous_tpd_start_count"] == 0
        assert diagnostics["postsolve_certification"]["continuous_tpd_solve_count"] == 0
        assert diagnostics["postsolve_certification"]["continuous_tpd_converged_count"] == 0
        assert diagnostics["postsolve_certification"]["held_stage_i_status"] == "not_requested"


def test_equilibrium_flash_rejects_ipopt_iteration_limit_before_postsolve() -> None:
    _skip_without_ipopt()

    with pytest.raises(epcsaft.SolutionError) as exc_info:
        _configured_equilibrium("flash", T=HYDROCARBON_T, P=HYDROCARBON_BUBBLE_P, z=HYDROCARBON_FLASH_Z).solve(
            solver_options=_iteration_limit_solver_options()
        )

    diagnostics = exc_info.value.diagnostics
    assert diagnostics is not None
    assert diagnostics["route_status"] == "solver_rejected"
    assert diagnostics["solver_status"] == "max_iterations_exceeded"
    assert diagnostics["application_status"] == "maximum_iterations_exceeded"
    assert diagnostics["solver_accepted"] is False
    assert diagnostics["route_accepted"] is False
    assert diagnostics["max_iterations"] == 1
    assert diagnostics["iteration_count"] == 1
    assert diagnostics["ipopt_print_level"] == (5 if _equilibrium_debug_enabled() else 0)
    assert diagnostics["iteration_history_limit"] == (50 if _equilibrium_debug_enabled() else 4)
    assert 0 < diagnostics["iteration_history_size"] <= diagnostics["iteration_history_limit"]
    assert len(diagnostics["iteration_history"]) == diagnostics["iteration_history_size"]
    assert diagnostics["seed_attempt_count"] >= 1
    assert diagnostics["seed_attempt_solver_accepted_count"] == 0
    assert diagnostics["seed_attempt_route_accepted_count"] == 0
    for attempt in diagnostics["seed_attempts"]:
        assert attempt["route_status"] == "solver_rejected"
        assert attempt["solver_status"] == "max_iterations_exceeded"
        assert attempt["application_status"] == "maximum_iterations_exceeded"
        assert attempt["solver_accepted"] is False
        assert attempt["route_accepted"] is False
        assert attempt["max_iterations"] == 1
        assert attempt["iteration_count"] == 1


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def _neutral_lle_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "m": np.asarray([1.0, 2.0]),
            "s": np.asarray([3.5, 4.0]),
            "e": np.asarray([150.0, 250.0]),
            "MW": np.asarray([0.016, 0.030]),
            "k_ij": np.asarray([[0.0, 0.5], [0.5, 0.0]]),
        },
        species=["A", "B"],
    )


def _symmetric_ternary_nonassociating_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "m": np.asarray([1.5, 1.5, 1.5], dtype=float),
            "s": np.asarray([3.7, 3.7, 3.7], dtype=float),
            "e": np.asarray([220.0, 220.0, 220.0], dtype=float),
            "MW": np.asarray([0.016, 0.030, 0.044], dtype=float),
            "k_ij": np.asarray(
                [
                    [0.0, 0.8, 0.8],
                    [0.8, 0.0, 0.8],
                    [0.8, 0.8, 0.0],
                ],
                dtype=float,
            ),
        },
        species=["A", "B", "C"],
    )


def _associating_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([32.042e-3, 84.147e-3]),
            "m": np.asarray([1.5255, 2.5303]),
            "s": np.asarray([3.2300, 3.8499]),
            "e": np.asarray([188.90, 278.11]),
            "e_assoc": np.asarray([2899.5, 0.0]),
            "vol_a": np.asarray([0.035176, 0.0]),
            "assoc_scheme": ["2B", None],
            "k_ij": np.asarray([[0.0, 0.051], [0.051, 0.0]]),
            "z": np.asarray([0.0, 0.0]),
            "dielc": np.asarray([33.05, 2.02]),
        },
        species=["Methanol", "Cyclohexane"],
    )


def _ionic_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([18.01528e-3, 22.98e-3, 35.45e-3]),
            "m": np.asarray([1.2047, 1.0, 1.0]),
            "s": np.asarray([2.7927, 2.8232, 2.7560]),
            "e": np.asarray([353.95, 230.0, 170.0]),
            "z": np.asarray([0.0, 1.0, -1.0]),
            "dielc": np.asarray([78.09, 8.0, 8.0]),
            "d_born": np.asarray([0.0, 3.445, 4.1]),
            "f_solv": np.asarray([1.5, 1.0, 1.0]),
        },
        species=["H2O", "Na+", "Cl-"],
    )


def _ionic_associating_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([18.01528e-3, 22.98e-3, 35.45e-3]),
            "m": np.asarray([1.2047, 1.0, 1.0]),
            "s": np.asarray([2.7927, 2.8232, 2.7560]),
            "e": np.asarray([353.95, 230.0, 170.0]),
            "e_assoc": np.asarray([2425.7, 0.0, 0.0]),
            "vol_a": np.asarray([0.04509, 0.0, 0.0]),
            "assoc_scheme": ["2B", None, None],
            "z": np.asarray([0.0, 1.0, -1.0]),
            "dielc": np.asarray([78.09, 8.0, 8.0]),
            "d_born": np.asarray([0.0, 3.445, 4.1]),
            "f_solv": np.asarray([1.5, 1.0, 1.0]),
        },
        species=["H2O", "Na+", "Cl-"],
    )


def _gross_2002_figure2_associating_vle_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    metadata = {
        "source": "Gross/Sadowski 2002 Figure 2",
        "paper": "Gross and Sadowski 2002",
        "table": "Gross 2002 Figure 2 caption plus Gross 2001 pure-component table",
        "figure": "Figure 2",
        "source_path": "analyses/paper_validation/2002_gross",
        "source_backed": source_backed,
        "caption_system": "methanol-isobutane",
        "table_002_conflict": "methanol-isobutanol",
        "pure_isobutane_source": (
            "docs/papers/md/ePC-SAFT-Literature/"
            "Gross, Sadowski - 2001 - PC-SAFT An equation of state based on a perturbation theory for chain molec.md"
        ),
    }
    return epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([32.042e-3, 58.123e-3]),
            "m": np.asarray([1.5255, 2.2616]),
            "s": np.asarray([3.2300, 3.7574]),
            "e": np.asarray([188.90, 216.53]),
            "e_assoc": np.asarray([2899.5, 0.0]),
            "vol_a": np.asarray([0.035176, 0.0]),
            "assoc_scheme": ["2B", None],
            "k_ij": np.asarray([[0.0, 0.05], [0.05, 0.0]]),
            "z": np.asarray([0.0, 0.0]),
            "dielc": np.asarray([1.0, 1.0]),
        },
        species=["Methanol", "Isobutane"],
        metadata=metadata,
    )


def test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X).solve(
        solver_options=_solver_options()
    )

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_p")


def test_equilibrium_bubble_temperature_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("bubble_temperature", P=HYDROCARBON_BUBBLE_P, x=HYDROCARBON_LIQUID_X).solve(
        solver_options=_solver_options()
    )

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_t")


def test_equilibrium_dew_pressure_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("dew_pressure", T=HYDROCARBON_T, y=HYDROCARBON_VAPOR_Y).solve(
        solver_options=_solver_options()
    )

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_p")


def test_equilibrium_dew_temperature_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("dew_temperature", P=HYDROCARBON_BUBBLE_P, y=HYDROCARBON_VAPOR_Y).solve(
        solver_options=_solver_options()
    )

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_t")


def test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point(hydrocarbon_flash_result) -> None:
    result = hydrocarbon_flash_result
    _assert_hydrocarbon_pair(result, problem_kind="neutral_tp_flash")
    assert result.split_detected is True
    assert result.phases["liquid"].phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
    assert result.phases["vapor"].phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
    assert result.diagnostics["activation_compiler"] == "activation_plan"
    assert result.diagnostics["activation_plan"]["family_key"] == "neutral_tp_flash"
    species_count = len(HYDROCARBON_FLASH_Z)
    local_variable_count = species_count + 1
    assert [list(row) for row in result.diagnostics["variable_layout"]["phase_amount_indices"]] == [
        list(range(phase * local_variable_count, phase * local_variable_count + species_count)) for phase in range(2)
    ]
    assert list(result.diagnostics["variable_layout"]["phase_volume_indices"]) == [
        phase * local_variable_count + species_count for phase in range(2)
    ]


@pytest.fixture(scope="module")
def hydrocarbon_flash_result():
    _skip_without_ipopt()
    return _configured_equilibrium("flash", T=HYDROCARBON_T, P=HYDROCARBON_BUBBLE_P, z=HYDROCARBON_FLASH_Z).solve(
        solver_options=_solver_options()
    )
