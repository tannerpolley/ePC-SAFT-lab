# Generalized Phase-Set Certification Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next #189 child after #260 that turns the current internal neutral generalized phase-set diagnostic into a route-refined generalized phase-set certification gate while keeping public generalized multiphase route exposure closed.

**Architecture:** Extend the existing neutral amount-volume NLP, HELD Stage II candidate-set replay metadata, and retained `check_generalized_phase_set.py` checker instead of adding a new public route family. The native work should accept an arbitrary requested neutral phase-kind list with at least three phases, build the Stage III Ipopt seed from the selected Stage II candidate set, refine that full candidate set in the shared multiphase NLP, and report strict solver, replay, mass-balance, phase-distance, and rejection-diagnostic evidence. The Python checker becomes the #189 completion gate by requiring generalized candidate-set replay and Stage III refinement evidence, while docs and activation mirrors continue to mark `neutral_multiphase_nonassoc` internal-only.

**Tech Stack:** C++ native equilibrium NLP core, pybind11 private bindings, `epcsaft-equilibrium` activation diagnostics, Ipopt exact-Hessian route refinement, pytest through `run_pytest.py`, `scripts/validation/check_generalized_phase_set.py`, M4 registry and issue mirrors.

---

## Intake

- Direct planning approval: user invoked `$superpowers-project:write-plan` for a new child under #189, selected `Phase-Set Completion`, and selected `Current Branch`.
- Source issue mirror: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- GFPE doctrine: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Parent GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Current open prerequisite child: `https://github.com/ePC-SAFT/ePC-SAFT/issues/260`
- Prior #189 children: #252 internal generalized phase-set diagnostics, #256 bubble/dew boundary traces, #258 retained cloud/shadow source-data gate.
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Candidate child title: `M4: complete generalized phase-set certification gate`

## Planning Decisions

- Scope: neutral nonassociating generalized phase-set completion only. Associating, electrolyte, reactive, CE, CPE, VLLE, and LLLE public admission stay outside this child.
- Sequencing: #260 remains the current open #189 child. This plan is ready to create the next issue after #260 is merged, or earlier if the tracker owner intentionally opens the next child before #260 closes.
- Exposure: internal checker-gated evidence only. Do not add `neutral_multiphase_nonassoc` to public `Equilibrium` route specs, public routes, or production-exposed capability rows.
- Test-complete status: the new checker command must fail unless generalized Stage II candidate-set replay is consumed by strict Stage III Ipopt route refinement for the requested phase-kind list.
- Metrics: exact Hessian, Ipopt `success`, application `solve_succeeded`, Stage III replay metadata consumption, candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, ln-fugacity consistency norm <= `1.0e-6`, positive pairwise phase distance, at least one rejected candidate with distinct reason, and zero public route exposure.
- Native freshness: any proof that imports a stale `.pyd` is incomplete. The checker must emit and enforce a native freshness receipt when `--require-complete` is supplied.
- Publication decision: while #260 is open, publish this child as `status:blocked` and add a GitHub native dependency edge showing it is blocked by #260. Move it to `status:ready` only after #260 closes cleanly.

## Verified Planning Facts

