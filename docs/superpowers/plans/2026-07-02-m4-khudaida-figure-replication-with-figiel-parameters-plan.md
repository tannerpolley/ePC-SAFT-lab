# Khudaida Figure Replication With Figiel Parameters Plan

**Goal:** Reopen Khudaida 2026 figure reproduction as a figure-by-figure M4
equilibrium validation tranche that first proves the retained Figiel 2025
ePC-SAFT parameter snapshot through the public package route before treating
parameter regression as a blocker.

**Owning milestone:** M4 - Equilibrium
**Owning package:** `packages/epcsaft-equilibrium`
**Tracking issue:** #405
**Ready leaf:** #406

## Outcome Proof

**Intent:** Replace the broad Khudaida model-reproduction blocker with narrow
figure issues that can be resolved one at a time from retained source data,
Figiel 2025 parameters, regenerated artifacts, and package-level public-route
diagnostics.
**Current Behavior:** The retained Khudaida figure folders already exist under
`analyses/paper_validation/2026_khudaida/figures`, but current fit statistics
are incomplete: Figures 1, 8, 9, and 10 have zero model rows; Figures 3, 5, 6,
7, and S3 accept zero model rows; Figures 2, 4, and S2 accept only partial
rows. The Khudaida parameter snapshot is also not byte-identical to the Figiel
2025 snapshot for pure parameters and binary interactions.
**Expected Outcome:** Each figure issue either regenerates source/model data,
plots, statistics, and residual diagnostics with the Figiel 2025 parameter
snapshot, or stops with exact failed rows and source-backed residual evidence.
M5 issue #338 remains related historical evidence for the old Khudaida
parameter probe, but it is not a blocker for this Figiel-parameter campaign.
**Target Output:** A parent issue, twelve figure issues, local mirrors, and a
figure-specific validation ladder that can prove complete Khudaida figure
artifacts and model reproduction through the public package route.
**Owner:** M4 equilibrium package owner for package-route behavior and retained
paper-validation artifacts.
**Interface:** `packages/epcsaft-equilibrium`, public
`Equilibrium(..., route="electrolyte_lle")`, Khudaida figure scripts, Figiel
2025 parameter snapshots, retained plot/statistics artifacts, and GitHub issue
dependencies.
**Cutover:** Replace the old single broad #320/#338 conclusion with one
figure-at-a-time proof issues that first validate the Figiel parameter path.
**Replaced Path:** Treating Khudaida figure reproduction as globally
regression-blocked before proving the already-retained Figiel parameter source
through each figure workflow.
**Evidence:** Retained source/model CSVs, regenerated plots, fit statistics,
parameter-provenance records, public-route residual diagnostics, issue mirrors,
and checker output.
**Acceptance Proof:** All child issues #406 through #417 close with retained
evidence and the final Khudaida checker reports complete artifacts and complete
model reproduction for the accepted figure set.
**Stop Criteria:** Stop if a figure lacks traceable source inputs, Figiel
parameter provenance, public-route execution, retained residual diagnostics, or
exact failed-row evidence.
**Avoid:** Do not add hidden fitted parameters in M4, use private-native-only
proof, count diagnostic-only success, broaden capability claims, or use M5 #338
as a precondition for these figure proofs.
**Risk:** Figure 10 is not an HELD2 flash proof; it must be retained as a
source/sigma-profile provenance figure so it does not dilute LLE evidence.

## Implementation Boundaries

**Files To Create:** Figure-specific tests or retained statistics/provenance
artifacts only when needed by child issues #406 through #417.
**Files To Modify:** `analyses/paper_validation/2026_khudaida/**`,
`scripts/validation/check_khudaida_2026_figure_validation.py`,
`packages/epcsaft-equilibrium/**`, focused package tests, issue mirrors, and
M4 docs or registries only when the proven claim changes.
**Files To Avoid:** `packages/epcsaft-regression/**`, downstream repositories,
release docs, and unrelated EOS/provider refactors.
**Source Of Truth:** Khudaida retained figure source data, the Figiel 2025
parameter snapshot in `analyses/paper_validation/2025_figiel/parameters`, and
the M4 public-route equilibrium certification contract.
**Read Path:** For each figure, trace source CSVs, feed construction, parameter
loading, public route call, model CSVs, fit statistics, plotted artifacts, and
checker records before changing solver behavior.
**Write Path:** Change the smallest owner needed for that figure to regenerate
public-route model data and retained evidence with Figiel parameter provenance.
**Integration Points:** Figure scripts, shared Khudaida checker, public
electrolyte LLE route, package tests, docs/registries, and GitHub issue
dependencies.
**Migration Or Cutover:** Work one child issue at a time in issue-number order,
moving the next figure from blocked to ready only after its predecessor closes.
**Replaced Path Handling:** Keep #338 related but unblocking for this campaign;
only propose M5 follow-up after a child retains failed Figiel-parameter proof.
**Acceptance Proof Gate:** The child PR must include figure artifact paths,
numeric statistics, parameter provenance, residual diagnostics, and exact
commands before closeout.

