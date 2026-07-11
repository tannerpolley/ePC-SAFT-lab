# M6 Standalone CE Nonideal Input Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` task-by-task. Use
> `superpowers:test-driven-development` for contract changes,
> `superpowers:systematic-debugging` for failed source or runtime gates,
> `chemical-engineer` for every parameter/standard-state decision, and
> `superpowers:verification-before-completion` at each checkpoint.

**Goal:** Convert the existing blocked nonideal MEA ledger into an executable,
source-qualified typed input only if every active record closes, then retain
Linux model receipts, literature/model tables, plots, and a machine-checkable
M6 evidence receipt for M4.

**Architecture:** M6 owns source classification, citations, fitted-receipt
identity, typed input snapshots, analysis tables, plots, and the evidence
checker. It begins only after #329 completes the M4 component receipt/checker
contract, then consumes the M3 resolved-model-input API and the M4 receipt API
without changing either package or M4's admission checker. Input acceptance,
evidence completeness, and model-result acceptance remain separate: a
source-complete input may produce a rejected CE solve, that rejection remains
visible, and a later M4 leaf performs source-qualified classification.

**Tech Stack:** Python 3.13 local development baseline, `uv`, pytest, JSON,
CSV, Matplotlib, Pillow, MPLGallery, typed ePC-SAFT model configuration,
equilibrium-native receipts, Ruff, and Sphinx.

## Global Constraints

- Milestone ownership is `M6 - Validation`; no M3 provider or M4 equilibrium
  implementation change belongs to this plan.
- This M6 leaf is `blocked_by` the completed #329 component receipt/checker
  contract. It blocks a separate M4 source-qualified classification or defect
  leaf; it does not block #329 itself and it does not directly activate #330.
- Preserve commits `34820228`, `aa48d200`, and `a38705d0` as completed
  migration/evidence foundations; do not recreate their retired branch layout.
- Keep `model_configuration.json` and `parameter_set.json` absent while any
  active ledger record is blocked, conflicting, out of domain, or unresolved.
- Do not infer zeros, extend validity domains, relabel a fitted value as
  literature, or reuse a historical model output as a current prediction.
- Literature observations require a resolvable source identity and an exact
  table, figure, or equation locator. Unresolved surname-only rows remain
  excluded from scoring.
- Model-prediction tests retain at least one plot containing the real source
  observations and the current model values used by the test.
- The 20, 40, 60, and 80 degree Celsius grids execute only when every active
  input and reaction correlation has a domain covering 293.15-353.15 K.
- A rejected native solve remains a labeled row; it is not omitted or replaced
  by an imported curve or diagnostic seed.
- Public equilibrium capability state is outside M6. M4 issue #330 decides
  admission after consuming this evidence.
- Every checkpoint runs focused tests, `git diff --check`, and the repository
  cleanup hook.

---

## Source Evidence

- Approved cross-workstream design:
  `docs/superpowers/specs/2026-07-10-m4-nonideal-mea-speciation-linux-migration-design.md`.
- M4 consumer contract:
  `docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md`.
- Current ledger root:
  `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/`.
- Verified starting inventory: 11 named pure/correlation/formulation records,
  108 unique off-diagonal `k_ij`/`l_ij`/`k_hb_ij` records, and five reaction
  records. Only the retained water segment-size correlation is currently
  accepted across the execution grid.
- Current named blockers include the CO2 segment-count conflict, missing
  CO2/MEA permittivity sources, unsupported neutral solvation values,
  Figiel-domain limits, interaction provenance/structural-zero evidence,
  ion-dispersion formulation mapping, missing Nasrifar source material,
  reaction-coefficient conflicts, and unproven nonideal standard-state mapping.
- Current observation blocker:
  `source/unresolved_reference_observations.csv` contains imported rows without
  sufficient bibliography/locator metadata for literature scoring.
- Historical downstream model rows remain in
  `source/imported_downstream_model_snapshot.csv` and are comparison-only.

## Test Complete And Metrics

- Every ledger row has one stable record ID, evidence status, gate status,
  source kind/path/locator, units or basis, supported domain, execution domain,
  current typed mapping, and blocker reason.
- Accepted ledger rows have a traceable literature source, fitted receipt, or
  cited defining model rule; blocked rows cannot enter executable JSON.
