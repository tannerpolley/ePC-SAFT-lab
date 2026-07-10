# Nonideal MEA Speciation Linux Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `superpowers:subagent-driven-development` in the current session or
> `superpowers:executing-plans` in a later session. Use
> `superpowers:test-driven-development` for each implementation change,
> `superpowers:systematic-debugging` for unexpected failures, and independent
> review before every integration checkpoint.

**Goal:** Recover the useful nonideal MEA speciation evidence and plotting work
from `codex/m4-ce-nonideal-speciation-plots` into the current Linux analysis
layout, while allowing current-model predictions only after one strict typed
input graph has complete, traceable scientific evidence.

**Architecture:** Adapt source evidence rather than merging stale branch
history. Classify imported observations, imported downstream model snapshots,
diagnostic seeds, and current local predictions separately. Gate the executable
path on a strict `model_configuration.json` plus schema-v3 `parameter_set.json`,
load it through `Mixture.from_folder`, evaluate exact state receipts, and call
only the internal standalone-CE NLP owner. Generate durable tables first;
render plots from those tables without importing the model runtime.

**Tech Stack:** Python 3.9-3.13, `uv`, pytest, Ruff, Matplotlib, Pillow animation,
JSON/JSONL/CSV, ePC-SAFT typed model inputs, the internal equilibrium NLP and
Ipopt, Sphinx, MPLGallery, Bash, and Git.

**Global Constraints:** Keep public reactive speciation, reactive LLE,
electrolyte LLE, TP flash, CPE, and multiphase routes closed. Do not repair the
20 deferred Khudaida/Gross paper failures in this plan. Do not invent missing
parameters, turn matrix blanks into evidence, infer scientific zeros, preserve
retired loose options, or call old public/alternate solver routes. A missing
record or unsupported temperature domain stops executable migration loudly.
No push, force push, remote branch deletion, or history rewrite is authorized.

---

## Source And Scope

- Approved spec:
  `docs/superpowers/specs/2026-07-10-m4-nonideal-mea-speciation-linux-migration-design.md`
- Milestone/package owner: M4, `packages/epcsaft-equilibrium`
- Analysis owner: `analyses/package_validation/standalone_ce`
- Source branch: `codex/m4-ce-nonideal-speciation-plots` at `f3057e11`
- Integration target: local `main`
- Branch integration policy: adapt the seven unique commits; do not merge their
  retired `analyses/paper_validation/standalone_ce` paths or false capability
  metadata.
- Task 9 boundary: the working line may contain the paused typed-input commits,
  but the publication-safe line intentionally omits them and their known
  paper-specific failures. Tasks 4-10 remain conditional on both a closed
  scientific evidence gate and the typed provider contract being available.

## Source Evidence

### Verified inputs

- Water PC-SAFT, association, dielectric, and solvation records are printed in
  `docs/papers/md/ePC-SAFT-Literature/Figiel, Yu, Held - 2025 - Predicting Thermodynamic Properties of Ions in Single Solvents and in Mixe.md`.
- MEA molecular and association records plus MEA-water `k_ij=-0.052` are printed
  in `docs/papers/md/MEA/Baygi and Pahlavanzadeh - 2015 - Application of the PC-SAFT equation of state for modeling CO2 solub.md`.
- Held 2014 prints HCO3-, CO3^2-, H3O+, and OH- ion records and the listed
  water-ion interactions in
  `docs/papers/md/ePC-SAFT-Literature/Held et al. - 2014 - ePC-SAFT Revised.md`.
- Figiel 2025 prints the empirical relative-permittivity coefficient `7.01`,
  salt-free solvent mass-fraction basis, demonstrated total-ion-fraction limit,
  dielectric-saturation ion permittivity `8`, and the SSM+DS formulation.
- Source-branch reaction-constant tables trace R1-R5 to Nasrifar 2010 Table 1.
- Downstream fit commits identify the MEAH+/MEACOO- records and their mutual
  interaction as fitted snapshots rather than literature values.

### Imported evidence roles

