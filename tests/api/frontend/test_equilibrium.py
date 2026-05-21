from __future__ import annotations

import inspect
from types import MappingProxyType

import pytest

import epcsaft
import epcsaft._core as _core
import epcsaft.equilibrium as equilibrium_module
from tests.support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_FLASH_Z,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_RHO,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)


def test_workflow_object_is_constructed_with_problem_spec() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    equilibrium = epcsaft.Equilibrium(mixture, route="bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X)

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
def test_equilibrium_constructor_configures_route_before_solve(route: str, kwargs: dict[str, object], problem_kind: str) -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    result = epcsaft.Equilibrium(mixture, route=route, **kwargs).solve(
        solver_options={
            "max_iterations": 200,
            "tolerance": 1.0e-8,
            "ipopt_iteration_history_limit": 4,
        }
    )

    _assert_hydrocarbon_pair(result, problem_kind=problem_kind)


def test_equilibrium_requires_constructor_route() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    with pytest.raises((TypeError, epcsaft.InputError), match="route"):
        epcsaft.Equilibrium(mixture)


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
        ("flash", {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": HYDROCARBON_FLASH_Z}, "z", "x", HYDROCARBON_LIQUID_X),
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
        epcsaft.Equilibrium(mixture, route=route, **missing_payload)

    forbidden_payload = dict(valid_kwargs)
    forbidden_payload[forbidden_key] = forbidden_value
    with pytest.raises(epcsaft.InputError, match=forbidden_key):
        epcsaft.Equilibrium(mixture, route=route, **forbidden_payload)


def test_solver_options_live_on_solve_not_constructor() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    with pytest.raises((TypeError, epcsaft.InputError), match="solver_options"):
        epcsaft.Equilibrium(
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
    result = epcsaft.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    ).solve(solver_options=options)

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_p")


def test_solve_signature_rejects_legacy_route_specs() -> None:
    signature = inspect.signature(epcsaft.Equilibrium.solve)

    for removed in ("route", "T", "P", "x", "y", "z"):
        assert removed not in signature.parameters


def test_constructor_configured_result_exposes_named_phase_helpers() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    result = epcsaft.Equilibrium(
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


def test_flash_result_exposes_feed_composition_helper() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    result = epcsaft.Equilibrium(
        mixture,
        route="flash",
        T=HYDROCARBON_T,
        P=HYDROCARBON_BUBBLE_P,
        z=HYDROCARBON_FLASH_Z,
    ).solve(solver_options={"max_iterations": 200, "tolerance": 1.0e-8, "ipopt_iteration_history_limit": 4})

    assert result.z == pytest.approx(HYDROCARBON_FLASH_Z)
    assert result.liquid_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
    assert result.vapor_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)


def test_equilibrium_problem_and_structure_are_read_only_metadata() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    equilibrium = epcsaft.Equilibrium(
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
    equilibrium = epcsaft.Equilibrium(
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
    equilibrium = epcsaft.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=HYDROCARBON_T,
        x=HYDROCARBON_LIQUID_X,
    )

    for key in ("jacobian_backend", "solver_backend"):
        with pytest.raises(epcsaft.InputError, match=key):
            equilibrium.solve(solver_options={key: "auto"})

    solver_options_signature = inspect.signature(equilibrium_module.EquilibriumSolverOptions)
    assert "jacobian_backend" not in solver_options_signature.parameters
    assert "solver_backend" not in solver_options_signature.parameters


def _equilibrium() -> epcsaft.Equilibrium:
    return epcsaft.Equilibrium(epcsaft.Mixture(hydrocarbon_parameter_set()), route="bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X)


def _configured_equilibrium(route: str, **kwargs: object) -> epcsaft.Equilibrium:
    return epcsaft.Equilibrium(epcsaft.Mixture(hydrocarbon_parameter_set()), route=route, **kwargs)


def _solver_options() -> dict[str, object]:
    return {"max_iterations": 200, "tolerance": 1.0e-8, "ipopt_iteration_history_limit": 4}


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
    assert diagnostics["eval_h_calls"] > 0
    assert diagnostics["postsolve_certification"]["accepted"] is True


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X).solve(solver_options=_solver_options())

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_p")


def test_equilibrium_bubble_temperature_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("bubble_temperature", P=HYDROCARBON_BUBBLE_P, x=HYDROCARBON_LIQUID_X).solve(solver_options=_solver_options())

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_t")


def test_equilibrium_dew_pressure_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("dew_pressure", T=HYDROCARBON_T, y=HYDROCARBON_VAPOR_Y).solve(solver_options=_solver_options())

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_p")


def test_equilibrium_dew_temperature_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("dew_temperature", P=HYDROCARBON_BUBBLE_P, y=HYDROCARBON_VAPOR_Y).solve(solver_options=_solver_options())

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_t")


def test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("flash", T=HYDROCARBON_T, P=HYDROCARBON_BUBBLE_P, z=HYDROCARBON_FLASH_Z).solve(solver_options=_solver_options())

    _assert_hydrocarbon_pair(result, problem_kind="neutral_tp_flash")
    assert result.split_detected is True
    assert result.phases["liquid"].phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
    assert result.phases["vapor"].phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
