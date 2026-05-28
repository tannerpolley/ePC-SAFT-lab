from __future__ import annotations

import epcsaft
from epcsaft_equilibrium import Equilibrium


def test_equilibrium_import_is_owned_by_extension_package() -> None:
    assert not hasattr(epcsaft, "Equilibrium")
    assert Equilibrium.__module__.startswith("epcsaft_equilibrium")
