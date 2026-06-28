---
issue: 349
title: "M4: add HELD2 public-route scenario validation ladder"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/349"
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
branch: codex/issue-0349-held2-public-route-scenario-validation-ladder
last_synced: "2026-06-28"
---

# M4: add HELD2 public-route scenario validation ladder

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/349
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**Classification:** AFK after #348 closes
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

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

- [ ] Scenario checker covers stable, unstable, boundary, phase-label, neutral-limit, common-ion, and mixed-salt cases.
- [ ] Package-level pytest selectors collect and run real electrolyte HELD2 tests.
- [ ] Scenario artifacts retain discovery, Stage III, postsolve, and residual diagnostics.
- [ ] M5 regression blockers are created or referenced for fitted-model failures.

## Blocked by

- #348

## Proof Oracle

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and scenario" -q
```
