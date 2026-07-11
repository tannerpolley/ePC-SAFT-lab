# M6 Gross 2002 Public Bubble/Dew Evidence Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` task-by-task. Use
> `superpowers:test-driven-development` for every contract change,
> `superpowers:systematic-debugging` for every numerical failure, and
> `superpowers:verification-before-completion` before each checkpoint.

**Goal:** Refresh the exact Gross/Sadowski 2002 Figures 2-9 evidence that backs
the exposed associating bubble/dew routes after the M3 model-input cutover,
without pulling unrelated paper repairs into M3 or broadening capability state.

**Architecture:** A blocked M6 leaf consumes the completed M3 resolved-input
SDK and M4 consumer cutover, migrates only source-complete Gross inputs,
regenerates Figures 2-9 sequentially through public routes, and emits one
freshness-bound receipt. The existing strict checker remains primary. A small
M6 contract cleanup removes a redundant import of the private M4 result-type
owner before the later M4 decomposition leaf moves that type.

**Tech Stack:** Python 3.13 local runtime, M3 typed model input, M4 equilibrium
public API and native extension, pytest, NumPy/Pandas, Matplotlib, MPLGallery,
Ruff, Sphinx, canonical JSON/SHA-256 receipts, and GitHub dependencies.

## Global Constraints

- Milestone ownership is M6; provider and equilibrium implementation remain
  M3 and M4.
- Start only after the coordinated M3 provider cutover and M4 resolved-input
  consumer leaf pass.
- Scope is Gross/Sadowski Figures 2-9 evidence used by public
  `bubble_pressure` and `dew_pressure` capability rows.
- Run figure generators in numerical order and stop on the first incomplete
  required source/input/route contract.
- Do not change paper values, fit parameters, infer structural zeros, relax
  score/checker thresholds, or substitute an internal route.
- Tests calculating predictions retain real source rows and source/model plots.
- Renderers read retained tables only and import no ePC-SAFT package.
- Figures 1, 8, and 10 may be read as unchanged prerequisite artifacts when
  required by the existing full checker; this plan does not expand their
  scientific scope.
- Public capability state does not change. Failure produces an exact M6
  blocker and a separate M4 replace-or-close decision, not stale acceptance.

---

## Source Evidence

- Approved spec:
  `docs/superpowers/specs/2026-07-10-m6-gross-2002-public-bubble-dew-evidence-refresh.md`.
- Source campaign:
  `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`.
