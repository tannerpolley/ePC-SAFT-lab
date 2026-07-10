from __future__ import annotations

import epcsaft
import epcsaft_equilibrium
import numpy as np
import pytest
from epcsaft.model.parameters import BinaryRecord, PureRecord


def _parameter_set(
    components: tuple[str, ...],
    *,
    molar_mass: tuple[float, ...],
    m: tuple[float, ...],
    sigma: tuple[float, ...],
    epsilon_k: tuple[float, ...],
    epsilon_k_ab: tuple[float, ...] | None = None,
    kappa_ab: tuple[float, ...] | None = None,
    association_scheme: tuple[str | None, ...] | None = None,
    k_ij: float | None = None,
) -> epcsaft.ParameterSet:
    epsilon_k_ab = epsilon_k_ab or tuple(0.0 for _ in components)
    kappa_ab = kappa_ab or tuple(0.0 for _ in components)
    association_scheme = association_scheme or tuple(None for _ in components)
    pure = tuple(
        PureRecord(
            component=component,
            molar_mass=molar_mass_i,
            m=m_i,
            sigma=sigma_i,
            epsilon_k=epsilon_k_i,
            charge=0.0,
            epsilon_k_ab=epsilon_k_ab_i,
            kappa_ab=kappa_ab_i,
            association_scheme=scheme_i,
            relative_permittivity=1.0,
            born_diameter=0.0,
            solvation_factor=1.0,
        )
        for component, molar_mass_i, m_i, sigma_i, epsilon_k_i, epsilon_k_ab_i, kappa_ab_i, scheme_i in zip(
            components,
            molar_mass,
            m,
            sigma,
            epsilon_k,
            epsilon_k_ab,
            kappa_ab,
            association_scheme,
            strict=True,
        )
    )
    binary = () if k_ij is None else (BinaryRecord((components[0], components[1]), k_ij=k_ij),)
    return epcsaft.ParameterSet.from_records(
        pure,
        binary,
        metadata={"source": "Gross and Sadowski reference parameters", "source_backed": True},
    )


def _pure_ethane_parameter_set() -> epcsaft.ParameterSet:
    return _parameter_set(
        ("Ethane",),
        molar_mass=(30.070e-3,),
        m=(1.6069,),
        sigma=(3.5206,),
        epsilon_k=(191.42,),
    )


def _binary_parameter_set() -> epcsaft.ParameterSet:
    return _parameter_set(
        ("Methane", "Ethane"),
        molar_mass=(16.043e-3, 30.070e-3),
        m=(1.0, 1.6069),
        sigma=(3.7039, 3.5206),
        epsilon_k=(150.03, 191.42),
        k_ij=3.0e-4,
    )


def _unproven_pure_parameter_set() -> epcsaft.ParameterSet:
    return _parameter_set(
        ("UnprovenPureComponent",),
        molar_mass=(20.180e-3,),
        m=(1.2,),
        sigma=(3.1,),
        epsilon_k=(120.0,),
    )


def _pure_associating_parameter_set() -> epcsaft.ParameterSet:
    return _parameter_set(
        ("Methanol",),
        molar_mass=(32.042e-3,),
        m=(1.5255,),
        sigma=(3.2300,),
        epsilon_k=(188.90,),
        epsilon_k_ab=(2899.5,),
        kappa_ab=(0.035176,),
        association_scheme=("2B",),
    )


def _skip_without_ipopt() -> None:
    if not bool(epcsaft_equilibrium.capabilities()["optimizer"]["ipopt"]["adapter_available"]):
        pytest.skip("single-component VLE route requires the native Ipopt adapter")


def _single_component_result(
    diagnostics: dict[str, object],
) -> epcsaft_equilibrium.EquilibriumResult:
    phases = {
        "liquid": epcsaft_equilibrium.EquilibriumPhase(
            "liquid", [1.0], 450.0, 233.15, 2.0e6, 0.5
        ),
        "vapor": epcsaft_equilibrium.EquilibriumPhase(
            "vapor", [1.0], 25.0, 233.15, 2.0e6, 0.5
        ),
    }
    return epcsaft_equilibrium.EquilibriumResult(
        backend="native",
        problem_kind="single_component_vle",
        phases=phases,
        stable=True,
        split_detected=True,
        diagnostics=diagnostics,
        route="single_component_vle",
        selector_route="single_component_vle",
        composition_role="pure",
    )


def test_single_component_vle_route_configures_pure_temperature_problem() -> None:
    mixture = epcsaft.Mixture(_pure_ethane_parameter_set())

    equilibrium = epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=233.15)
    structure = equilibrium.structure()

    assert equilibrium.problem.route == "single_component_vle"
    assert equilibrium.problem.selector_route == "single_component_vle"
    assert equilibrium.problem.knowns == ("T",)
    assert equilibrium.problem.unknowns == ("P_sat", "rho_vapor", "rho_liquid")
    assert equilibrium.problem.composition_role == "pure"
    assert equilibrium.problem.activation_key == "single_component_vle"
    assert equilibrium.problem.expected_phase_keys == ("liquid", "vapor")
    assert equilibrium.problem.fixed_specs["T"] == pytest.approx(233.15)
    assert equilibrium.problem.fixed_specs["z"] == pytest.approx([1.0])
    assert structure.selector_route == "single_component_vle"
    assert structure.activation_key == "single_component_vle"
    assert structure.variable_model == "phase_species_amounts_plus_phase_volume_plus_route_scalar"


