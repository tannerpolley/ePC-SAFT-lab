---
issue: 350
title: "M4: admit HELD2 public-route capability evidence after full validation"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/350
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
branch: codex/issue-0350-held2-public-route-capability-evidence-after-validation
last_synced: "2026-06-29"
---

# M4: admit HELD2 public-route capability evidence after full validation

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/350
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**AFK/HITL:** AFK
**Classification:** AFK after #349 closes
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

## Outcome Summary

**Intent:** Admit registry, docs, and #191 capability evidence only after the full HELD2 public-route validation ladder passes.
**Target Output:** Evidence-backed registry rows and capability docs that name exact scope and proof commands.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Capability payloads, registries, docs, #191 mirror, and validation commands.
**Cutover:** Move HELD2 public-route capability from planned to evidence-backed only for the proven families.
**Replaced Path:** Broad electrolyte claims based on representative route admission or private diagnostics.
**Acceptance Proof:** Registry tests and docs validation pass.
**Stop Criteria:** Stop if #349 has not passed, capability scope cannot be stated narrowly, or docs would imply unsupported electrolyte families.
**Avoid:** Do not close #191 unless #343 and #320 are closed with retained evidence.

## Acceptance Criteria

- [x] Registry rows name exact passed proof commands and route scope.
- [x] Capability docs distinguish representative admission, Perdomo/Figiel validation, and full HELD2 public-route phase discovery.
- [x] #191 retains blocker state until #343 and #320 close.
- [x] Unsupported electrolyte families remain closed in docs and registry evidence.

## Acceptance Evidence

- #349 is closed with scenario evidence: `check_electrolyte_held2_public_route_scenarios.py --json --require-complete` returns `complete=True`, no blockers, and 7 accepted scenarios covering stable, unstable, boundary, phase-label, neutral-limit, common-ion, and mixed-salt/asymmetric cases.
- Registry admission row now names the full public-route proof: `check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete`.
- Registry admission row now names the scenario ladder proof: `check_electrolyte_held2_public_route_scenarios.py --json --require-complete`.
- Registry contract row now names the #350 proof oracle: `uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q`.
- Capability docs state that #314 remains representative public-route admission, #348/#349 provide full HELD2-style public-route discovery and scenario validation for the retained `electrolyte_lle` scope, and #320 remains the Perdomo/Figiel validation blocker.
- Unsupported generic electrolyte, reactive, CE/CPE, regression, fitted-model, and release surfaces remain closed in registry/docs evidence.

## Closed blockers

- #349

## Proof Oracle

```powershell
uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
```
