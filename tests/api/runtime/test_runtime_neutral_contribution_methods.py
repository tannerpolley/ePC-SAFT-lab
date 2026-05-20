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


def test_state_contribution_term_payloads_match_totals():
    state, _species = _ionic_state()

    ares = state.ares(return_contribution_terms=True)
    assert set(ares) == {"total", "terms"}
    assert set(ares["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert ares["total"] == pytest.approx(state.residual_helmholtz())
    assert sum(ares["terms"].values()) == pytest.approx(ares["total"])

    z_terms = state.z(return_contribution_terms=True)
    assert set(z_terms) == {"total", "terms"}
    assert set(z_terms["terms"]) == {"hc", "disp", "assoc", "ion", "born", "ideal"}
    assert z_terms["total"] == pytest.approx(state.compressibility_factor())
    assert sum(z_terms["terms"].values()) == pytest.approx(z_terms["total"])

    dadt = state.dadt(return_contribution_terms=True)
    assert set(dadt) == {"total", "terms"}
    assert set(dadt["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert dadt["total"] == pytest.approx(state.temperature_derivative_residual_helmholtz())
    assert sum(dadt["terms"].values()) == pytest.approx(dadt["total"])

    mures = state.mures(return_contribution_terms=True)
    assert set(mures) == {"total", "terms"}
    assert set(mures["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    _assert_array(mures["total"], state.residual_chemical_potential())
    _assert_array(_sum_term_arrays(mures["terms"]), mures["total"])

    dadx = state.dadx()
    assert set(dadx) == {
        "total",
        "terms",
        "ares_terms",
        "sum_x_terms",
        "z_raw_terms",
        "z_terms",
        "z_total",
        "derivative_backend",
        "derivative_available",
    }
    assert set(dadx["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert set(dadx["ares_terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert set(dadx["sum_x_terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert set(dadx["z_raw_terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert set(dadx["z_terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    _assert_array(dadx["total"], _sum_term_arrays(dadx["terms"]))
    assert dadx["z_total"] == pytest.approx(state.compressibility_factor())
    assert dadx["ares_terms"]["hc"] == pytest.approx(state.ares(return_contribution_terms=True)["terms"]["hc"])

    fugcoef = state.fugcoef(return_contribution_terms=True)
    fugcoef_coeff = state.fugcoef(natural_log=False, return_contribution_terms=True)
    assert set(fugcoef) == {"total", "terms", "term_basis", "terms_total_natural_log"}
    assert set(fugcoef["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    _assert_array(fugcoef["total"], state.fugacity_coefficient())
    _assert_array(fugcoef_coeff["total"], state.fugacity_coefficient(natural_log=False))
    _assert_array(_sum_term_arrays(fugcoef["terms"]), fugcoef["terms_total_natural_log"])
    _assert_array(_sum_term_arrays(fugcoef_coeff["terms"]), fugcoef_coeff["terms_total_natural_log"])
    assert fugcoef["term_basis"] == "natural_log"

def test_state_contribution_map_aliases_use_public_family_names():
    state, _species = _ionic_state()

    families = {"hard_chain", "dispersion", "association", "ionic", "born"}
    helmholtz = state.helmholtz_contributions()
    residual_helmholtz = state.residual_helmholtz_contributions()
    pressure = state.pressure_contributions()
    chemical_potential = state.chemical_potential_contributions()
    ln_phi = state.ln_fugacity_coefficient_contributions()

    assert set(helmholtz["terms"]) == families
    assert set(residual_helmholtz["terms"]) == families
    assert families | {"ideal"} == set(pressure["terms"])
    assert set(chemical_potential["terms"]) == families
    assert set(ln_phi["terms"]) == families
    assert helmholtz["term_basis"] == "dimensionless_residual_helmholtz"
    assert pressure["term_basis"] == "pressure_from_compressibility_factor"
    assert_allclose(ln_phi["total"], state.fugacity_coefficient())

def test_activity_coefficient_contribution_map_is_explicitly_unsupported():
    state, _species = _ionic_state()

    with pytest.raises(epcsaft.InputError, match="Activity coefficients are available"):
        state.activity_coefficient_contributions()

def test_dadrho_hierarchy_identities_hold_for_neutral_and_ionic_states():
    for factory in (_neutral_state, _ionic_state):
        state, species = factory()
        z_payload = state.z(return_contribution_terms=True)
        dadx = state.dadx()
        mures = state.mures()
        diagnostics = state.state_diagnostics(species=species)
        lnfug = np.asarray(diagnostics["fugacity_coefficient_terms"]["lnfugcoef_total"], dtype=float)

        z_residual = sum(float(dadx["z_terms"][key]) for key in ("hc", "disp", "assoc", "ion", "born"))
        assert z_residual == pytest.approx(state.z() - 1.0)
        assert z_payload["terms"]["ideal"] + z_residual == pytest.approx(z_payload["total"])

        reconstructed_mu = sum(
            dadx["ares_terms"][key] + dadx["z_raw_terms"][key] + dadx["terms"][key] - dadx["sum_x_terms"][key]
            for key in ("hc", "disp", "assoc", "ion", "born")
        )
        assert_allclose(reconstructed_mu, mures)
        assert_allclose(lnfug, mures - np.log(state.z()))

def test_neutral_composition_and_fugacity_terms_return_expected_values():
    state, species = _neutral_state()

    dadx = state.composition_derivative_residual_helmholtz()
    terms = state.state_diagnostics(species=species)["fugacity_coefficient_terms"]
    assert set(dadx) == {
        "total",
        "terms",
        "ares_terms",
        "sum_x_terms",
        "z_raw_terms",
        "z_terms",
        "z_total",
        "derivative_backend",
        "derivative_available",
    }
    for key in ("hc", "disp", "assoc", "ion", "born"):
        assert_allclose(dadx["terms"][key], terms[f"dadx_{key}"])
        assert_allclose(dadx["ares_terms"][key], terms[f"a_{key}"])
        assert_allclose(dadx["sum_x_terms"][key], terms[f"sum_x_dadx_{key}"])
        assert_allclose(dadx["z_raw_terms"][key], terms[f"z_raw_{key}"])
        assert_allclose(dadx["z_terms"][key], terms[f"z_{key}"])
    _assert_array(dadx["terms"]["hc"], [6.883394758977889, 9.511092421642308, 12.258394188218157])
    _assert_array(dadx["terms"]["disp"], [-7.506335725134188, -12.640545058126808, -17.221530131978034])
    _assert_array(dadx["terms"]["assoc"], [0.0, 0.0, 0.0])
    _assert_array(dadx["terms"]["ion"], [0.0, 0.0, 0.0])
    _assert_array(dadx["terms"]["born"], [0.0, 0.0, 0.0])
    assert dadx["z_total"] == pytest.approx(0.04594621208078564)
    _assert_array(terms["mu_total"], [-1.1478687523834008, -3.6543804288405415, -5.488063725572939])
    _assert_array(terms["lnfugcoef_total"], [1.9324151168689134, -0.5740965595882255, -2.407779856320623])
    assert terms["z_total"] == pytest.approx(0.04594621208078564)
    reconstructed_mu = sum(
        dadx["ares_terms"][key] + dadx["z_raw_terms"][key] + dadx["terms"][key] - dadx["sum_x_terms"][key]
        for key in ("hc", "disp", "assoc", "ion", "born")
    )
    assert_allclose(reconstructed_mu, state.residual_chemical_potential())

def test_state_diagnostics_matches_public_methods():
    neutral_state, neutral_species = _neutral_state()
    neutral_diag = neutral_state.state_diagnostics(species=neutral_species)
    assert neutral_diag["activity_coefficient"] == {}
    assert neutral_diag["mean_ionic_activity_coefficient_mole"] == {}
    assert neutral_diag["mean_ionic_activity_coefficient_molality"] == {}
    assert neutral_diag["solvation_free_energy"] == {}
    assert neutral_diag["relative_permittivity"] is None
    assert neutral_diag["osmotic_coefficient"] is None
    assert neutral_diag["mass_density"] is None
    assert neutral_diag["pressure"] == pytest.approx(neutral_state.pressure())
    assert neutral_diag["density"] == pytest.approx(neutral_state.density())
    assert neutral_diag["density_molar"] == pytest.approx(neutral_state.molar_density())
    assert neutral_diag["compressibility_factor"] == pytest.approx(neutral_state.compressibility_factor())
    _assert_array(neutral_diag["residual_chemical_potential"], neutral_state.residual_chemical_potential())
    _assert_array(neutral_diag["fugacity_coefficient"], neutral_state.fugacity_coefficient(natural_log=False))

    ionic_state, ionic_species = _ionic_state()
    ionic_diag = ionic_state.state_diagnostics(species=ionic_species)
    assert ionic_diag["activity_coefficient"] == ionic_state.activity_coefficient(species=ionic_species)
    assert ionic_diag["density"] == pytest.approx(ionic_state.molar_density())
    assert ionic_diag["density_molar"] == pytest.approx(ionic_state.molar_density())
    assert ionic_diag["mass_density"] == pytest.approx(ionic_state.mass_density())
    assert ionic_diag["mean_ionic_activity_coefficient_mole"] == ionic_state.activity_coefficient(
        species=ionic_species,
        mean_ionic_form=True,
        basis="mole",
    )
    assert ionic_diag["mean_ionic_activity_coefficient_molality"] == ionic_state.activity_coefficient(
        species=ionic_species,
        mean_ionic_form=True,
        basis="molality",
    )
    assert ionic_diag["solvation_free_energy"] == ionic_state.solvation_free_energy(species=ionic_species)
    _assert_array(ionic_diag["relative_permittivity"][1], ionic_state.relative_permittivity()[1])
    _assert_array(ionic_diag["osmotic_coefficient"], ionic_state.osmotic_coefficient())
    _assert_array(ionic_diag["residual_chemical_potential"], ionic_state.residual_chemical_potential())
    _assert_array(ionic_diag["fugacity_coefficient"], ionic_state.fugacity_coefficient(natural_log=False))
