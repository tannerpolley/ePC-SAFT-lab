# M4 CE Generic Pope Homotopy Continuation

Milestone: `M4 - Equilibrium`
Package: `packages/epcsaft-equilibrium`
Status: `draft`
Last synced: `2026-06-29`

## Summary

Create a generic native continuation and homotopy substrate for equilibrium
NLP workflows, then use standalone chemical equilibrium and speciation as the
first production adopter. The goal is a robust CE solver that can start from
reaction constraints rather than source-oracle answers, while keeping the
activation matrix, activation family, and public route vocabulary clean.

The first adopter is `reactive_speciation`. Bubble/dew, HELD, branch tracing,
and CPE are not changed by this spec. They may later reuse the substrate through
a separate merge plan after CE proves the path with retained numerical tests.

## Project Context Evidence

- Verified repo scope: `docs/superpowers/PROJECT_CONTEXT.md` requires strict
  postsolve proof and rejects acceptable-point, tiny-step, feasible-point, and
  iteration-limit seed paths as capability evidence.
- Verified CE source spec:
  `docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md`
  records Pope 2004 as a CE robustness pattern: max-min feasible composition,
  pseudo-Gibbs continuation, separate continuation diagnostics, and final CE
  residual proof.
- Verified narrow issue guardrail:
  `docs/superpowers/issues/2026-06-26-m4-equilibrium-issue-0326-m4-ce-add-single-ce-nlp-activation-path.md`
  forbids Pope-style continuation as a side route for the original single-NLP
  activation slice.
- Decision from this brainstorm: that guardrail is superseded for this new
  scope. Pope/homotopy is allowed as native solver infrastructure inside the
  admitted CE activation family, but not as a public bypass route.
- Verified native Ipopt seam:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/nlp_problem.h`
  defines a thin `NlpProblem` contract for variables, bounds, objective,
  constraints, derivatives, scaling, and diagnostics.
- Verified Ipopt adapter seam:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/solvers/ipopt_adapter.h`
  and `.cpp` already support exact derivatives, option profiles,
  continuation-state warm starts, retained iteration history, and strict proof
  acceptance.
- Verified current CE implementation:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
  solves homogeneous CE as one Ipopt NLP over log species amounts with
  conservation constraints and final balance/affinity gates.
- Verified current CE block:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/chemical_equilibrium_block.cpp`
  provides ideal Gibbs objective, reaction residuals, exact gradients, exact
  Hessian data, and conservation diagnostics.
- Verified Python public path:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
  currently requires caller-provided `initial_amounts` for
  `reactive_speciation`.
- Verified MEA evidence state:
  `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
  and the MEA retained analysis currently use oracle-seeded CE comparison for
  proof-like plots. That is diagnostic evidence, not the desired unassisted CE
  proof.

## Recommended Architecture

The activation matrix admits the equilibrium family and public route. A route
family can declare that its production solver strategy is continuation-capable,
but the activation matrix must not add public route names such as `pope`,
`homotopy`, or `max_min`.

`NlpProblem` stays thin. It only feeds Ipopt the problem contract: variables,
bounds, objective, gradient, constraints, Jacobian, optional Hessian, scaling,
and local diagnostics. It does not own continuation policy.

A new generic continuation driver sits above `NlpProblem`. It receives an
ordered continuation plan, asks a route-specific factory for each stage's
`NlpProblem`, calls the existing Ipopt adapter, passes accepted primal and dual
state to the next stage, and records a structured trace. The driver understands
stage status, warm-start state, tolerances, option profiles, and trace schema.
It does not know CE chemistry, MEA species, phase splits, or source-oracle data.

CE/speciation is the first adopter. CE supplies a plan factory that can:

1. build an independent max-min feasible interior seed from conservation
   constraints;
2. try the final true Gibbs CE proof solve from that seed;
3. run an adaptive Pope-style pseudo-Gibbs homotopy only when the direct proof
   solve does not pass or when trace diagnostics are explicitly requested;
4. require a final `lambda=1` true Gibbs proof solve before accepting the
   public result.

## Components

### Activation Contract

Keep `reactive_speciation` as the public CE route and activation family. Add
only strategy metadata needed to prove that the admitted family uses the generic
continuation-capable Ipopt NLP infrastructure. Future phase-equilibrium families
can use the same metadata shape without changing this CE spec.

### Generic Continuation Driver

Add native driver types for:

- continuation plan metadata;
- stage identifiers and homotopy parameter values;
- Ipopt option profile per stage;
- accepted-state transfer;
- stage-level acceptance checks;
- retained trace serialization;
- final-proof gate summary.

The driver should work for any factory that produces `NlpProblem` instances and
stage acceptance checks. CE is the only production factory in this spec.

### Max-Min Feasible Initializer

