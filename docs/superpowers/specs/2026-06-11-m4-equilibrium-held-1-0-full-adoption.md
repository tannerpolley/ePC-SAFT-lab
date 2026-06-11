# M4 Equilibrium HELD 1.0 Full Adoption

Milestone: `M4 - Equilibrium`
Affected packages: `packages/epcsaft-equilibrium`, provider public derivative
contracts where explicitly required
Affected validation milestone: `M6 - Validation`
Status: `draft`
Created: `2026-06-11`

## Summary

This spec broadens the local HELD 1.0 framing from the narrow #148 evidence
slice into a full adoption contract for every equilibrium family or method that
can claim phase-discovery support.

The central rule is simple: a closed predecessor issue is evidence, not adoption.
No family, method, registry row, capability line, or validation gate may claim
HELD 1.0 coverage only because an earlier issue closed. A family or method is
covered only when the active implementation path has executable HELD-stage
evidence, exact derivative coverage where the route requires it, postsolve
certification, and registry/capability text that matches the evidence.

The nearest resolvable implementation issue remains #187, because #186 and #148
are closed and #187 is the shared NLP/Ipopt gate that all later HELD adoption
work needs. The tracker should be refreshed before #187 execution so stale
blocked state does not hide the real queue.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` defines GFPE doctrine as the
  M4 organizing contract and says current deterministic TPD/candidate screening
  is seed and certification support, not full HELD.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  defines the HELD ladder: deterministic support, continuous TPD, Stage I
  stability, Stage II dual cutting-plane phase discovery, Stage III Ipopt
  refinement, then HELD2.0 for strong electrolytes.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
  keeps GFPE family rows unexposed until full HELD-stage phase discovery, exact
  derivatives, and postsolve certification pass.
- Verified:
  `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
  identifies Stage 8 shared NLP/Ipopt as the gate before Stage 9 real-mixture
  HELD proof, Stage 10 neutral fixture proof, Stage 11 boundary workflows, Stage
  12 generalized phase-set PE, Stage 13 associating GFPE, Stage 15 electrolyte
  GFPE, and Stage 17 registry/capability closure.
- Verified:
  `docs/superpowers/specs/2026-06-08-m3-held-readiness-cleanup.md` intentionally
  kept #148 narrow unless a later approved spec broadened HELD 1.0. This file is
  that broadening spec.
- Verified: GitHub M4 live state has #148 and #186 closed, while #187, #188,
  #189, #190, #191, and #145 remain open with blocked labels. #192 is the M6
  validation closure issue blocked by the M4 proof chain.
- Inference: the local tracker mirrors still need refresh after #148/#186
  closure because their readiness fields still describe blocked queues that may
  now have only downstream implementation dependencies.

## User Decisions

- Broaden HELD 1.0 beyond #148's narrow closure boundary.
- Treat all equilibrium families and public methods as requiring explicit
  coverage, derivation from a covered base family, or a documented exclusion
  from HELD claims.
- Create one new spec first, before writing a new implementation plan or issue.
- Make the spec detailed enough that the next closest ready issue can start
  from it without another broad context reconstruction.

## Full Adoption Definition

HELD 1.0 full adoption means every equilibrium family or method sits in exactly
one of these states:

1. `held_1_admitted`: the method or family has continuous TPD, Stage I, true
   Stage II dual phase discovery, Stage III Ipopt refinement, exact route
   derivatives where required, and postsolve phase-set certification.
2. `derived_from_held_1`: the method is a boundary or diagram workflow derived
   from a HELD-admitted base GFPE path and has strict convergence and
   certification receipts for the degree-of-freedom swap.
3. `held_variant_required`: the family needs a family-specific extension before
   it can be admitted, such as HELD2.0 for strong electrolytes or association
   derivative gates for associating systems.
4. `outside_phase_discovery`: the workflow does not use phase discovery and
   cannot borrow HELD completion language.
