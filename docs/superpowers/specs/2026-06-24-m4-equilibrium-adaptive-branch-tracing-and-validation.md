# M4 Equilibrium Adaptive Branch Tracing And Validation

Milestone: `M4 - Equilibrium`
Affected package: `packages/epcsaft-equilibrium`
Validation root: `analyses/paper_validation`
Status: `draft`
Created: `2026-06-24`

## Summary

This spec turns the Gross/Sadowski 2002 Figure 2 branch-shape failure into
durable project code. The immediate goal is not another figure-specific patch.
The goal is an internal branch-tracing and validation layer that makes VLE,
LLE, and later GFPE envelope evidence depend on solved branch points rather
than smooth interpolation through too few points.

The first implementation should add reusable Python-side branch tracing in
`packages/epcsaft-equilibrium`. It should drive the existing public
`Equilibrium(...).solve()` point routes, carry continuation state between
neighboring solves, adaptively refine branch intervals, and write retained
diagnostics that paper-validation checkers can inspect. Native C++ remains the
owner of exact point solves, exact Hessian evidence, route diagnostics, and
postsolve certification. It should not gain Gross-specific branch or plotting
logic in this slice.

## User Decisions

- Scope: internal tracer first.
- Public API: do not expose a stable public branch/envelope API in the first
  implementation.
- Native boundary: keep native changes diagnostic-only unless a missing
  point-solve receipt blocks branch validation.
- Validation target: start with the Figure 2 sparse-sampling failure class,
  then make the same trace contract available to the rest of Gross/Sadowski
  2002 and future M4 route-family validation.
- Visual companion: not needed for this spec.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` makes M4 capability claims
  evidence-gated and assigns equilibrium implementation ownership to
  `packages/epcsaft-equilibrium`.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  defines the GFPE doctrine. Derived bubble/dew workflows are admitted route
  slices, not full HELD/GFPE proof by themselves.
- Verified:
  `docs/superpowers/plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md`
  opened a narrow source-backed associating VLE point-solve admission lane for
  Gross/Sadowski 2002 Figures 2, 6, 8, and 9.
- Verified:
  `docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md`
  assigns Figure 2-5 plot replication to paper-validation artifacts and
  forbids hiding native route implementation inside figure PRs.
- Verified: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
  exposes a point-oriented `Equilibrium(...).solve()` workflow.
- Verified:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py` already
  defines `EquilibriumSolverOptions.continuation_state` and retained result
  diagnostics.
- Verified:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
  maps `bubble_pressure`, `bubble_temperature`, `dew_pressure`, and
  `dew_temperature` through derived bubble/dew selector routes.
- Verified:
  `analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py`
  currently performs Figure 2 branch solving in figure-local code and carries
  continuation state by hand.
- Verified:
  `analyses/paper_validation/2002_gross/scripts/generate_clean_literature_overlays.py`
  smooths model curves with PCHIP-style interpolation through existing model
  points. This smoothing is useful for display only and cannot be treated as
  physical branch evidence when the solved points are sparse.
- Inference: Figure 2's blue-line miss was a branch-sampling and acceptance
  contract failure. The point route could solve additional low-composition
  anchors, but the reusable package layer did not force those anchors or block
  sparse interpolation from counting as a successful branch.

## Problem Statement

The current package has production point routes and paper-validation plot
scripts, but it does not have a reusable branch-tracing contract between them.
That gap allowed a sparse Figure 2 model curve to be smoothed into a continuous
line that looked like a valid branch while still being physically too low in
the low-composition region.

This failure class will recur for other M4 route families unless branch
validation checks the solved branch itself:

- required source anchors must be solved or explicitly rejected;
- interval gaps must be bounded;
- high-curvature regions must be refined;
- requested composition and solved composition must be compared;
- continuation state must be recorded rather than hidden inside a script loop;
- interpolation must never replace missing physical solves;
- figure acceptance must depend on branch completeness and solver receipts,
  not only visual smoothness or a top-level plot score.

## Non-Goals

- No electrolyte admission.
- No reactive, CE, CPE, or generalized phase-count admission.
- No HELD Stage I/II phase-discovery implementation in this slice.
- No new public branch/envelope tracing API in the first implementation.
- No Gross-specific code in native C++.
- No weakening of exact Hessian, postsolve, source-provenance, or fresh-native
  evidence gates.
- No acceptance credit for curves generated only by interpolation through
  sparse point solves.

## Recommended Approach

Use an internal Python branch tracer backed by existing point routes.

The tracer should live in `packages/epcsaft-equilibrium` so it can become a
shared project-code primitive for validation, issue work, and later API design.
The first consumers should be paper-validation generation scripts and checker
tests. Once the contract has been validated across multiple figures and route
families, a later spec can decide whether to promote the tracer into a public
`EquilibriumTrace` or `Equilibrium(...).trace()` API.

This is intentionally narrower than a native continuation solver. Native C++
should continue to solve one requested point at a time, expose exact derivative
and postsolve receipts, and return enough metadata for Python to decide whether
a branch point is accepted.

