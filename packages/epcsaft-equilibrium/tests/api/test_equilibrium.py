from __future__ import annotations

import inspect
import os
from types import MappingProxyType

import epcsaft
import numpy as np
import pytest
from epcsaft.model.parameters import (
    ConstantInteractionRecord,
    InteractionProvenance,
    PureRecord,
    StructuralZeroPolicy,
)
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
import epcsaft_equilibrium as equilibrium_module
import epcsaft_equilibrium.workflows as workflows_module
from equilibrium_support.equilibrium_cases import (
    GROSS_2002_LLE_FEED,
    GROSS_2002_TEMPERATURE_K,
    gross_2002_associating_parameter_set,
)
from equilibrium_support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_RHO,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)

GROSS_2002_FIGURE2_TEMPERATURE_K = 373.15
GROSS_2002_FIGURE2_LIQUID_X = [0.35, 0.65]
GROSS_2002_FIGURE2_VAPOR_Y = [0.35, 0.65]


def test_workflow_object_is_constructed_with_problem_spec() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(
        mixture, route="bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X
    )

    assert equilibrium.mixture is mixture
    assert equilibrium.problem.route == "bubble_pressure"


ROUTE_CONSTRUCTOR_CASES = (
    ("bubble_pressure", {"T": HYDROCARBON_T, "x": HYDROCARBON_LIQUID_X}, "neutral_bubble_p"),
    ("dew_pressure", {"T": HYDROCARBON_T, "y": HYDROCARBON_VAPOR_Y}, "neutral_dew_p"),
)


@pytest.mark.parametrize(("route", "kwargs", "problem_kind"), ROUTE_CONSTRUCTOR_CASES)
def test_equilibrium_constructor_configures_route_before_solve(
    route: str, kwargs: dict[str, object], problem_kind: str
) -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    equilibrium = equilibrium_module.Equilibrium(mixture, route=route, **kwargs)
    structure = equilibrium.structure()

    assert problem_kind.startswith("neutral_")
    assert equilibrium.problem.route == route
    assert equilibrium.problem.selector_route == route
    assert structure.route == route
    assert structure.selector_route == route
    assert structure.activation_key


def test_equilibrium_requires_constructor_route() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    with pytest.raises((TypeError, epcsaft.InputError), match="route"):
        equilibrium_module.Equilibrium(mixture)


