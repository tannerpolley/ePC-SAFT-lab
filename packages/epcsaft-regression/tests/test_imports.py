from __future__ import annotations

import epcsaft
import epcsaft_regression


def test_regression_extension_exports_workflow_and_capabilities() -> None:
    assert hasattr(epcsaft_regression, "Regression")
    assert hasattr(epcsaft_regression, "FitProblem")
    assert hasattr(epcsaft_regression, "FitResult")
    assert hasattr(epcsaft_regression, "RegressionEvaluation")
    assert hasattr(epcsaft_regression, "RegressionReceipt")
    assert epcsaft_regression.capabilities()["provider_contract"]["provider_package"] == "epcsaft"
    assert epcsaft.Mixture is not None


def test_regression_extension_has_no_loose_record_fit_exports() -> None:
    for name in (
        "fit_binary_pair",
        "fit_binary_parameters",
        "fit_liquid_electrolyte_parameters",
        "fit_pure_ion",
        "fit_pure_neutral",
        "fit_pure_parameters",
    ):
        assert name not in epcsaft_regression.__all__
        assert not hasattr(epcsaft_regression, name)
