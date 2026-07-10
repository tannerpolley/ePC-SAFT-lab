from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.dev import generate_equilibrium_activation as generator


def _copy_provider_package(tmp_path: Path) -> Path:
    source_package = generator.REPO_ROOT / "packages" / "epcsaft" / "src" / "epcsaft"
    copied_package = tmp_path / "epcsaft"
    shutil.copytree(source_package, copied_package)
    return copied_package


def _copy_equilibrium_package(tmp_path: Path) -> Path:
    source_package = generator.REPO_ROOT / "packages" / "epcsaft-equilibrium"
    copied_package = tmp_path / "epcsaft-equilibrium"
    shutil.copytree(source_package / "cmake", copied_package / "cmake")
    native_relative = Path("src/epcsaft_equilibrium/native/equilibrium")
    shutil.copytree(source_package / native_relative, copied_package / native_relative)
    return copied_package


def _write_provider_manifest(copied_package: Path, mutate) -> None:
    manifest_path = copied_package / "native_sdk" / "provider_native_sdk_v1" / "provider_sources.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _patch_provider_identity_roots(monkeypatch: pytest.MonkeyPatch, copied_package: Path) -> None:
    monkeypatch.setattr(generator.native_freshness, "PROVIDER_PACKAGE_ROOT", copied_package)
    monkeypatch.setattr(
        generator.native_freshness,
        "PROVIDER_NATIVE_SOURCE_ROOT",
        copied_package / "native",
    )
    monkeypatch.setattr(
        generator.native_freshness,
        "PROVIDER_SDK_ROOT",
        copied_package / "native_sdk" / "provider_native_sdk_v1",
    )


def _write_equilibrium_manifest(copied_package: Path, mutate) -> None:
    manifest_path = copied_package / "cmake" / "equilibrium_native_sources.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _patch_equilibrium_identity_roots(
    monkeypatch: pytest.MonkeyPatch,
    copied_package: Path,
) -> None:
    native_root = copied_package / "src" / "epcsaft_equilibrium" / "native" / "equilibrium"
    monkeypatch.setattr(generator.native_freshness, "EQUILIBRIUM_PACKAGE_ROOT", copied_package)
    monkeypatch.setattr(generator.native_freshness, "EQUILIBRIUM_NATIVE_SOURCE_ROOT", native_root)
    monkeypatch.setattr(
        generator.native_freshness,
        "EQUILIBRIUM_NATIVE_SOURCE_MANIFEST",
        copied_package / "cmake" / "equilibrium_native_sources.json",
    )


