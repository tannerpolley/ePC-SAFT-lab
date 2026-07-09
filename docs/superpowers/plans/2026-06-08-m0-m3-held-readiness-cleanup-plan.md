# M3 HELD Readiness Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the M3 / HELD 1.0 readiness cleanup by keeping #161 as an independent direct CppAD evidence issue for explicit association and Picard, anchoring #208 to closed provider issue #207, and splitting the capability-registry mismatch into a separate follow-up issue.

**Architecture:** Keep this as tracker and documentation cleanup only. Repo-local mirrors and milestone pages must match live GitHub issue state, while source implementation remains out of scope. #207 is the closed M3 provider derivative-bundle dependency; #208 should become ready after verifying that #207's provider contract is present in the checkout.

**Tech Stack:** Markdown, GitHub CLI (`gh`), GitHub Issues dependency API, PowerShell, `rg`, Sphinx docs validation, repo cleanup hook.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-08-m3-held-readiness-cleanup.md`
- Source Spec Commit: `da299c39`
- Primary Milestone: `M0 - Governance`
- Affected Milestones: `M3 - EOS`, `M4 - Equilibrium`, `M6 - Validation`
- Affected Packages: `packages/epcsaft`, `packages/epcsaft-equilibrium`
- GitHub Issues: #161, #207, #208
- User Decisions:
  - Include local repo mirrors and live GitHub tracker updates.
  - Find an existing M3 dependency issue before creating one.
  - Keep #161 open as an independent direct CppAD proof issue with the Picard path still present.
  - Mark #208 ready after verifying #207 is present in the checkout.
  - Split the `single_component_vle` provider/equilibrium capability mismatch into a separate follow-up issue.

## Current Verified Tracker Facts

- #161 is open in `M3 - EOS` with `status:needs-design`.
- #207, `Expose objective-free local phase EOS derivative bundle`, is closed in `M3 - EOS`.
- GitHub already records #208 as blocked by #207.
- #208 is open in `M4 - Equilibrium` and still carries `status:blocked` locally and on GitHub.
- No local #207 issue mirror exists under `docs/superpowers/issues`.
- The current checkout contains provider `EosLocalPhaseDerivativeBundle` and `eos_local_phase_helmholtz_derivatives_cpp()`.
- The equilibrium extension still owns `target_pressure` and pressure-work objective assembly in `eos_phase_block.cpp` and `phase_block_derivatives.cpp`, which is expected #208 implementation scope.

## TDD, Debug, And Verification Policy

This is docs/tracker cleanup, not feature or bug implementation, so test-driven development does not apply. Execution must still use `superpowers:verification-before-completion` before claiming completion.

Required verification:

- Live GitHub readback for #161, #207, #208, and #208 dependency edges.
- Provider/equilibrium contract seam searches with `rg`.
- `uv run python scripts/dev/validate_project.py docs`.
- Repo-scoped cleanup hook.
- Final `git status --short --branch`.

## Acceptance Criteria

- [ ] #161 is open on GitHub with a comment that preserves the M8 evidence, keeps the Picard path present, and records direct provider CppAD proof as independent future work.
- [ ] The #161 local mirror and `docs/superpowers/milestones/M3-eos/README.md` no longer imply that the final M8 decision memo is pending or that #161 blocks HELD/M4/#208.
- [ ] A local #207 mirror exists and records the closed provider derivative-bundle contract.
- [ ] #208 local mirror, #208 plan, M4 README, and live GitHub labels no longer treat #208 as blocked by missing M3 provider work after #207 is verified.
- [ ] #148 is not edited unless the executor finds new ambiguity; the current narrow neutral HELD-style evidence boundary is preserved.
- [ ] A separate M6 follow-up issue is created for the `single_component_vle` capability evidence mismatch.
- [ ] Docs validation passes.
- [ ] Cleanup hook reports no matching leftover repo-owned processes.

## Non-Goals

- No provider EOS implementation.
- No equilibrium route implementation.
- No HELD/GFPE route expansion.
- No public route exposure changes.
- No associating, electrolyte, reactive, or generalized multiphase claims.
- No `epcsaft-regression` work.
- No closure of #208 in this cleanup plan.
- No direct edits to `.chatgpt` packet files.

## File Map

- Create: `docs/superpowers/issues/2026-06-01-m3-eos-issue-0207-expose-objective-free-local-phase-eos-derivative-bundle.md`
- Modify: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
- Modify: `docs/superpowers/issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md`
- Modify: `docs/superpowers/milestones/M3-eos/README.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md`
- Live tracker: `https://github.com/ePC-SAFT/ePC-SAFT/issues/161`
- Live tracker: `https://github.com/ePC-SAFT/ePC-SAFT/issues/207`
- Live tracker: `https://github.com/ePC-SAFT/ePC-SAFT/issues/208`
- Live tracker: new `M6 - Validation` follow-up issue for capability evidence mismatch.