- Current capability owner:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`.
- Current strict checker:
  `scripts/validation/check_gross_2002_full_replication.py`.
- Figure roots:
  `analyses/paper_validation/2002_gross/figures/figure_02` through
  `figure_09`.
- Current private-owner caller:
  `tests/native/contracts/test_gross_2002_figure01_internal_saturation.py`.

## Test Complete And Metrics

- A committed baseline records every failing Gross node after the M3/M4
  cutover, its figure, and its exact input/route/checker cause.
- Each executable Figure 2-9 input contains accepted M3 schema/version,
  source-qualified scientific records, exact structural-zero evidence, and no
  retired option file.
- Figures execute in order; every accepted model row uses public bubble/dew,
  current native identity, exact input/state fingerprints, and current
  derivative/postsolve fields.
- Every source/model/plotted table has stable row IDs, units, hashes, and image
  siblings; renderers are table-only.
- The strict checker accepts with complete/exact-association/fresh-native
  requirements, or a scoped checker has mutation-proven parity for every
  Figure 2-9 capability field.
- `equilibrium-confidence`, activation/capability equality, strict docs, Ruff,
  diff, cleanup, and independent reviews pass.
- The final receipt names exactly Figures 2-9 and does not claim unrelated
  Gross, LLE, electrolyte, reactive, or release scope.

## Outcome Proof

**Intent:** Keep the current bubble/dew capability evidence executable after
the typed-input cutover instead of treating its paper bundle as unrelated
cleanup.

**Current Behavior:** Public capability rows cite Gross Figures 2-9 and strict
repository lanes execute the Gross checker, while the M3 plan correctly leaves
paper migration to M6.

**Expected Outcome:** One M6 receipt proves that source-complete Figures 2-9
load the accepted M3 input schema, run through public M4 bubble/dew routes, and
retain fresh source/model/plot/checker evidence.

**Target Output:** Focused baseline classification, migrated Gross model-input
files, sequentially regenerated Figure 2-9 tables/plots/receipts, private-owner
caller cleanup, strict checker receipt, and capability-evidence freshness proof.

**Owner:** M6 owns paper artifacts/checker/receipt; M3 owns input semantics; M4
owns runtime routes and capability state.

**Interface:** Figure `generate_data.py`/`render_figure.py`,
`check_gross_2002_full_replication.py`, M3 configuration receipts, M4 public
route receipts, and a new M6 `public_bubble_dew_evidence_receipt.json`.

**Cutover:** Replace retired/unversioned Gross runtime configuration and stale
generated receipts. Do not preserve fallback loaders or duplicate plots.

**Replaced Path:** Retired option files, Windows-only path assumptions, stale
native/input identities, and a redundant M6 import of
`workflows.EquilibriumResult` are removed.

**Evidence:** RED mutations, sequential generator receipts, strict checker,
retained tables/plots, capability equality, docs/Ruff/diff/cleanup, and
independent thermodynamic/code review.

**Acceptance Proof:** The fresh strict checker returns complete with no
Figures 2-9 blocker; public bubble/dew capability rows point to current hashed
artifacts and the same M3/M4 identities; the M6 receipt is accepted by M0 and
the M4 caller-cutover dependency.

**Stop Criteria:** Stop on missing source evidence, an unresolvable active
model choice, a rejected public route, stale native identity, plot/table drift,
or any need to change an unrelated capability or scientific threshold.

**Avoid:** Do not fit missing values, edit unrelated paper bundles, treat a
diagnostic route as public evidence, or convert checker failure into a pass by
reducing scope without parity proof.

**Risk:** The M3 cutover may expose a genuinely incomplete Gross input or the
current full checker may couple public-route evidence to unrelated paper
requirements. The plan stops on missing input and permits a scoped checker only
after mutation-proven parity for every capability-backed Figure 2-9 field.

## Implementation Boundaries

**Files To Create:** One M6 gate receipt and focused receipt/checker mutation
tests under the Gross campaign shared results/tests.

**Files To Modify:** Gross Figure 2-9 configuration, generators, table-only
renderers, results, campaign checker/manifest only when required; the one Gross
private-owner test; M6 milestone docs and capability evidence hashes/paths.

**Files To Avoid:** M3/M4 production implementation, other paper-validation
roots, regression package, release workflows, and downstream repositories.

**Source Of Truth:** Retained Gross source artifacts and manifests, accepted M3
model-input receipts, M4 native/public route receipts, and strict checker.

**Read Path:** Source manifest -> M3 input -> public M4 route -> retained model
table -> table-only plot -> strict M6 checker -> M6 receipt.

**Write Path:** Translate proven inputs, generate canonical tables/receipts,
render plots from tables, and write the final receipt only after rehashing all
upstream artifacts.

**Integration Points:** M3 resolved-input receipts, the M4 provider consumer
and public bubble/dew selector, equilibrium capability evidence, Gross figure
contracts, the validation registry, MPLGallery, M0 closeout, and the M4
route-gated result-type cutover.

**Migration Or Cutover:** Baseline first, migrate source-complete inputs, then
Figures 2-5, Figures 6-9, and final receipt. No partial set enters capability
evidence.

**Replaced Path Handling:** Delete retired option/configuration files and stale
references in the same figure checkpoint; keep no redirector.

**Acceptance Proof Gate:** M3/M4 prerequisites, all tasks, strict checker,
equilibrium-confidence, reviews, cleanup, and clean Git are mandatory.

## Execution Dependency Graph

```text
M3 resolved-input cutover + M4 consumer
                  |
                  v
