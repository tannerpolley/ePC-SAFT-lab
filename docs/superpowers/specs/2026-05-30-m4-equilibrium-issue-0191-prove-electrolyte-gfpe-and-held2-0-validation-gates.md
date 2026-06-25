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

## Current State After #306

- #269 closed the Khudaida closed-admission source gate: source rows,
  explicit-ion expansion, parameter-bundle construction, native electrolyte
  diagnostics, and closed public route state.
- #300 closed the prerequisite reduced-basis and Born SSM/DS exactness gate:
  exact charge-neutral NaCl lifting and CppAD derivative receipts.
- #302 closed the native charge-neutral electrolyte TPD screening gate:
  `_native_electrolyte_tpd_phase_discovery` reports three finite source-backed
  candidates, selected candidate count `2`, minimum TPD
  `-0.010922388988229025`, and maximum charge residual `0.0`.
- #306 closed the HELD2 counterion-pair phase-discovery gate with a Stage III
  handoff record.
- #312 is the active child blocker for Stage III electrolyte reduced-variable
  refinement.
- #313 and #314 are blocked by #312 and #313 respectively for postsolve
  certification and public route admission.

The #302 result is instability-screening evidence and a candidate seed. The
#306 result is phase-discovery and handoff evidence. Neither result is Stage
III electrolyte refinement, postsolve phase-set certification, or public route
admission.

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

## Full HELD2 Adoption Test Spine

The remaining electrolyte work must progress through this test spine in order.
Each child gate must leave retained checker output, focused native or Python
contracts, and a parent #191 tracker update.

1. Prerequisite evidence: #269, #300, and #302 stay historical prerequisite
   gates for source fixtures, reduced electroneutral variables, Born SSM/DS
   derivative receipts, and charge-neutral TPD screening.
2. Phase discovery: #306 proved independent counterion-pair matrix
   construction, reduced-coordinate trial/candidate lifting, finite TPD
   candidate metrics, pair-based mean-ionic bookkeeping, and a Stage III
   handoff record. It includes single-salt, common-anion, and multivalent
   matrix tests.
3. Stage III refinement: #312 must consume the #306
   candidate-set record and solve the reduced electrolyte phase-set equations
   with exact residual derivative evidence. Required residual families are
   neutral transfer, pair-based mean-ionic transfer, material balance in
   reduced coordinates, phase pressure consistency, and domain margins.
4. Postsolve certification: #313 must certify the refined phase set
   with per-phase charge balance, explicit-ion material balance reconstruction,
   neutral and mean-ionic transfer residual tolerances, pressure consistency,
   positive phase amounts, noncollapsed compositions, and stable replay from
   retained candidates.
5. Source-backed validation breadth: before public admission, validation must
   include the Khudaida fixture and at least one multi-ion mixed-solvent
   fixture from the local methodology context, with water + 1-butanol + NaCl +
   KCl Table 5 as the preferred first multi-ion case.
6. Public route admission: only after the previous gates pass may #314 expose
   a public electrolyte route. That admission checker must consume the source,
   phase-discovery, Stage III, and postsolve checkers and keep unrelated
   reactive, associating-generalized, and regression claims outside #191.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md`
- `docs/papers/md/Equilibrium/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md`

## Child Gate Sequence

1. Closed #269: closed-admission source gate.
2. Closed #300: reduced electroneutral basis and Born SSM/DS exactness gate.
3. Closed #302: charge-neutral electrolyte TPD screening gate.
4. Closed #306: counterion-pair HELD2 phase-discovery gate.
5. Open #312: Stage III electrolyte reduced-variable refinement gate.
6. Open #313: postsolve electrolyte phase-set certification gate, blocked by #312.
7. Open #314: public electrolyte route admission gate, blocked by #313.

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
