# Picard Stress Evidence To Rescue Or Retire Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one M8 toybox stress-evidence lane that can either rescue Picard for more research or retire it cleanly after issue 223.

**Architecture:** Add a single retained stress-evidence workflow under `analyses/package_validation/explicit_association_toybox` that reuses the existing exact implicit, Picard policy, JAX derivative, saturation, and objective-probe helpers. The workflow produces retained CSVs, plotted-data CSVs, readable figures, and a decision memo without changing provider, equilibrium, regression, benchmark, or public API files.

**Tech Stack:** Python, NumPy, SciPy, JAX where derivative evidence is required, Matplotlib, pytest, Superpowers Project docs.

---

## Source And Decisions

- Source spec: `docs/superpowers/specs/2026-06-05-m8-python-toybox-picard-stress-evidence-to-rescue-or-retire.md`
- Milestone: `M8 - Python Toybox`
- Related prior evidence: issue 223 / PR 233 final admission packet.
- Related design issue: issue 161, but this plan must not mark issue 161 provider-ready.
- Planning decisions:
  - Use one integrated M8 plan.
  - Optimize for evidence that can rescue Picard or rule it out.
  - Use proposed gates that the final report must justify from retained data.

## Acceptance Criteria

- A retained Picard stress matrix covers association strength, density,
  temperature, composition, topology, asymmetric mixture, and cross-association
  cases.
- Exact implicit association is retained as the baseline for every case where the
  baseline solves.
- The same fixed Picard policy grid is evaluated against the stress matrix; no
  new approximation family is introduced.
- Retained rows include scalar, property-proxy, derivative, Hessian, objective,
  closure-only timing, and end-to-end simulation timing metrics where each metric
  applies.
- JAX derivatives of the explicit Picard expression are compared against exact
  implicit sensitivity baselines.
- A tiny equilibrium-style objective probe reports whether Picard changes
  objective residuals, gradient direction, Hessian conditioning, or local step
  quality.
- Final figures use readable scientific plotting: data markers or case points,
  dotted exact/Picard model curves where curve data exist, physical axes, grid
  rules, plotted-data CSVs, and no bar plots.
- A final Markdown decision memo chooses one outcome: retire Picard, keep M8-only
  research, or recommend a narrow future M3 provider-admission issue.
- No provider, equilibrium, regression, benchmark, public API, or package
  capability files are changed.

## Non-Goals

- No provider EOS implementation.
- No M4 equilibrium implementation.
- No M5 regression work.
- No M6 benchmark promotion.
- No new explicit association approximation families.
- No conclusion based only on scalar `a^assoc` plots.

## Proposed Gates

These gates are candidate decision criteria. The implementation should report
them transparently and let the decision memo justify whether they are strong
enough.

- Exact implicit baseline solves for every retained case included in the final
  decision.
- Picard density-root and saturation solves do not fail when exact implicit
  succeeds.
- Association Helmholtz, total residual proxy, pressure proxy, derivative, and
  Hessian relative errors stay bounded across each stress family.
- Equilibrium-style objective diagnostics do not show sign, rank, conditioning,
  or local-step regressions that would plausibly damage Ipopt-like workflows.
- Median end-to-end simulation timing is faster than exact implicit in each
  retained case family.
- No retained case family is routinely slower than exact implicit.

## Task 1: Stress Matrix Configuration

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/picard_stress_evidence.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/picard_stress_cases.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py`

- [ ] **Step 1: Write the failing config/schema tests**
  - Assert the stress matrix contains pure/self-association, one associating plus
    inert, unequal associating binary, cross-association, water-like strong
    association, and asymmetric composition cases.
  - Assert the matrix declares density, temperature, association-strength, and
    composition axes.
  - Assert every case has a stable `case_id`, `case_family`, `topology_id`,
    `simulation_scope`, and `decision_role`.
- [ ] **Step 2: Run the test and verify the expected failure**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py -q`
  - Expected before implementation: missing stress config/helper.
- [ ] **Step 3: Implement the stress matrix loader**
  - Add a small typed loader that reads the YAML and returns deterministic case
    records.
  - Reuse existing case conventions from `association_case_matrix.py`,
    `asymmetric_binary_closures.py`, `paper_systems.py`, and
    `water_parameter_cases.py` instead of inventing unrelated names.
- [ ] **Step 4: Run the test and verify it passes**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py -q`
- [ ] **Step 5: Commit**
  - Commit message: `analysis: add Picard stress case matrix`

## Task 2: Stress Evidence Evaluator

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/picard_stress_evidence.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/picard_policy_grid.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_evidence.py`

- [ ] **Step 1: Write the failing evaluator tests**
  - Assert output rows include exact implicit baseline rows and Picard policy rows
    for all supported stress cases.
  - Assert row schema includes site-fraction error, mass-action residual,
    association Helmholtz relative error, total residual proxy relative error,
    pressure proxy relative error, closure timing, simulation timing, and status
    columns.
  - Assert unsupported cases fail loudly with a retained status and message, not
    silent omission.
