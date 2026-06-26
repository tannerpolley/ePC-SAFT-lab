---
issue: 191
title: "M4: prove electrolyte GFPE and HELD2.0 validation gates"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/191"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "blocked_by_320"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates
last_synced: "2026-06-26"
---

# Prove electrolyte GFPE and HELD2.0 validation gates

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
Branch: codex/issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates
AFK/HITL: HITL

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/191
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
**Classification:** HITL
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Prove electrolyte GFPE and HELD2.0 validation gates after the neutral generalized phase-set path, associating prerequisite evidence, electrolyte source gate, reduced-basis/Born exactness gate, electrolyte TPD screening gate, HELD2 phase discovery, Stage III electrolyte refinement, postsolve certification, representative public route admission, full Khudaida figure-level model reproduction, and broader HELD2 flash scenario gates are each proven by retained evidence.

## Reopened Closeout Correction

#191 was reopened on 2026-06-26 because #314 proved representative public route
admission, not full electrolyte LLE model reproduction. The #314 checker used a
source-backed Khudaida explicit-ion feed and certified one public-route payload;
that evidence is valid but too narrow for final M4 electrolyte LLE closeout.

#320 is now the active #191 child blocker. It requires the full Khudaida
retained figure checker to pass with model reproduction enabled and adds a
broader HELD2 flash scenario gate covering neutral-limit parity, source-backed
electrolyte LLE, common-ion or mixed-salt reduced coordinates, stable feeds,
unstable feeds, boundary feeds, and phase-label permutations. It must also
prove accepted electrolyte rows use the shared native `NlpProblem`/Ipopt
exact-Hessian production path with route-owned transforms/scaling, exact
objective gradients, exact constraint Jacobians, exact Lagrangian Hessians,
Born SSM+DS active-block exactness, projected electrochemical or modified
mean-ionic residuals, and strict Stage III Ipopt success when Stage III evidence
is counted.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md#outcome-proof
**Intent:** Keep #191 as the parent acceptance gate for electrolyte GFPE and prevent final closeout until all child gates, including #320, pass with retained executable evidence.
**Target Output:** Maintainers see #191 open and blocked by #320 until full Khudaida figure-level model reproduction, broader HELD2 flash scenario validation, and shared `NlpProblem`/Ipopt exact-Hessian route receipts pass.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub issue dependencies, local issue mirrors, M4 docs, validation checkers, and native diagnostics consumed by issue-resolution workflows.
**Cutover:** Replace the #314-only closeout path with the #320 full reproduction and HELD2 scenario gate.
**Replaced Path:** Representative public route admission treated as final electrolyte LLE completion evidence.
**Acceptance Proof:** #191 closes only after #320 passes its proof oracle, accepted route diagnostics prove the exact-Hessian production path, and the parent mirror is updated with closed provenance.
**Stop Criteria:** Do not close #191 while #320 is open, while Khudaida model reproduction fails, while HELD2 flash scenario tests are absent, while accepted rows bypass `NlpProblem`/Ipopt, while Born SSM+DS active-block exact-Hessian evidence is absent, or while charged transfer is certified with raw single-ion chemical-potential equality.
**Avoid:** Do not count collapsed near-feed splits, synthetic payloads, source-only plots, downstream metrics, or broad release claims as completion evidence.

## Closed Prerequisites And Remaining Gates

- #189, #275, #286, #300, #302, and #306 are closed and remain only as historical dependency provenance.
- #306 closed the HELD2 counterion-pair phase-discovery gate in reduced electroneutral coordinates.
- #312 provides the retained Stage III reduced-variable refinement proof.
- #313 provides the retained postsolve certification proof.
- #314 provides representative public electrolyte route-admission proof for one
  certified source-backed payload. It is no longer treated as final #191
  closeout evidence.
- #320 is open and blocks #191 until full Khudaida model reproduction and
  broader HELD2 flash scenario tests pass.

## Child Issues

