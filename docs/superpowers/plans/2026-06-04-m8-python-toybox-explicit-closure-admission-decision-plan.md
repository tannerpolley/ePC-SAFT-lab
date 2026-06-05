# Final Picard Admission Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the final M8 Picard evidence packet needed to recommend whether issue #161 should close, stay blocked, or become a narrow M3 provider-admission issue.

**Architecture:** Extend the toybox so the existing fixed Picard policy grid can run through the same pure-saturation simulation path as the exact implicit baseline. Join policy-grid relative errors, end-to-end simulation timing, solver/root status, and readable saturation plots into one retained decision report. Keep this analysis-only: provider, equilibrium, regression, public API, and benchmark capability files stay untouched.

**Tech Stack:** Python, NumPy, SciPy, JAX, CSV, Markdown, pytest, Matplotlib, ripgrep.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md`
- Issue Mirror: `docs/superpowers/issues/2026-06-04-m8-python-toybox-issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/223`
- Related Provider Design Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/161`
- Milestone: `M8 - Python Toybox`
- Package: `analysis`
- AFK/HITL: `HITL`; final #161 action remains a human-reviewed decision memo.

## Locked Decisions

- Use the existing M8 issue #223 rather than creating a new tracker issue.
- Run end-to-end simulation timing across the full fixed Picard grid where the toybox supports the case.
- Generate a #161 close/defer/promote decision memo; do not automatically close or rewrite live #161.
- Keep Picard step count and damping as fixed policy settings, not new closure families and not adaptive convergence controls.

## Dependencies

This plan consumes evidence and APIs created by these completed or open M8 lanes:

- `docs/superpowers/plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md`
- `docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid-plan.md`
- `docs/superpowers/plans/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence-plan.md`

Current retained evidence roots:

- `analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/output/picard_policy_grid.csv`
- `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation.csv`
- `analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/output/picard_policy_cppad_handoff_matrix.csv`

## Acceptance Criteria

- [ ] `evaluate_closure(...)`, pressure-density coupling, and pure-saturation solving accept every closure name in `PICARD_POLICY_GRID`.
- [ ] A final retained CSV contains exact implicit baseline rows and all 25 Picard policies for each supported simulation case.
- [ ] The retained CSV includes relative-error columns for association Helmholtz, total residual Helmholtz proxy, pressure proxy, saturation pressure, vapor density, liquid density, selected derivatives, and selected Hessian/Jacobian diagnostics.
- [ ] The retained CSV includes closure-only and end-to-end simulation timing for exact implicit and Picard policies.
- [ ] The final figure lane renders readable saturation-style comparisons with data markers, dotted exact-implicit curves, and dotted Picard curves. No bar plots are added.
- [ ] A Markdown decision memo recommends one #161 disposition: close without provider implementation, close as design-complete and open a narrow M3 provider-admission issue, or keep blocked for one named missing evidence item.
- [ ] The issue #223 local mirror and issue #161 local mirror point to the final evidence plan/report and do not claim provider readiness.
- [ ] No `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, public API, benchmark registry, or capability claim files change.

## Non-Goals

- No provider EOS implementation.
- No equilibrium package implementation.
- No regression package work.
- No benchmark admission.
- No public API or capability change.
- No new explicit association closure family.
- No claim that JAX proves provider CppAD behavior; JAX remains proxy evidence.

## File Map

- Modify `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py` so policy-grid closure names can be evaluated through the same string contract used by property and saturation code.
- Modify `analyses/package_validation/explicit_association_toybox/scripts/toy_property_eos.py` only if `closure_models.evaluate_closure(...)` alone is insufficient for policy-grid names.
- Create `analyses/package_validation/explicit_association_toybox/scripts/final_picard_admission_report.py` to join policy-grid errors, saturation simulation results, timing, and #161 recommendation fields.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py` as the figure-lane data entrypoint.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py` for readable pressure-density and saturation-style plots.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.csv`.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report_plotted_data.csv`.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.png`.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.svg`.
- Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.mpl.yaml`.
- Create `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md`.
- Create `analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py`.
- Modify `analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py`.
- Modify `analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py`.
- Modify `docs/superpowers/issues/2026-06-04-m8-python-toybox-issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence.md`.
- Modify `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`.

## Tasks

