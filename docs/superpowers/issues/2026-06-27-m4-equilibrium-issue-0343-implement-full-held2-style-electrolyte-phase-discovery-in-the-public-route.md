---
issue: 343
title: "M4: implement full HELD2-style electrolyte phase discovery in the public route"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/343
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
afk_hitl: HITL
branch: codex/issue-0343-held2-parent-proof-sync
last_synced: "2026-06-29"
---

# M4: implement full HELD2-style electrolyte phase discovery in the public route

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/343
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Complete full HELD2-style electrolyte phase discovery in the public route after child slices close.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** Child slices may run only after their blockers close.
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md#outcome-proof
**Intent:** Parent the full public-route HELD2 electrolyte phase-discovery adoption sequence.
**Target Output:** The public `electrolyte_lle` route can discover candidate phase sets through HELD2-style reduced-electroneutral Stage I/II discovery, refine them through Stage III Ipopt, certify them postsolve, and expose only evidence-backed capability claims.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** Native discovery diagnostics, `NlpProblem`/Ipopt Stage III refinement, public `Equilibrium(..., route="electrolyte_lle")`, validation scripts, registries, and capability docs.
**Cutover:** Keep #314 and #320 as retained partial evidence, but require #343 child closure before #191 can claim full HELD2-style public-route phase discovery.
**Replaced Path:** Representative public admission, retained diagnostics, deterministic TPD screening, or boundary-only residual solves treated as production phase discovery.
**Acceptance Proof:** Child issues #344 through #350 close with retained proof and the final validation ladder passes.
**Stop Criteria:** Stop if a child slice requires M5 parameter regression, reactive electrolyte LLE, CE/CPE coupling, hidden charge clipping, raw single-ion equality, fallback solver flags, or capability claims broader than retained evidence.
**Avoid:** Do not close #191 through tracker metadata alone, and do not use #314 or #320 as substitutes for full discovery orchestration.

## What To Build

Implement and validate full HELD2-style electrolyte phase discovery as a public
route capability through the seven child issue slices.

## Acceptance Criteria

- [x] #344 defines HELD2 public-route doctrine and validation matrix.
- [x] #345 implements continuous reduced-electroneutral TPD minimization.
- [x] #346 adds the HELD2 Stage I electrolyte stability certificate.
- [x] #347 implements HELD2 Stage II dual/cutting-plane discovery.
- [x] #348 integrates HELD2 discovery into the public route before Stage III.
- [x] #349 adds the public-route scenario validation ladder.
- [x] #350 admits registry/docs capability evidence after full validation.
- [x] #191 remains open until this closeout PR closes #343; #320 and #350 already close with retained evidence.

## Blocked by

- None. #344, #345, #346, #347, #348, #349, #350, and #320 are closed.

## Child Evidence

- #344 closed with the public-route doctrine and validation matrix.
- #345 closed with the continuous reduced-electroneutral TPD substrate.
- #346 closed with the Stage I stability certificate.
- #347 closed with Stage II dual/cutting-plane discovery and replay evidence.
- #348 closed with public `electrolyte_lle` orchestration through Stage I/II discovery, Stage III replay consumption, and postsolve certification.
- #349 closed with the seven-scenario public-route validation ladder.
- #350 closed with the registry, docs, and capability-admission evidence for the retained public `electrolyte_lle` scope while keeping generic electrolyte, reactive, CE/CPE, regression, and release claims closed.
- #320 closed by PR #341 on 2026-06-29 with the retained Perdomo/Figiel HELD2 flash validation and exact-Hessian public-route proof.

## Closeout Proof

Retained on branch `codex/issue-0343-held2-parent-proof-sync` after the stale
package diagnostic expectation was aligned to the implemented exact-Hessian
public route:

- `uv run --no-sync python scripts/validation/check_electrolyte_held2_public_route_scenarios.py --json --require-complete`
  - `complete=True`, blockers empty, 7 accepted scenarios.
  - Public-route solve scenarios: unstable feed, boundary feed, phase-label permutation.
  - Reduced-basis prerequisite scenarios: common-ion electrolyte and mixed-salt asymmetric electrolyte.
  - Retained unstable-feed route Hessian: `exact`.
- `uv run --no-sync python scripts/validation/check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete`
  - `complete=True`, blockers empty.
  - Public route: `electrolyte_lle`; selector family: `electrolyte_lle`; problem kind: `electrolyte_lle`.
  - Postsolve accepted: `True`; `exact_hessian_available=True`; `hessian_approximation=exact`; `route_hessian_approximation=exact`.
  - Charge residual `0 <= 1e-08`; neutral transfer residual `5.56798114281776e-08 <= 1e-04`; mean-ionic transfer residual `4.10447853482765e-08 <= 1e-04`.
- `uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests -k "electrolyte and held2" -q`
  - `17 passed, 206 deselected`.
- `uv run --no-sync python -m pytest tests/native/contracts/test_equilibrium_benchmark_registry.py tests/native/contracts/test_generalized_equilibrium_registry.py -q`
  - `28 passed`.

This closes #343 through the proof/sync PR only. #191 remains open until #343 is
actually closed and then re-evaluated for final M4 electrolyte closeout.

## Non-goals

- No M5 parameter regression.
- No Khudaida fitted-model claim without #338 or equivalent M5 evidence.
- No reactive electrolyte, CE/CPE, or release claim.

## Proof Oracle

```bash
uv run --no-sync python scripts/validation/check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python scripts/validation/check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests -k "electrolyte and held2" -q
uv run --no-sync python -m pytest tests/native/contracts/test_equilibrium_benchmark_registry.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
```
