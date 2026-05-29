from __future__ import annotations

import numpy as np
import pytest

import epcsaft._core as _core
from epcsaft import InputError
from epcsaft.state.native_adapter import ePCSAFTMixture
from support.numeric import assert_allclose
from support.runtime_cases import _ionic_params


def _compact_ssmds_born_state(
    phase: str = "liq",
    rel_perm_mode: str = "auto",
    mu_born_mode: str = "auto",
    rho: float | None = None,
):
    species = ["water", "Na+", "Cl-"]
    params = _ionic_params()
    params["elec_model"] = {
        "rel_perm": {"rule": "empirical", "differential_mode": rel_perm_mode},
        "born_model": {
            "d_Born_mode": "fitted_param",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {"differential_mode": mu_born_mode, "comp_dep_delta_d": True},
        },
    }
    mixture = ePCSAFTMixture.from_params(params, species=species)
    pressure = 1.0e5
    temperature = 298.15
    composition = np.array([0.9998, 1.0e-4, 1.0e-4])
    state = (
        mixture.state(T=temperature, x=composition, rho=rho, phase=phase)
        if rho is not None
        else mixture.state(T=temperature, x=composition, P=pressure, phase=phase)
    )
    return species, state


def _matrix(payload: dict[str, object], key: str) -> np.ndarray:
    return np.asarray(payload[key], dtype=float)


def test_liquid_ssmds_born_derivatives_are_supported_for_compact_ionic_fixture() -> None:
    species, state = _compact_ssmds_born_state("liq")

    payload = state.born_ssmds_liquid_derivatives()

    assert payload["supported"] is True
    assert payload["backend"] in {"analytic", "cppad"}
    assert payload["phase_scope"] == "liquid_electrolyte_only"
    assert payload["parameters"] == ("d_born", "f_solv")
    assert payload["vapor_support"] is False
    assert "finite" not in str(payload["backend"]).lower()

    d_born = np.asarray(payload["a_born_d_d_born"], dtype=float)
    f_solv = np.asarray(payload["a_born_d_f_solv"], dtype=float)
    assert d_born.shape == (len(species),)
    assert f_solv.shape == (len(species),)
    assert np.all(np.isfinite(d_born))
    assert np.all(np.isfinite(f_solv))
    solvent_index = 0
    ion_indices = [idx for idx, name in enumerate(species) if name != species[solvent_index]]
    assert d_born[solvent_index] == pytest.approx(0.0)
    assert np.any(np.abs(d_born[ion_indices]) > 0.0)
    assert np.any(np.abs(f_solv) > 0.0)

    for key in (
        "mu_res_d_d_born",
        "mu_res_d_f_solv",
        "lnfug_d_d_born",
        "lnfug_d_f_solv",
        "lngamma_d_d_born",
        "lngamma_d_f_solv",
    ):
        values = _matrix(payload, key)
        assert values.shape == (len(species), len(species))
        assert np.all(np.isfinite(values))

    assert_allclose(payload["lnfug_d_d_born"], payload["mu_res_d_d_born"])
    assert_allclose(payload["lnfug_d_f_solv"], payload["mu_res_d_f_solv"])


def test_activity_coefficient_accepts_explicit_cppad_ssmds_born_derivative_mode() -> None:
    species, state = _compact_ssmds_born_state("liq", rel_perm_mode="cppad", mu_born_mode="cppad")

    gamma = state.activity_coefficient(species=species, mean_ionic_form=True, basis="molality")

    assert gamma["Na+Cl-"] > 0.0
    assert np.isfinite(gamma["Na+Cl-"])


def test_auto_ssmds_born_composition_derivative_uses_cppad_backend() -> None:
    _, state = _compact_ssmds_born_state("liq", rel_perm_mode="auto", mu_born_mode="auto")

    derivative = state.composition_derivative_residual_helmholtz()

    assert derivative["derivative_backend"]["born"] == "cppad"
    assert np.all(np.isfinite(derivative["terms"]["born"]))


def test_ssmds_born_rejects_analytical_mu_born_derivative_mode() -> None:
    with pytest.raises(_core.NativeValueError, match="SSM/DS Born requires CppAD"):
        _, state = _compact_ssmds_born_state(
            "liq",
            rel_perm_mode="cppad",
            mu_born_mode="analytical",
            rho=55000.0,
        )
        state.ares()


def test_vapor_ssmds_born_derivatives_raise_out_of_scope() -> None:
    _, state = _compact_ssmds_born_state("vap")

    with pytest.raises(InputError, match="liquid-electrolyte only"):
        state.born_ssmds_liquid_derivatives()
