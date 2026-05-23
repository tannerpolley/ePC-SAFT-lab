from __future__ import annotations

import ast
import csv
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ALLOWED_ROOT_PYTHON_ENTRY_FILES = {"__init__.py", "__init__.pyi", "__main__.py", "_core.pyi", "_types.py"}
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
    "2012_held": REPO_ROOT / "analyses" / "paper_validation" / "2012_held",
    "2014_held": REPO_ROOT / "analyses" / "paper_validation" / "2014_held",
    "2015_baygi": REPO_ROOT / "analyses" / "paper_validation" / "2015_baygi",
    "2019_bulow": REPO_ROOT / "analyses" / "paper_validation" / "2019_bulow",
    "2020_bulow": REPO_ROOT / "analyses" / "paper_validation" / "2020_bulow",
    "2025_figiel": REPO_ROOT / "analyses" / "paper_validation" / "2025_figiel",
    "2026_khudaida": REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida",
    "dielectric_fits": REPO_ROOT / "analyses" / "data_validation" / "dielectric_fits",
    "miac_fits": REPO_ROOT / "analyses" / "data_validation" / "miac_fits",
    "osmotic_validation": REPO_ROOT / "analyses" / "data_validation" / "osmotic_validation",
    "package_plot_smokes": REPO_ROOT / "analyses" / "package_validation" / "package_plot_smokes",
}
PAPER_VALIDATION_PARAMETER_SNAPSHOTS = {
    "analyses/paper_validation/2001_gross": "2001_Gross",
    "analyses/paper_validation/2002_gross": "2002_Gross",
    "analyses/paper_validation/2024_hubach": "2024_Hubach",
    "analyses/paper_validation/2024_yu": "2024_Yu",
    "analyses/paper_validation/2026_khudaida": "2026_Khudaida",
    "analyses/paper_validation/2026_rezaee": "2026_Rezaee",
    "analyses/paper_validation/2005_cameretti": "2005_Cameretti",
    "analyses/paper_validation/2008_held": "2008_Held",
    "analyses/paper_validation/2012_held": "2012_Held",
    "analyses/paper_validation/2014_held": "2014_Held",
    "analyses/paper_validation/2015_baygi": "2015_Baygi",
    "analyses/paper_validation/2019_bulow": "2019_Bulow",
    "analyses/paper_validation/2020_bulow": "2020_Bulow",
    "analyses/paper_validation/2021_bulow": "2021_Bulow",
    "analyses/paper_validation/2022_ascani": "2022_Ascani",
    "analyses/paper_validation/2023_ascani": "2023_Ascani",
    "analyses/paper_validation/2025_figiel": "2025_Figiel",
}
MIGRATED_ANALYSIS_IDS = set(ANALYSIS_ROOTS) - {"2025_figiel"}
CATEGORY_ROOTS = {
    REPO_ROOT / "analyses" / "paper_validation",
    REPO_ROOT / "analyses" / "data_validation",
    REPO_ROOT / "analyses" / "package_validation",
}
PAPER_VALIDATION_DOC_ROOTS = {
    "analyses/paper_validation/2015_baygi",
    "analyses/paper_validation/2001_gross",
    "analyses/paper_validation/2002_gross",
    "analyses/paper_validation/2005_cameretti",
    "analyses/paper_validation/2008_held",
    "analyses/paper_validation/2012_held",
    "analyses/paper_validation/2014_held",
    "analyses/paper_validation/2019_bulow",
    "analyses/paper_validation/2020_bulow",
    "analyses/paper_validation/2021_bulow",
    "analyses/paper_validation/2025_figiel",
    "analyses/paper_validation/2022_ascani",
    "analyses/paper_validation/2023_ascani",
    "analyses/paper_validation/2026_khudaida",
    "analyses/paper_validation/2024_hubach",
    "analyses/paper_validation/2024_yu",
    "analyses/paper_validation/2026_rezaee",
}
PAPER_VALIDATION_DOC_SUBDIRS = {"md", "pdf"}
PAPER_VALIDATION_ROOT_DIRS = {"docs", "figures", "parameters", "scripts", "shared", "tables"}
PAPER_VALIDATION_FIGURE_SUBDIRS = {"source", "scripts", "results"}
PAPER_VALIDATION_PURE_COLUMNS = [
    "component",
    "m",
    "s",
    "e",
    "e_assoc",
    "vol_a",
    "assoc_scheme",
    "z",
    "dielc",
    "d_born",
    "f_solv",
    "MW",
    "source",
]
PAPER_VALIDATION_BINARY_FILES = {"k_ij.csv", "l_ij.csv", "k_hb_ij.csv"}
PAPER_VALIDATION_PARAMETER_NUMERIC_COLUMNS = {
    "m",
    "e",
    "e_assoc",
    "vol_a",
    "z",
    "d_born",
    "f_solv",
    "MW",
}
PAPER_VALIDATION_PARAMETER_REQUIRED_VALUE_COLUMNS = PAPER_VALIDATION_PARAMETER_NUMERIC_COLUMNS | {"s", "dielc"}
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