| Source-branch artifact | Required role after migration |
|---|---|
| `phase2_speciation_activity_curves.csv` | `imported_downstream_model_snapshot` |
| `phase2_speciation_reference_points.csv` | `literature_observation` only after exact bibliography/table metadata is retained; otherwise unresolved and excluded from scoring |
| `phase2_speciation_target_roles.csv` | `imported_downstream_model_snapshot` |
| `phase2_activity_constant_candidates.csv` | source evidence |
| `phase2_reaction_constant_source_verification.csv` | source evidence |
| old generated results, plots, probe, and animation | imported historical snapshots, never current local predictions |

### Proven hard blockers at planning time

1. Branch CO2 segment count `2.079` conflicts with the retained literature
   value `2.0729`.
2. CO2 relative permittivity `1.4122` lacks an exact retained source.
3. MEA relative permittivity `32` lacks an exact retained source.
4. MEA and CO2 `f_solv=1` lack valid fitted or literature evidence.
5. The Figiel empirical dielectric correlation is demonstrated at 298.15 K,
   not across the branch's 293.15-353.15 K grid.
6. Component-permittivity and dielectric-saturation record domains do not yet
   cover 20-80 degrees Celsius.
7. The water sigma correlation needs a retained validity domain covering the
   requested grid.
8. Most zero `k_ij`, `l_ij`, and `k_hb_ij` cells lack exact row evidence or a
   cited structural-zero policy.
9. The old ion-dispersion behavior has no exact one-to-one mapping to the
   current formulation choices.

### Immutable execution grids

The source branch's static sampling coordinates are retained as coordinates,
not as solver seeds or proof of solution quality:

| Temperature (degrees Celsius) | Loading start | Loading end | Loading count |
|---:|---:|---:|---:|
| 20 | 0.020 | 0.795 | 161 |
| 40 | 0.005 | 0.800 | 161 |
| 60 | 0.001 | 0.800 | 161 |
| 80 | 0.001 | 0.800 | 161 |

The migrated animation grid is exactly 20, 40, 60, and 80 degrees Celsius at
loadings 0.10, 0.30, 0.50, and 0.70. The stale branch's 0 degree Celsius frame
is deliberately displaced because it lies outside the approved 20-80 degree
Celsius scope and retained evidence does not prove the active records at
273.15 K. Re-admitting that frame requires a later spec change and complete
domain evidence. Imported curve rows may be used as explicitly labeled
diagnostic seeds, but their loading coordinates do not replace the immutable
execution grid or support acceptance.

Tasks 4-10 are conditional on Task 3 closing every active blocker. If Task 3
cannot do so from traceable evidence, commit the blocked evidence ledger, keep
the executable input absent, and stop this plan without claiming migration
completion.

## Outcome Proof

**Intent:** Recover useful nonideal MEA evidence and plotting assets without
misrepresenting stale downstream curves as current Linux predictions or
reopening unsupported public equilibrium routes.

**Current Behavior:** The source branch uses a retired analysis path, loose
`user_options.json`, incomplete parameter provenance, an obsolete API call,
stale generated outputs, and false public-capability metadata; current `main`
keeps reactive speciation closed and requires strict typed model input.

**Expected Outcome:** Imported evidence is classified and retained in the
current layout; an executable bundle exists only when every active record and
temperature domain is proven; Linux generation writes exact receipts and
honest failure rows; table-only rendering produces verified plot bundles; and
public capability truth remains unchanged.

**Target Output:** Current-layout source tables, a source manifest and blocker
ledger, a strict typed input folder if evidence closes, Linux generation and
table-only rendering scripts, retained CSV/JSON/JSONL receipts, eight static
plot bundles, a complete-input-only animation preview/GIF bundle, MPLGallery registrations,
updated analysis documentation, and focused verification evidence.

**Owner:** M4 owns equilibrium and analysis behavior; M3 typed provider input
is consumed as an existing contract; the main thread owns Git integration,
review, cleanup, and branch decisions.

**Interface:** `epcsaft.Mixture.from_folder`,
`ResolvedModelInput.evaluate(temperature=..., composition=...)`,
`epcsaft.runtime_build_info()`, and
`epcsaft_equilibrium.workflows._run_standalone_ce_validation`.

**Cutover:** Useful source-branch assets move to
`analyses/package_validation/standalone_ce/.../{source,scripts,output}` only
after their roles are explicit; the current typed generator and table-only
renderer then displace the old loose loader and model-calling renderer.

