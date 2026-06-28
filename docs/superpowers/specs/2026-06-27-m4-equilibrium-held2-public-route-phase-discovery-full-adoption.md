# M4 HELD2 Public Route Phase Discovery Full Adoption

## Purpose

Lay out the missing implementation backbone for full HELD2-style electrolyte
phase discovery in `packages/epcsaft-equilibrium`. The existing M4 electrolyte
issues prove readiness, charge-neutral screening, retained phase-discovery
diagnostics, local Stage III refinement, postsolve certification, and
representative public admission. They do not fully implement HELD2-style
global phase discovery as the production candidate-generation engine behind
the public electrolyte route.

This spec turns that remaining long-term plan into concrete M4 issue slices.

## Scope

Owner: M4 equilibrium, package `packages/epcsaft-equilibrium`.

Target public behavior:

- `Equilibrium(..., route="electrolyte_lle")` can use HELD2-style discovery to
  find and certify electrolyte phase sets without relying on one retained
  representative fixture or hand-picked candidate set.
- The public route orchestrates discovery, Stage III Ipopt refinement, and
  postsolve certification.
- The route keeps reduced electroneutral coordinates, projected
  electrochemical or mean-ionic residuals, exact derivative receipts where
  claimed, and explicit phase-set completeness diagnostics.

Out of scope:

- Reactive electrolyte LLE.
- CE/CPE coupling.
- M5 parameter regression.
- Claiming Khudaida model reproduction without an M5-fitted parameter bundle.
- Replacing all boundary workflows with HELD2 discovery.

## Verified Current Coverage

- #300 closed the reduced electroneutral variable and Born SSM/DS exactness
  readiness gate.
- #302 closed native-backed charge-neutral electrolyte TPD screening, but it
  explicitly kept full HELD2 dual discovery pending.
- #306 closed a counterion-pair phase-discovery diagnostics gate. It proved
  matrix-rank and reduced-coordinate bookkeeping, but did not cut over public
  route candidate generation.
- #312 closed retained Stage III reduced-variable refinement evidence.
- #313 closed retained postsolve certification evidence.
- #314 closed representative public electrolyte route admission only.
- #320/PR #341 validates a Perdomo/Figiel electrolyte boundary row through the
  shared `NlpProblem`/Ipopt exact-Hessian route, but keeps full public HELD2
  production discovery out of the claim.

## Gap

The project plan says deterministic TPD/candidate screening is not full HELD.
The remaining missing capability is a production-grade HELD2-style discovery
orchestrator:

1. Continuous reduced electroneutral TPD minimization in volume-composition
   space.
2. Stage I stability certification over a governed start set.
3. Stage II dual/cutting-plane candidate discovery with explicit lower and
   upper bounds, bound-gap convergence, and candidate storage.
4. Stage III Ipopt refinement driven by Stage II candidates, not by a synthetic
   or fixture-specific phase set.
5. Postsolve phase-set completeness certification tied back to the Stage II
   dual certificate.
6. Public route orchestration and result diagnostics.
7. Scenario validation across stable, unstable, boundary, phase-label
   permutation, common-ion, and mixed-salt cases.
8. Registry, capability, and documentation admission after executable evidence.

## Engineering Doctrine

The implementation must preserve these HELD2 electrolyte requirements:

- Each trial and accepted phase is electroneutral by construction or by an
  explicit equality constraint.
- Charged-species transfer is checked by projected electrochemical or
  modified mean-ionic residuals, not raw single-ion chemical-potential
  equality.
- Ion trace phases are allowed through transformed positive coordinates.
- `Solve_Succeeded` alone is not accepted evidence. Physical postsolve and
  phase-set completeness must pass.
- Candidate discovery must report seed coverage, convergence failures,
  finite residuals, active bounds, and bound gaps.
- Public route capability claims must be narrower than the retained evidence.

## Issue Set

This spec is implemented by one tracking issue and seven vertical slices:

1. #343: full HELD2 public-route adoption tracking.
2. #344: doctrine and validation matrix.
3. #345: continuous reduced-electroneutral TPD minimizer.
4. #346: Stage I stability certificate.
5. #347: Stage II dual/cutting-plane discovery.
6. #348: public route orchestration through Stage III and postsolve.
7. #349: multi-scenario HELD2 validation ladder.
8. #350: registry, docs, and capability admission.

## Acceptance

The overall adoption is complete only when:

- the public electrolyte route uses HELD2 discovery for candidate generation;
- Stage III refinement consumes the discovered candidate set;
- postsolve certification reports phase-set completeness and physical
  residuals;
- retained tests cover stable, unstable, boundary, phase-label permutation,
  common-ion, and mixed-salt cases;
- registry/capability docs admit only the evidence-backed scope; and
- #191 can close without relying on #314 representative evidence or #320
  boundary-only evidence as a substitute for full phase discovery.
