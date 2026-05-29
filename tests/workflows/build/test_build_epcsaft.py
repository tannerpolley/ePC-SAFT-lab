from __future__ import annotations

import json

import pytest

from scripts.dev import build_epcsaft


def test_build_script_rejects_clean_build_only_combination(monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["build_epcsaft.py", "--clean", "--build-only"])

    with pytest.raises(SystemExit) as excinfo:
        build_epcsaft.main()

    assert excinfo.value.code == 2
    assert "--clean cannot be combined with --build-only" in capsys.readouterr().err


def test_build_script_help_lists_incremental_workflow_flags(capsys) -> None:
    parser = build_epcsaft._parser()

    parser.print_help()
    help_text = capsys.readouterr().out

    assert "--configure-only" in help_text
    assert "--build-only" in help_text
    assert "--parallel" in help_text
    assert "--profile" in help_text
    assert "--status" in help_text


def test_build_script_default_profile_builds_extension_native_modules() -> None:
    args = build_epcsaft._parser().parse_args([])
    settings = build_epcsaft._resolve_settings(args)

    assert args.profile == "fast"
    assert settings.enable_ceres is True
    assert settings.build_equilibrium_native_module is True
    assert settings.build_regression_native_module is True
    assert settings.enable_ipopt is True
    assert settings.parallel == "4"


def test_build_script_can_disable_only_ipopt() -> None:
    args = build_epcsaft._parser().parse_args(["--disable-ipopt"])
    settings = build_epcsaft._resolve_settings(args)

    assert settings.build_equilibrium_native_module is True
    assert settings.build_regression_native_module is True
    assert settings.enable_ipopt is False


def test_build_script_provider_profile_disables_extension_native_modules() -> None:
    args = build_epcsaft._parser().parse_args(["--profile", "provider"])
    settings = build_epcsaft._resolve_settings(args)

    assert settings.enable_ceres is False
    assert settings.build_equilibrium_native_module is False
    assert settings.build_regression_native_module is False
    assert settings.enable_ipopt is False
    assert settings.parallel == "4"


def test_build_script_passes_profile_to_cmake(monkeypatch) -> None:
    captured: dict[str, list[str]] = {}

    monkeypatch.setattr(build_epcsaft, "_capture", lambda cmd, env: "C:/pybind11")
    monkeypatch.setattr(build_epcsaft, "_cmake_command", lambda: ["cmake"])
    monkeypatch.setattr(build_epcsaft, "_pyproject_version", lambda: "0.2.0")
    monkeypatch.setattr(build_epcsaft, "_generator_args", lambda env, configured_generator=None: [])
    monkeypatch.setattr(build_epcsaft, "_run", lambda cmd, env: captured.setdefault("cmd", cmd))

    build_epcsaft._configure(
        {},
        build_profile="provider",
        enable_ceres=False,
        build_equilibrium_native_module=False,
        build_regression_native_module=False,
        use_system_ceres=False,
        ceres_dir=None,
        use_system_cppad=False,
        enable_ipopt=False,
        use_system_ipopt=False,
        ipopt_dir=None,
        ipopt_root=None,
        build_type="Release",
    )

    assert "-DEPCSAFT_BUILD_PROFILE=provider" in captured["cmd"]


def test_build_script_rejects_solver_overrides_when_provider_profile_disables_their_native_modules() -> None:
    with pytest.raises(ValueError, match="Ipopt cannot be enabled"):
        build_epcsaft._resolve_settings(build_epcsaft._parser().parse_args(["--profile", "provider", "--enable-ipopt"]))


