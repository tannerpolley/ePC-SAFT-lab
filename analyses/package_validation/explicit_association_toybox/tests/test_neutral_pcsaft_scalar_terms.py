from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.pcsaft_inputs import (
    ToyPCSAFTState,
    state_from_config,
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