## Tasks

### Task 1: Preflight And Contract Evidence

**Files:**
- Read: `docs/superpowers/specs/2026-06-08-m3-held-readiness-cleanup.md`
- Read: `docs/agents/issue-tracker.md`
- Read: `docs/superpowers/milestones/M3-eos/README.md`
- Read: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Read: `packages/epcsaft/src/epcsaft/native/eos/core_internal.h`
- Read: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/local_helmholtz_derivatives.cpp`
- Read: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/eos_phase_block.cpp`
- Read: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/derivatives/phase_block_derivatives.cpp`
- Test: GitHub issue and dependency readbacks.

- [ ] **Step 1: Confirm working-tree state before changes**

Run:

```powershell
git status --short --branch
```

Expected:

```text
current branch may be ahead of origin by existing local commits
only .gitignore is dirty before cleanup edits
```

If additional files are dirty, inspect them before editing and do not overwrite unrelated user work.

- [ ] **Step 2: Confirm #161/#207/#208 live issue states**

Run:

```powershell
gh issue view 161 --json number,title,state,milestone,labels,url
gh issue view 207 --json number,title,state,milestone,labels,url
gh issue view 208 --json number,title,state,milestone,labels,url
```

Expected:

```text
#161 state OPEN, milestone M3 - EOS
#207 state CLOSED, milestone M3 - EOS
#208 state OPEN, milestone M4 - Equilibrium
```

- [ ] **Step 3: Confirm #208 is blocked by #207**

Run:

```powershell
gh api /repos/ePC-SAFT/ePC-SAFT/issues/208/dependencies/blocked_by --jq '.[].number'
```

Expected:

```text
207
```

- [ ] **Step 4: Verify provider contract exists locally**

Run:

```powershell
rg -n "EosLocalPhaseDerivativeBundle|eos_local_phase_helmholtz_derivatives_cpp" packages/epcsaft/src/epcsaft/native/eos packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1
```

Expected: matches in provider native EOS files, including `core_internal.h` and `local_helmholtz_derivatives.cpp`.

- [ ] **Step 5: Verify old provider objective terms are absent from provider-owned EOS paths**

Run:

```powershell
rg -n "eos_phase_objective_derivatives_cpp|target_pressure|pressure_work" packages/epcsaft/src/epcsaft/native/eos packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1
```

Expected: no matches.

- [ ] **Step 6: Verify equilibrium still owns pressure-work assembly for #208**

Run:

```powershell
rg -n "target_pressure|pressure_work|eos_local_phase_helmholtz_derivatives_cpp" packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/eos_phase_block.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/derivatives/phase_block_derivatives.cpp
```

Expected: matches in equilibrium files only. This confirms #208 is implementation work, not M3 provider work.

- [ ] **Step 7: Commit checkpoint**

No files should be changed by Task 1. Do not commit.

### Task 2: Keep #161 As Independent CppAD Evidence Issue

**Files:**
- Modify: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
- Modify: `docs/superpowers/milestones/M3-eos/README.md`
- Test: `gh issue view 161 --json state,labels`
- Test: `uv run python scripts/dev/validate_project.py docs`

- [ ] **Step 1: Update #161 local mirror frontmatter**

Keep:

```yaml
state: "open"
```

Set:

```yaml
readiness: "needs direct CppAD proof"
last_synced: "2026-06-08"
```

- [ ] **Step 2: Replace the #161 local mirror summary**

Replace the current summary paragraph with text that says #161 stays open as an
independent explicit-association and Picard evidence issue. Preserve that the
tested `n = 7`, `lambda = 0.5` damped Picard toybox result is not sufficient for
provider admission, and state that Picard still needs direct provider CppAD
testing before provider admission.

- [ ] **Step 3: Update the #161 disposition section**

Rename `## Final Disposition` to `## Current Disposition` and record:

- the final M8 memo rejects provider admission for the tested damped Picard
  framing;
- the stress memo selects `retire_picard` for that framing;
- those decisions do not remove Picard from the independent direct CppAD proof
  issue;
- Picard stays present as a fixed-depth explicit association candidate family;
- #161 is not a HELD 1.0, M4, or #208 dependency.

- [ ] **Step 4: Update M3 README current-open and recently-closed tables**

