from __future__ import annotations

import importlib.util

import epcsaft


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


def test_removed_root_compatibility_modules_are_not_importable() -> None:
    removed_modules = {
        "epcsaft.capability_evidence",
        "epcsaft.diagnostics",
        "epcsaft.electrolyte",
        "epcsaft.eos",
        "epcsaft.epcsaft",
        "epcsaft.reactive",
        "epcsaft.reactive_electrolyte",
        "epcsaft.reactive_regression",
        "epcsaft.reactive_speciation",
        "epcsaft.reactive_staged",
    }
    for module_name in removed_modules:
        assert importlib.util.find_spec(module_name) is None
