from __future__ import annotations

from pathlib import Path

import epcsaft

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT = REPO_ROOT / "docs" / "contracts" / "provider_api_v1.md"


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def test_provider_contract_names_stable_core_surfaces() -> None:
    text = _contract_text()

    assert "Provider contract id: `provider_api_v1`." in text
    for surface in (
        "`ParameterSet`",
        "`ModelOptions`",
        "`Mixture`",
        "`State`",
        "`create_input_template(...)`",
        "`runtime_build_info()`",
        "provider-scoped `capabilities()`",
    ):
        assert surface in text


def test_current_root_exports_are_marked_as_transition_surfaces() -> None:
    text = _contract_text()
    normalized = " ".join(text.split())

    for name in ("ParameterSet", "ModelOptions", "Mixture", "State", "create_input_template"):
        assert name in epcsaft.__all__

    assert "Equilibrium" not in epcsaft.__all__
    assert "Regression" in epcsaft.__all__
    assert "Equilibrium` is owned by `epcsaft-equilibrium`" in text
    assert "remaining transition export" in normalized


def test_provider_contract_freezes_derivative_result_shape() -> None:
    text = _contract_text()

    for field in (
        "`supported`",
        "`backend`",
        "`derivative_backend`",
        "`message`",
        "`value`",
        "`jacobian`",
        "`outputs`",
        "`variables`",
        "`shape`",
    ):
        assert field in text

    capabilities = epcsaft.capabilities()
    result_shape = capabilities["derivatives"]["property_derivative_result_apis"]["result_shape"]
    for field in ("supported", "backend", "derivative_backend", "value", "jacobian", "outputs", "variables", "shape"):
        assert field in result_shape


def test_cppad_stays_core_owned_while_equilibrium_capabilities_are_extension_owned() -> None:
    text = _contract_text()

    assert "CppAD and exact derivative provider support remain core-owned" in text
    assert "Equilibrium capability reporting is owned by `epcsaft-equilibrium`." in text

    build_info = epcsaft.runtime_build_info()
    native_dependencies = build_info["native_dependencies"]
    assert "cppad" in native_dependencies

    capabilities = epcsaft.capabilities()
    assert capabilities["package_ownership"] == {
        "provider": "epcsaft",
        "regression": "epcsaft-regression",
    }
    assert capabilities["package_views"]["provider"]["contract_id"] == "provider_api_v1"
    assert set(capabilities["package_views"]) == {"provider", "regression"}
    assert "equilibrium" not in capabilities


def test_extensions_must_not_use_private_core_as_provider_contract() -> None:
    text = _contract_text()

    assert "must not import" in text
    assert "`epcsaft._core`" in text
    assert "private modules" in text