- `scripts/validation/check_generalized_phase_set.py` currently validates internal diagnostic records from `_native_neutral_tpd_phase_discovery`, but it hard-requires three-phase records and does not run Stage III Ipopt refinement for the generalized candidate set.
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp` already contains `select_generalized_phase_candidate_set`, `solve_candidate_simplex_fractions`, and `evaluate_neutral_multiphase_eos_postsolve`.
- `append_phase_discovery_seed_candidates` currently only adds a Stage II seed when `selected_candidate_count == 2`; generalized candidate-set replay uses `kHeldStageIIDualLoopCandidateSetName` but is not consumed by the current route-refinement seed path.
- `build_two_phase_eos_initial_point_from_candidate_set` currently requires exactly two selected candidates.
- `evaluate_neutral_multiphase_eos_postsolve` reuses the shared amount-volume postsolve with stability certification and phase-kind input.
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp` exposes `_native_neutral_tpd_phase_discovery` and direct multiphase NLP/postsolve helpers, but not a private generalized multiphase route-refinement result helper.
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py` and activation tests already keep `neutral_multiphase_nonassoc` declared-not-exposed with no public routes.
- The M4 registry row `PE-Generalized Multiphase` still has `phase_discovery_status: full_held_required` and records #252 as internal diagnostic evidence only.

## Test-Complete Definition And Metrics

This plan is complete only when all of the following are true:

- `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` exits zero.
- The checker payload reports `requested_phase_count == 3`, `selected_candidate_count == 3`, `held_stage_ii_replay_seed_name == "held_stage_ii_dual_loop_candidate_set"`, `held_stage_iii_status == "ipopt_refinement_completed_current_route"`, `held_stage_iii_consumed_stage_ii_replay_metadata is true`, and `held_stage_iii_replay_seed_name == "held_stage_ii_dual_loop_candidate_set"`.
- The Stage III route-refinement payload reports `solver_status == "success"`, `application_status == "solve_succeeded"`, exact Hessian evidence, `accepted is true`, `postsolve.accepted is true`, no selected seed attempt ending in `max_iterations_exceeded`, and no stale native freshness receipt.
- The selected candidate-set evidence reports candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, ln-fugacity consistency norm <= `1.0e-6`, positive pairwise phase distance, normalized selected compositions, strictly positive phase fractions, and selected phase-count equality with the requested phase-kind list.
- The checker rejects hard-coded three-phase assumptions by deriving required record phase counts from the payload and requested phase-kind list.
- The checker rejects missing Stage III replay, incomplete Stage II candidate-set replay, duplicate/collapsed selected phases, lower-free-energy rejected candidates, generic rejected reasons for lower-free-energy rows, uncertified phase-set records, malformed records, and public route exposure.
- Existing #189 evidence remains green: generalized phase-set diagnostics, boundary traces, cloud/shadow source-data gate, and #260 cloud/shadow route gate if #260 has already merged.

## Acceptance Criteria

- [ ] A new #189 AFK child issue and local mirror define generalized phase-set certification as distinct from #252 diagnostic records and #260 cloud/shadow route evidence.
- [ ] Native generalized phase-set route refinement consumes Stage II candidate-set replay metadata for a requested phase-kind list with at least three phases.
- [ ] Stage III route refinement runs through the shared neutral amount-volume multiphase NLP with exact derivative evidence and strict Ipopt/application convergence.
- [ ] The retained checker emits a machine-readable generalized completion payload with requested phase kinds, selected/rejected candidate counts, replay metadata, route-refinement status, residual norms, native freshness receipt, and public exposure status.
- [ ] Checker tests fail on hard-coded phase-count assumptions, missing route refinement, missing replay metadata, incomplete candidate-set mass balance, duplicate or collapsed selected phases, lower-free-energy rejected candidates, uncertified records, and public route exposure.
- [ ] Activation and capability mirrors keep `neutral_multiphase_nonassoc` internal-only with empty public routes.
- [ ] M4 registry and GFPE doctrine show the new internal generalized certification evidence without claiming final public generalized multiphase admission.
- [ ] #189 remains open after this child unless final public capability admission is separately proven.

## Non-Goals

- No public `Equilibrium(route="neutral_multiphase_nonassoc")` exposure.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No source-backed representative associating or electrolyte replay in this child.
- No final public `PE-Generalized Multiphase` production exposure.
- No closure of #189 from this child alone if public admission remains unproven.
- No changes to M3 provider/EOS packages or M5 regression packages.

## File Map

- Create: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Create after issue creation: `docs/superpowers/issues/<date>-m4-equilibrium-issue-<number>-complete-generalized-phase-set-certification-gate.md`

## Tasks

### Task 1: Create The #189 Child Issue And Mirror

**Use Cases:**
- A worker needs a narrow AFK issue because #189 is a HITL umbrella and #260 owns only cloud/shadow route evidence.
- A reviewer needs the child to state that this is generalized phase-set completion, not final public route exposure.
- The local and GitHub tracker need the #189 queue to show #252, #256, #258, and #260 as prior evidence before this child starts.

**Files:**
- Create: `docs/superpowers/issues/<date>-m4-equilibrium-issue-<number>-complete-generalized-phase-set-certification-gate.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Confirm #189 and #260 state**

  Run:

  ```powershell
  gh issue view 189 --repo ePC-SAFT/ePC-SAFT --json number,state,labels,milestone,comments,url
  gh issue view 260 --repo ePC-SAFT/ePC-SAFT --json number,state,labels,milestone,url
  git status --short --branch
  ```

  Expected: #189 is open and `status:ready`; #260 is either closed/merged or intentionally accepted as an open prerequisite; the worktree used for issue creation is clean except for deliberate planning files.

- [ ] **Step 2: Create one GitHub child issue**

  Use the Issue Creation Packet below. Assign milestone `M4 - Equilibrium` and labels while #260 is open:

  ```text
  enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
  ```

- [ ] **Step 3: Create the local issue mirror**

  Create the mirror with the actual issue number, parent #189 URL, this source plan path, the exact proof oracle, and the non-goals from this plan.