**Replaced Path:** The retired paper-validation tree, `results/`,
`user_options.json`, hard-coded loose options, `from_dataset(...,
user_options=...)`, public `reactive_speciation`, separate animation solver,
and stale model-only output names are not carried forward.

**Evidence:** Exact literature Markdown sources, downstream fit receipts and
commit lineage, source manifests, typed definition/state receipts, Linux build
receipt, CE balance/stationarity results, plotted-data snapshots, MPLGallery
records, focused pytest results, strict docs, Ruff, diff review, and visual
inspection.

**Acceptance Proof:** Every active input record resolves with exact provenance
and a domain covering every executed state; every current-model row names the
local configuration fingerprint and solve result; each plot has matching
SVG/PNG/PDF/CSV artifacts; old paths and public routes remain absent; and the
focused tests and validators pass without touching the 20 deferred paper
failures.

**Stop Criteria:** Stop at the first unresolved scientific record, conflicting
source value, unsupported temperature domain, ambiguous formulation mapping,
unexpected native path, or missing plot snapshot. Retain a precise blocker
ledger and do not create executable inputs or current-model claims past that
point.

**Avoid:** Do not use silent values, inferred structural zeros, stale plots as
runtime proof, surname-only citations as literature identity, source-seeded
success as acceptance, or finite sampled states as global certification.

**Risk:** External evidence may not close the historical model's gaps, and a
scientifically honest run may still fail balance or stationarity; either result
must remain visible and can prevent completion while still yielding useful
classified evidence.

## Implementation Boundaries

**Files To Create:** Analysis-local evidence-role tests, classified source
tables, a blocker ledger, `source/model_input/model_configuration.json` and
`parameter_set.json` only after evidence closes, a Linux nonideal generator,
current prediction/receipt tables, eight static plot bundles, one animation
bundle only when its complete input contract passes, and their MPLGallery
records.

**Files To Modify:** The current standalone-CE source manifest, renderer,
analysis metadata/README, `tests/native/contracts/test_standalone_ce_gate.py`,
focused equilibrium capability/standard-state tests when required,
`tests/workflows/repo/test_project_structure.py`, and root
`.mplgallery/manifest.yaml`.

**Files To Avoid:** `analyses/paper_validation/standalone_ce`, the 20 deferred
Khudaida/Gross repairs, unrelated provider/regression code, downstream
repositories, release metadata, remote refs, and existing stashes.

**Source Of Truth:** Retained primary literature, explicit downstream fit
receipts identified by commit, the approved spec, current typed-input schemas,
current standalone-CE closed-capability metadata, and generated state receipts.

**Read Path:** Trace each proposed model field from literature or fitted receipt
to source manifest, typed parameter record, `Mixture.from_folder`, evaluated
state receipt, internal CE call, durable output row, and plotted snapshot.

**Write Path:** Add a failing analysis contract, classify or source the record,
write the minimal current-layout artifact, remove the displaced old-path
assumption, run focused verification, and commit one coherent checkpoint.

**Integration Points:** Provider configuration parsing/resolution, equilibrium
standard-state validation, internal native NLP activation, analysis generation,
Matplotlib rendering, MPLGallery discovery, docs, project layout gates, and Git
branch cleanup.

**Migration Or Cutover:** Adapt the useful content commit-by-commit onto local
`main`; never merge the stale branch tree. Delete the local source branch only
after all useful content and verification evidence are present.

**Replaced Path Handling:** Retain historical numbers only under explicit
imported roles; do not copy old generated results into current `output/` as
live evidence; remove all migrated loose/duplicate execution paths rather than
adding redirectors.

**Acceptance Proof Gate:** No checkpoint may call the migration complete until
its RED test is observed, GREEN verification passes, displaced paths are
absent, review findings are resolved, `git diff --check` is clean, and the
repository cleanup hook passes.

## Decision Ledger

