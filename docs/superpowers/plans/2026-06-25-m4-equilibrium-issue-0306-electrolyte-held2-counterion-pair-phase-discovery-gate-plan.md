# Electrolyte HELD2 Counterion-Pair Phase-Discovery Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #306 by adding the next #191 electrolyte gate:
native HELD2 phase-discovery diagnostics in reduced electroneutral coordinates
with independent counterion-pair bookkeeping and mean-ionic residual evidence.

**Architecture:** This is a phase-discovery gate, not Stage III electrolyte
refinement or public electrolyte route admission. The native equilibrium core
must build the independent counterion-pair matrix for active charged species,
use it to generate charge-neutral trial/candidate coordinates, report reduced
TPD/candidate evidence, and expose mean-ionic residual bookkeeping for later
Stage III and postsolve gates. The retained checker consumes #269, #300, and
#302 before granting completion.

**Tech Stack:** C++ equilibrium native core, pybind11 bindings, Python
validation checker, pytest contracts through `run_pytest.py`, M4 issue mirrors,
M4 benchmark registry, GitHub dependencies.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/306`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md`
- Source Plan: `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md`
- Prior Child Gate: `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0302-add-electrolyte-charge-neutral-tpd-gate.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Replace the open HELD2 phase-discovery blocker with a retained
native diagnostic that uses paper-derived reduced electroneutral coordinates.
**Current Behavior:** `_native_electrolyte_tpd_phase_discovery` performs
deterministic charge-neutral TPD screening for the Khudaida NaCl fixture but
does not build the general counterion-pair matrix, run HELD2 phase discovery,
or report mean-ionic residual rows.
**Expected Outcome:** A retained checker exits successfully only when #269,
#300, and #302 pass; native diagnostics report a full-rank counterion-pair
matrix, charge-neutral reduced-coordinate candidates, finite TPD metrics, and
mean-ionic residual bookkeeping; public electrolyte routes stay closed.
**Target Output:** `scripts/validation/check_electrolyte_held2_phase_discovery.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-native-held2-discovery --require-public-routes-closed --require-complete` returns `complete: true` with no blockers.
**Owner:** M4 equilibrium package owner.
**Interface:** Native `_native_electrolyte_held2_phase_discovery` binding,
retained checker JSON, pytest contracts, M4 issue mirror, registry row, and M4
README.
**Cutover:** The new checker becomes the #306 proof oracle and removes the
HELD2 phase-discovery blocker from #191 after merge.
**Replaced Path:** The current charge-vector projection TPD screen remains a
seed gate; the new path adds independent counterion-pair reduced coordinates
and discovery metadata that later Stage III can consume.
**Evidence:** Failing-then-passing native contract tests, checker JSON,
counterion-matrix rank receipts, mean-ionic residual receipts, docs validation,
and GitHub issue/PR closure evidence.
**Acceptance Proof:** Acceptance is proven when the native diagnostic records a
full-rank `N_ch - 1` counterion-pair matrix, charge-neutral candidate rows,
finite discovery metrics, mean-ionic residual bookkeeping, closed public route
state, and explicit pending Stage III/postsolve/admission gates.
**Stop Criteria:** Stop if the native path cannot construct a full-rank
counterion-pair matrix for the active charged species, if candidate generation
leaves the electroneutral subspace, if charged transfer equilibrium is checked
with raw single-ion chemical potentials, or if public route admission becomes
necessary to complete the gate.
**Avoid:** Do not add Stage III electrolyte refinement, postsolve certification,
public electrolyte LLE/TP-flash routes, reactive routes, regression work,
downstream study logic, or release claims.
**Risk:** A phase-discovery diagnostic can be mistaken for a solved electrolyte
route; all evidence must keep discovery, refinement, certification, and public
admission separate.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_electrolyte_held2_phase_discovery.py`, `tests/native/contracts/test_electrolyte_held2_phase_discovery.py`, and source-backed preprocessor fixture files only if existing local data cannot express the multi-ion counterion matrix case.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`, `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`, `tests/native/contracts/test_generalized_equilibrium_registry.py`, `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`, `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md`, `docs/superpowers/milestones/M4-equilibrium/README.md`, and `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`.
**Files To Avoid:** Public route maps beyond closed-state assertions,
regression package files, downstream repositories, generated build trees, and
provider EOS implementation internals.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, Stage 14/15 electrolyte
plan, the local 2022 multiphase electrolyte methodology markdown, #269 source
gate, #300 readiness gate, and #302 TPD gate.
**Read Path:** Read Khudaida data through `check_electrolyte_gfpe_gate.py`,
read readiness through `check_electrolyte_held2_readiness.py`, read TPD
screening through `check_electrolyte_tpd_gate.py`, and read counterion-pair
requirements from the local paper markdown.
**Write Path:** Write one native diagnostic entrypoint, one checker, one
contract test module, capability/registry evidence rows, and tracker updates.
**Integration Points:** `evaluate_electrolyte_tpd_phase_discovery`,
`NeutralPhaseDiscoveryResult`, pybind11 registration, extension stubs,
capability evidence, and M4 registry evidence.
**Migration Or Cutover:** #191 remains blocked by #306 until this PR merges;
after merge, dependency readiness should expose Stage III electrolyte refinement
as the next child gate.
**Replaced Path Handling:** Keep the #302 TPD checker as prerequisite evidence
and seed support; do not rewrite it into a route-quality certificate.
**Acceptance Proof Gate:** The proof oracle commands below must pass before
push, PR creation, merge, and issue close.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Next child | Live M4 queue plus #191 blocker state | #306 owns HELD2 counterion-pair phase discovery. | Converts the next #191 blocker into a PR-sized issue. | No | M4 owner |
| Coordinate basis | 2022 electrolyte methodology | Use an independent counterion-pair matrix with rank `N_ch - 1`. | Prevents hardcoded one-salt NaCl logic from becoming the HELD2 gate. | No | M4 owner |
| Charged transfer residuals | Electrolyte equilibrium equations | Track mean-ionic residual rows, not raw single-ion equality. | Aligns candidate evidence with electrolyte thermodynamics. | No | M4 owner |
| Public route state | GFPE doctrine | Keep `electrolyte_lle` closed. | Avoids unsupported user-facing capability claims. | No | M4 owner |
| Stage III | #191 acceptance sequence | Defer electrolyte reduced-variable refinement to the next child. | Keeps #306 focused on phase discovery. | Yes | M4 owner |

## Diagnostic Payload Contract

The #306 checker must reject a native payload unless it records the following
groups with source-backed values and finite numeric receipts:

- `algorithm_scope`: `held2_counterion_pair_phase_discovery_only`.
- `source_gates`: `khudaida_2026_source_gate_complete`,
  `held2_readiness_gate_complete`, and `electrolyte_tpd_gate_complete`.
- `charged_species`: charged species labels, explicit charges, active charged
  species indices, cation indices, anion indices, and the charged feed ordering
  used by the counterion-pair preprocessor.
- `counterion_pairs`: pair labels, counterion-pair matrix, row sums, matrix
  rank, expected rank `N_ch - 1`, rank tolerance, and transformed variable
  count.
- `electroneutral_lift`: lift matrix, lifted candidate compositions, per-phase
  charge residual maximum, component nonnegativity margin, composition-sum
  residual, and lift/back-lift round-trip residual.
- `reduced_tpd`: coordinate basis label
  `counterion_pair_transformed_variables`, reduced start count, converged start
  count, selected candidate count, minimum TPD, duplicate-candidate distance,
  and candidate-to-feed distance.
- `mean_ionic_residuals`: pair labels, residual values, residual scale,
  maximum absolute residual, and an explicit `bookkeeping_only_until_stage_iii`
  status.
- `stage_statuses`: `phase_discovery_complete`,
  `stage_iii_refinement_pending`, `postsolve_certification_pending`, and
  `public_route_admission_closed`.
- `source_fixtures`: the Khudaida NaCl fixture and a multi-ion fixture from the
  local mixed-solvent mixed-electrolyte source context, especially the
  water + 1-butanol + NaCl + KCl Table 5 case with Na+/Cl- and K+/Cl- pairs.

The checker must fail if the payload only contains a hardcoded NaCl pair, if a
multi-ion fixture is absent, if raw single-ion transfer equality appears in
acceptance evidence, if a required prerequisite checker is incomplete, or if
any Stage III, postsolve, or public-admission status is marked complete.

## Required Contract Tests

- `test_counterion_pair_matrix_rank_single_salt`: Na+/Cl- builds one row with
  rank `1`, expected rank `1`, and inverse-valence row entries.
- `test_counterion_pair_matrix_rank_common_anion`: Na+/K+/Cl- builds two
  independent rows for Na+/Cl- and K+/Cl- with rank `2`.
- `test_counterion_pair_matrix_multivalent_source_example`: K+/Cl-/Na+/SO4--,
  ordered by feed abundance from the methodology example, builds a `3 x 4`
  full-rank matrix and uses the sulfate `1/2` inverse-valence coefficient.
- `test_reduced_lift_keeps_charge_zero`: random transformed-coordinate samples
  lift to explicit-ion compositions with maximum charge residual <= `1.0e-10`.
- `test_reduced_lift_round_trip_is_stable`: lifted candidates can be projected
  back to transformed coordinates within the declared round-trip tolerance.
- `test_mean_ionic_rows_are_pair_based`: charged transfer diagnostics expose
  pair residual labels and reject raw single-ion residual rows as acceptance
  evidence.
- `test_phase_discovery_payload_rejects_stage_iii_claims`: the checker rejects
  payloads that mark Stage III refinement, postsolve certification, or public
  route admission complete under #306.
- `test_checker_consumes_prerequisite_gates`: incomplete #269, #300, or #302
  payloads produce blockers before native HELD2 discovery evidence is read as
  complete.
- `test_public_electrolyte_routes_stay_closed`: capability and registry
  evidence keep `electrolyte_lle` outside public and production route families.
- `test_ascani_2022_table5_fixture_loaded`: the multi-ion source fixture is
  available to tests with water, 1-butanol, NaCl, and KCl feed metadata and
  mean-ionic pair labels.

## Stage III Handoff Contract

#306 must emit a candidate-set record that the next electrolyte refinement
child can consume directly. The handoff record must include phase amount
estimates, explicit-ion phase compositions, reduced transformed coordinates,
phase kind labels, counterion-pair matrix, mean-ionic pair labels, source
fixture id, TPD values, and `pending_stage_iii_refinement`. The next child then
owns the equation solve for neutral transfer residuals, mean-ionic transfer
residuals, material balance in reduced coordinates, pressure consistency,
strict derivative evidence, and postsolve certification.

## Acceptance Criteria

- [ ] A local mirror exists for #306 and #191 is blocked by #306 on GitHub.
- [ ] Native equilibrium exposes `_native_electrolyte_held2_phase_discovery`.
- [ ] The native payload reports charged-species indices, charge vector,
  counterion-pair matrix, matrix rank, transformed-variable dimension, and
  charge-neutral lift/back-lift residuals.
- [ ] The native payload satisfies the Diagnostic Payload Contract and emits a
  Stage III handoff record that does not claim refinement completion.
- [ ] At least one NaCl source-backed fixture and one multi-ion or
  mixed-electrolyte source-backed preprocessor fixture exercise the matrix
  construction.
- [ ] Single-salt, common-anion, and multivalent counterion-pair matrix tests
  prove full-rank construction for the required source and methodology cases.
- [ ] Reduced-coordinate lift/back-lift tests prove charge residual,
  nonnegativity margin, composition-sum residual, and round-trip residual
  tolerances.
- [ ] Candidate phase-discovery metrics are finite and include selected
  candidate count, minimum TPD, candidate charge residuals, and pending
  Stage III/postsolve/admission gates.
- [ ] Mean-ionic residual bookkeeping exists for candidate phase sets.
- [ ] Raw single-ion charged-transfer equality is rejected as acceptance
  evidence.
- [ ] The retained checker consumes #269, #300, and #302 evidence before
  granting completion.
- [ ] Capabilities and registry evidence keep public electrolyte routes closed.
- [ ] #191 and M4 README show #306 as closed after merge and list the remaining
  Stage III, postsolve, and public-admission blockers.

## Non-Goals

- No public `electrolyte_lle` route admission.
- No Stage III electrolyte Ipopt refinement.
- No postsolve electrolyte phase-set certification cutover.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.
- No provider EOS rewrite.

## Tasks

### Task 1: Publish And Verify Tracker State

**Use Cases:**
- A milestone reviewer needs historical evidence that #191 was blocked by #306
  while HELD2 phase discovery was open.
- A resolver needs a local #306 mirror with acceptance criteria, proof oracle,
  and cutover boundaries.
- Dependency readiness needs visible evidence that #306 closed before #312
  became the active Stage III blocker and that #269/#300/#302 are closed
  provenance.

**Files:**
- `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md`
- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`

