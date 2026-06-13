---
issue: 250
title: "M4: add source-backed neutral nonassociating LLE showcase fixture"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/250"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md"
source_plan: "docs/superpowers/plans/2026-06-13-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0250-source-backed-neutral-lle-showcase
last_synced: "2026-06-13"
---

# M4: add source-backed neutral nonassociating LLE showcase fixture

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/250
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md
**Source Plan:** docs/superpowers/plans/2026-06-13-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
**Goal Command:** /goal Resolve M4 issue 250: add the first source-backed neutral nonassociating LLE fixture, checker, retained analysis, and registry evidence for the current neutral route="lle" utility, without broadening associating, electrolyte, reactive, CE, CPE, or generalized phase-set claims.
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

Add the first source-backed neutral nonassociating LLE fixture and showcase for
the current production `route="lle"` utility. The work must audit a
perfluoroalkane + n-alkane source candidate, retain fixture data, prove
current-route acceptance with HELD Stage II/III and exact-Hessian evidence,
render retained-data figures, and update the M4 registry without broadening
associating, electrolyte, reactive, CE, CPE, or generalized phase-set claims.

## Acceptance Criteria

- [ ] `data/reference/equilibrium_benchmarks/neutral_lle/<source_slug>/` contains source notes, metadata, pure parameters, binary interactions, feed rows, experimental tie-lines, and thresholds.
- [ ] `scripts/validation/check_neutral_lle_showcase.py --json --require-complete` proves fixture completeness, route acceptance, exact Hessian support, HELD Stage II replay, HELD Stage III replay consumption, material balance, pressure consistency, fugacity consistency, phase distance, and candidate completeness.
- [ ] Package-level tests prove the source-backed fixture through the current `route="lle"` utility.
- [ ] `analyses/package_validation/neutral_nonassociating_lle_showcase/` writes retained JSON/CSV data and renders PNG/SVG figures from retained data only.
- [ ] M4 registry and docs state this is neutral nonassociating LLE showcase evidence only.

## Blocked by

- None

## Non-goals

- No associating LLE admission.
- No electrolyte LLE admission.
- No reactive LLE admission.
- No salting-out, SLE, precipitation, CE, or CPE claims.
- No generalized arbitrary phase-count or LLLE production claim.
- No public route broadening beyond the current neutral `route="lle"` utility.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_neutral_lle_showcase_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_showcase_fixture.py -q
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --fixture data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2010_perfluoroalkane_alkane --json --require-complete
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body Text

```markdown
# M4: add source-backed neutral nonassociating LLE showcase fixture

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/250
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md
**Source Plan:** docs/superpowers/plans/2026-06-13-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
**Goal Command:** /goal Resolve M4 issue 250: add the first source-backed neutral nonassociating LLE fixture, checker, retained analysis, and registry evidence for the current neutral route="lle" utility, without broadening associating, electrolyte, reactive, CE, CPE, or generalized phase-set claims.

See the source plan for the task-by-task implementation sequence and proof oracle.
```