- The typed bundle resolves all nine species in the declared order at every
  executed temperature/composition and produces deterministic definition/state
  fingerprints.
- The static grids contain exactly four 161-point loading sequences; the
  animation grid contains exactly 16 states. No state outside the proven input
  domain executes.
- Every attempted CE state records input fingerprint, native build identity,
  seed provenance, acceptance, balance, stationarity, full nonideality/final
  lambda, and the M4 receipt hash.
- Literature and current-model rows share explicit coordinates, species,
  units, and source/result identities before they enter plotted data.
- Every retained current-model figure has an exact plotted-data CSV and
  same-stem SVG/PNG/PDF siblings. Animation output exists only when all 16
  animation states are complete.
- The M6 evidence receipt separately reports `input_status`,
  `observation_status`, `execution_status`, `plot_status`,
  `scientific_result_status`, `evidence_complete`, and `admission_candidate`;
  no aggregate status hides a rejected solve.
- `evidence_complete=true` is allowed with
  `scientific_result_status=rejected` and `admission_candidate=false` when all
  planned attempts, failures, receipts, and applicable artifacts are retained.
- `plot_status=not_applicable_no_accepted_prediction` is allowed only when
  there are zero accepted current-model prediction rows and no model-prediction
  assertion. Every accepted prediction assertion still requires a real
  literature/model plotted-data table and retained plot bundle.

## Outcome Proof

**Intent:** Supply M4 with a reproducible nonideal MEA input and real-data
evidence without inventing historical model details or treating imported model
curves as validation observations.

**Current Behavior:** The current Linux analysis preserves useful source-branch
tables and an explicit blocker ledger, but the executable typed bundle is
absent, 293 observation rows are unresolved for literature scoring, and no
current nonideal Linux prediction can be claimed.

**Expected Outcome:** Either the ledger remains an exact, committed blocker
receipt with no executable input, or every active record closes and one typed
bundle produces deterministic M3 receipts, M4 CE receipts, retained result
tables, and literature/model figures on Linux.

**Target Output:** Updated evidence ledgers, resolved observation table,
conditional `model_configuration.json` and `parameter_set.json`, M6 input
evidence receipt, current prediction/solve/CE receipt tables, table-only plot
bundles when applicable, analysis metadata, MPLGallery registrations, and M6
evidence-completeness checker JSON.

**Owner:** M6 owns the analysis/source/artifact files and evidence checker;
M3 owns typed model resolution; M4 owns the CE solver, numerical receipt, and
admission decision.

**Interface:** `Mixture.from_folder(...)`, the M3 resolved configuration
receipt, M4 `StandaloneCEReceipt`,
`validate_nonideal_input.py --json --require-complete`, retained CSV/JSONL
tables, and
`check_nonideal_mea_evidence.py --json --require-evidence-complete`. The later
M4 classification leaf consumes the resulting receipt; this M6 plan does not
modify `check_standalone_ce_gate.py`.

**Cutover:** The accepted typed bundle displaces the historical loose options
and matrix snapshots only after all active evidence closes. Current Linux rows
then displace imported-model rows in the `current_local_model_prediction` role,
while imported rows remain separately labeled.

**Replaced Path:** Retired `analyses/paper_validation/standalone_ce`,
`user_options.json`, loose option mappings, stale results folders, direct model
dictionaries, source-seeded completion, and plot-time model execution remain
absent.

**Evidence:** Primary-source locators, fitted lineage, row hashes, typed input
fingerprints, provider/equilibrium native identities, M4 receipt hashes,
explicit failure rows, literature/model plotted data, visual review, focused
tests, docs, Ruff, diff, and cleanup receipts.

**Acceptance Proof:** M6 is complete when the input and observation gates are
source-complete, every planned state resolves and retains its M4 attempt
receipt, every accepted model-prediction assertion is represented in a
literature/model plot, and the M6 evidence checker reports
`evidence_complete=true` without changing M4 capability state. A
scientifically rejected solve may complete M6 evidence with
`admission_candidate=false`; the later M4 classification leaf remains required
and #330 stays blocked.

**Stop Criteria:** Stop before executable input on the first blocked ledger
row, unresolved active observation, unsupported temperature domain,
configuration fingerprint mismatch, stale native identity, unexpected native
path, or table/plot mismatch.

