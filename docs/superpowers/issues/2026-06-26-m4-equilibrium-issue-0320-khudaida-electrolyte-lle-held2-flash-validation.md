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
readiness: "ready"
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
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
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

- [x] The retained Perdomo 2025 HELD2.0 Table 4 row inputs, species order, units, and phase labels are recorded before model comparison.
- [x] The validation uses `analyses/paper_validation/2025_figiel/parameters` directly and proves autodiff electrolyte derivatives, empirical permittivity, and Born SSM+DS options are active.
- [x] The accepted Perdomo/Figiel boundary row has retained source data, retained model data, retained residual statistics, and explicit route diagnostics.
- [x] The accepted electrolyte boundary row reports positive phase volumes, neutral transfer residuals, mean-ionic transfer residuals, pressure consistency, exact reduced Hessian availability, and finite reduced-domain lift/back-lift diagnostics.
- [x] The accepted model row is generated through the shared native `NlpProblem`/Ipopt phase NLP with no residual-only production bypass.
- [x] Accepted route diagnostics expose exact objective gradients, exact constraint Jacobians, exact Lagrangian Hessian support, the reduced electroneutral variable model, Ipopt status, seed name, and retained sparse Jacobian/Hessian probe values.
- [x] Electrolyte coordinates prove a reduced electroneutral lift/back-lift into true species amounts; hidden charge clipping is not used.
- [x] Charged transfer is certified by projected electrochemical or modified mean-ionic potential residuals; raw single-ion chemical-potential equality is not counted as completion evidence.
- [x] Born SSM+DS active phase blocks have exact-Hessian evidence before the Perdomo/Figiel boundary row is accepted.
- [x] HELD2 Stage III refinement remains retained as collapsed single-phase evidence and is not counted as accepted two-phase flash evidence.
- [x] The HELD2 pytest proof collects and runs real electrolyte HELD2 tests; zero selected tests fails the gate.
- [x] Public capability language remains narrowed to the focused validation binding; no broader electrolyte HELD2 production claim is made.
- [x] #191 remains open and blocked until #320 is merged and the dependency sync runs.

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

## Implementation Evidence

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

Accepted reduced-electroneutral boundary route evidence:

| Check | Result |
| --- | ---: |
| Native binding | `_native_electrolyte_bubble_t_route_result` |
| Route problem | `electrolyte_bubble_t_eos` |
| Route status | `accepted` |
| Ipopt backend status | `success` / `solve_succeeded` |
| Ipopt iterations | `6` |
| Seed | `canonical_phase_density_root` |
| Variable model | `reduced_electroneutral_logit_amount_volume_temperature` |
| Hessian path | exact, `cppad_phase_temperature_reduced_residual_constraints` |
| Residual derivative path | `cppad_phase_temperature_reduced_residual_constraints` |
| Objective | `0.0` |
| Temperature | `351.90223321057 K` |
| Liquid composition | `[0.29880119520, 0.61277245109, 0.04421317685, 0.04421317685]` |
| Vapor composition | `[0.59580640799, 0.32808099777, 0.03805629712, 0.03805629712]` |
| Liquid volume | `2.39444114281e-05` |
| Vapor volume | `2.72238721719e-02` |
| Vapor charge residual | `0.0` within `1e-12` |
| Public exposure | focused validation binding only; not production-exposed |

Retained projected residuals at the accepted state:

| Residual | Value |
| --- | ---: |
| scaled liquid pressure | `3.19072194057e-09` |
| scaled vapor pressure | `-4.30848711425e-13` |
| methanol reduced transfer | `-1.33e-14` |
| water reduced transfer | `4.44e-15` |
| LiCl mean-ionic transfer | `1.42e-14` |

The accepted route is an equality-constrained reduced residual NLP. Solver
variables are `log(T)`, `log(V_liquid)`, `log(V_vapor)`, and reduced
electroneutral composition logits. The physical lift/back-lift fixes the
liquid composition, reconstructs the vapor composition from neutral species and
a LiCl electroneutral group, and evaluates the public package EOS phase blocks
with active Figiel association, empirical permittivity, and Born SSM+DS.

