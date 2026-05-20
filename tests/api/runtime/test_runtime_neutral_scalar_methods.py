"""Object-oriented integration tests for the pybind11 native ePC-SAFT runtime."""

import numpy as np
import pytest

import epcsaft
import epcsaft.epcsaft as epcsaft_module
from epcsaft import ePCSAFTMixture
from epcsaft.eos import StateDiagnosticsView
from tests.helpers.numeric import assert_allclose
from tests.helpers.runtime_cases import (
    _assert_array,
    _ionic_state,
    _neutral_state,
    _sum_term_arrays,
)


def test_neutral_scalar_methods_return_expected_values():
    state, _species = _neutral_state()

    assert state.density() == pytest.approx(14330.417110)
    assert state.density(units="molar") == pytest.approx(14330.417110)
    assert state.density(units="mol/m^3") == pytest.approx(14330.417110)
    assert state.molar_density() == pytest.approx(14330.417110)
    with pytest.raises(epcsaft.InputError, match="density units must be"):
        state.density(units="weird")
    with pytest.raises(epcsaft.InputError, match="Mass density requires component molecular weights"):
        state.mass_density()
    with pytest.raises(epcsaft.InputError, match="Mass density requires component molecular weights"):
        state.density(units="mass")
    assert state.pressure() == pytest.approx(1276374.1152948933)
    assert state.compressibility_factor() == pytest.approx(0.04594621208078564)
    assert state.residual_helmholtz() == pytest.approx(-3.54988545131505)
    assert state.temperature_derivative_residual_helmholtz() == pytest.approx(0.03077401856781036)
    assert state.residual_enthalpy() == pytest.approx(-15758.229958475444)
    assert state.residual_entropy() == pytest.approx(-55.751451436621096)
    assert state.residual_gibbs() == pytest.approx(-2759.779056027235)
    _assert_array(state.residual_chemical_potential(), [-1.1478687523834008, -3.6543804288405415, -5.488063725572939])

    fugacity_coefficient = state.fugacity_coefficient()
    fugacity_coefficient_coeff = state.fugacity_coefficient(natural_log=False)
    _assert_array(fugacity_coefficient, [1.9324151168689134, -0.5740965595882255, -2.407779856320623])
    _assert_array(fugacity_coefficient_coeff, [6.906169322700795, 0.5632134688356544, 0.09001491894620331])
    assert_allclose(np.exp(fugacity_coefficient), fugacity_coefficient_coeff)

def test_state_method_aliases_match_canonical_methods():
    state, species = _ionic_state()
    aliases = state.method_aliases()
    assert aliases == {
        "pressure": "p",
        "density": "rho",
        "molar_density": "rho_molar",
        "mass_density": "rho_mass",
        "compressibility_factor": "z",
        "residual_helmholtz": "ares",
        "temperature_derivative_residual_helmholtz": "dadt",
        "composition_derivative_residual_helmholtz": "dadx",
        "residual_enthalpy": "hres",
        "residual_entropy": "sres",
        "residual_gibbs": "gres",
        "residual_chemical_potential": "mures",
        "activity_coefficient": "gamma",
        "fugacity_coefficient": "fugcoef",
        "relative_permittivity": "epsr",
        "osmotic_coefficient": "osmotic_coef",
        "state_diagnostics": "diag",
        "solvation_free_energy": "gsolv",
    }

    assert state.p() == pytest.approx(state.pressure())
    assert state.rho() == pytest.approx(state.density())
    assert state.rho_molar() == pytest.approx(state.molar_density())
    assert state.rho_mass() == pytest.approx(state.mass_density())
    assert state.z() == pytest.approx(state.compressibility_factor())
    assert state.ares() == pytest.approx(state.residual_helmholtz())
    assert state.dadt() == pytest.approx(state.temperature_derivative_residual_helmholtz())
    assert state.hres() == pytest.approx(state.residual_enthalpy())
    assert state.sres() == pytest.approx(state.residual_entropy())
    assert state.gres() == pytest.approx(state.residual_gibbs())
    assert state.dadx()["z_total"] == pytest.approx(state.composition_derivative_residual_helmholtz()["z_total"])
    _assert_array(state.mures(), state.residual_chemical_potential())
    _assert_array(state.fugcoef(), state.fugacity_coefficient())
    _assert_array(state.fugcoef(natural_log=False), state.fugacity_coefficient(natural_log=False))
    assert state.epsr()[0] == pytest.approx(state.relative_permittivity()[0])
    _assert_array(state.osmotic_coef(), state.osmotic_coefficient())
    assert state.gamma(species=species) == state.activity_coefficient(species=species)
    assert state.gamma(species=species, mean_ionic_form=True, basis="molality") == state.activity_coefficient(
        species=species, mean_ionic_form=True, basis="molality"
    )
    assert state.diag(species=species)["pressure"] == pytest.approx(
        state.state_diagnostics(species=species)["pressure"]
    )
    assert state.gsolv(species=species) == state.solvation_free_energy(species=species)
    with pytest.raises(AttributeError):
        _ = state.fugacity_coefficient_terms
    with pytest.raises(AttributeError):
        _ = state.lnfug_terms

def test_state_diagnostics_view_wraps_stable_payload():
    state, species = _ionic_state()

    payload = state.state_diagnostics(species=species)
    view = state.state_diagnostics_view(species=species)

    assert isinstance(view, StateDiagnosticsView)
    assert view.as_dict()["pressure"] == pytest.approx(payload["pressure"])
    assert view.pressure == pytest.approx(payload["pressure"])
    assert view.density == pytest.approx(payload["density_molar"])
    assert view.compressibility_factor == pytest.approx(payload["compressibility_factor"])
    assert view.has_ionic_outputs is True
    assert set(view.fugacity_coefficient_terms) == set(payload["fugacity_coefficient_terms"])