- [ ] **Step 2: Run the test and verify the expected failure**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_evidence.py -q`
- [ ] **Step 3: Implement the evaluator**
  - Reuse exact implicit and Picard policy evaluation helpers.
  - Keep the Picard policy selected before evaluation starts.
  - Do not add adaptive convergence logic inside the Picard expression.
- [ ] **Step 4: Run focused evaluator tests**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_evidence.py -q`
- [ ] **Step 5: Commit**
  - Commit message: `analysis: evaluate Picard stress evidence grid`

## Task 3: JAX Derivative And Hessian Stress Comparison

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/picard_stress_derivatives.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/jax_picard_autodiff_backend.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/implicit_sensitivity.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_derivatives.py`

- [ ] **Step 1: Write the failing derivative tests**
  - Assert derivative rows include variables for density, composition,
    temperature, and association-strength parameters where supported.
  - Assert Hessian rows include variable pairs, max relative error, conditioning
    flags, and exact implicit baseline status.
  - Assert JAX unavailable cases fail loudly with a direct dependency message.
- [ ] **Step 2: Run the test and verify the expected failure**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_derivatives.py -q`
- [ ] **Step 3: Implement derivative comparison**
  - Reuse the existing JAX Picard backend and exact implicit sensitivity helper.
  - Keep derivative semantics explicit: Picard derivatives are derivatives of the
    approximate explicit EOS.
- [ ] **Step 4: Run derivative tests**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_jax_picard_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_hessian_agreement.py -q`
- [ ] **Step 5: Commit**
  - Commit message: `analysis: stress Picard derivative and Hessian evidence`

## Task 4: Equilibrium-Style Objective Probe

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/picard_stress_objective_probe.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/equilibrium_style_objective_sensitivity.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_objective_probe.py`

- [ ] **Step 1: Write the failing objective-probe tests**
  - Assert objective rows include exact and Picard objective value, gradient
    error, Hessian error, conditioning summary, local-step direction agreement,
    and objective status.
  - Assert the probe is fixed-state and M8-only; it must not import
    `epcsaft_equilibrium` or create M4 route behavior.
- [ ] **Step 2: Run the test and verify the expected failure**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_objective_probe.py -q`
- [ ] **Step 3: Implement the objective probe**
  - Consume provider-like scalar/property/derivative rows from the stress
    evaluator.
  - Report whether Picard changes local objective direction or Hessian
    conditioning enough to threaten Ipopt-like workflows.
- [ ] **Step 4: Run objective-probe tests**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_objective_probe.py analyses/package_validation/explicit_association_toybox/tests/test_equilibrium_style_objective_sensitivity.py -q`
- [ ] **Step 5: Commit**
  - Commit message: `analysis: probe Picard objective sensitivity under stress`

## Task 5: Final Stress Report, Figures, And Decision Memo

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence_plotted_data.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.png`
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.svg`
- Create: `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.pdf`
- Create: `analyses/package_validation/explicit_association_toybox/docs/picard_stress_rescue_or_retire_decision.md`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_report.py`

- [ ] **Step 1: Write the failing report tests**
  - Assert the retained CSV includes scalar, property, derivative, Hessian,
    objective, and timing columns.
  - Assert the decision memo contains one of `retire_picard`, `keep_m8_only`, or
    `recommend_m3_provider_admission_issue`.
  - Assert plotted-data CSVs exist and no rendered bar-plot artifact is produced.
- [ ] **Step 2: Run the test and verify the expected failure**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_report.py -q`
- [ ] **Step 3: Implement data generation**
  - Command: `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py`
  - Expected: retained stress CSV and decision memo are written.
- [ ] **Step 4: Implement readable figures**
  - Command: `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py`
  - Expected: PNG, SVG, plotted-data CSV, and Matplotlib metadata are written.
- [ ] **Step 5: Run report tests**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_report.py -q`
- [ ] **Step 6: Commit**
  - Commit message: `analysis: report Picard stress rescue decision`

## Task 6: Project Docs And Final Verification

**Files:**
- Modify: `docs/superpowers/milestones/M8-python-toybox/README.md`
- Modify: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`

- [ ] **Step 1: Update docs**
  - Link the stress evidence lane and decision memo from the M8 milestone index.
  - Update issue 161 docs only as evidence context; do not mark provider-ready
    unless the stress memo explicitly recommends the M3 provider-admission route.
  - Update the toybox README with the retained stress-evidence workflow.
- [ ] **Step 2: Run proof oracle**
  - Command: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_objective_probe.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_report.py -q`
  - Command: `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py`
  - Command: `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py`
  - Command: `uv run python scripts/dev/validate_project.py quick`
- [ ] **Step 3: Render evidence in chat**
  - Show the new or updated plot with an absolute filesystem path.
  - Include a compact Markdown table summarizing real retained data from
    `picard_stress_evidence.csv`.
- [ ] **Step 4: Commit**
  - Commit message: `docs: document Picard stress evidence workflow`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_objective_probe.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_report.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py`
- `uv run python scripts/dev/validate_project.py quick`

## Risk Notes

- The plan may retire Picard. That is an acceptable completion outcome.
- JAX dependency failures should be loud and direct because this plan specifically
  requires JAX derivative evidence.
- Timing evidence must report both closure-only timing and end-to-end simulation
  timing; closure-only speedups are not enough.
- The final report must not claim provider readiness unless the retained data
  clear the proposed gates and the memo explicitly recommends a future M3 issue.