def _equilibrium_activation_rows() -> list[dict[str, object]]:
    mirror = REPO_ROOT / "src" / "epcsaft" / "runtime" / "equilibrium_activation.py"
    tree = ast.parse(mirror.read_text(encoding="utf-8"), filename=mirror.relative_to(REPO_ROOT).as_posix())
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "EQUILIBRIUM_ACTIVATION_MATRIX" for target in node.targets):
            rows = ast.literal_eval(node.value)
            assert isinstance(rows, list)
            return rows
    raise AssertionError("EQUILIBRIUM_ACTIVATION_MATRIX was not found in the generated runtime mirror.")


def _workflow_route_specs() -> dict[str, dict[str, str]]:
    workflow_path = REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "workflows.py"
    tree = ast.parse(workflow_path.read_text(encoding="utf-8"), filename=workflow_path.relative_to(REPO_ROOT).as_posix())
    specs: dict[str, dict[str, str]] = {}
    spec_tables = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue
        if not isinstance(value, ast.Dict):
            continue
        if not any(isinstance(target, ast.Name) and target.id.endswith("ROUTE_SPECS") for target in targets):
            continue
        spec_tables += 1
        for route_node, spec_node in zip(value.keys, value.values):
            route = ast.literal_eval(route_node)
            assert isinstance(route, str)
            assert isinstance(spec_node, ast.Call)
            spec: dict[str, str] = {}
            for keyword in spec_node.keywords:
                if keyword.arg is None:
                    continue
                if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    spec[keyword.arg] = keyword.value.value
            specs[route] = spec

    assert spec_tables == 1
    assert specs
    return specs


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