- [ ] **Step 4: Update parent queue context**

  Update the #189 mirror and M4 README so they name this child as the generalized phase-set certification gate after #260. Keep final public admission listed as a separate remaining #189 gate.

- [ ] **Step 5: Commit tracker setup**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Create generalized phase-set certification issue"
  ```

### Task 2: Add Red Completion Checker Tests

**Use Cases:**
- A checker maintainer needs failures that distinguish #252 record-shape completion from full generalized phase-set certification.
- A native worker needs tests that fail while Stage III generalized route refinement does not consume the Stage II candidate-set replay seed.
- A capability reviewer needs public `neutral_multiphase_nonassoc` exposure to remain a hard blocker.

**Files:**
- Create: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Test: `scripts/validation/check_generalized_phase_set.py`

- [ ] **Step 1: Add payload builders for completion cases**

  In `test_generalized_phase_set_completion_checker.py`, add helpers that construct payloads with:

  ```python
  requested_phase_kinds = ["liquid", "liquid", "liquid"]
  requested_phase_count = 3
  held_stage_ii_replay_seed_name = "held_stage_ii_dual_loop_candidate_set"
  held_stage_iii_replay_seed_name = "held_stage_ii_dual_loop_candidate_set"
  ```

- [ ] **Step 2: Add a failing route-refinement requirement test**

  Assert that a payload with valid #252-style records but no route-refinement block returns `complete is False` and includes `missing_generalized_route_refinement`.

- [ ] **Step 3: Add replay metadata tests**

  Assert blockers for:

  ```text
  held_stage_ii_candidate_set_replay_missing
  held_stage_iii_candidate_set_replay_not_consumed
  generalized_selected_phase_count_mismatch
  generalized_phase_count_hard_coded
  ```

- [ ] **Step 4: Add residual and solver status tests**

  Assert blockers for non-success Ipopt status, non-`solve_succeeded` application status, material balance above `1.0e-8`, pressure consistency above `1.0e-3`, ln-fugacity consistency above `1.0e-6`, and non-positive phase distance.

- [ ] **Step 5: Preserve public closure tests**

  Keep or extend the existing public exposure test so `neutral_multiphase_nonassoc` in `capabilities()["public_routes"]` returns `neutral_multiphase_public_route_exposed`.

- [ ] **Step 6: Run the red tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
  ```

  Expected: new completion tests fail on missing checker functions, missing route-refinement fields, or missing native route evidence.

- [ ] **Step 7: Commit the red tests**

  Run:

  ```powershell
  git add tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py
  git commit -m "Add red generalized phase-set completion tests"
  ```

### Task 3: Add Generalized Candidate-Set Route Refinement

**Use Cases:**
- A requested three-phase neutral candidate set needs a Stage III Ipopt refinement seed built from all selected Stage II candidates, not only a selected pair.
- The route-refinement result must reuse the shared amount-volume multiphase NLP and exact Hessian path.
- A failed or partial Ipopt solve must be reported as incomplete evidence instead of being accepted by diagnostic record shape alone.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`

- [ ] **Step 1: Generalize candidate-set initial point construction**

  Replace the exact-two-candidate restriction in `build_two_phase_eos_initial_point_from_candidate_set` with a new helper named `build_multiphase_eos_initial_point_from_candidate_set`. The helper must require `selected_phase_compositions.size() == phase_kinds.size()`, `selected_phase_fractions.size() == phase_kinds.size()`, and `selected_phase_kinds.size() == phase_kinds.size()`.

- [ ] **Step 2: Preserve pair seed behavior**

  Keep the existing two-phase seed name `held_stage_ii_dual_loop_candidate_pair` when `selected_candidate_count == 2`. Use `held_stage_ii_dual_loop_candidate_set` when `selected_candidate_count >= 3`.

- [ ] **Step 3: Add a generalized route-refinement helper**

  Add a private native function shaped like:

  ```cpp
  NeutralTwoPhaseEosRouteResult solve_neutral_multiphase_eos_route(
      const add_args& args,
      double temperature,
      double target_pressure,
      const std::vector<double>& feed_composition,
      const std::vector<int>& phase_kinds,
      const IpoptSolveOptions& options,
      double material_tolerance,
      double pressure_tolerance,
      double chemical_potential_tolerance,
      double phase_distance_tolerance
  );
  ```

  The result should use problem name `neutral_multiphase_eos`, seed from Stage II candidate-set replay, `evaluate_neutral_multiphase_eos_postsolve`, exact Hessian requirements, strict route acceptance, and `NeutralRouteCertificationLevel::PhaseSetCertified`.

- [ ] **Step 4: Add the private pybind result helper**

  In `register_bindings.cpp`, expose `_native_neutral_multiphase_eos_route_result` with arguments for mixture, temperature, pressure, feed composition, phase kinds, Ipopt controls, and tolerances. Return the same route-result dictionary shape as selector route proofs and include `requested_phase_kinds`, `requested_phase_count`, and `public_route_admission: "closed"`.

- [ ] **Step 5: Add native diagnostics tests**

  In `test_internal_multiphase_activation_contracts.py`, add a test that calls `_native_neutral_multiphase_eos_route_result` for the symmetric ternary case and asserts strict solver status, Stage II candidate-set seed name, Stage III replay consumption, selected candidate count 3, exact Hessian evidence, and public exposure closure.

- [ ] **Step 6: Build and run native diagnostics**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
  ```