### Task 1: Make Picard Policy Names Work Through Property Coupling

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/toy_property_eos.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py`

- [ ] **Step 1: Add failing policy-name evaluation tests**

Add this test to `analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py`:

```python
def test_every_picard_policy_name_evaluates_through_closure_contract() -> None:
    case = association_case_by_id("pure_2b_self")
    density = float(case.density_grid[1])
    delta = case.scaled_delta(case.strength_scale)

    for policy in PICARD_POLICY_GRID:
        direct = evaluate_picard_policy(
            policy,
            system=case.system,
            density=density,
            composition=case.composition,
            delta=delta,
        )
        named = evaluate_closure(
            policy.closure_name,
            system=case.system,
            density=density,
            composition=case.composition,
            delta=delta,
        )
        assert named.name == policy.closure_name
        assert np.array_equal(named.xa, direct.xa)
```

Add this test to `analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py`:

```python
def test_pure_saturation_accepts_non_default_picard_policy_name() -> None:
    result = solve_pure_saturation(
        _methanol_case(),
        temperature=352.28,
        closure_name="picard_n11_lambda1",
        pressure_seed_Pa=175_580.0,
        liquid_density_seed_mol_m3=22_891.0,
    )

    assert result.status == "computed_toy_pure_saturation"
    assert result.closure_name == "picard_n11_lambda1"
    assert result.rho_liq_mol_m3 > result.rho_vap_mol_m3
```

- [ ] **Step 2: Run the focused failing tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py::test_every_picard_policy_name_evaluates_through_closure_contract analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py::test_pure_saturation_accepts_non_default_picard_policy_name -q
```

Expected: both tests fail because `evaluate_closure(...)` currently only accepts `damped_picard_7_05` and `exact_2b_reduction`.

- [ ] **Step 3: Add a policy-name lookup**

In `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`, add:

```python
PICARD_POLICY_BY_NAME = {policy.closure_name: policy for policy in PICARD_POLICY_GRID}


def picard_policy_from_name(name: str) -> PicardPolicy | None:
    return PICARD_POLICY_BY_NAME.get(name)
```

Then change `evaluate_closure(...)` so any policy-grid name routes to `evaluate_picard_policy(...)`:

```python
    policy = picard_policy_from_name(name)
    if policy is None:
        raise ValueError(f"Unknown association closure: {name}")
    return evaluate_picard_policy(
        policy,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )
```

Keep `EXACT_2B_REDUCTION` handling before this policy lookup.

- [ ] **Step 4: Run the focused tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py::test_every_picard_policy_name_evaluates_through_closure_contract analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py::test_pure_saturation_accepts_non_default_picard_policy_name -q
```

Expected: both tests pass.

- [ ] **Step 5: Run surrounding policy and saturation tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit**

Commit only this task's files:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/closure_models.py analyses/package_validation/explicit_association_toybox/scripts/toy_property_eos.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py
git commit -m "analysis: route Picard policy names through toybox EOS"
```

### Task 2: Build Final Admission Report Rows

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/final_picard_admission_report.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py`
- Modify: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`

- [ ] **Step 1: Write the final-report schema test**

Create `analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py` with:

```python
from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.final_picard_admission_report import (
    FINAL_REPORT_COLUMNS,
    build_final_picard_admission_rows,
)


def test_final_picard_report_contains_full_grid_and_simulation_metrics() -> None:
    rows = build_final_picard_admission_rows(repeat_count=1, max_source_rows=1)

    assert rows
    assert set(FINAL_REPORT_COLUMNS).issubset(rows[0])
    assert {int(row["step_count"]) for row in rows if row["step_count"] != ""} == {3, 5, 7, 9, 11}
    assert {float(row["damping"]) for row in rows if row["damping"] != ""} == {0.35, 0.5, 0.65, 0.8, 1.0}
    assert "implicit_exact_mass_action" in {row["policy_name"] for row in rows}
    assert all(row["issue_161_recommendation"] for row in rows)
    assert any(row["simulation_elapsed_median_seconds_picard"] != "" for row in rows)
```

