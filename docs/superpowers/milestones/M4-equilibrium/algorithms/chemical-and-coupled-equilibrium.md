---
doctrine_schema_version: 1
algorithm_ids:
  - standalone-chemical-equilibrium
  - simultaneous-chemical-phase-equilibrium
source_local_path: docs/papers/md/Equilibrium/Ascani - 2023 - Simultaneous Predictions of Chemical and Phase Equilibria in Systems with an Esterif.md
source_anchors:
  - section-2.1-equations-1-10-ce-cpe-thermodynamics
  - section-2.2-equations-13-17-coupled-residual-solve
  - algorithmic-structure-steps-1-4
  - figure-7-cpe-procedure
runtime_status: closed
algorithm_parity_status: incomplete
conservation_basis: fixed-elemental-inventory
---

# Standalone Chemical And Coupled Phase-Chemical Equilibrium

## Two Different Problem Families

Standalone chemical equilibrium is a homogeneous single-phase problem. It
solves species amounts or reaction extents subject to conservation,
nonnegativity, a declared standard state, and zero independent reaction
affinities. An activity-based equilibrium-constant relation is an equivalent
form only when it uses the same species basis and standard-state convention.

Simultaneous chemical and phase equilibrium is a multiphase problem. Its final
formulation must satisfy interphase transfer equilibrium and reaction
equilibrium together while preserving material or element balance. It is not a
standalone chemical-equilibrium solve followed by a phase-only flash.

Local source: Ascani 2023, Sections 2.1 and 2.2, the Algorithmic Structure
steps, and Figure 7 in the paper named by `source_local_path` above.

## Source Scope

Ascani 2023 frames the thermodynamic problem as total Gibbs minimization under
fixed elemental inventory and species nonnegativity. Reaction coordinates
produce reaction-adjusted species amounts, and the phase sums satisfy those
species balances. The demonstrated algorithm uses homogeneous chemical
equilibrium, stability analysis, and phasewise chemical-equilibrium
calculations to build initial guesses. Its final reactive flash solves the
interphase fugacity and reaction-equilibrium equations in one coupled residual
system.

The demonstrated systems contain four neutral molecular species, one
esterification reaction, and liquid-liquid phase equilibrium. They do not
prove generic electrolyte CPE, reactive vapor-liquid equilibrium, or arbitrary
reaction-network support.

## Package Contracts

A standalone CE child design must declare:

- the true-species and conservation basis;
- independent reactions or an equivalent null-space basis;
- standard states and equilibrium-constant conventions;
- variables, bounds, scaling, derivatives, and acceptance checks;
- source-qualified validation independent of any phase-split claim.

A CPE child design must add phase amounts and compositions, interphase
transfer conditions, phase-specific constraints, stability or phase-discovery
logic, and a coupled final solve. It may use a constrained thermodynamic
objective or a source-backed exact residual formulation, but the final path
must couple phase transfer and reaction affinity rather than sequence two
independent production solves.

## Package Status

The package retains a homogeneous Gibbs/Ipopt foundation and useful CE schema
work. Its retained nonideal MEA balance and stationarity proof does not pass,
so standalone CE remains closed. Reactive LLE, reactive electrolyte LLE, and
simultaneous CPE also remain closed and require separate child designs after
their prerequisites pass.