| Decision | Reason | Consequence |
|---|---|---|
| Adapt, do not merge, the seven source-branch commits | Direct merge resurrects deleted paths and false capability metadata | Branch history stays separate; useful content is re-homed deliberately |
| Treat old curves as imported downstream snapshots | They predate the typed-input/native runtime | They may be compared but never labeled current model output |
| Keep reactive routes closed | Current balance/stationarity proof is incomplete | This migration cannot change public capabilities |
| Use one generator and one table-only renderer | Separates scientific execution from presentation and removes duplicate solver ownership | All model calls and animation-input tables occur before plotting |
| Require exact typed input and state receipts | Task 9 removed loose/default scientific input | Missing records stop execution at a named boundary |
| Make 20-80 degrees Celsius conditional on source domains | Figiel's empirical dielectric evidence is limited to 298.15 K | No extrapolation is permitted merely to recreate old plots |
| Preserve imported fitted provenance | MEAH+/MEACOO- values are downstream fits, not literature | Receipts must name their fitted lineage |
| Delay local branch deletion | Useful source material is not yet proven present on main | Delete only after final local verification; remote deletion remains separate |

## Test Complete And Metrics

- Analysis contract: every source/output row has one allowed evidence role and
  every literature row has exact source metadata.
- Typed input: all nine components resolve at every requested temperature and
  composition; definition and state fingerprints remain deterministic.
- Grid identity: static execution uses the four exact 161-point loading grids;
  animation execution uses the exact 16-state 20-80 degree Celsius grid, and
  the stale 0 degree Celsius frame is absent.
- Internal owner: every nonideal solve reaches the single internal NLP seam;
  public reactive imports remain absent.
- Scientific receipts: every solve records balance, stationarity, convergence,
  failure classification, temperature, loading, composition, and configuration
  fingerprint.
- Plot integrity: eight static plots have exact plotted-data snapshots and
  SVG/PNG/PDF siblings; the animation preview/GIF has matching input and preview
  data only when all 16 required states are valid.
- Artifact integrity: eight root MPLGallery entries always resolve to completed
  static files; a ninth animation-preview entry exists only after the complete
  animation input contract passes.
- Linux hygiene: no drive-letter path, backslash-only path, PowerShell command,
  Conda command, executable/DLL assumption, or retired options file appears in
  the migrated workflow.
- Capability truth: the standalone-CE checker remains blocked unless its strict
  balance/stationarity requirements genuinely pass; no public family is added.

## Implementation Tasks

### Task 1: Add Migration Contract Tests

**Owner:** M4 analysis contracts

**Use Cases:**

- A maintainer sees a failing proof when migrated assets use the retired path,
  loose options, unclassified rows, or Windows-only commands.
- Acceptance evidence checks require the current analysis tree and reject a
  duplicate/old execution path before migration begins.

**Files:**

- Create: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/migration_contract.json`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Write only the migration-boundary RED contracts**

  Assert a missing migration contract, then require source branch/base commit,
  current source/scripts/output roots, the four evidence roles, exact static
  and animation grids, deliberate displacement of the 0 degree Celsius frame,
  Linux-only commands, and absence of `user_options.json`, retired trees,
  public reactive imports, and old `results/` paths. Do not add future typed
  input, generator, plot, or gallery tests in this task.

- [ ] **Step 2: Prove RED**

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py tests/native/contracts/test_standalone_ce_gate.py tests/workflows/repo/test_project_structure.py -q
  ```

  Expected result: the migration test fails only because the machine-readable
  migration contract is absent.

- [ ] **Step 3: Add the immutable migration contract and reach GREEN**

  Write the exact branch lineage, current paths, roles, grids, excluded 0 degree
  Celsius frame, closed public routes, and Linux command contract. Refactor
  shared assertions inside the analysis test module; do not create a second
  repository-wide policy helper. Re-run the command and require zero failures.

- [ ] **Step 4: Checkpoint commit**

  Commit message: `test(validation): define nonideal MEA migration contracts`

### Task 2: Classify And Migrate Retained Source Evidence

**Owner:** M4 analysis evidence

**Use Cases:**

- A reviewer can distinguish literature observations, imported downstream
  model snapshots, diagnostic seeds, and current local predictions.
- Migration preserves useful branch evidence while old result artifacts and
  ambiguous citations remain displaced or explicitly excluded.

**Files:**

- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/source_manifest.csv`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/imported_downstream_model_snapshot.csv`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/imported_target_role_snapshot.csv`
- Create after citation completion: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/literature_speciation_observations.csv`
- Create if citations remain incomplete: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/unresolved_reference_observations.csv`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/phase2_activity_constant_candidates.csv`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/phase2_reaction_constant_source_verification.csv`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/phase2_reaction_constant_basis.csv`

