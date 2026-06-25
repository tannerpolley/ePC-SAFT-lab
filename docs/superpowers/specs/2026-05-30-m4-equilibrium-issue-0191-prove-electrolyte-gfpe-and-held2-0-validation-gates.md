# Prove electrolyte GFPE and HELD2.0 validation gates

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
Status: `open`
Last synced: `2026-06-25`

## Summary

Prove electrolyte GFPE and HELD2.0 validation gates without opening public
electrolyte LLE or TP-flash routes before the electrolyte-specific phase
discovery, refinement, postsolve, and source-backed validation evidence exists.

#191 is a HITL umbrella. It is not a direct implementation issue. Resolve it
through child gates that each add executable evidence and then update this
parent with closed provenance.

## Current State After #302

- #269 closed the Khudaida closed-admission source gate: source rows,
  explicit-ion expansion, parameter-bundle construction, native electrolyte
  diagnostics, and closed public route state.
- #300 closed the prerequisite reduced-basis and Born SSM/DS exactness gate:
  exact charge-neutral NaCl lifting and CppAD derivative receipts.
- #302 closed the native charge-neutral electrolyte TPD screening gate:
  `_native_electrolyte_tpd_phase_discovery` reports three finite source-backed
  candidates, selected candidate count `2`, minimum TPD
  `-0.010922388988229025`, and maximum charge residual `0.0`.
- #306 is the active child blocker for HELD2 counterion-pair phase discovery.

The #302 result is instability-screening evidence and a candidate seed. It is
not full HELD2 phase discovery, Stage III electrolyte refinement, postsolve
phase-set certification, or public route admission.

## HELD2 Algorithm Doctrine

For this project, HELD2 means the electrolyte extension of the staged HELD
phase-discovery workflow for distributed ions. The required electrolyte
thermodynamics come from the local multiphase electrolyte methodology paper and
the M4 GFPE doctrine:

- charged true species must be represented explicitly with declared charges;
- per-phase electroneutrality is mandatory;
- an independent counterion-pair matrix must span `N_ch - 1` reduced ionic
  coordinates for the active charged species;
- transformed electrolyte variables must keep candidate and refined phases in
  the electroneutral subspace by construction;
- neutral species equilibrium is checked with neutral chemical-potential or
  fugacity residuals;
- charged species transfer equilibrium is checked with independent mean-ionic
  chemical-potential or mean-ionic fugacity residuals, not raw single-ion
  chemical-potential equality;
- phase discovery must produce candidate phase-set evidence before Stage III
  refinement can claim convergence;
- Stage III refinement must solve the electrolyte reduced-variable phase-set
  equations and then pass postsolve material, charge, pressure, neutral
  transfer, mean-ionic transfer, and domain diagnostics.

## Acceptance Gates

- [ ] HELD2 counterion-pair phase-discovery evidence is retained and consumes
  the #269, #300, and #302 prerequisite gates.
- [ ] Stage III electrolyte refinement consumes the HELD2 candidate set and
  solves in reduced electroneutral variables.
- [ ] Postsolve electrolyte phase-set certification verifies material balance,
  per-phase charge balance, pressure consistency, neutral transfer residuals,
  mean-ionic transfer residuals, and domain margins.
- [ ] Electrolyte GFPE route admission is gated by source-backed validation and
  postsolve certification.
- [ ] Capability evidence distinguishes neutral, associating, electrolyte, and
  reactive support.
- [ ] Docs do not claim electrolyte production support before executable
  evidence passes.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md`
- `docs/papers/md/Equilibrium/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md`

## Child Gate Sequence

1. Closed #269: closed-admission source gate.
2. Closed #300: reduced electroneutral basis and Born SSM/DS exactness gate.
3. Closed #302: charge-neutral electrolyte TPD screening gate.
4. Open #306: counterion-pair HELD2 phase-discovery gate.
5. Future child: Stage III electrolyte reduced-variable refinement gate.
6. Future child: postsolve electrolyte phase-set certification gate.
7. Future child: public electrolyte route admission gate.

## Implementation Notes

- Keep this issue in `packages/epcsaft-equilibrium` unless a child issue
  explicitly approves cross-milestone work.
- Consume provider Born derivative receipts through public provider APIs rather
  than rewriting provider EOS behavior inside M4.
- Keep public `electrolyte_lle` absent from public routes, proof routes, and
  production families until the route-admission child closes.
- Keep raw single-ion chemical-potential equality out of acceptance criteria for
  charged species; use independent mean-ionic residuals.

## Non-Goals

- No reactive route admission.
- No associating shortcut around exact derivative gates.
- No parameter-regression target.
- No publication or release claim.

## Validation

- Run the child proof oracle for the active child gate.
- Run focused native contracts for changed native diagnostics.
- Run docs validation after tracker, mirror, registry, or capability text
  changes.