Add a reusable linear-conservation initializer. It solves for amounts and a
margin variable under conservation equalities, positivity inequalities, and
bounded variables, maximizing the minimum scaled amount. It uses Ipopt through
the same `NlpProblem` contract with exact derivative data. If no strictly
positive feasible point exists, CE stops with the initializer trace.

### CE Continuation Factory

Refactor CE so the native layer can create a parameterized CE `NlpProblem` for a
homotopy value. The current ideal CE path can keep analytic derivatives and the
existing Gibbs block. Later nonideal CE can introduce CppAD-backed objective
derivatives at this factory boundary, with value/gradient/Hessian cross-checks
before any production claim.

### Python Workflow Adapter

Make `reactive_speciation(initial_amounts=None, ...)` the proof-oriented public
path. Omitted initial amounts use the independent max-min plus adaptive
continuation policy. Explicit caller seeds remain accepted for expert
diagnostics but must be labeled in the result payload.

The public result diagnostics should include:

- `initialization_policy`;
- `seed_source`;
- `uses_source_oracle_initial_amounts`;
- `continuation_trace`;
- `stage_count`;
- final proof route and activation-family metadata;
- final balance, affinity, and Ipopt KKT summaries.

## Data Flow

1. Python compiles species, reactions, feed amounts, conservation matrix,
   standard states, and solver options.
2. Native code builds the activation plan and variable layout for the admitted
   family.
3. If `initial_amounts` is omitted, native CE runs the max-min feasible
   initializer and records its trace.
4. CE tries the final true Gibbs proof solve from the independent initializer.
5. If the final proof solve passes, the driver returns a one-proof-path trace.
6. If the proof solve does not pass and adaptive homotopy is enabled, the driver
   moves from a gentle pseudo-Gibbs objective toward the true CE Gibbs objective
   through accepted homotopy stages.
7. Accepted stage variables and multipliers seed the next stage through the
   existing Ipopt continuation-state mechanism.
8. The final answer is accepted only when the `lambda=1` true CE proof solve
   satisfies final balance, affinity, and Ipopt proof gates.
9. MEA retained analysis runs with `initial_amounts=None` and compares CE output
   against Smith-Missen source curves without consuming source-oracle mole
   fractions as seeds.

## Error Handling

- Invalid schema, standard-state, or option inputs raise before native solving.
- Invalid caller-provided initial amounts raise before the native solve and
  produce no initialization trace.
- A failed max-min initializer raises with initializer diagnostics, conservation
  residuals, active constraints, and Ipopt status.
- A failed direct proof solve with adaptive homotopy disabled raises with the
  direct proof trace.
- Adaptive homotopy records every failed and accepted stage with homotopy
  parameter, step size, Ipopt status, scaled residuals, and KKT diagnostics.
- Intermediate homotopy stages never certify equilibrium by themselves.
- A failed final `lambda=1` proof solve raises even when intermediate stages
  were accepted.
- CppAD derivative mismatch is a hard native error when the CppAD CE objective
  seam is added.
- Source-oracle or Smith-Missen-seeded runs may exist only as labeled
  diagnostic comparisons. Proof runs must assert
  `uses_source_oracle_initial_amounts=false`.

## Testing And Proof Oracles

### Native Proofs

- Max-min feasible initializer exact cases:
  - two-species total conservation with known interior;
  - charge-neutral conservation with charged species;
  - tiny-species feasible case with large scaling spread;
  - infeasible conservation totals;
  - rank-deficient or duplicate conservation rows.
- Generic continuation driver smoke tests:
  - synthetic scalar or small quadratic `NlpProblem` with known parameter path;
  - accepted primal and dual state transfer;
  - stage trace schema;
  - adaptive step reduction when a stage does not pass;
  - final proof rejection when intermediate stages pass but final proof fails;
  - incompatible continuation-state rejection.
- CE native tests:
  - A/B ideal closed-form case with `initial_amounts=None`;
  - existing Pope tiny-species fixture without oracle seed;
  - exact Hessian availability for ideal CE;
  - activation matrix stays on the clean `reactive_speciation` family;
  - no public CE bypass binding appears.
- Derivative tests:
  - analytic ideal CE gradients and Hessians remain exact;
  - if CppAD CE objective support is added, CppAD value, gradient, and Hessian
    must match the analytic ideal path before broader use.

### MEA Numerical Proofs

Use the MEA H2O CO2 source-oracle lineage from MEA thermodynamics as comparison
data, but not as seeds.

Required retained runs:

- pointwise independent solves across the retained loading grid, with each
  loading using `initial_amounts=None`;
- CE-owned ordered continuation sweeps that may use only CE's previous accepted
  result, never Smith-Missen output;
- shuffled-order pointwise solves for a representative subset to prove that
  ordering is not hiding source-oracle assistance;
- at least 20 C and 40 C curves over the retained loading range;
- all retained species plotted individually and grouped where the source oracle
  uses grouped species;
