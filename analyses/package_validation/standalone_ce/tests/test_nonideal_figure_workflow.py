from __future__ import annotations

import ast
import copy
import csv
import hashlib
import io
import itertools
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "package_validation" / "standalone_ce"
FIGURE_ROOT = ANALYSIS_ROOT / "figures" / "mea_reactive_speciation_oracle_comparison"
MIGRATION_CONTRACT_PATH = FIGURE_ROOT / "source" / "migration_contract.json"
SOURCE_ROOT = FIGURE_ROOT / "source"
MODEL_INPUT_ROOT = SOURCE_ROOT / "model_input"
INPUT_EVIDENCE_LEDGER_PATH = MODEL_INPUT_ROOT / "input_evidence_ledger.csv"
REACTION_EVIDENCE_LEDGER_PATH = SOURCE_ROOT / "reaction_input_evidence_ledger.csv"

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

SPECIES_ORDER = [
    "CO2",
    "MEA",
    "H2O",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
]
EXPECTED_INTERACTION_RECORD_IDS = [
    f"interaction.{matrix_name}.{component_a}__{component_b}"
    for matrix_name in ("k_ij", "l_ij", "k_hb_ij")
    for index, component_a in enumerate(SPECIES_ORDER)
    for component_b in SPECIES_ORDER[index + 1 :]
]
NAMED_INPUT_RECORDS = {
    "pure.CO2.m",
    "pure.CO2.relative_permittivity",
    "pure.MEA.relative_permittivity",
    "pure.CO2.f_solv",
    "pure.MEA.f_solv",
    "formulation.figiel_empirical_relative_permittivity",
    "formulation.figiel_dielectric_saturation",
    "formulation.figiel_born_diameter",
    "formulation.figiel_solvation_factor",
    "correlation.H2O.sigma",
    "formulation.ion_dispersion_mapping",
}
BLOCKED_NAMED_INPUT_RECORDS = NAMED_INPUT_RECORDS - {"correlation.H2O.sigma"}
FIGIEL_DOMAIN_RECORDS = {
    "formulation.figiel_empirical_relative_permittivity",
    "formulation.figiel_dielectric_saturation",
    "formulation.figiel_born_diameter",
    "formulation.figiel_solvation_factor",
}
HELD_2008_SOURCE = (
    "docs/papers/md/ePC-SAFT-Literature/Held, Cameretti, Sadowski - 2008 - "
    "Modeling aqueous electrolyte solutions. Part 1. Fully dissociated.md"
)
FIGIEL_2025_SOURCE = (
    "docs/papers/md/ePC-SAFT-Literature/Figiel, Yu, Held - 2025 - Predicting "
    "Thermodynamic Properties of Ions in Single Solvents and in Mixe.md"
)
BAYGI_2015_SOURCE = (
    "docs/papers/md/MEA/Baygi and Pahlavanzadeh - 2015 - Application of the "
    "PC-SAFT equation of state for modeling CO2 solub.md"
)
PHASE2_REACTION_SOURCE = (
    "analyses/package_validation/standalone_ce/figures/"
    "mea_reactive_speciation_oracle_comparison/source/"
    "phase2_activity_constant_candidates.csv"
)
EXPECTED_NAMED_RECORD_FIELDS = {
    "pure.CO2.m": {
        "historical_value": "historical=2.079;traceable=2.0729",
        "evidence_status": "blocked_conflicting_value",
        "source_path": BAYGI_2015_SOURCE,
        "source_locator": "Table 2 line 187",
        "supported_temperature_min_k": "",
        "supported_temperature_max_k": "",
        "current_mapping": "unresolved",
        "blocker_reason": "historical 2.079 conflicts with traceable literature 2.0729",
    },
    "pure.CO2.relative_permittivity": {
        "historical_value": "1.4122",
        "evidence_status": "blocked_missing_retained_source",
        "source_path": "",
        "source_locator": "",
        "supported_temperature_min_k": "",
        "supported_temperature_max_k": "",
        "current_mapping": "unresolved",
        "blocker_reason": "no retained source supports CO2 relative permittivity 1.4122",
    },
    "pure.MEA.relative_permittivity": {
        "historical_value": "32",
        "evidence_status": "blocked_missing_retained_source",
        "source_path": "",
        "source_locator": "",
        "supported_temperature_min_k": "",
        "supported_temperature_max_k": "",
        "current_mapping": "unresolved",
        "blocker_reason": "no retained source supports MEA relative permittivity 32",
    },
    "pure.CO2.f_solv": {
        "historical_value": "1",
        "evidence_status": "blocked_missing_fitted_or_literature_receipt",
        "source_path": "",
        "source_locator": "",
        "supported_temperature_min_k": "",
        "supported_temperature_max_k": "",
        "current_mapping": "unresolved",
        "blocker_reason": (
            "CO2 neutral f_solv=1 has neither a fitted receipt nor literature evidence"
        ),
    },
    "pure.MEA.f_solv": {
        "historical_value": "1",
        "evidence_status": "blocked_missing_fitted_or_literature_receipt",
        "source_path": "",
        "source_locator": "",
        "supported_temperature_min_k": "",
        "supported_temperature_max_k": "",
        "current_mapping": "unresolved",
        "blocker_reason": (
            "MEA neutral f_solv=1 has neither a fitted receipt nor literature evidence"
        ),
    },
    "formulation.figiel_empirical_relative_permittivity": {
        "historical_value": "epsilon_r_mix=epsilon_r_salt_free/(1+7.01*x_ion)",
        "evidence_status": "blocked_temperature_domain_298.15K_only",
        "source_path": FIGIEL_2025_SOURCE,
        "source_locator": (
            "Eq. 11 lines 140-149; tested-temperature limitation lines 152-161"
        ),
        "supported_temperature_min_k": "298.15",
        "supported_temperature_max_k": "298.15",
        "current_mapping": "empirical_relative_permittivity",
        "blocker_reason": (
            "the empirical rule was investigated only at 298.15 K and does not prove "
            "293.15-353.15 K"
        ),
    },
    "formulation.figiel_dielectric_saturation": {
        "historical_value": "ion_relative_permittivity=8;dielectric_saturation=true",
        "evidence_status": "blocked_temperature_domain_298.15K_only",
        "source_path": FIGIEL_2025_SOURCE,
        "source_locator": (
            "SSM+DS formulation lines 78-93; study scope at 298.15 K lines 389-398"
        ),
        "supported_temperature_min_k": "298.15",
        "supported_temperature_max_k": "298.15",
        "current_mapping": "dielectric_saturation",
        "blocker_reason": "retained DS evidence does not cover 293.15-353.15 K",
    },
    "formulation.figiel_born_diameter": {
        "historical_value": "branch ion-specific d_born snapshot",
        "evidence_status": "blocked_temperature_domain_298.15K_only",
        "source_path": FIGIEL_2025_SOURCE,
        "source_locator": (
            "Born/SSM+DS discussion lines 78-98; Table 3 lines 297-313; study scope "
            "lines 389-398"
        ),
        "supported_temperature_min_k": "298.15",
        "supported_temperature_max_k": "298.15",
        "current_mapping": "born_diameter_records",
        "blocker_reason": (
            "retained Born/SSM+DS evidence does not establish active records across "
            "293.15-353.15 K"
        ),
    },
    "formulation.figiel_solvation_factor": {
        "historical_value": "H2O=1.5;ions=1;CO2=1;MEA=1",
        "evidence_status": "blocked_temperature_domain_298.15K_only",
        "source_path": FIGIEL_2025_SOURCE,
        "source_locator": (
            "solvation-parameter fitting discussion lines 270-285; Table 2 lines "
            "286-296; study scope lines 389-398"
        ),
        "supported_temperature_min_k": "298.15",
        "supported_temperature_max_k": "298.15",
        "current_mapping": "solvation_factor_records",
        "blocker_reason": (
            "Figiel evidence is 298.15 K only and does not validate the historical "
            "CO2/MEA neutral values"
        ),
    },
    "correlation.H2O.sigma": {
        "historical_value": (
            "sigma_A=2.7927+10.11*exp(-0.01775*T_K)-1.417*exp(-0.01146*T_K)"
        ),
        "evidence_status": "accepted_traceable_literature",
        "gate_status": "accepted",
        "source_path": HELD_2008_SOURCE,
        "source_locator": "Table 1 lines 111-126; Eq. 7 and domain lines 129-137",
        "supported_temperature_min_k": "273.15",
        "supported_temperature_max_k": "373.15",
        "current_mapping": "double_exponential_sigma_correlation",
        "blocker_reason": "",
    },
    "formulation.ion_dispersion_mapping": {
        "historical_value": "historical runtime behavior not explicitly configured",
        "evidence_status": "blocked_no_exact_current_formulation_mapping",
        "source_path": "",
        "source_locator": "",
        "supported_temperature_min_k": "",
        "supported_temperature_max_k": "",
        "current_mapping": "unresolved",
        "blocker_reason": (
            "old ion-dispersion behavior has no exact one-to-one mapping to a current "
            "typed formulation choice"
        ),
    },
}
MATRIX_HISTORICAL_VALUES = {
    "k_ij": {
        tuple(sorted(("MEA", "H2O"))): "-0.052",
        tuple(sorted(("H2O", "CO3^2-"))): "-0.25",
        tuple(sorted(("H2O", "H3O+"))): "0.25",
        tuple(sorted(("H2O", "OH-"))): "-0.25",
        tuple(sorted(("MEAH+", "MEACOO-"))): "-0.00201813457644",
    },
    "l_ij": {},
    "k_hb_ij": {},
}
REACTION_RECORD_IDS = {f"reaction.{reaction_id}" for reaction_id in ("R1", "R2", "R3", "R4", "R5")}
REACTION_COMMON_EXPECTED_FIELDS = {
    "historical_expression": "ln_K=A+B/T_K+C*ln(T_K)+D*T_K",
    "historical_source_path": PHASE2_REACTION_SOURCE,
    "claimed_primary_source_path": MISSING_NASRIFAR_SOURCE_PATH,
    "primary_source_status": "blocked_missing_local_nasrifar_primary_source",
    "baygi_source_path": BAYGI_2015_SOURCE,
    "baygi_source_locator": (
        "Table 4 lines 263-275; Eq. 17 lines 398-408; Eq. 18 lines 409-417"
    ),
    "execution_temperature_min_k": "293.15",
    "execution_temperature_max_k": "353.15",
    "standard_state_status": "blocked_exact_nonideal_mapping_unverified",
    "gate_status": "blocked",
    "historical_snapshot_use": "audit_only_non_executable",
}
EXPECTED_REACTION_RECORD_FIELDS = {
    "reaction.R1": {
        **REACTION_COMMON_EXPECTED_FIELDS,
        "historical_A": "132.899",
        "historical_B": "-13445.9",
        "historical_C": "-22.4773",
        "historical_D": "0",
        "historical_source_locator": "row R1",
        "baygi_A": "132.899",
        "baygi_B": "-13445.9",
        "baygi_C": "22.4773",
        "baygi_D": "0",
        "baygi_temperature_min_k": "273.15",
        "baygi_temperature_max_k": "498.15",
        "baygi_basis_evidence": "Baygi reports K_X under the ideal a_i=x_i assumption",
        "baygi_comparison": "conflict:C historical=-22.4773 Baygi=22.4773",
        "temperature_domain_status": "blocked_coefficient_conflict_prevents_domain_use",
        "blocker_reason": (
            "Baygi coefficient conflict prevents its 273.15-498.15 K domain from "
            "validating the historical correlation; claimed Nasrifar source is absent; "
            "exact nonideal standard-state mapping is unverified"
        ),
    },
    "reaction.R2": {
        **REACTION_COMMON_EXPECTED_FIELDS,
        "historical_A": "231.456",
        "historical_B": "-12092.1",
        "historical_C": "-36.7816",
        "historical_D": "0",
        "historical_source_locator": "row R2",
        "baygi_A": "231.465",
        "baygi_B": "-12092.10",
        "baygi_C": "-36.7816",
        "baygi_D": "0",
        "baygi_temperature_min_k": "273.15",
        "baygi_temperature_max_k": "498.15",
        "baygi_basis_evidence": "Baygi reports K_X under the ideal a_i=x_i assumption",
        "baygi_comparison": "conflict:A historical=231.456 Baygi=231.465",
        "temperature_domain_status": "blocked_coefficient_conflict_prevents_domain_use",
        "blocker_reason": (
            "Baygi coefficient conflict prevents its 273.15-498.15 K domain from "
            "validating the historical correlation; claimed Nasrifar source is absent; "
            "exact nonideal standard-state mapping is unverified"
        ),
    },
    "reaction.R3": {
        **REACTION_COMMON_EXPECTED_FIELDS,
        "historical_A": "216.049",
        "historical_B": "-12431.7",
        "historical_C": "-35.4819",
        "historical_D": "0",
        "historical_source_locator": "row R3",
        "baygi_A": "216.049",
        "baygi_B": "-12431.70",
        "baygi_C": "-35.4819",
        "baygi_D": "0",
        "baygi_temperature_min_k": "273.15",
        "baygi_temperature_max_k": "498.15",
        "baygi_basis_evidence": "Baygi reports K_X under the ideal a_i=x_i assumption",
        "baygi_comparison": "coefficients_match",
        "temperature_domain_status": "accepted_traceable_baygi_domain",
        "blocker_reason": (
            "Baygi coefficients match and its 273.15-498.15 K domain covers execution; "
            "overall gate remains blocked because the claimed Nasrifar source is absent "
            "and exact nonideal standard-state mapping is unverified"
        ),
    },
    "reaction.R4": {
        **REACTION_COMMON_EXPECTED_FIELDS,
        "historical_A": "2.8898",
        "historical_B": "-3635.09",
        "historical_C": "0",
        "historical_D": "0",
        "historical_source_locator": "row R4",
        "baygi_A": "-1.8652",
        "baygi_B": "-1545.3",
        "baygi_C": "0",
        "baygi_D": "0",
        "baygi_temperature_min_k": "293.15",
        "baygi_temperature_max_k": "323.15",
        "baygi_basis_evidence": (
            "Baygi reports K_X and an explicit R4 K_m-to-K_x conversion; ideal "
            "a_i=x_i assumption"
        ),
        "baygi_comparison": (
            "conflict:A,B historical=2.8898,-3635.09 Baygi=-1.8652,-1545.3"
        ),
        "temperature_domain_status": (
            "blocked_coefficient_conflict_and_domain_ends_at_323.15K"
        ),
        "blocker_reason": (
            "Baygi coefficients conflict and its domain ends at 323.15 K; claimed "
            "Nasrifar source is absent; exact nonideal standard-state mapping is "
            "unverified"
        ),
    },
    "reaction.R5": {
        **REACTION_COMMON_EXPECTED_FIELDS,
        "historical_A": "2.1211",
        "historical_B": "-8189.38",
        "historical_C": "0",
        "historical_D": "-0.007484",
        "historical_source_locator": "row R5",
        "baygi_A": "2.1211",
        "baygi_B": "-8189.38",
        "baygi_C": "0",
        "baygi_D": "-0.007484",
        "baygi_temperature_min_k": "273.15",
        "baygi_temperature_max_k": "323.15",
        "baygi_basis_evidence": "Baygi reports K_X under the ideal a_i=x_i assumption",
        "baygi_comparison": "coefficients_match",
        "temperature_domain_status": "blocked_baygi_domain_ends_at_323.15K",
        "blocker_reason": (
            "Baygi coefficients match but its domain ends at 323.15 K; claimed Nasrifar "
            "source is absent; exact nonideal standard-state mapping is unverified"
        ),
    },
}
TASK_3_BLOCKED_STATUS = "blocked_execution_stops_before_tasks_4_through_10"


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


