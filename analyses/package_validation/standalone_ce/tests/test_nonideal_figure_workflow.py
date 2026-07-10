from __future__ import annotations

import ast
import csv
import hashlib
import io
import itertools
import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "package_validation" / "standalone_ce"
FIGURE_ROOT = ANALYSIS_ROOT / "figures" / "mea_reactive_speciation_oracle_comparison"
MIGRATION_CONTRACT_PATH = FIGURE_ROOT / "source" / "migration_contract.json"
SOURCE_ROOT = FIGURE_ROOT / "source"

SOURCE_REVISION = "f3057e11"
SOURCE_ARTIFACT_ROOT = (
    "analyses/paper_validation/standalone_ce/figures/"
    "mea_reactive_speciation_oracle_comparison/source"
)
EXCLUDED_FROM_LITERATURE_SCORING = "excluded_from_literature_scoring"
UNRESOLVED_CITATION_REASON = (
    "surname_only_citations_lack_resolvable_bibliographic_identity_and_exact_"
    "table_or_figure_locator"
)

MIGRATED_SOURCE_TABLES = {
    "imported_downstream_model_snapshot.csv": {
        "source_name": "phase2_speciation_activity_curves.csv",
        "source_sha256": "ab6607a7d3e12921eb7647b97e67f82741950cf309941d2a3d1006651205b1fb",
        "original_columns": [
            "temperature_C",
            "CO2_loading",
            "effective_CO2_loading",
            "species",
            "mole_fraction",
            "curve_role",
            "solver_success",
        ],
        "row_count": 5796,
    },
    "unresolved_reference_observations.csv": {
        "source_name": "phase2_speciation_reference_points.csv",
        "source_sha256": "e50a01ce724878464d145923d2458e595ed282d9be63d507e066e11a57443e29",
        "original_columns": [
            "source",
            "temperature_C",
            "MEA_weight_fraction",
            "CO2_loading",
            "species",
            "mole_fraction",
            "point_role",
            "target_role",
        ],
        "row_count": 293,
    },
    "imported_target_role_snapshot.csv": {
        "source_name": "phase2_speciation_target_roles.csv",
        "source_sha256": "d6d80e2603353ad876f223bb1b0bd576fb4a52a75e8f097666019fc3ac4d610a",
        "original_columns": [
            "row_id",
            "source",
            "temperature_C",
            "MEA_weight_fraction",
            "CO2_loading",
            "species",
            "target_role",
            "validation_use",
            "reconciled_mole_fraction",
        ],
        "row_count": 666,
    },
}

UNCHANGED_SOURCE_TABLES = {
    "phase2_activity_constant_candidates.csv": (
        "24071df004a6a527584451ddd07ab1468004c855131d2efd66e5e81b2def1dc2"
    ),
    "phase2_reaction_constant_source_verification.csv": (
        "a2ac96b293767b71d0766f76309743c211b9486faded912c96f905d2bdee72bf"
    ),
    "phase2_reaction_constant_basis.csv": (
        "93ef666df9cffe2571ac50d5128bc1504aeb05446c8f90056ec0be48fe778124"
    ),
}

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
EXPECTED_EXCLUDED_EVIDENCE_ROLES = ["unresolved_reference_observation"]
MISSING_NASRIFAR_SOURCE_PATH = (
    "docs/papers/md/Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of "
    "acid gas-aqueous ethanolamine solutions us.md"
)
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


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        return reader.fieldnames, list(reader)


def _projected_source_sha256(
    fieldnames: list[str], rows: list[dict[str, str]]
) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row[field] for field in fieldnames} for row in rows)
    return hashlib.sha256(buffer.getvalue().encode("utf-8")).hexdigest()


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
    assert contract["excluded_evidence_roles"] == EXPECTED_EXCLUDED_EVIDENCE_ROLES
    assert not set(contract["evidence_roles"]) & set(contract["excluded_evidence_roles"])
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


