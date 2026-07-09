---
issue: 349
title: "M4: add HELD2 public-route scenario validation ladder"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/349
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: electrolyte
backend: Ipopt
readiness: ready
release_target: equilibrium-0.x
source_spec: docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
source_plan: docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
afk_hitl: AFK
branch: codex/issue-0349-held2-public-route-scenario-validation-ladder
last_synced: "2026-06-28"
---

# M4: add HELD2 public-route scenario validation ladder

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/349
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

## Outcome Summary

**Intent:** Add retained public-route scenario validation for full HELD2 behavior.
**Target Output:** Package tests and a checker cover stable, unstable, boundary, phase-label, neutral-limit, common-ion, and mixed-salt cases.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Package tests, validation checker, retained data snapshots where literature comparison is used, and public route diagnostics.
**Cutover:** Validate the public route across the scenario ladder before registry admission.
**Replaced Path:** Single representative admission or boundary-only validation used as full scenario evidence.
**Acceptance Proof:** Scenario checker and package-level pytest selector pass with real collected tests.
**Stop Criteria:** Stop if a required model-data comparison needs M5 parameter regression, untraceable inputs, or synthetic evidence.
**Avoid:** Do not hide failed fitted-model reproduction inside M4 algorithm proof.

## Acceptance Criteria

- [x] Scenario checker covers stable, unstable, boundary, phase-label, neutral-limit, common-ion, and mixed-salt cases.
- [x] Package-level pytest selectors collect and run real electrolyte HELD2 tests.
- [x] Scenario artifacts retain discovery, Stage III, postsolve, and residual diagnostics.
- [x] M5 regression blockers are created or referenced for fitted-model failures.

## Acceptance Evidence

- Checker: `check_electrolyte_held2_public_route_scenarios.py --json --require-complete` returns `complete=True`, no blockers, and 7 accepted scenarios.
- Public electrolyte route scenarios: unstable, boundary, and phase-label cases use the source-backed Khudaida electrolyte LLE public route with Stage II `dual_loop_verified`, Stage III `complete`, postsolve `complete`, phase distance `3.0328142543445402e-06 > 1e-08`, charge residual `0.0`, and mean-ionic transfer residual `2.1991608690541398e-05`.
- Stable and neutral-limit scenarios: binary neutral LLE public route retains `held_stage_i_status: no_negative_tpd_candidate_found`, `min_tpd: -8.806807572753356e-16`, phase distance `0.9888667362181911`, and no charged residual-family claim.
- Common-ion scenario: Ascani 2022 NaCl/KCl basis fixture retains rank `2/2`, max charge residual `3.469446951953614e-18`, and round-trip residual `8.809142651444724e-19`.
- Mixed/asymmetric scenario: Ascani multivalent counterion fixture retains rank `3/3`, max charge residual `0.0`, and round-trip residual `2.425902360936316e-18`.
- Model-data regression boundary: fitted Khudaida figure reproduction remains referenced to M5 #338; this M4 gate does not hide new fitted parameters or treat model regression as scenario proof.

## Closed blockers

- #348

## Proof Oracle

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and scenario" -q
```