def _fail(record_id: str, detail: str) -> None:
    raise AssertionError(f"{record_id}: {detail}")


def _validate_input_evidence_rows(rows: list[dict[str, str]]) -> None:
    record_ids = [row["record_id"] for row in rows]
    if len(record_ids) != len(set(record_ids)):
        _fail("input_evidence_ledger", "duplicate record_id")

    by_id = {row["record_id"]: row for row in rows}
    if not NAMED_INPUT_RECORDS <= set(by_id):
        missing = sorted(NAMED_INPUT_RECORDS - set(by_id))[0]
        _fail(missing, "missing named input record")
    actual_named_ids = {
        record_id for record_id in record_ids if not record_id.startswith("interaction.")
    }
    if actual_named_ids != NAMED_INPUT_RECORDS:
        _fail("input_evidence_ledger", "unexpected named input record set")

    for record_id, expected_fields in EXPECTED_NAMED_RECORD_FIELDS.items():
        row = by_id[record_id]
        for field, expected_value in expected_fields.items():
            if row[field] != expected_value:
                _fail(record_id, f"{field} must be {expected_value!r}")
        if (
            row["execution_temperature_min_k"],
            row["execution_temperature_max_k"],
        ) != ("293.15", "353.15"):
            _fail(record_id, "execution domain must remain 293.15-353.15 K")

    for record_id in sorted(BLOCKED_NAMED_INPUT_RECORDS):
        row = by_id[record_id]
        if row["gate_status"] != "blocked":
            _fail(record_id, "named blocker must remain blocked")
        if not row["blocker_reason"]:
            _fail(record_id, "named blocker requires an exact reason")
        if row["historical_snapshot_use"] != "audit_only_non_executable":
            _fail(record_id, "historical snapshot must remain audit-only")

    for record_id in sorted(FIGIEL_DOMAIN_RECORDS):
        row = by_id[record_id]
        if (
            row["supported_temperature_min_k"],
            row["supported_temperature_max_k"],
        ) != ("298.15", "298.15"):
            _fail(record_id, "Figiel evidence must remain limited to 298.15 K")

    water_sigma = by_id["correlation.H2O.sigma"]
    if water_sigma["gate_status"] != "accepted":
        _fail(water_sigma["record_id"], "traceable accepted record changed status")
    if water_sigma["evidence_status"] != "accepted_traceable_literature":
        _fail(water_sigma["record_id"], "accepted record requires literature evidence")
    if water_sigma["source_path"] != HELD_2008_SOURCE:
        _fail(water_sigma["record_id"], "unexpected source path")
    if water_sigma["source_locator"] != "Table 1 lines 111-126; Eq. 7 and domain lines 129-137":
        _fail(water_sigma["record_id"], "unexpected source locator")
    if (
        water_sigma["supported_temperature_min_k"],
        water_sigma["supported_temperature_max_k"],
    ) != ("273.15", "373.15"):
        _fail(water_sigma["record_id"], "accepted domain must cover 0-100 degC")
    if water_sigma["historical_value"] != (
        "sigma_A=2.7927+10.11*exp(-0.01775*T_K)-1.417*exp(-0.01146*T_K)"
    ):
        _fail(water_sigma["record_id"], "accepted correlation changed")

    expected_interaction_ids: set[str] = set()
    for matrix_name in ("k_ij", "l_ij", "k_hb_ij"):
        for index, component_a in enumerate(SPECIES_ORDER):
            for component_b in SPECIES_ORDER[index + 1 :]:
                record_id = f"interaction.{matrix_name}.{component_a}__{component_b}"
                expected_interaction_ids.add(record_id)
                row = by_id.get(record_id)
                if row is None:
                    _fail(record_id, "missing unique off-diagonal pair")
                pair = tuple(sorted((component_a, component_b)))
                expected_value = MATRIX_HISTORICAL_VALUES[matrix_name].get(pair, "0")
                if row["historical_value"] != expected_value:
                    _fail(record_id, f"historical value must be {expected_value}")
                expected_status = (
                    "blocked_source_required"
                    if expected_value != "0"
                    else "blocked_unverified_structural_zero"
                )
                if row["evidence_status"] != expected_status:
                    _fail(record_id, f"evidence_status must be {expected_status}")
                if row["gate_status"] != "blocked":
                    _fail(record_id, "interaction pair must remain blocked")
                if row["historical_snapshot_use"] != "audit_only_non_executable":
                    _fail(record_id, "historical matrix value must remain audit-only")

    actual_interaction_ids = {
        record_id for record_id in record_ids if record_id.startswith("interaction.")
    }
    if actual_interaction_ids != expected_interaction_ids:
        unexpected = sorted(actual_interaction_ids - expected_interaction_ids)
        _fail(unexpected[0] if unexpected else "interaction_evidence", "unexpected pair set")
    if len(actual_interaction_ids) != 108:
        _fail("interaction_evidence", "expected 108 unique off-diagonal matrix rows")


