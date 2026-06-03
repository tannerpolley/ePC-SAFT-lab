from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.pcsaft_inputs import (
    ToyPCSAFTState,
    state_from_config,
)
from analyses.package_validation.explicit_association_toybox.scripts.hard_chain import (
    ares_hc,
    ares_hs,
    hard_chain_state,
)
from analyses.package_validation.explicit_association_toybox.scripts.dispersion import (
    ares_disp,
    dispersion_polynomials,
    mixed_dispersion_moments,
)


def test_state_from_config_validates_component_shapes() -> None:
    state = state_from_config(
        {
            "temperature": 303.15,
            "density": 0.01,
            "segments": [2.0, 1.0],
            "sigma": [3.0, 3.5],
            "epsilon_over_k": [200.0, 150.0],
            "k_ij": [[0.0, 0.02], [0.02, 0.0]],
        },
        component_count=2,
        composition=np.array([0.25, 0.75]),
    )

    assert isinstance(state, ToyPCSAFTState)
    assert state.component_count == 2
    assert np.allclose(state.composition, [0.25, 0.75])
    assert state.temperature == pytest.approx(303.15)
    assert state.density == pytest.approx(0.01)


def test_state_from_config_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="segments length must match component_count"):
        state_from_config(
            {
                "temperature": 303.15,
                "density": 0.01,
                "segments": [2.0],
                "sigma": [3.0, 3.5],
                "epsilon_over_k": [200.0, 150.0],
                "k_ij": [[0.0, 0.02], [0.02, 0.0]],
            },
            component_count=2,
            composition=np.array([0.25, 0.75]),
        )


def test_state_from_config_rejects_non_normalized_composition() -> None:
    with pytest.raises(ValueError, match="composition must sum to one"):
        state_from_config(
            {
                "temperature": 303.15,
                "density": 0.01,
                "segments": [2.0, 1.0],
                "sigma": [3.0, 3.5],
                "epsilon_over_k": [200.0, 150.0],
                "k_ij": [[0.0, 0.02], [0.02, 0.0]],
            },
            component_count=2,
            composition=np.array([0.25, 0.70]),
        )


def test_hard_chain_reduces_to_hard_sphere_for_monomer() -> None:
    state = ToyPCSAFTState(
        temperature=303.15,
        density=0.01,
        composition=np.array([1.0]),
        segments=np.array([1.0]),
        sigma=np.array([3.0]),
        epsilon_over_k=np.array([200.0]),
        k_ij=np.array([[0.0]]),
    )
    hc = hard_chain_state(state)

    assert hc.eta > 0.0
    assert ares_hc(state, hc) == pytest.approx(ares_hs(hc))


def test_hard_chain_returns_finite_scalar_for_binary_state() -> None:
    state = state_from_config(
        {
            "temperature": 303.15,
            "density": 0.01,
            "segments": [2.0, 1.0],
            "sigma": [3.0, 3.5],
            "epsilon_over_k": [200.0, 150.0],
            "k_ij": [[0.0, 0.0], [0.0, 0.0]],
        },
        component_count=2,
        composition=np.array([0.5, 0.5]),
    )
    value = ares_hc(state, hard_chain_state(state))

    assert np.isfinite(value)
    assert value > 0.0


def test_dispersion_polynomials_match_pure_monomer_leading_coefficients() -> None:
    polynomials = dispersion_polynomials(m_bar=1.0, eta=0.05)

    assert polynomials.a[0] == pytest.approx(0.9105631445)
    assert polynomials.b[0] == pytest.approx(0.7240946941)
    assert np.isfinite(polynomials.i1)
    assert np.isfinite(polynomials.i2)
    assert np.isfinite(polynomials.c1)


def test_dispersion_returns_negative_finite_scalar() -> None:
    state = state_from_config(
        {
            "temperature": 303.15,
            "density": 0.01,
            "segments": [2.0, 1.0],
            "sigma": [3.0, 3.5],
            "epsilon_over_k": [200.0, 150.0],
            "k_ij": [[0.0, 0.0], [0.0, 0.0]],
        },
        component_count=2,
        composition=np.array([0.5, 0.5]),
    )
    hc = hard_chain_state(state)
    moments = mixed_dispersion_moments(state)
    value = ares_disp(state, hc, moments)

    assert np.isfinite(value)
    assert value < 0.0
