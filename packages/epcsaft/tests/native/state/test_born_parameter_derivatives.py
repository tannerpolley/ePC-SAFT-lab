from __future__ import annotations

import epcsaft._core as _core
import numpy as np
import pytest
from epcsaft import InputError
from epcsaft.state.native_adapter import create_struct, ePCSAFTMixture
from support.numeric import assert_allclose
from support.runtime_cases import _ionic_params


def _compact_born_state(
    phase: str = "liq",
    rel_perm_mode: str = "auto",
    mu_born_mode: str = "auto",
    rho: float | None = None,
    solvation_shell_model: bool = True,
    dielectric_saturation: bool = True,
):
    species = ["water", "Na+", "Cl-"]
    params = _ionic_params()
    params["elec_model"] = {
        "rel_perm": {"rule": "empirical", "differential_mode": rel_perm_mode},
        "born_model": {
            "d_Born_mode": "fitted_param",
            "solvation_shell_model": solvation_shell_model,
            "dielectric_saturation": dielectric_saturation,
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


def test_liquid_born_parameter_derivatives_are_supported_for_compact_ionic_fixture() -> None:
    species, state = _compact_born_state("liq")

    payload = state.born_parameter_derivatives()

    assert payload["supported"] is True
    assert payload["backend"] == "cppad"
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

    parameter_order = tuple(f"d_born:{name}" for name in species) + tuple(f"f_solv:{name}" for name in species)
    for public_payload in (
        state.ln_fugacity_parameter_derivative_result(),
        state.activity_parameter_derivative_result(species=species),
    ):
        assert public_payload["backend"] == "cppad"
        assert public_payload["parameter_order"] == parameter_order
        assert np.asarray(public_payload["jacobian"], dtype=float).shape == (len(species), 2 * len(species))


def test_activity_coefficient_accepts_explicit_cppad_born_derivative_mode() -> None:
    species, state = _compact_born_state("liq", rel_perm_mode="cppad", mu_born_mode="cppad")

    gamma = state.activity_coefficient(species=species, mean_ionic_form=True, basis="molality")

    assert gamma["Na+Cl-"] > 0.0
    assert np.isfinite(gamma["Na+Cl-"])


def test_auto_born_composition_derivative_uses_cppad_backend() -> None:
    _, state = _compact_born_state("liq", rel_perm_mode="auto", mu_born_mode="auto")

    derivative = state.composition_derivative_residual_helmholtz()

    assert derivative["derivative_backend"]["born"] == "cppad"
    assert np.all(np.isfinite(derivative["terms"]["born"]))


def test_born_rejects_analytical_mu_born_derivative_mode() -> None:
    with pytest.raises(_core.NativeValueError, match="SSM/DS Born requires CppAD"):
        _, state = _compact_born_state(
            "liq",
            rel_perm_mode="cppad",
            mu_born_mode="analytical",
            rho=55000.0,
        )
        state.ares()


def test_vapor_born_parameter_derivatives_raise_out_of_scope() -> None:
    _, state = _compact_born_state("vap")

    with pytest.raises(InputError, match="liquid-electrolyte only"):
        state.born_parameter_derivatives()


def test_disabled_solvation_shell_and_dielectric_saturation_reduce_to_direct_born() -> None:
    species, state = _compact_born_state(
        "liq",
        solvation_shell_model=False,
        dielectric_saturation=False,
    )
    rho = state.density()
    params = _ionic_params()
    params["elec_model"] = {
        "rel_perm": {"rule": "empirical", "differential_mode": "auto"},
        "born_model": {
            "d_Born_mode": "fitted_param",
            "solvation_shell_model": False,
            "dielectric_saturation": False,
            "mu_born_model": {"differential_mode": "auto", "comp_dep_delta_d": True},
        },
    }
    direct_args = create_struct(params)
    direct_args.born_model = 1
    direct_state = _core.NativeState(
        _core.NativeMixture(direct_args),
        298.15,
        [0.9998, 1.0e-4, 1.0e-4],
        0,
        False,
        0.0,
        True,
        rho,
        False,
        0.0,
    )

    actual = state.ares(return_contribution_terms=True)["terms"]["born"]
    expected = direct_state.residual_helmholtz_result().born
    assert actual == pytest.approx(expected)

    payload = state.born_parameter_derivatives()
    assert payload["backend"] == "cppad"
    assert_allclose(payload["a_born_d_f_solv"], np.zeros(len(species)))
    assert_allclose(payload["mu_res_d_f_solv"], np.zeros((len(species), len(species))))