- [ ] **Step 1: Add only row-role and citation RED cases**

  Require exact role values, source identity, table/figure locator, units, and
  exclusion reason for unresolved rows. Assert no old generated plot/result is
  classified as local output.

- [ ] **Step 2: Adapt source-branch tables**

  Copy numeric source rows deterministically from `f3057e11`, add only explicit
  role/source metadata, and preserve checksums or source-commit identities in
  the manifest.

- [ ] **Step 3: Verify GREEN**

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py -q
  ```

  Expected result: all tests introduced through Task 2 pass. Tests for typed
  execution, generation, plots, and registrations are not added until their
  owning tasks.

- [ ] **Step 4: Checkpoint commit**

  Commit message: `data(validation): classify retained nonideal MEA evidence`

### Task 3: Close Or Record The Scientific Input Evidence Gate

**Owner:** M4 scientific evidence, reviewed with `chemical-engineer`

**Use Cases:**

- A model-input reviewer can trace every active value, correlation domain,
  structural zero, reaction-constant domain/standard-state basis, and
  formulation choice to literature, a fitted receipt, or a cited defining
  model equation.
- If the migration cannot replace ambiguous old input, the repository gains a
  precise blocker artifact and execution stops before false current evidence.

**Files:**

- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/README.md`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/input_evidence_ledger.csv`
- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/reaction_input_evidence_ledger.csv`
- Create only if every active record closes: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/model_configuration.json`
- Create only if every active record closes: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/parameter_set.json`

- [ ] **Step 1: Add blocker mutation tests**

  Cover the CO2 segment-count conflict, missing CO2/MEA permittivity sources,
  neutral solvation factors, empirical/DS domains, water-sigma domain,
  interaction structural-zero evidence, ion-dispersion mapping, and each R1-R5
  reaction-constant correlation's temperature domain and standard-state basis.
  Each mutation must fail with the exact record identifier.

- [ ] **Step 2: Perform bounded source recovery**

  Search retained primary papers and the identified downstream fit receipts.
  Record source file, table/equation, value, provenance kind, domain, and
  current mapping. Historical runtime behavior and loose option defaults may
  be retained only as non-executable audit evidence. They cannot close an
  active value, zero, correlation, or formulation choice. Active records close
  only with exact literature evidence, a traceable fitted receipt, or a cited
  defining model/combining-rule equation.

- [ ] **Step 3: Apply the evidence gate**

  If all records close, write the strict configuration and parameter graph.
  If any blocker remains, keep those executable JSON files absent, write the
  exact blocked ledgers, run the negative tests, commit them with every test
  GREEN, and stop Tasks 4-10.

- [ ] **Step 4: Verify the gate**

  Blocked path, including the publication-safe line that omits paused Task 9:

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py tests/native/contracts/test_standalone_ce_gate.py tests/workflows/repo/test_project_structure.py -q
  ```

  Complete path, only after every evidence record closes and the typed provider
  contract is present:

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py packages/epcsaft/tests/api/frontend/test_formulation_records.py -q
  ```

  Expected result when evidence closes: typed input and all blocker mutations
  pass. Expected result when evidence remains incomplete: the blocked-path
  command passes by proving the named loud stop and absence of executable
  inputs without depending on unpublished Task 9 files.

- [ ] **Step 5: Checkpoint commit**

  Complete path: `data(model): define traceable nonideal MEA input`

  Blocked path: `docs(validation): record nonideal MEA input blockers`

### Task 4: Build The Strict Typed Input Loader

**Owner:** M4 analysis integration consuming M3 provider API

**Use Cases:**

- The migrated nine-component mixture loads only through the current
  configuration/parameter schema and evaluates deterministic state receipts.
- The typed cutover rejects retired files, unknown keys, unsupported domains,
  and any duplicate serializer or payload-side value insertion.

**Files:**

- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`
- Modify only if a general contract gap is proven: `packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py`
- Modify only if a general contract gap is proven: `packages/epcsaft/src/epcsaft/model/resolved_input.py`

- [ ] **Step 1: Write state-resolution RED tests**

  Load with `Mixture.from_folder(MODEL_INPUT_DIR, components=SPECIES_ORDER)` and
  evaluate the exact static and animation grids from `migration_contract.json`.
  Assert fingerprint, evaluated correlations, structural zeros, exact native
  mappings, source identities, and domain enforcement.

- [ ] **Step 2: Implement the smallest integration seam**

  Prefer analysis-only wiring. Change provider code only if the strict schema
  cannot represent an already sourced record; add its provider-level RED test
  first and do not add an analysis-specific shortcut.

- [ ] **Step 3: Verify GREEN and derivatives**

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py packages/epcsaft/tests/native/state/test_relative_permittivity_derivatives.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py -q
  ```

