from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import epcsaft
import epcsaft_equilibrium
import epcsaft_regression
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PROVIDER_NATIVE_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src" / "epcsaft" / "native"

CONTRACTS = {
    "provider": REPO_ROOT / "docs" / "contracts" / "provider_api_v1.md",
    "provider_native": REPO_ROOT / "docs" / "contracts" / "provider_native_sdk_v1.md",
    "extension": REPO_ROOT / "docs" / "contracts" / "extension_compatibility.md",
    "native": REPO_ROOT / "docs" / "contracts" / "native_extension_boundary.md",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _copy_provider_package(tmp_path: Path) -> Path:
    source_package = REPO_ROOT / "packages" / "epcsaft" / "src" / "epcsaft"
    copied_package = tmp_path / "epcsaft"
    shutil.copytree(source_package, copied_package)
    return copied_package


def _write_provider_manifest(copied_package: Path, mutate) -> None:
    manifest_path = copied_package / "native_sdk" / "provider_native_sdk_v1" / "provider_sources.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _run_provider_sdk_probe(tmp_path: Path, copied_package: Path) -> subprocess.CompletedProcess[str]:
    probe_source = tmp_path / "probe"
    probe_source.mkdir()
    (probe_source / "CMakeLists.txt").write_text(
        "\n".join(
            [
                "cmake_minimum_required(VERSION 3.20)",
                "project(provider_manifest_probe LANGUAGES CXX)",
                f'set(EPCSAFT_EIGEN_INCLUDE "{(copied_package / "native").as_posix()}")',
                f'include("{(copied_package / "native_sdk" / "provider_native_sdk_v1" / "epcsaft_provider_sdk.cmake").as_posix()}")',
                "epcsaft_provider_sdk_add_provider_native(provider_manifest_probe)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return subprocess.run(
        ["cmake", "-S", str(probe_source), "-B", str(tmp_path / "build")],
        check=False,
        capture_output=True,
        text=True,
    )


def _assert_provider_sdk_manifest_error(result: subprocess.CompletedProcess[str], message: str) -> None:
    combined_output = " ".join((result.stdout + result.stderr).split())
    assert result.returncode != 0
    assert message in combined_output


def test_package_extension_contract_docs_exist_and_share_status() -> None:
    for path in CONTRACTS.values():
        text = _read(path)
        assert "Status: pre-extraction contract." in text

    assert "provider_api_v1" in _read(CONTRACTS["provider"])
    assert "provider_native_sdk_v1" in _read(CONTRACTS["provider_native"])
    assert "Final package ownership" in _read(CONTRACTS["extension"])
    assert "Target Native Ownership" in _read(CONTRACTS["native"])


def test_transfer_plan_current_state_matches_runtime_boundary_progress() -> None:
    plan = _read(CONTRACTS["provider"])

    assert "provider-scoped `capabilities()`" in plan
    assert "provider runtime metadata still reports regression transition capability data" not in plan


def test_adr_and_source_docs_agree_on_package_owners() -> None:
    files = [
        REPO_ROOT / "docs" / "adr" / "0005-package-extension-split.md",
        REPO_ROOT / "docs" / "superpowers" / "PROJECT_CONTEXT.md",
        REPO_ROOT / "docs" / "pages" / "package_architecture.rst",
        REPO_ROOT / "docs" / "protocols" / "build_package_dependency_protocol.rst",
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "pages" / "README.rst",
    ]

    for path in files:
        text = _read(path)
        assert "epcsaft-equilibrium" in text, path
        assert "epcsaft-regression" in text, path


def test_live_docs_do_not_use_rejected_core_ownership_phrases() -> None:
    stale_phrases = (
        "package-owned equilibrium/regression",
        "package-owned phase",
        "Regression and equilibrium are core package capabilities",
        "one installable distribution",
        "avoid splitting EOS/equilibrium/regression",
        "Downstream projects should file GitHub issues against ``tannerpolley/ePC-SAFT``",
    )
    roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "pages",
        REPO_ROOT / "docs" / "protocols",
        REPO_ROOT / "docs" / "agents",
        REPO_ROOT / "docs" / "contracts",
    ]

    offenders: list[str] = []
    for root in roots:
        paths = [root] if root.is_file() else list(root.rglob("*"))
        for path in paths:
            if path.is_file() and path.suffix in {".md", ".rst"}:
                text = _read(path)
                for phrase in stale_phrases:
                    if phrase in text:
                        offenders.append(f"{path.relative_to(REPO_ROOT)}: {phrase}")

    assert offenders == []


def test_extension_compatibility_contract_rejects_hidden_core_wrappers() -> None:
    text = _read(CONTRACTS["extension"])

    assert "Core provider imports must not import extension packages by default." in text
    assert "must not use private" in text
    assert "hidden long-lived compatibility wrappers" in text
    assert "removed in the coordinated migration" in text


def test_runtime_capabilities_are_separable_by_future_package_owner() -> None:
    capabilities = epcsaft.capabilities()

    assert capabilities["package"] == "epcsaft"
    assert capabilities["owner"] == "core_provider"
    assert capabilities["reports_only_provider_capabilities_after_split"] is True
    assert capabilities["native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert "package_ownership" not in capabilities
    assert "package_views" not in capabilities
    assert "equilibrium" not in capabilities
    assert "regression" not in capabilities
    assert "optimizers" not in capabilities

    equilibrium_capabilities = epcsaft_equilibrium.capabilities()
    assert equilibrium_capabilities["package"] == "epcsaft-equilibrium"
    assert equilibrium_capabilities["owner"] == "equilibrium_extension"
    assert equilibrium_capabilities["provider_contract"]["provider_native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert equilibrium_capabilities["forbidden_default_dependencies"] == ["ceres"]
    assert equilibrium_capabilities["requires"] == ["epcsaft", "cppad", "ipopt"]
    assert equilibrium_capabilities["public_routes"] == [
        "bubble_pressure",
        "dew_pressure",
        "single_component_vle",
    ]

    regression_capabilities = epcsaft_regression.capabilities()
    assert regression_capabilities["package"] == "epcsaft-regression"
    assert regression_capabilities["owner"] == "regression_extension"
    assert regression_capabilities["provider_contract"]["provider_native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert regression_capabilities["forbidden_default_dependencies"] == ["ipopt"]
    assert regression_capabilities["requires"] == ["epcsaft", "cppad", "ceres"]


def test_provider_native_sdk_is_runtime_visible_without_extension_ownership() -> None:
    sdk = epcsaft.provider_native_sdk()

    assert sdk["contract_id"] == "provider_native_sdk_v1"
    assert sdk["provider_api_contract_id"] == "provider_api_v1"
    assert sdk["owner_package"] == "epcsaft"
    assert sdk["native_target"] == "epcsaft_provider_native"
    assert sdk["required_native_dependencies"] == ["cppad", "eigen"]
    assert sdk["forbidden_native_dependencies"] == ["ceres", "ipopt"]
    assert sdk["extension_consumers"] == ["epcsaft-equilibrium", "epcsaft-regression"]
    assert "epcsaft._core" not in sdk["stable_python_surface"]
    assert sdk["native_contract_exported"] is True
    assert sdk["provider_only_core"] is True
    assert sdk["equilibrium_native_enabled"] is False
    assert sdk["regression_native_enabled"] is False
    assert sdk["native_metadata"]["native_target"] == "epcsaft_provider_native"
    assert sdk["source_sdk_kind"] == "source_cmake_sdk"
    assert sdk["source_sdk_version"] == "provider_native_sdk_v1"
    assert sdk["cmake_config_path"].endswith("epcsaft_provider_sdk.cmake")
    assert sdk["source_manifest_path"].endswith("provider_sources.json")
    assert Path(sdk["include_root"]).as_posix().endswith("epcsaft/native")
    assert sdk["supported_extension_native_modules"] == [
        "epcsaft_equilibrium._native_core",
        "epcsaft_regression._native_core",
    ]


def test_root_and_provider_package_builds_consume_canonical_provider_source_manifest() -> None:
    root_cmake = (REPO_ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    package_cmake = (REPO_ROOT / "packages" / "epcsaft" / "CMakeLists.txt").read_text(encoding="utf-8")
    helper = (
        REPO_ROOT
        / "packages"
        / "epcsaft"
        / "src"
        / "epcsaft"
        / "native_sdk"
        / "provider_native_sdk_v1"
        / "epcsaft_provider_sdk.cmake"
    )
    manifest = helper.with_name("provider_sources.json")

    assert helper.is_file()
    assert manifest.is_file()
    for cmake_text in (root_cmake, package_cmake):
        assert "epcsaft_provider_sdk.cmake" in cmake_text
        assert "set(EPCSAFT_PROVIDER_NATIVE_SOURCES" not in cmake_text
        assert "set(EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS" not in cmake_text
        assert "native/model/parameter_setup.cpp" not in cmake_text


def test_provider_source_manifest_declares_only_existing_paths() -> None:
    manifest_path = (
        REPO_ROOT
        / "packages"
        / "epcsaft"
        / "src"
        / "epcsaft"
        / "native_sdk"
        / "provider_native_sdk_v1"
        / "provider_sources.json"
    )
    package_root = manifest_path.parents[2]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    role_checks = {
        "sources": Path.is_file,
        "include_dirs": Path.is_dir,
    }

    for key, role_check in role_checks.items():
        entries = manifest[key]
        assert len(entries) == len(set(entries))
        for relative_path in entries:
            assert relative_path
            assert role_check(package_root / relative_path), relative_path


def test_provider_source_manifest_mutation_drives_sdk_target_graph(tmp_path: Path) -> None:
    copied_package = _copy_provider_package(tmp_path)

    manifest_path = copied_package / "native_sdk" / "provider_native_sdk_v1" / "provider_sources.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutated_source = "native/manifest_mutation.cpp"
    mutated_include_dir = "native/manifest_include_mutation"
    (copied_package / mutated_source).write_text(
        "int provider_manifest_mutation = 0;\n",
        encoding="utf-8",
    )
    (copied_package / mutated_include_dir).mkdir()
    manifest["sources"].append(mutated_source)
    manifest["include_dirs"].append(mutated_include_dir)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    probe_source = tmp_path / "probe"
    probe_source.mkdir()
    (probe_source / "CMakeLists.txt").write_text(
        "\n".join(
            [
                "cmake_minimum_required(VERSION 3.20)",
                "project(provider_manifest_probe LANGUAGES CXX)",
                f'set(EPCSAFT_EIGEN_INCLUDE "{(copied_package / "native").as_posix()}")',
                f'include("{(copied_package / "native_sdk" / "provider_native_sdk_v1" / "epcsaft_provider_sdk.cmake").as_posix()}")',
                "epcsaft_provider_sdk_add_provider_native(provider_manifest_probe)",
                "get_target_property(provider_sources provider_manifest_probe SOURCES)",
                "get_target_property(provider_include_dirs provider_manifest_probe INCLUDE_DIRECTORIES)",
                f'list(FIND provider_sources "{(copied_package / mutated_source).as_posix()}" source_index)',
                f'list(FIND provider_include_dirs "{(copied_package / mutated_include_dir).as_posix()}" include_dir_index)',
                'if(source_index EQUAL -1 OR include_dir_index EQUAL -1)',
                '    message(FATAL_ERROR "provider target did not consume the mutated manifest graph")',
                "endif()",
                "",
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        ["cmake", "-S", str(probe_source), "-B", str(tmp_path / "build")],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    ("manifest_key", "mutated_entry", "message"),
    [
        ("sources", "native/missing_source.cpp", "Provider native source manifest entry does not exist"),
        ("include_dirs", "native/missing_include_root", "Provider native source manifest entry does not exist"),
        ("sources", "", "Provider native source manifest path must be a nonempty package-relative path"),
        ("include_dirs", "", "Provider native source manifest path must be a nonempty package-relative path"),
        ("sources", "native/eos", "Provider native source manifest 'sources' entries must be existing files"),
        ("include_dirs", "native/model/parameter_setup.cpp", "Provider native source manifest 'include_dirs' entries must be existing directories"),
    ],
)
def test_provider_source_manifest_invalid_entries_break_sdk_loader(
    tmp_path: Path,
    manifest_key: str,
    mutated_entry: str,
    message: str,
) -> None:
    copied_package = _copy_provider_package(tmp_path)
    _write_provider_manifest(
        copied_package,
        lambda manifest: manifest[manifest_key].append(mutated_entry),
    )

    result = _run_provider_sdk_probe(tmp_path, copied_package)

    _assert_provider_sdk_manifest_error(result, message)


@pytest.mark.parametrize(
    ("manifest_key", "duplicate_entry", "message"),
    [
        ("sources", "native/model/parameter_setup.cpp", "Provider native source manifest 'sources' entries must be unique"),
        ("include_dirs", "native/model", "Provider native source manifest 'include_dirs' entries must be unique"),
    ],
)
def test_provider_source_manifest_duplicate_entries_break_sdk_loader(
    tmp_path: Path,
    manifest_key: str,
    duplicate_entry: str,
    message: str,
) -> None:
    copied_package = _copy_provider_package(tmp_path)
    _write_provider_manifest(
        copied_package,
        lambda manifest: manifest[manifest_key].append(duplicate_entry),
    )

    result = _run_provider_sdk_probe(tmp_path, copied_package)

    _assert_provider_sdk_manifest_error(result, message)


def test_provider_owns_pure_neutral_parameter_derivative_native_symbol() -> None:
    definition_fragment = "CppADDerivativeResult cppad_pure_neutral_parameter_derivatives_cpp("
    definitions: list[str] = []
    for root in (
        PROVIDER_NATIVE_ROOT,
        REPO_ROOT / "packages" / "epcsaft-equilibrium",
        REPO_ROOT / "packages" / "epcsaft-regression",
    ):
        for path in sorted(root.rglob("*.cpp")):
            if definition_fragment in _read(path):
                definitions.append(path.relative_to(REPO_ROOT).as_posix())

    assert definitions == ["packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/pure_neutral.cpp"]


def test_downstream_protocol_uses_clean_repository_intake_boundary() -> None:
    downstream = _read(REPO_ROOT / "docs" / "pages" / "downstream_dependency_protocol.rst")

    assert "current clean repository's own contribution channel" in downstream
    assert "preserved lab does not route or mutate live issues" in downstream
    assert "ePC-SAFT/ePC-SAFT" not in downstream


def test_downstream_local_install_docs_use_provider_scoped_capabilities() -> None:
    downstream = _read(REPO_ROOT / "docs" / "pages" / "downstream_local_installs.rst")

    assert 'provider_caps["package"] == "epcsaft"' in downstream
    assert 'provider_caps["package_ownership"]' not in downstream
