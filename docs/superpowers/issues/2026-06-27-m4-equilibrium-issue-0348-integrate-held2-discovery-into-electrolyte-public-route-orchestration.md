---
issue: 348
title: "M4: integrate HELD2 discovery into electrolyte public route orchestration"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/348
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

# M4: integrate HELD2 discovery into electrolyte public route orchestration

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/348
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task

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

- [x] Public route results include Stage I/II discovery provenance.
- [x] Stage III consumes Stage II replay payloads.
- [x] Postsolve certification is retained with charge, pressure, transfer, amount, and domain evidence.
- [x] Private-native-only diagnostics cannot satisfy public-route proof.

## Acceptance Evidence

- Public route: `Equilibrium(..., route="electrolyte_lle")` returns accepted diagnostics for the electrolyte LLE route with `held2_phase_discovery`, `electrolyte_stage_iii_refinement`, and `postsolve_certification` retained in the public result.
- Stage II replay: Stage III seed provenance records `stage_ii_replay_ready: true`, source `stage_ii_dual_loop_selected_candidates`, seed `held_stage_ii_dual_loop_candidate_pair`, replay fractions `[0.08980929801532778, 0.9101907019846722]`, and candidate ranks `[1, 4]`.
- Stage III receipt: Ipopt returns `acceptable_point` / `solved_to_acceptable_level`; the route admits it only for `electrolyte_stage_iii_reduced_variable_refinement` after scaled constraint, stationarity, and complementarity norms are below the chemical-potential tolerance.
- Postsolve certification: charge residual `0.0`, pressure consistency norm `3.827153705060482e-09`, max neutral transfer residual `1.0530152042997898e-05`, and mean-ionic transfer residual `2.1991608690541398e-05` are retained under the public route.
- Public proof gate: `check_electrolyte_public_admission.py --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete` returns `complete=True` with no blockers.

## Closed blockers

- #347

## Proof Oracle

```bash
uv run --no-sync python scripts/validation/check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests -k "electrolyte and held2 and public and route" -q
```
