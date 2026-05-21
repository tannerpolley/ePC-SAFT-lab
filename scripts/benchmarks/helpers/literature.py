from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter, OrderedDict
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from epcsaft.runtime.capability_evidence import TEST_SLICES, VALIDATION_LANES
from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft.runtime import __git_commit__, __version__

REPO_ROOT = Path(__file__).resolve().parents[3]

EXECUTABLE = "executable"
BLOCKED = "blocked"
ALLOWED_STATUSES = {EXECUTABLE, BLOCKED}
REGISTRY_ONLY = "registry_only"
EXECUTE_EXECUTABLE_CASES = "execute_executable_cases"


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    title: str
    source: str
    model_setup: dict[str, Any]
    input_records: tuple[str, ...]
    expected: dict[str, Any] | None
    tolerances: dict[str, Any] | None
    command: str
    status: str
    package_surface: tuple[str, ...]
    validation_paths: tuple[str, ...]
    notes: str
    blocked_by_issue: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["input_records"] = list(self.input_records)
        payload["package_surface"] = list(self.package_surface)
        payload["validation_paths"] = list(self.validation_paths)
        return payload


def _git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return str(__git_commit__)
    commit = completed.stdout.strip()
    return commit or str(__git_commit__)


def _tail_text(text: str, *, max_lines: int = 12) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[-max_lines:])


