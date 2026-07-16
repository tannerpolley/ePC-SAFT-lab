# M4 Equilibrium HELD 1.0 Adoption And #187 Start Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the missing Stage II HELD issue, refresh the M4 queue around #187, and resolve the nearest #187 shared NLP/Ipopt diagnostic gap needed before full HELD 1.0 adoption can proceed.

**Architecture:** Treat closed #148 and #186 as evidence only, then create the open Stage II issue that blocks #188/#189. Keep #187 focused on the shared NLP/Ipopt infrastructure gate by proving native diagnostics are already emitted and carrying any missing Stage 8 fields through the Python route-diagnostics normalization seam.

**Tech Stack:** GitHub CLI, GitHub issue dependencies API, Python, pytest through `uv run python run_pytest.py`, native C++/pybind diagnostics already exposed by `epcsaft-equilibrium`, Sphinx docs validation.

---

## Intake

- Source spec:
  `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- Existing issue mirror:
  `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md`
- Existing issue plan:
  `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate-plan.md`
- GitHub issue:
  `https://github.com/ePC-SAFT/ePC-SAFT/issues/187`
- Milestone:
  `M4 - Equilibrium`
- User decision:
  Create one plan that includes immediate Stage II issue creation before #187 execution.

## Acceptance Criteria

- [ ] A new M4 feature issue exists for promoting neutral HELD 1.0 Stage II from candidate audit to replayable dual phase-discovery gate.
- [ ] The new Stage II issue is blocked by #187 and blocks #188/#189 through GitHub issue dependencies.
- [ ] #187 live readiness is refreshed after confirming #186 is closed and no open dependency still blocks #187.
- [ ] `native_route_diagnostics()` preserves the Stage 8 Ipopt numerics fields emitted by native route payloads.
- [ ] Focused diagnostics tests prove profile exact-Hessian gate, scaling-quality flags, active-bound counts, bound controls, barrier/regularization fields, and restoration observation survive Python normalization.
- [ ] #187 remains scoped to shared NLP/Ipopt infrastructure and does not promote HELD, associating, electrolyte, reactive, CE, CPE, benchmark, or public capability claims.

## Non-Goals

- No HELD Stage II algorithm implementation in #187.
- No source-backed neutral TP flash fixture admission in #187.
- No public route exposure or capability broadening.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No registry promotion from closed issue state.
- No downstream application behavior.

## Dependency Notes

- #148 closed the narrow neutral HELD-style baseline; it does not satisfy full HELD 1.0 adoption.
- #186 closed the pretreatment/selector gate; it should no longer block #187 if GitHub dependencies confirm no other open blocker.
- #187 is the nearest resolvable M4 implementation issue.
- The new Stage II issue should sit between #187 and #188/#189.
- #188 and #189 remain blocked until #187 plus the Stage II issue are complete.

## File Map

- Create no source files for #187.
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py`
- Read/check: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- Read/check: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Read/check: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/solvers/ipopt_adapter.cpp`
- Read/check: `packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py`
- Read/check: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Read/check: `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- Optional doc touch only if tracker artifacts are updated by the same worker:
  `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md`

## Task 1: Create The Stage II HELD Issue And Refresh #187 Readiness

**Files:**
- Read: the then-active issue and milestone routing policy
- Read: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- GitHub: `https://github.com/ePC-SAFT/ePC-SAFT/issues/187`
- GitHub: `https://github.com/ePC-SAFT/ePC-SAFT/issues/188`
- GitHub: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`

- [ ] **Step 1: Verify #187 blockers**

Run:

```powershell
gh issue view 186 --repo ePC-SAFT/ePC-SAFT --json number,state,title,closedAt
gh api /repos/ePC-SAFT/ePC-SAFT/issues/187/dependencies/blocked_by --jq '.[] | {number, state, title}'
```

Expected:

- #186 is `CLOSED`.
- #187 has no open blocking issue. If an open blocking issue appears, stop and
  record the blocker before changing #187 readiness.

- [ ] **Step 2: Create the Stage II HELD issue**

Run:

```powershell
$stage2IssueUrl = @'
Implement the missing HELD 1.0 adoption gate between #187 and #188: promote neutral Stage II from the current finite candidate bound audit to a replayable dual phase-discovery loop with explicit lower/upper bound history, candidate storage, stopping criteria, and Stage III replay metadata.