- [ ] **Step 2: Run the new test and verify failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q
```

Expected: failure because `final_picard_admission_report.py` does not exist.

- [ ] **Step 3: Implement report constants and row builder**

Create `analyses/package_validation/explicit_association_toybox/scripts/final_picard_admission_report.py` with these public entrypoints:

```python
FINAL_REPORT_COLUMNS = (
    "case_id",
    "topology_id",
    "simulation_id",
    "simulation_type",
    "component_family",
    "mixture_family",
    "step_count",
    "damping",
    "policy_name",
    "exact_iteration_count",
    "solver_status_exact",
    "solver_status_picard",
    "density_root_status_exact",
    "density_root_status_picard",
    "association_helmholtz_relative_error",
    "total_ares_proxy_relative_error",
    "pressure_proxy_relative_error",
    "saturation_pressure_relative_error",
    "liquid_density_relative_error",
    "vapor_density_relative_error",
    "derivative_max_relative_error",
    "hessian_max_relative_error",
    "closure_elapsed_median_seconds_exact",
    "closure_elapsed_median_seconds_picard",
    "simulation_elapsed_median_seconds_exact",
    "simulation_elapsed_median_seconds_picard",
    "closure_speedup_vs_exact",
    "simulation_speedup_vs_exact",
    "pareto_band",
    "admission_band",
    "issue_161_recommendation",
)
```

Implement `build_final_picard_admission_rows(repeat_count: int = 3, max_source_rows: int | None = None) -> list[dict[str, object]]` so it:

- calls `run_picard_policy_grid(repeat_count=repeat_count)` for closure-level rows;
- loads saturation rows through `load_public_saturation_rows(...)` and `load_provider_cases(...)`;
- computes exact implicit saturation once per source row;
- computes Picard saturation for every `PICARD_POLICY_GRID` closure name for the same source row;
- measures each saturation solve with `timed_closure(...)`;
- computes relative errors with `relative_error(...)`;
- records solver failure messages as row status strings rather than hiding them;
- assigns `admission_band` through a small deterministic function named `classify_admission_band(row)`;
- sets `issue_161_recommendation` to one of `close_without_provider_implementation`, `close_design_complete_open_narrow_provider_admission_issue`, or `keep_blocked_for_named_missing_evidence`.

- [ ] **Step 4: Add CSV and Markdown writers**

In the same module, add:

```python
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "final_picard_admission_report" / "output" / "final_picard_admission_report.csv"
DEFAULT_MEMO = ANALYSIS_ROOT / "docs" / "issue_161_picard_admission_decision.md"


def generate_final_picard_admission_report(
    output_path: Path = DEFAULT_OUTPUT,
    memo_path: Path = DEFAULT_MEMO,
    *,
    repeat_count: int = 3,
) -> Path:
    ...
```

The Markdown memo must include:

- retained row count;
- best high-accuracy policy by evidence;
- fastest policy by simulation timing;
- worst retained relative-error row;
- worst retained simulation residual row;
- the selected #161 recommendation;
- an explicit sentence that no provider implementation is admitted unless the recommendation says `close_design_complete_open_narrow_provider_admission_issue`.

- [ ] **Step 5: Run the new test**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q
```

Expected: pass.

- [ ] **Step 6: Generate the final retained data and memo**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/scripts/final_picard_admission_report.py
```

Expected:

- `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.csv` exists.
- `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md` exists.

- [ ] **Step 7: Commit**

Commit only this task's files:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/final_picard_admission_report.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.csv analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md
git commit -m "analysis: generate final Picard admission evidence"
```

### Task 3: Render Final Decision Figures

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py`

- [ ] **Step 1: Add figure-lane tests**

Extend `analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py` with:

```python
def test_final_picard_report_figure_lane_writes_plot_data(tmp_path) -> None:
    from analyses.package_validation.explicit_association_toybox.figures.final_picard_admission_report.scripts.render_figure import (
        build_plotted_rows,
    )

    rows = build_final_picard_admission_rows(repeat_count=1, max_source_rows=1)
    plotted = build_plotted_rows(rows)

    assert plotted
    assert {"reference_marker", "model_curve"} <= {row["plot_role"] for row in plotted}
    assert {"Data", "Exact implicit"} <= {row["series_label"] for row in plotted}
    assert all(row["plot_kind"] in {"saturation_pressure", "liquid_density"} for row in plotted)
```

- [ ] **Step 2: Run the figure-lane test and verify failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py::test_final_picard_report_figure_lane_writes_plot_data -q
```

Expected: failure because the figure-lane module does not exist.

- [ ] **Step 3: Implement the generate-data entrypoint**

Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py` with a `main()` that calls:

```python
from analyses.package_validation.explicit_association_toybox.scripts.final_picard_admission_report import (
    generate_final_picard_admission_report,
)


def main() -> None:
    print(generate_final_picard_admission_report())
```

- [ ] **Step 4: Implement plotted rows and rendering**

Create `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py` with:

- `build_plotted_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]`;
- data markers from retained reference rows;
- dotted exact-implicit model curves;
- dotted Picard curves for at least the best `fast`, `balanced`, and `high_accuracy` policies when those labels exist;
- axis labels using scientific notation and units;
- no bar plots.

Render:

- `final_picard_admission_report.png`;
- `final_picard_admission_report.svg`;
- `final_picard_admission_report_plotted_data.csv`;
- `final_picard_admission_report.mpl.yaml`.

- [ ] **Step 5: Run tests and render figures**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py
```