**Avoid:** Do not broaden a correlation domain, use numeric blanks/zeros as
evidence, fit new parameters without a separate M5 target contract, score
imported model snapshots as observations, or smooth away failed states.

**Risk:** Retained literature may never define the historical nine-species
configuration across 20-80 degrees Celsius. The correct output is then the
precise blocker ledger, not a partial executable bundle or recreated plot.

## Implementation Boundaries

**Files To Create:** Conditional typed input JSON under the existing
`source/model_input/` root; `source/literature_speciation_observations.csv` only
after exact citations close; `scripts/validate_nonideal_input.py` and
`scripts/generate_nonideal_data.py`;
`scripts/check_nonideal_mea_evidence.py`; M6 receipt/current
prediction/solve/CE receipt tables under the figure `output/` root; and
completed plot bundles when accepted prediction assertions exist.

**Files To Modify:** Existing input/reaction ledgers, source manifest,
`test_nonideal_figure_workflow.py`, table-only `render_figure.py`,
`analysis.yaml`, analysis README, `.mplgallery/manifest.yaml`, focused
project-structure tests, and M6 evidence-checker tests. The M4 strict gate and
its tests are consumed only by the later M4 classification/admission work.

**Files To Avoid:** `packages/epcsaft/**`,
`packages/epcsaft-equilibrium/src/**`, `packages/epcsaft-regression/**`, other
paper-validation bundles, downstream repositories, remote refs, and release
metadata.

**Source Of Truth:** Retained primary literature and fitted receipts, the
accepted ledger, M3 schema/receipt, M4 receipt schema, and exact generated
tables behind retained plots.

**Read Path:** Source/fitted evidence -> ledger -> typed input snapshot -> M3
definition/state receipt -> M4 CE receipt -> current result row -> joined
literature/model plotted data -> figure and M6 checker receipt.

**Write Path:** Add a failing evidence mutation, verify it names the missing
record, update one source-backed row or retain its blocker, generate only after
all rows close, render only from promoted tables, and commit one coherent
checkpoint.

**Integration Points:** M3 model configuration parsing/evaluation, M4 CE
receipt, analysis generation, retained-data promotion, Matplotlib rendering,
MPLGallery discovery, the later M4 source-classification input seam, docs, and
repository structure checks.

**Migration Or Cutover:** Preserve the three completed migration commits;
continue from the blocked ledger. Create executable JSON and current-model
artifacts only on the accepted branch of the evidence gate.

**Replaced Path Handling:** Keep historical values only as audit fields or
explicit imported snapshots. Delete no source evidence; delete any obsolete
execution path when its last caller moves to typed input.

**Acceptance Proof Gate:** No complete M6 claim is allowed until source,
typed-input, runtime, applicable plot, M6 evidence-checker, visual-review,
docs, Ruff, diff, cleanup, and independent chemical-engineering review
receipts are fresh. A rejected run with no accepted prediction uses the
explicit non-admission plot state rather than fabricating a model curve.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Continue from blocked ledger | Commits `34820228`, `aa48d200`, `a38705d0` already migrated/classified it | No restart or stale-branch merge | M6 |
| Keep executable JSON conditional | Most active rows remain blocked | Absence is the expected loud gate | M6 |
| Separate input and solve status | Correct input can yield a rejected model state | M6 may finish evidence while #330 stays blocked | M6/M4 |
| Keep milestone checkers separate | M6 proves evidence completeness; M4 decides classification and admission | M6 owns `check_nonideal_mea_evidence.py`; a later M4 leaf consumes it | M6/M4 |
| Allow explicit non-admission completion | A complete attempted run can reject every state | Preserve failure receipts, set `admission_candidate=false`, and require plots only for accepted prediction assertions | M6 |
| Require real plotted observations | Imported model curves are not observations | Resolve citations before model-prediction figures count | M6 |
| Use table-only rendering | Plot-time model calls duplicate execution ownership | Generator writes tables; renderer reads tables only | M6 |
| Preserve exact grids conditionally | Historical grids are useful but exceed current proven domains | Execute them only after all domains cover them | M6 |
| Do not refit in M6 | Missing parameters require a traceable target/optimizer contract | Route fitting to M5 | M5 |