- [ ] **Step 4: Checkpoint commit**

  Commit message: `feat(validation): resolve typed nonideal MEA input`

### Task 5: Implement One Linux Data Generator Through The Internal NLP

**Owner:** M4 equilibrium analysis runtime

**Use Cases:**

- A Linux developer generates current model rows, exact configuration receipts,
  provider/equilibrium native freshness identities, and seed provenance through
  the single internal standalone-CE owner.
- Failed balance, stationarity, convergence, or input resolution remains a
  visible result row and cannot be replaced by a source seed or stale curve.

**Files:**

- Create: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_nonideal_data.py`
- Modify: `analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py`
- Modify if seam characterization is required: `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py`
- Modify if capability guard coverage is required: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Write generator RED tests**

  Characterize `Mixture.from_folder`, per-state receipt evaluation,
  `_run_standalone_ce_validation`, exact reaction/standard-state inputs,
  the immutable static/animation grids, failure-row persistence, full-set
  transactional promotion, no public import, and no second animation solver.
  Require every attempt to record initial-amount source, source temperature,
  source loading, attempt index, and whether an imported snapshot was used.

- [ ] **Step 2: Implement the generator**

  Use repository-relative `pathlib`, current typed input, and one solve owner.
  Create both `epcsaft.runtime_build_info()` and
  `scripts.validation.native_freshness.build_equilibrium_native_receipt(
  native_module=extension_native_core(), checker_command=...)`; call
  `require_equilibrium_native_fresh` before reproducible current rows are
  accepted. Generate the complete artifact set in ignored
  `output/runs/<run-id>/`, validate row counts, grid identity, fingerprints,
  receipt linkage, and source roles, then promote the complete curated set
  together. Any unexpected failure leaves the previous curated set untouched.
  Persist current predictions, static and animation solve summaries, animation
  input data, definition/state receipts, reaction constants, both runtime
  identities, seed provenance, and failure classifications.

- [ ] **Step 3: Verify GREEN**

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py tests/native/contracts/test_standalone_ce_gate.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
  ```

- [ ] **Step 4: Checkpoint commit**

  Commit message: `feat(validation): generate nonideal MEA Linux receipts`

### Task 6: Regenerate Current Model Tables And Receipts

**Owner:** M4 scientific execution

**Use Cases:**

- A reviewer can reproduce each current row from the retained typed input and
  Linux runtime receipt.
- Scientific rejection is retained as evidence, while stale imported curves
  stay visibly separate from current local results.

**Files:**

- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_current_local_predictions.csv`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_solve_summary.csv`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_generation_summary.json`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_configuration_receipts.jsonl`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_linux_runtime_receipt.json`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/phase2_eos_x_gamma_reaction_constants.csv`
- Create/regenerate when every required animation state is valid: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_speciation_temperature_sweep_animation_data.csv`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_speciation_temperature_sweep_solve_summary.csv`
- Create/regenerate: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/mea_ce_eos_x_gamma_speciation_temperature_sweep_solve_summary.json`

- [ ] **Step 1: Build the equilibrium profile**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium
  ```

  Expected result: current Linux provider and equilibrium native modules build
  and import from the active checkout.

- [ ] **Step 2: Run the generator**

  ```bash
  uv run --no-sync python analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_nonideal_data.py
  ```

  Expected result: zero exit only after a structurally valid complete artifact
  set is promoted. Individual scientific rejections remain rows and make any
  affected plot/animation incomplete. Missing input, unsupported domains,
  stale equilibrium native identity, or unexpected native-path failure exits
  nonzero without changing the previous curated set.

- [ ] **Step 3: Verify receipts and metrics**

  Run the focused analysis and gate tests. Confirm every exact static state and
  all 16 animation states appear in solve summaries, the 0 degree Celsius frame
  is absent, each attempt carries seed provenance, every current row carries
  the configuration fingerprint, and the provider/equilibrium receipts match
  the current checkout. Create animation input data only when all 16 required
  states are valid; otherwise retain the failure summary and treat the
  animation as incomplete.

