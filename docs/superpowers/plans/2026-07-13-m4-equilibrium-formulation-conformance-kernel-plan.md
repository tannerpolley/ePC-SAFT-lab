# Equilibrium Formulation Conformance Kernel Plan

> **Execution discipline:** Use `chemical-engineer` for thermodynamic and
> numerical claims, vertical red/green TDD for each family, and focused
> verification before the local commit.

**Goal:** Exercise every family in the canonical equilibrium-formulations
document with deterministic, EOS-free manufactured problems and prove that one
analysis-private execution kernel can run the families without equating their
mathematical formulations or expanding public capability.

**Owning milestone and package:** This is M4 `epcsaft-equilibrium` formulation
proof work. It remains under `analyses/reference_oracles/`; it is not installed
package code. A later Python EOS-evaluation toolbox belongs to the separately
owned M8 toybox and is outside this plan.

**Architecture:** A common receipt envelope exposes two nominally distinct
paths: direct constrained/reduced minimization and residual solving. Family
adapters own coordinates, constraints, topology, independent evidence, and
certificates. A formulation identifier is carried by every problem, result,
and certificate so cross-family certificate reuse fails explicitly.

**Dependencies:** Python, NumPy, pytest, and repository tooling only. No
ePC-SAFT evaluator, native extension, IPOPT, SciPy optimizer, or package API.

## Task 1: Shared kernel contracts

Create `analyses/reference_oracles/equilibrium_formulations/kernel.py` and
tests proving:

- direct and residual problems use separate execution paths;
- bounds, scales, dimensions, nonfinite callbacks, and derivative receipts are
  validated;
- deterministic multistart and backend identity are recorded;
- no fallback is attempted;
- acceptance requires both generic numerical checks and a formulation-matched
  independent certificate;
- certificates cannot cross formulation identifiers.

## Task 2: Public pressure-boundary family

Add manufactured bubble-pressure, dew-pressure, and pure-saturation residual
adapters. Test full residual rank, normalization, separated positive volumes,
analytic Jacobians, known roots, critical-volume collapse, and the explicit
absence of a global stability claim.

## Task 3: Neutral and association-aware HELD

Register the existing neutral HELD manufactured oracle with the common receipt
envelope without moving its family-owned phase state, direct objective, TPD,
or common-tangent certificate. Add an association-aware manufactured evaluator
with a unique implicit state, analytic implicit derivative, inner residual
receipt, stale-state rejection, and singular-inner-Jacobian failure.

## Task 4: Perdomo HELD2 and Ascani pair equilibrium

Add separate manufactured adapters. HELD2 tests eliminated-ion recovery,
modified-mole normalization and balances, charge feasibility, modified
potential equality, Galvani-gauge invariance, and invalid eliminated amounts.
Ascani tests pair-basis rank/null-charge identity, pair transfers, analytic
residual roots, balance/charge feasibility, pair-potential gauge invariance,
and rank-deficient bases. Cross-family tests must reject exchanged
certificates.

## Task 5: Standalone CE and CPE

Add a convex manufactured CE problem with a complete reaction basis, known
extent, elemental balance, zero affinity, objective comparison, and boundary
complementarity case. Add a simultaneous manufactured CPE problem whose
solution differs from both phase-only and reaction-only optima and requires
elemental balance, interphase potential equality, reaction affinity,
phase-topology, and objective evidence in one certificate.

## Task 6: Cross-family and convergence characterization

Run every adapter through the common kernel and test:

- analytic derivatives against central differences;
- degrees of freedom and independent constraint/Jacobian rank;
- phase permutation/relabeling, extensive scaling, reaction-basis,
  species/reference-energy shifts, and applicable Galvani-gauge invariance;
- deterministic basin maps and tolerance/initialization perturbations;
- phase/species boundary behavior and metastable/local traps;
- invalid domains, invalid family coordinates/topologies, incomplete reaction
  bases, and singular implicit association state;
- unchanged package imports and public capability declarations.

Document verified, inferred, assumed, and unknown claims in the analysis
README. Manufactured solutions are mathematical test cases, never physical
predictions.

## Completion gate

Run the focused analysis tests twice, Ruff on owned Python files, project
structure and capability-boundary contracts, `git diff --check`, and the repo
cleanup hook. Review constraint ranks, units/bases, certificate independence,
derivative coverage, topology degeneracy, and explicit nonclaims. Commit the
completed EOS-free conformance work locally; do not push. Stop before creating
the M8 Python EOS-evaluation toolbox.