5. `blocked_by_missing_evidence`: the family or method is known, but the
   executable evidence chain is incomplete.

Closed issue state is never one of these states. It can only supply evidence
for a gate.

## Adoption Gates

### Gate 1 - Selector And Pretreatment

Issue coverage: #186, closed.

The selector and pretreatment pipeline must still be checked by later issues
when a new family or method enters the route. Closure of #186 means the current
route-shape and selector admission layer exists; it does not mean later methods
inherit HELD adoption automatically.

Required carry-forward evidence:

- public request shape is separated from GFPE family admission;
- mixture classification rejects unsupported association, electrolyte, or
  reactive inputs before optimizer dispatch;
- diagnostics identify route shape, input basis, selector admission, parameter
  readiness, derivative readiness, and exposure state separately.

### Gate 2 - Shared NLP And Ipopt Infrastructure

Issue coverage: #187, open and nearest resolvable.

This is the next implementation gate. It must finish before the HELD proof lane
is used for source-backed neutral admission, boundary workflows, generalized
phase sets, associating GFPE, or electrolyte GFPE.

Required evidence:

- `NlpProblem` owns physical variable layout, bounds, scaling, constraints,
  objective, gradient, sparse Jacobian, and Lagrangian Hessian contracts;
- sparse Jacobian and Hessian structures have fixed route-owned ordering;
- route-owned scaling and Ipopt option profiles are testable;
- exact-Hessian profile selection is visible in diagnostics;
- scaled numerical acceptance is separate from physical postsolve acceptance;
- solver failure, inadmissible route state, derivative gap, scaling problem,
  and postsolve certification failure are distinguishable.

### Gate 3 - True HELD 1.0 Phase Discovery

Issue coverage: #148 closed as baseline evidence, but full adoption still needs
one open child issue.

The gap is Stage II. Current neutral evidence closes a finite candidate bound
audit for the current fixture. Full HELD 1.0 adoption needs a replayable dual
cutting-plane phase-discovery loop.

Required evidence:

- continuous TPD minimization in volume-composition space;
- Stage I multistart stability with converged-start accounting;
- Stage II dual phase discovery with lower/upper bound history, gap tolerance,
  candidate creation, candidate rejection, and stopping reason;
- persisted candidate phases with route-assembly metadata;
- Stage III Ipopt refinement using the candidate phase set;
- relation between Stage II bounds and Stage III refined objective;
- incomplete TPD starts, open Stage II gaps, tiny-step paths, acceptable-level
  points, feasible-only points, and iteration-limit routes remain incomplete
  evidence.

New issue to create from this spec:

```text
M4: promote neutral HELD 1.0 Stage II to replayable dual phase-discovery gate
```

Recommended placement:

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Type: `Feature`
- Blocked by: #187
- Blocks: #188 and #189

Minimum acceptance:

- replace the current Stage II finite candidate audit as the adoption gate with
  a replayable dual phase-discovery loop;
- report lower bound, upper bound, bound gap, iteration count, candidates,
  rejected candidates, and stopping reason;
- persist candidate phase metadata enough for Stage III replay;
- keep deterministic screening as seed and postsolve support only;
- update registry language so `candidate_bound_audit` cannot be confused with
  `dual_loop_verified`;
- do not broaden associating, electrolyte, reactive, CE, CPE, or public route
  capability claims.

### Gate 4 - Source-Backed Neutral TP Flash Admission

Issue coverage: #188, open.

The neutral TP flash fixture is the first real GFPE admission proof. It must use
source-backed data and a supplied phase-discovery payload instead of hiding a
separate proof solve inside the fixture command.

Required evidence:

- hydrocarbon workbook-derived TP flash fixture or another accepted
  ePC-SAFT-compatible source-backed fixture;
- explicit species, parameters, binary interactions, temperature, pressure,
  feed composition, expected phase count, phase compositions, phase fractions,
  source path, and tolerances;