- [x] Confirm #306 closed with retained phase-discovery evidence and blocks
  #191 only as historical dependency provenance.
- [x] Confirm #191 moves to #312/#313/#314 as the remaining blockers after
  #306 closes.
- [x] Update local mirrors and the M4 README with the next active blocker.

### Task 2: Add Counterion-Pair Matrix Contracts

**Use Cases:**
- Native tests must fail until charged species are converted into a full-rank
  independent counterion-pair matrix.
- The test suite must prove multi-ion coordinate construction, not only the
  one-salt NaCl lift from #300.
- The contract must record acceptance evidence and the old one-salt path it
  replaces for HELD2 phase discovery.

**Files:**
- `tests/native/contracts/test_electrolyte_held2_phase_discovery.py`
- `scripts/validation/check_electrolyte_held2_phase_discovery.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`

- [ ] Add tests for the native binding shape and counterion-pair matrix rank.
- [ ] Add tests for NaCl and multi-ion source-backed preprocessor fixtures.
- [ ] Add checker schema tests for reduced-coordinate and mean-ionic fields.
- [ ] Add matrix tests for Na+/Cl-, Na+/K+/Cl-, and K+/Cl-/Na+/SO4--
  inverse-valence rows.
- [ ] Add checker-negative tests for incomplete prerequisite gates, raw
  single-ion charged-transfer rows, and premature Stage III/postsolve/public
  admission statuses.