- [ ] **Step 4: Checkpoint commit**

  Commit message: `data(validation): retain nonideal MEA Linux predictions`

### Task 7: Render Static Figures And Animation From Tables Only

**Owner:** M4 analysis plotting

**Use Cases:**

- A user can compare literature observations, imported downstream snapshots,
  current local predictions, and failed states without relying on color alone.
- Plot regeneration is displaced from model execution and reproduces exact
  SVG/PNG/PDF/CSV siblings plus the animation preview and GIF only when their
  complete generator-owned input exists.

**Files:**

- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py`
- Create/regenerate: eight `output/mea_ce_eos_x_gamma_speciation_{concentrated|trace}_{20|40|60|80}C.{svg,png,pdf,csv}` bundles
- Create/regenerate only when the complete animation input exists: `output/mea_ce_eos_x_gamma_speciation_temperature_sweep.gif`
- Create/regenerate only when the complete animation input exists: `output/mea_ce_eos_x_gamma_speciation_temperature_sweep_preview.{svg,png,pdf,csv}`

- [ ] **Step 1: Write renderer RED tests**

  Reject imports of `epcsaft` or `epcsaft_equilibrium`, missing role styles,
  missing failure annotations, incomplete siblings, and plot data that differ
  from the durable generation tables. Assert the renderer only reads the
  generator-owned animation data/solve summary and never writes scientific
  solve tables.

- [ ] **Step 2: Implement table-only rendering**

  Use distinct marker/line styles, print-readable labels, explicit units and
  temperatures, role-aware legends, and visible failed-state annotations.
  Render the GIF/preview only when all 16 generator-owned animation states are
  present and valid. If any state is missing or rejected, retain the generator
  failure summary, create no animation presentation artifact, and report the
  incomplete animation as a migration blocker.

- [ ] **Step 3: Render and verify**

  ```bash
  uv run --no-sync python analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py -q
  ```

- [ ] **Step 4: Inspect every changed plot**

  Open all eight SVGs and, when complete, the animation preview and GIF. Check
  clipping, legends, units, role differentiation, and consistency with retained
  tables. An absent animation caused by a rejected/missing state is reviewed as
  a blocker, not replaced with partial frames.

- [ ] **Step 5: Checkpoint commit**

  Commit message: `docs(validation): render nonideal MEA comparison plots`

### Task 8: Register Plot Bundles And Preserve Capability Truth

**Owner:** M4 analysis/docs integration

**Use Cases:**

- MPLGallery discovers every truthful completed plot through exact
  current-layout paths and plotted-data snapshots.
- Repository documentation visibly preserves the closed public route and
  replaces stale branch completion claims with current receipt-based truth.

**Files:**

- Modify: `.mplgallery/manifest.yaml`
- Modify: `analyses/package_validation/standalone_ce/analysis.yaml`
- Modify: `analyses/package_validation/standalone_ce/README.md`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Modify user-facing docs only if commands/capability text changes: `docs/pages/development_workflows.rst`

- [ ] **Step 1: Add registration/capability RED tests**

  Require eight static manifest rows plus the animation-preview row only when
  its complete 16-state input exists. Require current paths, existing sibling
  files, source and plotted-data links, closed public routes, provider and fresh
  equilibrium runtime receipts, diagnostic-seed provenance, and honest
  blocked/accepted CE metrics. Source-seeded success must never support
  capability admission.

- [ ] **Step 2: Register and document**

  Append eight static plot entries. Append the animation preview only when its
  complete input contract passes; otherwise document the incomplete animation
  and leave it unregistered. Update analysis metadata and README with Linux
  commands, evidence roles, exact model-input fingerprint, both runtime
  identities, seed provenance limits, and current scientific result without
  admission language.

- [ ] **Step 3: Verify GREEN**

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py tests/native/contracts/test_standalone_ce_gate.py tests/workflows/repo/test_project_structure.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
  uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
  ```

  Expected checker result in this migration scope: exit code 1 with structured
  blocked JSON matching the retained live balance/stationarity failure and no
  broadened capability. A zero exit is accepted only if an independently
  reviewed, in-scope strict proof genuinely changes the scientific result; do
  not repair or admit the route merely because this command returns nonzero.

