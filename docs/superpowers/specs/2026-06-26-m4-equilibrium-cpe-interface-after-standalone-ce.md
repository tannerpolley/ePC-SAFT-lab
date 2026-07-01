# M4 CPE Interface After Standalone CE

## Scope

This contract defines the future simultaneous phase-plus-chemistry equilibrium
surface. It is a blocked interface contract only; it does not open reactive LLE,
reactive electrolyte LLE, or CPE runtime routes.

## Variables

The interface variables are phase species amounts, phase volumes, and reaction variables in one simultaneous solve.

- Phase species amounts for every candidate phase and true species.
- Phase volumes or equivalent route-owned density/pressure variables.
- Reaction variables, such as independent reaction extents or a coupled
  reaction-coordinate basis.

## Constraints

- Overall material balance across all phases and true species.
- Phase pressure consistency for every candidate phase.
- Transferable-potential equality for transferable species across phases.
- Reaction affinity for every declared reaction using explicit standard-state
  and equilibrium-constant conventions.
- Phase charge balance when ionic species are present.

## Derivatives

Future CPE admission requires exact coupled objective gradients, constraint
Jacobians, and Lagrangian Hessian evidence for the simultaneous phase-plus-
chemistry system. Standalone CE derivative evidence and PE derivative evidence
are prerequisites, not substitutes for the coupled derivative contract.

## Blockers

PE blockers:

- HELD Stage I stability.
- HELD Stage II dual phase discovery.
- HELD Stage III Ipopt refinement.
- Postsolve phase-set certification.

CE blockers:

- Standard-state registry.
- Reaction-affinity certification.
- Exact chemical-potential derivatives.
- Standalone CE validation ladder.

## Disallowed Evidence

Phase-only validation, CE-only validation, and sequential speciation plus flash
validation do not prove CPE. The CPE route must be one coupled solve over the
candidate phase set; it is not staged speciation followed by phase flash.
