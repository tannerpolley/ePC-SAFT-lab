---
issue: 348
title: "M4: integrate HELD2 discovery into electrolyte public route orchestration"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/348"
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
branch: codex/issue-0348-held2-discovery-electrolyte-public-route-orchestration
last_synced: "2026-06-28"
---

# M4: integrate HELD2 discovery into electrolyte public route orchestration

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/348
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**Classification:** AFK after #347 closes
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

## Outcome Summary

**Intent:** Route public electrolyte LLE through HELD2 discovery, Stage III refinement, and postsolve certification.
**Target Output:** Public `Equilibrium(..., route="electrolyte_lle")` results retain Stage I/II discovery provenance, Stage III Ipopt receipts, and postsolve certification.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Public route orchestration, native discovery payloads, Stage III Ipopt route, postsolve certification, and `check_electrolyte_public_admission.py`.
**Cutover:** Public route uses Stage II candidates before Stage III when electrolyte discovery is required.
**Replaced Path:** Private-native-only diagnostics or hand-picked candidate sets satisfying public-route acceptance.
**Acceptance Proof:** Public admission checker and focused route tests pass.
**Stop Criteria:** Stop on `NlpProblem`/Ipopt bypass, missing exact-Hessian receipts, missing postsolve certification, or unsupported route broadening.
**Avoid:** Do not claim reactive, CE/CPE, regression, or unfitted Khudaida support.

## Acceptance Criteria

- [ ] Public route results include Stage I/II discovery provenance.
- [ ] Stage III consumes Stage II replay payloads.
- [ ] Postsolve certification is retained with charge, pressure, transfer, amount, and domain evidence.
- [ ] Private-native-only diagnostics cannot satisfy public-route proof.

## Blocked by

- #347

## Proof Oracle

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and public and route" -q
```
