---
issue: 320
title: "M4: validate Perdomo HELD2 electrolyte flash with Figiel ePC-SAFT parameters"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/320"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0320-khudaida-held2-validation
last_synced: "2026-06-27"
---

# M4: validate Perdomo HELD2 electrolyte flash with Figiel ePC-SAFT parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/320
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
**Goal Command:** /goal Resolve issue 320 by validating the Perdomo 2025 HELD2.0 electrolyte flash algorithm through the Figiel 2025 ePC-SAFT parameter route.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation-plan.md#outcome-proof
**Intent:** Replace the premature #191 closeout boundary with a source-backed HELD2.0 algorithm gate that uses Perdomo 2025 equations/results as the algorithm reference and the latest retained Figiel 2025 ePC-SAFT parameter snapshot as the package fugacity source.
**Target Output:** Accepted electrolyte flash rows are generated through the shared native `NlpProblem`/Ipopt exact-Hessian route path and retain per-row evidence for reduced electroneutral coordinates, projected neutral/mean-ionic residuals, Born SSM+DS active-block exactness, and noncollapsed phase certification.
**Owner:** `packages/epcsaft-equilibrium` owns solver behavior; `analyses/paper_validation/2025_figiel/parameters` owns the retained ePC-SAFT parameter snapshot used by this check.
**Interface:** Native HELD2 Stage III refinement diagnostics, public `Equilibrium(..., route="electrolyte_lle")` admission once the noncollapsed gate passes, `VariableTransform` lift/back-lift records, and pytest scenario contracts.
**Cutover:** #191 cannot close on the #314 representative admission checker alone; it closes only after #320 has accepted noncollapsed HELD2 evidence and updates parent evidence.
**Replaced Path:** Khudaida figure reproduction as the sole #320 acceptance source.
**Acceptance Proof:** The proof oracle commands pass from the repo root, accepted route diagnostics prove the exact-Hessian path, and #191 names #320 as closed provenance after merge.
**Stop Criteria:** Stop if source inputs, parameter provenance, species basis, charge balance, solver seeds, or retained data cannot be verified against Perdomo/Figiel inputs before changing solver logic; also stop if the route bypasses `NlpProblem`/Ipopt, hides charge imbalance by clipping, compares raw single-ion chemical potentials, or lacks Born SSM+DS active-block exact-Hessian evidence.
**Avoid:** Do not count collapsed near-feed splits, source-only tables, synthetic payloads, downstream metrics, or broad electrolyte/release claims as completion evidence.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Validate the Perdomo 2025 HELD2.0 electrolyte flash algorithm against retained
Perdomo rows while using the latest local Figiel 2025 ePC-SAFT parameters as
the package fugacity source. Accepted electrolyte rows must come from the
shared pressure-transformed Helmholtz `NlpProblem`/Ipopt production path with
route-owned transforms/scaling, exact objective gradients, exact constraint
Jacobians, exact Lagrangian Hessians, Born SSM+DS active-block exactness, and
postsolve certification.

## Acceptance Criteria

- [ ] The retained Perdomo 2025 HELD2.0 row inputs, species order, units, and phase labels are recorded before model comparison.
- [ ] The validation uses `analyses/paper_validation/2025_figiel/parameters` directly and proves autodiff electrolyte derivatives, empirical permittivity, and Born SSM+DS options are active.
- [ ] Perdomo/Figiel model rows that are counted as accepted have retained source data, retained model data, retained residual statistics, and explicit route diagnostics.
- [ ] Accepted electrolyte flashes report noncollapsed phase distance, positive phase amounts, per-phase charge residuals, neutral transfer residuals, mean-ionic transfer residuals, pressure consistency, exact reduced Hessian availability, and finite domain margins.
- [ ] Every accepted model row is generated through the shared native `NlpProblem`/Ipopt phase NLP with no residual-only or equation-only production bypass.
- [ ] Accepted route diagnostics expose fixed sparse Jacobian/Hessian receipts, exact objective gradients, exact constraint Jacobians, exact Lagrangian Hessians, `profile_exact_hessian_gate`, Ipopt user scaling, Ipopt option profile, linear solver, and bound-barrier diagnostics.
- [ ] Electrolyte coordinates prove per-phase reduced electroneutral lift/back-lift into true species amounts; hidden charge clipping fails the gate.
- [ ] Charged transfer is certified by projected electrochemical or modified mean-ionic potential/fugacity residuals; raw single-ion chemical-potential equality is rejected as completion evidence.
- [ ] Born SSM+DS active phase blocks have exact-Hessian evidence before Perdomo/Figiel model rows are accepted.
- [ ] HELD2 flash tests cover neutral-limit parity with the HELD 1.0-style base, source-backed electrolyte LLE, common-ion or mixed-salt reduced coordinates, stable feeds, unstable feeds, boundary feeds, and phase-label permutations.
- [ ] HELD2 Stage III refinement consumes the HELD2 candidate set and reports both Ipopt `success` and `solve_succeeded` when Stage III evidence is counted.
- [ ] The HELD2 pytest proof collects and runs at least one electrolyte HELD2 flash scenario test; zero selected tests fails the gate.
- [ ] Public capability and docs language is narrowed to the behavior proven by the full checker.
- [ ] #191 remains open and blocked by #320 until all #320 proof commands pass.

## Source Audit Receipts

- GFPE doctrine requires source-backed validation, the common `NlpProblem`
  route substrate, exact first derivatives, exact Lagrangian Hessians,
  route-owned bounds/scaling/transforms, Ipopt barrier constraints, and staged
  HELD evidence. Electrolyte routes add per-phase charge balance and projected
  electrochemical potentials in a charge-neutral reduced basis.
