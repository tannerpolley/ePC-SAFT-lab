from __future__ import annotations

from pathlib import Path

import epcsaft._core as _core

REPO_ROOT = Path(__file__).resolve().parents[3]
EQUILIBRIUM_PACKAGE_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium"
EQUILIBRIUM_MODULE_ROOT = EQUILIBRIUM_PACKAGE_ROOT / "src" / "epcsaft_equilibrium"
EQUILIBRIUM_NATIVE_ROOT = EQUILIBRIUM_PACKAGE_ROOT / "native" / "equilibrium"


def test_native_equilibrium_entrypoint_is_exposed() -> None:
    assert hasattr(_core, "_native_equilibrium_selector_contract")
    assert hasattr(_core, "_native_equilibrium_selector_route_result")
    assert not hasattr(_core, "_evaluate_electrolyte_lle_residual_native")


def test_equilibrium_runtime_does_not_import_external_optimizers() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            EQUILIBRIUM_MODULE_ROOT / "equilibrium.py",
            EQUILIBRIUM_MODULE_ROOT / "workflows.py",
        )
    )

    external_optimizer = "sci" + "py.optimize"
    forbidden = (
        external_optimizer,
        "least" + "_squares",
        "differential" + "_evolution",
        "minimize" + "_scalar",
        "_solve_predictive_electrolyte",
        "_electrolyte_gibbs_seed_from_trial",
        "_electrolyte_stability_from_basis",
    )

    for token in forbidden:
        assert token not in source


def test_package_runtime_has_no_external_optimizer_dependency_or_imports() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    docs_requirements = (REPO_ROOT / "docs" / "requirements.txt").read_text(encoding="utf-8")
    package_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / "src" / "epcsaft").rglob("*.py")
        if path.name != "__pycache__"
    )

    dependency_token = "sci" + "py"
    assert dependency_token not in pyproject.lower()
    assert dependency_token not in docs_requirements.lower()
    assert f"from {dependency_token}" not in package_sources
    assert f"import {dependency_token}" not in package_sources


def test_public_equilibrium_does_not_expose_python_backend_tokens() -> None:
    source = (REPO_ROOT / "src" / "epcsaft" / "__init__.py").read_text(encoding="utf-8")
    equilibrium_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            EQUILIBRIUM_MODULE_ROOT / "equilibrium.py",
            EQUILIBRIUM_MODULE_ROOT / "workflows.py",
        )
    )

    assert '"python"' not in source
    assert "Python-first" not in equilibrium_source
    assert "np.linalg." + "lstsq" not in equilibrium_source


def test_native_route_result_serialization_uses_bridge_module() -> None:
    bridge = EQUILIBRIUM_NATIVE_ROOT / "results" / "route_result_bridge.h"
    bindings = (REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "module.cpp").read_text(
        encoding="utf-8"
    )
    equilibrium_registration = (EQUILIBRIUM_NATIVE_ROOT / "register_bindings.cpp").read_text(encoding="utf-8")

    assert bridge.exists()
    assert '#include "equilibrium/results/route_result_bridge.h"' not in bindings
    assert '#include "equilibrium/results/route_result_bridge.h"' in equilibrium_registration
    assert "apply_eos_route_metadata_fields(out, result);" in equilibrium_registration
    assert "apply_ipopt_route_status_fields(out, result);" in equilibrium_registration
    assert "apply_ipopt_route_solution_fields(out, result);" in equilibrium_registration


def test_selector_core_and_two_phase_support_have_dedicated_owners() -> None:
    selector = EQUILIBRIUM_NATIVE_ROOT / "core" / "selector_core.cpp"
    source = (EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.cpp").read_text(encoding="utf-8")

    assert selector.exists()
    assert "solve_selector_route" in selector.read_text(encoding="utf-8")
    assert "solve_seeded_neutral_two_phase_route" not in source
