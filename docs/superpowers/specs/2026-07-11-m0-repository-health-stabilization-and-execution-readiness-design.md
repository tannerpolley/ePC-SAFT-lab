# Repository Health Stabilization And Execution Readiness

Milestone: `M0 - Governance`
Packages: repository-wide coordination; implementation remains owned by `M1`, `M3`, `M4`, `M5`, and `M6`
Status: `approved design basis; specification recorded from the 2026-07-11 repository-health assessment`
Last reviewed: `2026-07-11`

## Context

The repository has recently undergone substantial Git cleanup, Linux migration,
package separation, capability correction, issue/milestone reconciliation, and
scientific-validation triage. Those changes materially improved the project,
but they also exposed a gap between governance health and executable software
health.

The roadmap, package boundaries, local issue mirrors, and capability language
are now much clearer than the implementation state they govern. The provider,
equilibrium, regression, validation, and packaging workstreams each have useful
completed foundations, but they do not yet form one fresh, reproducible,
end-to-end green state. Task 9 is paused, several paper-specific failures are
deliberately deferred, native binaries require fresh-build proof before runtime
conclusions are trusted, and the current source architecture makes further
feature work more expensive than it should be.

This specification converts the repository-health assessment into a durable
execution-readiness contract. It does not add another implementation program.
It defines the order, gates, ownership boundaries, and stopping rules that the
existing milestone-owned specifications and plans must satisfy.

## Snapshot At Design Time

The following facts were observed on `main` at `c00ee92a`:

- the worktree was clean;
- local `main` was three documentation commits ahead of `origin/main`;
- the remaining local branches were `codex/task9-paused` and
  `codex/m4-ce-nonideal-speciation-plots`;
- three stashes were intentionally retained, including the Task 9 deferred
  paper-repair state, an autostash, and reaction-constant-convention drift;
- provider and equilibrium package ownership was governed by ADR 0005;
- public equilibrium admission remained limited to `bubble_pressure`,
  `dew_pressure`, and scoped nonassociating hydrocarbon
  `single_component_vle`;
- Task 9 contained useful typed-input concepts and tests but was not suitable
  for wholesale integration;
- paper-specific validation failures were known and intentionally deferred
  rather than hidden behind invented values or broadened claims;
- the loaded native extension could not be used as a current source/runtime
  oracle without a fresh rebuild because it did not match current source;
- the local issue and milestone graph had recently been reconciled into
  package-owned M0 through M7 workstreams.

These are design-time measurements, not permanent constants. Every execution
plan must refresh them before acting.

## Health Assessment

### What is healthy

- The active package split is explicit: provider in `packages/epcsaft`,
  equilibrium in `packages/epcsaft-equilibrium`, and regression in
  `packages/epcsaft-regression`.
- Git history is preserved, local work is recoverable, and the active worktree
  is not carrying an unidentified dirty payload.
- Capability claims are narrower and more defensible than earlier broad
  declarations.
- Scientific validation now distinguishes executable evidence from inventories,
  diagnostics, and sampled candidates.
- Milestone and issue ownership is much clearer than before the reconciliation.
- Linux is the active development basis, and the old Windows-oriented workflow
  is no longer the intended build path.

### What is not healthy

- There is no single fresh build-and-test receipt proving the present integrated
  source state.
- Provider model input remains multiply serialized and can resolve scientific
  correlations before the owning state conditions exist.
- Equilibrium source accumulated several generations of public, closed,
  experimental, paper-specific, and diagnostic paths in one production
  extension.
- The paused Task 9 architecture materially increases source volume and cannot
  be treated as a ready branch merely because its concepts are directionally
  useful.
- Some validation campaigns depend on paper-specific bundles that are not ready
  for broad re-execution under the new model-input contract.
- The roadmap is denser than the available clean implementation capacity. New
  work must be sequenced by dependency and deletion value, not by issue count.
- Existing large specifications and plans can create the appearance of progress
  without reducing implementation risk unless each accepted slice produces an
  executable result or removes a real owner overlap.

## Goals

1. Establish a stable, reproducible baseline before resuming broad feature
   implementation.
2. Preserve useful local branch and stash work without merging it indiscriminately.
3. Make the provider model-input boundary the first scientific architecture
   prerequisite after baseline proof.
4. Reduce equilibrium to a clear production path for currently admitted
   routes before attempting additional route admission.
5. Keep paper-specific validation repairs independent from provider and solver
   architecture unless an exposed capability directly depends on that paper.
6. Require each milestone to produce its own executable receipt rather than
   relying on an umbrella narrative.
7. Keep Git operations, commits, pushes, and branch cleanup deliberate,
   reviewable, and recoverable.
8. Prevent roadmap work from adding more owners, wrappers, defaults, or
   validation-specific runtime branches.

## Non-Goals