- The M4 stage plan requires exact objective gradients, exact constraint
  Jacobians, exact Lagrangian Hessians, sparse derivative receipts, user
  scaling, exact-Hessian production profiles, and no `NlpProblem` bypass.
- The HELD2 source paper requires reduced electroneutral coordinates,
  modified electrochemical potentials, and HELD phase discovery under
  electroneutrality.
- The Ascani 2022 electrolyte source requires electrolyte equilibrium through
  transformed variables and mean-ionic conditions, not raw single-ion equality.
- The Perdomo 2025 source paper supplies the HELD2.0 reduced-coordinate,
  electroneutral flash algorithm and sample electrolyte flash results. The
  reported numerical results use SAFT-gamma Mie GC electrolyte fugacities.
- The Figiel 2025 local parameter snapshot supplies the ePC-SAFT fugacity source
  for this package validation and enables autodiff electrolyte derivatives,
  empirical permittivity, and Born SSM+DS options.

## Blocked by

- Perdomo 2025 reports HELD2.0 results with the SAFT-gamma Mie GC electrolyte
  EOS. The requested package check intentionally uses the latest local Figiel
  2025 ePC-SAFT parameter snapshot instead. With that fugacity source, the
  Stage III projected-residual problem reaches exact-Hessian residual
  feasibility but collapses to a single phase, so the Perdomo two-phase result
  cannot be claimed as reproduced by #320.
- Perdomo Table 4 is a bubble-temperature phase-boundary result with trace
  vapor ions, not a finite-positive-phase TP flash row. The current electrolyte
  public route surface exposes `electrolyte_lle`, but it does not expose an
  electrolyte bubble/dew boundary route that can validate an incipient vapor
  boundary without forcing a finite vapor phase amount.
- Charge-neutral trace-ion starts are now evaluated by electrolyte TPD
  discovery. Under the Figiel 2025 ePC-SAFT fugacity source, those trace-ion
  vapor-like starts have positive projected TPD values for the retained
  Perdomo Table 4 row, so they are not selected as the unstable phase set.

## Blocker Evidence

The focused package test uses:

- HELD2.0 algorithm source: `docs/papers/md/Equilibrium/Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems.md`.
- Perdomo Table 4 row: methanol + water + LiCl, `P=101.325 kPa`, LiCl `4.0 molal`,
  salt-free methanol mole fraction `0.300`, `T=351.25 K`, table species order
  `(Li+, Cl-, methanol, water)`.
- Figiel parameter source: `analyses/paper_validation/2025_figiel/parameters`,
  including `user_options.json` with autodiff electrolyte derivatives,
  empirical permittivity, and Born solvation-shell plus dielectric-saturation
  enabled.
- Package species order: `(Methanol, H2O, Li+, Cl-)`.
- Normalized Perdomo liquid feed: `[0.29880119520, 0.61277245109,
  0.04421317685, 0.04421317685]`.

Observed route evidence:

| Check | Result |
| --- | ---: |
| Ipopt backend status | `success` / `solve_succeeded` |
| Route problem | `electrolyte_stage_iii_projected_residual_refinement` |
| Hessian path | exact, `cppad_phase_system_projected_electrolyte...` |
| Reduced residual infinity norm | `1.291596e-9` |
| Pressure consistency norm | `2.507e-3 Pa` |
| Charge-balance norm | `4.765e-22` |
| Phase distance | `2.353e-9` |
| Postsolve status | rejected: `phase_distance` |
| Electrolyte TPD candidates | `30` total, including `24` trace-ion candidates |
| Trace-ion TPD range | `1.257001e-1` to `1.132025` |

This proves the package route can drive the Perdomo/Figiel HELD2 residual
system through the public native `NlpProblem`/Ipopt exact-Hessian path, but the
computed phases are indistinguishable under the existing noncollapsed-phase
gate. Do not close #320 or #191 as two-phase HELD2 validation on this evidence.

## Implemented During Blocker Investigation

- Electrolyte Stage III completion now requires the route postsolve result to
  be accepted, not only Ipopt `success` / `solve_succeeded`. This prevents
  diagnostic-only success from being counted as accepted electrolyte evidence.
- Electrolyte pressure consistency now uses pressure-unit scaling
  `max(abs(P) * residual_tolerance, residual_tolerance)`, matching the neutral
  two-phase route tolerance contract. This keeps pressure residuals in Pa from
  being compared to reduced transfer residual tolerances.
- The retained representative `electrolyte_lle` public admission gate still
  passes after the stricter route-accepted status gate. Current evidence:
  public admission `accepted`, postsolve certification `complete`, Stage III
  `complete`, pressure residual `4.6129005e-3 Pa`, pressure tolerance `10 Pa`,
  phase distance `1.7075547e-8`, and route accepted `true`.

## Non-goals

- No reactive electrolyte LLE route.
- No parameter regression target.
- No application-specific downstream metrics.
- No release claim.

## Proof Oracle

```powershell
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and flash"
uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

The pytest proof must report the exact collected scenario tests when the selector
changes; zero selected tests fails the issue gate.

## GitHub Body Text

This issue reopens the #191 completion boundary by requiring source-backed
Perdomo HELD2.0 electrolyte flash validation through the package route using
the latest retained Figiel 2025 ePC-SAFT parameter snapshot. #314 remains
representative route-admission evidence, but it is not sufficient evidence that
the HELD2 electrolyte flash algorithm has accepted noncollapsed validation
rows.
