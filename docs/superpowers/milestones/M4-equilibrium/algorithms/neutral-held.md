---
doctrine_schema_version: 1
algorithm_ids:
  - pereira-held
source_local_path: docs/papers/md/Equilibrium/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md
source_anchors:
  - figure-1-table-1-three-stage-scheme
  - section-3.1-stage-i-stability
  - section-3.2-stage-ii-dual-loop
  - section-3.3-stage-iii-free-energy-minimization
stage_iii_primary_problem: direct-total-free-energy-minimization
residual_solve_role: optional-corrector-or-diagnostic
interphase_stationarity: molecular-chemical-potential-equality
runtime_status: closed
algorithm_parity_status: incomplete
stage_ii_status: not-executed
stage_iii_status: not-executed
---

# Pereira HELD For Neutral Molecular Fluids

## Identity And Scope

Pereira and coauthors define HELD as a three-stage algorithm for a
nonreactive molecular-fluid flash at fixed temperature, pressure, and overall
composition. The algorithm determines the stable phase count, compositions,
volumes, and phase fractions without requiring the user to supply a phase
count.

The 2012 paper applies HELD to SRK, SAFT-HS, and SAFT-VR models. It does not
provide ePC-SAFT model-parity evidence. The published stochastic searches aim
for reliable solutions but do not provide deterministic finite-time global
certification.

Local source: Pereira et al. 2012, Figure 1, Table 1, and Sections 3.1 through
3.3 in the paper named by `source_local_path` above.

## Three Coordinated Stages

Stage I performs a tangent-plane stability search. The published
implementation uses repeated tunnelling minimizations. Finding a negative
tangent-plane distance establishes instability. Failing to find one after a
finite search does not prove global stability.

Stage II alternates two different optimization problems:

- a linear upper or outer dual problem in the Lagrange multipliers;
- nonconvex Helmholtz lower or inner problems in composition and volume.

Each lower solution adds a cutting plane, updates the dual bounds, and may add
a candidate phase. A finite candidate list, deterministic screening pass, or
single bound audit does not execute this loop and cannot establish Stage II
parity.

Stage III directly minimizes the total free energy over the candidate phase
set. Pereira writes the objective as the total Gibbs free energy, assembled
from each phase's Helmholtz energy and the imposed-pressure volume term. The
problem enforces overall material balance and candidate-neighborhood bounds.
If the candidate set cannot satisfy balance or convergence checks, the
controller returns to Stage II. It then removes duplicate phases and refines
trace components.

## Stationarity And Certification

At a Stage III stationary point, all retained phases share the imposed
pressure and each transferable molecular component has the same chemical
potential across phases. The solver must check those conditions, material
balance, phase amounts, phase separation, domain validity, and the Stage II to
Stage III handoff.

An exact residual equation solve may correct a free-energy candidate or supply
diagnostics. It does not replace the direct free-energy objective and must not
be labeled as the canonical Stage III algorithm.

## Boundary Routes

Direct bubble-pressure and dew-pressure routes solve incipient-phase boundary
problems. They may reuse the phase evaluator and local NLP infrastructure, but
they do not execute HELD Stages I through III. Their admission evidence stays
independent of HELD algorithm parity.

## Package Status

The package retains useful neutral stability, candidate, local-NLP,
exact-derivative, and postsolve components. Current evidence does not establish
a complete Pereira HELD controller. Neutral TP flash and neutral LLE therefore
remain closed.