- material balance, phase pressure consistency, chemical-potential or fugacity
  equality, phase distinctness, exact derivative evidence, and postsolve
  stability;
- registry remains unexposed until the full gate chain passes.

### Gate 5 - Derived Boundary Workflows

Issue coverage: #189, open.

Bubble and dew can be derived from neutral GFPE. Cloud and shadow remain future
derived workflows until their contracts and route evidence exist.

Required evidence:

- boundary workflows are degree-of-freedom swaps over the shared GFPE core;
- strict route convergence is required for completion;
- routine validation stays contract-level unless a named route point or explicit
  sweep is requested;
- diagram traces report per-point diagnostics and skipped-point reasons;
- boundary workflows do not become independent family rows.

### Gate 6 - Generalized Phase-Set PE

Issue coverage: #189, open.

Full adoption requires phase-count independence after phase discovery. Repeated
two-phase calls are not generalized phase-set evidence.

Required evidence:

- phase-set record with phase count, phase kind, source, amount, volume,
  composition, objective value, feasibility, and status;
- arbitrary candidate phase-set feasibility;
- lower-free-energy feasible phase set rejection tests;
- duplicate and collapsed phase rejection;
- candidate completeness certification;
- replay only after each base family has source-backed validation.

### Gate 7 - Associating GFPE

Issue coverage: #145 and #190, open.

Associating GFPE may reuse neutral HELD machinery only after association
derivative architecture is proven for the selected association model. Association
is not covered by neutral HELD alone.

Required evidence:

- selected association architecture: lifted site variables with mass-action
  constraints or complete implicit association sensitivities;
- exact first and second derivative coverage for the active association terms;
- source-backed Gross/Sadowski associating proof target;
- association-specific postsolve checks for site bounds, mass-action residuals,
  contribution activation, and derivative block coverage;
- approximate explicit association closures stay diagnostic unless a route is
  deliberately exposed as approximate.

### Gate 8 - Electrolyte GFPE And HELD2.0 Bridge

Issue coverage: #191, open.

Strong electrolytes require HELD2.0 and reduced electroneutral variables. HELD
1.0 neutral evidence cannot be reused as electrolyte admission proof.

Required evidence:

- reduced electroneutral variable basis with lift and back-lift;
- per-phase charge-balance constraints;
- projected electrochemical potential equality;
- Born SSM+DS exact-Hessian evidence before electrolyte validation;
- electrolyte TPD and HELD2.0 diagnostics;
- source-backed Khudaida electrolyte fixture first, then Held/Ascani follow-ons
  after source and convention audits.

### Gate 9 - Registry, Capability, And Benchmark Closure

Issue coverage: #192, open in `M6 - Validation`.

Capabilities may move only after M4 proof gates exist. The registry must not
advance before executable evidence can point to source-backed fixtures and
validation commands.

Required evidence:

- family rows distinguish current public utilities from generalized GFPE
  admission;
- benchmark fixtures include source, model family, expected behavior,
  tolerances, and command receipts;
- capability output separates neutral, associating, electrolyte, reactive, CE,
  and CPE scope;
- docs and tests fail when capability claims outpace executable evidence.

## Family And Method Coverage Matrix