Keep #161 under `## Current Open Issues` with readiness
`needs direct CppAD proof`, and do not list #161 under `## Recently Closed`.

- [ ] **Step 5: Reopen or confirm live GitHub #161 as independent**

Run:

```powershell
$comment = @'
Reopening/keeping this as an independent explicit-association and Picard CppAD evidence issue.

The M8 evidence still retires the tested damped Picard provider-admission path:

- `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md` recommends no provider implementation for that tested framing.
- `analyses/package_validation/explicit_association_toybox/docs/picard_stress_rescue_or_retire_decision.md` selects `retire_picard` for that tested framing.

The remaining scope includes direct provider CppAD evidence for the fixed-depth Picard path and any other explicit association closure candidate. This issue is not a HELD 1.0, M4, or #208 dependency.
'@
gh issue reopen 161 --comment $comment
```

Expected: GitHub reports #161 open.

- [ ] **Step 6: Verify #161 open**

Run:

```powershell
gh issue view 161 --json state,labels --jq '{state: .state, labels: [.labels[].name]}'
```

Expected:

```json
state is OPEN
```

- [ ] **Step 7: Validate docs after #161 cleanup**

Run:

```powershell
uv run python scripts/dev/validate_project.py docs
```

Expected: Sphinx build succeeds.

- [ ] **Step 8: Commit #161 cleanup**

Run:

```powershell
git add -- docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md docs/superpowers/milestones/M3-eos/README.md
git commit -m "Keep explicit association CppAD proof independent"
```

Expected: commit succeeds and includes only the #161 mirror plus M3 README changes.

### Task 3: Anchor #207 Locally And Mark #208 Ready

**Files:**
- Create: `docs/superpowers/issues/2026-06-01-m3-eos-issue-0207-expose-objective-free-local-phase-eos-derivative-bundle.md`
- Modify: `docs/superpowers/milestones/M3-eos/README.md`
- Modify: `docs/superpowers/issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md`
- Modify: `docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Test: `gh issue view 208 --json labels`
- Test: `uv run python scripts/dev/validate_project.py docs`

- [ ] **Step 1: Create the local #207 mirror**

Create `docs/superpowers/issues/2026-06-01-m3-eos-issue-0207-expose-objective-free-local-phase-eos-derivative-bundle.md` with:

```markdown
---
issue: 207
title: "Expose objective-free local phase EOS derivative bundle"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/207"
state: "closed"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "core"
capability: "derivatives"
backend: "CppAD"
readiness: "closed"
release_target: "core-0.x"
source_spec: Null
source_plan: Null
afk_hitl: "AFK"
branch: Null
last_synced: "2026-06-08"
---

# Expose objective-free local phase EOS derivative bundle

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/207
Synced Commit: https://github.com/ePC-SAFT/ePC-SAFT/commit/58bcf830
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This closed mirror exists because #208
depends on #207 and local M4 planning needs a durable repo-local reference.

## Summary

Provider EOS exposes an objective-free local phase thermodynamic derivative
bundle with CppAD/implicit chain-rule coverage. The provider contract has no
equilibrium objective, target-pressure, or pressure-work semantics.

## Acceptance Criteria

- [x] Provider EOS derivative APIs no longer expose solver-objective names,
  target pressure, or pressure-work terms.
- [x] A local phase derivative bundle exposes the derivative orders needed by
  equilibrium without making provider EOS own an NLP objective.
- [x] Born, SSM/DS, relative-permittivity, and implicit association chain-rule
  coverage remains provider-owned and CppAD-backed.
- [x] Provider build lists, native SDK manifests, declarations, and focused
  provider tests use the provider derivative interface.
- [x] No `packages/epcsaft-equilibrium` or `packages/epcsaft-regression`
  implementation behavior changed except through documented provider contracts.

## Proof Oracle

- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
- `uv run python run_pytest.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py -q`
- `rg -n "eos_phase_objective_derivatives_cpp|target_pressure|pressure_work" packages/epcsaft/src/epcsaft/native/eos`

## Tracker Metadata

- Milestone: `M3 - EOS`
- Package: `core`
- Capability: `derivatives`
- Backend: `CppAD`
- Readiness: `closed`
- AFK/HITL: `AFK`
- Release target: `core-0.x`
- Labels: `agent-ready, native, area:core, area:derivatives, backend:cppad, type:task`
```

- [ ] **Step 2: Add #207 to the M3 README closed table**

In `docs/superpowers/milestones/M3-eos/README.md`, add this row at the top of `## Recently Closed`, directly after the #161 row added in Task 2:

