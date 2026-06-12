# M4: add Pereira-style neutral LLE HELD reliability campaign

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/247
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-12-m4-equilibrium-pereira-held-neutral-lle-reliability-plan.md
**Classification:** AFK
**Labels:** validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve M4 issue: add Pereira-style neutral LLE HELD reliability campaign after #246 is complete; implement the checker, retained full-campaign artifacts, docs updates, and proof oracle.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the full-campaign neutral LLE HELD reliability gate needed before
associating GFPE can borrow the neutral HELD 1.0 algorithm path. The issue
creates a validation checker for 100 accepted unstable neutral LLE conditions
with 100 independent route-refinement repeats per condition, retained JSON/CSV
evidence, start-policy receipts, first-failure reproduction rows, and
documentation wiring that preserves source-backed LLE, generalized phase-set,
and associating boundaries.

## Acceptance Criteria

- [ ] `scripts/validation/check_held_reliability.py` exists with
  `--family neutral-lle`, `--conditions`, `--repeats`, `--seed`,
  `--require-complete`, `--json`, and `--output-dir`.
- [ ] Unit tests cover complete campaign summary, campaign-size rejection,
  objective-spread rejection, missing start-policy receipts, and first-failure
  reproduction output.
- [ ] Shared neutral LLE validation runtime removes duplicated synthetic LLE
  fixture parameters from `check_phase_discovery.py`.
- [ ] The full campaign accepts exactly 100 unstable neutral LLE conditions and
  runs exactly 100 independent repeats for each accepted condition.
- [ ] The retained summary records `attempted_repeats: 10000`,
  `failed_repeats: 0`, and `accepted_conditions: 100`.
- [ ] Every accepted repeat reports converged continuous TPD, verified Stage II
  dual loop, Stage II bound gap within tolerance, Stage III Ipopt refinement
  consuming Stage II replay metadata, `solver_status == "success"`, and
  `application_status == "solve_succeeded"`.
- [ ] Every accepted repeat satisfies material balance `<= 1.0e-8`, pressure
  consistency `<= 1.0e-3`, ln fugacity consistency `<= 1.0e-6`, phase distance
  `>= 1.0e-6`, and `selected_candidate_count == 2`.
- [ ] Every condition's 100 repeats agree on phase count and selected phase
  roles with objective spread `<= 1.0e-6`.
- [ ] Retained outputs are written under
  `analyses/package_validation/held_lle_reliability/shared/results`.
- [ ] The campaign records current commit, native module path, build-refresh
  command or #246 freshness receipt, candidate start sources, start policy,
  stage statuses, route status, and first failure if any.
- [ ] Docs state this is synthetic neutral LLE algorithm reliability evidence,
  not source-backed public LLE showcase evidence, generalized phase-set
  completion, or associating GFPE admission.

## Dependency Satisfied

- https://github.com/ePC-SAFT/ePC-SAFT/issues/246 closed through
  https://github.com/ePC-SAFT/ePC-SAFT/pull/248 on 2026-06-12.

## Non-goals

- No associating, electrolyte, reactive, CE, or CPE route admission.
- No generalized phase-count or LLLE production claim.
- No source-backed neutral LLE public showcase.
- No replacement of #246 fresh-native receipts.
- No capability promotion solely from this reliability campaign.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_held_reliability_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_held_reliability.py --family neutral-lle --conditions 100 --repeats 100 --seed 1729 --require-complete --json --output-dir analyses/package_validation/held_lle_reliability/shared/results
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body Text

Published body matches this mirror's issue metadata, build scope, acceptance
criteria, blocker, non-goals, and proof oracle.
