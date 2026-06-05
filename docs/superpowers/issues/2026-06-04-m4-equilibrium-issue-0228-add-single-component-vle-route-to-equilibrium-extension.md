---
issue: 228
title: "Add single-component VLE route to equilibrium extension"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/228"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "vle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-04-m4-equilibrium-single-component-vle-route.md"
source_plan: "docs/superpowers/plans/2026-06-04-m4-equilibrium-single-component-vle-route-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0228-add-single-component-vle-route-to-equilibrium-extension
last_synced: "2026-06-05"
---

# Add single-component VLE route to equilibrium extension

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/228
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m4-equilibrium-single-component-vle-route.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m4-equilibrium-single-component-vle-route-plan.md
**Branch:** codex/issue-0228-add-single-component-vle-route-to-equilibrium-extension
**AFK/HITL:** HITL
**Labels:** type:task, status:ready, ready-for-human, area:equilibrium, area:derivatives, backend:ipopt, native, python-api
**Goal Command:** None - HITL review required
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

Add a production-owned single-component VLE route in `epcsaft-equilibrium`.
The provider package continues to own EOS state/property evaluation, while the
equilibrium extension owns coexistence route assembly, Ipopt/NLP discipline,
result payloads, diagnostics, and failure policy.

## Current Implementation Note

The branch implements the native residual block as
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/saturation_block.*`
and wires the production route through the existing derived pressure-route
substrate in
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp`.
The public route remains `single_component_vle`; association remains rejected
until exact association sensitivities or lifted association-site variables are
covered by a separate M4 issue.

## Acceptance Criteria

- [ ] `epcsaft-equilibrium` exposes a production-owned single-component VLE route or route block; the provider package does not expose a new vapor-pressure API.
- [ ] The route solves common `P_sat`, vapor density, and liquid density from pressure equality and chemical-potential or fugacity equality.
- [ ] Route initialization, variable scaling, bounds, diagnostics, and failure policy are owned by the equilibrium extension.
- [ ] Exact derivative/NLP evidence is reported consistently with existing equilibrium capability contracts.
- [ ] Public result payloads include `P_sat`, vapor density, liquid density, residuals, solver status, and route diagnostics without claiming broader binary bubble/dew or GFPE behavior.
- [ ] CMake/source lists and focused equilibrium tests cover the new files.

## Blocked by

- None

## Non-goals

- No provider vapor-pressure API.
- No binary bubble/dew, full GFPE, HELD, or phase-discovery route rewrite.
- No M5 regression package work.
- No dependency on the M8 Python toybox saturation solver.

## Proof Oracle

- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Target epcsaft_equilibrium_native_core -Parallel 10`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python scripts/dev/validate_project.py quick`