### Task 1: Close Or Preserve Every Source And Observation Blocker

**Use Cases:**

- A reviewer can trace every active parameter, formulation choice, reaction
  constant, structural zero, and scored observation to a precise source or
  fitted receipt.
- A remaining blocker stays visible and prevents the old loose execution path
  from returning.

**Files:**

- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/input_evidence_ledger.csv`
- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/reaction_input_evidence_ledger.csv`
- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/source_manifest.csv`
- Modify or retain unresolved: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/unresolved_reference_observations.csv`
- Create only after citation closure: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/literature_speciation_observations.csv`
- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`

**Interfaces:**

- Consumes current ledger schemas and retained sources.
- Produces accepted-or-blocked rows with immutable `record_id` and explicit
  source/domain/mapping fields; no runtime object is produced in this task.

- [ ] **Step 1: Extend RED mutations for every remaining blocker class.** Add
  parameterized tests for conflicting values, absent source locators,
  incomplete fitted lineage, unsupported domains, unverified zeros,
  formulation mismatch, reaction-basis mismatch, and unresolved observation
  citations. Require executable JSON to remain absent whenever any mutation is
  present.

- [ ] **Step 2: Verify RED where evidence is incomplete.** Run
  `uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py -q`.
  Expected: contract tests pass for the current explicit blocked state; a
  temporary mutation that marks a blocker accepted fails with its record ID.

- [ ] **Step 3: Perform bounded source recovery.** For each row, record an
  exact primary-source/fitted locator and domain or preserve its existing
  blocker. Do not infer a mapping from historical runtime behavior. Resolve
  Bottinger/Jakobsen/Matin observations only when exact bibliography and row
  coordinates are retained.

- [ ] **Step 4: Verify GREEN for the achieved state.** Re-run the Task 1 test.
  Expected: either all rows are accepted and the observation table exists, or
  the blocked state passes by proving exact blockers and absent executable
  input.

- [ ] **Step 5: Checkpoint commit.** Use
  `data(validation): qualify nonideal MEA source evidence` when rows close, or
  `docs(validation): refine nonideal MEA input blockers` when they remain
  blocked.

### Task 2: Materialize And Verify The Typed Input Bundle

**Use Cases:**

- A source-complete nine-species bundle resolves deterministically at every
  requested state through M3 without loose options or value insertion.
- The accepted typed bundle displaces historical matrices only after all row
  evidence is complete.

**Files:**

- Create conditionally: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/model_configuration.json`
- Create conditionally: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/parameter_set.json`
- Create conditionally: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/nonideal_input_evidence_receipt.json`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/validate_nonideal_input.py`
- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`

**Interfaces:**

- Produces CLI `validate_nonideal_input.py --json --require-complete`.
- Consumes `Mixture.from_folder(MODEL_INPUT_ROOT,
  components=SPECIES_ORDER)` and M3 definition/state receipts.
- Produces `input_status`, ledger hashes, schema/source identities, component
  order, tested state fingerprints, evaluated correlations, structural-zero
  evidence, and exact native mapping identity.

- [ ] **Step 1: Write RED typed-bundle tests.** Require the exact nine-species
  order, versioned model configuration, parameter graph, all accepted ledger
  record IDs, deterministic fingerprints, state-domain enforcement, and exact
  native mappings at all static/animation coordinates.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py -q`.
  Expected while Task 1 is blocked: analysis tests pass by proving JSON is
  absent; complete-path tests remain gated and are not made green with values.

- [ ] **Step 3: Write the bundle only on complete evidence.** Serialize each
  accepted row into the M3 schema, retain source identity and domain, load the
  folder, evaluate every requested state, and write the evidence receipt only
  after all fingerprints and mappings validate.

- [ ] **Step 4: Refactor and verify GREEN.** Generate JSON from accepted ledger
  records through one deterministic script path, not copied dictionaries.
  Re-run Task 2 and `validate_nonideal_input.py --json --require-complete`.
  Expected: zero exit only on a complete source-qualified bundle.

- [ ] **Step 5: Checkpoint commit.** Commit
  `data(model): define source-qualified nonideal MEA input`.

### Task 3: Generate Linux CE Receipts And Current Model Tables

