from __future__ import annotations

import epcsaft
import numpy as np
import pytest
from support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_COMPONENTS,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
)
from support.model_configurations import (
    neutral_model_options,
    neutral_scientific_parameter_set,
    scientific_hydrocarbon_parameter_set,
)


def _hydrocarbon_mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture(
        scientific_hydrocarbon_parameter_set(),
        model_options=neutral_model_options(),
    )


def test_mixture_owns_only_components_parameters_and_model_options() -> None:
    mixture = epcsaft.Mixture(
        scientific_hydrocarbon_parameter_set(),
        components=HYDROCARBON_COMPONENTS,
        model_options=neutral_model_options(),
    )

    assert mixture.components == HYDROCARBON_COMPONENTS
    assert not hasattr(mixture, "state")
    assert not hasattr(mixture, "equilibrium")
    assert not hasattr(mixture, "regression")


def test_state_is_initialized_from_mixture_and_conditions() -> None:
    mixture = _hydrocarbon_mixture()

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
        _hydrocarbon_mixture(),
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
        _hydrocarbon_mixture(),
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


def test_state_evaluates_provider_input_once_and_native_consumes_exact_snapshot(monkeypatch) -> None:
    parameters = neutral_scientific_parameter_set()
    mixture = epcsaft.Mixture(parameters, model_options=neutral_model_options())
    submitted = np.asarray([0.4, 0.6], dtype=np.float64)
    evaluations = 0
    original = epcsaft.ResolvedModelInput.evaluate

    def counted_evaluate(self, *, temperature, composition):
        nonlocal evaluations
        evaluations += 1
        return original(self, temperature=temperature, composition=composition)

    monkeypatch.setattr(epcsaft.ResolvedModelInput, "evaluate", counted_evaluate)

    state = epcsaft.State(mixture, T=300.0, rho=100.0, x=submitted, phase="liq")

    assert evaluations == 1
    assert np.asarray(
        state.configuration_receipt["state"]["canonical_composition"], dtype=np.float64
    ).tobytes() == submitted.tobytes()
    assert (
        state._runtime.configuration_fingerprint()
        == state.evaluated_model_input.snapshot_fingerprint_sha256
    )
