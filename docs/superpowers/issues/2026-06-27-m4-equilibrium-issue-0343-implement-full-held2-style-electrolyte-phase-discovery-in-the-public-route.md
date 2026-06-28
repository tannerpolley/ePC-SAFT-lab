---
issue: 343
title: "M4: implement full HELD2-style electrolyte phase discovery in the public route"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/343"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "blocked_by_344_345_346_347_348_349_350"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md"
source_plan: "docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md"
afk_hitl: "HITL"
branch: codex/held2-phase-discovery-issue-slices
last_synced: "2026-06-27"
---

# M4: implement full HELD2-style electrolyte phase discovery in the public route

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/343
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**Classification:** HITL
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
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

- [ ] #344 defines HELD2 public-route doctrine and validation matrix.
- [ ] #345 implements continuous reduced-electroneutral TPD minimization.
- [ ] #346 adds the HELD2 Stage I electrolyte stability certificate.
- [ ] #347 implements HELD2 Stage II dual/cutting-plane discovery.
- [ ] #348 integrates HELD2 discovery into the public route before Stage III.
- [ ] #349 adds the public-route scenario validation ladder.
- [ ] #350 admits registry/docs capability evidence after full validation.
- [ ] #191 remains open until #343, #350, and #320 close with retained evidence.

## Blocked by

- #344
- #345
- #346
- #347
- #348
- #349
- #350

## Non-goals

- No M5 parameter regression.
- No Khudaida fitted-model claim without #338 or equivalent M5 evidence.
- No reactive electrolyte, CE/CPE, or release claim.

## Proof Oracle

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2" -q
uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
```