**Use Cases:**

- Every current model row is reproducible from one M3 input fingerprint and one
  M4 standalone CE receipt.
- Rejected states remain visible and displace the old practice of treating an
  imported curve as current Linux output.

**Files:**

- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_nonideal_data.py`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_current_local_predictions.csv`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_solve_summary.csv`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_configuration_receipts.jsonl`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_standalone_ce_receipts.jsonl`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_generation_summary.json`
- Create/regenerate: `analyses/package_validation/standalone_ce/shared/results/standalone_ce_receipt.json`
- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`

**Interfaces:**

- Consumes the Task 2 typed bundle and M4 `StandaloneCEReceipt` API.
- Produces one attempt row per state with input/native/receipt hashes, seed
  provenance, full nonideality/final lambda, result/failure class, balance, and
  stationarity.
- Produces one canonical selected-state receipt at
  `shared/results/standalone_ce_receipt.json` for the M4 independent checker;
  its state ID points to the matching JSONL row.

- [ ] **Step 1: Write RED generator tests.** Require immutable grid identity,
  one CE execution owner, provider/equilibrium native freshness, complete
  receipt linkage, explicit failure rows, and directory-level transactional
  promotion from `output/runs/<run-id>/`.

- [ ] **Step 2: Verify RED.** Run the analysis test. Expected: new generator
  assertions fail because the script/current tables are absent.

- [ ] **Step 3: Implement one Linux generator.** Load the typed folder, record
  M3 receipts, call the single current M4 CE owner, retain each M4 receipt,
  validate row counts/hashes, and promote the complete artifact set together.
  Keep imported snapshots read-only and separately labeled.

- [ ] **Step 4: Run and verify GREEN.** Build the equilibrium profile, run the
  generator, then rerun the analysis test. Expected: zero exit only for a
  structurally complete table set; rejected scientific states remain rows and
  keep #330 blocked.

- [ ] **Step 5: Checkpoint commit.** Commit
  `data(validation): retain nonideal MEA Linux receipts`.

### Task 4: Render Real Literature Versus Current Model Evidence

**Use Cases:**

- A user can inspect the exact real observations and every accepted current
  prediction used by validation assertions, with failures and imported-model
  context visibly distinct.
- Table-only plots replace plot-time solver calls and stale model-only images.
- A run with zero accepted current predictions records the explicit
  non-admission plot state instead of inventing a comparison curve.

**Files:**

- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py`
- Create/regenerate: exact plotted-data CSV plus SVG/PNG/PDF bundles under the
  existing figure `output/` root for each evidence-complete temperature/view
- Create/regenerate only after all 16 states pass the input/runtime contract:
  animation input CSV, preview SVG/PNG/PDF/CSV, and GIF
- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`

**Interfaces:**

- Consumes only Task 1 literature rows and Task 3 current/imported result
  tables; imports neither `epcsaft` nor `epcsaft_equilibrium`.
- Produces plotted-data rows with `evidence_role`, source identity, model input
  fingerprint, receipt hash, species, coordinates, value, units, and result
  status.

- [ ] **Step 1: Write RED plot contracts.** For every accepted current-model
  prediction assertion, require at least one real literature row and one
  current-model row in its validation figure, distinct marker/line roles beyond
  color, failure annotations, exact CSV/image siblings, and absence of model
  imports. When there are zero accepted prediction rows, require
  `plot_status=not_applicable_no_accepted_prediction`, the complete rejected
  attempt table, and no model-validation assertion.

- [ ] **Step 2: Verify RED.** Run the analysis test. Expected: figure tests fail
  until evidence-complete joined tables and bundles exist; unresolved source
  rows cannot satisfy them.

- [ ] **Step 3: Implement table-only rendering.** Join rows by declared
  temperature/loading/species coordinates, preserve units and source IDs,
  render only evidence-complete figures, and omit the animation when any of its
  16 states is incomplete. If every current solve is rejected, retain the
  literature and failure tables, emit the explicit non-admission plot status,
  and do not register a model-prediction figure.

- [ ] **Step 4: Render, verify GREEN, and inspect.** Run the renderer and
  analysis tests, then inspect every changed SVG/PNG and the GIF when present.
  Expected: no clipping or ambiguous legend; plotted-data hashes match the
  source/current tables.

- [ ] **Step 5: Checkpoint commit.** Commit
  `docs(validation): render nonideal MEA literature comparisons`.

### Task 5: Publish And Independently Check The M6 Evidence Receipt

**Use Cases:**

- The later M4 classification leaf can consume one exact M6 evidence receipt
  without reinterpreting source tables.
- The M6 checker reports input completeness, observations, execution,
  applicable plots, and scientific rejection separately; it can complete a
  non-admission evidence run without changing M4's strict gate.

**Files:**

- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/nonideal_mea_evidence_receipt.json`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/check_nonideal_mea_evidence.py`
- Modify: `analyses/package_validation/standalone_ce/analysis.yaml`
- Modify: `analyses/package_validation/standalone_ce/README.md`
- Modify: `.mplgallery/manifest.yaml`
- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

**Interfaces:**

- Produces M6 receipt fields `input_status`, `observation_status`,
  `execution_status`, `plot_status`, `scientific_result_status`,
  `evidence_complete`, `admission_candidate`, fingerprints, source/plot paths,
  receipt hashes, and blockers.
- Produces CLI
  `check_nonideal_mea_evidence.py --json --require-evidence-complete`.
- Produces an acyclic artifact flow: M6 evidence receipt -> M6 checker output ->
  later M4 classification. The evidence receipt never hashes or embeds its own
  checker output.
- Is consumed by the later M4 source-qualified classification leaf; does not
  set activation/capability fields or modify the canonical M4 admission
  checker.

- [ ] **Step 1: Write RED M6-checker mutations.** Remove each status,
  fingerprint, source table, M4 receipt hash, applicable plotted-data path, and
  image sibling in turn. Mutate a rejected run to
  `admission_candidate=true`, and mutate a run with accepted prediction rows to
  `plot_status=not_applicable_no_accepted_prediction`. Require the M6 checker
  to name each mismatch while existing capability tests keep
  `reactive_speciation` closed.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py tests/workflows/repo/test_project_structure.py -q`.
  Expected: new M6-receipt/checker assertions fail until the receipt and checker
  exist.

- [ ] **Step 3: Generate and register the evidence receipt.** Hash the accepted
  ledgers, typed receipts, solve/CE tables, applicable plotted data, and
  artifacts. Set `evidence_complete=true` only when all planned attempts and
  hashes exist. Set `admission_candidate=false` for any rejected numerical
  result. Use `plot_status=not_applicable_no_accepted_prediction` only when no
  accepted prediction assertion exists; update MPLGallery only for complete
  plot bundles.

- [ ] **Step 4: Implement the independent M6 completeness checker.** Read the
  receipt after it is written, rehash every referenced source/runtime/artifact
  file, validate the status cross-product, and exit zero for
  `--require-evidence-complete` when evidence is complete even if
  `scientific_result_status=rejected`. Do not call the CE solver, modify the
  receipt, import the M4 admission checker, or make checker output an input to
  the receipt hash.

- [ ] **Step 5: Refactor and verify GREEN.** Rerun focused tests, the M6 input
  checker, and
  `uv run --no-sync python analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/check_nonideal_mea_evidence.py --json --require-evidence-complete`.
  Expected: an evidence-complete rejected solve exits zero with
  `admission_candidate=false`; the later M4 classification leaf becomes ready,
  and #330 stays blocked.

- [ ] **Step 6: Checkpoint commit.** Commit
  `docs(validation): register nonideal MEA evidence receipt`.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m6-standalone-ce-nonideal-input-evidence-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m6-standalone-ce-nonideal-input-evidence-plan.md
uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py tests/native/contracts/test_standalone_ce_gate.py tests/workflows/repo/test_project_structure.py -q
uv run --no-sync python analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/validate_nonideal_input.py --json --require-complete
uv run --no-sync python analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/check_nonideal_mea_evidence.py --json --require-evidence-complete
uv run --no-sync ruff check analyses/package_validation/standalone_ce tests/workflows/repo/test_project_structure.py
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

If Task 1 remains blocked, the correct verified checkpoint is the focused
analysis test proving exact blockers and absent executable JSON. Tasks 2-5 do
not run, and M6 is not reported complete.
