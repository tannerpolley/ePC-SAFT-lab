from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ALLOWED_ROOT_PYTHON_ENTRY_FILES = {"__init__.py", "__init__.pyi", "__main__.py", "_types.py"}
ALLOWED_NATIVE_DOMAIN_FOLDERS = {
    "autodiff",
    "bindings",
    "eos",
    "equilibrium",
    "model",
    "regression",
    "runtime",
}
IMPORT_BOUNDARY_WATCHLIST = {
    "epcsaft.equilibrium",
    "epcsaft.equilibrium.core",
    "epcsaft.equilibrium.electrolyte_bubble",
    "epcsaft.equilibrium.reactive_electrolyte",
    "epcsaft.equilibrium.reactive_speciation",
    "epcsaft.equilibrium.reactive_staged",
    "epcsaft.equilibrium.workflows",
    "epcsaft.frontend",
    "epcsaft.frontend.equilibrium",
    "epcsaft.frontend.mixture",
    "epcsaft.frontend.regression",
    "epcsaft.frontend.state",
    "epcsaft.model.options",
    "epcsaft.model.parameters",
    "epcsaft.model.templates",
    "epcsaft.regression",
    "epcsaft.regression.core",
    "epcsaft.regression.reactive",
    "epcsaft.runtime",
    "epcsaft.runtime.capability_evidence",
    "epcsaft.runtime.core",
    "epcsaft.state.eos_views",
    "epcsaft.state.native_adapter",
    "epcsaft.state.properties",
}
ANALYSIS_ROOTS = {
    "2012_held": REPO_ROOT / "analyses" / "paper_validation" / "native" / "2012_held",
    "2014_held": REPO_ROOT / "analyses" / "paper_validation" / "native" / "2014_held",
    "2015_baygi": REPO_ROOT / "analyses" / "paper_validation" / "application" / "2015_baygi",
    "2019_bulow": REPO_ROOT / "analyses" / "paper_validation" / "native" / "2019_bulow",
    "2020_bulow": REPO_ROOT / "analyses" / "paper_validation" / "native" / "2020_bulow",
    "2025_figiel": REPO_ROOT / "analyses" / "paper_validation" / "native" / "2025_figiel",
    "2026_khudaida": REPO_ROOT / "analyses" / "paper_validation" / "application" / "2026_khudaida",
    "dielectric_fits": REPO_ROOT / "analyses" / "data_validation" / "dielectric_fits",
    "miac_fits": REPO_ROOT / "analyses" / "data_validation" / "miac_fits",
    "osmotic_validation": REPO_ROOT / "analyses" / "data_validation" / "osmotic_validation",
    "package_plot_smokes": REPO_ROOT / "analyses" / "package_validation" / "package_plot_smokes",
}
MIGRATED_ANALYSIS_IDS = set(ANALYSIS_ROOTS) - {"2025_figiel"}
CATEGORY_ROOTS = {
    REPO_ROOT / "analyses" / "paper_validation",
    REPO_ROOT / "analyses" / "paper_validation" / "native",
    REPO_ROOT / "analyses" / "paper_validation" / "application",
    REPO_ROOT / "analyses" / "data_validation",
    REPO_ROOT / "analyses" / "package_validation",
}
TEST_SUBGROUP_ROOTS = {
    "tests/api",
    "tests/api/frontend",
    "tests/api/package",
    "tests/native/contracts",
    "tests/native/equilibrium",
    "tests/native/equilibrium/blocks",
    "tests/native/equilibrium/diagnostics",
    "tests/native/equilibrium/results",
    "tests/native/regression",
    "tests/native/state",
    "tests/support",
    "tests/workflows/build",
    "tests/workflows/repo",
}
REPLACED_FLAT_TEST_FILES = {
    "tests/api/equilibrium",
    "tests/api/parameters",
    "tests/api/reactive",
    "tests/api/regression",
    "tests/api/runtime",
    "tests/api/test_runtime.py",
    "tests/api/test_regression_api.py",
    "tests/api/test_reactive_speciation.py",
    "tests/api/test_reactive_regression.py",
    "tests/api/test_reactive_electrolyte_bubble.py",
    "tests/api/test_cppad_api_reset.py",
    "tests/api/frontend/test_cppad_api_reset.py",
    "tests/equilibrium",
    "tests/regression",
    "tests/helpers",
    "tests/native/ceres",
    "tests/native/cppad",
    "tests/native/runtime",
    "tests/native/test_runtime_contracts.py",
    "tests/native/test_chemical_equilibrium_native.py",
    "tests/workflows/benchmarks",
}


