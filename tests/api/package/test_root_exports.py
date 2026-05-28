from __future__ import annotations

import importlib.util

import epcsaft


def _find_spec(module_name: str):
    try:
        return importlib.util.find_spec(module_name)
    except ModuleNotFoundError:
        return None


def test_root_public_api_is_reset_to_clean_frontend_names() -> None:
    required = {
        "Mixture",
        "State",
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
    assert "Equilibrium" not in epcsaft.__all__
    assert not hasattr(epcsaft, "Equilibrium")
    assert legacy.isdisjoint(epcsaft.__all__)
    for name in legacy:
        assert not hasattr(epcsaft, name)


def test_removed_root_compatibility_modules_are_not_importable() -> None:
    removed_modules = {
        "epcsaft.capability_evidence",
        "epcsaft.diagnostics",
        "epcsaft.electrolyte",
        "epcsaft.equilibrium",
        "epcsaft.equilibrium.core",
        "epcsaft.equilibrium.native_adapter",
        "epcsaft.equilibrium.options",
        "epcsaft.equilibrium.problems",
        "epcsaft.equilibrium.results",
        "epcsaft.equilibrium.workflows",
        "epcsaft.eos",
        "epcsaft.epcsaft",
        "epcsaft.frontend.equilibrium",
        "epcsaft.regression.electrolyte",
        "epcsaft.regression.results",
        "epcsaft.regression.targets",
        "epcsaft.reactive",
        "epcsaft.reactive_electrolyte",
        "epcsaft.reactive_regression",
        "epcsaft.reactive_speciation",
        "epcsaft.reactive_staged",
        "epcsaft.runtime.build_info",
        "epcsaft.runtime.capabilities",
        "epcsaft.runtime.evidence",
    }
    for module_name in removed_modules:
        assert _find_spec(module_name) is None