Expected:

- test passes;
- PNG and SVG figure artifacts exist;
- plotted-data CSV exists and contains data-marker and model-curve rows.

- [ ] **Step 6: Commit**

Commit only this task's files:

```powershell
git add analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py
git commit -m "analysis: render final Picard admission figures"
```

### Task 4: Sync Issue Mirrors Without Claiming Provider Readiness

**Files:**
- Modify: `docs/superpowers/issues/2026-06-04-m8-python-toybox-issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence.md`
- Modify: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
- Modify: `docs/superpowers/milestones/M8-python-toybox/README.md`
- Modify: `docs/superpowers/milestones/M3-eos/README.md`

- [ ] **Step 1: Update #223 local mirror acceptance criteria**

Update `docs/superpowers/issues/2026-06-04-m8-python-toybox-issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence.md` so the acceptance criteria match this plan:

- full fixed Picard grid simulation evidence;
- exact implicit timing baseline;
- relative-error columns;
- #161 decision memo;
- no provider readiness claim.

- [ ] **Step 2: Update #161 local mirror with the decision-memo dependency**

Update `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md` so it points to:

- `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md`;
- this plan path;
- issue #223 as the final M8 evidence owner.

Keep #161 readiness as `needs design` unless the memo explicitly recommends a narrow provider-admission issue.

- [ ] **Step 3: Update milestone indexes**

Update:

- `docs/superpowers/milestones/M8-python-toybox/README.md` to describe #223 as the final Picard grid-plus-simulation admission packet.
- `docs/superpowers/milestones/M3-eos/README.md` to state that #161 is awaiting the M8 decision memo rather than ready for provider code.

- [ ] **Step 4: Verify wording**

Run:

```powershell
rg -n "final_picard_admission_report|issue_161_picard_admission_decision|provider implementation|provider-admission|M8" docs/superpowers/issues docs/superpowers/milestones/M8-python-toybox/README.md docs/superpowers/milestones/M3-eos/README.md
```

Expected: #223 and M8 mention the final evidence packet; #161 and M3 mention the M8 decision memo; no wording says provider implementation is admitted.

- [ ] **Step 5: Commit**

Commit only docs sync files:

```powershell
git add docs/superpowers/issues/2026-06-04-m8-python-toybox-issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence.md docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md docs/superpowers/milestones/M8-python-toybox/README.md docs/superpowers/milestones/M3-eos/README.md
git commit -m "docs: tie Picard admission decision to M8 evidence"
```

### Task 5: Final Verification And Handoff

**Files:**
- Read: `git status --short`
- Read: `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md`
- Read: `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.csv`

- [ ] **Step 1: Run focused tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Regenerate retained artifacts**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py
```

Expected: retained CSVs, memo, PNG, SVG, and plotted-data CSV are current.

- [ ] **Step 3: Run project validation**

Run:

```powershell
uv run python scripts/dev/validate_project.py quick
```

Expected: validation completes successfully.

- [ ] **Step 4: Run cleanup hook**

Run:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected: no owned leftover processes are reported.

- [ ] **Step 5: Prepare handoff**

The final handoff must include:

- a Markdown table with retained row count, best high-accuracy policy, fastest simulation policy, worst relative-error row, worst simulation residual row, and #161 recommendation;
- inline rendering of `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.png` with an absolute filesystem path;
- explicit statement that provider implementation remains blocked unless the memo recommends a narrow M3 provider-admission issue.

- [ ] **Step 6: Commit**

Commit remaining final artifacts:

```powershell
git add analyses/package_validation/explicit_association_toybox docs/superpowers
git commit -m "analysis: finalize Picard admission evidence packet"
```

## Proof Oracle

Run these commands before claiming the plan complete:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py
rg -n "collapsed|diagonal|mean_field|polish" analyses/package_validation/explicit_association_toybox/scripts analyses/package_validation/explicit_association_toybox/config
uv run python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

The `rg` command should produce no active runnable closure references. Historical prose references are acceptable only outside `scripts` and `config`.

## Risk Notes

- Full-grid saturation simulation may be slow. Keep `repeat_count=1` in unit tests and use the default report repeat count only in generated artifacts.
- Some source rows may fail density or saturation solves for a policy. Record the failure status in the final report and let `admission_band` reflect it; do not hide it with a substitute row.
- The final decision memo is evidence for human review. It does not mutate live GitHub issue #161 by itself.