def _probe_epcsaft_import_modules(source: str) -> set[str]:
    probe = f"""
import json
import sys

{source}

watchlist = {sorted(IMPORT_BOUNDARY_WATCHLIST)!r}
print(json.dumps(sorted(name for name in watchlist if name in sys.modules)))
"""
    env = os.environ.copy()
    src_root = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = src_root + os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else src_root
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return set(json.loads(result.stdout))


def _tracked_files(*paths: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def test_strict_solver_derivative_text_gate_passes() -> None:
    subprocess.run(
        [sys.executable, "scripts/dev/check_text_gates.py"],
        cwd=REPO_ROOT,
        text=True,
        check=True,
    )


def test_removed_numerics_stack_is_not_a_package_dev_test_or_analysis_runtime_dependency() -> None:
    removed_dependency_name = "sci" + "py"
    removed_python_ipopt_wrapper = "cy" + "ipopt"
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    lock_text = (REPO_ROOT / "uv.lock").read_text(encoding="utf-8").lower()
    assert removed_dependency_name not in pyproject_text
    assert removed_python_ipopt_wrapper not in pyproject_text
    assert removed_python_ipopt_wrapper not in lock_text

    tracked = _tracked_files("src", "tests", "scripts", "analyses", "docs", "README.md", "CHANGELOG.md")
    import_offenders: list[str] = []
    import_snippets = (f"import {removed_dependency_name}", f"from {removed_dependency_name}")
    for relpath in tracked:
        if relpath.replace("\\", "/").startswith("docs/papers/"):
            continue
        if not relpath.endswith(".py"):
            if Path(relpath).suffix.lower() not in {".md", ".rst", ".toml", ".yaml", ".yml", ".txt", ".ps1"}:
                continue
        path = REPO_ROOT / relpath
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        assert removed_python_ipopt_wrapper not in text, relpath
        if not relpath.endswith(".py"):
            continue
        path = REPO_ROOT / relpath
        if not path.exists():
            continue
        if any(snippet in text for snippet in import_snippets):
            import_offenders.append(relpath)
    assert import_offenders == []
    removed_fit_script = "/".join(
        (
            "analyses",
            "paper_validation",
            "application",
            "2026_rezaee",
            "scripts",
            "rezaee_reactive_" + "equilibrium_fit.py",
        )
    )
    assert not (REPO_ROOT / removed_fit_script).exists()
    assert not (REPO_ROOT / "src" / "epcsaft" / ("_optional" + "_backends")).exists()
    removed_ipopt_helper = REPO_ROOT / "scripts" / "dev" / ("setup_windows_" + removed_python_ipopt_wrapper + "_uv.ps1")
    assert not removed_ipopt_helper.exists()


def test_root_package_contains_only_entry_python_files() -> None:
    root_files = {
        path.name
        for path in (REPO_ROOT / "src" / "epcsaft").iterdir()
        if path.is_file() and path.suffix in {".py", ".pyi"}
    }
    assert root_files == ALLOWED_ROOT_PYTHON_ENTRY_FILES
    assert not (REPO_ROOT / "src" / "epcsaft" / "equilibrium_core").exists()
    assert (REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "core").is_dir()


def test_native_cpp_sources_live_under_domain_workflow_modules() -> None:
    native_root = REPO_ROOT / "src" / "epcsaft" / "native"
    root_native_impl_files = sorted(
        path.name for path in native_root.iterdir() if path.is_file() and path.suffix in {".cpp", ".h", ".hpp"}
    )
    assert root_native_impl_files == []
    assert not (REPO_ROOT / "src" / "epcsaft" / "bindings.cpp").exists()
    assert (native_root / "bindings" / "module.cpp").is_file()

    invalid_native_locations: list[str] = []
    for path in sorted(native_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".cpp", ".h", ".hpp"}:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        parts = Path(rel).parts
        if len(parts) < 5 or parts[3] not in ALLOWED_NATIVE_DOMAIN_FOLDERS:
            invalid_native_locations.append(rel)
    assert invalid_native_locations == []


def test_native_include_paths_do_not_reference_deleted_legacy_topology() -> None:
    native_root = REPO_ROOT / "src" / "epcsaft" / "native"
    native_sources = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in sorted(native_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp"}
    ]
    assert native_sources

    legacy_include_tokens = (
        '#include "../',
        "equilibrium_nlp/",
        "native/cppad/",
        "native/contributions/",
        "epcsaft_equilibrium.h",
        "epcsaft_chemical_equilibrium.h",
        "epcsaft_core_internal.h",
        "epcsaft_cppad_internal.h",
        "epcsaft_contrib_internal.h",
        "epcsaft_electrolyte.h",
    )
    pybind_allowed = {
        "src/epcsaft/native/bindings/module.cpp",
        "src/epcsaft/native/equilibrium/register_bindings.cpp",
        "src/epcsaft/native/equilibrium/results/route_result_bridge.h",
    }

    legacy_offenders: list[str] = []
    pybind_offenders: list[str] = []
    for rel in native_sources:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        for token in legacy_include_tokens:
            if token in text:
                legacy_offenders.append(f"{rel}: {token}")
        if "pybind11/" in text and rel not in pybind_allowed:
            pybind_offenders.append(rel)

    assert legacy_offenders == []
    assert pybind_offenders == []


def test_native_equilibrium_bindings_are_registered_through_selector_domain_units() -> None:
    module = (REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "module.cpp").read_text(
        encoding="utf-8"
    )
    bindings_root = REPO_ROOT / "src" / "epcsaft" / "native" / "bindings"
    forbidden_includes = (
        "equilibrium/blocks/",
        "equilibrium/routes/",
        "equilibrium/solvers/",
        "equilibrium/results/",
        "equilibrium/core/second_order.h",
        "equilibrium/core/two_phase_eos_route.h",
        "equilibrium/core/selector_core.h",
        "equilibrium/facade.h",
    )
    offenders = []
    for path in sorted(bindings_root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp"}:
            text = path.read_text(encoding="utf-8")
            for token in forbidden_includes:
                if token in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {token}")

    assert "register_equilibrium_bindings(m);" in module
    assert (REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium" / "register_bindings.cpp").exists()
    assert not (REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "equilibrium_binding_types.h").exists()
    assert not (REPO_ROOT / "src" / "epcsaft" / "native" / "bindings" / "equilibrium_bindings.cpp").exists()
    assert offenders == []


def test_equilibrium_facade_does_not_expose_route_builder_types() -> None:
    facade = (REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium" / "facade.h").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "equilibrium/routes/route_builders.h",
        "NativeRouteMetadata",
        "NeutralTwoPhaseEosNlpContract",
        "NeutralTwoPhaseEosRouteResult",
        "ReactiveTwoPhaseEosPostsolve",
        "ReactiveTwoPhaseEosRouteResult",
        "route_builders",
    )
    offenders = [token for token in forbidden if token in facade]

    assert offenders == []


def test_deleted_equilibrium_route_sources_and_bindings_are_absent() -> None:
    deleted_sources = (
        "src/epcsaft/native/equilibrium/workflows.cpp",
        "src/epcsaft/native/equilibrium/routes/route_builders.cpp",
        "src/epcsaft/native/equilibrium/routes/route_builders.h",
        "src/epcsaft/native/equilibrium/routes/reactive",
        "src/epcsaft/native/equilibrium/routes/stability",
    )
    for relpath in deleted_sources:
        assert not (REPO_ROOT / relpath).exists(), relpath

    binding_source_paths = [
        path
        for path in sorted((REPO_ROOT / "src" / "epcsaft" / "native" / "bindings").rglob("*"))
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp"}
    ]
    binding_source_paths.append(
        REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium" / "register_bindings.cpp"
    )
    binding_sources = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in binding_source_paths
    )
    forbidden_bindings = (
        "_native_neutral_tp_flash_eos",
        "_native_neutral_lle_eos",
        "_native_electrolyte_lle_eos",
        "_native_electrolyte_bubble_p_eos",
        "_native_neutral_stability_tpd",
        "_native_electrolyte_stability_tpd",
        "_native_reactive_stability_tpd",
        "_native_reactive_lle_eos",
        "_native_reactive_electrolyte_lle_eos",
        "_native_reactive_two_phase_eos",
        "_solve_chemical_equilibrium_native",
        "_evaluate_chemical_equilibrium_residual_native",
        "_evaluate_reactive_phase_equilibrium_residual_native",
        "_evaluate_electrolyte_lle_residual_native",
        "_native_neutral_bubble_p_eos_route_result",
        "_native_neutral_dew_p_eos_route_result",
        "_native_neutral_bubble_t_eos_route_result",
        "_native_neutral_dew_t_eos_route_result",
        "solve_neutral_bubble_p_eos_route",
        "solve_neutral_dew_p_eos_route",
        "solve_neutral_bubble_t_eos_route",
        "solve_neutral_dew_t_eos_route",
    )
    binding_offenders = [name for name in forbidden_bindings if name in binding_sources]

    assert binding_offenders == []


def test_python_equilibrium_package_exposes_only_production_selector_vle_support() -> None:
    import epcsaft
    import epcsaft.equilibrium as equilibrium
    import epcsaft.equilibrium.workflows as workflows
    from epcsaft.state.native_adapter import ePCSAFTMixture

    route_specific_methods = {
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "flash",
    }
    assert hasattr(epcsaft.Equilibrium, "solve")
    assert {name for name in route_specific_methods if hasattr(epcsaft.Equilibrium, name)} == set()
    assert {name for name in {"bubble_p", "bubble_t", "dew_p", "dew_t", "tp_flash"} if hasattr(epcsaft.Equilibrium, name)} == set()

    forbidden_exports = {
        "bubble_p",
        "bubble_t",
        "dew_p",
        "dew_t",
        "tp_flash",
        "lle_flash",
        "neutral_stability",
        "electrolyte_stability",
        "electrolyte_lle_flash_native",
        "electrolyte_bubble_pressure",
        "reactive_phase_equilibrium",
        "reactive_stability_native",
        "ReactiveSpeciationProblem",
        "ReactiveElectrolyteBubbleProblem",
        "ReactivePhaseEquilibriumProblem",
        "TPFlash",
        "LLEProblem",
        "ElectrolyteLLEProblem",
        "ElectrolyteBubblePoint",
        "StabilityAnalysis",
    }
    leaked = sorted(name for name in forbidden_exports if hasattr(equilibrium, name))

    assert leaked == []

    workflow_route_helpers = {
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "flash",
        "solve_selector_vle",
    }
    assert [name for name in workflow_route_helpers if hasattr(workflows, name)] == []
    assert [name for name in route_specific_methods if hasattr(ePCSAFTMixture, name)] == []


def test_public_python_solver_surfaces_do_not_own_optimizer_or_root_loops() -> None:
    public_solver_sources = (
        REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "workflows.py",
        REPO_ROOT / "src" / "epcsaft" / "frontend" / "equilibrium.py",
        REPO_ROOT / "src" / "epcsaft" / "frontend" / "regression.py",
        REPO_ROOT / "src" / "epcsaft" / "regression" / "core.py",
    )
    blocked_terms = (
        "sci" + "py.optimize",
        "minimize" + "_scalar",
        "root" + "_scalar",
        "least" + "_squares",
        "differential" + "_evolution",
        "brent" + "q",
        "brent" + "h",
        "f" + "solve",
        "bisect" + "ion",
        "golden" + "_section",
    )

    offenders: list[str] = []
    for path in public_solver_sources:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in blocked_terms:
            if term in text:
                offenders.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {term}")
    assert offenders == []


def test_public_vle_workflows_dispatch_only_through_selector_binding() -> None:
    workflows = (REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "workflows.py").read_text(
        encoding="utf-8"
    )
    required_selector_calls = workflows.count("_native_equilibrium_selector_route_result")
    forbidden_direct_route_bindings = (
        "_native_neutral_bubble_p_eos_route_result",
        "_native_neutral_bubble_t_eos_route_result",
        "_native_neutral_dew_p_eos_route_result",
        "_native_neutral_dew_t_eos_route_result",
        "_native_neutral_tp_flash_eos_route_result",
    )

    assert required_selector_calls >= 1
    assert [token for token in forbidden_direct_route_bindings if token in workflows] == []


def test_public_equilibrium_callers_do_not_pass_removed_route_controls() -> None:
    public_route_names = {
        "equilibrium",
        "equilibrium_curve",
        "electrolyte_lle",
        "flash",
        "electrolyte_lle_tp",
        "lle_flash",
        "lle_tp",
        "reactive_lle",
    }
    blocked_route_keywords = {"initial" + "_phases"}
    blocked_option_keywords = {"damp" + "ing", "return" + "_best" + "_effort"}

    offenders: list[str] = []
    for relpath in _tracked_files("src", "tests", "scripts", "analyses"):
        rel = relpath.replace("\\", "/")
        if not rel.endswith(".py"):
            continue
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = ""
            if isinstance(func, ast.Attribute):
                name = func.attr
            elif isinstance(func, ast.Name):
                name = func.id
            if name in public_route_names:
                for keyword in node.keywords:
                    if keyword.arg in blocked_route_keywords:
                        offenders.append(f"{rel}:{node.lineno}: public route keyword {keyword.arg}")
            if name == "EquilibriumOptions":
                for keyword in node.keywords:
                    if keyword.arg in blocked_option_keywords:
                        offenders.append(f"{rel}:{node.lineno}: removed option keyword {keyword.arg}")
    assert offenders == []


def test_custom_scalar_solver_tokens_are_limited_to_density_closure_exception() -> None:
    allowed_paths = {
        "src/epcsaft/native/eos/density.cpp",
        "src/epcsaft/native/model/native_types.h",
    }
    blocked_terms = (
        "br" + "ent",
        "bisect" + "ion",
        "golden" + "_section",
        "golden" + "-" + "section",
        "root" + "_scalar",
        "minimize" + "_scalar",
        "least" + "_squares",
        "new" + "ton",
        "line" + "_search",
        "multi" + "start",
        "multi" + "_start",
    )
    tracked = _tracked_files("src/epcsaft")

    offenders: list[str] = []
    for relpath in tracked:
        rel = relpath.replace("\\", "/")
        if rel in allowed_paths:
            continue
        if Path(rel).suffix.lower() not in {".py", ".cpp", ".h", ".hpp"}:
            continue
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in blocked_terms:
            if term in text:
                offenders.append(f"{rel}: {term}")
    assert offenders == []


def test_package_import_is_lazy_across_equilibrium_and_regression_extensions() -> None:
    loaded = _probe_epcsaft_import_modules("import epcsaft")
    assert {
        "epcsaft.frontend",
        "epcsaft.frontend.equilibrium",
        "epcsaft.frontend.mixture",
        "epcsaft.frontend.regression",
        "epcsaft.frontend.state",
        "epcsaft.model.options",
        "epcsaft.model.parameters",
        "epcsaft.model.templates",
        "epcsaft.runtime",
        "epcsaft.runtime.capability_evidence",
        "epcsaft.runtime.core",
        "epcsaft.state.eos_views",
    } <= loaded
    assert loaded.isdisjoint(
        {
            "epcsaft.equilibrium",
            "epcsaft.equilibrium.core",
            "epcsaft.equilibrium.electrolyte_bubble",
            "epcsaft.equilibrium.reactive_electrolyte",
            "epcsaft.equilibrium.reactive_speciation",
            "epcsaft.equilibrium.reactive_staged",
            "epcsaft.equilibrium.workflows",
            "epcsaft.regression",
            "epcsaft.regression.core",
            "epcsaft.regression.reactive",
            "epcsaft.state.native_adapter",
            "epcsaft.state.properties",
        }
    )


def test_frontend_import_does_not_load_solver_extensions() -> None:
    loaded = _probe_epcsaft_import_modules(
        "from epcsaft import Mixture, ModelOptions, ParameterSet\n"
        "_ = (Mixture, ModelOptions, ParameterSet)"
    )
    assert {
        "epcsaft.frontend",
        "epcsaft.frontend.mixture",
        "epcsaft.model.options",
        "epcsaft.model.parameters",
    } <= loaded
    assert loaded.isdisjoint(
        {
            "epcsaft.equilibrium",
            "epcsaft.equilibrium.core",
            "epcsaft.equilibrium.electrolyte_bubble",
            "epcsaft.equilibrium.reactive_electrolyte",
            "epcsaft.equilibrium.reactive_speciation",
            "epcsaft.equilibrium.reactive_staged",
            "epcsaft.equilibrium.workflows",
            "epcsaft.regression",
            "epcsaft.regression.core",
            "epcsaft.regression.reactive",
            "epcsaft.state.native_adapter",
            "epcsaft.state.properties",
        }
    )


def test_top_level_public_exports_load_only_the_requested_extension() -> None:
    loaded = _probe_epcsaft_import_modules("import epcsaft\n_ = epcsaft.Equilibrium")
    assert "epcsaft.frontend" in loaded
    assert "epcsaft.equilibrium" not in loaded
    assert "epcsaft.regression" not in loaded
    assert "epcsaft.regression.reactive" not in loaded


def test_reference_data_root_is_canonical() -> None:
    assert (REPO_ROOT / "data" / "reference" / "epcsaft_parameters").is_dir()
    assert not (REPO_ROOT / "data" / "epcsaft_parameters").exists()


def test_analysis_category_roots_exist() -> None:
    for root in sorted(CATEGORY_ROOTS):
        assert root.is_dir(), root


def test_migrated_analyses_have_local_contract_files() -> None:
    for analysis_id, root in sorted(ANALYSIS_ROOTS.items()):
        assert (root / "README.md").is_file(), analysis_id
        assert (root / "analysis.yaml").is_file(), analysis_id
        scripts_root = root / "scripts"
        figure_scripts = sorted((root / "figures").glob("*/scripts"))
        assert scripts_root.is_dir() or figure_scripts, analysis_id


def test_old_gallery_and_script_roots_are_not_tracked() -> None:
    assert _tracked_files("docs/plots") == []
    assert _tracked_files("scripts/paper_validation") == []
    assert _tracked_files("scripts/fits") == []
    assert _tracked_files("tests/plots") == []


def test_reorganized_test_subgroup_roots_exist() -> None:
    for relpath in sorted(TEST_SUBGROUP_ROOTS):
        assert (REPO_ROOT / relpath).is_dir(), relpath


def test_test_tree_uses_namespace_packages_without_init_markers() -> None:
    assert list((REPO_ROOT / "tests").rglob("__init__.py")) == []


def test_replaced_flat_test_modules_are_absent_from_the_working_tree() -> None:
    for relpath in sorted(REPLACED_FLAT_TEST_FILES):
        assert not (REPO_ROOT / relpath).exists(), relpath


def test_generated_output_roots_are_not_tracked_in_analyses() -> None:
    tracked = _tracked_files("analyses")
    stale = [
        path
        for path in tracked
        if "/out/" in path.replace("\\", "/")
        or "/results/runs/" in path.replace("\\", "/")
        or "/results/final/" in path.replace("\\", "/")
        or ("/figures/" in path.replace("\\", "/") and "/output/runs/" in path.replace("\\", "/"))
    ]
    assert stale == []


def test_analysis_metadata_does_not_reference_removed_final_results_layout() -> None:
    tracked = _tracked_files("analyses")
    metadata_files = [REPO_ROOT / path for path in tracked if path.endswith("/analysis.yaml")]
    assert metadata_files
    for path in metadata_files:
        text = path.read_text(encoding="utf-8")
        assert "results/final" not in text, path


def test_migrated_analysis_metadata_uses_figure_owned_outputs() -> None:
    for analysis_id in sorted(MIGRATED_ANALYSIS_IDS):
        path = ANALYSIS_ROOTS[analysis_id] / "analysis.yaml"
        text = path.read_text(encoding="utf-8")
        assert "figures: figures/<figure_id>/output" in text, path
        assert "runs: figures/<figure_id>/output/runs" in text, path


def test_migrated_analyses_use_complete_figure_owned_roots() -> None:
    for analysis_id in sorted(MIGRATED_ANALYSIS_IDS):
        figures_root = ANALYSIS_ROOTS[analysis_id] / "figures"
        assert figures_root.is_dir(), analysis_id
        figure_roots = sorted(path for path in figures_root.iterdir() if path.is_dir())
        assert figure_roots, analysis_id
        for figure_root in figure_roots:
            assert (figure_root / "scripts").is_dir(), figure_root
            optional_roots = (figure_root / "input", figure_root / "output")
            assert any(path.is_dir() for path in optional_roots) or any(
                (figure_root / "scripts").glob("*.py")
            ), figure_root


def test_selected_figure_scripts_do_not_read_canonical_data_root_directly() -> None:
    analysis_ids = ("2012_held", "2014_held", "2019_bulow", "2020_bulow")
    forbidden_snippets = (
        'REPO_ROOT / "data"',
        "REPO_ROOT / 'data'",
        'common.REPO_ROOT / "data"',
        "common.REPO_ROOT / 'data'",
        "data/reference",
    )
    for analysis_id in analysis_ids:
        figures_root = ANALYSIS_ROOTS[analysis_id] / "figures"
        for path in sorted(figures_root.rglob("*.py")):
            if path.name == "generate_data.py":
                continue
            text = path.read_text(encoding="utf-8")
            for snippet in forbidden_snippets:
                assert snippet not in text, f"{path} still references canonical data root via {snippet!r}"


def test_analysis_template_uses_figure_owned_outputs() -> None:
    text = (REPO_ROOT / "analyses" / "_template" / "analysis.yaml").read_text(encoding="utf-8")
    assert "figures: figures/<figure_id>/output" in text
    assert "runs: figures/<figure_id>/output/runs" in text


def test_figiel_analysis_is_migrated_to_figure_owned_layout() -> None:
    root = ANALYSIS_ROOTS["2025_figiel"]
    text = (root / "analysis.yaml").read_text(encoding="utf-8")
    assert "figures: figures/<figure_id>/output" in text
    assert "runs: figures/<figure_id>/output/runs" in text
    assert not (root / "data").exists()
    assert (root / "figures").is_dir()
    for figure_id in ("figure_4", "figure_5", "figure_6", "figure_7", "figure_8", "figure_9"):
        figure_root = root / "figures" / figure_id
        assert (figure_root / "input").is_dir(), figure_id
        assert (figure_root / "output").is_dir(), figure_id
        assert (figure_root / "scripts").is_dir(), figure_id