def _validate_reaction_evidence_rows(rows: list[dict[str, str]]) -> None:
    record_ids = [row["record_id"] for row in rows]
    if len(record_ids) != len(set(record_ids)):
        _fail("reaction_input_evidence_ledger", "duplicate record_id")
    if set(record_ids) != REACTION_RECORD_IDS:
        missing = sorted(REACTION_RECORD_IDS - set(record_ids))
        _fail(missing[0] if missing else "reaction_input_evidence_ledger", "unexpected reaction set")

    for row in rows:
        record_id = row["record_id"]
        for field, expected_value in EXPECTED_REACTION_RECORD_FIELDS[record_id].items():
            if row[field] != expected_value:
                _fail(record_id, f"{field} must be {expected_value!r}")
        if row["gate_status"] != "blocked":
            _fail(record_id, "reaction record must remain blocked")
        if row["primary_source_status"] != "blocked_missing_local_nasrifar_primary_source":
            _fail(record_id, "Nasrifar primary source blocker changed")
        if row["standard_state_status"] != "blocked_exact_nonideal_mapping_unverified":
            _fail(record_id, "standard-state mapping blocker changed")
        if row["historical_snapshot_use"] != "audit_only_non_executable":
            _fail(record_id, "historical reaction coefficients must remain audit-only")
        if row["execution_temperature_min_k"] != "293.15" or row[
            "execution_temperature_max_k"
        ] != "353.15":
            _fail(record_id, "execution domain changed")
        if not row["baygi_comparison"]:
            _fail(record_id, "Baygi evidence/conflict comparison is required")


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