## Parameter Contract

- Source of truth: `analyses/paper_validation/2025_figiel/parameters`.
- The existing Khudaida parameter folder may remain only if the implementation
  retains row-equivalence/provenance evidence against the Figiel snapshot.
- No fitted parameters may be added inside the M4 validation path.
- If a figure cannot pass after the Figiel provenance is correct, retain the
  exact rows, residuals, parameter source, and plotted comparison before
  proposing any M5 follow-up.

## Figure Issue Map

| Issue | Figure | Scope | Readiness |
| --- | --- | --- | --- |
| #405 | Parent | All Khudaida figure replication with Figiel 2025 parameters | blocked by #406-#417 |
| #406 | Figure 1 | 293.15 K salt-free, 5 wt% NaCl, and 10 wt% NaCl LLE comparison | ready |
| #407 | Figure 2 | 293.15 K, 5 wt% NaCl electrolyte LLE | blocked by #406 |
| #408 | Figure 3 | 303.15 K, 5 wt% NaCl electrolyte LLE | blocked by #407 |
| #409 | Figure 4 | 313.15 K, 5 wt% NaCl electrolyte LLE | blocked by #408 |
| #410 | Figure 5 | 293.15 K, 10 wt% NaCl electrolyte LLE | blocked by #409 |
| #411 | Figure 6 | 303.15 K, 10 wt% NaCl electrolyte LLE | blocked by #410 |
| #412 | Figure 7 | 313.15 K, 10 wt% NaCl electrolyte LLE | blocked by #411 |
| #413 | Figure 8 | Separation-factor metric from reproduced phase compositions | blocked by #412 |
| #414 | Figure 9 | Ethanol distribution-coefficient metric from reproduced phase compositions | blocked by #413 |
| #415 | Figure 10 | Sigma-profile source/provenance figure | blocked by #414 |
| #416 | Figure S2 | 5 wt% NaCl supporting LLE panels at 293.15, 303.15, and 313.15 K | blocked by #415 |
| #417 | Figure S3 | 10 wt% NaCl supporting LLE panels at 293.15, 303.15, and 313.15 K | blocked by #416 |

## Shared Acceptance Criteria

- Each figure regenerates retained CSV data and plot artifacts from traceable
  source inputs.
- Each model-comparable row uses the public package route; private-native-only,
  diagnostic-only, residual-only, or alternate solver proof does not count.
- Each LLE row retains material balance, pressure consistency, phase charge,
  reduced electroneutral lift/back-lift, neutral transfer, mean-ionic transfer,
  phase distance, exact-Hessian evidence, and Ipopt route receipts.
- Each metric figure computes metrics from reproduced phase compositions rather
  than accepting a source-only plot.
- Figure 10 is classified as a source/sigma-profile provenance figure and is
  not counted as HELD2 LLE residual evidence.
- Figure statistics include row counts, tolerance basis, AAD/RMSE/max-error
  summaries, parameter provenance, and exact failed rows when a figure cannot
  pass.

### Task 1: Publish and mirror the figure issue set

**Use Cases:**
- Acceptance evidence is visible in GitHub and local mirrors for #405 through
  #417.
- Cutover from the old broad blocker is explicit: #338 is related evidence, not
  a prerequisite for the Figiel-parameter figure path.

**Files:**
- `docs/superpowers/issues/2026-07-02-m4-khudaida-issue-0405-figure-replication-with-figiel-parameters.md`
- `docs/superpowers/issues/2026-07-02-m4-khudaida-issue-04*.md`

### Task 2: Resolve figure issues in dependency order

**Use Cases:**
- Acceptance evidence for each figure includes regenerated data, plots,
  statistics, and residual diagnostics before the next figure starts.
- Cutover is incremental: each child replaces one slice of the old global
  Khudaida blocker with retained figure-specific proof.

**Files:**
- `analyses/paper_validation/2026_khudaida/figures/figure_*/**`
- `packages/epcsaft-equilibrium/tests/**`
- `scripts/validation/check_khudaida_2026_figure_validation.py`

### Task 3: Close the parent only after the full figure set passes

**Use Cases:**
- Acceptance evidence covers the final Khudaida checker, package tests, and
  docs validator.
- Cutover is complete only when the parent no longer relies on #320/#338 as
  substitutes for per-figure proof.

**Files:**
- `docs/superpowers/issues/2026-07-02-m4-khudaida-issue-0405-figure-replication-with-figiel-parameters.md`
- `docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md`

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and electrolyte and lle" -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
```