| Family or method | Required HELD adoption state | Current issue coverage | Gap |
| --- | --- | --- | --- |
| Public `flash` utility | `held_1_admitted` for proof lane; public cheap route may remain deterministic by default | #148, #187, #188 | full Stage II dual loop and source-backed admission chain |
| Neutral nonassociating `lle` utility | `held_1_admitted` before any generalized claim | #148, #187, #188, #189 | shared NLP, Stage II dual loop, phase-set completeness |
| `bubble_pressure`, `bubble_temperature`, `dew_pressure`, `dew_temperature` | `derived_from_held_1` | #189 | strict derived workflow evidence and trace diagnostics |
| Cloud/shadow workflows | `derived_from_held_1` after implementation | #189 | route contracts and executable evidence |
| `single_component_vle` | direct boundary-route evidence, no borrowed HELD claim | #228 closed, #192 later | capability registry alignment if exposed separately |
| PE-Neutral TP Flash | `held_1_admitted` | #187, #188 | shared NLP, Stage II dual loop, supplied phase-discovery payload |
| PE-Generalized Multiphase | `held_1_admitted` with phase-count independence | #189 | generalized phase-set route and completeness tests |
| PE-Associating TP Flash | `held_variant_required` | #145, #190 | exact association derivatives and source-backed associating proof |
| PE-Electrolyte LLE/TP Flash | `held_variant_required` | #191 | HELD2.0, reduced electroneutral basis, Born SSM+DS exact Hessian |
| CE Chemical Equilibrium | `outside_phase_discovery` | future CE work | standard-state and reaction-affinity proof, no HELD claim |
| CPE Combined Phase-Chemical | `held_variant_required` for phase part plus CE proof | future CPE work | simultaneous PE/CE proof after base PE and CE gates |

## Recommended Approach

### Option A - Full Adoption Spec Plus One Stage II Child Issue

Use this spec as the broad adoption contract, refresh stale tracker blockers,
start #187, and create the Stage II dual-loop issue as a child prerequisite for
#188/#189.

Tradeoff:

- Best queue hygiene and lowest risk of overloading #187.
- Adds one issue, but that issue owns a real missing algorithm gate instead of
  burying it in fixture work.

Recommendation: use Option A.

### Option B - Fold Stage II Into #188

Keep the tracker smaller by expanding #188 to include true Stage II dual
discovery before the neutral fixture.

Tradeoff:

- Fewer issue objects.
- Makes #188 too broad because fixture admission and phase-discovery algorithm
  adoption are different risks.

### Option C - One HELD Mega-Issue

Create one issue to cover neutral, associating, electrolyte, generalized
multiphase, CE, CPE, registry, and benchmark closure.

Tradeoff:

- Clear top-level theme.
- Too large for one PR and likely to recreate the stale blocked-state problem.

## Next Ready Issue Start Packet

Use this packet when starting #187 after refreshing tracker readiness.

### Preflight