def test_retained_nonideal_source_rows_have_explicit_roles_and_lineage() -> None:
    activity_path = SOURCE_ROOT / "imported_downstream_model_snapshot.csv"
    activity_columns, activity_rows = _read_csv(activity_path)
    activity_source = f"{SOURCE_ARTIFACT_ROOT}/phase2_speciation_activity_curves.csv"
    assert len(activity_rows) == MIGRATED_SOURCE_TABLES[activity_path.name]["row_count"]
    assert _projected_source_sha256(
        MIGRATED_SOURCE_TABLES[activity_path.name]["original_columns"], activity_rows
    ) == MIGRATED_SOURCE_TABLES[activity_path.name]["source_sha256"]
    assert activity_columns[-8:] == [
        "evidence_role",
        "source_artifact",
        "source_revision",
        "temperature_units",
        "loading_units",
        "value_units",
        "classification",
        "scoring_use",
    ]
    assert {row["evidence_role"] for row in activity_rows} == {
        "imported_downstream_model_snapshot"
    }
    assert {row["source_artifact"] for row in activity_rows} == {activity_source}
    assert {row["source_revision"] for row in activity_rows} == {SOURCE_REVISION}
    assert {row["temperature_units"] for row in activity_rows} == {"degC"}
    assert {row["loading_units"] for row in activity_rows} == {
        "mol_CO2_per_mol_MEA"
    }
    assert {row["value_units"] for row in activity_rows} == {"mole_fraction"}
    assert {row["classification"] for row in activity_rows} == {"imported"}
    assert {row["scoring_use"] for row in activity_rows} == {
        EXCLUDED_FROM_LITERATURE_SCORING
    }

    target_path = SOURCE_ROOT / "imported_target_role_snapshot.csv"
    target_columns, target_rows = _read_csv(target_path)
    target_source = f"{SOURCE_ARTIFACT_ROOT}/phase2_speciation_target_roles.csv"
    assert len(target_rows) == MIGRATED_SOURCE_TABLES[target_path.name]["row_count"]
    assert _projected_source_sha256(
        MIGRATED_SOURCE_TABLES[target_path.name]["original_columns"], target_rows
    ) == MIGRATED_SOURCE_TABLES[target_path.name]["source_sha256"]
    assert target_columns[-9:] == [
        "evidence_role",
        "source_artifact",
        "source_revision",
        "temperature_units",
        "MEA_weight_fraction_units",
        "loading_units",
        "value_units",
        "classification",
        "scoring_use",
    ]
    assert {row["evidence_role"] for row in target_rows} == {
        "imported_downstream_model_snapshot"
    }
    assert {row["source_artifact"] for row in target_rows} == {target_source}
    assert {row["source_revision"] for row in target_rows} == {SOURCE_REVISION}
    assert {row["temperature_units"] for row in target_rows} == {"degC"}
    assert {row["MEA_weight_fraction_units"] for row in target_rows} == {
        "mass_fraction"
    }
    assert {row["loading_units"] for row in target_rows} == {
        "mol_CO2_per_mol_MEA"
    }
    assert {row["value_units"] for row in target_rows} == {"mole_fraction"}
    assert {row["classification"] for row in target_rows} == {"imported"}
    assert {row["scoring_use"] for row in target_rows} == {
        EXCLUDED_FROM_LITERATURE_SCORING
    }


def test_unresolved_reference_rows_are_never_literature_observations() -> None:
    unresolved_path = SOURCE_ROOT / "unresolved_reference_observations.csv"
    unresolved_columns, unresolved_rows = _read_csv(unresolved_path)
    unresolved_source = f"{SOURCE_ARTIFACT_ROOT}/phase2_speciation_reference_points.csv"
    assert len(unresolved_rows) == MIGRATED_SOURCE_TABLES[unresolved_path.name]["row_count"]
    assert _projected_source_sha256(
        MIGRATED_SOURCE_TABLES[unresolved_path.name]["original_columns"], unresolved_rows
    ) == MIGRATED_SOURCE_TABLES[unresolved_path.name]["source_sha256"]
    assert unresolved_columns[-12:] == [
        "evidence_role",
        "source_artifact",
        "source_revision",
        "temperature_units",
        "MEA_weight_fraction_units",
        "loading_units",
        "value_units",
        "citation_status",
        "table_or_figure_locator",
        "classification",
        "scoring_use",
        "exclusion_reason",
    ]
    assert {row["evidence_role"] for row in unresolved_rows} == {
        "unresolved_reference_observation"
    }
    contract = json.loads(MIGRATION_CONTRACT_PATH.read_text(encoding="utf-8"))
    assert {row["evidence_role"] for row in unresolved_rows} <= set(
        contract["excluded_evidence_roles"]
    )
    assert not {row["evidence_role"] for row in unresolved_rows} & set(
        contract["evidence_roles"]
    )
    assert "literature_observation" not in {
        row["evidence_role"] for row in unresolved_rows
    }
    assert {row["source_artifact"] for row in unresolved_rows} == {unresolved_source}
    assert {row["source_revision"] for row in unresolved_rows} == {SOURCE_REVISION}
    assert {row["temperature_units"] for row in unresolved_rows} == {"degC"}
    assert {row["MEA_weight_fraction_units"] for row in unresolved_rows} == {
        "mass_fraction"
    }
    assert {row["loading_units"] for row in unresolved_rows} == {
        "mol_CO2_per_mol_MEA"
    }
    assert {row["value_units"] for row in unresolved_rows} == {"mole_fraction"}
    assert {row["citation_status"] for row in unresolved_rows} == {"unresolved"}
    assert {row["table_or_figure_locator"] for row in unresolved_rows} == {
        "unresolved"
    }
    assert {row["classification"] for row in unresolved_rows} == {"excluded"}
    assert {row["scoring_use"] for row in unresolved_rows} == {
        EXCLUDED_FROM_LITERATURE_SCORING
    }
    assert {row["exclusion_reason"] for row in unresolved_rows} == {
        UNRESOLVED_CITATION_REASON
    }
    assert not (SOURCE_ROOT / "literature_speciation_observations.csv").exists()