def test_scientific_input_gate_records_named_blockers_and_one_accepted_correlation() -> None:
    _, input_rows = _read_csv(INPUT_EVIDENCE_LEDGER_PATH)
    _validate_input_evidence_rows(input_rows)
    by_id = {row["record_id"]: row for row in input_rows}
    assert by_id["pure.CO2.m"]["historical_value"] == (
        "historical=2.079;traceable=2.0729"
    )
    assert by_id["pure.CO2.relative_permittivity"]["historical_value"] == "1.4122"
    assert by_id["pure.MEA.relative_permittivity"]["historical_value"] == "32"
    assert by_id["pure.CO2.f_solv"]["historical_value"] == "1"
    assert by_id["pure.MEA.f_solv"]["historical_value"] == "1"
    assert by_id["formulation.ion_dispersion_mapping"]["evidence_status"] == (
        "blocked_no_exact_current_formulation_mapping"
    )


@pytest.mark.parametrize(
    ("record_id", "field"),
    [
        (record_id, field)
        for record_id, expected_fields in EXPECTED_NAMED_RECORD_FIELDS.items()
        for field in expected_fields
    ]
    + [(record_id, "gate_status") for record_id in BLOCKED_NAMED_INPUT_RECORDS]
    + [
        (record_id, field)
        for record_id in NAMED_INPUT_RECORDS
        for field in ("execution_temperature_min_k", "execution_temperature_max_k")
    ],
)
def test_named_input_material_evidence_mutations_fail_with_exact_record_id(
    record_id: str, field: str
) -> None:
    _, input_rows = _read_csv(INPUT_EVIDENCE_LEDGER_PATH)
    mutated_rows = copy.deepcopy(input_rows)
    row = next(candidate for candidate in mutated_rows if candidate["record_id"] == record_id)
    row[field] = "__mutated__"
    with pytest.raises(AssertionError, match=rf"^{re.escape(record_id)}:"):
        _validate_input_evidence_rows(mutated_rows)


