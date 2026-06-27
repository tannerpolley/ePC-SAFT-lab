---
issue: 320
title: "M4: make Khudaida electrolyte LLE figure and HELD2 flash validation pass"
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
branch: codex/issue-0320-khudaida-electrolyte-lle-held2-flash-validation
last_synced: "2026-06-27"
---

# M4: make Khudaida electrolyte LLE figure and HELD2 flash validation pass

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/320
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
**Goal Command:** /goal Resolve issue 320 by making the Khudaida full-figure electrolyte LLE model-fit checker and HELD2 flash scenario gate pass.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation-plan.md#outcome-proof
**Intent:** Replace the premature #191 closeout boundary with a source-backed model-reproduction gate that proves electrolyte LLE behavior across the Khudaida figure set and exercises HELD2 flashing beyond one representative feed.
**Target Output:** The Khudaida checker reports complete artifacts, complete model reproduction, zero blockers, every modeled figure or panel score at least `8.0`, and accepted model rows generated through the shared native `NlpProblem`/Ipopt exact-Hessian route path.
**Owner:** `packages/epcsaft-equilibrium` owns solver behavior; `analyses/paper_validation/2026_khudaida` owns retained source/model plot artifacts.
**Interface:** Public `Equilibrium(..., route="electrolyte_lle")`, native `NlpProblem` route metadata, `VariableTransform` lift/back-lift records, retained paper-validation scripts, figure fit-statistics CSVs, and pytest scenario contracts.
**Cutover:** #191 cannot close on the #314 representative admission checker alone; it closes only after #320 passes and updates parent evidence.
**Replaced Path:** Single-feed public admission as a proxy for electrolyte LLE model validity.
**Acceptance Proof:** The proof oracle commands pass from the repo root, accepted route diagnostics prove the exact-Hessian path, and #191 names #320 as closed provenance after merge.
**Stop Criteria:** Stop if source inputs, parameter provenance, species basis, charge balance, solver seeds, or plotted data cannot be verified against retained inputs before changing solver logic; also stop if the route bypasses `NlpProblem`/Ipopt, hides charge imbalance by clipping, compares raw single-ion chemical potentials, or lacks Born SSM+DS active-block exact-Hessian evidence.
**Avoid:** Do not count collapsed near-feed splits, source-only figures, synthetic payloads, downstream metrics, or broad electrolyte/release claims as completion evidence.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Make the full Khudaida 2026 electrolyte LLE figure-reproduction checker pass
and add a retained HELD2 flash scenario gate that proves electrolyte flashing
across source-backed, neutral-limit, stable, unstable, boundary, phase-order,
and reduced-coordinate scenarios. Accepted electrolyte rows must come from the
shared pressure-transformed Helmholtz `NlpProblem`/Ipopt production path with
route-owned transforms/scaling, exact objective gradients, exact constraint
Jacobians, exact Lagrangian Hessians, Born SSM+DS active-block exactness, and
postsolve certification.

## Acceptance Criteria

- [ ] The Khudaida checker returns `artifact_complete=true`, `model_reproduction_complete=true`, and zero artifact/model blockers.
- [ ] Every modeled Khudaida figure or panel has retained source data, retained model data, retained fit statistics, and plot score `>= 8.0`.
- [ ] Figures without model-comparable equilibrium data are explicitly recorded by the checker and cannot hide failed model rows.
- [ ] Accepted electrolyte flashes report noncollapsed phase distance, positive phase amounts, per-phase charge residuals, neutral transfer residuals, mean-ionic transfer residuals, pressure consistency, exact reduced Hessian availability, and finite domain margins.
- [ ] Every accepted model row is generated through the shared native `NlpProblem`/Ipopt phase NLP with no residual-only or equation-only production bypass.
- [ ] Accepted route diagnostics expose fixed sparse Jacobian/Hessian receipts, exact objective gradients, exact constraint Jacobians, exact Lagrangian Hessians, `profile_exact_hessian_gate`, Ipopt user scaling, Ipopt option profile, linear solver, and bound-barrier diagnostics.
- [ ] Electrolyte coordinates prove per-phase reduced electroneutral lift/back-lift into true species amounts; hidden charge clipping fails the gate.
- [ ] Charged transfer is certified by projected electrochemical or modified mean-ionic potential/fugacity residuals; raw single-ion chemical-potential equality is rejected as completion evidence.
- [ ] Born SSM+DS active phase blocks have exact-Hessian evidence before Khudaida model rows are accepted.
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
- The Khudaida 2026 source data supply experimental mixed-solvent NaCl LLE
  tie-lines, pure-component parameters, dielectric constants, binary
  interaction parameters, and AAD references; the retained Khudaida checker
  currently states that public `electrolyte_lle` model rows do not yet reproduce
  the salted tie-lines.

## Blocked by

- None

## Non-goals

- No reactive electrolyte LLE route.
- No parameter regression target.
- No application-specific downstream metrics.
- No release claim.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --json --require-complete --require-model-pass
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and flash"
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

The pytest proof must report the exact collected scenario tests when the selector
changes; zero selected tests fails the issue gate.

## GitHub Body Text

This issue reopens the #191 completion boundary by requiring full Khudaida
source-data model reproduction and multi-scenario HELD2 flash validation. #314
remains representative route-admission evidence, but it is not sufficient
evidence that electrolyte LLE model behavior matches the retained literature
figures.