- Confirm GitHub #186 is closed and no live dependency still blocks #187.
- Refresh #187 local mirror and labels if the only blocker was #186.
- Read:
  - `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md`
  - `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate-plan.md`
  - this spec
  - GFPE Stage 8 in
    `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- Keep ownership in `packages/epcsaft-equilibrium/**` unless a public provider
  contract must be referenced explicitly.

### Candidate Files

- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/nlp_problem.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/nlp_problem.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/variable_layout.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/variable_layout.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/variable_transform.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/variable_transform.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/second_order.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/solvers/ipopt_adapter.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/solvers/ipopt_adapter.cpp`
- `packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py`
- `packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py`
- `tests/native/contracts/test_generalized_equilibrium_registry.py`

### First Red Tests To Seek Or Add

- NlpProblem bounds/scaling/objective/gradient/constraint/Jacobian/Hessian size
  contracts.
- Fixed sparse Jacobian and Hessian ordering.
- Failure when sparse structure and value vector sizes diverge.
- Route-owned Ipopt option profile selection.
- Exact-Hessian profile gate diagnostics.
- User-scaling diagnostics with real scale magnitudes and scaled residual norms.
- Active-bound, barrier, regularization, linear-solver, and iteration-history
  diagnostic payload shape.
- Distinction between scaled numerical acceptance and physical postsolve
  certification.

### Completion Criteria For #187

- Shared NLP assembly owns variable layout, constraints, scaling, bounds, and
  diagnostics for neutral GFPE routes.
- Ipopt option handling is package-owned and tested.
- Postsolve payloads preserve enough evidence for later HELD/TPD certification.
- Route admission fails loudly for missing exact derivatives, scaling-contract
  violations, sparse structure/value mismatches, and inadmissible route states.
- The issue does not promote HELD, associating, electrolyte, reactive, CE, CPE,
  benchmark, or public capability claims.

### Proof Oracle Candidates

Run only the slices matching the changed surface:

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py -q
```

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py -q
```

```powershell
uv run python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
```

```powershell
uv run python scripts/dev/validate_project.py docs
```

Use the Stage 9 checker only as a regression receipt after #187 touches route
diagnostics or Ipopt behavior:

```powershell
uv run python scripts/validation/check_phase_discovery.py --json
```

## Issue To Create After This Spec

Create this issue before starting #188, or create it now and mark it blocked by
#187:

```text
Title: M4: promote neutral HELD 1.0 Stage II to replayable dual phase-discovery gate
Milestone: M4 - Equilibrium
Type: Feature
Package: equilibrium
Backend: Ipopt
Readiness: blocked until #187 is closed
Blocks: #188, #189
```

Body outline:

```text
Implement the missing HELD 1.0 adoption gate between #187 and #188: promote
neutral Stage II from the current finite candidate bound audit to a replayable
dual phase-discovery loop with explicit lower/upper bound history, candidate
storage, stopping criteria, and Stage III replay metadata.

Acceptance:
- Stage II reports lower bound, upper bound, bound gap, stopping reason,
  candidate list, rejected candidates, and replay metadata.
- Stage III route refinement consumes Stage II candidate metadata.
- Incomplete continuous TPD starts, open Stage II gaps, tiny-step paths,
  acceptable-level points, feasible-only points, and iteration-limit routes do
  not satisfy the adoption gate.
- Registry and diagnostics distinguish deterministic screening, continuous TPD,
  Stage I, Stage II audit, Stage II dual-loop verification, and Stage III
  refinement.
- No associating, electrolyte, reactive, CE, CPE, public route, or capability
  broadening occurs in this issue.

Proof:
- focused phase-discovery tests;
- registry contract tests for HELD status vocabulary;
- check_phase_discovery.py with route refinement and require-complete;
- docs validation.
```

## Tracker Hygiene Task

Before resolving #187, refresh the M4 tracker state:

- #187 should no longer be blocked by #186 if GitHub dependencies confirm #186
  was the only prerequisite.
- #188 should still be blocked by #187 and by the new Stage II dual-loop issue
  if that issue is created.
- #189 should remain blocked by #188 and the generalized phase-set readiness
  path.
- #145 should be reviewed because #148 is closed, but #145 still has additional
  associating proof prerequisites.
- #190 remains blocked by #145 and exact associating derivative evidence.
- #191 remains blocked by #189 and electrolyte-specific HELD2.0 prerequisites.
- #192 remains blocked by #188/#189/#190/#191 proof evidence.

## Non-Goals

- No source implementation in this spec.
- No new public route exposure from this spec.
- No associating, electrolyte, reactive, CE, or CPE admission from neutral HELD
  evidence.
- No capability or benchmark promotion from closed issue state alone.
- No broad issue closure by documenting remaining work.
- No downstream application metrics, wrappers, or private project behavior.

## Open Questions

- Should the Stage II dual-loop issue be created immediately as blocked by #187,
  or created immediately after #187 lands so its body can cite the final #187
  diagnostics shape?
- Should `single_component_vle` receive a separate capability alignment task in
  #192, or be handled inside the M6 registry closure issue?
- Should #145's stale #148 dependency be cleaned in the same tracker pass as
  #187, or deferred until associating derivative evidence is ready?

## Self-Review

- Placeholder scan: no unresolved placeholders remain.
- Scope check: this is a broad adoption spec, but the execution path is split
  into #187, one new Stage II issue, #188, #189, #145/#190, #191, and #192.
- Ambiguity check: closed issue state is explicitly evidence only, not adoption.
- Capability check: no family or method receives a new production claim from
  this document.
