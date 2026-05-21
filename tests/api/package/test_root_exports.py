from __future__ import annotations

import epcsaft
import epcsaft.eos as eos


def test_root_public_api_is_reset_to_clean_frontend_names() -> None:
    required = {
        "Mixture",
        "State",
        "Equilibrium",
        "Regression",
        "ParameterSet",
        "ModelOptions",
        "create_input_template",
    }
    legacy = {
        "ePCSAFTMixture",
        "ePCSAFTState",
        "bubble_p",
        "dew_p",
        "fit_pure_neutral",
        "fit_pure_parameters",
        "BubblePoint",
        "TPFlash",
    }

    assert required <= set(epcsaft.__all__)
    assert legacy.isdisjoint(epcsaft.__all__)
    for name in legacy:
        assert not hasattr(epcsaft, name)
        assert not hasattr(eos, name)
    assert eos.Mixture is epcsaft.Mixture
    assert eos.State is epcsaft.State