@pytest.mark.parametrize(
    ("route", "kwargs"),
    (
        ("bubble_temperature", {"P": HYDROCARBON_BUBBLE_P, "x": HYDROCARBON_LIQUID_X}),
        ("dew_temperature", {"P": HYDROCARBON_BUBBLE_P, "y": HYDROCARBON_VAPOR_Y}),
        ("flash", {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": [0.5, 0.5]}),
        ("lle", {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": [0.5, 0.5]}),
    ),
)
def test_unproven_routes_are_rejected_before_native_selector_dispatch(
    monkeypatch: pytest.MonkeyPatch,
    route: str,
    kwargs: dict[str, object],
) -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())
    monkeypatch.setattr(
        workflows_module,
        "extension_native_core",
        lambda: pytest.fail("closed route reached native selector dispatch"),
    )

    with pytest.raises(epcsaft.InputError, match=f"Unknown equilibrium route '{route}'"):
        equilibrium_module.Equilibrium(mixture, route=route, **kwargs)


@pytest.mark.parametrize(
    ("route", "valid_kwargs", "missing_key", "forbidden_key", "forbidden_value"),
    (
        ("bubble_pressure", {"T": HYDROCARBON_T, "x": HYDROCARBON_LIQUID_X}, "T", "P", HYDROCARBON_BUBBLE_P),
        ("dew_pressure", {"T": HYDROCARBON_T, "y": HYDROCARBON_VAPOR_Y}, "y", "x", HYDROCARBON_LIQUID_X),
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


def test_equilibrium_public_constructor_has_no_phase_kinds_escape_hatch() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    with pytest.raises(TypeError, match="phase_kinds"):
        equilibrium_module.Equilibrium(
            mixture,
            route="bubble_pressure",
            T=HYDROCARBON_T,
            x=HYDROCARBON_LIQUID_X,
            phase_kinds=["liquid", "liquid"],
        )


@pytest.mark.parametrize(
    ("parameter_builder_name", "route", "kwargs", "problem_kind"),
    (
        (
            "_gross_2002_figure2_associating_vle_parameter_set",
            "bubble_pressure",
            {"T": GROSS_2002_FIGURE2_TEMPERATURE_K, "x": GROSS_2002_FIGURE2_LIQUID_X},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure2_associating_vle_parameter_set",
            "dew_pressure",
            {"T": GROSS_2002_FIGURE2_TEMPERATURE_K, "y": GROSS_2002_FIGURE2_VAPOR_Y},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure3_associating_vle_parameter_set",
            "bubble_pressure",
            {"T": 360.0, "x": [0.2, 0.8]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure3_associating_vle_parameter_set",
            "dew_pressure",
            {"T": 360.0, "y": [0.2, 0.8]},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure4_associating_vle_parameter_set",
            "bubble_pressure",
            {"T": 313.15, "x": [0.8, 0.2]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure4_associating_vle_parameter_set",
            "dew_pressure",
            {"T": 313.15, "y": [0.8, 0.2]},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure5_1propanol_benzene_parameter_set",
            "bubble_pressure",
            {"T": 313.15, "x": [0.7, 0.3]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure5_1propanol_benzene_parameter_set",
            "dew_pressure",
            {"T": 313.15, "y": [0.7, 0.3]},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure5_2propanol_benzene_parameter_set",
            "bubble_pressure",
            {"T": 313.15, "x": [0.7, 0.3]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure5_2propanol_benzene_parameter_set",
            "dew_pressure",
            {"T": 313.15, "y": [0.7, 0.3]},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure6_1butanol_butane_parameter_set",
            "bubble_pressure",
            {"T": 373.15, "x": [0.5, 0.5]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure6_1butanol_butane_parameter_set",
            "dew_pressure",
            {"T": 373.15, "y": [0.5, 0.5]},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure7_ethanol_butane_parameter_set",
            "bubble_pressure",
            {"T": 373.15, "x": [0.5, 0.5]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure7_ethanol_butane_parameter_set",
            "dew_pressure",
            {"T": 373.15, "y": [0.5, 0.5]},
            "neutral_dew_p",
        ),
        (
            "gross_2002_associating_parameter_set",
            "bubble_pressure",
            {"T": GROSS_2002_TEMPERATURE_K, "x": GROSS_2002_LLE_FEED},
            "neutral_bubble_p",
        ),
        (
            "gross_2002_associating_parameter_set",
            "dew_pressure",
            {"T": GROSS_2002_TEMPERATURE_K, "y": GROSS_2002_LLE_FEED},
            "neutral_dew_p",
        ),
        (
            "_gross_2002_figure9_methanol_1octanol_parameter_set",
            "bubble_pressure",
            {"T": 393.15, "x": [0.4, 0.6]},
            "neutral_bubble_p",
        ),
        (
            "_gross_2002_figure9_methanol_1octanol_parameter_set",
            "dew_pressure",
            {"T": 393.15, "y": [0.4, 0.6]},
            "neutral_dew_p",
        ),
    ),
)
def test_equilibrium_vle_admits_source_backed_gross_2002_associating_binary(
    parameter_builder_name: str,
    route: str,
    kwargs: dict[str, object],
    problem_kind: str,
) -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(globals()[parameter_builder_name]())

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
    readiness = diagnostics["parameter_readiness"]
    assert readiness["associating_admission_proof_route"] == (
        f"associating_neutral_vle_gross_2002_{route}_figures_2_9_"
        "public_exact_hessian"
    )
    assert readiness["associating_admission_fixture"] == "Gross/Sadowski 2002 Figures 2-9 associating binary VLE"
    assert readiness["associating_admission_backend"] == "cppad_implicit_association"


@pytest.mark.parametrize(
    ("temperature_k", "x_butane"),
    (
        (433.15, 0.46),
        (473.15, 0.24),
    ),
)
def test_equilibrium_vle_admits_supercritical_figure6_branch_points(
    temperature_k: float,
    x_butane: float,
) -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(_gross_2002_figure6_1butanol_butane_parameter_set())

    result = equilibrium_module.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=temperature_k,
        x=[1.0 - x_butane, x_butane],
    ).solve(
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
    assert result.route == "bubble_pressure"
    assert result.problem_kind == "neutral_bubble_p"
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["postsolve_accepted"] is True


@pytest.mark.parametrize(
    ("parameter_builder_name", "route", "kwargs"),
    (
        (
            "_gross_2002_figure2_associating_vle_parameter_set",
            "bubble_pressure",
            {"T": GROSS_2002_FIGURE2_TEMPERATURE_K, "x": GROSS_2002_FIGURE2_LIQUID_X},
        ),
        (
            "_gross_2002_figure2_associating_vle_parameter_set",
            "dew_pressure",
            {"T": GROSS_2002_FIGURE2_TEMPERATURE_K, "y": GROSS_2002_FIGURE2_VAPOR_Y},
        ),
    ),
)
def test_equilibrium_vle_rejects_associating_binary_without_source_backed_proof(
    parameter_builder_name: str,
    route: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(epcsaft.InputError, match=r"source-backed Gross/Sadowski 2002 Figures 2-9"):
        equilibrium_module.Equilibrium(
            epcsaft.Mixture(globals()[parameter_builder_name](source_backed=False)),
            route=route,
            **kwargs,
        )


@pytest.mark.parametrize(
    ("route", "kwargs"),
    (
        ("bubble_pressure", {"T": HYDROCARBON_T, "x": [0.35, 0.65]}),
        ("dew_pressure", {"T": HYDROCARBON_T, "y": [0.35, 0.65]}),
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


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def _parameter_set_from_records(
    *,
    species: list[str],
    mw: list[float],
    m: list[float],
    sigma: list[float],
    epsilon_k: list[float],
    charge: list[float],
    epsilon_k_ab: list[float],
    kappa_ab: list[float],
    association_scheme: list[str | None],
    relative_permittivity: list[float],
    born_diameter: list[float],
    solvation_factor: list[float],
    k_ij: float,
    metadata: dict[str, object] | None = None,
) -> epcsaft.ParameterSet:
    pure_records = tuple(
        PureRecord(
            component=component,
            molar_mass=mw_i,
            m=m_i,
            sigma=sigma_i,
            epsilon_k=epsilon_k_i,
            charge=charge_i,
            epsilon_k_ab=epsilon_k_ab_i,
            kappa_ab=kappa_ab_i,
            association_scheme=scheme_i,
            relative_permittivity=relative_permittivity_i,
            born_diameter=born_diameter_i,
            solvation_factor=solvation_factor_i,
        )
        for (
            component,
            mw_i,
            m_i,
            sigma_i,
            epsilon_k_i,
            charge_i,
            epsilon_k_ab_i,
            kappa_ab_i,
            scheme_i,
            relative_permittivity_i,
            born_diameter_i,
            solvation_factor_i,
        ) in zip(
            species,
            mw,
            m,
            sigma,
            epsilon_k,
            charge,
            epsilon_k_ab,
            kappa_ab,
            association_scheme,
            relative_permittivity,
            born_diameter,
            solvation_factor,
            strict=True,
        )
    )
    interactions = (
        ConstantInteractionRecord(
            "k_ij",
            (species[0], species[1]),
            k_ij,
            InteractionProvenance(
                "literature",
                str((metadata or {}).get("source", "Gross and Sadowski 2002")),
            ),
        ),
    )
    policies = tuple(
        StructuralZeroPolicy(
            family,
            (species[0], species[1]),
            reason,
            InteractionProvenance("model_structural_zero", source),
        )
        for family, reason, source in (
            (
                "l_ij",
                "The pair uses the uncorrected Lorentz diameter rule.",
                "Lorentz diameter rule / EqID sigma_mixing",
            ),
            (
                "k_hb_ij",
                "The Gross 2002 base association-volume combining rule has no binary correction.",
                "Gross and Sadowski 2002 Eq. 3 / EqID kappa_assoc_mixing",
            ),
        )
    )
    return epcsaft.ParameterSet.from_records(
        pure_records,
        interactions,
        interaction_policies=policies,
        metadata=metadata,
    )


def _associating_parameter_set() -> epcsaft.ParameterSet:
    return _parameter_set_from_records(
        species=["Methanol", "Cyclohexane"],
        mw=[32.042e-3, 84.147e-3],
        m=[1.5255, 2.5303],
        sigma=[3.2300, 3.8499],
        epsilon_k=[188.90, 278.11],
        charge=[0.0, 0.0],
        epsilon_k_ab=[2899.5, 0.0],
        kappa_ab=[0.035176, 0.0],
        association_scheme=["2B", None],
        relative_permittivity=[33.05, 2.02],
        born_diameter=[0.0, 0.0],
        solvation_factor=[1.0, 1.0],
        k_ij=0.051,
        metadata={"source": "Gross and Sadowski 2002 Figure 8", "source_backed": True},
    )


def _gross_2002_figure2_associating_vle_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["Methanol", "Isobutane"],
        source="Gross/Sadowski 2002 Figure 2",
        metadata_extra={
            "caption_system": "methanol-isobutane",
            "table_002_conflict": "methanol-isobutanol",
            "pure_isobutane_source": (
                "docs/papers/md/ePC-SAFT-Literature/"
                "Gross, Sadowski - 2001 - PC-SAFT An equation of state based on a perturbation theory for chain molec.md"
            ),
        },
        mw=[32.042e-3, 58.123e-3],
        m=[1.5255, 2.2616],
        s=[3.2300, 3.7574],
        e=[188.90, 216.53],
        e_assoc=[2899.5, 0.0],
        vol_a=[0.035176, 0.0],
        kij=0.05,
        source_backed=source_backed,
    )


def _gross_2002_figure3_associating_vle_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["1-Propanol", "Ethylbenzene"],
        source="Gross/Sadowski 2002 Figure 3",
        metadata_extra={"reference_system": "1-propanol-ethylbenzene"},
        mw=[60.096e-3, 106.167e-3],
        m=[2.9997, 3.0799],
        s=[3.2522, 3.7974],
        e=[233.40, 287.35],
        e_assoc=[2276.8, 0.0],
        vol_a=[0.015268, 0.0],
        kij=0.023,
        source_backed=source_backed,
    )


def _gross_2002_figure4_associating_vle_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["1-Pentanol", "Benzene"],
        source="Gross/Sadowski 2002 Figure 4",
        metadata_extra={"reference_system": "1-pentanol-benzene"},
        mw=[88.15e-3, 78.114e-3],
        m=[3.6260, 2.4653],
        s=[3.4508, 3.6478],
        e=[247.28, 287.35],
        e_assoc=[2252.1, 0.0],
        vol_a=[0.010319, 0.0],
        kij=0.0135,
        source_backed=source_backed,
    )


def _gross_2002_figure5_1propanol_benzene_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["1-Propanol", "Benzene"],
        source="Gross/Sadowski 2002 Figure 5",
        metadata_extra={"reference_system": "1-propanol-benzene"},
        mw=[60.096e-3, 78.114e-3],
        m=[2.9997, 2.4653],
        s=[3.2522, 3.6478],
        e=[233.40, 287.35],
        e_assoc=[2276.8, 0.0],
        vol_a=[0.015268, 0.0],
        kij=0.020,
        source_backed=source_backed,
    )


def _gross_2002_figure5_2propanol_benzene_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["2-Propanol", "Benzene"],
        source="Gross/Sadowski 2002 Figure 5",
        metadata_extra={"reference_system": "2-propanol-benzene"},
        mw=[60.096e-3, 78.114e-3],
        m=[3.0929, 2.4653],
        s=[3.2085, 3.6478],
        e=[208.42, 287.35],
        e_assoc=[2253.9, 0.0],
        vol_a=[0.024675, 0.0],
        kij=0.021,
        source_backed=source_backed,
    )


def _gross_2002_figure6_1butanol_butane_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["1-Butanol", "Butane"],
        source="Gross/Sadowski 2002 Figure 6",
        metadata_extra={
            "reference_system": "1-butanol-n-butane",
            "temperature_series_C": [60.0, 100.0, 160.0, 200.0],
        },
        mw=[74.123e-3, 58.123e-3],
        m=[2.7515, 2.3316],
        s=[3.6139, 3.7086],
        e=[259.59, 222.88],
        e_assoc=[2544.6, 0.0],
        vol_a=[0.006692, 0.0],
        kij=0.015,
        source_backed=source_backed,
    )


def _gross_2002_figure7_ethanol_butane_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["Ethanol", "Butane"],
        source="Gross/Sadowski 2002 Figure 7",
        metadata_extra={
            "reference_system": "ethanol-n-butane",
            "temperature_series_C": [60.0, 100.0, 160.0, 200.0],
        },
        mw=[46.069e-3, 58.123e-3],
        m=[2.3827, 2.3316],
        s=[3.1771, 3.7086],
        e=[198.24, 222.88],
        e_assoc=[2653.4, 0.0],
        vol_a=[0.032384, 0.0],
        kij=0.028,
        source_backed=source_backed,
    )


def _gross_2002_figure9_methanol_1octanol_parameter_set(*, source_backed: bool = True) -> epcsaft.ParameterSet:
    return _gross_2002_associating_vle_parameter_set(
        species=["Methanol", "1-Octanol"],
        source="Gross/Sadowski 2002 Figure 9",
        metadata_extra={"reference_system": "methanol-1-octanol"},
        mw=[32.042e-3, 130.23e-3],
        m=[1.5255, 4.3555],
        s=[3.2300, 3.7145],
        e=[188.90, 262.74],
        e_assoc=[2899.5, 2754.8],
        vol_a=[0.035176, 0.002197],
        kij=0.020,
        assoc_scheme=["2B", "2B"],
        source_backed=source_backed,
    )


def _gross_2002_associating_vle_parameter_set(
    *,
    species: list[str],
    source: str,
    metadata_extra: dict[str, object],
    mw: list[float],
    m: list[float],
    s: list[float],
    e: list[float],
    e_assoc: list[float],
    vol_a: list[float],
    kij: float,
    source_backed: bool,
    assoc_scheme: list[str | None] | None = None,
) -> epcsaft.ParameterSet:
    return _parameter_set_from_records(
        species=species,
        mw=mw,
        m=m,
        sigma=s,
        epsilon_k=e,
        charge=[0.0, 0.0],
        epsilon_k_ab=e_assoc,
        kappa_ab=vol_a,
        association_scheme=assoc_scheme or ["2B", None],
        relative_permittivity=[1.0, 1.0],
        born_diameter=[0.0, 0.0],
        solvation_factor=[1.0, 1.0],
        k_ij=kij,
        metadata={
            "source": source,
            "paper": "Gross and Sadowski 2002",
            "table": "Gross 2002 figure caption plus Gross 2001 pure-component table",
            "figure": source.rsplit(" ", 1)[-1],
            "source_path": "analyses/paper_validation/2002_gross",
            "source_backed": source_backed,
            **metadata_extra,
        },
    )


def test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("bubble_pressure", T=HYDROCARBON_T, x=HYDROCARBON_LIQUID_X).solve(
        solver_options=_solver_options()
    )

    _assert_hydrocarbon_pair(result, problem_kind="neutral_bubble_p")


def test_equilibrium_dew_pressure_recovers_shared_hydrocarbon_point() -> None:
    _skip_without_ipopt()

    result = _configured_equilibrium("dew_pressure", T=HYDROCARBON_T, y=HYDROCARBON_VAPOR_Y).solve(
        solver_options=_solver_options()
    )

    _assert_hydrocarbon_pair(result, problem_kind="neutral_dew_p")
