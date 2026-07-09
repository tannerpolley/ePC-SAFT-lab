---
issue: 269
title: "M4: add electrolyte GFPE closed-admission source gate"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/269
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: electrolyte
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-06-18"
---

# M4: add electrolyte GFPE closed-admission source gate

**Mirror Retention:** Keep

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/269
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-17-m4-equilibrium-issue-0191-electrolyte-gfpe-closed-admission-gate-plan.md
**Classification:** AFK
AFK/HITL: AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/269 using docs/superpowers/issues/2026-06-17-m4-equilibrium-issue-0269-add-electrolyte-gfpe-closed-admission-source-gate.md and docs/superpowers/plans/2026-06-17-m4-equilibrium-issue-0191-electrolyte-gfpe-closed-admission-gate-plan.md. Complete proof oracle: issue acceptance criteria checked.
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

Add the first executable #191 child gate by validating the Khudaida source
fixture, explicit-ion expansion, source parameter-bundle execution, native
electrolyte/charge diagnostics, and closed public route state.

This issue is a native sub-issue of https://github.com/ePC-SAFT/ePC-SAFT/issues/191.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Native GitHub sub-issue link: #269 is a sub-issue of #191.
- Blocked by: None.

## Acceptance Criteria

- [x] Khudaida source fixture rows parse, normalize, and expand formula-basis NaCl to explicit Na+ and Cl- rows with charge balance <= `1.0e-8`.
- [x] `paper_validation_parameter_path("2026_Khudaida")` can construct a native mixture for at least one expanded Khudaida feed row.
- [x] Native electrolyte contribution and phase-charge diagnostics run on source-backed Khudaida inputs and return finite active electrolyte terms.
- [x] `electrolyte_lle` remains absent from public routes, production families, proof routes, and route derivative evidence.
- [x] M4 registry and README record this as a closed-admission prerequisite, not public electrolyte GFPE admission.

## Resolution Notes

- Added `scripts/validation/check_electrolyte_gfpe_gate.py` as the retained proof checker for the Khudaida pre-association electrolyte gate.
- The checker reports the raw Khudaida paper-row closure drift separately (`max_raw_formula_row_sum_error` is about `0.01`) and normalizes finite source rows before explicit-ion expansion for native calls.
- The path-based `2026_Khudaida` paper-validation parameter bundle now constructs a native mixture, while the public string dataset lookup remains closed.
- Native diagnostics cover active electrolyte contribution terms plus charge-balance rows on source-backed expanded compositions, with association disabled only for the pre-association phase-charge smoke.
- Public electrolyte route admission remains closed.

## Blocked By

- None.

## Non-goals

- No public electrolyte route admission.
- No packaged provider dataset registration.
- No electrolyte TPD, HELD2 candidate generation, or route postsolve certification.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_gfpe_gate_checker.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py
uv run --no-sync python scripts/data/curate_paper_validation_parameters.py
uv run --no-sync python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments,
labels, milestone, sub-issue linkage, Project fields, and PR linkage.