- [ ] **Step 7: Commit native route refinement**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py
  git commit -m "Add generalized phase-set route refinement"
  ```

### Task 4: Wire The Retained Completion Checker

**Use Cases:**
- A reviewer needs one command that proves generalized phase-set completion with native freshness and strict Stage III route refinement.
- A failed generalized route solve must produce named blockers without weakening #252 diagnostic-record coverage.
- The checker must derive expected phase count from `--phase-kinds` and payload fields instead of hard-coding three-phase records.

**Files:**
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`

- [ ] **Step 1: Add completion evaluation**

  Add `evaluate_generalized_phase_set_completion(payload: dict[str, Any]) -> dict[str, Any]` for pure payload tests and `run_generalized_phase_set_completion(*, phase_kinds: list[str], run_route_refinement: bool, checker_command: list[str]) -> dict[str, Any]` for native execution.

- [ ] **Step 2: Add CLI controls**

  Add:

  ```text
  --phase-kinds liquid,liquid,liquid
  --run-route-refinement
  --require-route-refinement
  ```

  The default command can preserve the existing #252 diagnostic behavior. The new #189 completion proof must use all three flags plus `--require-complete`.

- [ ] **Step 3: Enforce replay and route metrics**

  Require Stage II candidate-set replay readiness, Stage III replay consumption, strict Ipopt status, exact Hessian evidence, selected candidate count equal to requested phase count, candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3`, ln-fugacity consistency norm <= `1.0e-6`, and positive phase distance.

- [ ] **Step 4: Enforce public closure and native freshness**

  Include `native_freshness_receipt` in the output. When `--require-complete` is supplied, call `native_freshness.require_receipt` before returning success. Keep `neutral_multiphase_public_route_exposed` as a hard blocker.

- [ ] **Step 5: Run checker tests and command**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
  uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete
  ```

- [ ] **Step 6: Commit checker completion gate**

  Run:

  ```powershell
  git add scripts/validation/check_generalized_phase_set.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py
  git commit -m "Add generalized phase-set completion checker"
  ```

### Task 5: Preserve Activation Closure And Registry Evidence

**Use Cases:**
- Public users must not see `neutral_multiphase_nonassoc` as a route until a later public-admission child proves it.
- Milestone readers need to distinguish #252 diagnostic records from this route-refined completion gate.
- Registry tests need an executable command and required checks for the internal generalized certification evidence.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Strengthen activation tests**

  Assert `neutral_multiphase_nonassoc` remains in `declared_not_exposed_families`, remains absent from `public_routes`, and has empty public route lists even after private route-refinement evidence exists.

- [ ] **Step 2: Update the registry row**

  In `PE-Generalized Multiphase`, add internal evidence for:

  ```text
  generalized_candidate_set_stage_ii_replay
  generalized_stage_iii_ipopt_refinement
  selected_phase_count_matches_requested_phase_kinds
  route_refinement_consumes_candidate_set_seed
  public_route_admission_closed
  ```

- [ ] **Step 3: Update registry tests**

  Require the new evidence command and checks in `test_generalized_equilibrium_registry.py`, while keeping `production_exposed: false` and public route absence.

- [ ] **Step 4: Update GFPE doctrine and M4 README**

  Add the new proof command and state that it proves internal neutral generalized phase-set certification only. Keep final public capability admission and representative associating/electrolyte replay outside this child.

- [ ] **Step 5: Run activation and registry checks**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