The retained `_native_electrolyte_bubble_t_reduced_nlp_probe` evidence exposes
the shared `NlpProblem` exact-Hessian substrate directly: `variable_count=5`,
finite sparse Jacobian values, finite sparse Hessian values, and constraints
matching the independently recomputed projected residual vector within
`1e-9`.

## Scope Boundaries

- Perdomo 2025 reports HELD2.0 numerical results with the SAFT-gamma Mie GC
  electrolyte EOS. This #320 validation intentionally uses the retained local
  Figiel 2025 ePC-SAFT fugacity source, so the exact numeric temperature and
  vapor split are package-route validation evidence, not a SAFT-gamma Mie
  reproduction claim.
- Perdomo Table 4 is a bubble-temperature phase-boundary row. The accepted
  #320 evidence is therefore the fixed-pressure boundary route, not a finite
  positive-phase TP flash row.
- The retained Stage III projected-residual flash test still reaches residual
  feasibility but collapses to one phase under the noncollapsed postsolve gate.
  That result remains diagnostic evidence only and is not counted as the
  accepted #320 row.
- Khudaida artifact generation still completes, but the checker reports
  `model_reproduction_complete=False` with `model_blockers=12`. That remains
  outside the revised #320 Perdomo/Figiel algorithm gate and must not be used
  to claim full Khudaida electrolyte HELD2 validation.

## Implemented During Resolution

- Electrolyte Stage III completion requires the route postsolve result to be
  accepted, not only Ipopt `success` / `solve_succeeded`. This prevents
  diagnostic-only success from being counted as accepted electrolyte evidence.
- Electrolyte pressure consistency uses pressure-unit scaling
  `max(abs(P) * residual_tolerance, residual_tolerance)`, matching the neutral
  two-phase route tolerance contract. This keeps pressure residuals in Pa from
  being compared to reduced transfer residual tolerances.
- Added active-association exact derivative support for fixed-pressure
  temperature routes by differentiating the implicit association response with
  respect to temperature, density, and composition instead of dropping solvent
  association from the validation route.
- Replaced the positive-log least-squares boundary route with a true reduced
  electroneutral residual-constraint `NlpProblem` for electrolyte
  bubble-temperature validation.
- Added a narrow native reduced-NLP probe for retained diagnostics of the
  solver variables, physical lift/back-lift, sparse Jacobian, sparse Hessian,
  and projected residual vector.

## Non-goals

- No reactive electrolyte LLE route.
- No parameter regression target.
- No application-specific downstream metrics.
- No release claim.

## Proof Oracle

```powershell
uv run --no-sync python scripts\dev\build_epcsaft.py --build-only --parallel 4
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and flash" -q
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Retained local proof from 2026-06-27:

- Build: completed, `epcsaft_equilibrium._native_core` linked and imported.
- Focused pytest: `2 passed, 199 deselected`.
- Khudaida checker: `artifact_complete=True model_reproduction_complete=False blockers=0 model_blockers=12`.
- Khudaida analysis: `[done] 2026 Khudaida analysis complete.`
- Registry contracts: `28 passed`.
- Docs: Sphinx build succeeded.

The pytest proof must report the exact collected scenario tests when the
selector changes; zero selected tests fails the issue gate. The Khudaida
commands are retained as compatibility checks only; their incomplete model
reproduction status is not part of the revised #320 Perdomo/Figiel acceptance.

## GitHub Body Text

This issue reopens the #191 completion boundary by requiring source-backed
Perdomo HELD2.0 electrolyte boundary validation through the package route using
the latest retained Figiel 2025 ePC-SAFT parameter snapshot. The accepted row is
Perdomo Table 4 as a bubble-temperature boundary problem, solved through the
shared native `NlpProblem`/Ipopt exact-Hessian path in reduced electroneutral
coordinates. #314 remains representative route-admission evidence only; #191
must not be marked ready until the #320 PR is merged and dependency readiness
sync has run.
