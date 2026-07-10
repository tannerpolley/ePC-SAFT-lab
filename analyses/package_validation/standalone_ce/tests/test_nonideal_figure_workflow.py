from __future__ import annotations

import ast
import itertools
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "package_validation" / "standalone_ce"
FIGURE_ROOT = ANALYSIS_ROOT / "figures" / "mea_reactive_speciation_oracle_comparison"
MIGRATION_CONTRACT_PATH = FIGURE_ROOT / "source" / "migration_contract.json"

EXPECTED_PATHS = {
    "analysis_root": "analyses/package_validation/standalone_ce",
    "figure_root": (
        "analyses/package_validation/standalone_ce/figures/"
        "mea_reactive_speciation_oracle_comparison"
    ),
    "source_root": (
        "analyses/package_validation/standalone_ce/figures/"
        "mea_reactive_speciation_oracle_comparison/source"
    ),
    "scripts_root": (
        "analyses/package_validation/standalone_ce/figures/"
        "mea_reactive_speciation_oracle_comparison/scripts"
    ),
    "output_root": (
        "analyses/package_validation/standalone_ce/figures/"
        "mea_reactive_speciation_oracle_comparison/output"
    ),
}
EXPECTED_EVIDENCE_ROLES = [
    "literature_observation",
    "imported_downstream_model_snapshot",
    "current_local_model_prediction",
    "diagnostic_seed",
]
EXPECTED_STATIC_GRID = [
    {"temperature_c": 20.0, "loading_start": 0.020, "loading_end": 0.795, "loading_count": 161},
    {"temperature_c": 40.0, "loading_start": 0.005, "loading_end": 0.800, "loading_count": 161},
    {"temperature_c": 60.0, "loading_start": 0.001, "loading_end": 0.800, "loading_count": 161},
    {"temperature_c": 80.0, "loading_start": 0.001, "loading_end": 0.800, "loading_count": 161},
]
EXPECTED_PLANNED_COMMANDS = [
    {
        "command": (
            "uv run --no-sync python run_pytest.py "
            "analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py "
            "tests/native/contracts/test_standalone_ce_gate.py "
            "tests/workflows/repo/test_project_structure.py -q"
        ),
        "owner_task": 1,
        "currently_available": True,
    },
    {
        "command": "uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium",
        "owner_task": 6,
        "currently_available": True,
    },
    {
        "command": (
            "uv run --no-sync python analyses/package_validation/standalone_ce/figures/"
            "mea_reactive_speciation_oracle_comparison/scripts/generate_nonideal_data.py"
        ),
        "owner_task": 6,
        "currently_available": False,
    },
    {
        "command": (
            "uv run --no-sync python analyses/package_validation/standalone_ce/figures/"
            "mea_reactive_speciation_oracle_comparison/scripts/render_figure.py"
        ),
        "owner_task": 7,
        "currently_available": True,
    },
]


def test_nonideal_mea_migration_contract_is_immutable_and_linux_only() -> None:
    assert MIGRATION_CONTRACT_PATH.is_file(), (
        "nonideal MEA migration requires the immutable machine-readable contract at "
        f"{MIGRATION_CONTRACT_PATH.relative_to(REPO_ROOT)}"
    )
    contract = json.loads(MIGRATION_CONTRACT_PATH.read_text(encoding="utf-8"))

    assert contract["schema_version"] == "epcsaft.standalone_ce.nonideal_mea_migration.v1"
    assert contract["lineage"] == {
        "source_branch": "codex/m4-ce-nonideal-speciation-plots",
        "source_tip_commit": "f3057e11",
        "local_main": "main",
        "integration_policy": "adapt_only_do_not_merge",
    }
    assert contract["paths"] == EXPECTED_PATHS
    for relative_root in contract["paths"].values():
        assert (REPO_ROOT / relative_root).is_dir(), relative_root
    assert contract["evidence_roles"] == EXPECTED_EVIDENCE_ROLES
    assert contract["static_grid"] == EXPECTED_STATIC_GRID

    animation_grid = contract["animation_grid"]
    assert animation_grid == {
        "temperatures_c": [20.0, 40.0, 60.0, 80.0],
        "loadings_mol_co2_per_mol_mea": [0.10, 0.30, 0.50, 0.70],
        "state_count": 16,
        "excluded_temperatures_c": [0.0],
        "exclusion_reason": "outside_approved_scope_and_unproven_at_273.15_K",
    }
    states = list(
        itertools.product(
            animation_grid["temperatures_c"],
            animation_grid["loadings_mol_co2_per_mol_mea"],
        )
    )
    assert len(states) == animation_grid["state_count"]
    assert all(temperature_c != 0.0 for temperature_c, _ in states)

    assert "public_routes" not in contract
    assert contract["capability_boundary"] == {
        "public_routes": [],
        "closed_surfaces": [
            "reactive_speciation",
            "reactive_lle",
            "reactive_electrolyte_lle",
            "cpe",
        ],
        "execution_owner": "epcsaft_equilibrium.workflows._run_standalone_ce_validation",
    }
    assert contract["globally_closed_relevant_families"] == {
        "scope": "migration_global_constraints_not_analysis_capability_surface",
        "families": ["electrolyte_lle", "tp_flash", "multiphase"],
    }
    assert "commands" not in contract
    assert contract["planned_commands"] == EXPECTED_PLANNED_COMMANDS
    assert contract["forbidden_migration_artifacts"] == [
        "analyses/paper_validation/standalone_ce",
        "user_options.json",
        "results/",
        "public_reactive_imports",
        "windows_only_commands",
    ]

    commands = [record["command"] for record in contract["planned_commands"]]
    command_text = "\n".join(commands).lower()
    assert all(command.startswith("uv run --no-sync python ") for command in commands)
    for forbidden_fragment in (
        "\\",
        "powershell",
        "pwsh",
        "conda",
        ".exe",
        ".dll",
    ):
        assert forbidden_fragment not in command_text

    assert not (REPO_ROOT / "analyses" / "paper_validation" / "standalone_ce").exists()
    assert not (FIGURE_ROOT / "results").exists()
    assert not list(ANALYSIS_ROOT.rglob("user_options.json"))

    source_paths = sorted((FIGURE_ROOT / "scripts").glob("*.py"))
    assert source_paths
    for path in source_paths:
        source = path.read_text(encoding="utf-8")
        source_lower = source.lower()
        assert "user_options.json" not in source_lower, path
        assert "phase2_runtime_user_options" not in source_lower, path
        assert re.search(r"[a-z]:[\\/]", source, flags=re.IGNORECASE) is None, path
        for forbidden_fragment in ("powershell", "pwsh", "conda", ".exe", ".dll"):
            assert forbidden_fragment not in source_lower, path

        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    alias.name
                    not in {
                        "epcsaft.reactive_speciation",
                        "epcsaft_equilibrium.reactive_speciation",
                    }
                    for alias in node.names
                ), path
                continue
            if not isinstance(node, ast.ImportFrom):
                continue
            module = node.module or ""
            assert not module.endswith(".reactive_speciation"), path
            if module in {"epcsaft", "epcsaft_equilibrium", "epcsaft_equilibrium.workflows"}:
                assert all(alias.name != "reactive_speciation" for alias in node.names), path
