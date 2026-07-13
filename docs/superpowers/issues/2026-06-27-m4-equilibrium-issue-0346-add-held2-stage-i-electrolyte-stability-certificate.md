---
issue: 346
title: "M4: add HELD2 Stage I electrolyte stability certificate"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/346
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
last_synced: "2026-07-12"
---

**Source-faithful historical classification (2026-07-12):** Preserve this closed issue as component history only. Perdomo HELD2 requires modified-mole coordinates and direct total-free-energy Stage III; Ascani counterion-pair and mean-ionic work is a separate algorithm family. Existing receipts do not establish source-faithful Perdomo HELD2 parity or public `electrolyte_lle` admission, which remains closed pending #459.

**Mirror Retention:** Keep

# M4: add HELD2 Stage I electrolyte stability certificate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/346
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md#outcome-proof
**Intent:** Convert continuous reduced-coordinate TPD output into a HELD2 Stage I stability certificate.
**Target Output:** Stable, unstable, incomplete, and suspect-start classifications with retained residual and bound evidence.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Slice #345 minimizer output, native diagnostics, package tests, and `check_electrolyte_held2_stage_i.py`.
**Cutover:** Feed Stage II only with certified Stage I payloads.
**Replaced Path:** Single-start or deterministic-screen-only stability claims.
**Acceptance Proof:** Stage I checker and focused tests pass.
**Stop Criteria:** Stop if no-negative-TPD, negative-TPD, or incomplete-start states cannot be distinguished with retained evidence.
**Avoid:** Do not infer phase-set completeness or public-route admission from Stage I alone.

## Acceptance Criteria

- [ ] Stable cases retain a complete no-negative-TPD certificate.
- [ ] Unstable cases retain negative-TPD trial phases for Stage II.
- [ ] Incomplete minimization fails loudly with diagnostics.
- [ ] Stage I certificates are replayable from retained payloads.

## Closed prerequisite

- #345

## Proof Oracle

```bash
uv run --no-sync python scripts/validation/check_electrolyte_held2_stage_i.py --json --require-continuous-tpd --require-complete
uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests -k "electrolyte and held2 and stage_i" -q
```