def test_source_manifest_preserves_source_identities_and_excludes_old_results() -> None:
    manifest_columns, manifest_rows = _read_csv(SOURCE_ROOT / "source_manifest.csv")
    assert manifest_columns == [
        "source_id",
        "source_path",
        "role",
        "source_artifact",
        "source_revision",
        "source_sha256",
        "classification",
        "scoring_use",
        "citation_status",
        "citation_source",
        "citation_locator",
        "basis_or_units",
        "notes",
    ]
    assert manifest_rows[0]["source_id"] == "phase1_speciation_curve"
    assert manifest_rows[0]["source_path"] == "source/phase1_speciation_curve.csv"
    assert manifest_rows[0]["role"] == "imported_downstream_model_snapshot"
    assert manifest_rows[0]["source_artifact"] == (
        "analyses/paper_validation/standalone_ce/figures/"
        "mea_reactive_speciation_oracle_comparison/source/phase1_speciation_curve.csv"
    )
    assert manifest_rows[0]["source_revision"] == "b593ca4c"
    assert manifest_rows[0]["source_sha256"] == (
        "a3fd41a358eddc48a759fe75b31e64850406b2b003db5239596d6379b48defa3"
    )
    assert hashlib.sha256((SOURCE_ROOT / "phase1_speciation_curve.csv").read_bytes()).hexdigest() == (
        manifest_rows[0]["source_sha256"]
    )
    assert manifest_rows[0]["classification"] == "imported"
    assert manifest_rows[0]["scoring_use"] == EXCLUDED_FROM_LITERATURE_SCORING
    assert manifest_rows[0]["citation_status"] == (
        "not_applicable_downstream_model_output"
    )
    assert manifest_rows[0]["citation_locator"] == ""

    by_id = {row["source_id"]: row for row in manifest_rows}
    assert set(by_id) == {
        "phase1_speciation_curve",
        "imported_downstream_model_snapshot",
        "imported_target_role_snapshot",
        "unresolved_reference_observations",
    } | {Path(source_name).stem for source_name in UNCHANGED_SOURCE_TABLES}
    for target_name, expected in MIGRATED_SOURCE_TABLES.items():
        source_name = expected["source_name"]
        row = by_id[target_name.removesuffix(".csv")]
        assert row["source_artifact"] == f"{SOURCE_ARTIFACT_ROOT}/{source_name}"
        assert row["source_revision"] == SOURCE_REVISION
        assert row["source_sha256"] == expected["source_sha256"]
        assert row["scoring_use"] == EXCLUDED_FROM_LITERATURE_SCORING

    for source_name, source_sha256 in UNCHANGED_SOURCE_TABLES.items():
        path = SOURCE_ROOT / source_name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source_sha256
        row = by_id[Path(source_name).stem]
        assert row["source_artifact"] == f"{SOURCE_ARTIFACT_ROOT}/{source_name}"
        assert row["source_revision"] == SOURCE_REVISION
        assert row["source_sha256"] == source_sha256
        assert row["role"] == "reaction_constant_source_evidence"
        assert row["classification"] == "unresolved_source_evidence"
        assert row["scoring_use"] == EXCLUDED_FROM_LITERATURE_SCORING
        assert row["citation_status"] == "unresolved_missing_local_primary_source"
        assert row["citation_source"] == MISSING_NASRIFAR_SOURCE_PATH
        assert row["citation_locator"] == ""

    assert by_id["phase2_reaction_constant_basis"]["basis_or_units"] == (
        "ln_K=A+B/T+C_ln(T)+D_T;T_K;mole_fraction_equilibrium_constant"
    )
    assert all(row["classification"] != "current_local_model_prediction" for row in manifest_rows)
    assert all("results/" not in row["source_path"] for row in manifest_rows)


def test_retained_source_locators_require_the_exact_repo_source_file() -> None:
    _, manifest_rows = _read_csv(SOURCE_ROOT / "source_manifest.csv")
    retained_rows = [
        row for row in manifest_rows if row["citation_status"] == "source_locator_retained"
    ]
    for row in retained_rows:
        assert row["citation_locator"]
        assert row["citation_source"]
        assert (REPO_ROOT / row["citation_source"]).is_file(), row["source_id"]

    reaction_source_rows = [
        row
        for row in manifest_rows
        if row["role"] == "reaction_constant_source_evidence"
    ]
    assert len(reaction_source_rows) == 3
    assert not (REPO_ROOT / MISSING_NASRIFAR_SOURCE_PATH).exists()
    assert {row["citation_status"] for row in reaction_source_rows} == {
        "unresolved_missing_local_primary_source"
    }


def test_phase1_manifest_lineage_resolves_to_hashed_git_object() -> None:
    _, manifest_rows = _read_csv(SOURCE_ROOT / "source_manifest.csv")
    phase1 = next(row for row in manifest_rows if row["source_id"] == "phase1_speciation_curve")
    source_object = subprocess.run(
        [
            "git",
            "show",
            f"{phase1['source_revision']}:{phase1['source_artifact']}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    assert source_object.returncode == 0, source_object.stderr.decode("utf-8")
    assert hashlib.sha256(source_object.stdout).hexdigest() == phase1["source_sha256"]