- [ ] **Step 4: Checkpoint commit**

  Commit message: `docs(validation): register nonideal MEA evidence`

### Task 9: Run Focused Verification And Independent Review

**Owner:** Main-thread integration

**Use Cases:**

- A reviewer receives fresh provider, equilibrium, analysis, docs, plotting,
  and Linux-path evidence without invoking deferred paper repairs.
- Independent review can reject a false migration-complete claim before branch
  cleanup or any later publication decision.

**Files:**

- Modify only for verified findings: files owned by Tasks 1-8
- Create temporarily outside commits: review package under `.superpowers/`

- [ ] **Step 1: Run focused tests**

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/standalone_ce/tests/test_nonideal_figure_workflow.py tests/native/contracts/test_standalone_ce_gate.py packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py packages/epcsaft/tests/api/frontend/test_formulation_records.py packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py packages/epcsaft/tests/native/state/test_relative_permittivity_derivatives.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/workflows/repo/test_project_structure.py -q
  ```

- [ ] **Step 2: Run static/docs checks**

  ```bash
  uv run --no-sync ruff check analyses/package_validation/standalone_ce packages/epcsaft/src/epcsaft/model packages/epcsaft-equilibrium/src/epcsaft_equilibrium tests/native/contracts/test_standalone_ce_gate.py tests/workflows/repo/test_project_structure.py
  uv run python scripts/dev/validate_project.py docs
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

- [ ] **Step 3: Request independent scientific and code review**

  Review source roles, active record provenance/domains, typed receipts, the
  internal owner, failure semantics, plot/table consistency, closed capability
  truth, and absence of retired paths. Apply only verified findings under TDD.

- [ ] **Step 4: Re-run affected checks and commit review fixes**

  Commit message: `fix(validation): close nonideal MEA review gaps`

### Task 10: Complete Local Integration And Retire Superseded Local Branches

**Owner:** Main-thread Git integration

**Use Cases:**

- Local `main` contains every proven useful source-branch artifact and no stale
  duplicate path before the source branch is retired.
- The handoff shows exact commits, validation, scientific result, deferred
  failures, stashes, branches, and clean status without pushing paused work.

**Files:**

- Modify only if final verification finds drift: Task 1-9 owned paths
- Remove temporary review package: `.superpowers/`

- [ ] **Step 1: Prove source-branch coverage**

  Compare `f3057e11` source/data/plot intent against current-layout artifacts.
  Confirm old results are either classified imported inputs or deliberately
  displaced, not silently lost or mislabeled.

- [ ] **Step 2: Verify final local state**

  ```bash
  git status --short --branch
  git branch -vv
  git stash list
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

- [ ] **Step 3: Delete only superseded local branches**

  Record both local tip commit IDs and prove content coverage first. Because
  these adapted branches are not ancestors of `main`, a forced local branch
  deletion is permitted only after useful content is proven present, the
  matching remote refs are confirmed intact, and all stashes are preserved.
  Delete `codex/m4-ce-nonideal-speciation-plots` only after this migration is
  complete. Treat deletion of `codex/m4-ce-downstream-one-nlp-issue-updates` as
  separately audited prior-work cleanup after `bedeeaac` is verified as its
  complete useful replacement; it is not scientific acceptance evidence for
  this migration.

- [ ] **Step 4: Commit final tracked fixes only when present**

  If final verification produced real tracked fixes, commit them as
  `chore(validation): complete local nonideal MEA migration`. Branch deletion
  alone creates no tracked diff and must not produce an empty commit.

- [ ] **Step 5: Handoff without push**

  Report commits, exact test/checker results, any retained scientific rejection,
  remaining Task 9 paper failures, worktree status, branches, stashes, and
  publication boundary. Render every changed plot inline with absolute paths
  and compact real-data tables.

## Proof Oracle

The migration is complete only when Tasks 1-10 pass, every active scientific
record and executed domain is traceable, current Linux outputs are regenerated,
all plot bundles are visually verified, public capabilities remain closed, the
source branch is fully displaced, and Git is clean. If Task 3 records unresolved
evidence, the correct outcome is a locally committed blocked-evidence checkpoint
with Tasks 4-10 unexecuted and the source branch retained.
