from __future__ import annotations

import numpy as np
import pytest

from epcsaft import InputError, ePCSAFTMixture
from tests.helpers.numeric import assert_allclose
from tests.helpers.runtime_cases import _ionic_params


def _compact_ssmds_born_state(phase: str = "liq"):
    species = ["water", "Na+", "Cl-"]
    params = _ionic_params()
    params["elec_model"] = {
        "rel_perm": {"rule": "empirical", "differential_mode": "auto"},
        "born_model": {
            "d_Born_mode": "fitted_param",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {"differential_mode": "auto", "comp_dep_delta_d": True},
        },
    }
    mixture = ePCSAFTMixture.from_params(params, species=species)
    pressure = 1.0e5
    temperature = 298.15
    composition = np.array([0.9998, 1.0e-4, 1.0e-4])
    state = mixture.state(T=temperature, x=composition, P=pressure, phase=phase)
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


def test_vapor_ssmds_born_derivatives_raise_out_of_scope() -> None:
    _, state = _compact_ssmds_born_state("vap")

    with pytest.raises(InputError, match="liquid-electrolyte only"):
        state.born_ssmds_liquid_derivatives()