- residual tables with max mole-fraction error by species, loading, and
  temperature;
- initialization audit tables with seed source, stage count, homotopy use,
  final proof residuals, and source-oracle seed flag.

Required retained plots:

- CE unassisted pointwise speciation vs Smith-Missen source oracle;
- CE-owned continuation speciation vs Smith-Missen source oracle;
- max absolute mole-fraction error by loading and species;
- stage-count or homotopy-use diagnostic by loading;
- old oracle-seeded comparison, if retained, clearly labeled as diagnostic and
  not as the proof plot.

### Validation Commands

The later implementation plan should select the exact command list, but the
minimum proof family is:

- focused native max-min and continuation-driver pytest;
- focused CE API pytest;
- standalone CE gate checker with oracle requirements;
- MEA retained data generation;
- MEA retained plot rendering;
- repo cleanup hook before handoff.

## Non-Goals

- No CPE or reactive phase-equilibrium production claim.
- No bubble/dew, HELD, branch-tracing, or phase-route migration in this first
  spec.
- No public algorithm-lane route names for Pope, homotopy, direct, or max-min.
- No source-oracle seeded MEA proof.
- No CppAD CE production claim unless derivative checks are added in the same
  implementation slice.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Workflow mode | User workflow-mode answer, 2026-06-29 | Start with intense brainstorming and spec before Auto implementation. | No code changes happen until this spec is reviewed and approved. | No | M4 owner |
| Scope target | User, 2026-06-29 | Use full Pope/homotopy ideas for a robust CE/speciation algorithm. | Supersedes the earlier max-min-only slice. | No | M4 owner |
| Genericity | User, 2026-06-29 | Prefer the generic route wherever possible, even if implementation is larger. | Adds a route-agnostic continuation substrate instead of a CE-only driver. | No | M4 owner |
| First adopter boundary | User, 2026-06-29 | Prove CE path is clean and generic first; plan broader merging later. | Bubble/dew, HELD, and branch tracing are out of this first implementation scope. | No | M4 owner |
| Activation cleanliness | User, 2026-06-29 | Keep activation matrix and activation family clean for CE and phase equilibrium. | Continuation is solver strategy metadata, not a public route family. | No | M4 owner |
| `NlpProblem` boundary | User, 2026-06-29 | `NlpProblem` only supplies objective, constraints, bounds, variables, derivatives, and scaling to Ipopt. | Continuation orchestration sits above `NlpProblem`. | No | M4 owner |
| Solve policy | User, 2026-06-29 | Adaptive: max-min seed, direct final proof, homotopy only when needed or requested. | Avoids unnecessary multiple Ipopt solves on easy points while retaining Pope robustness. | No | M4 owner |
| Public API seed policy | User, 2026-06-29 | `initial_amounts` omitted should use the independent initializer; explicit seeds remain labeled diagnostics. | MEA proof can be unassisted while preserving expert diagnostic controls. | No | M4 owner |
| Old anti-Pope guardrail | Repo evidence plus user decision, 2026-06-29 | Revise the old issue guardrail so it forbids public bypass routes, not internal Pope/homotopy infrastructure. | Implementation planning must update tests/docs that currently ban Pope-style continuation absolutely. | No | M4 owner |
| CppAD CE integration | Code evidence and user request, 2026-06-29 | Put CppAD at the future CE objective-provider boundary, not inside the first generic driver requirement. | CppAD-backed nonideal CE remains available for a later slice with derivative proof. | Yes | M4 owner |
| Phase-route adoption | User and repo scope, 2026-06-29 | Plan later merge/adoption after CE proof is retained. | Generic substrate must not force bubble/dew or HELD changes now. | Yes | M4 owner |
| MEA proof strength | User, 2026-06-29 | Add more MEA and native proof: pointwise, CE-owned continuation, shuffled subset, retained plots, and native driver contracts. | Testing must prove unassisted CE behavior numerically, not just API plumbing. | No | M4 owner |
| First pseudo-Gibbs objective | Brainstorm design boundary, 2026-06-29 | Choose the exact gentle pseudo-Gibbs objective during implementation planning. | Planning must define the homotopy objective before code work starts. | Yes | M4 owner |
| MEA numerical tolerances | Brainstorm testing boundary, 2026-06-29 | Set exact per-species and aggregate pass/fail tolerances during implementation planning. | MEA proof cannot close until tolerances are explicit and source-backed. | Yes | M4 owner |

## Open Questions For Planning

- What exact homotopy objective form should the first CE implementation use for
  the gentle pseudo-Gibbs stage?
- Should CppAD CE objective support be included in the same implementation plan
  or recorded as a child issue after analytic ideal CE homotopy passes?
- What are the exact MEA loading-grid tolerances for pass/fail by species and
  temperature?
