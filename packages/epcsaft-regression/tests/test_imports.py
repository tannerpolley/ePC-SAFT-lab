from __future__ import annotations

import epcsaft
import epcsaft_regression


def test_regression_extension_exports_workflow_and_capabilities() -> None:
    assert hasattr(epcsaft_regression, "Regression")
    assert epcsaft_regression.capabilities()["provider_contract"]["provider_package"] == "epcsaft"
    assert epcsaft.Mixture is not None