def test_build_script_uses_local_windows_ipopt_sdk_default(monkeypatch, tmp_path) -> None:
    ipopt_root = tmp_path / "Documents" / "deps" / "ipopt-msvc"
    ipopt_root.mkdir(parents=True)
    monkeypatch.delenv("EPCSAFT_IPOPT_ROOT", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_IPOPT_ROOT", raising=False)

    args = build_epcsaft._parser().parse_args([])
    settings = build_epcsaft._resolve_settings(args)

    assert build_epcsaft.resolve_ipopt_root_for_build(
        None,
        enable_ipopt=settings.enable_ipopt,
        ipopt_dir=args.ipopt_dir,
        default_root=ipopt_root,
        label="Ipopt root",
    ) == ipopt_root.resolve()


def test_build_script_profiles_resolve_optional_native_dependency_state() -> None:
    full = build_epcsaft._resolve_settings(build_epcsaft._parser().parse_args(["--profile", "full"]))
    fast = build_epcsaft._resolve_settings(build_epcsaft._parser().parse_args(["--profile", "fast"]))
    ipopt = build_epcsaft._resolve_settings(build_epcsaft._parser().parse_args(["--profile", "ipopt"]))
    provider = build_epcsaft._resolve_settings(build_epcsaft._parser().parse_args(["--profile", "provider"]))
    system_ceres = build_epcsaft._resolve_settings(
        build_epcsaft._parser().parse_args(["--ceres-dir", "C:/ceres/lib/cmake/Ceres"])
    )
    system_ipopt = build_epcsaft._resolve_settings(
        build_epcsaft._parser().parse_args(["--ipopt-dir", "C:/ipopt/lib/cmake/Ipopt"])
    )

    assert full.enable_ipopt is True
    assert full.parallel == "4"
    assert fast.enable_ipopt is True
    assert fast.parallel == "4"
    assert ipopt.enable_ipopt is True
    assert ipopt.parallel == "4"
    assert provider.enable_ceres is False
    assert provider.build_equilibrium_native_module is False
    assert provider.build_regression_native_module is False
    assert provider.enable_ipopt is False
    assert system_ceres.enable_ipopt is True
    assert system_ipopt.enable_ipopt is True


def test_package_and_dev_defaults_require_ceres_and_cppad() -> None:
    cmake_text = (build_epcsaft.REPO_ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    root_pyproject_text = (build_epcsaft.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pyproject_text = (build_epcsaft.REPO_ROOT / "packages" / "epcsaft" / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    presets = json.loads((build_epcsaft.REPO_ROOT / "CMakePresets.json").read_text(encoding="utf-8"))

    assert 'option(EPCSAFT_ENABLE_CERES "Enable Ceres Solver support for native regression solves" ON)' in cmake_text
    assert 'option(EPCSAFT_ENABLE_CPPAD "Enable package-wide CppAD support" ON)' in cmake_text
    assert 'option(EPCSAFT_ENABLE_IPOPT "Enable native Ipopt support for production equilibrium NLP solves" ON)' in cmake_text
    assert "EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE" in cmake_text
    assert "EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE" in cmake_text
    assert "EPCSAFT_BUILD_PROFILE" in cmake_text
    assert 'EPCSAFT_BUILD_PROFILE STREQUAL "provider"' in cmake_text
    assert "EPCSAFT_ENABLE_CERES=OFF is not supported" not in cmake_text
    assert "derivative-capable package builds require CppAD" in cmake_text
    assert 'set(EPCSAFT_CERES_VERSION "2.2.0")' in cmake_text
    assert "find_package(Ceres ${EPCSAFT_CERES_VERSION} CONFIG REQUIRED)" in cmake_text
    assert "GIT_SHALLOW TRUE" in cmake_text
    assert 'add_subdirectory("${ceres_solver_SOURCE_DIR}" "${ceres_solver_BINARY_DIR}" EXCLUDE_FROM_ALL)' in cmake_text
    assert "EPCSAFT_NATIVE_MODEL_SOURCES" in cmake_text
    assert "EPCSAFT_NATIVE_EOS_SOURCES" in cmake_text
    assert "EPCSAFT_NATIVE_AUTODIFF_SOURCES" in cmake_text
    assert "EPCSAFT_NATIVE_EQUILIBRIUM_SOURCES" in cmake_text
    assert "EPCSAFT_NATIVE_REGRESSION_SOURCES" in cmake_text
    assert "EPCSAFT_PROVIDER_NATIVE_SOURCES" in cmake_text
    assert "EPCSAFT_NATIVE_OBJECT_TARGETS" in cmake_text
    assert "add_library(epcsaft_provider_native OBJECT" in cmake_text
    assert "add_library(epcsaft_equilibrium_native OBJECT" in cmake_text
    assert "add_library(epcsaft_regression_native OBJECT" in cmake_text
    assert "target_link_libraries(epcsaft_regression_native PUBLIC Ceres::ceres)" in cmake_text
    assert 'target_link_libraries(epcsaft_equilibrium_native PUBLIC "${EPCSAFT_IPOPT_TARGET}")' in cmake_text
    assert "EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS" in cmake_text
    assert "EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS" in cmake_text
    assert "EPCSAFT_REGRESSION_NATIVE_INCLUDE_DIRS" in cmake_text
    assert "file(GLOB EPCSAFT_NATIVE_SOURCES" not in cmake_text
    assert "src/epcsaft/native/*.cpp" not in cmake_text
    assert "src/epcsaft/native/cppad/*.cpp" not in cmake_text
    assert "src/epcsaft/native/contributions/*.cpp" not in cmake_text
    assert "src/epcsaft/native/equilibrium_nlp/*.cpp" not in cmake_text
    assert "src/epcsaft/native/equilibrium_nlp" not in cmake_text
    assert "pybind11_add_module(_core NO_EXTRAS src/epcsaft/bindings.cpp)" not in cmake_text
    assert "pybind11_add_module(_core NO_EXTRAS" in cmake_text
    assert "EPCSAFT_PROVIDER_NATIVE_ROOT" in cmake_text
    assert "bindings/module.cpp" in cmake_text
    assert "EPCSAFT_EQUILIBRIUM_REGISTER_BINDINGS_SOURCE" in cmake_text
    assert 'ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_equilibrium"' in cmake_text
    assert 'ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_regression"' in cmake_text
    assert "packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp" not in cmake_text
    assert "unset(Ceres_BINARY_DIR CACHE)" in cmake_text
    assert "unset(Ceres_SOURCE_DIR CACHE)" in cmake_text
    assert "EPCSAFT_ENABLE_CERES" not in root_pyproject_text
    assert "EPCSAFT_ENABLE_CERES" not in pyproject_text

    native_default = next(p for p in presets["configurePresets"] if p["name"] == "native-default")
    assert native_default["cacheVariables"]["EPCSAFT_ENABLE_CERES"] == "ON"
    assert native_default["cacheVariables"]["EPCSAFT_ENABLE_CPPAD"] == "ON"
    assert native_default["cacheVariables"]["EPCSAFT_ENABLE_IPOPT"] == "ON"

    native_required = next(p for p in presets["configurePresets"] if p["name"] == "native-required")
    assert native_required["cacheVariables"]["EPCSAFT_ENABLE_CERES"] == "ON"
    assert native_required["cacheVariables"]["EPCSAFT_ENABLE_CPPAD"] == "ON"

    native_ceres_cppad = next(p for p in presets["configurePresets"] if p["name"] == "native-ceres-cppad")
    assert native_ceres_cppad["cacheVariables"]["EPCSAFT_ENABLE_CERES"] == "ON"
    assert native_ceres_cppad["cacheVariables"]["EPCSAFT_ENABLE_CPPAD"] == "ON"

    native_system_ceres = next(p for p in presets["configurePresets"] if p["name"] == "native-system-ceres")
    assert native_system_ceres["cacheVariables"]["EPCSAFT_ENABLE_CERES"] == "ON"
    assert native_system_ceres["cacheVariables"]["EPCSAFT_USE_SYSTEM_CERES"] == "ON"
    assert native_system_ceres["cacheVariables"]["EPCSAFT_ENABLE_CPPAD"] == "ON"

    dev_native = next(p for p in presets["configurePresets"] if p["name"] == "dev-native")
    assert dev_native["generator"] == "Ninja"
    assert dev_native["binaryDir"] == "${sourceDir}/build/dev"
    assert dev_native["cacheVariables"]["CMAKE_BUILD_TYPE"] == "Release"
    assert dev_native["cacheVariables"]["CMAKE_MAKE_PROGRAM"] == "${sourceDir}/.venv/Scripts/ninja.exe"
    assert dev_native["cacheVariables"]["EPCSAFT_ENABLE_CERES"] == "ON"
    assert dev_native["cacheVariables"]["EPCSAFT_ENABLE_CPPAD"] == "ON"


def test_build_status_reports_generator_core_optional_flags_and_stale_lock(tmp_path, monkeypatch) -> None:
    build_dir = tmp_path / "build" / "dev"
    package_dir = tmp_path / "src" / "epcsaft"
    build_dir.mkdir(parents=True)
    package_dir.mkdir(parents=True)
    (package_dir / "_core.cp313-win_amd64.pyd").write_bytes(b"native")
    (build_dir / ".ninja_lock").write_text("", encoding="utf-8")
    (build_dir / ".ninja_log").write_text(
        "# ninja log v7\n1\t2\t3\tCMakeFiles/example.cpp.obj\tabc\n",
        encoding="utf-8",
    )
    (build_dir / "CMakeCache.txt").write_text(
        "\n".join(
            [
                "CMAKE_GENERATOR:INTERNAL=Ninja",
                "EPCSAFT_BUILD_PROFILE:STRING=provider",
                "EPCSAFT_ENABLE_CERES:BOOL=ON",
                "EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE:BOOL=ON",
                "EPCSAFT_USE_SYSTEM_CERES:BOOL=OFF",
                "EPCSAFT_ENABLE_CPPAD:BOOL=ON",
                "EPCSAFT_ENABLE_IPOPT:BOOL=OFF",
                "EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE:BOOL=ON",
                "EPCSAFT_USE_SYSTEM_IPOPT:BOOL=ON",
                "Ipopt_DIR:PATH=C:/ipopt/lib/cmake/Ipopt",
                "Ceres_DIR:PATH=C:/ceres/lib/cmake/Ceres",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(build_epcsaft, "BUILD_DIR", build_dir)
    monkeypatch.setattr(build_epcsaft, "PACKAGE_DIR", package_dir)
    monkeypatch.setattr(build_epcsaft, "_repo_build_processes", lambda: [])

    lines = build_epcsaft._status_lines(stale_lock_seconds=0)

    assert "configured_generator: Ninja" in lines
    assert "native_core: present" in lines
    assert "build_profile: provider" in lines
    assert "ceres_configured: ON" in lines
    assert "regression_native_module_configured: ON" in lines
    assert "system_ceres_configured: OFF" in lines
    assert "ceres_dir: C:/ceres/lib/cmake/Ceres" in lines
    assert "cppad_configured: ON" in lines
    assert "ipopt_configured: OFF" in lines
    assert "equilibrium_native_module_configured: ON" in lines
    assert "system_ipopt_configured: ON" in lines
    assert "ipopt_dir: C:/ipopt/lib/cmake/Ipopt" in lines
    assert "profile_hint: fast/full-no-ipopt" in lines
    assert "ninja_lock: present" in lines
    assert "stale_ninja_lock: true" in lines
    assert "last_ninja_target: CMakeFiles/example.cpp.obj" in lines


def test_source_checkout_build_syncs_editable_native_import_target(tmp_path, monkeypatch) -> None:
    source_package = tmp_path / "packages" / "epcsaft" / "src" / "epcsaft"
    editable_site = tmp_path / "venv" / "Lib" / "site-packages"
    editable_package = editable_site / "epcsaft"
    source_package.mkdir(parents=True)
    editable_package.mkdir(parents=True)
    (editable_site / "_epcsaft_editable.py").write_text("# editable marker\n", encoding="utf-8")
    source_artifact = source_package / "_core.cp313-win_amd64.pyd"
    source_artifact.write_bytes(b"source-build")
    stale_artifact = editable_package / "_core.cp312-win_amd64.pyd"
    stale_artifact.write_bytes(b"stale")

    monkeypatch.setattr(build_epcsaft, "PACKAGE_DIR", source_package)
    monkeypatch.setattr(build_epcsaft.sysconfig, "get_path", lambda name: str(editable_site) if name == "purelib" else None)

    build_epcsaft._sync_editable_native_artifacts()

    assert (editable_package / source_artifact.name).read_bytes() == b"source-build"
    assert not stale_artifact.exists()