```markdown
| [#207](https://github.com/ePC-SAFT/ePC-SAFT/issues/207) | [commit 58bcf830](https://github.com/ePC-SAFT/ePC-SAFT/commit/58bcf830) | `derivatives` | `CppAD` | Exposed the objective-free local phase EOS derivative bundle needed by #208. |
```

- [ ] **Step 3: Update #208 mirror readiness and dependency wording**

In `docs/superpowers/issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md`, change:

```yaml
readiness: "blocked"
```

to:

```yaml
readiness: "ready"
```

Set `last_synced` to `"2026-06-08"`.

Replace the acceptance criterion:

```markdown
- [ ] This issue is blocked by the M3 provider derivative bundle issue until that provider contract is merged.
```

with:

```markdown
- [ ] The closed #207 provider derivative bundle contract is verified in the checkout before M4 route-assembly edits begin.
```

In tracker metadata, replace:

```markdown
- Readiness: `blocked`
- Labels: `native, area:equilibrium, area:derivatives, backend:cppad, backend:ipopt, status:blocked, type:task`
```

with:

```markdown
- Readiness: `ready`
- Labels: `native, area:equilibrium, area:derivatives, backend:cppad, backend:ipopt, ready-for-human, type:task`
```

- [ ] **Step 4: Update #208 plan wording**

In `docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md`, replace:

```markdown
- [ ] This issue is blocked by the M3 provider derivative bundle issue until that provider contract is merged.
```

with:

```markdown
- [ ] The closed #207 provider derivative bundle contract is verified in the checkout before M4 route-assembly edits begin.
```

Replace Task 1 Step 1:

```markdown
- [ ] Confirm GitHub issue #208 is still `blocked` and verify blocker/design state before code changes.
```

with:

```markdown
- [ ] Confirm GitHub issue #208 is `ready`, verify #207 is closed and linked as the completed M3 dependency, and verify the provider derivative bundle exists in the checkout before code changes.
```

- [ ] **Step 5: Update M4 README #208 row**

In `docs/superpowers/milestones/M4-equilibrium/README.md`, replace the #208 row with:

```markdown
| [#208](https://github.com/ePC-SAFT/ePC-SAFT/issues/208) | `derivatives` | `CppAD` | `ready` | Move equilibrium objective assembly onto the closed #207 provider derivative bundle contract. |
```

- [ ] **Step 6: Update live GitHub #208 labels and comment**

Run:

```powershell
gh issue edit 208 --remove-label "status:blocked" --add-label "ready-for-human"
gh issue comment 208 --body "M3 dependency #207 is closed and already linked as the completed blocker. Local cleanup now treats #208 as ready for M4 route-assembly work after verifying the provider derivative bundle exists in the checkout."
```

Expected: #208 no longer has `status:blocked` and has `ready-for-human`.

- [ ] **Step 7: Verify live #208 labels and dependency**

Run:

```powershell
gh issue view 208 --json state,labels --jq '{state: .state, labels: [.labels[].name]}'
gh api /repos/ePC-SAFT/ePC-SAFT/issues/208/dependencies/blocked_by --jq '.[].number'
```

Expected:

```text
state remains OPEN
labels include ready-for-human
labels exclude status:blocked
blocked_by includes 207
```

- [ ] **Step 8: Validate docs after #207/#208 cleanup**

Run:

```powershell
uv run python scripts/dev/validate_project.py docs
```

Expected: Sphinx build succeeds.

- [ ] **Step 9: Commit #207/#208 cleanup**

Run:

```powershell
git add -- docs/superpowers/issues/2026-06-01-m3-eos-issue-0207-expose-objective-free-local-phase-eos-derivative-bundle.md docs/superpowers/milestones/M3-eos/README.md docs/superpowers/issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md docs/superpowers/milestones/M4-equilibrium/README.md
git commit -m "Mark M4 derivative assembly issue ready"
```

Expected: commit succeeds and does not include `.gitignore`.

### Task 4: Create Separate Capability Evidence Follow-Up

**Files:**
- Live tracker: new GitHub issue in `M6 - Validation`
- Test: `gh issue list --state open --search "single-component VLE activation capability evidence"`
- Test: GitHub issue readback using the URL returned by the creation command.

- [ ] **Step 1: Search for an existing capability mismatch issue**

Run:

```powershell
gh issue list --state open --search '"single_component_vle" "capability evidence" OR "single-component VLE" "activation capability evidence"' --json number,title,state,milestone,labels --limit 20
```

Expected: no exact issue for reconciling provider-side capability evidence with equilibrium activation for `single_component_vle`.

- [ ] **Step 2: Create the M6 follow-up issue**

Run:

```powershell
$body = @'
## Outcome

Reconcile provider-side capability evidence and validation routing with the equilibrium extension activation matrix for `single_component_vle`.

## Context

The equilibrium extension activation matrix production-exposes four families: `neutral_tp_flash`, `neutral_lle`, `single_component_vle`, and `bubble_dew_derived_routes`.

Provider-side capability evidence appears to list only three equilibrium production families and the run-pytest validation routing appears to assert the three-family shape. This may be intentional extension-local separation, or it may be stale capability evidence.

## Acceptance Criteria

- [ ] Verify whether provider-side `capability_evidence.py` should mirror `single_component_vle`.
- [ ] If the omission is intentional, document the ownership reason and add a regression test that protects the intended separation.
- [ ] If the omission is stale, update provider-side validation routing and tests so `single_component_vle` is represented consistently.
- [ ] Keep capability claims honest and avoid exposing broader equilibrium families.
- [ ] Run focused capability/activation contract tests and docs validation.

## Non-Goals

- No new public route exposure.
- No equilibrium solver implementation.
- No M3 provider derivative bundle changes.
- No regression package work.

## Proof Oracle

uv run python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/workflows/repo/test_run_pytest.py -q
uv run python scripts/dev/validate_project.py docs
'@
gh issue create --title "M6: Reconcile single-component VLE activation and capability evidence registries" --body $body --milestone "M6 - Validation" --label "validation,area:equilibrium,area:derivatives,type:task"
```

Expected: GitHub creates one M6 issue and returns its URL.

- [ ] **Step 3: Record the follow-up issue in the task completion note**

In the implementation handoff or PR body, record:

Record the exact GitHub issue URL returned by Step 2 after this label:

```text
Capability evidence follow-up:
```

Do not edit capability registries in this cleanup plan.

- [ ] **Step 4: Commit checkpoint**

No repo-local files should be changed by Task 4. Do not commit unless a local mirror is explicitly created in a later approved issue-publication pass.

### Task 5: Final Verification And Handoff

**Files:**
- Test: `docs/superpowers/**`
- Test: live GitHub issue readbacks for #161, #207, #208, and the M6 follow-up.
- Test: repo cleanup hook.

- [ ] **Step 1: Run docs validation**

Run:

```powershell
uv run python scripts/dev/validate_project.py docs
```

Expected: Sphinx build succeeds.

- [ ] **Step 2: Verify live tracker state**

Run:

```powershell
gh issue view 161 --json state --jq .state
gh issue view 207 --json state --jq .state
gh issue view 208 --json state,labels --jq '{state: .state, labels: [.labels[].name]}'
gh api /repos/ePC-SAFT/ePC-SAFT/issues/208/dependencies/blocked_by --jq '.[].number'
```

Expected:

```text
161: OPEN
207: CLOSED
208: OPEN, labels include ready-for-human, labels exclude status:blocked
208 blocked_by includes 207
```

- [ ] **Step 3: Run the cleanup hook**

Run:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected:

```text
No matching leftover development processes under the repository root.
```

- [ ] **Step 4: Confirm final git status**

Run:

```powershell
git status --short --branch
```

Expected:

```text
current branch may be ahead of origin by the cleanup commits
only the pre-existing .gitignore edit remains dirty
```

Only the pre-existing `.gitignore` modification should remain dirty.

- [ ] **Step 5: Final report**

Report:

```text
Verified current repo state:
Files changed:
Issue/doc changes applied:
Validation run:
Validation skipped and why:
Remaining blockers:
Next recommended issue:
```

## Proof Oracle

Run these commands before the plan is considered complete:

```powershell
uv run python scripts/dev/validate_project.py docs
```

```powershell
gh issue view 161 --json state --jq .state
gh issue view 207 --json state --jq .state
gh issue view 208 --json state,labels --jq '{state: .state, labels: [.labels[].name]}'
gh api /repos/ePC-SAFT/ePC-SAFT/issues/208/dependencies/blocked_by --jq '.[].number'
```

```powershell
rg -n "eos_phase_objective_derivatives_cpp|target_pressure|pressure_work" packages/epcsaft/src/epcsaft/native/eos packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1
```

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Risk Notes

- Live GitHub issue state is authoritative. If GitHub state differs from the verified state in this plan, stop and re-run the planning grill before mutating tracker state.
- #208 should become ready only after the provider bundle exists in the current checkout and #207 remains closed.
- The `single_component_vle` capability mismatch is deliberately split out. Do not repair capability registries inside the #161/#208 readiness cleanup.
- Keep `.gitignore` out of all cleanup commits unless the user explicitly assigns it.
