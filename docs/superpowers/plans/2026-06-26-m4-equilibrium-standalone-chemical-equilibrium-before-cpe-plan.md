# Standalone Chemical Equilibrium Before CPE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Build standalone homogeneous chemical/speciation equilibrium for
M4 before any simultaneous phase-plus-chemistry production route.

**Architecture:** The tranche promotes the existing CE placeholder into a
validated standalone method, then leaves CPE as a blocked downstream coupling
contract. Work proceeds through schema, standard-state, native residual/NLP,
algorithm, oracle, API, validation, and activation gates, with CPE limited to
an interface contract until both PE and CE proof chains exist.

**Tech Stack:** `packages/epcsaft-equilibrium`, C++ native equilibrium blocks,
pybind11 bindings, Python workflow/result surfaces, Ipopt, CppAD metadata,
Cantera/Pope reference fixtures, M4 registry/docs, pytest through
`run_pytest.py`, retained validation checkers, GitHub issue mirrors.

---

## Intake

- Source Spec:
  `docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md`
- Source Issue:
  `docs/superpowers/issues/2026-06-26-m4-ce-issue-0321-m4-ce-standalone-chemical-speciation-equilibrium-foundation-before-cpe.md`
- Source Plan:
  `docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/321`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- AFK/HITL: `AFK for the first eight implementation slices after issue mirrors
  are validated; HITL for activation and CPE coupling review gates`

## Outcome Proof