## Architecture

### Internal Package Layer

Add an internal module under `packages/epcsaft-equilibrium/src/epcsaft_equilibrium`.
The exact filename can be chosen during planning, but the intended ownership is
package code, not an analysis-only helper.

Candidate module name:

```text
epcsaft_equilibrium.branch_tracing
```

The module should provide a route-neutral trace engine that can initially cover
derived two-phase boundary routes:

- `bubble_pressure`
- `dew_pressure`
- `bubble_temperature`
- `dew_temperature`

It should be designed so later work can extend it to LLE and multiphase
branches without changing the retained evidence shape.

### Core Data Objects

The first implementation should use explicit data objects rather than loosely
typed dict plumbing.

`BranchTraceOptions` should capture:

- route;
- fixed thermodynamic variable, such as `T` for pressure traces or `P` for
  temperature traces;
- coordinate role, such as liquid composition for bubble routes or vapor
  composition for dew routes;
- required anchors;
- optional seed points;
- maximum composition interval;
- maximum pressure or temperature interval;
- curvature tolerance;
- requested-to-solved coordinate tolerance;
- maximum refinement iterations;
- maximum accepted points;
- exact-Hessian requirement;
- postsolve acceptance requirement;
- solver options forwarded to `Equilibrium(...).solve()`;
- continuation policy.

`BranchTraceAnchor` should capture:

- anchor id;
- requested coordinate;
- source role;
- source reference;
- whether the anchor is required for acceptance;
- optional expected pressure or temperature from source data;
- optional uncertainty used by validation scoring.

`BranchTracePoint` should capture:

- point id;
- route;
- requested coordinate;
- solved coordinate;
- paired phase coordinate;
- pressure;
- temperature;
- phase compositions;
- continuation state used;
- continuation state returned;
- selected seed or retry metadata;
- exact Hessian status;
- postsolve status;
- native route status;
- solver status;
- residual norms;
- whether the point is accepted;
- rejection reason when not accepted.

`BranchTraceSegment` should capture:

- left and right point ids;
- coordinate gap;
- pressure or temperature gap;
- slope estimate;
- curvature estimate;
- refinement reason;
- whether the segment satisfies acceptance thresholds.

`BranchTraceResult` should capture:

- route;
- fixed thermodynamic state;
- points;
- segments;
- required anchors solved;
- completeness flag;
- blocking reasons;
- diagnostic summary;
- export helpers for CSV rows and pandas DataFrames.

### Solve Loop

The branch tracer should not use a one-pass fixed grid as evidence. It should:

1. Solve every required anchor first.
2. Add configured seed points when anchors do not bracket the whole branch.
3. Sort accepted points by the route coordinate.
4. Build segments between neighboring accepted points.
5. Refine any segment that violates a gap, pressure/temperature jump, or
   curvature threshold.
6. Carry continuation state from the nearest accepted neighbor when solving a
   refinement point.
7. Rebuild segments after each refinement pass.
8. Stop only when all required anchors and all branch segments satisfy the
   trace contract, or when a loud incomplete result records blockers.

The initial implementation may use midpoint refinement. Later work can add
arclength, tangent, or sensitivity-informed refinement once native diagnostics
support that.

### Native Boundary

Native C++ remains point-solve infrastructure in this spec.

The Python trace layer may require additional normalized diagnostics from
native results. If missing, the implementation should add only diagnostic
receipts, such as:

- requested route;
- selector route;
- requested composition;
- solved liquid composition;
- solved vapor composition;
- requested fixed `T` or `P`;
- solved `T` or `P`;
- exact Hessian availability and backend;
- postsolve acceptance;
- selected seed index or seed source;
- continuation state;
- primal, dual, complementarity, and consistency residual summaries.

Native should not know about Gross/Sadowski 2002 figures, paper-validation
folder names, plot scores, or source anchors.

### Paper-Validation Integration

Gross/Sadowski 2002 figure generators should consume the internal branch tracer
instead of open-coding branch loops in figure-local scripts.

For Figure 2, the model-generation path should:

- build source anchors from retained source rows;
- request both bubble and dew branch traces;
- require low-composition anchors to be solved rather than interpolated across;
- export accepted trace points to the figure's model CSV;
- export trace diagnostics to a retained summary artifact;
- fail the checker if any required anchor or segment remains incomplete.

The shared overlay renderer may still generate smooth display rows from
accepted trace points, but score and acceptance must remain tied to the trace
completeness record.

## Data Flow

```text
source/reference branch anchors
  -> BranchTraceOptions and BranchTraceAnchor records
  -> Equilibrium(...).solve() point routes
  -> native point-solve diagnostics
  -> BranchTracePoint and BranchTraceSegment records
  -> BranchTraceResult
  -> paper-validation model CSV and trace diagnostics
  -> renderer and score JSON
  -> full-replication checker
```

The key rule is that source anchors and accepted trace points are evidence.
Dense display rows are presentation artifacts.