def _run_equilibrium_manifest_probe(
    tmp_path: Path,
    copied_package: Path,
) -> subprocess.CompletedProcess[str]:
    source_dir = tmp_path / "equilibrium-manifest-probe"
    source_dir.mkdir()
    helper = copied_package / "cmake" / "EquilibriumNativeSourceIdentity.cmake"
    (source_dir / "CMakeLists.txt").write_text(
        "\n".join(
            [
                "cmake_minimum_required(VERSION 3.20)",
                "project(equilibrium_manifest_probe NONE)",
                f'include("{helper.as_posix()}")',
                "epcsaft_equilibrium_load_native_source_manifest(",
                f'    "{copied_package.as_posix()}"',
                "    object_sources",
                "    module_sources",
                "    identity_files",
                ")",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return subprocess.run(
        ["cmake", "-S", str(source_dir), "-B", str(tmp_path / "equilibrium-manifest-build")],
        check=False,
        capture_output=True,
        text=True,
    )


def test_activation_generator_rejects_loaded_native_built_from_stale_sources(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    native_path = tmp_path / "stale_native.so"
    native_path.write_text("native", encoding="utf-8")
    current = generator.native_freshness.equilibrium_native_source_identity()
    native_core = SimpleNamespace(
        __file__=str(native_path),
        __name__="stale_native",
        _native_equilibrium_build_identity=lambda: {
            "algorithm": current["algorithm"],
            "source_identity": "0" * 64,
            "source_scope": current["scope"],
            "source_file_count": current["file_count"],
            "scope_limit": current["scope_limit"],
        },
    )
    monkeypatch.setattr(generator.native_freshness, "git_commit", lambda: "0123456789abcdef")

    with pytest.raises(RuntimeError, match="loaded equilibrium native source identity does not match"):
        generator._require_fresh_native_metadata(native_core)


def test_activation_generator_accepts_exact_current_source_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    native_path = tmp_path / "fresh_native.so"
    native_path.write_text("native", encoding="utf-8")
    current = generator.native_freshness.equilibrium_native_source_identity()
    native_core = SimpleNamespace(
        __file__=str(native_path),
        __name__="fresh_native",
        _native_equilibrium_build_identity=lambda: {
            "algorithm": current["algorithm"],
            "source_identity": current["source_identity"],
            "source_scope": current["scope"],
            "source_file_count": current["file_count"],
            "scope_limit": current["scope_limit"],
        },
    )
    monkeypatch.setattr(generator.native_freshness, "git_commit", lambda: "0123456789abcdef")

    receipt = generator._require_fresh_native_metadata(native_core)

    assert receipt["source_identity_matches"] is True
    assert receipt["embedded_source_identity"] == current["source_identity"]


def test_root_and_standalone_builds_consume_canonical_native_source_manifest() -> None:
    root_cmake = (generator.REPO_ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    package_cmake = (generator.REPO_ROOT / "packages" / "epcsaft-equilibrium" / "CMakeLists.txt").read_text(
        encoding="utf-8"
    )
    helper = (
        generator.REPO_ROOT / "packages" / "epcsaft-equilibrium" / "cmake" / "EquilibriumNativeSourceIdentity.cmake"
    )
    manifest = helper.with_name("equilibrium_native_sources.json")

    assert helper.is_file()
    assert manifest.is_file()
    for cmake_text in (root_cmake, package_cmake):
        assert "EquilibriumNativeSourceIdentity.cmake" in cmake_text
        assert "epcsaft_equilibrium_load_native_source_manifest(" in cmake_text
        assert "epcsaft_equilibrium_apply_native_source_identity(" in cmake_text
        assert "blocks/association_block.cpp" not in cmake_text
        assert '"${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/module.cpp"' not in cmake_text


def test_canonical_native_source_manifest_exactly_covers_equilibrium_cpp_and_headers() -> None:
    native_root = (
        generator.REPO_ROOT
        / "packages"
        / "epcsaft-equilibrium"
        / "src"
        / "epcsaft_equilibrium"
        / "native"
        / "equilibrium"
    )
    manifest_path = (
        generator.REPO_ROOT / "packages" / "epcsaft-equilibrium" / "cmake" / "equilibrium_native_sources.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    object_sources = set(manifest["object_sources"])
    module_sources = set(manifest["module_sources"])
    headers = set(manifest["headers"])
    listed = object_sources | module_sources | headers
    discovered = {
        path.relative_to(native_root).as_posix() for pattern in ("*.cpp", "*.h") for path in native_root.rglob(pattern)
    }

    assert manifest["schema_version"] == 1
    assert module_sources == {"module.cpp", "register_bindings.cpp"}
    assert object_sources.isdisjoint(module_sources)
    assert object_sources.isdisjoint(headers)
    assert module_sources.isdisjoint(headers)
    assert listed == discovered


def test_equilibrium_identity_provider_inputs_match_manifest_sources_and_header_contracts() -> None:
    provider_root = generator.native_freshness.PROVIDER_PACKAGE_ROOT
    manifest_path = generator.native_freshness.PROVIDER_SDK_ROOT / "provider_sources.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_provider_entries = {
        "provider/native_sdk/provider_native_sdk_v1/epcsaft_provider_sdk.cmake",
        "provider/native_sdk/provider_native_sdk_v1/provider_sources.json",
    }
    expected_provider_entries.update(f"provider/{path}" for path in manifest["sources"])
    for include_dir in manifest["include_dirs"]:
        include_root = provider_root / include_dir
        for pattern in ("*.h", "*.hpp"):
            expected_provider_entries.update(
                f"provider/{path.relative_to(provider_root).as_posix()}" for path in include_root.rglob(pattern)
            )

    provider_entries = {
        logical_path
        for logical_path, _ in generator.native_freshness._equilibrium_native_identity_files()
        if logical_path.startswith("provider/")
    }

    assert provider_entries == expected_provider_entries
    assert "provider/native/bindings/module.cpp" not in provider_entries
    assert "provider/native/bindings/payload_converters.cpp" not in provider_entries


def test_equilibrium_identity_rejects_missing_provider_include_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    copied_package = _copy_provider_package(tmp_path)
    _write_provider_manifest(
        copied_package,
        lambda manifest: manifest["include_dirs"].append("native/missing_include_root"),
    )
    _patch_provider_identity_roots(monkeypatch, copied_package)

    with pytest.raises(FileNotFoundError, match="provider native source manifest entry is missing"):
        generator.native_freshness.equilibrium_native_source_identity()


@pytest.mark.parametrize(
    ("manifest_key", "duplicate_entry"),
    [
        ("sources", "native/model/parameter_setup.cpp"),
        ("include_dirs", "native/model"),
    ],
)
def test_equilibrium_identity_rejects_duplicate_provider_manifest_entries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    manifest_key: str,
    duplicate_entry: str,
) -> None:
    copied_package = _copy_provider_package(tmp_path)
    _write_provider_manifest(
        copied_package,
        lambda manifest: manifest[manifest_key].append(duplicate_entry),
    )
    _patch_provider_identity_roots(monkeypatch, copied_package)

    with pytest.raises(ValueError, match=r"provider native source manifest .* entries must be unique"):
        generator.native_freshness.equilibrium_native_source_identity()


@pytest.mark.parametrize(
    ("manifest_key", "mutated_entry", "error_type", "message"),
    [
        ("sources", "native/missing_source.cpp", FileNotFoundError, "provider native source manifest entry is missing"),
        ("sources", "", ValueError, "provider native source manifest path must be a nonempty package-relative path"),
        (
            "include_dirs",
            "",
            ValueError,
            "provider native source manifest path must be a nonempty package-relative path",
        ),
        (
            "sources",
            "native/eos",
            ValueError,
            "provider native source manifest 'sources' entries must be existing files",
        ),
        (
            "include_dirs",
            "native/model/parameter_setup.cpp",
            ValueError,
            "provider native source manifest 'include_dirs' entries must be existing directories",
        ),
    ],
)
def test_equilibrium_identity_rejects_invalid_provider_manifest_entries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    manifest_key: str,
    mutated_entry: str,
    error_type: type[Exception],
    message: str,
) -> None:
    copied_package = _copy_provider_package(tmp_path)
    _write_provider_manifest(
        copied_package,
        lambda manifest: manifest[manifest_key].append(mutated_entry),
    )
    _patch_provider_identity_roots(monkeypatch, copied_package)

    with pytest.raises(error_type, match=message):
        generator.native_freshness.equilibrium_native_source_identity()


def test_cmake_and_python_native_source_identity_manifests_match(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    build_dir = tmp_path / "build"
    source_dir.mkdir()
    (source_dir / "identity_probe.cpp").write_text("int identity_probe = 0;\n", encoding="utf-8")
    helper = (
        generator.REPO_ROOT / "packages" / "epcsaft-equilibrium" / "cmake" / "EquilibriumNativeSourceIdentity.cmake"
    )
    equilibrium_root = generator.REPO_ROOT / "packages" / "epcsaft-equilibrium"
    provider_root = generator.REPO_ROOT / "packages" / "epcsaft" / "src" / "epcsaft"
    (source_dir / "CMakeLists.txt").write_text(
        "\n".join(
            [
                "cmake_minimum_required(VERSION 3.20)",
                "project(identity_probe LANGUAGES CXX)",
                f'include("{helper.as_posix()}")',
                'add_library(identity_probe STATIC "identity_probe.cpp")',
                "epcsaft_equilibrium_apply_native_source_identity(",
                "    identity_probe",
                f'    "{equilibrium_root.as_posix()}"',
                f'    "{provider_root.as_posix()}"',
                ")",
                "get_target_property(identity identity_probe EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY)",
                "get_target_property(file_count identity_probe EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_FILE_COUNT)",
                "get_target_property(algorithm identity_probe EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_ALGORITHM)",
                "get_target_property(scope identity_probe EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_SCOPE)",
                'file(WRITE "${CMAKE_BINARY_DIR}/identity.txt" "${identity}\n${file_count}\n${algorithm}\n${scope}\n")',
                "",
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        ["cmake", "-S", str(source_dir), "-B", str(build_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    cmake_identity, cmake_count, cmake_algorithm, cmake_scope = (
        (build_dir / "identity.txt").read_text(encoding="utf-8").splitlines()
    )
    python_identity = generator.native_freshness.equilibrium_native_source_identity()

    assert cmake_identity == python_identity["source_identity"]
    assert int(cmake_count) == python_identity["file_count"]
    assert cmake_algorithm == python_identity["algorithm"]
    assert cmake_scope == python_identity["scope"]


@pytest.mark.parametrize(
    ("manifest_key", "mutated_entry", "python_error", "python_message", "cmake_message"),
    [
        (
            "object_sources",
            "",
            ValueError,
            "equilibrium native source manifest path must be package-relative",
            "Equilibrium native source manifest path must be a nonempty package-relative path",
        ),
        (
            "headers",
            "routes",
            FileNotFoundError,
            "equilibrium native identity source is missing",
            "Equilibrium native source manifest entries must be existing files",
        ),
    ],
)
def test_cmake_and_python_reject_invalid_equilibrium_manifest_entries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    manifest_key: str,
    mutated_entry: str,
    python_error: type[Exception],
    python_message: str,
    cmake_message: str,
) -> None:
    copied_package = _copy_equilibrium_package(tmp_path)
    _write_equilibrium_manifest(
        copied_package,
        lambda manifest: manifest[manifest_key].append(mutated_entry),
    )
    _patch_equilibrium_identity_roots(monkeypatch, copied_package)

    with pytest.raises(python_error, match=python_message):
        generator.native_freshness.equilibrium_native_source_identity()

    result = _run_equilibrium_manifest_probe(tmp_path, copied_package)
    combined_output = " ".join((result.stdout + result.stderr).split())
    assert result.returncode != 0
    assert cmake_message in combined_output