def test_single_component_vle_route_returns_saturation_payload() -> None:
    _skip_without_ipopt()
    mixture = epcsaft.Mixture(_pure_ethane_parameter_set())

    result = epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=233.15).solve(
        solver_options={"max_iterations": 200, "tolerance": 1.0e-8}
    )
    payload = result.to_dict()

    assert result.route == "single_component_vle"
    assert result.selector_route == "single_component_vle"
    assert result.problem_kind == "single_component_vle"
    assert result.saturation_pressure == pytest.approx(result.pressure)
    assert result.P_sat == pytest.approx(result.pressure)
    assert result.vapor_density == pytest.approx(result.phases["vapor"].density)
    assert result.liquid_density == pytest.approx(result.phases["liquid"].density)
    assert result.x == pytest.approx([1.0])
    assert result.y == pytest.approx([1.0])
    assert result.diagnostics["problem_name"] == "single_component_vle_eos"
    assert result.diagnostics["route_status"] == "accepted"
    assert result.diagnostics["postsolve_certification"]["accepted"] is True
    assert result.diagnostics["postsolve_certification"]["stability_checked"] is False
    assert result.diagnostics["phase_distance"] == pytest.approx(
        result.diagnostics["postsolve_certification"]["phase_distance"]
    )
    assert result.diagnostics["phase_distance"] > 1.0e-2
    assert payload["P_sat"] == pytest.approx(result.pressure)
    assert payload["vapor_density"] == pytest.approx(result.vapor_density)
    assert payload["liquid_density"] == pytest.approx(result.liquid_density)
    assert result.liquid_density > result.vapor_density
    assert payload["saturation_residuals"]["pressure_consistency_norm"] <= 1.0e-2
    assert payload["saturation_residuals"]["chemical_potential_consistency_norm"] <= 1.0e-6


@pytest.mark.parametrize(
    "missing_field",
    [
        "pressure_consistency_norm",
        "chemical_potential_consistency_norm",
        "ln_fugacity_consistency_norm",
    ],
)
def test_single_component_vle_serialization_requires_each_residual_diagnostic(
    missing_field: str,
) -> None:
    diagnostics: dict[str, object] = {
        "pressure_consistency_norm": 1.0e-8,
        "chemical_potential_consistency_norm": 2.0e-8,
        "ln_fugacity_consistency_norm": 3.0e-8,
    }
    diagnostics.pop(missing_field)

    with pytest.raises(
        epcsaft.SolutionError,
        match=rf"single_component_vle diagnostics missing required field '{missing_field}'",
    ):
        _single_component_result(diagnostics).to_dict()


@pytest.mark.parametrize("invalid_value", [float("nan"), float("inf"), -1.0])
def test_single_component_vle_serialization_rejects_invalid_residual_diagnostic(
    invalid_value: float,
) -> None:
    diagnostics: dict[str, object] = {
        "pressure_consistency_norm": invalid_value,
        "chemical_potential_consistency_norm": 2.0e-8,
        "ln_fugacity_consistency_norm": 3.0e-8,
    }

    with pytest.raises(
        epcsaft.SolutionError,
        match="single_component_vle diagnostic 'pressure_consistency_norm' must be finite and non-negative",
    ):
        _single_component_result(diagnostics).to_dict()


def test_single_component_vle_route_rejects_binary_mixture() -> None:
    mixture = epcsaft.Mixture(_binary_parameter_set())

    with pytest.raises(epcsaft.InputError, match="single_component_vle requires exactly one component"):
        epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=233.15)


def test_single_component_vle_route_rejects_unproven_pure_associating_component() -> None:
    mixture = epcsaft.Mixture(_pure_associating_parameter_set())

    with pytest.raises(
        epcsaft.InputError,
        match="single_component_vle requires a nonassociating pure-component input",
    ):
        epcsaft_equilibrium.Equilibrium(
            mixture,
            route="single_component_vle",
            T=298.15,
        )


def test_single_component_vle_route_rejects_nonassociating_component_outside_nist_scope() -> None:
    mixture = epcsaft.Mixture(_unproven_pure_parameter_set())

    with pytest.raises(
        epcsaft.InputError,
        match="NIST-backed methane, ethane, or propane",
    ):
        epcsaft_equilibrium.Equilibrium(
            mixture,
            route="single_component_vle",
            T=233.15,
        )


def test_single_component_vle_route_rejects_temperature_outside_retained_nist_range() -> None:
    mixture = epcsaft.Mixture(_pure_ethane_parameter_set())

    with pytest.raises(epcsaft.InputError, match="retained NIST temperature range"):
        epcsaft_equilibrium.Equilibrium(
            mixture,
            route="single_component_vle",
            T=300.0,
        )


def test_single_component_vle_route_rejects_public_composition_specs() -> None:
    mixture = epcsaft.Mixture(_pure_ethane_parameter_set())

    with pytest.raises(epcsaft.InputError, match="single_component_vle must not specify x, y, or z"):
        epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=233.15, z=[1.0])


def test_provider_does_not_export_vapor_pressure_api() -> None:
    assert not hasattr(epcsaft, "vapor_pressure")
    assert not hasattr(epcsaft, "saturation_pressure")