Source spec:
docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md

Outcome:
Neutral HELD Stage II can be used as a full adoption gate only when a replayable dual phase-discovery loop records bound history, candidate creation and rejection, stopping criteria, and route-refinement metadata.

Acceptance:
- Stage II reports lower bound, upper bound, bound gap, stopping reason, candidate list, rejected candidates, and replay metadata.
- Stage III route refinement consumes Stage II candidate metadata.
- Incomplete continuous TPD starts, open Stage II gaps, tiny-step paths, acceptable-level points, feasible-only points, and iteration-limit routes do not satisfy the adoption gate.
- Registry and diagnostics distinguish deterministic screening, continuous TPD, Stage I, Stage II audit, Stage II dual-loop verification, and Stage III refinement.
- No associating, electrolyte, reactive, CE, CPE, public route, benchmark, or capability broadening occurs in this issue.

Non-goals:
- No source-backed neutral TP flash fixture admission.
- No boundary workflow or generalized phase-set PE admission.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No public route exposure.

Proof oracle:
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py -q
uv run python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
uv run python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run python scripts/dev/validate_project.py docs
'@ | gh issue create `
  --repo ePC-SAFT/ePC-SAFT `
  --template feature.yml `
  --title "M4: promote neutral HELD 1.0 Stage II to replayable dual phase-discovery gate" `
  --milestone "M4 - Equilibrium" `
  --label "enhancement,native,solver,docs,validation,equilibrium,area:equilibrium,backend:ipopt,status:blocked,type:feature" `
  --project "ePC-SAFT Roadmap" `
  --body-file -
$stage2IssueUrl
```

Expected:

- GitHub prints the new issue URL.
- Save the printed URL and issue number in the task notes.

- [ ] **Step 3: Add dependency edges**

Run with the issue number returned by Step 2:

```powershell
$stage2IssueNumber = [int]($stage2IssueUrl -replace '.*/issues/', '')
$issue187Id = gh api /repos/ePC-SAFT/ePC-SAFT/issues/187 --jq '.id'
$stage2IssueId = gh api "/repos/ePC-SAFT/ePC-SAFT/issues/$stage2IssueNumber" --jq '.id'
gh api -X POST "/repos/ePC-SAFT/ePC-SAFT/issues/$stage2IssueNumber/dependencies/blocked_by" -F issue_id="$issue187Id"
gh api -X POST /repos/ePC-SAFT/ePC-SAFT/issues/188/dependencies/blocked_by -F issue_id="$stage2IssueId"
gh api -X POST /repos/ePC-SAFT/ePC-SAFT/issues/189/dependencies/blocked_by -F issue_id="$stage2IssueId"
```

Expected:

- The Stage II issue is blocked by #187.
- #188 and #189 list the Stage II issue as a blocker.

- [ ] **Step 4: Refresh #187 readiness labels if blockers are clear**

Run:

```powershell
gh issue edit 187 --repo ePC-SAFT/ePC-SAFT --remove-label "status:blocked" --add-label "status:ready"
```

Expected:

- #187 no longer carries `status:blocked`.
- #187 carries `status:ready`.

- [ ] **Step 5: Commit only local tracker edits made in this task**

If this task updated local mirrors, stage only those local tracker files and commit:

```powershell
git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md
git commit -m "docs: refresh held adoption issue queue"
```

Expected:

- The commit contains only tracker files intentionally edited by this task.

## Task 2: Prove The Existing #187 Native Substrate Before Editing

**Files:**
- Test: `packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
- Test: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Test: `tests/native/contracts/test_equilibrium_benchmark_registry.py`

- [ ] **Step 1: Run the Ipopt adapter contract**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py -q
```

Expected:

- Tests pass.
- The output proves the native adapter already covers exact Hessian mode,
  diagnostic limited-memory mode, option profiles, user scaling, active-bound
  diagnostics, barrier/regularization diagnostics, linear-solver reporting, and
  warm-start state sizing.

- [ ] **Step 2: Run current route-result diagnostics slices**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py -q
```

Expected:

- Tests pass.
- Current neutral VLE/LLE result payloads still expose route diagnostics and do
  not regress while #187 is narrowed to the Python normalization seam.

- [ ] **Step 3: Run registry contracts**

Run:

```powershell
uv run python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
```

Expected:

- Tests pass.
- Registry doctrine still keeps production exposure behind HELD and derivative
  gates.

- [ ] **Step 4: Stop on missing native substrate evidence**

If any command above fails, do not edit the normalization layer first. Record
the failing test node and failure reason, then repair the lower native or
registry layer before continuing.

## Task 3: Add A Failing Python Diagnostic Normalization Test

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py`

- [ ] **Step 1: Append the Stage 8 diagnostics preservation test**

Add this test to
`packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py`:

```python
def test_native_route_diagnostics_preserves_stage8_ipopt_numerics_contract() -> None:
    route = {
        "accepted": True,
        "status": "accepted",
        "postsolve_accepted": True,
        "solver_accepted": True,
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "option_profile": "held_refinement",
        "solver_acceptance_policy": "success_status_and_scaled_kkt_required",
        "exact_hessian_policy": "required_by_profile",
        "scaling_contract": "adapter_enforced_nlp_objective_variable_constraint_scaling",
        "residual_scaling_policy": "nlp_provided_nondimensional_or_extensive_reference_scales",
        "linear_solver_policy": "ipopt_default_recorded",
        "barrier_policy": "ipopt_internal_barrier_for_declared_bounds",
        "scaling_method": "user-scaling",
        "linear_solver_requested": "mumps",
        "linear_solver_selected": "mumps",
        "profile_exact_hessian_gate": True,
        "variable_scaling_quality_passed": True,
        "constraint_scaling_quality_passed": True,
        "scaled_acceptance_passed": True,
        "restoration_phase_observed": False,
        "active_lower_bound_count": 1,
        "active_upper_bound_count": 2,
        "active_variable_bound_count": 3,
        "step_trial_count_max": 4,
        "bound_push": 1.0e-10,
        "bound_frac": 1.0e-10,
        "regularization_size_final": 0.0,
        "regularization_size_max": 2.0e-8,
    }

    diagnostics = native_route_diagnostics(route)

    assert diagnostics["option_profile"] == "held_refinement"
    assert diagnostics["profile_exact_hessian_gate"] is True
    assert diagnostics["variable_scaling_quality_passed"] is True
    assert diagnostics["constraint_scaling_quality_passed"] is True
    assert diagnostics["scaled_acceptance_passed"] is True
    assert diagnostics["restoration_phase_observed"] is False
    assert diagnostics["active_lower_bound_count"] == 1
    assert diagnostics["active_upper_bound_count"] == 2
    assert diagnostics["active_variable_bound_count"] == 3
    assert diagnostics["step_trial_count_max"] == 4
    assert diagnostics["bound_push"] == 1.0e-10
    assert diagnostics["bound_frac"] == 1.0e-10
    assert diagnostics["regularization_size_final"] == 0.0
    assert diagnostics["regularization_size_max"] == 2.0e-8
```

- [ ] **Step 2: Run the new test and verify the failure**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py::test_native_route_diagnostics_preserves_stage8_ipopt_numerics_contract -q
```

Expected:

- The test fails because at least one Stage 8 field is not preserved by
  `native_route_diagnostics()`.

## Task 4: Preserve The Missing Stage 8 Diagnostic Fields

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py`

- [ ] **Step 1: Add the missing boolean keys**

In `_ROUTE_BOOL_DIAGNOSTIC_KEYS`, include these keys:

```python
    "profile_exact_hessian_gate",
    "variable_scaling_quality_passed",
    "constraint_scaling_quality_passed",
    "restoration_phase_observed",
```

- [ ] **Step 2: Add the missing integer keys**

In `_ROUTE_INT_DIAGNOSTIC_KEYS`, include these keys:

```python
    "active_lower_bound_count",
    "active_upper_bound_count",
    "active_variable_bound_count",
    "step_trial_count_max",
```

- [ ] **Step 3: Add the missing float keys**

In `_ROUTE_FLOAT_DIAGNOSTIC_KEYS`, include these keys:

```python
    "bound_push",
    "bound_frac",
