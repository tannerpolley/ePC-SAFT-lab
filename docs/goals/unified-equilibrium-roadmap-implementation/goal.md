# Unified Equilibrium Roadmap Implementation Goal

Implement the remaining unified equilibrium roadmap gaps by extending the existing ePC-SAFT native Ipopt, route-builder, reactive residual, stability, certification, benchmark, and capability-evidence modules.

## Source Plan

Follow the durable implementation plan:

```text
docs/superpowers/plans/2026-05-20-unified-equilibrium-roadmap-implementation.md
```

## Outcome

The package should satisfy the remaining `docs/roadmaps/unified_equilibrium_core_algorithm.md` requirements without adding a disconnected solver path:

- universal route postsolve certification is shared and route-agnostic;
- `kind="reactive_stability"` routes through a native coupled reactive stability NLP;
- reactive LLE and reactive electrolyte LLE are production-registered only after executable benchmark and holdout evidence pass;
- `epcsaft.capabilities()` remains honest and source-backed;
- validation, cleanup, and git status are clean at handoff.

## Hard Constraints

- Reuse the current native Ipopt adapter, route builders, reactive residual surface, stability builders, bindings, diagnostics, and capability registry.
- Do not add a Python production optimizer loop.
- Do not add a staged speciation fallback for `reactive_stability`.
- Do not promote reactive LLE or reactive electrolyte LLE capabilities until benchmark proof passes.
- Preserve exact-or-loud Hessian behavior for production native Ipopt routes.
- Keep broad Graphify or JetBrains refreshes as Scout/Judge tasks, not untracked side artifacts.

## Starter Command

```text
/goal Follow docs/goals/unified-equilibrium-roadmap-implementation/goal.md.
```