def test_deleted_equilibrium_route_sources_and_bindings_are_absent() -> None:
    deleted_sources = (
        "src/epcsaft/native/equilibrium/facade.h",
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


def test_equilibrium_activation_families_cannot_create_ad_hoc_native_route_files() -> None:
    native_equilibrium_root = REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium"
    shared_owner = native_equilibrium_root / "routes" / "derived" / "bubble_dew.cpp"
    route_file_allowlist = {
        "src/epcsaft/native/equilibrium/core/activation_matrix.h",
        "src/epcsaft/native/equilibrium/core/selector_core.cpp",
        "src/epcsaft/native/equilibrium/core/selector_core.h",
        "src/epcsaft/native/equilibrium/core/two_phase_eos_route.h",
        "src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp",
    }

    assert shared_owner.is_file()

    activation_rows = _equilibrium_activation_rows()
    activation_key_tokens = {str(row["key"]).lower() for row in activation_rows}
    route_specific_filename_tokens = (
        *sorted(activation_key_tokens),
        "bubble",
        "dew",
        "flash",
        "lle",
        "speciation",
        "stability",
        "vle",
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "tp_flash",
        "hydrocarbon",
    )
    route_file_offenders: list[str] = []
    for path in sorted(native_equilibrium_root.rglob("*")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in route_file_allowlist:
            continue
        name = path.name.lower()
        if path.is_dir():
            if any(token in name for token in route_specific_filename_tokens):
                route_file_offenders.append(rel)
            continue
        if not path.is_file() or path.suffix.lower() not in {".cpp", ".h", ".hpp"}:
            continue
        if any(token in name for token in route_specific_filename_tokens):
            route_file_offenders.append(rel)
    assert route_file_offenders == []


def test_equilibrium_activation_production_rows_must_enter_through_selector_route_specs() -> None:
    rows = _equilibrium_activation_rows()
    activation_keys = {str(row["key"]) for row in rows}
    production_keys = {str(row["key"]) for row in rows if row["production_exposed"] is True}
    declared_not_exposed_keys = {str(row["key"]) for row in rows if row["production_exposed"] is False}
    route_specs = _workflow_route_specs()
    selector_families = {spec["selector_family"] for spec in route_specs.values()}
    selector_routes = {spec["selector_route"] for spec in route_specs.values()}

    assert production_keys
    assert selector_families == production_keys
    assert selector_families <= activation_keys
    assert selector_routes.isdisjoint(declared_not_exposed_keys)
    for row in rows:
        if row["production_exposed"] is not True:
            continue
        assert row["exposure_status"] == "production_exposed", row["key"]
        assert row["postsolve_certification"] == "on", row["key"]
        assert row["derivative_requirement"] == "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes", row["key"]
        assert row["residual_families"], row["key"]
        assert row["constraint_families"], row["key"]
        assert row["proof_routes"], row["key"]
        assert row["variable_model"], row["key"]
        assert row["density_backend"], row["key"]

    selector_core = (
        REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium" / "core" / "selector_core.cpp"
    ).read_text(encoding="utf-8", errors="ignore")
    missing_selector_admission = sorted(key for key in production_keys if key not in selector_core)
    assert missing_selector_admission == []


def test_activation_matrix_families_do_not_gain_direct_pybind_route_entrypoints() -> None:
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    binding_source_paths = [
        path
        for path in sorted((REPO_ROOT / "src" / "epcsaft" / "native" / "bindings").rglob("*"))
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp"}
    ]
    binding_source_paths.append(
        REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium" / "register_bindings.cpp"
    )

    direct_binding_tokens = {f"_native_{key}" for key in activation_keys}
    binding_offenders: list[str] = []
    for path in binding_source_paths:
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in sorted(direct_binding_tokens):
            if token in text:
                binding_offenders.append(f"{rel}: {token}")
    assert binding_offenders == []


def test_equilibrium_route_solve_and_contract_owners_stay_in_shared_core_files() -> None:
    native_equilibrium_root = REPO_ROOT / "src" / "epcsaft" / "native" / "equilibrium"
    allowed_route_owner_files = {
        "src/epcsaft/native/equilibrium/core/activated_equilibrium_nlp.cpp",
        "src/epcsaft/native/equilibrium/core/activated_equilibrium_nlp.h",
        "src/epcsaft/native/equilibrium/core/selector_core.cpp",
        "src/epcsaft/native/equilibrium/core/selector_core.h",
        "src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp",
        "src/epcsaft/native/equilibrium/core/two_phase_eos_route.h",
        "src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp",
    }
    route_api_pattern = re.compile(
        r"(?m)^\s*(?!return\b)(?:[\w:<>]+[\s*&]+)+(?<!::)"
        r"(?:solve|evaluate)_[a-z0-9_]+_(?:route|nlp_contract)\s*\("
    )

    route_api_offenders: list[str] = []
    for path in sorted(native_equilibrium_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".cpp", ".h", ".hpp"}:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in allowed_route_owner_files:
            continue
        matches = sorted(set(route_api_pattern.findall(path.read_text(encoding="utf-8", errors="ignore"))))
        if matches:
            route_api_offenders.append(f"{rel}: {', '.join(matches)}")
    assert route_api_offenders == []


def test_equilibrium_python_surface_has_one_public_solve_lane_and_no_route_helpers() -> None:
    route_specs = _workflow_route_specs()
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    legacy_route_aliases = {"bubble_p", "bubble_t", "dew_p", "dew_t", "tp_flash", "lle_flash"}
    route_specific_names = set(route_specs) | activation_keys | legacy_route_aliases
    forbidden_helper_names = route_specific_names | {f"_solve_{name}" for name in route_specific_names}
    inspected_paths = (
        REPO_ROOT / "src" / "epcsaft" / "frontend" / "equilibrium.py",
        REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "workflows.py",
        REPO_ROOT / "src" / "epcsaft" / "state" / "native_adapter.py",
    )

    offenders: list[str] = []
    for path in inspected_paths:
        rel = path.relative_to(REPO_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in forbidden_helper_names:
                offenders.append(f"{rel}:{node.lineno}: def {node.name}")

    frontend_tree = ast.parse(
        (REPO_ROOT / "src" / "epcsaft" / "frontend" / "equilibrium.py").read_text(encoding="utf-8"),
        filename="src/epcsaft/frontend/equilibrium.py",
    )
    equilibrium_class = next(
        node for node in frontend_tree.body if isinstance(node, ast.ClassDef) and node.name == "Equilibrium"
    )
    public_methods = sorted(
        node.name
        for node in equilibrium_class.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    solve_calls = [
        node
        for node in ast.walk(equilibrium_class)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id.startswith("_solve_selector")
    ]
    workflow_tree = ast.parse(
        (REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "workflows.py").read_text(encoding="utf-8"),
        filename="src/epcsaft/equilibrium/workflows.py",
    )
    workflow_helpers = [
        node.name
        for node in workflow_tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_solve_selector")
    ]

    assert offenders == []
    assert public_methods == ["problem", "solve", "structure"]
    assert len(solve_calls) == 1
    assert len(workflow_helpers) == 1


def test_regression_package_keeps_downstream_application_benchmarks_out_of_core() -> None:
    inspected_paths = (
        REPO_ROOT / "src" / "epcsaft" / "regression" / "core.py",
        REPO_ROOT / "src" / "epcsaft" / "regression" / "native_adapter.py",
    )
    forbidden_tokens = (
        "fit_mea",
        "mea_co2_h2o",
        "MEAH+",
        "MEACOO-",
    )

    offenders: list[str] = []
    for path in inspected_paths:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT).as_posix()
        offenders.extend(f"{rel}: {token}" for token in forbidden_tokens if token in text)

    assert offenders == []


def test_state_native_adapter_does_not_own_regression_native_wrappers() -> None:
    state_path = REPO_ROOT / "src" / "epcsaft" / "state" / "native_adapter.py"
    tree = ast.parse(state_path.read_text(encoding="utf-8"), filename=state_path.relative_to(REPO_ROOT).as_posix())
    regression_wrapper_names = {
        "_evaluate_generic_native_debug",
        "_fit_generic_native_ceres",
        "_fit_pure_neutral_native_debug",
    }
    defined_names = {
        node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    assert regression_wrapper_names.isdisjoint(defined_names)


def test_equilibrium_constructor_configured_api_has_no_legacy_kwargs_or_setup_helpers() -> None:
    frontend_path = REPO_ROOT / "src" / "epcsaft" / "frontend" / "equilibrium.py"
    tree = ast.parse(frontend_path.read_text(encoding="utf-8"), filename=frontend_path.relative_to(REPO_ROOT).as_posix())
    equilibrium_class = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Equilibrium"
    )
    methods = {node.name: node for node in equilibrium_class.body if isinstance(node, ast.FunctionDef)}

    assert {"setup", "initialize"}.isdisjoint(methods)
    assert "__getattr__" not in methods
    assert {"bubble_pressure", "bubble_temperature", "dew_pressure", "dew_temperature", "flash"}.isdisjoint(methods)

    constructor = methods["__init__"]
    solve = methods["solve"]
    constructor_kwargs = [arg.arg for arg in constructor.args.kwonlyargs]
    solve_kwargs = [arg.arg for arg in solve.args.kwonlyargs]

    assert constructor.args.vararg is None
    assert constructor.args.kwarg is None
    assert constructor_kwargs == ["route", "T", "P", "x", "y", "z"]
    assert solve.args.vararg is None
    assert solve.args.kwarg is None
    assert solve_kwargs == ["solver_options"]


def test_python_equilibrium_package_exposes_only_production_selector_solve_support() -> None:
    import epcsaft
    import epcsaft.equilibrium as equilibrium
    import epcsaft.equilibrium.workflows as workflows
    from epcsaft.state.native_adapter import ePCSAFTMixture

    route_specific_methods = set(_workflow_route_specs())
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    declared_not_exposed_keys = {
        str(row["key"]) for row in _equilibrium_activation_rows() if row["production_exposed"] is False
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
        "EquilibriumProblem",
        "EquilibriumStructure",
        "ReactiveSpeciationProblem",
        "ReactiveElectrolyteBubbleProblem",
        "ReactivePhaseEquilibriumProblem",
        "TPFlash",
        "LLEProblem",
        "ElectrolyteLLEProblem",
        "ElectrolyteBubblePoint",
        "StabilityAnalysis",
        *activation_keys,
        *declared_not_exposed_keys,
    }
    leaked = sorted(name for name in forbidden_exports if hasattr(equilibrium, name))

    assert leaked == []

    workflow_route_helpers = {
        *route_specific_methods,
        "solve_selector_vle",
        "solve_selector_equilibrium",
        *(f"solve_{key}" for key in activation_keys),
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


def test_public_equilibrium_workflows_dispatch_only_through_selector_binding() -> None:
    workflows = (REPO_ROOT / "src" / "epcsaft" / "equilibrium" / "workflows.py").read_text(
        encoding="utf-8"
    )
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    selector_routes = {spec["selector_route"] for spec in _workflow_route_specs().values()}
    required_selector_calls = workflows.count("_native_equilibrium_selector_route_result")
    forbidden_direct_route_bindings = (
        "_native_neutral_bubble_p_eos_route_result",
        "_native_neutral_bubble_t_eos_route_result",
        "_native_neutral_dew_p_eos_route_result",
        "_native_neutral_dew_t_eos_route_result",
        "_native_neutral_tp_flash_eos_route_result",
        *(f"_native_{key}" for key in activation_keys),
        *(f"_native_{route}_route_result" for route in selector_routes),
    )

    assert required_selector_calls == 1
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
            if name == "EquilibriumSolverOptions":
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


def test_paper_validation_parameter_inputs_are_local_snapshots() -> None:
    reference_root = REPO_ROOT / "data" / "reference" / "epcsaft_parameters"

    for analysis_rel, dataset in sorted(PAPER_VALIDATION_PARAMETER_SNAPSHOTS.items()):
        parameter_root = REPO_ROOT / analysis_rel / "parameters"
        assert parameter_root.is_dir(), analysis_rel
        assert not (parameter_root / dataset).exists(), f"{analysis_rel}: nested dataset folder is not allowed"
        assert (parameter_root / "mixed").is_dir(), analysis_rel
        assert (parameter_root / "pure").is_dir(), analysis_rel
        assert (parameter_root / "user_options.json").is_file(), analysis_rel

        source_dataset = reference_root / dataset
        assert source_dataset.is_dir(), dataset

        source_files = {
            path.relative_to(source_dataset).as_posix(): path
            for path in source_dataset.rglob("*")
            if path.is_file()
        }
        input_files = {
            path.relative_to(parameter_root).as_posix(): path
            for path in parameter_root.rglob("*")
            if path.is_file()
        }
        assert set(input_files) == set(source_files), f"{analysis_rel}: {dataset}"

        for relpath, source_path in source_files.items():
            assert input_files[relpath].read_bytes() == source_path.read_bytes(), f"{analysis_rel}: {relpath}"


def test_paper_validation_parameter_bundles_are_complete_and_uniform() -> None:
    for analysis_rel in sorted(PAPER_VALIDATION_DOC_ROOTS):
        parameter_root = REPO_ROOT / analysis_rel / "parameters"
        assert parameter_root.is_dir(), analysis_rel
        assert not list(parameter_root.rglob("_placeholder.md")), analysis_rel

        pure_files = sorted((parameter_root / "pure").glob("*.csv"))
        assert pure_files, analysis_rel
        for pure_file in pure_files:
            with pure_file.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                assert reader.fieldnames == PAPER_VALIDATION_PURE_COLUMNS, pure_file
            assert rows, pure_file
            for row in rows:
                assert row["component"].strip(), pure_file
                assert row["source"].strip(), f"{pure_file}: {row['component']}"
                assert "=" not in ",".join(row[column] for column in PAPER_VALIDATION_PARAMETER_REQUIRED_VALUE_COLUMNS), row
                for column in PAPER_VALIDATION_PARAMETER_REQUIRED_VALUE_COLUMNS:
                    assert row[column].strip() != "", f"{pure_file}: {row['component']} {column}"

        binary_root = parameter_root / "mixed" / "binary_interaction"
        assert binary_root.is_dir(), analysis_rel
        assert {path.name for path in binary_root.glob("*.csv")} >= PAPER_VALIDATION_BINARY_FILES | {
            "source_manifest.csv"
        }
        for filename in sorted(PAPER_VALIDATION_BINARY_FILES):
            matrix_file = binary_root / filename
            with matrix_file.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                header = next(reader)
                rows = list(reader)
            assert header[0] == "component", matrix_file
            assert rows, matrix_file
            assert len(rows) == len(header) - 1, matrix_file
            assert [row[0] for row in rows] == header[1:], matrix_file
            for row in rows:
                assert len(row) == len(header), matrix_file
                assert all(cell.strip() != "" for cell in row[1:]), matrix_file


def test_paper_validation_temperature_dependent_parameters_are_preserved() -> None:
    from epcsaft.model.datasets import get_prop_dict

    temperature = 298.15
    ascani = get_prop_dict(
        REPO_ROOT / "analyses" / "paper_validation" / "2023_ascani" / "parameters",
        ["H2O", "1-Pentanol"],
        [0.5, 0.5],
        temperature,
    )
    expected_sigma = 2.7927 + 10.11 * math.exp(-0.01775 * temperature) - 1.417 * math.exp(
        -0.01146 * temperature
    )
    assert abs(float(ascani["s"][0]) - expected_sigma) < 1.0e-12
    assert abs(float(ascani["k_ij"][0, 1]) - (0.00016 * temperature - 0.0461)) < 1.0e-12

    held = get_prop_dict(
        REPO_ROOT / "analyses" / "paper_validation" / "2012_held" / "parameters",
        ["Methanol"],
        [1.0],
        temperature,
    )
    assert abs(float(held["dielc"][0]) - (-53.398 * math.log(temperature) + 336.170)) < 1.0e-12


def test_analysis_category_roots_exist() -> None:
    for root in sorted(CATEGORY_ROOTS):
        assert root.is_dir(), root


def test_paper_validation_uses_flat_paper_roots() -> None:
    paper_root = REPO_ROOT / "analyses" / "paper_validation"
    actual = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in paper_root.iterdir()
        if path.is_dir()
    }
    assert actual == PAPER_VALIDATION_DOC_ROOTS
    assert not (paper_root / "native").exists()
    assert not (paper_root / "application").exists()
    for old_domain in ("co2_solubility", "eos", "equilibrium", "extraction"):
        assert not (paper_root / old_domain).exists()


def test_paper_validation_docs_are_local_source_snapshots() -> None:
    for analysis_rel in sorted(PAPER_VALIDATION_DOC_ROOTS):
        analysis_root = REPO_ROOT / analysis_rel
        docs_root = analysis_root / "docs"
        shared_source = analysis_root / "shared" / "source"
        tables_root = analysis_root / "tables"
        assert docs_root.is_dir(), analysis_rel
        assert {path.name for path in analysis_root.iterdir() if path.is_dir()} == PAPER_VALIDATION_ROOT_DIRS
        assert {path.name for path in docs_root.iterdir() if path.is_dir()} == PAPER_VALIDATION_DOC_SUBDIRS
        assert (docs_root / "source_manifest.csv").is_file(), analysis_rel
        assert not (docs_root / "figures").exists(), analysis_rel
        assert not (docs_root / "tables").exists(), analysis_rel
        assert (shared_source / "figures_manifest.csv").is_file(), analysis_rel
        assert not (shared_source / "tables").exists(), analysis_rel
        assert (tables_root / "tables_manifest.csv").is_file(), analysis_rel
        assert list((docs_root / "md").glob("*.md")), analysis_rel
        assert any(path.is_file() for path in (docs_root / "pdf").iterdir()), analysis_rel
        assert any(path.is_file() for path in shared_source.iterdir()), analysis_rel


def test_paper_validation_tables_use_table_subfolders() -> None:
    for analysis_rel in sorted(PAPER_VALIDATION_DOC_ROOTS):
        tables_root = REPO_ROOT / analysis_rel / "tables"
        assert tables_root.is_dir(), analysis_rel
        assert (tables_root / "tables_manifest.csv").is_file(), analysis_rel
        assert not (REPO_ROOT / analysis_rel / "shared" / "source" / "tables").exists(), analysis_rel

        table_roots = sorted(path for path in tables_root.iterdir() if path.is_dir())
        if not table_roots:
            assert (tables_root / "_placeholder.md").is_file(), analysis_rel
            continue
        assert not (tables_root / "_placeholder.md").exists(), analysis_rel
        for table_root in table_roots:
            assert re.fullmatch(r"table_\d{3}", table_root.name), table_root
            assert any(table_root.glob("*.md")), table_root
            assert any(table_root.glob("*.csv")), table_root


def test_paper_validation_figures_use_source_scripts_results_layout() -> None:
    for analysis_rel in sorted(PAPER_VALIDATION_DOC_ROOTS):
        figures_root = REPO_ROOT / analysis_rel / "figures"
        assert figures_root.is_dir(), analysis_rel
        figure_roots = sorted(path for path in figures_root.iterdir() if path.is_dir())
        if not figure_roots:
            assert (figures_root / "_placeholder.md").is_file(), analysis_rel
            continue
        assert not any(path.is_file() for path in figures_root.iterdir()), analysis_rel
        for figure_root in figure_roots:
            assert {path.name for path in figure_root.iterdir() if path.is_dir()} == PAPER_VALIDATION_FIGURE_SUBDIRS
            assert not any(path.is_file() for path in figure_root.iterdir()), figure_root
            for subdir in PAPER_VALIDATION_FIGURE_SUBDIRS:
                assert any((figure_root / subdir).iterdir()), figure_root / subdir
            for source_png in (figure_root / "source").glob("paper_source_*.png"):
                assert (source_png.with_suffix(source_png.suffix + ".sha256")).is_file(), source_png
            assert list((figure_root / "source").glob("paper_source_*.jpg")) == [], figure_root


def test_paper_validation_has_no_root_data_results_or_diagnostics() -> None:
    for analysis_rel in sorted(PAPER_VALIDATION_DOC_ROOTS):
        analysis_root = REPO_ROOT / analysis_rel
        assert not (analysis_root / "data").exists(), analysis_rel
        assert not (analysis_root / "results").exists(), analysis_rel
        assert not (analysis_root / "diagnostics").exists(), analysis_rel


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


def test_native_equilibrium_tests_stay_in_named_subfolders() -> None:
    root = REPO_ROOT / "tests" / "native" / "equilibrium"
    allowed_subdirs = {"blocks", "diagnostics", "results"}
    direct_python_files = sorted(
        path.relative_to(REPO_ROOT).as_posix() for path in root.glob("*.py")
    )
    actual_subdirs = sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )

    assert direct_python_files == []
    assert actual_subdirs == sorted(allowed_subdirs)


def test_test_tree_uses_namespace_packages_without_init_markers() -> None:
    assert list((REPO_ROOT / "tests").rglob("__init__.py")) == []


def test_replaced_flat_test_modules_are_absent_from_the_working_tree() -> None:
    for relpath in sorted(REPLACED_FLAT_TEST_FILES):
        assert not (REPO_ROOT / relpath).exists(), relpath


def test_generated_output_roots_are_not_tracked_in_analyses() -> None:
    tracked = _tracked_files("analyses")
    stale: list[str] = []
    docs_figures = "/docs/" + "figures/"
    docs_tables = "/docs/" + "tables/"
    shared_source_tables = "/shared/source/" + "tables/"
    for path in tracked:
        normalized = path.replace("\\", "/")
        if (
            "/out/" in normalized
            or "/results/runs/" in normalized
            or "/results/final/" in normalized
            or ("/figures/" in normalized and "/output/runs/" in normalized)
        ):
            stale.append(path)
            continue
        if normalized.startswith("analyses/paper_validation/") and (
            docs_figures in normalized
            or docs_tables in normalized
            or shared_source_tables in normalized
            or ("/figures/" in normalized and "/input/" in normalized)
            or ("/figures/" in normalized and "/output/" in normalized)
            or re.search(r"^analyses/paper_validation/[^/]+/(data|results|diagnostics)/", normalized)
        ):
            stale.append(path)
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
        if path.as_posix().startswith((REPO_ROOT / "analyses" / "paper_validation").as_posix()):
            assert "figures: figures/<figure_id>/results" in text, path
            assert "runs: figures/<figure_id>/results/runs" in text, path
        else:
            assert "figures: figures/<figure_id>/" + "output" in text, path
            assert "runs: figures/<figure_id>/" + "output/runs" in text, path


def test_migrated_analyses_use_complete_figure_owned_roots() -> None:
    for analysis_id in sorted(MIGRATED_ANALYSIS_IDS):
        figures_root = ANALYSIS_ROOTS[analysis_id] / "figures"
        assert figures_root.is_dir(), analysis_id
        figure_roots = sorted(path for path in figures_root.iterdir() if path.is_dir())
        assert figure_roots, analysis_id
        for figure_root in figure_roots:
            assert (figure_root / "scripts").is_dir(), figure_root
            if figure_root.as_posix().startswith((REPO_ROOT / "analyses" / "paper_validation").as_posix()):
                optional_roots = (figure_root / "source", figure_root / "results")
            else:
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
    assert "figures: figures/<figure_id>/" + "output" in text
    assert "runs: figures/<figure_id>/" + "output/runs" in text


def test_figiel_analysis_is_migrated_to_figure_owned_layout() -> None:
    root = ANALYSIS_ROOTS["2025_figiel"]
    text = (root / "analysis.yaml").read_text(encoding="utf-8")
    assert "figures: figures/<figure_id>/results" in text
    assert "runs: figures/<figure_id>/results/runs" in text
    assert not (root / "data").exists()
    assert (root / "figures").is_dir()
    for figure_id in ("figure_4", "figure_5", "figure_6", "figure_7", "figure_8", "figure_9"):
        figure_root = root / "figures" / figure_id
        assert (figure_root / "source").is_dir(), figure_id
        assert (figure_root / "results").is_dir(), figure_id
        assert (figure_root / "scripts").is_dir(), figure_id
