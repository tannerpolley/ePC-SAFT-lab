---
doctrine_schema_version: 1
authority: m4-equilibrium-package-architecture
current_public_routes:
  - bubble_pressure
  - dew_pressure
  - single_component_vle
public_boundary_routes:
  bubble_pressure:
    algorithm_family: direct-boundary
    executes_held_discovery: false
  dew_pressure:
    algorithm_family: direct-boundary
    executes_held_discovery: false
doctrine_documents:
  - algorithms/neutral-held.md
  - algorithms/strong-electrolyte-held2.md
  - algorithms/ascani-electrolyte-equilibrium.md
  - algorithms/chemical-and-coupled-equilibrium.md
runtime_activation_owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h
---

# Generalized Fluid-Phase Equilibrium

This document is the short M4 package-architecture authority for equilibrium.
The algorithm documents linked below own scientific terminology. The native
activation descriptor owns runtime exposure. Historical plans and issue
receipts record implementation history, but they do not redefine either
authority.

## Source Hierarchy

Use these authorities in order:

1. `docs/latex/equations.tex` for ePC-SAFT contribution equations.
2. The local paper Markdown named in each algorithm doctrine for the published
   formulation.
3. The four M4 algorithm doctrines for package terminology and algorithm
   boundaries.
4. The native activation descriptor for callable route status.
5. M6 registries and retained artifacts for literature reproduction evidence.

The algorithm doctrines are:

- [Pereira HELD for neutral molecular fluids](algorithms/neutral-held.md)
- [Perdomo HELD2 for strong electrolytes](algorithms/strong-electrolyte-held2.md)
- [Ascani counterion-pair electrolyte equilibrium](algorithms/ascani-electrolyte-equilibrium.md)
- [Standalone chemical equilibrium and coupled phase-chemical equilibrium](algorithms/chemical-and-coupled-equilibrium.md)

The
[source-faithful recovery specification](../../specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md)
governs conflicts with historical completion language.

## Current Capability Boundary

The public equilibrium surface remains limited to `bubble_pressure`,
`dew_pressure`, and scoped methane/ethane/propane `single_component_vle`.
Bubble and dew pressure are direct local boundary problems. They do not execute
Pereira HELD phase discovery and do not produce HELD stage receipts.

Neutral TP flash, neutral LLE, generalized multiphase equilibrium, electrolyte
LLE, standalone chemical equilibrium, reactive LLE, reactive electrolyte LLE,
and simultaneous phase-chemical equilibrium remain closed. Internal component
evidence does not admit these route families.

## Derived Boundary Workflows

Bubble-pressure and dew-pressure routes are public as direct local boundary
problems within their scoped evidence. Bubble/dew temperature, cloud, and
shadow workflows remain closed. Future admission for any closed boundary
workflow requires its own source-backed route evidence and activation change.

## Package Ownership

M3 provider code owns resolved model input, EOS evaluation, and provider
derivatives. M4 equilibrium code consumes that resolved input and owns:

- phase evaluation and typed equilibrium problem formulations;
- local NLP contracts and the shared Ipopt adapter;
- stability and phase-discovery controllers;
- formulation-specific postsolve certification;
- the native activation descriptor and typed result path.

M6 owns benchmark datasets, literature reproduction, retained figures, and
evidence maturity. Algorithm parity, local equilibrium validity, phase
discovery, and literature reproduction remain separate gates.

## Canonical Architecture

```text
provider-resolved model
  -> phase evaluator
  -> typed boundary, stability, free-energy, or chemical problem
  -> shared local-NLP interface and Ipopt adapter where applicable
  -> formulation-specific result and certificate

Pereira or Perdomo controller
  -> Stage I stability search
  -> Stage II linear upper / nonconvex lower loop
  -> Stage III direct free-energy minimization
  -> trace refinement and postsolve checks

native activation descriptor
  -> admitted typed request
  -> one production owner
  -> typed public result
```

HELD Stage II contains a distinct linear upper problem and nonconvex lower
problems. One local NLP cannot replace that controller. HELD Stage III directly
minimizes total free energy over the candidate phase set. Pressure and the
applicable independent potential equalities follow from stationarity and are
checked after the solve. A residual equation solve may correct or diagnose a
candidate; it does not define Stage III.

Electrolyte formulations must preserve their own independent coordinates and
potential conditions. Perdomo modified-mole HELD2 and the Ascani
counterion-pair formulation remain different algorithm families. Code may
compare individual ionic electrochemical potentials only when it declares an
explicit phase-electric or Galvani-potential convention.

Standalone chemical equilibrium solves one homogeneous chemical system.
Simultaneous phase-chemical equilibrium uses a coupled final formulation that
satisfies both interphase transfer and reaction equilibrium. Staged chemical
equilibration and stability calculations may provide seeds, but a sequential
chemical-equilibrium result followed by a phase-only solve does not establish
coupled equilibrium.

## Local NLP And Ipopt Contract

Each local problem declares variables, bounds, constraints, derivatives,
scaling, an option profile, and postsolve acceptance.
Ipopt must receive the route-owned scaling as user scaling. Automatic Ipopt scaling is useful for
diagnosis, but it is not the production contract for GFPE routes.

Solver acceptance records scaled constraint violation, scaled stationarity,
bound complementarity, active bounds, and the exact derivative receipt. The
shared profiles remain `proof`, `continuation_trace`, `held_refinement`, and
`diagnostic`. A route that claims an exact Hessian must pass
`profile_exact_hessian_gate` before it supplies production evidence. Stage 9
must not test real mixtures until the preceding infrastructure gate passes.

## Evidence And Admission Rules

M4 tracks five independent questions:

| Gate | Question |
| --- | --- |
| EOS validity | Does the provider evaluate the intended model and derivatives? |
| Local equilibrium validity | Does the supplied phase-set problem solve and certify its stated formulation? |
| Phase-discovery validity | Did the selected controller find the phases required by its claimed scope? |
| Algorithm parity | Did the code execute the operations named by the Pereira, Perdomo, or Ascani doctrine? |
| Literature reproduction | Does the accepted stack reproduce a selected real system within declared tolerances? |

Finite starts, sampled candidates, and a converged local refinement do not
prove a complete Stage II loop or globally complete phase discovery. The
stochastic HELD and HELD2 implementations described by the source papers also
do not provide a deterministic finite-time global guarantee.

Current deterministic TPD/candidate screening remains useful seed and
postsolve support, but it must not be described as full HELD. Registry family
labels are planning labels only; they are not runtime route or capability
keys.

Only the native activation descriptor may expose a route. Capability text,
registries, tests, and retained evidence must follow that descriptor and may
not broaden it.