def _run_case_command(command: str) -> dict[str, Any]:
    started = time.perf_counter()
    env = os.environ.copy()
    apply_native_runtime_env(env)
    completed = subprocess.run(
        ["cmd.exe", "/c", command],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    duration_seconds = time.perf_counter() - started
    return {
        "returncode": completed.returncode,
        "duration_seconds": duration_seconds,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _validate_case_contract(entry: dict[str, Any]) -> None:
    if entry["status"] != EXECUTABLE:
        return
    if entry["expected"] is None or entry["tolerances"] is None:
        raise ValueError(
            f"Executable literature benchmark case {entry['id']!r} is missing expected values or tolerances."
        )
    if not entry["command"]:
        raise ValueError(f"Executable literature benchmark case {entry['id']!r} is missing a command.")
    if not entry["validation_paths"]:
        raise ValueError(f"Executable literature benchmark case {entry['id']!r} is missing validation paths.")


LITERATURE_CASES: OrderedDict[str, BenchmarkCase] = OrderedDict(
    (
        (
            "gross_sadowski_pure_nonassociating",
            BenchmarkCase(
                id="gross_sadowski_pure_nonassociating",
                title="Gross/Sadowski pure PC-SAFT nonassociating parameters",
                source="Gross, Sadowski 2001 Table 2 neutral hydrocarbon reference",
                model_setup={
                    "route": "native neutral pure-parameter objective contract",
                    "dataset": "tests.support.regression_cases.HYDROCARBON_REFERENCE",
                },
                input_records=(
                    "tests/api/frontend",
                    "tests/support/regression_cases.py",
                ),
                expected={
                    "objective_reference": 9.701615164740784e-06,
                    "jacobian_shape": [8, 3],
                },
                tolerances={
                    "objective_rel": 2.0e-4,
                    "objective_abs": 0.0,
                },
                command="uv run python run_pytest.py tests/api/frontend/test_regression.py::test_regression_hydrocarbon_anchor_routes_through_new_object_api -q",
                status=EXECUTABLE,
                package_surface=(
                    "tests/api/frontend",
                    "scripts/validation/validate_hydrocarbon_regression.py",
                ),
                validation_paths=("tests/api/frontend",),
                notes="Current coverage is executable, numeric, and package-owned, but not yet routed through the issue #119 release-gate suite.",
            ),
        ),
        (
            "gross_sadowski_associating_systems",
            BenchmarkCase(
                id="gross_sadowski_associating_systems",
                title="Gross/Sadowski associating systems",
                source="Repo-contained ethanol/water 100 kPa associating-binary benchmark used as the current package-owned surrogate",
                model_setup={
                    "route": "native Ceres binary k_ij regression",
                    "dataset": "2012_Held",
                    "surrogate": "ethanol/water 100 kPa VLE",
                },
                input_records=(
                    "data/reference/regression/binary/ethanol_water_jced2021_vle_100kpa.csv",
                ),
                expected={
                    "binary_vle_fugacity_balance_max": 0.04,
                    "paper_kij_abs_error_max": 0.01,
                },
                tolerances={
                    "binary_vle_fugacity_balance_abs": 0.04,
                    "paper_kij_abs": 0.01,
                },
                command="uv run python scripts/benchmarks/benchmark_literature_suite.py --case gross_sadowski_associating_systems --registry-only",
                status=BLOCKED,
                package_surface=("scripts/benchmarks/benchmark_literature_suite.py",),
                validation_paths=("data/reference/regression/binary/ethanol_water_jced2021_vle_100kpa.csv",),
                notes="The ethanol/water source data remains available, but paper-surrogate regression is no longer a pytest proof gate.",
                blocked_by_issue=119,
            ),
        ),
        (
            "baygi_mea_association_and_mea_water_binary",
            BenchmarkCase(
                id="baygi_mea_association_and_mea_water_binary",
                title="Baygi MEA association and MEA-water binary baseline",
                source="Baygi and Pahlavanzadeh 2015 pure MEA association plus the missing normalized MEA/water binary VLE baseline",
                model_setup={
                    "route": "native pure associating regression contract for MEA",
                    "missing_piece": "repo-contained normalized MEA/water binary benchmark fixture",
                },
                input_records=(
                    "analyses/paper_validation/application/2015_baygi/scripts/run_all.py",
                ),
                expected=None,
                tolerances=None,
                command="uv run python scripts/benchmarks/benchmark_literature_suite.py --case baygi_mea_association_and_mea_water_binary",
                status=BLOCKED,
                package_surface=(
                    "analyses/paper_validation/application/2015_baygi/scripts/run_all.py",
                ),
                validation_paths=("analyses/paper_validation/application/2015_baygi/scripts/run_all.py",),
                notes="Pure MEA association is executable now, but the combined issue #119 family remains blocked because no normalized repo-contained MEA/water binary VLE benchmark fixture is currently present.",
                blocked_by_issue=119,
            ),
        ),
        (
            "cameretti_held_aqueous_electrolyte_density_miac",
            BenchmarkCase(
                id="cameretti_held_aqueous_electrolyte_density_miac",
                title="Cameretti/Held aqueous electrolyte density and MIAC",
                source="Held/Cameretti aqueous NaCl density, osmotic, and MIAC references",
                model_setup={
                    "route": "liquid-electrolyte state property benchmark",
                    "dataset": "2014_Held",
                    "state": "aqueous NaCl at 298.15 K and 101325 Pa",
                },
                input_records=(
                    "data/reference/osmotic/water/NaCl.csv",
                    "data/reference/MIAC/water/water-NaCl.csv",
                ),
                expected={
                    "osmotic_molality_probe": 0.5,
                    "miac_molality_probe": 0.5,
                },
                tolerances={
                    "osmotic_abs": 0.03,
                    "miac_abs": 0.08,
                },
                command="uv run python analyses/paper_validation/native/2014_held/scripts/run_all.py",
                status=EXECUTABLE,
                package_surface=("analyses/paper_validation/native/2014_held/scripts/run_all.py",),
                validation_paths=("analyses/paper_validation/native/2014_held/scripts/run_all.py",),
                notes="This family is explicit analysis evidence and is intentionally outside pytest.",
            ),
        ),
        (
            "held_mixed_solvent_density_osmotic_miac",
            BenchmarkCase(
                id="held_mixed_solvent_density_osmotic_miac",
                title="Held alcohol/salt mixed-solvent density, osmotic coefficient, and MIAC",
                source="Held mixed water/methanol NaCl literature reference rows",
                model_setup={
                    "route": "mixed-solvent electrolyte state property benchmark",
                    "dataset": "2012_Held",
                    "state": "water/methanol/NaCl at 298.15 K and 101325 Pa",
                },
                input_records=("data/reference/MIAC/water-methanol/water-methanol-NaCl.csv",),
                expected={
                    "miac_molality_probe": 0.0125,
                    "osmotic_range": [0.0, 2.0],
                },
                tolerances={
                    "miac_abs": 0.08,
                    "osmotic_range_abs": None,
                },
                command="uv run python analyses/paper_validation/native/2012_held/scripts/run_all.py",
                status=EXECUTABLE,
                package_surface=("analyses/paper_validation/native/2012_held/scripts/run_all.py",),
                validation_paths=("analyses/paper_validation/native/2012_held/scripts/run_all.py",),
                notes="This mixed-solvent Held family is explicit analysis evidence and is intentionally outside pytest.",
            ),
        ),
        (
            "bulow_ascani_dielectric_born",
            BenchmarkCase(
                id="bulow_ascani_dielectric_born",
                title="Bulow/Ascani concentration-dependent dielectric and Born behavior",
                source="Bulow/Ascani/Held advanced Born and dielectric parameter/data extraction plus Figure 2025 analysis assets",
                model_setup={
                    "route": "parameter/data validation and figure-owned analysis assets",
                    "datasets": ["2020_Bulow", "2021_Bulow", "2025_Figiel"],
                },
                input_records=(
                    "scripts/data/extract_paper_parameter_csvs.py",
                    "analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",
                ),
                expected=None,
                tolerances=None,
                command="uv run python scripts/benchmarks/benchmark_literature_suite.py --case bulow_ascani_dielectric_born",
                status=BLOCKED,
                package_surface=(
                    "scripts/data/extract_paper_parameter_csvs.py",
                    "analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",
                ),
                validation_paths=("analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",),
                notes="The data and analysis assets exist, but no dedicated issue-owned executable benchmark contract currently exposes this family as a release gate.",
                blocked_by_issue=119,
            ),
        ),
        (
            "figiel_2025_ssm_ds_born",
            BenchmarkCase(
                id="figiel_2025_ssm_ds_born",
                title="Figiel 2025 modified Born / SSM / DS",
                source="Figiel 2025 NaBr/H2O liquid-electrolyte MIAC and Born derivative parity fixture",
                model_setup={
                    "route": "liquid-electrolyte parity and native Ceres probe",
                    "dataset": "2025_Figiel",
                },
                input_records=("analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",),
                expected={
                    "miac_probe": 0.7732309439080085,
                    "parameter_movement_nonzero": ["d_born", "f_solv"],
                },
                tolerances={
                    "miac_abs": 1.0e-12,
                    "objective_nonincrease": True,
                },
                command="uv run python analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",
                status=EXECUTABLE,
                package_surface=(
                    "analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",
                ),
                validation_paths=(
                    "analyses/paper_validation/native/2025_figiel/scripts/validate_figure_data.py",
                ),
                notes="Current evidence is analysis-owned. Pytest keeps only generic API/native contracts.",
            ),
        ),
        (
            "rezaee_lithium_extraction_inputs",
            BenchmarkCase(
                id="rezaee_lithium_extraction_inputs",
                title="Rezaee lithium extraction thermodynamic model inputs",
                source="Rezaee 2025/2026 in-worktree DES/TOPO Li/Na source-backed diagnostic lane",
                model_setup={
                    "route": "package-local application diagnostic validation",
                    "analysis": "analyses/paper_validation/application/2026_rezaee",
                },
                input_records=(
                    "analyses/paper_validation/application/2026_rezaee/data/input/rezaee_2025_extraction_equilibrium_mole_fractions.csv",
                    "analyses/paper_validation/application/2026_rezaee/data/input/rezaee_2026_reaction_constants.csv",
                    "analyses/paper_validation/application/2026_rezaee/data/input/rezaee_2026_organic_pcsaft_parameters.csv",
                    "analyses/paper_validation/application/2026_rezaee/data/input/rezaee_2026_organic_binary_interactions.csv",
                ),
                expected={
                    "row_count": 26,
                    "direct_published_constant_closure_supported": False,
                    "source_text_equilibrium_data_points": 36,
                    "source_backed_si_equilibrium_rows": 26,
                },
                tolerances={
                    "max_abs_charge_residual": 1.0e-6,
                    "max_element_balance_norm": 1.0e-10,
                    "direct_li_extraction_aard_pct_min": 90.0,
                    "source_supported_combined_median_abs_ln_residual_min": 2.0,
                },
                command="uv run python analyses/paper_validation/application/2026_rezaee/scripts/run_all.py",
                status=EXECUTABLE,
                package_surface=(
                    "analyses/paper_validation/application/2026_rezaee/scripts/run_all.py",
                    "src/epcsaft/runtime/__init__.py",
                ),
                validation_paths=(
                    "analyses/paper_validation/application/2026_rezaee/results/reaction_equilibrium/summary.json",
                ),
                notes="Executable package-local diagnostic lane. Passing means the source/reference-state gap is reproduced honestly; it does not claim direct published-constant closure.",
            ),
        ),
    )
)


def run_literature_benchmarks(
    *,
    case: str | None = None,
    execute_commands: bool = False,
    command_runner: Callable[[str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if case is not None and case not in LITERATURE_CASES:
        raise ValueError(f"Unknown case {case!r}. Expected one of: {', '.join(LITERATURE_CASES)}")

    selected = [case] if case is not None else list(LITERATURE_CASES)
    runner = command_runner or _run_case_command
    entries = []
    execution_summary = {"attempted": 0, "passed": 0, "failed": 0, "blocked": 0}
    for name in selected:
        entry = LITERATURE_CASES[name].to_payload()
        _validate_case_contract(entry)
        if execute_commands:
            if entry["status"] == EXECUTABLE:
                result = runner(str(entry["command"]))
                returncode = int(result.get("returncode", 1))
                passed = returncode == 0
                entry["execution"] = {
                    "attempted": True,
                    "passed": passed,
                    "returncode": returncode,
                    "duration_seconds": float(result.get("duration_seconds", 0.0)),
                    "stdout_tail": _tail_text(str(result.get("stdout", ""))),
                    "stderr_tail": _tail_text(str(result.get("stderr", ""))),
                }
                execution_summary["attempted"] += 1
                execution_summary["passed" if passed else "failed"] += 1
            else:
                entry["execution"] = {
                    "attempted": False,
                    "passed": None,
                    "returncode": None,
                    "duration_seconds": None,
                    "stdout_tail": "",
                    "stderr_tail": "",
                    "blocked": True,
                    "reason": entry["notes"],
                }
                execution_summary["blocked"] += 1
        else:
            entry["execution"] = None
        entries.append(entry)
    status_counts = Counter(entry["status"] for entry in entries)
    if set(status_counts) - ALLOWED_STATUSES:
        unknown = ", ".join(sorted(set(status_counts) - ALLOWED_STATUSES))
        raise ValueError(f"Unsupported literature benchmark status(es): {unknown}")
    executable_cases = [entry["id"] for entry in entries if entry["status"] == EXECUTABLE]
    blocked_cases = [entry["id"] for entry in entries if entry["status"] == BLOCKED]
    return {
        "issue": 119,
        "title": "Executable literature benchmark and downstream gate registry",
        "package_version": str(__version__),
        "git_commit": _git_commit(),
        "selected_cases": selected,
        "run_mode": EXECUTE_EXECUTABLE_CASES if execute_commands else REGISTRY_ONLY,
        "execution_summary": execution_summary,
        "all_executable_commands_passed": execution_summary["failed"] == 0,
        "capability_evidence_source": "epcsaft.runtime.capability_evidence",
        "registered_validation_lanes": list(VALIDATION_LANES),
        "registered_pytest_slices": list(TEST_SLICES),
        "status_counts": dict(status_counts),
        "executable_cases": executable_cases,
        "blocked_cases": blocked_cases,
        "cases": entries,
    }


def render_literature_benchmark_table(payload: dict[str, Any]) -> str:
    headers = ["case", "status", "executed", "passed", "expected", "tolerances", "command"]
    widths = {header: len(header) for header in headers}
    rows: list[list[str]] = []
    for row in payload["cases"]:
        execution = row.get("execution")
        values = [
            str(row["id"]),
            str(row["status"]),
            "yes" if execution and execution["attempted"] else "no",
            (
                "yes"
                if execution and execution["passed"] is True
                else "no"
                if execution and execution["passed"] is False
                else "n/a"
            ),
            "yes" if row["expected"] is not None else "no",
            "yes" if row["tolerances"] is not None else "no",
            "yes" if row["command"] else "no",
        ]
        rows.append(values)
        for header, value in zip(headers, values):
            widths[header] = max(widths[header], len(value))

    def _format(values: list[str]) -> str:
        return "  ".join(value.ljust(widths[header]) for header, value in zip(headers, values))

    header_line = _format(headers)
    divider = "  ".join("-" * widths[header] for header in headers)
    body = "\n".join(_format(values) for values in rows)
    return "\n".join((header_line, divider, body))


def payload_as_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False)