### Task 3: Implement Native HELD2 Discovery Diagnostics

**Use Cases:**
- The native core must generate charge-neutral candidate coordinates from the
  independent counterion-pair matrix.
- Candidate evidence must be consumable by later Stage III electrolyte
  refinement.
- The new diagnostic must displace the current hardcoded charge projection as
  the HELD2 discovery gate while keeping it available as TPD seed evidence.
- The replaced path must remain visible so reviewers can see that #302 screening
  is seed evidence, not route-quality phase discovery.

**Files:**
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`

- [ ] Implement charged-species ordering and counterion-pair matrix assembly.
- [ ] Add reduced-coordinate trial/candidate lifting and charge checks.
- [ ] Add mean-ionic residual bookkeeping for candidate phase sets.
- [ ] Add explicit Stage III handoff fields: phase amount estimates,
  explicit-ion compositions, transformed coordinates, phase kinds, pair labels,
  source fixture id, and TPD values.
- [ ] Bind the diagnostic as `_native_electrolyte_held2_phase_discovery`.

### Task 4: Add The Retained Checker And Capability Evidence

**Use Cases:**
- The proof oracle must fail closed if #269, #300, or #302 regresses.
- The M4 registry must show phase-discovery evidence separately from Stage III
  and public route evidence.
- Users must not see public electrolyte support after this gate.

**Files:**
- `scripts/validation/check_electrolyte_held2_phase_discovery.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- `tests/native/contracts/test_generalized_equilibrium_registry.py`
- `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`

- [ ] Consume #269, #300, and #302 checker payloads.
- [ ] Record finite native HELD2 discovery metrics and residual bookkeeping.
- [ ] Verify the checker schema against the Diagnostic Payload Contract before
  returning `complete: true`.
- [ ] Keep `electrolyte_lle` absent from public routes and production families.
- [ ] Add registry/capability rows that name this as phase-discovery evidence.

### Task 5: Verify, Commit, PR, Merge, And Sync

**Use Cases:**
- The child issue must close through a PR with proof, not local-only evidence.
- The repo must return to clean synced `main` after merge.
- Dependency readiness must move #191 to the next electrolyte gate state after
  #306 closes.

**Files:**
- All files changed by Tasks 1-4.

- [ ] Run the proof oracle commands.
- [ ] Run the repo cleanup hook.
- [ ] Commit, push, open a PR that closes #306, and merge after clean proof.
- [ ] Sync local `main`, remove owned branches/worktrees, and run dependency
  readiness sync.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_electrolyte_held2_phase_discovery.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-native-held2-discovery --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_held2_phase_discovery.py tests/native/contracts/test_electrolyte_tpd_gate.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
