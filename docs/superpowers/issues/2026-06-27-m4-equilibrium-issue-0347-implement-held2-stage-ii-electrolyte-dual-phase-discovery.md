---
issue: 347
title: "M4: implement HELD2 Stage II electrolyte dual phase discovery"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/347"
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
branch: codex/issue-0347-held2-stage-ii-electrolyte-dual-phase-discovery
last_synced: "2026-06-27"
---

# M4: implement HELD2 Stage II electrolyte dual phase discovery

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/347
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md#slice-4-stage-ii-dualcutting-plane-discovery-347
**Intent:** Implement HELD2 Stage II dual/cutting-plane discovery for electrolyte phase sets.
**Target Output:** Candidate phase sets with lower/upper bounds, bound gaps, replay payloads, and rejection reasons.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Stage I certificate payloads, native discovery diagnostics, package tests, and `check_electrolyte_held2_stage_ii.py`.
**Cutover:** Provide replayable candidates for Stage III while keeping public route cutover separate.
**Replaced Path:** Counterion-pair diagnostics or TPD screening treated as full candidate discovery.
**Acceptance Proof:** Stage II checker and focused tests pass.
**Stop Criteria:** Stop on missing bound gaps, non-replayable candidates, rank-deficient reduced bases, or charge clipping.
**Avoid:** Do not claim Stage III or public-route success in this slice.

## Acceptance Criteria

- [x] Stage II reports lower/upper bounds and finite gaps for accepted candidate sets.
- [x] Rejected candidates retain explicit reasons, residuals, and charge/domain evidence.
- [x] Neutral-only, single-salt, common-ion, and mixed-salt bases are covered.
- [x] Candidate payloads are sufficient for Stage III replay.

## Acceptance Evidence

- Native route: `_native_electrolyte_held2_phase_discovery` now consumes the continuous reduced-electroneutral Stage I certificate and reports `dual_loop_verified`.
- Bound audit: lower bound `-0.36067618496483983`, upper bound `-0.36067618496483983`, bound gap `0.0`, tolerance `1e-08`, candidate count `5`, selected count `2`.
- Replay: phase fractions `[0.08980929801532778, 0.9101907019846722]`, max charge residual `0.0`, max composition-sum residual `0.0`, Stage III remains `pending_ipopt_refinement`.
- Rejections: three unselected candidates retain `not_selected_by_dual_loop_mass_balance_gate` with finite TPD, charge residual, composition residual, and positive domain margin diagnostics.
- Basis coverage: neutral-only, Khudaida NaCl single-salt, Ascani common-ion, and Ascani mixed-salt reduced bases all retain charge residuals `<= 3.5e-18`, composition residuals `0.0`, and round-trip residuals `<= 2.5e-18`.

## Closed blockers

- #346

## Proof Oracle

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_stage_ii.py --json --require-stage-i --require-bound-gap --require-replay --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and stage_ii" -q
```
