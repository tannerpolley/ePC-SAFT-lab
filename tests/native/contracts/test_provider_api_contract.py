from __future__ import annotations

from pathlib import Path

import epcsaft
from epcsaft.runtime import RouteDiagnosticsView

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

    for name in ("ParameterSet", "ModelOptions", "Mixture", "State", "create_input_template"):
        assert name in epcsaft.__all__

    assert "Equilibrium" not in epcsaft.__all__
    assert "Regression" not in epcsaft.__all__
    assert "Equilibrium` is owned by `epcsaft-equilibrium`" in text
    assert "Regression` is owned by `epcsaft-regression`" in text


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
    assert capabilities["package"] == "epcsaft"
    assert capabilities["owner"] == "core_provider"
    assert capabilities["contract_id"] == "provider_api_v1"
    assert capabilities["native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert capabilities["reports_only_provider_capabilities_after_split"] is True
    assert "package_ownership" not in capabilities
    assert "package_views" not in capabilities
    assert "equilibrium" not in capabilities
    assert "regression" not in capabilities
    assert "optimizers" not in capabilities


def test_extensions_must_not_use_private_core_as_provider_contract() -> None:
    text = _contract_text()

    assert "must not import" in text
    assert "`epcsaft._core`" in text
    assert "private modules" in text


def test_provider_contract_owns_public_route_diagnostics_view() -> None:
    text = _contract_text()

    assert "`RouteDiagnosticsView`" in text
    exc = epcsaft.SolutionError(
        "route failed",
        diagnostics={
            "route_status": "solver_rejected",
            "constraint_families": ["material_balance"],
        },
    )

    view = exc.route_diagnostics

    assert isinstance(view, RouteDiagnosticsView)
    assert view.route_status == "solver_rejected"
    assert view.constraint_families == ("material_balance",)
