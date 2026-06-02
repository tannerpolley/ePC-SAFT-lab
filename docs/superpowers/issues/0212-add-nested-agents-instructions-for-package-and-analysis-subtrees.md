---
issue: 212
title: "Add nested AGENTS.md instructions for package and analysis subtrees"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/212"
state: "open"
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: null
capability: "agent-instructions"
backend: null
readiness: "ready"
release_target: null
last_synced: "2026-06-02"
---

# Add Nested AGENTS.md Instructions For Package And Analysis Subtrees

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/212
**GitHub Milestone:** M0 - Governance
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-02-nested-agents-instruction-strategy-design.md
**Source Plan:** docs/superpowers/plans/2026-06-02-nested-agents-instruction-strategy-plan.md
**Classification:** AFK
**Labels:** type:task, status:ready, agent-ready, area:docs
**Goal Command:** /goal Add five approved nested AGENTS.md files plus a repo-structure guard, following docs/superpowers/plans/2026-06-02-nested-agents-instruction-strategy-plan.md
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## What To Build

Add the five approved nested `AGENTS.md` files for provider, equilibrium,
regression, analyses, and paper-validation subtrees. Add a structure guard so
the expected nested files remain discoverable, extra nested instruction files
are rejected, and the source spec remains tracked in the Superpowers Project
layout.

## Acceptance Criteria

- [ ] `packages/epcsaft/AGENTS.md` exists and contains provider-only instructions for EOS/state/parameter/native SDK work.
- [ ] `packages/epcsaft-equilibrium/AGENTS.md` exists and contains equilibrium route, Ipopt, GFPE, solver-status, and derivative-assembly instructions.
- [ ] `packages/epcsaft-regression/AGENTS.md` exists and contains regression/Ceres/target-dataset instructions.
- [ ] `analyses/AGENTS.md` exists and contains reproducible analysis artifact-layout instructions.
- [ ] `analyses/paper_validation/AGENTS.md` exists and contains the paper-validation exception layout from `docs/pages/project_structure.rst`.
- [ ] `tests/workflows/repo/test_project_structure.py` fails if any expected nested instruction file is missing, if extra nested `AGENTS.md` files appear outside the approved set, or if nested instructions contain machine-local user paths.
- [ ] `tests/workflows/repo/test_project_structure.py` tracks the source spec under `docs/superpowers/specs`.
- [ ] Public package APIs, native code, capability claims, and runtime behavior are unchanged.

## Blocked By

- None

## Non-Goals

- No provider, equilibrium, regression, or native implementation behavior changes.
- No nested instruction files below package internals such as `native/`, `tests/`, or `src/`.
- No duplication of root Git, cleanup, IntelliJ, tracker, or global milestone policy inside nested files.
- No user-level Codex instruction edits.

## Proof Oracle

- `rg --files -g AGENTS.md`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`