- [#269](2026-06-17-m4-equilibrium-issue-0269-add-electrolyte-gfpe-closed-admission-source-gate.md) closed the first #191 child gate. It proved the Khudaida source fixture, explicit-ion expansion, path-based paper-validation parameter-bundle execution, native electrolyte/charge diagnostics, and public route boundary state. It did not admit public electrolyte GFPE, electrolyte TPD, HELD2 phase discovery, or electrolyte postsolve certification.
- [#300](2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md) closed the reduced electroneutral variable and Born SSM/DS exactness readiness gate. It proved the exact charge-neutral NaCl amount lift, CppAD Born SSM/DS composition, fugacity, activity-parameter, `d_born`, and `f_solv` derivative receipts, and kept public electrolyte route admission closed.
- [#302](2026-06-24-m4-equilibrium-issue-0302-add-electrolyte-charge-neutral-tpd-gate.md) closed the native-backed charge-neutral electrolyte TPD screening gate. It proves three finite source-backed candidates, selected candidate count `2`, minimum TPD `-0.010922388988229025`, maximum charge residual `0.0`, readiness-only HELD2 status, and closed public electrolyte route state. It does not close HELD2 dual discovery, Stage III electrolyte refinement, postsolve electrolyte phase-set certification, or public route admission.
- [#306](2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md) closed the HELD2 counterion-pair phase-discovery child. It added native reduced-coordinate diagnostics with independent counterion-pair matrix rank evidence, charge-neutral candidates, mean-ionic residual bookkeeping, a Stage III handoff record, and closed public route state. It did not claim Stage III refinement, postsolve certification, or public electrolyte route admission.
- [#312](2026-06-25-m4-equilibrium-issue-0312-add-electrolyte-held2-stage-iii-reduced-variable-refinement-gate.md) adds the retained Stage III reduced-variable electrolyte refinement proof. It consumes the #306 candidate handoff, reports exact reduced residual derivative receipts, records strict Ipopt success and finite local phase compositions, and keeps postsolve certification plus public route admission pending.
- [#313](2026-06-25-m4-equilibrium-issue-0313-add-electrolyte-postsolve-phase-set-certification-gate.md) closes the postsolve certification child. It certifies explicit-ion material reconstruction, per-phase charge balance, neutral and mean-ionic transfer residuals, pressure consistency, phase amounts, and domain margins while keeping public route admission pending.
- [#314](2026-06-25-m4-equilibrium-issue-0314-admit-source-backed-public-electrolyte-gfpe-route.md) closed representative public electrolyte GFPE route admission. It consumes every prior electrolyte checker and admits only the source-backed Khudaida explicit-ion `electrolyte_lle` route, but it did not prove figure-level model reproduction or robust HELD2 flashing across the Khudaida data set.
- [#320](2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation.md) is the active final blocker. It requires all modeled Khudaida figures or panels to pass the retained checker with `normalized_plot_score >= 8.0`, requires the broader HELD2 flash scenario gate, and requires accepted electrolyte rows to prove the shared native `NlpProblem`/Ipopt exact-Hessian route path with Born SSM+DS active-block exactness and projected electrochemical or modified mean-ionic residuals.

## HELD2 Adoption Checkpoint Sequence

- Source and readiness checkpoints: #269, #300, and #302 remain prerequisite
  evidence for source fixtures, reduced electroneutral variables, Born SSM/DS
  derivatives, and charge-neutral TPD screening.
- #306 phase-discovery checkpoint: retained diagnostics are counterion-pair
  matrix rank, reduced-coordinate lift/back-lift residuals, finite TPD
  candidate metrics, pair-based mean-ionic residual bookkeeping, closed public
  routes, and a Stage III handoff record.
- #312 Stage III refinement checkpoint: consume the #306 candidate set and solve the
  local electrolyte reduced-variable phase-set equations with exact residual
  derivative receipts. The retained checker is
  `scripts/validation/check_electrolyte_stage_iii_refinement.py`.
- #313 postsolve checkpoint: certifies explicit-ion material reconstruction,
  per-phase charge balance, neutral transfer, mean-ionic transfer, pressure
  consistency, phase amounts, and domain margins through
  `scripts/validation/check_electrolyte_postsolve_certification.py`.
- #314 public admission checkpoint: consume all prior checkers and expose only
  the certified representative electrolyte route surface.
- #320 full reproduction checkpoint: make the full Khudaida figure checker pass
  with model reproduction required, then prove broader HELD2 flashing through
  retained scenario tests and exact-Hessian `NlpProblem`/Ipopt route receipts.

## Closeout Evidence Required

Do not close this umbrella on the #314 public-admission checker alone. Final
#191 closeout now requires the #320 proof oracle:

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --json --require-complete --require-model-pass
uv run --no-sync python scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and flash"
```

Expected retained result: Khudaida artifact and model reproduction complete,
zero artifact/model blockers, every modeled figure or panel score `>= 8.0`,
public route `electrolyte_lle`, certified phase diagnostics, noncollapsed phase
splits, exact reduced Hessian available, shared `NlpProblem`/Ipopt
exact-Hessian path, Born SSM+DS active-block exactness, reduced
electroneutral lift/back-lift, projected electrochemical or modified
mean-ionic residuals, and reactive/CE/CPE/regression/release claims closed.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/plans/2026-06-17-m4-equilibrium-issue-0191-electrolyte-gfpe-closed-admission-gate-plan.md`
- `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md`
- `docs/papers/md/Equilibrium/Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems.md`
- `docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md`
- `docs/papers/md/Equilibrium/Khudaida et al. - 2026 - Upgrading the Extraction of Ethanol and Isobutanol from an Aqueous Solution in the Presence of Sodiu.md`
- `analyses/paper_validation/2026_khudaida/README.md`
- `analyses/paper_validation/2026_khudaida/analysis.yaml`
- `analyses/paper_validation/2026_khudaida/docs/md/provenance_notes.md`
- `analyses/paper_validation/2026_khudaida/shared/source/figure_manifest.csv`
- `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`

## Acceptance Criteria

- [x] HELD2 counterion-pair phase discovery consumes #269, #300, and #302 evidence and reports full-rank reduced-coordinate diagnostics.
- [x] #312 Stage III electrolyte refinement consumes the HELD2 candidate set and solves in reduced electroneutral variables.
- [x] #313 postsolve electrolyte certification reports material, charge, pressure, neutral transfer, mean-ionic transfer, and domain diagnostics.
- [x] #314 representative electrolyte GFPE route admission is gated by source-backed validation and postsolve certification.
- [ ] #320 full Khudaida figure-level model reproduction passes with `--require-model-pass`.
- [ ] #320 accepted model rows prove the shared native `NlpProblem`/Ipopt
  exact-Hessian route path, fixed sparse derivative receipts, route-owned
  transforms/scaling, and Ipopt postsolve diagnostics.
- [ ] #320 proves Born SSM+DS active-block exact-Hessian evidence and reduced
  electroneutral lift/back-lift before accepting Khudaida model rows.
- [ ] #320 certifies charged transfer by projected electrochemical or modified
  mean-ionic residuals; raw single-ion chemical-potential equality is rejected.
- [ ] #320 HELD2 flash scenario tests cover neutral-limit parity, source-backed electrolyte LLE, common-ion or mixed-salt reduced coordinates, stable feeds, unstable feeds, boundary feeds, and phase-label permutations.
- [ ] Capability evidence distinguishes neutral, associating, electrolyte, and reactive support without broadening beyond the full retained evidence.
- [ ] Docs state the exact source-backed electrolyte production scope and do not broaden into generic electrolyte, reactive, CE/CPE, regression, or release claims.

## Proof Oracle

- Run the active child proof oracle for #320.
- Run focused electrolyte equilibrium tests when implemented by a child gate.
- Run native contracts for changed native diagnostics.
- Run docs validation.

## Non-Goals And Boundaries

- No reactive route admission.
- No associating shortcut around exact derivative gates.
- No publication or release claim.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `electrolyte`
- Backend: `Ipopt`
- Readiness: `blocked_by_320`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature`
