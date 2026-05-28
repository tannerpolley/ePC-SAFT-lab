from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
NATIVE_CONTRACT = REPO_ROOT / "docs" / "contracts" / "native_extension_boundary.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_native_boundary_contract_names_current_transition_state() -> None:
    text = _read(NATIVE_CONTRACT)
    normalized = " ".join(text.split())
    cmake = _read(REPO_ROOT / "CMakeLists.txt")

    assert "one native `_core` module" in text
    assert "logical native object targets" in normalized
    assert "epcsaft_provider_native" in cmake
    assert "epcsaft_equilibrium_native" in cmake
    assert "epcsaft_regression_native" in cmake
    assert "EPCSAFT_ENABLE_IPOPT" in cmake
    assert "EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE" in cmake
    assert "EPCSAFT_ENABLE_REGRESSION_NATIVE" in cmake


def test_native_boundary_contract_defines_logical_target_split() -> None:
    text = _read(NATIVE_CONTRACT)

    for target in (
        "provider/autodiff target",
        "equilibrium/Ipopt target",
        "regression/Ceres target",
    ):
        assert target in text

    assert "Provider target:" in text
    assert "must not link Ceres" in text
    assert "must not link Ipopt" in text
    assert "Equilibrium target:" in text
    assert "owns Ipopt linkage" in text
    assert "must not link Ceres" in text
    assert "Regression target:" in text
    assert "owns Ceres linkage" in text
    assert "must not link Ipopt by default" in text


def test_solver_libraries_are_linked_to_extension_owned_native_targets() -> None:
    cmake = _read(REPO_ROOT / "CMakeLists.txt")

    assert "target_link_libraries(epcsaft_regression_native PUBLIC Ceres::ceres)" in cmake
    assert 'target_link_libraries(epcsaft_equilibrium_native PUBLIC "${EPCSAFT_IPOPT_TARGET}")' in cmake
    assert 'target_link_libraries(epcsaft_provider_native PUBLIC "${EPCSAFT_CPPAD_LIBRARY}")' in cmake
    assert "target_link_libraries(epcsaft_provider_native PUBLIC Ceres::ceres)" not in cmake
    assert 'target_link_libraries(epcsaft_provider_native PUBLIC "${EPCSAFT_IPOPT_TARGET}")' not in cmake
    assert "EPCSAFT_ENABLE_CERES=OFF is not supported" not in cmake
    assert "#ifdef EPCSAFT_HAS_EQUILIBRIUM_NATIVE" in _read(REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "module.cpp")
    assert "#ifdef EPCSAFT_HAS_REGRESSION_NATIVE" in _read(REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "module.cpp")
    assert '#ifdef EPCSAFT_HAS_CERES' in _read(REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "module.cpp")


def test_provider_distribution_metadata_has_no_runtime_solver_packages() -> None:
    pyproject = tomllib.loads(_read(REPO_ROOT / "pyproject.toml"))
    dependencies = {str(item).split(">=", 1)[0].split("==", 1)[0].lower() for item in pyproject["project"]["dependencies"]}

    assert dependencies == {"numpy", "pandas"}
    assert {"ceres", "ipopt", "scipy", "casadi"}.isdisjoint(dependencies)


def test_native_boundary_contract_defines_extraction_proof_matrix() -> None:
    text = _read(NATIVE_CONTRACT)

    for proof in (
        "provider-only build or install proof passes without Ceres and Ipopt",
        "equilibrium proof passes with Ipopt and without Ceres",
        "regression proof passes with Ceres and without Ipopt",
        "regression/equilibrium integration proof is explicit and separate",
        "capability reports are package-owned and evidence-backed",
        "cmake.define.EPCSAFT_ENABLE_CERES=OFF",
        "cmake.define.EPCSAFT_ENABLE_IPOPT=OFF",
        "cmake.define.EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=OFF",
        "cmake.define.EPCSAFT_ENABLE_REGRESSION_NATIVE=OFF",
    ):
        assert proof in text


def test_provider_native_sdk_contract_is_bound_to_runtime_and_native_metadata() -> None:
    contract = _read(REPO_ROOT / "docs" / "contracts" / "provider_native_sdk_v1.md")
    runtime_init = _read(REPO_ROOT / "src" / "epcsaft" / "runtime" / "__init__.py")
    package_init = _read(REPO_ROOT / "src" / "epcsaft" / "__init__.py")
    native_stub = _read(REPO_ROOT / "src" / "epcsaft" / "_core.pyi")
    native_module = _read(REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "module.cpp")

    assert "Provider native SDK contract id: `provider_native_sdk_v1`." in contract
    assert "epcsaft_provider_native" in contract
    assert "`epcsaft._core` is not the provider-native SDK." in contract
    assert "provider_native_sdk" in runtime_init
    assert "provider_native_sdk" in package_init
    assert "_native_provider_sdk_contract" in native_stub
    assert "_native_provider_sdk_contract" in native_module
