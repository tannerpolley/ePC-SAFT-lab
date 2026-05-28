from __future__ import annotations

import epcsaft
from epcsaft.frontend import Mixture, Regression, State, create_input_template


def test_frontend_imports_are_the_public_object_names() -> None:
    assert Mixture is epcsaft.Mixture
    assert State is epcsaft.State
    assert not hasattr(epcsaft, "Equilibrium")
    assert Regression is epcsaft.Regression
    assert create_input_template is epcsaft.create_input_template