- [ ] **Step 6: Commit registry and docs evidence**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py docs/superpowers/milestones/M4-equilibrium
  git commit -m "Document generalized phase-set certification gate"
  ```

### Task 6: Final Proof Oracle And Parent Progress

**Use Cases:**
- A PR reviewer needs one proof oracle proving generalized Stage II replay, Stage III route refinement, public closure, and no regression in previous #189 children.
- A tracker reviewer needs #189 to remain open with only final public admission listed as the remaining umbrella gate.
- If #260 is still open, closeout needs to state the dependency instead of treating this child as final #189 completion.

**Files:**
- Modify: `docs/superpowers/issues/<date>-m4-equilibrium-issue-<number>-complete-generalized-phase-set-certification-gate.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Run the full proof oracle**

  Run every command in the Proof Oracle section below from the repo root.

- [ ] **Step 2: Record completion metrics**

  Record requested phase kinds, selected candidate count, selected phase fractions, candidate mass-balance norm, route solver/application status, exact Hessian status, Stage II seed name, Stage III replay source/seed/count, residual norms, native freshness receipt, and public exposure status in the child mirror.

- [ ] **Step 3: Update #189 progress**

  Add a #189 comment and mirror update saying this child completes internal neutral generalized phase-set certification. If #260 is merged, the remaining #189 gate is final public capability admission. If #260 is open, name #260 plus final public admission as remaining.

- [ ] **Step 4: Run cleanup**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

- [ ] **Step 5: Commit closeout evidence**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Record generalized phase-set certification closeout"
  ```

## Proof Oracle

Run these commands from the repo root:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

If #260 is still open when this child is implemented, run the cloud/shadow route command as dependency evidence and record its status instead of claiming #189 is ready for final public admission.

## Issue Creation Packet

Create one AFK child issue from this plan. If #260 is still open, publish it with `status:blocked` and a native GitHub dependency edge blocked by #260.

Title:

```text
M4: complete generalized phase-set certification gate
```

Body:

```markdown
## Summary

Add the next #189 child after #260: convert the current internal neutral generalized phase-set diagnostic into a route-refined generalized phase-set certification gate. This issue proves Stage II candidate-set replay and strict Stage III Ipopt refinement for a requested neutral multiphase candidate set while keeping public `neutral_multiphase_nonassoc` route exposure closed.

## Parent

- Parent issue: #189
- Source plan: `docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md`
- Prior children: #252 internal generalized phase-set diagnostics; #256 bubble/dew boundary traces; #258 cloud/shadow source-data gate; #260 cloud/shadow route evidence.
- Blocked by: #260 while #260 remains open.

## Acceptance Criteria

- [ ] Native generalized phase-set route refinement consumes Stage II candidate-set replay metadata for requested phase kinds `liquid,liquid,liquid`.
- [ ] Stage III Ipopt route refinement reports `solver_status == "success"`, `application_status == "solve_succeeded"`, exact Hessian evidence, accepted postsolve, and no iteration-limit selected seed attempt.
- [ ] The retained checker reports requested phase kinds/count, selected/rejected candidate counts, selected phase fractions, replay metadata, route-refinement status, residual norms, native freshness receipt, and public exposure status.
- [ ] Completion metrics satisfy candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, ln-fugacity consistency norm <= `1.0e-6`, positive phase distance, normalized compositions, and strictly positive phase fractions.
- [ ] Checker tests reject missing route refinement, missing replay metadata, hard-coded phase count, duplicate/collapsed phases, lower-free-energy rejected candidates, uncertified records, malformed records, and public route exposure.
- [ ] `neutral_multiphase_nonassoc` remains absent from public routes and production-exposed capability rows.
- [ ] M4 registry and GFPE doctrine record internal generalized certification evidence without final public production exposure.
- [ ] #189 remains open unless final public capability admission is separately proven.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Non-Goals

- No public `neutral_multiphase_nonassoc` route exposure.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No final public `PE-Generalized Multiphase` production exposure.
- No closure of #189 from this child alone if public admission remains unproven.
```

Labels:

```text
enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
```

Milestone:

```text
M4 - Equilibrium
```

## Risk And Dependency Notes

- Risk: #260 is still in progress on the current branch. Mitigation: this plan treats #260 as prerequisite evidence for the final #189 queue and does not edit #260 implementation files.
- Risk: `two_phase_eos_route` names are historical even when the NLP supports more than two phase blocks. Mitigation: add clearly named generalized helper functions and tests while preserving existing two-phase behavior.
- Risk: synthetic symmetric ternary evidence can be over-read as public generalized production support. Mitigation: keep activation closed and docs explicit that this is internal neutral certification evidence.
- Risk: native route success can be stale if Python imports an older binary. Mitigation: require build refresh plus native freshness receipt in the proof oracle.