def test_every_historical_interaction_cell_is_a_non_executable_evidence_record() -> None:
    _, input_rows = _read_csv(INPUT_EVIDENCE_LEDGER_PATH)
    interaction_rows = [
        row for row in input_rows if row["record_id"].startswith("interaction.")
    ]
    assert len(interaction_rows) == 108
    assert sum(row["historical_value"] != "0" for row in interaction_rows) == 5
    assert sum(row["historical_value"] == "0" for row in interaction_rows) == 103
    _validate_input_evidence_rows(input_rows)


@pytest.mark.parametrize("record_id", EXPECTED_INTERACTION_RECORD_IDS)
def test_interaction_status_mutations_fail_with_exact_record_id(record_id: str) -> None:
    _, input_rows = _read_csv(INPUT_EVIDENCE_LEDGER_PATH)
    mutated_rows = copy.deepcopy(input_rows)
    row = next(candidate for candidate in mutated_rows if candidate["record_id"] == record_id)
    row["evidence_status"] = "accepted"
    with pytest.raises(AssertionError, match=rf"^{re.escape(record_id)}:"):
        _validate_input_evidence_rows(mutated_rows)


def test_reaction_input_gate_records_exact_row_specific_evidence_rationales() -> None:
    _, reaction_rows = _read_csv(REACTION_EVIDENCE_LEDGER_PATH)
    _validate_reaction_evidence_rows(reaction_rows)
    by_id = {row["record_id"]: row for row in reaction_rows}
    assert by_id["reaction.R1"]["baygi_comparison"] == (
        "conflict:C historical=-22.4773 Baygi=22.4773"
    )
    assert by_id["reaction.R2"]["baygi_comparison"] == (
        "conflict:A historical=231.456 Baygi=231.465"
    )
    assert by_id["reaction.R3"]["baygi_comparison"] == "coefficients_match"
    assert by_id["reaction.R4"]["baygi_comparison"] == (
        "conflict:A,B historical=2.8898,-3635.09 Baygi=-1.8652,-1545.3"
    )
    assert by_id["reaction.R5"]["baygi_comparison"] == "coefficients_match"
    assert by_id["reaction.R1"]["temperature_domain_status"] == (
        "blocked_coefficient_conflict_prevents_domain_use"
    )
    assert by_id["reaction.R2"]["temperature_domain_status"] == (
        "blocked_coefficient_conflict_prevents_domain_use"
    )
    assert by_id["reaction.R3"]["temperature_domain_status"] == (
        "accepted_traceable_baygi_domain"
    )
    assert by_id["reaction.R4"]["temperature_domain_status"] == (
        "blocked_coefficient_conflict_and_domain_ends_at_323.15K"
    )
    assert by_id["reaction.R5"]["temperature_domain_status"] == (
        "blocked_baygi_domain_ends_at_323.15K"
    )
    assert {row["gate_status"] for row in reaction_rows} == {"blocked"}


@pytest.mark.parametrize(
    ("record_id", "field"),
    [
        (record_id, field)
        for record_id, expected_fields in EXPECTED_REACTION_RECORD_FIELDS.items()
        for field in expected_fields
    ],
)
def test_reaction_material_evidence_mutations_fail_with_exact_record_id(
    record_id: str, field: str
) -> None:
    _, reaction_rows = _read_csv(REACTION_EVIDENCE_LEDGER_PATH)
    mutated_rows = copy.deepcopy(reaction_rows)
    row = next(candidate for candidate in mutated_rows if candidate["record_id"] == record_id)
    row[field] = "__mutated__"
    with pytest.raises(AssertionError, match=rf"^{re.escape(record_id)}:"):
        _validate_reaction_evidence_rows(mutated_rows)


def test_incomplete_scientific_evidence_stops_executable_migration_tasks() -> None:
    readme_path = MODEL_INPUT_ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    assert TASK_3_BLOCKED_STATUS in readme
    assert "Tasks 4-10 must not execute" in readme
    assert not (MODEL_INPUT_ROOT / "model_configuration.json").exists()
    assert not (MODEL_INPUT_ROOT / "parameter_set.json").exists()
