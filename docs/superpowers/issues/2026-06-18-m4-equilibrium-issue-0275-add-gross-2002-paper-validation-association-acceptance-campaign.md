---
issue: 275
title: "M4: add Gross 2002 paper-validation association acceptance campaign"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/275"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-18-m4-equilibrium-gross-2002-association-acceptance-pass.md"
source_plan: null
afk_hitl: "AFK"
branch: null
last_synced: "2026-06-18"
---

# M4: add Gross 2002 paper-validation association acceptance campaign

**Mirror Retention:** Keep

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/275
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-18-m4-equilibrium-gross-2002-association-acceptance-pass.md
**Source Plan:** None
**Classification:** AFK
AFK/HITL: AFK
**Labels:** agent-ready, status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/275 using docs/superpowers/issues/2026-06-18-m4-equilibrium-issue-0275-add-gross-2002-paper-validation-association-acceptance-campaign.md and docs/superpowers/specs/2026-06-18-m4-equilibrium-gross-2002-association-acceptance-pass.md. Complete proof oracle: issue acceptance criteria checked.
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

Add a source-backed Gross/Sadowski 2002 association acceptance campaign under
`analyses/paper_validation/2002_gross` that covers all relevant paper figures,
with Figures 8 and 10 as the hard phase-split gates. The campaign must keep
source data, generated model data, retained plots, Matplotlib sidecars, and
campaign summaries attached to the existing paper-validation tree.

## Acceptance Criteria

- [ ] Add a Gross 2002 association acceptance manifest under `analyses/paper_validation/2002_gross/shared` that names the participating figures, hard-gate figures, source paths, parameter sources, route families, and thresholds.
- [ ] Keep all per-figure source data, scripts, and results inside the existing `analyses/paper_validation/2002_gross/figures/figure_NN` lanes.
- [ ] Preserve the existing Figure 8 methanol/cyclohexane source-backed fixture and connect its retained source rows, model output, plot data, and exact association-Hessian evidence to the campaign summary.
- [ ] Add Figure 10 water/1-pentanol as the hard cross-association VLLE/LLE stress gate, including source data, paper parameters, exact association derivative receipts, mass-action residuals, and retained mirror plots.
- [ ] Add Figure 1 as the pure-association sanity mirror before broad association confidence claims.
- [ ] Add Figures 2-7 and 9 as campaign-ready VLE mirrors only after their source points, physical units, digitization uncertainty, and required nonassociating pure-parameter provenance are retained.
- [ ] Resolve the Figure 2 methanol-isobutane/isobutanol source-text discrepancy before Figure 2 evidence can count.
- [ ] Add `scripts/validation/check_gross_2002_association_acceptance.py` with `--json`, `--require-complete`, `--require-exact-association-hessian`, and `--require-fresh-native` support.
- [ ] Retain campaign summary JSON/CSV under `analyses/paper_validation/2002_gross/shared/results`.
- [ ] Render every new or updated Gross 2002 mirror plot and retain the plotted-data CSV and Matplotlib sidecar.
- [ ] Keep capability text evidence-scoped; do not broaden electrolyte, reactive, CE, CPE, generalized phase-count, or broad associating-family claims from this campaign.

## Blocked By

- None

## Blocks

- https://github.com/ePC-SAFT/ePC-SAFT/issues/191, because electrolyte GFPE should not rely on association confidence until this Gross 2002 acceptance pass or an explicitly narrower approved substitute is complete.

## Non-goals

- No electrolyte admission.
- No HELD2.0 electrolyte validation.
- No reactive, CE, or CPE admission.
- No generalized phase-count or LLLE claim from a two-phase Gross 2002 mirror.
- No approximate association closure as campaign acceptance evidence.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments,
labels, milestone, dependency edges, issue type, and project fields.