## Error Handling

The trace layer should prefer loud incomplete results over hidden substitution
behavior.

Hard blockers:

- required anchor solve fails;
- exact Hessian evidence is missing when required;
- postsolve acceptance is false when required;
- requested-to-solved coordinate drift exceeds tolerance;
- route returns a mismatched selector route;
- refinement budget is exhausted while required segments remain invalid;
- branch points are non-monotone in the selected coordinate after sorting;
- required diagnostic fields are missing.

Candidate offset retries must not silently count as solving the requested
anchor. If an implementation keeps offset attempts as a diagnostic aid, the
accepted `BranchTracePoint` must record both requested and solved coordinates,
and the trace result must reject the anchor when drift exceeds the configured
tolerance.

## Validation And Tests

### Package Tests

Add focused tests under `packages/epcsaft-equilibrium/tests`.

Minimum package coverage:

- trace options validate supported route and coordinate roles;
- required anchors are solved before optional refinement;
- segment refinement inserts points when a composition gap threshold is
  exceeded;
- segment refinement inserts points when pressure or temperature curvature
  exceeds threshold;
- incomplete traces report blockers instead of returning successful results;
- exact Hessian and postsolve requirements are enforced from result
  diagnostics;
- continuation state from one accepted point can be carried to a neighboring
  solve;
- coordinate drift beyond tolerance rejects the point.

### Native Diagnostic Contract Tests

Only add native diagnostic contract tests if implementation discovers missing
receipts. Those tests should assert normalized diagnostics, not physical Gross
2002 values.

Possible diagnostic fields:

- requested and solved route metadata;
- requested and solved composition;
- fixed and solved thermodynamic variables;
- exact Hessian fields;
- postsolve acceptance fields;
- seed and continuation fields;
- residual summary fields.

### Paper-Validation Regression Tests

Add a regression fixture for the old Figure 2 failure class.

The fixture should prove that a sparse branch with too few low-composition
points cannot pass the full-replication checker merely because the renderer
creates a smooth line. A good test shape is:

- provide a model CSV with sparse accepted-looking rows;
- provide source anchors in the low-composition region;
- run the checker;
- expect a blocker for missing required trace anchors or invalid segment gaps.

### Gross/Sadowski 2002 Figure 2 Acceptance

Figure 2 acceptance should require:

- retained source anchors;
- bubble and dew trace diagnostics;
- all required anchors solved;
- bounded maximum composition interval;
- bounded maximum pressure interval or curvature;
- exact Hessian evidence on every accepted model point;
- postsolve acceptance on every accepted model point;
- source-to-model score computed from accepted trace points;
- renderer output in PNG, SVG, and PDF.

## Acceptance Criteria

The spec is ready to plan when it creates an issue slice that can be validated
without broad GFPE claims.

The implementation is complete when:

- an internal branch tracing module exists in `packages/epcsaft-equilibrium`;
- Gross/Sadowski 2002 Figure 2 generation uses the shared tracer instead of a
  figure-local solve loop;
- sparse branch interpolation cannot pass the checker;
- Figure 2's low-composition bubble branch is reproduced by solved trace
  points, not by display interpolation;
- every accepted trace point reports exact Hessian and postsolve evidence;
- retained trace diagnostics identify requested anchors, solved coordinates,
  segment gaps, refinement reasons, and blockers;
- focused package tests and paper-validation checker tests pass;
- no public branch-tracing API is claimed;
- no electrolyte, reactive, CE, CPE, generalized phase-count, or HELD Stage
  I/II admission claim is broadened.

## Suggested Issue Shape

Create a new child issue under the M4 equilibrium workstream for the first
implementation slice.

Suggested title:

```text
Add internal adaptive branch tracing for M4 boundary-route validation
```

Suggested scope:

- implement internal branch trace data objects and solve loop;
- wire Gross/Sadowski 2002 Figure 2 model generation to the shared tracer;
- add checker blockers for missing trace anchors and invalid sparse segments;
- add tests for refinement, exact-Hessian gating, coordinate drift, and Figure
  2 sparse-branch regression;
- update M4 README evidence after the branch-tracing gate passes.

Defer to later issues:

- public `EquilibriumTrace` API;
- native tangent or arclength continuation;
- LLE/multiphase branch tracing;
- HELD Stage I/II phase discovery;
- electrolyte branch/envelope tracing.

## Open Questions For Planning

- What thresholds should be the first defaults for maximum composition gap,
  pressure gap, and curvature in VLE traces?
- Should trace diagnostics be one retained JSON per branch or embedded as
  columns in model CSV plus a compact summary JSON?
- Which existing native diagnostic fields already cover requested/final route
  specs, and which must be added?
- Should the first branch tracer support only binary routes, or should the data
  objects be general enough for ternary and higher mixtures while tests cover
  binaries only?

## Exit Criteria For This Spec

This spec should transition to `superpowers-project:write-plan` after review.
The first plan should target a narrow implementation PR, not a broad GFPE
rewrite.