**Intent:** Create a source-backed, standalone CE/speciation implementation path
that can be executed issue by issue before CPE work begins.
**Current Behavior:** CE and CPE exist as planning placeholders; the native
reaction block and retained Ascani evidence are useful seeds, but the standalone
CE family lacks a complete schema, standard-state contract, derivative-backed
solver contract, oracle harness, public result schema, and activation gate.
**Expected Outcome:** A tracking issue and child issue set can drive CE from
placeholder status to a validated homogeneous equilibrium method while keeping
reactive LLE and reactive electrolyte LLE closed.
**Target Output:** `reactive_speciation` becomes eligible for production
exposure only after the standalone CE checker reports explicit standard-state
metadata, conservation residuals, reaction affinity residuals, derivative
evidence, oracle comparisons, retained literature validation, and capability
scope boundaries.
**Owner:** M4 equilibrium package owner.
**Interface:** M4 CE source plan, issue mirrors, activation matrix, CE request
schema, native reaction/speciation blocks, public CE result schema, validation
checker JSON, registry evidence, and capability payload.
**Cutover:** Replace the placeholder-only CE state with a gated standalone CE
route after all CE evidence closes; keep `reactive_lle` and
`reactive_electrolyte_lle` closed until separate CPE issues prove simultaneous
phase-plus-chemistry behavior.
**Replaced Path:** The old route-gate evidence and ideal reaction smoke tests
remain historical seeds; they no longer stand in for the standalone CE family
proof.
**Evidence:** Plan validators, GitHub tracking issue, child issue mirrors,
native unit tests, contract tests, oracle comparison JSON, retained validation
artifacts, activation/capability tests, registry evidence, docs validation, and
cleanup proof.
**Acceptance Proof:** Acceptance is proven when the issue set exists, the
standalone CE checker passes against source-backed fixtures, capability payloads
expose only CE scope, and CPE issue mirrors remain blocked by both CE and PE
validation gates.
**Stop Criteria:** Stop if standard-state conventions remain implicit, if
reaction-set rank or conservation basis behavior is ambiguous, if exact
derivative evidence is missing for an exposed route, or if a staged CE plus PE
solve is treated as CPE proof.
**Avoid:** Do not claim reactive LLE, reactive electrolyte LLE, downstream
application metrics, regression capability, release readiness, or CPE
production support from standalone CE evidence.
**Risk:** The main risk is overbroad capability language; every issue must keep
CE, PE, and CPE proof separate.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_standalone_ce_gate.py`,
`tests/native/contracts/test_standalone_ce_gate.py`,
`packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py`,
`packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`,
`packages/epcsaft-equilibrium/tests/native/blocks/test_chemical_equilibrium_blocks.py`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/chemical_equilibrium_block.h`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/chemical_equilibrium_block.cpp`,
`analyses/reference_oracles/chemical_equilibrium/cantera_pope_reference_cases.json`,
and issue mirrors under `docs/superpowers/issues/`.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/reaction_block.cpp`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/reaction_block.h`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`,
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`,
`docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`,
`docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`,
`docs/pages/development_workflows.rst`, and M4 issue/README files.
**Files To Avoid:** `packages/epcsaft-regression/**`,
downstream project repositories, release metadata, provider EOS internals
unless a public provider contract receipt is consumed, generated build trees,
and any public route claiming CPE support.
**Source Of Truth:** The source spec, M4 GFPE doctrine, M4 registry, existing
activation matrix, Ascani 2023 retained evidence, Cantera equilibrium docs, and
Pope 2004 constrained CE paper.
**Read Path:** Read the source spec, registry CE/CPE rows, activation matrix
reactive rows, reaction block tests, Ascani retained summaries, Cantera/Pope
oracle notes, and current capability tests before each issue.
**Write Path:** Write one vertical slice per child issue with tests, docs,
registry, capability evidence, and retained validation artifacts as required by
that slice.
**Integration Points:** Activation matrix, selector admission, native blocks,
pybind bindings, Python request/result schemas, capability payloads, M4
registry, validation scripts, and issue mirrors.
**Migration Or Cutover:** Keep CE closed until the CE activation gate passes;
open only `reactive_speciation` after proof, and keep CPE/reactive phase routes
closed until later CPE issue sets prove simultaneous coupled behavior.
**Replaced Path Handling:** Demote old prototype route-gate evidence to
historical input evidence and require the new standalone CE checker for any
future capability claim.
**Acceptance Proof Gate:** The proof oracle commands in this plan and the issue
mirrors must pass before issue close, PR merge, and capability broadening.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Initial scope | Native planning grill, 2026-06-26 | CE first; CPE only as a downstream interface contract. | Prevents combined reactive LLE work from hiding missing CE foundations. | No | M4 owner |
| Issue granularity | Native planning grill, 2026-06-26 | One tracking issue plus ten child issues. | Matches the committed source spec and keeps slices independently grabbable. | No | M4 owner |
| Proof policy | Native planning grill, 2026-06-26 | Strict gates with standard states, derivatives, oracles, retained validation, and capability gating. | Keeps scientific claims evidence-backed. | No | M4 owner |
| Activation boundary | M4 registry and GFPE doctrine | CE activation can open only `reactive_speciation`; CPE routes remain closed. | Avoids phase-equilibrium capability drift. | No | M4 owner |
| CPE dependency | Source spec and Ascani/Perdomo evidence | CPE depends on both CE proof and PE/stability proof. | Keeps staged CE plus PE out of production proof. | No | M4 owner |

## Required Contract Tests

- `test_ce_registry_placeholders_have_explicit_gates`: CE and CPE registry rows
  remain separate until their gates close.
- `test_reaction_schema_rejects_rank_ambiguous_basis`: invalid or ambiguous
  conservation bases fail loudly.
- `test_standard_state_required_for_reaction_residual`: no reaction residual is
  evaluated without an explicit standard-state record.
- `test_homogeneous_ce_reports_balance_and_affinity_residuals`: standalone CE
  returns conservation, charge when relevant, and affinity diagnostics.
- `test_ce_derivative_metadata_is_exact_for_admitted_route`: admitted CE route
  reports exact Jacobian and Hessian evidence.
- `test_cantera_pope_oracles_are_ce_only`: oracle fixtures cannot be used as
  LLE/CPE proof.
- `test_reactive_speciation_result_schema_is_ce_only`: public result fields do
  not claim phase-split behavior.
- `test_standalone_ce_gate_rejects_missing_evidence`: the retained checker
  rejects missing schema, standard-state, solver, oracle, validation, or
  activation evidence.
- `test_cpe_contract_requires_ce_and_pe_gates`: CPE interface docs and
  registry rows remain blocked until both proof chains exist.

## Acceptance Criteria

- [ ] GitHub tracking issue and ten child issues exist under `M4 - Equilibrium`
  with package scope `packages/epcsaft-equilibrium`.
- [ ] Local issue mirrors validate for every published issue.
- [ ] CE/CPE boundary docs and registry rows are explicit and tested.
- [ ] Reaction-set schema and conservation-basis compiler are tested for
  neutral, charged, rank-deficient, and impossible-basis cases.
- [ ] Standard-state registry prevents hidden `log K`, `delta G standard`,
  activity, molality, fugacity, and EOS `x phi` conventions.
- [ ] Homogeneous CE native/Python core reports exact residuals, derivatives,
  scaling, and diagnostics.
- [ ] Standalone CE enters through one activation-matrix NLP/Ipopt path using
  the shared CE residual contract.
- [ ] Cantera and Pope reference cases are retained as CE-only oracles.
- [ ] Public CE API/result schema exposes standalone speciation only.
- [ ] Validation ladder includes analytic, charged, Ascani, MEA, and oracle
  fixtures with retained artifacts.
- [ ] Activation gate opens only standalone CE after evidence closes.
- [ ] CPE interface contract remains blocked by CE and PE proof gates.

## Non-Goals

- No reactive LLE implementation in the standalone CE tranche.
- No reactive electrolyte LLE implementation in the standalone CE tranche.
- No parameter regression or downstream application metric work.
- No release readiness claim.
- No Cantera dependency in production CE runtime unless a later issue explicitly
  proves and accepts that design.

## Tasks

### Task 1: Publish The CE/CPE Boundary Tracking Set

**Use Cases:**

- A maintainer needs a GitHub tracking issue and child issues before agents
  start implementation.
- Issue mirrors need a durable source plan with acceptance proof and cutover
  handling.
- The issue set must displace stale broad closed tickets without treating them
  as current proof.

**Files:**

- Create:
  `docs/superpowers/issues/<issue-number>-m4-ce-standalone-chemical-speciation-foundation-before-cpe.md`
- Create: child issue mirrors under `docs/superpowers/issues/`
- Modify:
  `docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md`
- Test: `scripts/validate-issue-mirror.ps1`

- [ ] **Step 1: Draft issue bodies from this plan.**
  Use the issue packet below for the tracking issue and ten child issues.
- [ ] **Step 2: Publish issues in dependency order.**
  Run `gh issue create` for the tracking issue first, then child issues, all
  with milestone `M4 - Equilibrium`.
- [ ] **Step 3: Create mirrors.**
  Save each mirror under `docs/superpowers/issues/<issue-number>-<slug>.md`
  with the full GitHub body and workflow metadata required by the create-issues
  skill.
- [ ] **Step 4: Validate mirrors.**
  Run `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile <mirror>`.
- [ ] **Step 5: Commit issue artifacts.**
  Commit only the plan and issue mirrors after mirror validation passes.

### Task 2: Write CE/CPE Boundary Doctrine And Registry Gate

**Use Cases:**

- A user must see that CE is homogeneous speciation and CPE is simultaneous
  phase-plus-chemistry.
- Registry tests must reject hidden standard-state or staged CE plus PE proof.
- The first code issue needs a tested cutover from placeholder-only CE wording
  to executable CE gates.

**Files:**

- Modify:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`

- [ ] **Step 1: Add failing registry tests.**
  Assert CE has standard-state, reaction-affinity, and derivative gates, and
  CPE requires both CE and PE gates.
- [ ] **Step 2: Run the focused tests.**
  Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_equilibrium_benchmark_registry.py tests/native/contracts/test_generalized_equilibrium_registry.py -q`.
- [ ] **Step 3: Update docs and registry rows.**
  Encode the CE/CPE boundary and blocked CPE dependency text.
- [ ] **Step 4: Re-run tests and docs validation.**
  Run the same focused tests and `uv run --no-sync python scripts/dev/validate_project.py docs`.
- [ ] **Step 5: Commit.**
  Commit the doctrine and registry gate with a message scoped to CE boundary
  planning.

### Task 3: Define Reaction-Set Schema And Conservation Compiler

**Use Cases:**

- A CE request with true species and reactions must compile into a conservation
  basis with deterministic rank diagnostics.
- Charged species must include charge-balance basis behavior before electrolyte
  speciation can be trusted.
- Invalid basis, unknown species, impossible feeds, and duplicate reactions
  must fail before solver entry, replacing ad hoc reaction payloads.

**Files:**

- Create:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Create:
  `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`

- [ ] **Step 1: Write failing schema tests.**
  Cover neutral basis, charged basis, rank-deficient reactions, unknown species,
  and impossible feed conservation.
- [ ] **Step 2: Run schema tests and verify failure.**
  Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py -q`.
- [ ] **Step 3: Add request dataclasses and compiler functions.**
  Implement true-species labels, element/moiety matrix, charge vector,
  stoichiometric matrix, feed feasibility, and rank diagnostics.
- [ ] **Step 4: Re-run schema tests.**
  Require all schema tests to pass without entering native solver code.
- [ ] **Step 5: Commit.**
  Commit schema and conservation compiler work.

### Task 4: Define Standard-State And Equilibrium-Constant Registry

**Use Cases:**

- A reaction residual must never evaluate from an implicit standard-state
  convention.
- Ascani 2023 `K_a`, Cantera ideal cases, and Pope ideal-gas cases need
  traceable conversion metadata.
- The standard-state registry must replace scattered source-specific conversion
  logic.

**Files:**

- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Create:
  `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py`
- Modify: `analyses/paper_validation/2023_ascani/scripts/run_all.py`
- Modify: `analyses/paper_validation/2023_ascani/analysis.yaml`

- [ ] **Step 1: Write failing standard-state tests.**
  Cover `log K`, `delta G standard`, mole-fraction activity, molality, fugacity,
  EOS `x phi`, units, and temperature metadata.
- [ ] **Step 2: Run tests and verify missing registry failure.**
  Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py -q`.
- [ ] **Step 3: Implement standard-state records and conversions.**
  Add explicit records and conversion diagnostics consumed by CE requests.
- [ ] **Step 4: Update Ascani retained metadata.**
  Route the existing Ascani conversion through the registry and keep the
  retained source constants visible.
- [ ] **Step 5: Commit.**
  Commit the standard-state registry and retained metadata updates.

### Task 5: Build Homogeneous CE Native Residual And Objective Core

**Use Cases:**

- A homogeneous CE solve must report balances, affinities, objective value,
  gradients, Jacobian, Hessian, scaling, and domain margins.
- Existing ideal reaction smoke tests must become part of the CE block contract
  rather than isolated prototype evidence.
- The native block must expose exact derivative metadata before any route can
  be admitted.

**Files:**

- Create:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/chemical_equilibrium_block.h`
- Create:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/chemical_equilibrium_block.cpp`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/reaction_block.h`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/reaction_block.cpp`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Create:
  `packages/epcsaft-equilibrium/tests/native/blocks/test_chemical_equilibrium_blocks.py`

- [ ] **Step 1: Write failing native block tests.**
  Cover ideal `A <=> B`, `A + B <=> C`, charged conservation, gradient,
  Jacobian, Hessian, and domain-margin diagnostics.
- [ ] **Step 2: Run tests and verify native symbols are missing.**
  Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_chemical_equilibrium_blocks.py -q`.
- [ ] **Step 3: Implement the CE block.**
  Add homogeneous objective/residual evaluation and expose bindings for tests.
- [ ] **Step 4: Re-run native block tests.**
  Require exact residual and derivative assertions to pass.
- [ ] **Step 5: Commit.**
  Commit the native CE block and bindings.

### Task 6: Add Single CE NLP Activation Path

**Use Cases:**

- Standalone CE must enter through the same activation matrix, selector
  contract, native `NlpProblem`, and Ipopt adapter pattern used by the rest of
  M4 equilibrium.
- The #325 homogeneous CE residual/objective block must become the objective and
  residual source for that one NLP path, not a direct checker-only binding.
- Direct extent, element-potential/VCS-style, and Pope-style continuation ideas
  may appear only as non-executing reference notes. They must not become route
  diagnostics, metadata choices, execution lanes, selector branches, native
  bindings, public API fields, or checker gates.
- CPE must later be able to compose phase and chemistry without migrating from a
  separate standalone CE solver architecture.

**Files:**

- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Create:
  `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py`
- Create:
  `tests/native/contracts/test_standalone_ce_gate.py`
- Create: `scripts/validation/check_standalone_ce_gate.py`

- [ ] **Step 1: Write failing single-path activation tests.**
  Cover activation-matrix admission, selector classification, native
  `NlpProblem` construction, Ipopt-adapter solve diagnostics, and rejection of
  side-channel CE lane bindings.
- [ ] **Step 2: Run tests and verify failure.**
  Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py tests/native/contracts/test_standalone_ce_gate.py -q`.
- [ ] **Step 3: Implement the single CE NLP route.**
  Add activation-matrix/selector wiring and native NLP/Ipopt solve diagnostics
  that consume the #325 CE residual/objective block. Do not add
  `_native_chemical_equilibrium_algorithm_lanes`, direct extent, VCS-style, or
  Pope-style side-route bindings.
- [ ] **Step 4: Add checker coverage.**
  Make `check_standalone_ce_gate.py --json --require-single-nlp-path` validate
  the activation matrix, selector, native NLP route, Ipopt adapter diagnostics,
  and absence of side-channel CE solver bindings.
- [ ] **Step 5: Commit.**
  Commit the single CE NLP activation route and checker gate.

### Task 7: Create Cantera And Pope Reference Oracle Harness

**Use Cases:**

- Developers need CE oracle cases that distinguish chemical equilibrium proof
  from phase equilibrium proof.
- Cantera-compatible ideal cases should compare element balance, species mole
  fractions, and affinities.
- Pope-paper constrained ideal-gas reference cases should stress tiny species
  and constraint-potential behavior without creating an ePC-SAFT continuation
  route.

**Files:**

- Create:
  `analyses/reference_oracles/chemical_equilibrium/cantera_pope_reference_cases.json`
- Create:
  `analyses/reference_oracles/chemical_equilibrium/generate_reference_cases.py`
- Create:
  `tests/native/contracts/test_chemical_equilibrium_reference_oracles.py`
- Modify: `scripts/validation/check_standalone_ce_gate.py`

- [ ] **Step 1: Write failing oracle tests.**
  Assert reference records include source, solver, species order, balances,
  affinities, and a `ce_only` scope flag.
- [ ] **Step 2: Run oracle tests and verify missing fixture failure.**
  Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_chemical_equilibrium_reference_oracles.py -q`.
- [ ] **Step 3: Generate retained oracle records.**
  Add deterministic ideal CE cases from Cantera-compatible and Pope-paper
  reference definitions with no production runtime dependency.
- [ ] **Step 4: Wire oracle checker evidence.**
  Make the standalone CE checker reject oracle records that claim LLE or CPE
  proof.
- [ ] **Step 5: Commit.**
  Commit oracle harness and retained JSON.

### Task 8: Design Public CE API And Result Schema

**Use Cases:**

- A user needs a standalone speciation call that reports species amounts,
  activities, chemical potentials, extents, balances, affinities, and
  standard-state metadata.
- Capability output must distinguish standalone CE from reactive LLE and CPE.
- Old root-level reactive helpers must not become accidental compatibility
  surfaces unless this issue explicitly admits them.

**Files:**

- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Create:
  `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify:
  `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Write failing API tests.**
  Cover CE request creation, result fields, diagnostics, errors, and closed
  reactive phase routes.
- [ ] **Step 2: Run API tests and verify failure.**
  Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`.
- [ ] **Step 3: Implement CE API/result schema.**
  Expose only standalone speciation behavior and result diagnostics.
- [ ] **Step 4: Update docs.**
  Add user-facing CE API notes without claiming CPE support.
- [ ] **Step 5: Commit.**
  Commit API/result schema and docs.

### Task 9: Build Standalone CE Validation Ladder

**Use Cases:**

- The activation gate needs retained evidence beyond smoke tests.
- Analytic ideal, charged, Ascani, MEA, Cantera, and Pope cases need separate
  records with tolerances and source metadata.
- Scientific validation must expose source-data blockers instead of converting
  them into capability claims.

**Files:**

- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Create:
  `analyses/paper_validation/standalone_ce/analysis.yaml`
- Create:
  `analyses/paper_validation/standalone_ce/shared/results/summary.json`
- Modify:
  `analyses/paper_validation/2023_ascani/analysis.yaml`
- Modify:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`

- [ ] **Step 1: Write failing validation-checker tests.**
  Cover missing analytic, charged, Ascani, MEA, Cantera, Pope, derivative, and
  capability evidence.
- [ ] **Step 2: Run checker tests and verify failure.**
  Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_standalone_ce_gate.py -q`.
- [ ] **Step 3: Add retained validation records.**
  Store JSON summaries with species order, units, residuals, tolerances, and
  source links.
- [ ] **Step 4: Require complete checker mode.**
  Make `check_standalone_ce_gate.py --json --require-complete` consume every
  validation family.
- [ ] **Step 5: Commit.**
  Commit validation ladder and registry evidence updates.

### Task 10: Activate Standalone CE And Preserve CPE Closure

**Use Cases:**

- `reactive_speciation` can open only when every standalone CE gate passes.
- `reactive_lle` and `reactive_electrolyte_lle` must remain closed until CPE
  issues prove simultaneous coupled equilibrium.
- Capabilities, docs, registry rows, and tests must agree about the activation
  cutover.

**Files:**

- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Modify:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify:
  `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/pages/development_workflows.rst`

- [ ] **Step 1: Write failing activation tests.**
  Assert CE opens only under complete checker evidence and CPE/reactive phase
  routes stay closed.
- [ ] **Step 2: Run activation tests and verify failure.**
  Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_standalone_ce_gate.py -q`.
- [ ] **Step 3: Implement activation cutover.**
  Update activation/capability payloads for standalone CE only.
- [ ] **Step 4: Run complete proof oracle.**
  Run the proof oracle commands below.
- [ ] **Step 5: Commit.**
  Commit standalone CE activation and capability evidence.

### Task 11: Define CPE Interface Contract For Later Issues

**Use Cases:**

- Future reactive LLE work needs exact variables and blockers before code work
  starts.
- Reviewers must see that CPE is simultaneous phase-plus-chemistry, not staged
  CE followed by PE.
- The CPE contract must point to CE and PE gate dependencies and replace broad
  old reactive tickets with a current issue backbone.

**Files:**

- Modify:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Create:
  `docs/superpowers/specs/2026-06-26-m4-equilibrium-cpe-interface-after-standalone-ce.md`
- Create: local issue mirror for the CPE interface child issue
- Test: `tests/native/contracts/test_equilibrium_benchmark_registry.py`

- [ ] **Step 1: Write failing CPE contract tests.**
  Assert CPE names phase species amounts, phase volumes, reaction variables,
  reaction affinity, transfer-potential equality, phase charge when applicable,
  and PE/CE blockers.
- [ ] **Step 2: Run registry tests and verify failure.**
  Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q`.
- [ ] **Step 3: Write the CPE interface spec.**
  Define variables, constraints, derivatives, validation blockers, and
  disallowed staged proof.
- [ ] **Step 4: Update registry/docs.**
  Link the CPE contract and keep production exposure closed.
- [ ] **Step 5: Commit.**
  Commit the future CPE contract and blocked issue mirror.

## Issue Creation Packet

Create the issues in this dependency order:

1. Tracking issue: `M4 CE: standalone chemical/speciation equilibrium foundation before CPE`
   - Type: `Feature`
   - Classification: `AFK`
   - Labels: `enhancement`, `agent-ready`, `docs`, `validation`,
     `equilibrium`, `area:equilibrium`, `backend:ipopt`, `type:feature`
   - Blocked by: `None`
   - Goal Command: `/goal Create the standalone CE issue backbone and keep CE/CPE capability boundaries evidence-backed.`

2. Child: `M4 CE: write CE/CPE boundary doctrine and registry update`
   - Type: `Task`
   - Classification: `AFK`
   - Blocked by: tracking issue
   - Goal Command: `/goal Make CE and CPE registry/docs boundaries explicit and validated.`

3. Child: `M4 CE: define reaction-set schema and conservation-basis compiler`
   - Type: `Feature`
   - Classification: `AFK`
   - Blocked by: boundary doctrine issue
   - Goal Command: `/goal Add reaction schema and conservation-basis compiler tests and implementation.`

4. Child: `M4 CE: define standard-state and equilibrium-constant registry`
   - Type: `Feature`
   - Classification: `AFK`
   - Blocked by: reaction-set schema issue
   - Goal Command: `/goal Add explicit standard-state registry and conversion diagnostics for CE.`

5. Child: `M4 CE: build homogeneous CE residual and constrained objective core`
   - Type: `Feature`
   - Classification: `AFK`
   - Blocked by: standard-state registry issue
   - Goal Command: `/goal Build homogeneous CE native residual/objective core with exact derivative diagnostics.`

6. Child: `M4 CE: add single CE NLP activation path`
   - Type: `Feature`
   - Classification: `AFK`
   - Blocked by: homogeneous CE core issue
   - Goal Command: `/goal Add the standalone CE route through the single activation-matrix NLP/Ipopt path, with no side-channel algorithm lanes.`

7. Child: `M4 CE: create Cantera and Pope reference-oracle harness`
   - Type: `Task`
   - Classification: `AFK`
   - Blocked by: single CE NLP activation path issue
   - Goal Command: `/goal Create retained CE-only Cantera/Pope oracle fixtures and tests.`

8. Child: `M4 CE: design standalone speciation public API and result schema`
   - Type: `Feature`
   - Classification: `AFK`
   - Blocked by: CE core issue
   - Goal Command: `/goal Add standalone reactive_speciation API/result schema without CPE claims.`

9. Child: `M4 CE: build standalone validation ladder`
   - Type: `Task`
   - Classification: `AFK`
   - Blocked by: oracle harness and API schema issues
   - Goal Command: `/goal Build retained standalone CE validation ladder and checker evidence.`

10. Child: `M4 CE: activate standalone CE only after gates pass`
    - Type: `Feature`
    - Classification: `HITL`
    - Blocked by: validation ladder issue
    - Goal Command: `/goal Activate only standalone CE after strict checker proof and preserve CPE closure.`

11. Child: `M4 CPE: define simultaneous phase-plus-chemistry interface contract`
    - Type: `Task`
    - Classification: `HITL`
    - Blocked by: standalone CE activation issue and current PE validation gate
    - Goal Command: `/goal Define the future CPE interface contract without opening reactive phase routes.`

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-schema --require-standard-state --require-core --require-single-nlp-path --require-oracles --require-api --require-validation --require-activation --require-complete
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/native/blocks/test_chemical_equilibrium_blocks.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py tests/native/contracts/test_standalone_ce_gate.py tests/native/contracts/test_chemical_equilibrium_reference_oracles.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