Task 1 baseline and receipt contract
                  |
                  v
Task 2 input/caller migration
                  |
                  v
Task 3 Figures 2-5
                  |
                  v
Task 4 Figures 6-9
                  |
                  v
Task 5 strict receipt and handoff
```

### Task 1: Establish The Post-Cutover Baseline And Receipt Contract

**Use Cases:**

- Every current Gross failure is named by collected node, figure, and exact
  cause after the actual M3/M4 cutover.
- Receipt mutations fail on stale input/native identity, missing source/model
  rows, wrong public route, missing plot, or checker mismatch.

**Files:**

- Create: `tests/native/contracts/test_gross_2002_public_bubble_dew_receipt.py`
- Modify: `scripts/validation/check_gross_2002_full_replication.py` only if the
  receipt hook is absent.

**Interfaces:** Produces the exact baseline report and schema for
`public_bubble_dew_evidence_receipt.json`.

- [ ] **Step 1: Run collection and focused Gross tests after M3/M4 land.**
  Record exact failing node IDs and causes; do not copy a pre-cutover failure
  list into the receipt.
- [ ] **Step 2: Write RED receipt mutation tests.** Cover every required
  identity, row, artifact, route, derivative, postsolve, and checker field.
- [ ] **Step 3: Confirm feature-specific RED.** Existing scientific failures
  or missing receipt fields count; collection/environment failures do not.
- [ ] **Step 4: Implement only the receipt parser/incomplete status.** Keep the
  live gate nonzero until all figures pass.
- [ ] **Step 5: Commit.** Use
  `test(validation): define Gross public bubble dew receipt`.

### Task 2: Migrate Source-Complete Gross Inputs And Remove The Private-Type Caller

**Use Cases:**

- Each active Gross input either loads with exact source evidence under M3
  schema v1 or reports one blocker without a fallback.
- The migration replaces every retired option/configuration file and Windows-
  path assumption in scope; no duplicate loader or redirect survives.
- The Figure 1 internal saturation test proves exact `dict` behavior without
  importing `workflows.EquilibriumResult`.

**Files:**

- Modify: `analyses/paper_validation/2002_gross/parameters/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_02` through
  `figure_09` input-loading contracts.
- Modify: `tests/native/contracts/test_gross_2002_figure01_internal_saturation.py`

**Interfaces:** Consumes M3 `model_configuration.json`, schema-3 parameter
records, and public M4 SDK v1; produces exact input receipts for each figure.

- [ ] **Step 1: Write RED migration tests.** Reject retired filenames,
  defaults, missing records, unknown keys, Windows path assumptions, and
  mismatched component/source identity.
- [ ] **Step 2: Remove the redundant private-type assertion under test.** Keep
  `type(result) is dict` plus every source/route/result assertion and prove no
  behavior change.
- [ ] **Step 3: Translate only proven records.** Delete retired files; stop an
  affected figure when any active value is unresolved.
- [ ] **Step 4: Run focused input/provenance/provider-consumer tests.** Require
  exact definition fingerprints and no paper prediction yet.
- [ ] **Step 5: Commit.** Use
  `data(validation): migrate Gross bubble dew inputs`.

### Task 3: Regenerate And Review Gross Figures 2-5 Sequentially

**Use Cases:**

- Each figure retains source/model rows and plots from the public route.
- A blocked earlier figure prevents acceptance credit for later figures in
  this tranche.

**Files:**

- Modify: `analyses/paper_validation/2002_gross/figures/figure_02/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_03/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_04/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_05/**`

**Interfaces:** Public `bubble_pressure`/`dew_pressure`; exact M3/M4 receipts;
table-only renderers.

- [ ] **Step 1: Add RED per-figure contract/freshness assertions.** Require
  source rows, public route, input/native identity, derivatives, postsolve,
  tables, and plot siblings.
- [ ] **Step 2: Run each generator then renderer in numerical order.** Stop at
  the first exact blocker and leave later artifacts untouched.
- [ ] **Step 3: Run per-figure checker and inspect every changed plot.** Retain
  no model row without a source row.
- [ ] **Step 4: Run the campaign checker in non-complete mode.** Require no
  blocker for completed Figures 2-5.
- [ ] **Step 5: Commit each figure or coherent pair separately.** Do not batch
  a failing figure with an accepted one.

### Task 4: Regenerate And Review Gross Figures 6-9 Sequentially

**Use Cases:**

- Figures 6-9 meet the same source/public-route/receipt/plot contract as the
  first tranche.
- Existing accepted prerequisite artifacts remain unchanged unless their own
  strict field is stale.

**Files:**

- Modify: `analyses/paper_validation/2002_gross/figures/figure_06/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_07/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_08/**`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_09/**`

**Interfaces:** Same public route and retained artifact contract as Task 3.

- [ ] **Step 1: Add RED per-figure contract/freshness assertions.** Include the
  exact association-Hessian and branch requirements already named by the
  checker; add no new numerical threshold.
- [ ] **Step 2: Generate/render Figures 6-9 in order.** Stop on a missing
  source/input/route receipt.
- [ ] **Step 3: Run per-figure checks and inspect every changed plot.** Compare
  source/model tables and rendered series exactly.
- [ ] **Step 4: Run the complete strict checker.** Require fresh native and
  exact-association flags; diagnose, do not weaken, any remaining blocker.
- [ ] **Step 5: Commit focused checkpoints.** Keep unrelated paper files out.

### Task 5: Publish The Accepted M6 Receipt And Close The Public-Route Gate

**Use Cases:**

- M0 and the M4 route-gated decomposition leaf consume one immutable accepted
  receipt instead of inferring readiness from files.
- Capability output, docs, checker, and retained artifacts agree on the exact
  bubble/dew scope.

**Files:**

- Create: `analyses/paper_validation/2002_gross/shared/results/public_bubble_dew_evidence_receipt.json`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`
  only for current hashes/paths, not scope.
- Modify: `docs/superpowers/milestones/M6-validation/README.md`
- Modify: `scripts/dev/validation_registry.py` only if the focused receipt
  command is not already represented by the strict lane.

**Interfaces:** Produces one accepted M6 receipt consumed by the M0 closeout
graph and M4 Task 8 caller-cutover gate.

- [ ] **Step 1: Write RED final receipt/capability mutation tests.** Reject
  stale hashes, missing figures, wrong routes, broadened scope, and registry
  commands that omit fresh native proof.
- [ ] **Step 2: Rehash upstream artifacts and write the receipt once.** The
  checker output hashes upstream evidence; the evidence never hashes a later
  consumer receipt.
- [ ] **Step 3: Run final focused proof.** Run the strict Gross checker,
  activation/capability tests, `equilibrium-confidence`, docs, Ruff, diff, and
  cleanup.
- [ ] **Step 4: Request independent thermodynamic and code review.** Resolve
  real findings with RED tests and rerun Step 3.
- [ ] **Step 5: Commit.** Use
  `test(validation): refresh Gross public bubble dew evidence`.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m6-gross-2002-public-bubble-dew-evidence-refresh-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m6-gross-2002-public-bubble-dew-evidence-refresh-plan.md
uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_public_bubble_dew_receipt.py tests/native/contracts/test_gross_2002_full_replication_checker.py tests/native/contracts/test_gross_2002_figure01_internal_saturation.py -q
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python run_pytest.py --equilibrium-confidence -q
uv run --no-sync python scripts/docs/generate_equilibrium_activation.py --check
uv run --no-sync ruff check analyses/paper_validation/2002_gross tests/native/contracts/test_gross_2002_public_bubble_dew_receipt.py tests/native/contracts/test_gross_2002_figure01_internal_saturation.py
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

Expected: all commands pass, the strict checker has no Figures 2-9 blocker,
capability scope is unchanged, every changed plot is retained and reviewed,
and Git is clean after the final checkpoint.