- No provider, equilibrium, regression, paper-validation, packaging, or release
  implementation in this specification.
- No requirement to make every historical paper bundle executable before core
  development resumes.
- No public capability expansion.
- No removal of retained stashes or branches without a separate content review.
- No remote push, publication, pull request, or release action.
- No reinterpretation of a successful local solve as complete scientific
  validation.
- No replacement of milestone-owned specs or plans with one repository-wide
  implementation queue.

## Alternatives

### Resume the original 22-task sequence exactly where it paused

Rejected. The original sequence identified important defects, but its later
steps assume a model-input and equilibrium architecture that the current audit
shows should be simplified first. Continuing mechanically would compound the
existing density.

### Finish all paper-specific failures before architecture work

Rejected. Most paper failures are downstream consumers of the provider and
equilibrium contracts. Repairing each bundle first would repeatedly adapt to an
input boundary that is still changing and would encourage new special cases.

### Merge the paused Task 9 branch, then clean it up afterward

Rejected. The branch contains useful tests and scientific records, but its
provider source changes add thousands of net lines and several new near-
thousand-line owners. Cleanup after integration would make the larger design
the new compatibility constraint.

### Stabilize, simplify foundations, then resume milestone work

Selected. First prove the local baseline, then establish one provider input
owner and one equilibrium production path, then resume regression, validation,
packaging, and later scientific admission work through their owning milestones.

## Selected Design

### Principle 1: evidence before motion

No branch, stash, or planned feature is integrated merely because it represents
substantial effort. Integration requires a clear owner, current source identity,
focused executable proof, and a net reduction in ambiguity.

### Principle 2: foundations before consumers

The dependency order is:

```text
Git and fresh-build baseline
  -> provider model-definition and state-resolution boundary
  -> provider SDK consumer cutover
  -> equilibrium production-path simplification
  -> regression problem correctness
  -> literature/capability evidence refresh
  -> packaging and isolated-install proof
  -> final program closeout
```

Paper-specific repair runs beside this chain only when it does not require a
changing upstream contract. A paper that currently backs an exposed capability
is handled through its explicit M6 dependency, not through an unbounded paper
cleanup campaign.

### Principle 3: one milestone owns each result

| Result | Owning milestone | Required boundary |
| --- | --- | --- |
| Git/process/readiness and structural ratchets | M0 | repository-wide policy and receipt references |
| Linux build and package installation | M1 | artifact and isolated-install receipts |
| Public Python ergonomics | M2 | thin typed interfaces over package-owned native contracts |
| Provider model input and EOS/state correctness | M3 | one state-resolved native model definition |
| Equilibrium selector, NLP, Ipopt, and result correctness | M4 | one production path for admitted routes |
| Regression problem, native optimizer, and persistence | M5 | strict targets and authoritative native execution |
| Literature and capability evidence | M6 | source-backed executable checks and retained artifacts |
| External release/downstream migration | M7 | explicit publication or downstream authorization |

M0 may coordinate dependencies and validate receipts, but it must not absorb
the implementation or scientific decisions of M1, M3, M4, M5, or M6.

## Execution-Readiness Stages

### Stage A: preserve and inventory recoverable work

- Record branch heads, upstream relationships, and stash identities.
- Inspect branch-only commits and classify them as reusable tests, reusable
  scientific data, reusable implementation, obsolete scaffolding, or deferred
  history.
- Do not merge a branch as the unit of reuse when only selected commits or
  files meet the target architecture.
- Keep the worktree clean between classifications.

Exit: every retained branch and stash has an explicit reason to remain.

### Stage B: establish a fresh local baseline

- Build the provider and extension packages from current source on the active
  Linux environment.
- Prove checkout-import isolation where required.
- Record compiler, Python, dependency, native-source, and artifact identities.
- Run the smallest package-owned gates that distinguish source defects from
  stale-binary defects.
- Do not enter paper repair merely because a full collection exposes a known
  deferred paper failure.

Exit: current source can be evaluated without relying on stale native artifacts.

### Stage C: reset Task 9 around a smaller architecture

- Preserve red tests, typed scientific record ideas, and source citations.
- Reject the branch's giant serialization and receipt owners as the cutover
  architecture.
- Require a versioned complete model configuration and state-time resolution.
- Cut consumers over to one provider-owned native definition before deleting
  displaced serializers.

Exit: Task 9 is either complete through the smaller provider boundary or is
explicitly blocked on a named scientific input; no fake default closes it.

### Stage D: simplify equilibrium before expanding it

- Characterize the currently admitted public routes from a fresh build.
- Remove paper-program logic and closed diagnostic bindings from the production
  path.
- Make activation, NLP compilation, Ipopt execution, and result acceptance have
  one owner each.
