# M4 CE Convergence Robustness Hardening

## Purpose

Harden standalone chemical equilibrium convergence after the first generic Pope-style continuation implementation. The immediate failure mode is not route admission or plot generation; it is strict CE proof quality. A hard MEA point can need caller seed escalation, proof correction, and homotopy before it passes the reaction-stationarity acceptance gate.

This tranche turns the seven identified robustness improvements into issue-backed work:

1. Make convergence robustness measurable with retained machine-readable MEA and synthetic stress diagnostics.
2. Strengthen the final proof corrector so accepted results satisfy strict reaction stationarity.
3. Add a nonideality continuation from ideal mole-fraction activity to ePC-SAFT EOS-derived activity.
4. Treat caller seeds as hints that must still pass independent proof, not as accepted truth.
5. Improve reaction scaling without weakening acceptance tolerances.
6. Add extent/nullspace initialization as a second independent feasible-start path.
7. Classify failures sharply so diagnostics identify which gate failed and what proof is missing.

## Scope

**Milestone:** M4 - Equilibrium
**Package owner:** `packages/epcsaft-equilibrium`
**Primary public interface:** `epcsaft_equilibrium.reactive_speciation`
**Primary native owner:** CE NLP, objective, continuation, and Ipopt proof diagnostics under `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium`

## Current Evidence

- Verified: the branch now has ePC-SAFT EOS-derived CE plumbing and a representative seeded MEA Phase 2 point that reaches `reaction_stationarity_inf_norm = 1.0905800706950686e-09` after max-min/homotopy final proof.
- Verified: focused native/API tests for standard-state EOS activity, reactive speciation API, and nonideal CE activity pass on the current branch.
- Inference: the solver is now materially assisted. It can recover a hard point, but robustness is not yet a measured envelope across stress families.
- Risk: accepting a point because it eventually converged once is weaker than a retained sweep proving failure classification, stationarity correction, scaling, and initialization behavior.

## Requirements

- Preserve one public standalone CE route and one activation-family contract.
- Keep final acceptance strict: stationarity and balance gates may be made better conditioned, but not weakened.
- Use ePC-SAFT EOS-derived activity through existing provider/equilibrium contracts, not a toy activity model.
- Keep proof seed provenance explicit for caller seeds, max-min seeds, homotopy stages, and extent/nullspace seeds.
- Prefer machine-readable retained diagnostics over new plot output unless a future issue explicitly owns a plot deliverable.
- Keep CPE, reactive LLE, reactive electrolyte LLE, PE phase discovery, and downstream application metrics outside this tranche.

## Success Criteria

- The retained CE robustness harness records accepted/failing points, final proof status, stationarity norms, balance norms, seed source, activity path, scaling diagnostics, and failure class.
- Final proof correction drives accepted MEA and synthetic hard points below strict stationarity tolerance without relying on intermediate homotopy stages as proof.
- EOS nonideality continuation can start from the ideal activity path and accept only the final EOS-derived proof.
- Caller seeds are accepted only after independent proof; failed caller seeds escalate through CE-owned initialization.
- Reaction scaling improves solver conditioning while preserving the same acceptance thresholds in physical proof diagnostics.
- Extent/nullspace initialization provides a second feasible start path with conservation and positivity proof.
- Failure diagnostics report precise classes such as infeasible conservation system, initialization failure, Ipopt failure, proof-correction failure, stationarity failure, balance failure, EOS activity failure, or unsupported standard-state request.

## Non-Goals

- No new public homotopy, Pope, scaling, or initializer route.
- No phase-equilibrium route migration.
- No new downstream MEA-specific package API.
- No capability broadening beyond standalone CE/speciation evidence.
- No regenerated plot deliverable unless a later issue explicitly asks for it.
