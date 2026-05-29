from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_COMPONENTS,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    hydrocarbon_parameter_set,
)
from support.runtime_cases import _ionic_params


def test_mixture_owns_only_components_parameters_and_model_options() -> None:
    mixture = epcsaft.Mixture(
        hydrocarbon_parameter_set(),
        components=HYDROCARBON_COMPONENTS,
        model_options=epcsaft.ModelOptions(),
    )

    assert mixture.components == HYDROCARBON_COMPONENTS
    assert not hasattr(mixture, "state")
    assert not hasattr(mixture, "equilibrium")
    assert not hasattr(mixture, "regression")


def test_state_is_initialized_from_mixture_and_conditions() -> None:
    mixture = epcsaft.Mixture(hydrocarbon_parameter_set())

    state = epcsaft.State(
        mixture,
        T=HYDROCARBON_T,
        P=HYDROCARBON_BUBBLE_P,
        x=HYDROCARBON_LIQUID_X,
        phase="liquid",
    )

    assert state.temperature == pytest.approx(HYDROCARBON_T)
    assert state.composition == pytest.approx(np.asarray(HYDROCARBON_LIQUID_X))
    assert state.molar_density() == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=5.0e-5)
    assert state.z() == pytest.approx(state.compressibility_factor())


def test_cppad_state_proves_hydrocarbon_values_and_derivatives() -> None:
    state = epcsaft.State(
        epcsaft.Mixture(hydrocarbon_parameter_set()),
        T=HYDROCARBON_T,
        P=HYDROCARBON_BUBBLE_P,
        x=HYDROCARBON_LIQUID_X,
        phase="liq",
    )

    assert state.molar_density() == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=5.0e-5)
    assert state.compressibility_factor() == pytest.approx(0.0459462, rel=5.0e-5)
    assert state.ln_fugacity_coefficients() == pytest.approx(
        np.asarray([1.9324151168689134, -0.5740965595882255, -2.407779856320623]), rel=5.0e-5
    )

    pressure_density = state.pressure_density_derivative()
    fugacity_composition = state.ln_fugacity_composition_derivative()

    assert pressure_density["derivative_backend"] == "cppad"
    assert pressure_density["jacobian"].shape == (1, 1)
    assert fugacity_composition["derivative_backend"].startswith("cppad")
    assert fugacity_composition["jacobian"].shape == (3, 3)


def test_state_exposes_residual_property_aliases_and_contributions() -> None:
    state = epcsaft.State(
        epcsaft.Mixture(hydrocarbon_parameter_set()),
        T=HYDROCARBON_T,
        P=HYDROCARBON_BUBBLE_P,
        x=HYDROCARBON_LIQUID_X,
        phase="liq",
    )

    assert state.ares() == pytest.approx(state.residual_helmholtz())
    assert state.hres() == pytest.approx(state.residual_enthalpy())
    assert state.sres() == pytest.approx(state.residual_entropy())
    assert state.gres() == pytest.approx(state.residual_gibbs())

    contributions = state.ares_contributions()
    assert set(contributions) == {"hard_chain", "dispersion", "association", "ionic", "born"}
    assert state.ares() == pytest.approx(sum(contributions.values()))
    assert state.ares_contribution("dispersion") == pytest.approx(contributions["dispersion"])


def test_active_association_model_options_emit_implicit_assoc_mode() -> None:
    species = ("water", "Na+", "Cl-")
    assoc_parameters = epcsaft.ParameterSet.from_dict(_ionic_params(), species=species)
    assoc_options = epcsaft.ModelOptions().to_runtime_options(assoc_parameters)

    assert assoc_options["elec_model"]["assoc_model"]["dadx_differential_mode"] == "auto"

    assoc_mixture = epcsaft.Mixture(assoc_parameters, model_options=epcsaft.ModelOptions())

    assert assoc_mixture._runtime_parameters["elec_model"]["hc_model"]["dadx_differential_mode"] == "cppad"
    assert assoc_mixture._runtime_parameters["elec_model"]["disp_model"]["dadx_differential_mode"] == "cppad"
    assert assoc_mixture._runtime_parameters["elec_model"]["assoc_model"]["dadx_differential_mode"] == "auto"


def test_nonassociating_model_options_preserve_explicit_cppad_assoc_mode() -> None:
    species = ("water", "Na+", "Cl-")
    payload = _ionic_params()
    payload["e_assoc"] = np.zeros(3)
    payload["vol_a"] = np.zeros(3)
    payload["assoc_scheme"] = [None, None, None]
    parameters = epcsaft.ParameterSet.from_dict(payload, species=species)
    options = epcsaft.ModelOptions().to_runtime_options(parameters)

    assert options["elec_model"]["assoc_model"]["dadx_differential_mode"] == "cppad"

    mixture = epcsaft.Mixture(parameters, model_options=epcsaft.ModelOptions())

    assert mixture._runtime_parameters["elec_model"]["assoc_model"]["dadx_differential_mode"] == "cppad"