```

- [ ] **Step 4: Run the focused diagnostics test**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py -q
```

Expected:

- All native route diagnostics contract tests pass.

- [ ] **Step 5: Commit the focused #187 normalization change**

Run:

```powershell
git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py
git commit -m "fix: preserve shared ipopt route diagnostics"
```

Expected:

- The commit contains only the Python normalizer and its focused test.

## Task 5: Validate #187 Completion Evidence

**Files:**
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py`
- Test: `packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
- Test: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Test: `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- Docs: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`

- [ ] **Step 1: Run focused route diagnostics**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py -q
```

Expected:

- Pass.

- [ ] **Step 2: Run native Ipopt adapter contracts**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py -q
```

Expected:

- Pass.

- [ ] **Step 3: Run neutral route result slices**

Run:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py -q
```

Expected:

- Pass.

- [ ] **Step 4: Run registry contracts**

Run:

```powershell
uv run python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
```

Expected:

- Pass.

- [ ] **Step 5: Run docs validation**

Run:

```powershell
uv run python scripts/dev/validate_project.py docs
```

Expected:

- Sphinx docs build succeeds.

- [ ] **Step 6: Run the cleanup hook**

Run:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected:

- No leftover Codex processes are reported for this repository.

## Task 6: Close Or Handoff #187 With Honest Scope

**Files:**
- Optional modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md`
- Optional modify: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md`

- [ ] **Step 1: Prepare the #187 evidence summary**

Use this summary shape:

```markdown
#187 evidence:
- Shared `NlpProblem` shape validation covers bounds, initial point, objective, gradient, constraints, Jacobian, Hessian, and scaling vector sizes.
- Native Ipopt adapter tests cover exact Hessian profile gating, option profiles, user scaling, active-bound diagnostics, barrier and regularization diagnostics, linear-solver reporting, bounded iteration history, and continuation state sizing.
- Python route diagnostics now preserve the Stage 8 Ipopt numerics fields required by later HELD/TPD certification.
- No HELD Stage II dual-loop, source-backed fixture, boundary workflow, associating, electrolyte, reactive, CE, CPE, benchmark, or capability admission occurred in #187.
```

- [ ] **Step 2: Update local #187 mirror only if the issue is being handed off**

If local mirror text is updated, keep it factual:

```markdown
Readiness: `ready`
Current completion evidence: shared NLP/Ipopt diagnostics are preserved through native and Python route result seams.
Remaining downstream gates: Stage II dual-loop issue, #188 neutral fixture, #189 boundary/generalized phase-set workflows.
```

- [ ] **Step 3: Commit local tracker edits separately**

Run:

```powershell
git add docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md
git commit -m "docs: record issue 187 completion evidence"
```

Expected:

- The commit contains only #187 tracker/spec text.

- [ ] **Step 4: Update GitHub #187 after validation passes**

Run:

```powershell
gh issue comment 187 --repo ePC-SAFT/ePC-SAFT --body-file -
```

Paste the evidence summary from Step 1 to standard input, then close only when
the branch or PR that carries the code/test change has merged:

```powershell
gh issue close 187 --repo ePC-SAFT/ePC-SAFT --comment "Closed by shared NLP/Ipopt diagnostics evidence. Full HELD Stage II, source-backed neutral fixture, boundary workflows, associating GFPE, electrolyte GFPE, and registry closure remain open in their own issues."
```

Expected:

- #187 closes only after the implementation and validation evidence exists.
- Later M4 issues remain open.

## Final Proof Oracle

Run before claiming this plan complete:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py -q
```

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py -q
```

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py -q
```

```powershell
uv run python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
```

```powershell
uv run python scripts/dev/validate_project.py docs
```

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Self-Review

- Spec coverage: this plan covers the source spec's immediate queue action, the
  new Stage II issue, and the #187 start path.
- Scope control: this plan does not implement Stage II HELD, #188, #189, #190,
  #191, or #192.
- Placeholder scan: no unresolved placeholder markers or undefined file paths remain.
- TDD policy: Task 3 writes the failing Python route-diagnostics test before
  Task 4 changes the implementation.
- Debug policy: if native adapter or route-result tests fail, workers stop and
  diagnose the lower failing layer before editing Python normalization.
