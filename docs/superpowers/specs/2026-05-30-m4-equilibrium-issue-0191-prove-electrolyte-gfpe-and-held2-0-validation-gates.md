# Prove electrolyte GFPE and HELD2.0 validation gates

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
Status: `open`
Last synced: `2026-06-26`

## Summary

Prove electrolyte GFPE and HELD2.0 validation gates without treating public
electrolyte LLE route admission as complete until the electrolyte-specific
phase discovery, refinement, postsolve, full source-backed figure reproduction,
and broader HELD2 flash scenario evidence exists.

#191 is a HITL umbrella. It is not a direct implementation issue. Resolve it
through child gates that each add executable evidence and then update this
parent with closed provenance.

## Current State After #314 And #320 Reopen

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
- #312 closed the Stage III electrolyte reduced-variable refinement gate.
- #313 closed the postsolve electrolyte phase-set certification gate.
- #314 closed representative public route admission for one certified
  source-backed payload.
- #320 is the active child blocker for full Khudaida figure-level model
  reproduction and broader HELD2 flash scenario testing. Its closeout must also
  prove that accepted electrolyte rows stay on the shared native
  `NlpProblem`/Ipopt exact-Hessian production path.

The #302 result is instability-screening evidence and a candidate seed. The
#306 result is phase-discovery and handoff evidence. The #314 result is
representative route-admission evidence. None of those results prove that the
electrolyte route reproduces the retained Khudaida figures across all modeled
cases.

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
  chemical-potential, mean-ionic fugacity, or projected electrochemical
  residuals, not raw single-ion chemical-potential equality;
- accepted electrolyte flashes are generated through the common
  pressure-transformed Helmholtz `NlpProblem`/Ipopt phase NLP with route-owned
  bounds, smooth variable transforms, user scaling, exact objective gradients,
  exact constraint Jacobians, exact Lagrangian Hessians, sparse derivative
  receipts, and postsolve certification;
- Born SSM/DS active phase blocks have exact-Hessian evidence before Khudaida
  production rows are accepted;
- phase discovery must produce candidate phase-set evidence before Stage III
  refinement can claim convergence;
- Stage III refinement must solve the electrolyte reduced-variable phase-set
  equations, report strict Ipopt `success` and `solve_succeeded` when counted
  toward production readiness, and then pass postsolve material, charge,
  pressure, neutral transfer, mean-ionic transfer, and domain diagnostics.

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
- [ ] Khudaida figure-level model reproduction passes for every modeled figure
  or panel with retained fit statistics and plot score `>= 8.0`.
- [ ] Accepted Khudaida model rows prove the shared native `NlpProblem`/Ipopt
  exact-Hessian route path, including fixed sparse derivative receipts,
  `profile_exact_hessian_gate`, route-owned transforms/scaling, and Ipopt
  postsolve diagnostics.
- [ ] Born SSM/DS active blocks have exact-Hessian evidence before electrolyte
  model rows can close #320.
- [ ] Charged transfer uses projected electrochemical or modified mean-ionic
  residuals; raw single-ion chemical-potential equality is rejected.
- [ ] HELD2 flash scenario tests cover neutral-limit parity, source-backed
  electrolyte LLE, common-ion or mixed-salt reduced-coordinate behavior, stable
  feeds, unstable feeds, boundary feeds, and phase-label permutations.
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
5. Representative public route admission: #314 exposed a certified
   source-backed public route surface, but this is not full #191 closeout.
6. Source-backed validation breadth: #320 must make the Khudaida figure
   checker pass with model reproduction required and must add broader HELD2
   flash scenario tests. Validation must include the retained Khudaida fixture,
   at least one common-ion or mixed-salt reduced-coordinate case, and explicit
   proof that accepted rows use the shared native `NlpProblem`/Ipopt
   exact-Hessian production path with Born SSM/DS active-block exactness and
   projected electrochemical or modified mean-ionic residuals.
7. Final parent closeout: only after #320 passes may #191 close and hand off
   remaining benchmark/capability evidence to M6.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/papers/md/Equilibrium/Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems.md`
- `docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md`
- `docs/papers/md/Equilibrium/Khudaida et al. - 2026 - Upgrading the Extraction of Ethanol and Isobutanol from an Aqueous Solution in the Presence of Sodiu.md`
- `analyses/paper_validation/2026_khudaida/README.md`
- `analyses/paper_validation/2026_khudaida/analysis.yaml`
- `analyses/paper_validation/2026_khudaida/docs/md/provenance_notes.md`
- `analyses/paper_validation/2026_khudaida/shared/source/figure_manifest.csv`
- `docs/papers/md/Equilibrium/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md`

## Child Gate Sequence

1. Closed #269: closed-admission source gate.
2. Closed #300: reduced electroneutral basis and Born SSM/DS exactness gate.
3. Closed #302: charge-neutral electrolyte TPD screening gate.
4. Closed #306: counterion-pair HELD2 phase-discovery gate.
5. Closed #312: Stage III electrolyte reduced-variable refinement gate.
6. Closed #313: postsolve electrolyte phase-set certification gate.
7. Closed #314: representative public electrolyte route admission gate.
8. Open #320: full Khudaida electrolyte LLE figure and HELD2 flash validation
   gate, blocking #191.

## Implementation Notes

- Keep this issue in `packages/epcsaft-equilibrium` unless a child issue
  explicitly approves cross-milestone work.
- Consume provider Born derivative receipts through public provider APIs rather
  than rewriting provider EOS behavior inside M4.
- Treat public `electrolyte_lle` admission as representative until #320 proves
  full figure-level model reproduction and broader HELD2 flash scenarios.
- Keep raw single-ion chemical-potential equality out of acceptance criteria for
  charged species; use independent mean-ionic residuals.
- Keep production electrolyte acceptance on the shared native `NlpProblem`/Ipopt
  exact-Hessian route. Residual-only solves or adapter-owned thermodynamic
  equations are diagnostic substitutes only and cannot close #191.

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