- Keep neutral LLE, TP flash, electrolyte, reactive, and multiphase families
  closed unless their independent admission specifications pass later.

Exit: the production extension is understandable from the public request to the
typed result without traversing parallel solver or policy engines.

### Stage E: resume milestone-owned correctness and evidence work

- M5 establishes strict target and optimizer semantics.
- M6 refreshes only evidence selected by active capability dependencies.
- M1 proves package combinations and isolated installs after code interfaces
  settle.
- M0 closes the program only by consuming accepted child receipts.

Exit: the repository has a clean, reproducible proof graph and no issue is
closed by documentation alone.

## Git And Branch Policy

- `main` is the integration branch; no remote push occurs without an explicit
  review of the exact commit range.
- Local commits should be focused by milestone and architectural owner.
- A branch is merged only when its complete diff matches the accepted target.
  Otherwise, select commits or reimplement the validated concept under tests.
- Stashes remain recovery artifacts, not hidden dependencies.
- Generated artifacts are committed only when their owning code and source
  identity are stable and the repository contract requires retention.
- Cleanup never deletes unowned ignored files, stashes, branches, or scientific
  evidence.

## Error And Blocker Handling

- A stale native artifact is reported as an environment/source-identity blocker,
  not as a solver defect.
- A missing scientific parameter remains missing; it is not supplied by a
  default or inferred from an unrelated paper.
- A paper bundle that cannot consume the new core contract becomes a deferred
  M6 consumer issue unless it backs a currently exposed route.
- A branch with useful and harmful changes is split by evidence; effort already
  spent is not an integration criterion.
- A failed admission proof leaves the route closed while allowing the owning
  architecture or validation issue to complete with aligned closed state.

## Verification Contract

Every implementation stage derived from this spec must report:

- starting and ending Git identities;
- exact changed paths and owner;
- fresh native-source/build identity when native behavior is tested;
- focused tests for the changed contract;
- broader package tests proportional to risk;
- capability and documentation consistency;
- retained scientific data and plots when model predictions are computed;
- cleanup-hook result and final worktree status;
- explicit deferred failures not caused by the slice.

Passing tests against a stale extension, loose default, private workaround, or
paper-specific production branch do not satisfy this contract.

## Stop Gates

- Stop before integrating Task 9 wholesale.
- Stop before changing public capability state as part of structural cleanup.
- Stop when a proposed fix requires a compatibility wrapper or a second owner.
- Stop when a paper-specific repair would broaden the current slice.
- Stop when native-source identity is unknown for a numerical conclusion.
- Stop before deleting a branch or stash whose unique content has not been
  classified.
- Stop before pushing until the local commit range and focused proof are
  reviewed.

## Risks

- **Roadmap pause appears like lost momentum.** Control: measure progress by
  removed owner overlaps, reproducible receipts, and smaller dependency graphs.
- **Useful paused work is discarded accidentally.** Control: classify tests,
  records, data, and implementation separately before branch cleanup.
- **Structural cleanup changes numerics.** Control: fresh-build characterization
  and before/after receipts for every public route or provider state path.
- **Paper work remains deferred indefinitely.** Control: keep explicit M6 issues
  with source, current failure, and upstream dependency, but do not contaminate
  the core architecture.
- **Governance becomes another oversized layer.** Control: M0 stores schemas,
  dependencies, and receipt references only; package milestones own behavior.

## Unresolved Decisions

No material design decision remains. Exact branch retention, baseline commands,
issue dependencies, and per-file measurements are execution-time facts and must
be refreshed by the relevant plan rather than embedded as permanent policy.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Treat governance and executable health separately | The roadmap is reconciled while fresh integrated proof is still absent | Preserve the governance gains and require milestone-owned runtime receipts | M0 |
| Stabilize before resuming broad implementation | Stale native artifacts and paused Task 9 prevent reliable global conclusions | Establish a fresh Linux baseline first | M1/M0 |
| Do not merge Task 9 wholesale | Its useful concepts are accompanied by substantial new structural density | Salvage tests and scientific records selectively under a smaller design | M3 |
| Keep deferred papers outside core repair | Most paper failures consume rather than define the provider/equilibrium architecture | Track them explicitly under M6 and repair incrementally | M6 |
| Simplify equilibrium before admission work | Current production code contains multiple generations of closed and diagnostic paths | Reduce to the admitted route spine before adding families | M4 |
| Keep implementation milestone-owned | ADR 0005 and the current tracker establish package boundaries | M0 coordinates; M1/M3/M4/M5/M6 implement and prove | All |
| Preserve Git recoverability | Local branches and stashes contain classified and unclassified work | Review unique content before merge, deletion, or push | M0 |
| Accept aligned closed capability states | Maximum capability breadth is not required for repository correctness | A route may remain closed when code, API, docs, tests, and evidence agree | M4/M6 |
