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

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = REPO_ROOT
PROVIDER_PACKAGE_DIR = REPO_ROOT / "packages" / "epcsaft"
PROVIDER_PACKAGE_ROOT = PROVIDER_PACKAGE_DIR / "src" / "epcsaft"
PROVIDER_TEST_ROOT = PROVIDER_PACKAGE_DIR / "tests"
PROVIDER_NATIVE_ROOT = PROVIDER_PACKAGE_ROOT / "native"
EQUILIBRIUM_PACKAGE_DIR = REPO_ROOT / "packages" / "epcsaft-equilibrium"
EQUILIBRIUM_PACKAGE_ROOT = EQUILIBRIUM_PACKAGE_DIR / "src" / "epcsaft_equilibrium"
EQUILIBRIUM_TEST_ROOT = EQUILIBRIUM_PACKAGE_DIR / "tests"
EQUILIBRIUM_NATIVE_ROOT = EQUILIBRIUM_PACKAGE_DIR / "src" / "epcsaft_equilibrium" / "native" / "equilibrium"
REGRESSION_PACKAGE_DIR = REPO_ROOT / "packages" / "epcsaft-regression"
REGRESSION_PACKAGE_ROOT = REGRESSION_PACKAGE_DIR / "src" / "epcsaft_regression"
REGRESSION_TEST_ROOT = REGRESSION_PACKAGE_DIR / "tests"
ALLOWED_PROVIDER_PYTHON_ENTRY_FILES = {"__init__.py", "__init__.pyi", "__main__.py", "_core.pyi", "_types.py"}
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
    "epcsaft_equilibrium",
    "epcsaft_equilibrium.core",
    "epcsaft_equilibrium.workflows",
    "epcsaft_regression",
    "epcsaft.frontend",
    "epcsaft.frontend.mixture",
    "epcsaft.frontend.state",
    "epcsaft.model.options",
    "epcsaft.model.parameters",
    "epcsaft.model.templates",
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
    "explicit_association_toybox": REPO_ROOT / "analyses" / "package_validation" / "explicit_association_toybox",
    "package_plot_smokes": REPO_ROOT / "analyses" / "package_validation" / "package_plot_smokes",
    "standalone_ce": REPO_ROOT / "analyses" / "package_validation" / "standalone_ce",
}
STANDALONE_CE_NONIDEAL_FIGURE_ROOT = (
    ANALYSIS_ROOTS["standalone_ce"] / "figures" / "mea_reactive_speciation_oracle_comparison"
)
STANDALONE_CE_NONIDEAL_MIGRATION_CONTRACT = (
    STANDALONE_CE_NONIDEAL_FIGURE_ROOT / "source" / "migration_contract.json"
)
MIGRATED_ANALYSIS_IDS = set(ANALYSIS_ROOTS) - {"2025_figiel"}
CATEGORY_ROOTS = {
    REPO_ROOT / "analyses" / "paper_validation",
    REPO_ROOT / "analyses" / "data_validation",
    REPO_ROOT / "analyses" / "package_validation",
    REPO_ROOT / "analyses" / "reference_oracles",
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
}
PAPER_SOURCE_EVIDENCE_ROOTS = {"analyses/paper_validation/2026_rezaee"}
PAPER_VALIDATION_INFRA_ROOTS = {
    "analyses/paper_validation/scripts",
    "analyses/paper_validation/tests",
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
    PROVIDER_TEST_ROOT,
    PROVIDER_TEST_ROOT / "api",
    PROVIDER_TEST_ROOT / "api" / "frontend",
    PROVIDER_TEST_ROOT / "api" / "package",
    PROVIDER_TEST_ROOT / "native",
    PROVIDER_TEST_ROOT / "native" / "contracts",
    PROVIDER_TEST_ROOT / "native" / "state",
    PROVIDER_TEST_ROOT / "support",
    REPO_ROOT / "tests" / "native" / "contracts",
    EQUILIBRIUM_TEST_ROOT,
    EQUILIBRIUM_TEST_ROOT / "api",
    EQUILIBRIUM_TEST_ROOT / "contracts",
    EQUILIBRIUM_TEST_ROOT / "equilibrium_support",
    EQUILIBRIUM_TEST_ROOT / "native",
    EQUILIBRIUM_TEST_ROOT / "native" / "blocks",
    EQUILIBRIUM_TEST_ROOT / "native" / "diagnostics",
    EQUILIBRIUM_TEST_ROOT / "native" / "results",
    REGRESSION_TEST_ROOT,
    REGRESSION_TEST_ROOT / "api",
    REGRESSION_TEST_ROOT / "contracts",
    REGRESSION_TEST_ROOT / "native",
    REGRESSION_TEST_ROOT / "regression_support",
    REPO_ROOT / "tests" / "workflows" / "build",
    REPO_ROOT / "tests" / "workflows" / "repo",
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
    "tests/api/frontend/test_equilibrium.py",
    "tests/api/frontend",
    "tests/api/package",
    "tests/equilibrium",
    "tests/regression",
    "tests/helpers",
    "tests/native/ceres",
    "tests/native/cppad",
    "tests/native/runtime",
    "tests/native/test_runtime_contracts.py",
    "tests/native/test_chemical_equilibrium_native.py",
    "tests/native/contracts/test_equilibrium_activation_capabilities.py",
    "tests/native/state",
    "tests/support",
    "tests/workflows/benchmarks",
}
MILESTONE_MIRROR_FOLDERS = {
    "M0-governance": "M0 - Governance",
    "M1-packages": "M1 - Packages",
    "M2-python-api": "M2 - Python API",
    "M3-eos": "M3 - EOS",
    "M4-equilibrium": "M4 - Equilibrium",
    "M5-regression": "M5 - Regression",
    "M6-validation": "M6 - Validation",
    "M7-release": "M7 - Release",
    "M8-python-toybox": "M8 - Python Toybox",
}
MILESTONE_FRONT_MATTER_FIELDS = {
    "issue",
    "title",
    "url",
    "state",
    "milestone",
    "project",
    "package",
    "capability",
    "backend",
    "readiness",
    "release_target",
    "source_spec",
    "source_plan",
    "afk_hitl",
    "branch",
    "last_synced",
}
SUPERPOWERS_TEMPLATE_FILES = {
    "_templates/spec.md",
    "_templates/plan.md",
    "_templates/issue-mirror.md",
}
SUPERPOWERS_SPEC_FILES = {
    "PROJECT_CONTEXT.md",
    "specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md",
    "specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md",
    "specs/2026-05-27-m4-equilibrium-gfpe-package-cleanup-plan.md",
    "specs/2026-05-29-m5-regression-regression-production-backlog.md",
    "specs/2026-05-29-m6-validation-validation-benchmark-backlog.md",
    "specs/2026-05-29-m7-release-release-downstream-backlog.md",
    "specs/2026-06-01-m4-equilibrium-move-equilibrium-objective-assembly-to-extension.md",
}
SUPERPOWERS_SPEC_FILENAME_PATTERN = re.compile(r"^20\d\d-\d\d-\d\d-m[0-8]-[a-z0-9-]+\.md$")
SUPERPOWERS_ISSUE_FILENAME_PATTERN = re.compile(r"^20\d\d-\d\d-\d\d-m[0-8]-[a-z0-9-]+-issue-\d{4}-[a-z0-9-]+\.md$")
SUPERPOWERS_PLAN_FILENAME_PATTERN = re.compile(
    r"^20\d\d-\d\d-\d\d-m[0-8]-[a-z0-9-]+-(?:issue-\d{4}-)?[a-z0-9-]+-plan\.md$"
)
DATA_REFERENCE_FORBIDDEN_PATH_PATTERN = re.compile(
    r"(^|[/_.-])("
    r"19\d\d|20\d\d|nist|held|gross|matsuda|pereira|hubach|khudaida|"
    r"esteso|hernandez|susial|jced|ascani|digitized|paper_validation"
    r")([/_.-]|$)",
    re.IGNORECASE,
)
SUPERPOWERS_REGISTRY_FILES = {
    "milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md",
    "milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml",
    "milestones/M6-validation/registries/equilibrium-evidence-registry.yaml",
}
ISSUE_TYPE_FORMS = {
    "bug.yml": "bug",
    "feature.yml": "feature",
    "task.yml": "task",
    "downstream_dependency_bug.yml": "bug",
    "upstream_package_request.yml": "feature",
    "gate_issue.yml": "task",
    "micro_issue.yml": "task",
    "tracking_issue.yml": "task",
}
PROJECT_ROADMAP_REQUIRED_FIELDS = {
    "target_repo",
    "target_repo_root",
    "source_docs",
    "full_roadmap",
    "milestone_policy",
    "project_policy",
    "issue_types",
    "labels",
    "issue_forms",
    "local_files",
    "apply_policy",
    "projects_required_by_repo_config",
}
AGENTS_REQUIRED_DOC_LINKS = {
    "docs/superpowers/PROJECT_CONTEXT.md",
    "docs/agents/new-agent-start-here.md",
    "docs/agents/agent-happy-path.md",
    "docs/pages/development_workflows.rst",
    "docs/protocols/build_package_dependency_protocol.rst",
    "CMAKE.md",
    "docs/agents/issue-tracker.md",
    "docs/pages/project_structure.rst",
}
AGENTS_BANNED_PHRASES = {
    "Machine-Local",
    "Do Not Commit",
    "Best new-agent workflow",
    "Git Sandbox Rules",
    "Sandbox Notes",
    "Preferred native build",
    "Preferred high-level validation",
    "Package boundary:",
    "Repo Owner Agents",
    "Routing Playbooks",
}
EXPECTED_NESTED_AGENT_FILES = {
    "packages/epcsaft/AGENTS.md",
    "packages/epcsaft-equilibrium/AGENTS.md",
    "packages/epcsaft-regression/AGENTS.md",
    "analyses/AGENTS.md",
    "analyses/paper_validation/AGENTS.md",
}
EXPECTED_NESTED_AGENT_TOKENS = {
    "packages/epcsaft/AGENTS.md": (
        "core `epcsaft` provider package",
        "Do not add equilibrium route assembly",
        "Provider public derivatives must remain CppAD-backed",
        "provider SDK",
    ),
    "packages/epcsaft-equilibrium/AGENTS.md": (
        "`epcsaft-equilibrium`",
        "Ipopt NLPs",
        "pressure-transformed objective assembly",
        "Do not expose declared-not-exposed route families",
    ),
    "packages/epcsaft-regression/AGENTS.md": (
        "`epcsaft-regression`",
        "Ceres residual blocks",
        "Regression claims require native optimizer evidence",
    ),
    "analyses/AGENTS.md": (
        "source-controlled scientific analyses",
        "Separate data generation from rendering",
        "Do not place analysis scripts in root `scripts/`",
    ),
    "analyses/paper_validation/AGENTS.md": (
        "Paper-validation analyses",
        "figures/figure_NN/source/",
        "parameters/mixed/",
        "Do not add nested dataset-name folders",
    ),
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
    pythonpath_entries = [
        str(PROVIDER_PACKAGE_DIR / "src"),
        str(EQUILIBRIUM_PACKAGE_DIR / "src"),
        str(REGRESSION_PACKAGE_DIR / "src"),
    ]
    env["PYTHONPATH"] = (
        os.pathsep.join([*pythonpath_entries, env["PYTHONPATH"]])
        if env.get("PYTHONPATH")
        else os.pathsep.join(pythonpath_entries)
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return set(json.loads(result.stdout))


def _workspace_rel(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def _tracked_files(*paths: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _markdown_front_matter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{_workspace_rel(path)} must start with front matter"
    _, raw_front_matter, _ = text.split("---", 2)
    fields: dict[str, object] = {}
    for line in raw_front_matter.splitlines():
        if not line.strip():
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value == "null":
            parsed: object = None
        elif value.startswith('"') and value.endswith('"'):
            parsed = value[1:-1]
        else:
            parsed = int(value) if value.isdigit() else value
        fields[key.strip()] = parsed
    return fields


def _equilibrium_activation_rows() -> list[dict[str, object]]:
    mirror = EQUILIBRIUM_PACKAGE_ROOT / "equilibrium_activation.py"
    tree = ast.parse(mirror.read_text(encoding="utf-8"), filename=_workspace_rel(mirror))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "EQUILIBRIUM_ACTIVATION_MATRIX" for target in node.targets
        ):
            rows = ast.literal_eval(node.value)
            assert isinstance(rows, list)
            return rows
    raise AssertionError("EQUILIBRIUM_ACTIVATION_MATRIX was not found in the generated runtime mirror.")


def _workflow_route_specs() -> dict[str, dict[str, str]]:
    workflow_path = EQUILIBRIUM_PACKAGE_ROOT / "core" / "native_requests.py"
    tree = ast.parse(workflow_path.read_text(encoding="utf-8"), filename=_workspace_rel(workflow_path))
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
    scipy_allowed_prefixes = ("analyses/package_validation/explicit_association_toybox/",)
    python_ipopt_allowed_prefixes = (
        "analyses/package_validation/explicit_association_toybox/",
        "docs/superpowers/issues/2026-06-04-m8-python-toybox-",
        "docs/superpowers/plans/2026-06-04-m8-python-toybox-",
        "docs/superpowers/specs/2026-06-04-m8-python-toybox-",
        "docs/superpowers/milestones/M8-python-toybox/",
    )
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    lock_text = (REPO_ROOT / "uv.lock").read_text(encoding="utf-8").lower()
    assert removed_dependency_name not in pyproject_text
    assert removed_python_ipopt_wrapper not in pyproject_text
    assert removed_python_ipopt_wrapper not in lock_text

    tracked = _tracked_files("src", "tests", "scripts", "analyses", "docs", "README.md", "CHANGELOG.md")
    import_offenders: list[str] = []
    import_snippets = (f"import {removed_dependency_name}", f"from {removed_dependency_name}")
    for relpath in tracked:
        normalized_relpath = relpath.replace("\\", "/")
        if normalized_relpath.startswith("docs/papers/"):
            continue
        if not relpath.endswith(".py"):
            if Path(relpath).suffix.lower() not in {".md", ".rst", ".toml", ".yaml", ".yml", ".txt", ".sh"}:
                continue
        path = REPO_ROOT / relpath
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if not normalized_relpath.startswith(python_ipopt_allowed_prefixes):
            assert removed_python_ipopt_wrapper not in text, relpath
        if not relpath.endswith(".py"):
            continue
        if any(snippet in text for snippet in import_snippets):
            if normalized_relpath.startswith(scipy_allowed_prefixes):
                continue
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
    assert not (PROVIDER_PACKAGE_ROOT / ("_optional" + "_backends")).exists()
    removed_ipopt_helper = REPO_ROOT / "scripts" / "dev" / ("setup_" + removed_python_ipopt_wrapper + "_uv.py")
    assert not removed_ipopt_helper.exists()


def test_root_package_contains_only_entry_python_files() -> None:
    root_files = {
        path.name for path in PROVIDER_PACKAGE_ROOT.iterdir() if path.is_file() and path.suffix in {".py", ".pyi"}
    }
    assert root_files == ALLOWED_PROVIDER_PYTHON_ENTRY_FILES
    assert not (REPO_ROOT / "src" / "epcsaft").exists()
    assert not (REPO_ROOT / "epcsaft").exists()
    assert not (PROVIDER_PACKAGE_ROOT / "equilibrium_core").exists()
    assert not (PROVIDER_PACKAGE_ROOT / "equilibrium").exists()
    assert (EQUILIBRIUM_PACKAGE_ROOT / "core").is_dir()


def test_active_workflows_do_not_require_retired_root_provider_paths() -> None:
    assert _tracked_files("src/epcsaft", "epcsaft", "build_backend") == []

    scanned_roots = (
        "scripts",
        ".github/workflows",
        "analyses",
        "tests/workflows",
        "run_pytest.py",
        "CMakeLists.txt",
        "pyproject.toml",
        "README.md",
        "CMAKE.md",
    )
    allowed_contexts = (
        "packages/epcsaft/src/epcsaft",
        "packages/epcsaft-equilibrium/src/epcsaft_equilibrium",
        "packages/epcsaft-regression/src/epcsaft_regression",
        "src/epcsaft_equilibrium/native/equilibrium",
        "${EPCSAFT_PROVIDER_PACKAGE_ROOT}/src/epcsaft",
        '"src/epcsaft"',
        "'src/epcsaft'",
        "src/epcsaft/**/*.cpp",
        "src/epcsaft/**/*.h",
        "src/epcsaft/*.so",
    )

    offenders: list[str] = []
    for relpath in _tracked_files(*scanned_roots):
        if relpath in {
            "tests/workflows/repo/test_project_structure.py",
            "tests/workflows/build/test_build_epcsaft.py",
        }:
            continue
        path = REPO_ROOT / relpath
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".py",
            ".sh",
            ".rst",
            ".toml",
            ".txt",
            ".yaml",
            ".yml",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "src/epcsaft" in text and not any(context in text for context in allowed_contexts):
            offenders.append(relpath)
        if "Could not locate repo root containing src/epcsaft" in text:
            offenders.append(relpath)
        if "root build_backend" in text:
            offenders.append(relpath)

    assert sorted(set(offenders)) == []


def test_active_files_do_not_import_retired_extension_paths() -> None:
    retired_patterns = (
        "from " + "epcsaft.equilibrium",
        "import " + "epcsaft.equilibrium",
        "from " + "epcsaft.regression",
        "import " + "epcsaft.regression",
        "epcsaft." + "equilibrium_core",
        "scripts.validation." + "equilibrium_core",
    )
    scanned_roots = (
        "analyses",
        "packages",
        "scripts",
        "tests",
        "docs/pages",
        "docs/contracts",
        "docs/protocols",
        "README.md",
    )
    skipped = {
        "tests/workflows/repo/test_project_structure.py",
    }

    offenders: dict[str, list[str]] = {}
    for relpath in _tracked_files(*scanned_roots):
        if relpath in skipped:
            continue
        path = REPO_ROOT / relpath
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".py",
            ".sh",
            ".rst",
            ".toml",
            ".txt",
            ".yaml",
            ".yml",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = [pattern for pattern in retired_patterns if pattern in text]
        if matches:
            offenders[relpath] = matches

    assert offenders == {}


def test_active_guidance_does_not_require_retired_sibling_extension_repos() -> None:
    retired_sibling_patterns = (
        "../epcsaft-equilibrium",
        "../epcsaft-regression",
        r"Workspaces\Engineering\epcsaft-equilibrium",
        r"Workspaces\Engineering\epcsaft-regression",
        r"Documents\Workspaces\Engineering\epcsaft-equilibrium",
        r"Documents\Workspaces\Engineering\epcsaft-regression",
        "sibling-checkout",
        "sibling local development",
        "final local sibling-repo layout",
    )
    scanned_roots = (
        "docs/pages",
        "docs/agents",
        "docs/protocols",
        "scripts",
        ".github",
        "tests/workflows",
        "README.md",
        "CMAKE.md",
        "run_pytest.py",
    )
    skipped = {
        "tests/workflows/repo/test_project_structure.py",
    }

    offenders: dict[str, list[str]] = {}
    for relpath in _tracked_files(*scanned_roots):
        if relpath in skipped:
            continue
        path = REPO_ROOT / relpath
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".py",
            ".sh",
            ".rst",
            ".toml",
            ".txt",
            ".yaml",
            ".yml",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = [pattern for pattern in retired_sibling_patterns if pattern in text]
        if matches:
            offenders[relpath] = matches

    assert offenders == {}


def test_native_cpp_sources_live_under_domain_workflow_modules() -> None:
    native_root = PROVIDER_NATIVE_ROOT
    root_native_impl_files = sorted(
        path.name for path in native_root.iterdir() if path.is_file() and path.suffix in {".cpp", ".h", ".hpp"}
    )
    assert root_native_impl_files == []
    assert not (PROVIDER_PACKAGE_ROOT / "bindings.cpp").exists()
    assert (native_root / "bindings" / "module.cpp").is_file()

    invalid_native_locations: list[str] = []
    for path in sorted(native_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".cpp", ".h", ".hpp"}:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        parts = Path(rel).parts
        if len(parts) < 7 or parts[5] not in ALLOWED_NATIVE_DOMAIN_FOLDERS:
            invalid_native_locations.append(rel)
    assert invalid_native_locations == []


def test_native_include_paths_do_not_reference_deleted_legacy_topology() -> None:
    native_root = PROVIDER_NATIVE_ROOT
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
        "packages/epcsaft/src/epcsaft/native/bindings/module.cpp",
        "packages/epcsaft/src/epcsaft/native/bindings/payload_converters.cpp",
        "packages/epcsaft/src/epcsaft/native/bindings/payload_converters.h",
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
    provider_module = (PROVIDER_NATIVE_ROOT / "bindings" / "module.cpp").read_text(encoding="utf-8")
    extension_module = (EQUILIBRIUM_NATIVE_ROOT / "module.cpp").read_text(encoding="utf-8")
    bindings_root = PROVIDER_NATIVE_ROOT / "bindings"
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

    assert "register_equilibrium_bindings(m);" not in provider_module
    assert "register_equilibrium_bindings(m);" in extension_module
    assert (EQUILIBRIUM_NATIVE_ROOT / "register_bindings.cpp").exists()
    assert not (PROVIDER_NATIVE_ROOT / "bindings" / "equilibrium_binding_types.h").exists()
    assert not (PROVIDER_NATIVE_ROOT / "bindings" / "equilibrium_bindings.cpp").exists()
    assert offenders == []


def test_deleted_equilibrium_route_sources_and_bindings_are_absent() -> None:
    deleted_sources = (
        "packages/epcsaft/src/epcsaft/native/equilibrium/facade.h",
        "packages/epcsaft/src/epcsaft/native/equilibrium/workflows.cpp",
        "packages/epcsaft/src/epcsaft/native/equilibrium/routes/route_builders.cpp",
        "packages/epcsaft/src/epcsaft/native/equilibrium/routes/route_builders.h",
        "packages/epcsaft/src/epcsaft/native/equilibrium/routes/reactive",
        "packages/epcsaft/src/epcsaft/native/equilibrium/routes/stability",
    )
    for relpath in deleted_sources:
        assert not (REPO_ROOT / relpath).exists(), relpath

    binding_source_paths = [
        path
        for path in sorted((PROVIDER_NATIVE_ROOT / "bindings").rglob("*"))
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp"}
    ]
    binding_source_paths.append(EQUILIBRIUM_NATIVE_ROOT / "register_bindings.cpp")
    binding_sources = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in binding_source_paths)
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
    native_equilibrium_root = EQUILIBRIUM_NATIVE_ROOT
    shared_owner = native_equilibrium_root / "routes" / "derived" / "bubble_dew.cpp"
    route_file_allowlist = {
        EQUILIBRIUM_NATIVE_ROOT / "core" / "activation_matrix.h",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "selector_core.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "selector_core.h",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.h",
        EQUILIBRIUM_NATIVE_ROOT / "routes" / "derived" / "bubble_dew.cpp",
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
        rel = _workspace_rel(path)
        if path in route_file_allowlist:
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
        assert row["postsolve_certification"] in {"on", "tpd_postsolve"}, row["key"]
        assert row["derivative_requirement"] == "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes", row[
            "key"
        ]
        assert row["residual_families"], row["key"]
        assert row["constraint_families"], row["key"]
        assert row["proof_routes"], row["key"]
        assert row["variable_model"], row["key"]
        assert row["density_backend"], row["key"]

    selector_core = (EQUILIBRIUM_NATIVE_ROOT / "core" / "selector_core.cpp").read_text(
        encoding="utf-8", errors="ignore"
    )
    missing_selector_admission = sorted(key for key in production_keys if key not in selector_core)
    assert missing_selector_admission == []


def test_production_equilibrium_routes_delegate_ipopt_acceptance_to_adapter() -> None:
    route_sources = [
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "routes" / "derived" / "bubble_dew.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "results" / "result_builder.cpp",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in route_sources)
    adapter = (EQUILIBRIUM_NATIVE_ROOT / "solvers" / "ipopt_adapter.cpp").read_text(encoding="utf-8", errors="ignore")
    workflow = (EQUILIBRIUM_PACKAGE_ROOT / "workflows.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    assert "ipopt_solve_result_allows_postsolve(solve)" in combined
    assert "has_finite_complete_variables" not in combined
    assert "solve.accepted || solve.feasible_point" not in combined
    assert "result_.accepted = result_.solved || result_.acceptable" not in adapter
    assert 'solve.application_status == "solve_succeeded"' in adapter
    assert "success_status_and_scaled_kkt_required" in adapter
    assert "_resolved_ipopt_" not in workflow


def test_equilibrium_routes_delegate_result_acceptance_to_result_owners() -> None:
    route_sources = [
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.h",
        EQUILIBRIUM_NATIVE_ROOT / "routes" / "derived" / "bubble_dew.cpp",
    ]
    result_builder = (EQUILIBRIUM_NATIVE_ROOT / "results" / "result_builder.cpp").read_text(
        encoding="utf-8", errors="ignore"
    )
    held_certification = (
        EQUILIBRIUM_NATIVE_ROOT / "results" / "held_certification.cpp"
    ).read_text(encoding="utf-8", errors="ignore")

    forbidden_fragments = (
        ".solver_accepted =",
        ".solver_feasible_point = solve.feasible_point",
        ".solver_status = solve.solver_status",
        ".application_status = solve.application_status",
        ".accepted = result.postsolve.accepted",
        ".status = result.accepted ?",
        '.status = "solver_rejected"',
        ".status = certified_postsolve_status",
        "certified_postsolve_status(",
        "apply_ipopt_solve_metadata(",
        "discovery.held_stage_ii_bound_gap <= tpd_tolerance",
        "const bool continuous_tpd_complete =",
        "selected_upper_bound = 0.0;",
        "discovery.held_stage_ii_replay_ready =",
        "discovery.held_stage_ii_status =",
        "discovery.held_stage_ii_candidate_bound_audit_status =",
        "discovery.held_stage_ii_dual_loop_status =",
        "discovery.held_stage_ii_stopping_reason =",
        "discovery.held_stage_ii_replay_source =",
        "discovery.held_stage_ii_replay_seed_name =",
        "const bool solver_success =",
        "const bool finite_compositions =",
        "const bool residuals_pass =",
        "const bool phase_distance_pass =",
        "const bool bounds_pass =",
        "const bool derivative_pass =",
        "out.residual_inf_norm <= residual_tolerance",
        "out.phase_distance > phase_distance_tolerance",
        "out.active_bound_violation <= active_bound_tolerance",
        "phase_compositions = out.selected_phase_compositions;",
        "stage_ii.held_stage_ii_replay_ready",
        'out.held2_discovery.phase_discovery_status == "complete"',
        'out.phase_discovery_status = "complete";',
        'out.stage_iii_refinement_status = "pending";',
        'out.stage_iii_refinement_status = out.status == "complete"',
        'std::string stage_iii_refinement_status = "complete";',
    )
    acceptance_write_pattern = re.compile(
        r"\.(?:[A-Za-z_]*accepted|rejection_reason|phase_set_mass_balance_feasible)\s*="
    )
    held_policy_write_pattern = re.compile(
        r"\b[A-Za-z_][A-Za-z0-9_.]*\.held_stage_"
        r"(?:i_(?:status|negative_tpd_found)|ii_(?:status|candidate_bound_audit_status|"
        r"dual_loop_status|stopping_reason|replay_ready|replay_source|replay_seed_name))\s*="
    )
    electrolyte_policy_write_pattern = re.compile(
        r"\b[A-Za-z_][A-Za-z0-9_.]*\."
        r"(?:phase_discovery_status|stage_iii_refinement_status|postsolve_certification_status)\s*="
    )
    offenders: list[str] = []
    for path in route_sources:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = _workspace_rel(path)
        for fragment in forbidden_fragments:
            if fragment in text:
                offenders.append(f"{rel}: {fragment}")
        for match in acceptance_write_pattern.finditer(text):
            offenders.append(f"{rel}: {match.group(0)}")
        for match in held_policy_write_pattern.finditer(text):
            offenders.append(f"{rel}: {match.group(0)}")
        for match in electrolyte_policy_write_pattern.finditer(text):
            offenders.append(f"{rel}: {match.group(0)}")

    assert offenders == []
    assert "apply_neutral_route_solve_result" in result_builder
    assert "apply_neutral_route_postsolve" in result_builder
    assert "certify_neutral_postsolve" in result_builder
    assert "certify_neutral_phase_discovery" in result_builder
    assert "certify_electrolyte_postsolve" in result_builder
    assert "neutral_route_postsolve_status" in result_builder
    assert "certify_held_stage_i_evidence" in held_certification
    assert "complete_sampled_candidate_bound_audit" in held_certification
    assert "certify_held_stage_ii_bound_audit" in held_certification
    assert "held_stage_ii_replay_evidence_complete" in held_certification
    assert "sampled_candidate_replay_is_valid" in held_certification
    assert "held_stage_ii_replay_is_certified" in held_certification
    assert "certify_electrolyte_held2_phase_discovery" in held_certification
    assert "certify_electrolyte_stage_iii_refinement" in held_certification
    assert "certify_refined_neutral_postsolve" in held_certification
    assert 'postsolve.rejection_reason = "stage_ii_replay_not_consumed"' in held_certification


def test_neutral_lle_route_uses_only_the_sampled_candidate_pair() -> None:
    route_source = (
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.cpp"
    ).read_text(encoding="utf-8", errors="ignore")
    neutral_lle_route = route_source.split(
        "NeutralTwoPhaseEosRouteResult solve_activated_neutral_lle_eos_route(",
        maxsplit=1,
    )[1]

    assert 'out.initial_point_strategy = "sampled_candidate_pair_replay";' in neutral_lle_route
    assert "sampled_candidate_replay_is_valid(discovery)" in neutral_lle_route
    assert "build_two_phase_eos_initial_point_from_candidate_set(" in neutral_lle_route
    assert "sampled_candidate_pair_replay_unavailable" in neutral_lle_route
    assert "neutral_two_phase_seed_candidates" not in neutral_lle_route
    assert "append_phase_discovery_seed_candidates" not in neutral_lle_route
    assert "canonical_shifted_feed" not in neutral_lle_route
    assert "mirrored_shifted_feed" not in neutral_lle_route
    assert "binary_extreme_component_" not in neutral_lle_route
    assert "deterministic_seed_sweep" not in neutral_lle_route


def test_native_equilibrium_python_diagnostics_bridge_stays_centralized() -> None:
    bridge = (EQUILIBRIUM_NATIVE_ROOT / "results" / "route_result_bridge.h").read_text(
        encoding="utf-8", errors="ignore"
    )
    bindings = (EQUILIBRIUM_NATIVE_ROOT / "register_bindings.cpp").read_text(encoding="utf-8", errors="ignore")

    assert 'out["postsolve_accepted"] = result.postsolve_accepted' in bridge
    assert 'out["rejection_reason"] = result.rejection_reason' in bridge
    assert "neutral_route_stability_certificate_from_postsolve" in bridge
    assert "stability_checked = postsolve_dict" not in bindings
    assert "candidate_complete = postsolve_dict" not in bindings
    assert "route_physical_evidence_to_dict" in bridge
    assert 'out["physical_evidence"]' in bindings


def test_selector_request_pretreatment_and_phase_labels_stay_in_shared_bridges() -> None:
    workflows = (EQUILIBRIUM_PACKAGE_ROOT / "workflows.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )
    requests = (EQUILIBRIUM_PACKAGE_ROOT / "core" / "native_requests.py").read_text(encoding="utf-8", errors="ignore")
    results = (EQUILIBRIUM_PACKAGE_ROOT / "core" / "native_results.py").read_text(encoding="utf-8", errors="ignore")

    forbidden_workflow_fragments = (
        "NativeSelectorRouteSpec(",
        'composition_role="liquid"',
        'composition_role="vapor"',
        'composition_role="feed"',
        "route_tolerances = (",
        "phase_labels=expected_phase_keys",
        "native_route_phase_labels(",
    )
    offenders = [fragment for fragment in forbidden_workflow_fragments if fragment in workflows]
    assert offenders == []
    assert "selector_request_payload(" in workflows
    assert "selector_route_solver_tolerances(options)" in workflows
    assert "NativeSelectorRouteSpec(" in requests
    assert "def selector_route_solver_tolerances(" in requests
    assert "def native_route_phase_labels(" in results
    assert "labels = native_route_phase_labels(route, route_label)" in results
    assert "physical_evidence" in results


def test_activation_matrix_families_do_not_gain_direct_pybind_route_entrypoints() -> None:
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    binding_source_paths = [
        path
        for path in sorted((PROVIDER_NATIVE_ROOT / "bindings").rglob("*"))
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp"}
    ]
    binding_source_paths.append(EQUILIBRIUM_NATIVE_ROOT / "register_bindings.cpp")

    direct_binding_tokens = {f"_native_{key}" for key in activation_keys}
    binding_offenders: list[str] = []
    for path in binding_source_paths:
        rel = _workspace_rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in sorted(direct_binding_tokens):
            if token in text:
                binding_offenders.append(f"{rel}: {token}")
    assert binding_offenders == []


def test_equilibrium_route_solve_and_contract_owners_stay_in_shared_core_files() -> None:
    native_equilibrium_root = EQUILIBRIUM_NATIVE_ROOT
    allowed_route_owner_files = {
        EQUILIBRIUM_NATIVE_ROOT / "core" / "activated_equilibrium_nlp.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "activated_equilibrium_nlp.h",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "selector_core.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "selector_core.h",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.cpp",
        EQUILIBRIUM_NATIVE_ROOT / "core" / "two_phase_eos_route.h",
        EQUILIBRIUM_NATIVE_ROOT / "routes" / "derived" / "bubble_dew.cpp",
    }
    route_api_pattern = re.compile(
        r"(?m)^\s*(?!return\b)(?:[\w:<>]+[\s*&]+)+(?<!::)"
        r"(?:solve|evaluate)_[a-z0-9_]+_(?:route|nlp_contract)\s*\("
    )

    route_api_offenders: list[str] = []
    for path in sorted(native_equilibrium_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".cpp", ".h", ".hpp"}:
            continue
        rel = _workspace_rel(path)
        if path in allowed_route_owner_files:
            continue
        matches = sorted(set(route_api_pattern.findall(path.read_text(encoding="utf-8", errors="ignore"))))
        if matches:
            route_api_offenders.append(f"{rel}: {', '.join(matches)}")
    assert route_api_offenders == []

    activated_header = (
        EQUILIBRIUM_NATIVE_ROOT / "core" / "activated_equilibrium_nlp.h"
    ).read_text(encoding="utf-8", errors="ignore")
    activated_source = (
        EQUILIBRIUM_NATIVE_ROOT / "core" / "activated_equilibrium_nlp.cpp"
    ).read_text(encoding="utf-8", errors="ignore")
    chemical_header = (
        EQUILIBRIUM_NATIVE_ROOT / "core" / "chemical_equilibrium_nlp.h"
    ).read_text(encoding="utf-8", errors="ignore")
    chemical_source = (
        EQUILIBRIUM_NATIVE_ROOT / "core" / "chemical_equilibrium_nlp.cpp"
    ).read_text(encoding="utf-8", errors="ignore")
    activated_ce_symbols = (
        "evaluate_activated_chemical_equilibrium_nlp_contract",
        "solve_activated_chemical_equilibrium_nlp",
    )
    for symbol in activated_ce_symbols:
        assert symbol in activated_header
        assert symbol in activated_source
        assert symbol not in chemical_header
        assert symbol not in chemical_source

    obsolete_ce_indirection_symbols = (
        "build_homogeneous_chemical_equilibrium_contract",
        "solve_homogeneous_chemical_equilibrium",
    )
    combined_core_sources = "\n".join(
        (activated_header, activated_source, chemical_header, chemical_source)
    )
    assert [
        symbol for symbol in obsolete_ce_indirection_symbols if symbol in combined_core_sources
    ] == []
    assert "solve_max_min_feasible_initialization(" in activated_source
    assert "run_continuation_plan(" in activated_source

    assert "struct ChemicalEquilibriumNlpResult" in activated_header
    assert "struct ChemicalEquilibriumNlpResult" not in chemical_header
    forbidden_chemical_header_fragments = (
        '#include "equilibrium/core/continuation_driver.h"',
        '#include "equilibrium/core/two_phase_eos_route.h"',
        '#include "equilibrium/solvers/ipopt_adapter.h"',
        "IpoptSolveResult",
        "ContinuationTraceResult",
        "accepted_seed_source",
        "seed_attempt_order",
        "caller_seed_attempted",
    )
    assert [
        fragment for fragment in forbidden_chemical_header_fragments if fragment in chemical_header
    ] == []

    assert "struct ChemicalEquilibriumProofEvaluation" in chemical_header
    assert "evaluate_physical_proof(" in chemical_header
    assert "evaluate_physical_proof(" in chemical_source
    assert "const ChemicalEquilibriumProofEvaluation proof" in activated_source
    assert "proof.thermodynamically_accepted" in activated_source
    forbidden_activated_proof_policy = (
        "vector_inf_norm(",
        "postsolve.balance_residuals",
        "postsolve.reaction_affinities",
        "balance_inf_norm <= balance_tolerance",
        "reaction_stationarity_inf_norm <= reaction_stationarity_tolerance",
    )
    assert [
        fragment for fragment in forbidden_activated_proof_policy if fragment in activated_source
    ] == []


def test_equilibrium_python_surface_has_one_public_solve_lane_and_no_route_helpers() -> None:
    route_specs = _workflow_route_specs()
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    legacy_route_aliases = {"bubble_p", "bubble_t", "dew_p", "dew_t", "tp_flash", "lle_flash"}
    route_specific_names = set(route_specs) | activation_keys | legacy_route_aliases
    forbidden_helper_names = route_specific_names | {f"_solve_{name}" for name in route_specific_names}
    inspected_paths = (
        EQUILIBRIUM_PACKAGE_ROOT / "equilibrium.py",
        EQUILIBRIUM_PACKAGE_ROOT / "workflows.py",
        PROVIDER_PACKAGE_ROOT / "state" / "native_adapter.py",
    )

    offenders: list[str] = []
    for path in inspected_paths:
        rel = _workspace_rel(path) if path.is_relative_to(WORKSPACE_ROOT) else path.relative_to(REPO_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in forbidden_helper_names:
                offenders.append(f"{rel}:{node.lineno}: def {node.name}")

    frontend_tree = ast.parse(
        (EQUILIBRIUM_PACKAGE_ROOT / "equilibrium.py").read_text(encoding="utf-8"),
        filename=_workspace_rel(EQUILIBRIUM_PACKAGE_ROOT / "equilibrium.py"),
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
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id.startswith("_solve_selector")
    ]
    workflow_tree = ast.parse(
        (EQUILIBRIUM_PACKAGE_ROOT / "workflows.py").read_text(encoding="utf-8"),
        filename=_workspace_rel(EQUILIBRIUM_PACKAGE_ROOT / "workflows.py"),
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
        REGRESSION_PACKAGE_ROOT / "core.py",
        REGRESSION_PACKAGE_ROOT / "native_adapter.py",
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
        rel = _workspace_rel(path)
        offenders.extend(f"{rel}: {token}" for token in forbidden_tokens if token in text)

    assert offenders == []


def test_state_native_adapter_does_not_own_regression_native_wrappers() -> None:
    state_path = PROVIDER_PACKAGE_ROOT / "state" / "native_adapter.py"
    tree = ast.parse(state_path.read_text(encoding="utf-8"), filename=state_path.relative_to(REPO_ROOT).as_posix())
    regression_wrapper_names = {
        "_evaluate_generic_native_debug",
        "_fit_generic_native_ceres",
        "_fit_pure_neutral_native_debug",
    }
    defined_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    assert regression_wrapper_names.isdisjoint(defined_names)


def test_provider_native_sources_do_not_use_unnamed_namespaces() -> None:
    offenders: list[str] = []
    for path in sorted(PROVIDER_NATIVE_ROOT.rglob("*")):
        if path.suffix not in {".cpp", ".h", ".hpp"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"(?m)^\s*namespace\s*\{", text):
            line = text.count("\n", 0, match.start()) + 1
            offenders.append(f"{_workspace_rel(path)}:{line}")

    assert offenders == []


def test_m3_provider_source_files_stay_below_large_file_limit() -> None:
    native_cpp_limit = 1000
    state_facade_limit = 1250
    offenders: list[str] = []

    for path in sorted(PROVIDER_NATIVE_ROOT.rglob("*.cpp")):
        line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if line_count > native_cpp_limit:
            offenders.append(f"{_workspace_rel(path)} has {line_count} lines; limit is {native_cpp_limit}")

    for path in (
        PROVIDER_PACKAGE_ROOT / "state" / "native_adapter.py",
        PROVIDER_PACKAGE_ROOT / "state" / "native_payload.py",
    ):
        line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if line_count > state_facade_limit:
            offenders.append(f"{_workspace_rel(path)} has {line_count} lines; limit is {state_facade_limit}")

    assert offenders == []


def test_equilibrium_constructor_configured_api_has_no_legacy_kwargs_or_setup_helpers() -> None:
    frontend_path = EQUILIBRIUM_PACKAGE_ROOT / "equilibrium.py"
    tree = ast.parse(frontend_path.read_text(encoding="utf-8"), filename=_workspace_rel(frontend_path))
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
    import epcsaft_equilibrium as equilibrium
    import epcsaft_equilibrium.workflows as workflows
    from epcsaft.state.native_adapter import ePCSAFTMixture

    route_specific_methods = set(_workflow_route_specs())
    activation_keys = {str(row["key"]) for row in _equilibrium_activation_rows()}
    declared_not_exposed_keys = {
        str(row["key"]) for row in _equilibrium_activation_rows() if row["production_exposed"] is False
    }
    assert hasattr(equilibrium.Equilibrium, "solve")
    assert {name for name in route_specific_methods if hasattr(equilibrium.Equilibrium, name)} == set()
    assert {
        name
        for name in {"bubble_p", "bubble_t", "dew_p", "dew_t", "tp_flash"}
        if hasattr(equilibrium.Equilibrium, name)
    } == set()

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
        EQUILIBRIUM_PACKAGE_ROOT / "workflows.py",
        EQUILIBRIUM_PACKAGE_ROOT / "equilibrium.py",
        REGRESSION_PACKAGE_ROOT / "workflow.py",
        REGRESSION_PACKAGE_ROOT / "core.py",
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
                offenders.append(f"{_workspace_rel(path)}: {term}")
    assert offenders == []


def test_public_equilibrium_workflows_dispatch_only_through_selector_binding() -> None:
    workflows = (EQUILIBRIUM_PACKAGE_ROOT / "workflows.py").read_text(encoding="utf-8")
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
    assert "_native_neutral_two_phase_eos_result" not in workflows


def test_obsolete_second_pass_result_binding_is_not_registered_or_required() -> None:
    obsolete_binding = "_native_neutral_two_phase_eos_result"
    bindings = (EQUILIBRIUM_NATIVE_ROOT / "register_bindings.cpp").read_text(encoding="utf-8")
    native_loader = (EQUILIBRIUM_PACKAGE_ROOT / "_native.py").read_text(encoding="utf-8")
    native_stub = (EQUILIBRIUM_PACKAGE_ROOT / "_native_core.pyi").read_text(encoding="utf-8")

    assert obsolete_binding not in bindings
    assert obsolete_binding not in native_loader
    assert obsolete_binding not in native_stub


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
        "packages/epcsaft/src/epcsaft/native/eos/properties/density.cpp",
        "packages/epcsaft/src/epcsaft/native/model/native_types.h",
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
    tracked = _tracked_files("packages/epcsaft/src/epcsaft")

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
        "epcsaft.frontend.mixture",
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
            "epcsaft_equilibrium",
            "epcsaft_equilibrium.core",
            "epcsaft_equilibrium.workflows",
            "epcsaft_regression",
            "epcsaft.state.native_adapter",
            "epcsaft.state.properties",
        }
    )


def test_frontend_import_does_not_load_solver_extensions() -> None:
    loaded = _probe_epcsaft_import_modules(
        "from epcsaft import Mixture, ModelOptions, ParameterSet\n_ = (Mixture, ModelOptions, ParameterSet)"
    )
    assert {
        "epcsaft.frontend",
        "epcsaft.frontend.mixture",
        "epcsaft.model.options",
        "epcsaft.model.parameters",
    } <= loaded
    assert loaded.isdisjoint(
        {
            "epcsaft_equilibrium",
            "epcsaft_equilibrium.core",
            "epcsaft_equilibrium.workflows",
            "epcsaft_regression",
            "epcsaft.state.native_adapter",
            "epcsaft.state.properties",
        }
    )


def test_top_level_public_exports_do_not_load_equilibrium_extension() -> None:
    loaded = _probe_epcsaft_import_modules("import epcsaft\n_ = epcsaft.Mixture")
    assert "epcsaft.frontend" in loaded
    assert "epcsaft_equilibrium" not in loaded
    assert "epcsaft_regression" not in loaded


def test_reference_data_root_is_canonical() -> None:
    legacy_parameter_root = REPO_ROOT / "data" / "reference" / "epcsaft_parameters"
    assert legacy_parameter_root.is_dir()
    assert {path.name for path in legacy_parameter_root.iterdir()} == {"README.md"}
    readme = (legacy_parameter_root / "README.md").read_text(encoding="utf-8")
    assert "analyses/paper_validation/<paper_id>/parameters" in readme
    assert not (REPO_ROOT / "data" / "epcsaft_parameters").exists()


def test_paper_validation_parameter_inputs_are_local_snapshots() -> None:
    for analysis_rel in sorted(PAPER_VALIDATION_DOC_ROOTS):
        parameter_root = REPO_ROOT / analysis_rel / "parameters"
        assert parameter_root.is_dir(), analysis_rel
        assert (parameter_root / "mixed").is_dir(), analysis_rel
        assert (parameter_root / "pure").is_dir(), analysis_rel
        assert (parameter_root / "user_options.json").is_file(), analysis_rel
        dataset_suffixes = (
            "_Gross",
            "_Held",
            "_Baygi",
            "_Ascani",
            "_Yu",
            "_Rezaee",
            "_Cameretti",
            "_Bulow",
            "_Figiel",
            "_Khudaida",
            "_Hubach",
        )
        assert not any(child.is_dir() for child in parameter_root.iterdir() if child.name.endswith(dataset_suffixes))


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
                assert "=" not in ",".join(
                    row[column] for column in PAPER_VALIDATION_PARAMETER_REQUIRED_VALUE_COLUMNS
                ), row
                for column in PAPER_VALIDATION_PARAMETER_REQUIRED_VALUE_COLUMNS:
                    assert row[column].strip() != "", f"{pure_file}: {row['component']} {column}"

        binary_root = parameter_root / "mixed" / "binary_interaction"
        assert binary_root.is_dir(), analysis_rel
        source_manifest = binary_root / "source_manifest.csv"
        assert source_manifest.is_file(), analysis_rel
        with source_manifest.open(encoding="utf-8-sig", newline="") as handle:
            manifest_rows = list(csv.DictReader(handle))
        for filename in sorted(PAPER_VALIDATION_BINARY_FILES):
            matrix_file = binary_root / filename
            parameter_family = matrix_file.stem
            unresolved_rows = [
                row
                for row in manifest_rows
                if row.get("parameter") == parameter_family
                and row.get("provenance_status") == "unresolved_parameter_family"
            ]
            if unresolved_rows:
                assert not matrix_file.exists(), matrix_file
                assert all(not row.get("value", "").strip() for row in unresolved_rows), source_manifest
                continue
            assert matrix_file.is_file(), matrix_file
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


def test_untyped_paper_parameter_expressions_fail_loudly() -> None:
    from epcsaft.model.datasets import get_prop_dict

    temperature = 298.15
    with pytest.raises(ValueError, match=r"component 'H2O'.*field 's'"):
        get_prop_dict(
            REPO_ROOT / "analyses" / "paper_validation" / "2023_ascani" / "parameters",
            ["H2O", "1-Pentanol"],
            [0.5, 0.5],
            temperature,
        )

    with pytest.raises(ValueError, match=r"multiple pure parameter sets.*versioned model configuration"):
        get_prop_dict(
            REPO_ROOT / "analyses" / "paper_validation" / "2012_held" / "parameters",
            ["Methanol"],
            [1.0],
            temperature,
        )


def test_analysis_category_roots_exist() -> None:
    for root in sorted(CATEGORY_ROOTS):
        assert root.is_dir(), root


def test_paper_validation_uses_flat_paper_roots() -> None:
    paper_root = REPO_ROOT / "analyses" / "paper_validation"
    actual = {path.relative_to(REPO_ROOT).as_posix() for path in paper_root.iterdir() if path.is_dir()}
    assert actual == PAPER_VALIDATION_DOC_ROOTS | PAPER_SOURCE_EVIDENCE_ROOTS | PAPER_VALIDATION_INFRA_ROOTS
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
        figures_manifest = shared_source / "figures_manifest.csv"
        assert figures_manifest.is_file(), analysis_rel
        with figures_manifest.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            assert "sha256_file" not in (reader.fieldnames or []), figures_manifest
            for row in reader:
                assert re.fullmatch(r"figure_\d{2,}", row["figure_id"]), row
                assert row["local_file"].endswith(".png"), row
                assert (REPO_ROOT / row["local_file"]).is_file(), row
        assert not (shared_source / "tables").exists(), analysis_rel
        assert (tables_root / "tables_manifest.csv").is_file(), analysis_rel
        assert list((docs_root / "md").glob("*.md")), analysis_rel
        assert any(path.is_file() for path in (docs_root / "pdf").iterdir()), analysis_rel
        assert any(path.is_file() for path in shared_source.iterdir()), analysis_rel


def test_paper_source_evidence_lanes_have_no_model_artifact_skeletons() -> None:
    for analysis_rel in sorted(PAPER_SOURCE_EVIDENCE_ROOTS):
        analysis_root = REPO_ROOT / analysis_rel
        metadata = yaml.safe_load((analysis_root / "analysis.yaml").read_text(encoding="utf-8"))
        assert metadata["status"] == "internal_source_evidence_only", analysis_rel
        assert metadata["expected"]["model_validation_complete"] is False, analysis_rel
        assert metadata["expected"]["phase_models_supported"] is False, analysis_rel
        assert metadata["expected"]["public_route_admitted"] is False, analysis_rel
        assert {path.name for path in analysis_root.iterdir() if path.is_dir()} == {
            "docs",
            "figures",
            "scripts",
            "shared",
        }, analysis_rel
        assert not (analysis_root / "parameters").exists(), analysis_rel
        assert not (analysis_root / "tables").exists(), analysis_rel

        script_names = {
            path.name for path in (analysis_root / "scripts").glob("*.py")
        }
        assert script_names == {
            "_paths.py",
            "rezaee_2025_target_summary.py",
            "rezaee_section32_basis_inference.py",
            "run_all.py",
        }, analysis_rel
        assert not list(analysis_root.rglob("_placeholder.md")), analysis_rel

        figure_roots = sorted(
            path for path in (analysis_root / "figures").iterdir() if path.is_dir()
        )
        assert figure_roots, analysis_rel
        for figure_root in figure_roots:
            assert re.fullmatch(r"figure_\d{2,}", figure_root.name), figure_root
            assert {path.name for path in figure_root.iterdir() if path.is_dir()} == {
                "source"
            }, figure_root
            assert any((figure_root / "source").iterdir()), figure_root


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
            assert [path.name for path in figures_root.iterdir() if path.is_file()] == ["_placeholder.md"], analysis_rel
            continue
        assert not any(path.is_file() for path in figures_root.iterdir()), analysis_rel
        assert len({path.name for path in figure_roots}) == len(figure_roots), analysis_rel
        for figure_root in figure_roots:
            assert re.fullmatch(r"figure_\d{2,}", figure_root.name), figure_root
            assert {path.name for path in figure_root.iterdir() if path.is_dir()} == PAPER_VALIDATION_FIGURE_SUBDIRS
            assert not any(path.is_file() for path in figure_root.iterdir()), figure_root
            assert list(figure_root.rglob("*.sha256")) == [], figure_root
            for subdir in PAPER_VALIDATION_FIGURE_SUBDIRS:
                assert any((figure_root / subdir).iterdir()), figure_root / subdir
            for source_png in (figure_root / "source").glob("paper_source_*.png"):
                assert not (source_png.with_suffix(source_png.suffix + ".sha256")).exists(), source_png
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
    for path in sorted(TEST_SUBGROUP_ROOTS):
        assert path.is_dir(), _workspace_rel(path)


def test_extension_owned_tests_are_package_local() -> None:
    forbidden_root_extension_tests = [
        *(_tracked_files("tests/native/equilibrium")),
        *(_tracked_files("tests/native/regression")),
        "tests/api/frontend/test_regression.py"
        if (REPO_ROOT / "tests/api/frontend/test_regression.py").exists()
        else "",
        "tests/native/contracts/test_equilibrium_native_contracts.py"
        if (REPO_ROOT / "tests/native/contracts/test_equilibrium_native_contracts.py").exists()
        else "",
        "tests/native/contracts/test_ceres_cppad_build_contract.py"
        if (REPO_ROOT / "tests/native/contracts/test_ceres_cppad_build_contract.py").exists()
        else "",
    ]
    assert [path for path in forbidden_root_extension_tests if path] == []

    expected_package_tests = {
        EQUILIBRIUM_TEST_ROOT / "contracts" / "test_equilibrium_native_contracts.py",
        EQUILIBRIUM_TEST_ROOT / "native" / "blocks" / "test_ipopt_adapter_contract.py",
        EQUILIBRIUM_TEST_ROOT / "native" / "diagnostics" / "test_selector_core_contracts.py",
        EQUILIBRIUM_TEST_ROOT / "native" / "results" / "test_neutral_lle_reference_values.py",
        REGRESSION_TEST_ROOT / "api" / "test_regression.py",
        REGRESSION_TEST_ROOT / "contracts" / "test_ceres_cppad_build_contract.py",
        REGRESSION_TEST_ROOT / "native" / "test_pure.py",
        REGRESSION_TEST_ROOT / "native" / "test_binary.py",
        REGRESSION_TEST_ROOT / "native" / "test_liquid_electrolyte.py",
    }
    missing = sorted(_workspace_rel(path) for path in expected_package_tests if not path.is_file())
    assert missing == []


def test_package_local_extension_tests_do_not_import_root_test_support() -> None:
    offenders: list[str] = []
    for root in (EQUILIBRIUM_TEST_ROOT, REGRESSION_TEST_ROOT):
        for path in sorted(root.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if "tests.support" in text or "from tests" in text or "import tests" in text:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert offenders == []


def test_test_tree_uses_namespace_packages_without_init_markers() -> None:
    assert list((REPO_ROOT / "tests").rglob("__init__.py")) == []


def test_replaced_flat_test_modules_are_absent_from_the_working_tree() -> None:
    for relpath in sorted(REPLACED_FLAT_TEST_FILES):
        assert not (REPO_ROOT / relpath).exists(), relpath


def test_superpowers_project_layout_matches_local_contract() -> None:
    project_root = REPO_ROOT / "docs" / "superpowers"
    milestone_root = project_root / "milestones"
    assert project_root.is_dir()
    assert (project_root / "README.md").is_file()
    assert not (REPO_ROOT / "docs" / "milestones").exists()
    assert not (REPO_ROOT / "docs" / "roadmaps").exists()
    assert not (REPO_ROOT / "docs" / "plans").exists()
    assert (project_root / "PROJECT_CONTEXT.md").is_file()
    assert (project_root / "specs").is_dir()
    assert (project_root / "plans").is_dir()
    assert (project_root / "issues").is_dir()

    actual_folders = {path.name for path in milestone_root.iterdir() if path.is_dir()}
    assert actual_folders == set(MILESTONE_MIRROR_FOLDERS)

    missing_templates = sorted(path for path in SUPERPOWERS_TEMPLATE_FILES if not (project_root / path).is_file())
    assert missing_templates == []
    issue_template_fields = _markdown_front_matter(project_root / "_templates" / "issue-mirror.md")
    assert set(issue_template_fields) == MILESTONE_FRONT_MATTER_FIELDS

    missing_specs = sorted(path for path in SUPERPOWERS_SPEC_FILES if not (project_root / path).is_file())
    assert missing_specs == []
    spec_files = sorted(path.name for path in (project_root / "specs").glob("*.md") if path.name != "README.md")
    bad_spec_names = sorted(name for name in spec_files if not SUPERPOWERS_SPEC_FILENAME_PATTERN.fullmatch(name))
    assert bad_spec_names == []
    assert (project_root / "plans" / "README.md").is_file()
    plan_files = sorted(path.name for path in (project_root / "plans").glob("*.md") if path.name != "README.md")
    bad_plan_names = sorted(name for name in plan_files if not SUPERPOWERS_PLAN_FILENAME_PATTERN.fullmatch(name))
    assert bad_plan_names == []
    missing_registries = sorted(path for path in SUPERPOWERS_REGISTRY_FILES if not (project_root / path).is_file())
    assert missing_registries == []

    for folder, milestone in MILESTONE_MIRROR_FOLDERS.items():
        milestone_dir = milestone_root / folder
        readme = milestone_dir / "README.md"
        if readme.is_file():
            assert milestone in readme.read_text(encoding="utf-8")

    issues_dir = project_root / "issues"
    assert any(issues_dir.glob("*.md"))
    for path in sorted(path for path in issues_dir.glob("*.md") if path.name != "README.md"):
        fields = _markdown_front_matter(path)
        assert set(fields) == MILESTONE_FRONT_MATTER_FIELDS
        issue = fields["issue"]
        assert isinstance(issue, int)
        assert SUPERPOWERS_ISSUE_FILENAME_PATTERN.fullmatch(path.name)
        assert f"issue-{issue:04d}-" in path.name
        assert fields["url"] == f"https://github.com/ePC-SAFT/ePC-SAFT/issues/{issue}"
        text = path.read_text(encoding="utf-8")
        retained_closed_mirror = fields["state"] == "closed" and "**Mirror Retention:** Keep" in text
        if retained_closed_mirror:
            assert fields["readiness"] == "closed"
            assert fields["source_spec"] is None
            assert fields["source_plan"] is None
            assert fields["branch"] is None
        else:
            assert fields["state"] == "open"
        assert fields["project"] == "ePC-SAFT Roadmap"
        assert fields["milestone"] in set(MILESTONE_MIRROR_FOLDERS.values())
        milestone_folder = next(
            folder for folder, title in MILESTONE_MIRROR_FOLDERS.items() if title == fields["milestone"]
        )
        assert f"-{milestone_folder.lower()}-issue-" in path.name
        assert not str(fields["title"]).startswith("[Blocked]")
        if not retained_closed_mirror:
            source_spec = Path(str(fields["source_spec"]))
            source_plan = Path(str(fields["source_plan"]))
            assert source_spec.as_posix().startswith("docs/superpowers/specs")
            assert source_plan.as_posix().startswith("docs/superpowers/plans")
            assert (REPO_ROOT / source_spec).is_file(), str(source_spec)
            assert (REPO_ROOT / source_plan).is_file(), str(source_plan)
        assert fields["afk_hitl"] in {"AFK", "HITL"}
        if not retained_closed_mirror:
            assert str(fields["branch"]).startswith(f"codex/issue-{issue:04d}-")
        assert re.fullmatch(r"20\d\d-\d\d-\d\d", str(fields["last_synced"]))
        required_tokens = [
            "GitHub Issue:",
            "AFK/HITL:",
            "## Acceptance Criteria",
            "## Proof Oracle",
        ]
        if retained_closed_mirror:
            required_tokens.append("**Mirror Retention:** Keep")
        else:
            required_tokens.append("Source Plan:")
        for token in required_tokens:
            assert token in text, f"{_workspace_rel(path)} missing {token}"


def test_project_roadmap_setup_contract_matches_github_tracker_shape() -> None:
    roadmap_md = REPO_ROOT / "docs" / "agents" / "project-roadmap.md"
    roadmap_json = REPO_ROOT / "docs" / "agents" / "project-roadmap.json"
    issue_tracker = (REPO_ROOT / "docs" / "agents" / "issue-tracker.md").read_text(encoding="utf-8")
    triage_labels = (REPO_ROOT / "docs" / "agents" / "triage-labels.md").read_text(encoding="utf-8")

    assert roadmap_md.is_file()
    assert roadmap_json.is_file()
    setup = json.loads(roadmap_json.read_text(encoding="utf-8"))

    assert PROJECT_ROADMAP_REQUIRED_FIELDS.issubset(setup)
    assert setup["target_repo"] == "ePC-SAFT/ePC-SAFT"
    assert setup["full_roadmap"] == "docs/superpowers/PROJECT_CONTEXT.md"
    assert setup["milestone_policy"] == "mirror-existing-full-roadmap"
    assert setup["project_policy"] == "dashboard-only"
    assert setup["apply_policy"] == "default-branch-commit-push"
    assert setup["projects_required_by_repo_config"] is False
    assert set(setup["issue_types"]) == {"bug", "feature", "task"}
    assert setup["issue_relationships"]["canonical_blocker_state"] == "github_issue_dependencies"
    assert setup["issue_relationships"]["blocked_title_prefix_forbidden"] is True
    assert {"status:blocked", "Project Readiness=blocked"} <= set(setup["issue_relationships"]["dashboard_mirrors"])
    assert {"issue": 145, "blocked_by": 148} in setup["issue_relationships"]["audited_edges"]
    assert {"type:bug", "type:feature", "type:task", "status:triage", "status:ready", "status:blocked"}.issubset(
        setup["labels"]
    )
    assert {"bug", "feature", "task"}.issubset(setup["issue_forms"])
    assert setup["project"]["url"] == "https://github.com/orgs/ePC-SAFT/projects/1"
    assert setup["issue_type_backfill"]["missing_type_count_after_apply"] == 0

    for token in ("Bug", "Feature", "Task", "type:bug", "type:feature", "type:task", "blocked_by"):
        assert token in roadmap_md.read_text(encoding="utf-8")
        assert token in issue_tracker
    for token in ("type:bug", "type:feature", "type:task"):
        assert token in triage_labels


def test_agents_md_stays_a_short_tracked_repo_router() -> None:
    agents_path = REPO_ROOT / "AGENTS.md"
    text = agents_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    words = re.findall(r"\S+", text)

    assert lines[0] == "# ePC-SAFT Agent Instructions"
    assert len(lines) <= 80
    assert len(words) <= 1200

    missing_links = sorted(link for link in AGENTS_REQUIRED_DOC_LINKS if link not in text)
    assert missing_links == []

    banned = sorted(phrase for phrase in AGENTS_BANNED_PHRASES if phrase in text)
    assert banned == []
    assert not re.search(r"[A-Za-z]:\\Users\\Tanner", text)


def test_expected_nested_agents_files_are_present_and_scoped() -> None:
    missing = sorted(relpath for relpath in EXPECTED_NESTED_AGENT_FILES if not (REPO_ROOT / relpath).is_file())
    assert missing == []

    allowed = {"AGENTS.md", *EXPECTED_NESTED_AGENT_FILES}
    actual = {
        path.relative_to(REPO_ROOT).as_posix() for path in REPO_ROOT.rglob("AGENTS.md") if ".git" not in path.parts
    }
    unexpected = sorted(actual - allowed)
    assert unexpected == []

    for relpath, tokens in EXPECTED_NESTED_AGENT_TOKENS.items():
        text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
        missing_tokens = sorted(token for token in tokens if token not in text)
        assert missing_tokens == [], relpath
        assert not re.search(r"[A-Za-z]:\\Users\\Tanner", text)
        assert "docs/superpowers/PROJECT_CONTEXT.md" not in text
        assert "docs/agents/issue-tracker.md" not in text


def test_issue_templates_set_native_issue_types_and_compatibility_labels() -> None:
    template_root = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"

    for filename, issue_type in ISSUE_TYPE_FORMS.items():
        path = template_root / filename
        assert path.is_file(), filename
        form = yaml.safe_load(path.read_text(encoding="utf-8"))
        labels = set(form.get("labels", []))
        assert form["type"] == issue_type
        assert f"type:{issue_type}" in labels
        assert "ePC-SAFT/1" in set(form.get("projects", []))

    for filename in ("bug.yml", "feature.yml", "task.yml"):
        form = yaml.safe_load((template_root / filename).read_text(encoding="utf-8"))
        field_ids = {field.get("id") for field in form["body"] if "id" in field}
        assert {"plan-file", "outcome", "acceptance", "non-goals", "proof-oracle"}.issubset(field_ids)


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
            or re.search(r"^analyses/paper_validation/[^/]+/figures/(?!figure_\d{2,}/|_placeholder\.md$)", normalized)
            or normalized.endswith(".sha256")
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


def test_nonideal_mea_migration_contract_uses_current_analysis_roots() -> None:
    contract = json.loads(STANDALONE_CE_NONIDEAL_MIGRATION_CONTRACT.read_text(encoding="utf-8"))
    declared_paths = contract["paths"]

    assert declared_paths["analysis_root"] == ANALYSIS_ROOTS["standalone_ce"].relative_to(REPO_ROOT).as_posix()
    assert declared_paths["figure_root"] == STANDALONE_CE_NONIDEAL_FIGURE_ROOT.relative_to(REPO_ROOT).as_posix()
    for relative_root in declared_paths.values():
        assert (REPO_ROOT / relative_root).is_dir(), relative_root
    assert not (STANDALONE_CE_NONIDEAL_FIGURE_ROOT / "results").exists()
    assert not (REPO_ROOT / "analyses" / "paper_validation" / "standalone_ce").exists()


def test_migrated_analyses_use_complete_figure_owned_roots() -> None:
    for analysis_id in sorted(MIGRATED_ANALYSIS_IDS):
        figures_root = ANALYSIS_ROOTS[analysis_id] / "figures"
        assert figures_root.is_dir(), analysis_id
        figure_roots = sorted(path for path in figures_root.iterdir() if path.is_dir())
        assert figure_roots, analysis_id
        for figure_root in figure_roots:
            if figure_root.as_posix().startswith((REPO_ROOT / "analyses" / "paper_validation").as_posix()):
                assert re.fullmatch(r"figure_\d{2,}", figure_root.name), figure_root
            assert (figure_root / "scripts").is_dir(), figure_root
            if figure_root.as_posix().startswith((REPO_ROOT / "analyses" / "paper_validation").as_posix()):
                optional_roots = (figure_root / "source", figure_root / "results")
            else:
                optional_roots = (figure_root / "input", figure_root / "output")
            assert any(path.is_dir() for path in optional_roots) or any((figure_root / "scripts").glob("*.py")), (
                figure_root
            )


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


def test_reference_data_paths_use_taxonomy_not_source_names() -> None:
    reference_root = REPO_ROOT / "data" / "reference"
    offenders = [
        path.relative_to(reference_root).as_posix()
        for path in sorted(reference_root.rglob("*"))
        if DATA_REFERENCE_FORBIDDEN_PATH_PATTERN.search(path.relative_to(reference_root).as_posix())
    ]

    assert offenders == []


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
    for figure_id in ("figure_04", "figure_05", "figure_06", "figure_07", "figure_08", "figure_09"):
        figure_root = root / "figures" / figure_id
        assert (figure_root / "source").is_dir(), figure_id
        assert (figure_root / "results").is_dir(), figure_id
        assert (figure_root / "scripts").is_dir(), figure_id
