---
issue: 345
title: "M4: implement electrolyte continuous TPD minimizer in reduced coordinates"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/345"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md"
source_plan: "docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0345-electrolyte-continuous-tpd-reduced-coordinates
last_synced: "2026-06-28"
---

# M4: implement electrolyte continuous TPD minimizer in reduced coordinates

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/345
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**Classification:** AFK after #344 closes
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task
**Goal Command:** /goal Resolve issue 345 by implementing continuous reduced-electroneutral TPD minimization diagnostics.
**Execution Mode:** Direct current-thread resolve
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR-ready handoff
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus package validation

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md#slice-2-continuous-reduced-electroneutral-tpd-minimizer-345
**Intent:** Add continuous reduced-electroneutral TPD minimization as the HELD2 Stage I substrate.
**Target Output:** Native minimizer diagnostics for governed starts, charge residuals, bounds, domain margins, and convergence status.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Native electrolyte discovery core, Python package tests, and `check_electrolyte_held2_continuous_tpd.py`.
**Cutover:** Keep public route admission closed; this slice only creates minimizer evidence.
**Replaced Path:** Deterministic #302 screening used as a substitute for continuous TPD minimization.
**Acceptance Proof:** The continuous TPD checker and focused package tests pass.
**Stop Criteria:** Stop on missing derivative evidence, non-electroneutral trial phases, hidden charge clipping, or untraceable starts.
**Avoid:** Do not add Stage I, Stage II, Stage III, or public-route success claims in this slice.

## Acceptance Criteria

- [x] Continuous reduced-coordinate TPD returns replayable diagnostics for accepted and rejected starts.
- [x] Per-phase electroneutrality and positive-domain margins are retained.
- [x] Deterministic #302 screening remains seed/support evidence only.
- [x] Public `electrolyte_lle` behavior is unchanged except for closed-state diagnostics.

## Closed prerequisite

- #344

## Proof Oracle

```powershell
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and continuous and tpd" -q
uv run --no-sync python scripts\validation\check_electrolyte_held2_continuous_tpd.py --json --require-complete
```

## Resolution Evidence

- Native binding: `_native_electrolyte_held2_continuous_tpd_minimizer`.
- Native backend: `continuous_reduced_electroneutral_tpd_minimization`.
- Continuous solver backend: `continuous_reduced_electroneutral_coordinate_search`.
- Algorithm scope: `held2_continuous_reduced_electroneutral_tpd_minimizer_only`.
- Continuous starts: 4 total, 4 solved, 2 accepted, 2 rejected.
- Continuous TPD minimum: -0.36067618496483983.
- Maximum charge residual: 0.0.
- Maximum normalization residual: 1.1102230246251565e-16.
- Minimum positive domain margin: 1.3193414734302342e-05.
- Deterministic screening role: `seed_support_only`; deterministic screening is not claimed as full HELD.
- Public route admission: `separate_public_admission_gate`.
- Stage status boundary: Stage I certificate, Stage II discovery, Stage III refinement, and public admission remain pending follow-on slices.
