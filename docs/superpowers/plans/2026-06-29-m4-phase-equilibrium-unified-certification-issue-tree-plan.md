# M4 Phase Equilibrium Unified Certification Issue Tree Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers-project:create-issues` with `superpowers:verification-before-completion`.
> Use GitHub native sub-issues and dependencies; this plan changes tracker/docs
> state only and does not authorize solver or paper-validation implementation.

**Goal:** Preserve the existing M4 phase-certification hierarchy and add four
family-specific Task 15 rollup issues under the still-open parents so later
milestone-owned design and implementation work has one current tracking
location.

**Architecture:** Closed #364-#371 and #373-#375 remain immutable historical
tranches. New neutral/electrolyte LLE successors attach to open #363; neutral
multiphase and TP-flash successors attach to open #361. Each successor covers
at most one activation family, but is created as a non-executable rollup with
`status:needs-design`. Before executable work, its design must decompose into
an acyclic sequence of milestone-owned M6 source-readiness, M4 internal
implementation, M6 final-evidence, and M4 activation leaves. Native sub-issue
edges express hierarchy; native `blocked_by` edges separately express parent
completion: #363 is blocked by its two new LLE successors, and #361 is blocked
by its two new PE successors.

**Tech Stack:** GitHub Issues native issue types, milestones, sub-issues and
dependencies; `gh` REST/GraphQL; repository issue mirrors; M4 activation and
capability contracts; pytest mirror validators.

## Global Constraints

- Assign every new issue exactly to `M4 - Equilibrium` with native type
  `Feature` and matching `type:feature` compatibility label.
- Use #363 as parent for neutral LLE and electrolyte LLE successors; use #361
  as parent for neutral multiphase and neutral TP flash successors.
- Attach each successor as both a native sub-issue and a native completion
  blocker of its open parent: the successor issue blocks #363 or #361. Never
  add the inverse dependency from a successor to its parent.
- Preserve existing #363 `blocked_by` #372 and #361 `blocked_by` #363/#376
  edges. The four additions are acyclic because no successor depends on its
  tracking parent.
- Do not reopen closed #364, #370, or #374 and do not attach new work beneath a
  closed governance parent.
- Keep #330 as the only standalone `reactive_speciation` admission issue.
- Keep #331, #372, and #376 as the existing reactive/coupled future work.
- Do not batch-admit siblings: a passing family gives no evidence for another.
- Phase-discovery completeness is always scoped to the declared route,
  thermodynamic state/domain, phase-kind domain, model-input fingerprint,
  search domain, algorithm, starts, tolerances, and termination proof.
- A finite sampled candidate set never establishes a global phase set.
- Every new rollup is created with `status:needs-design`, no `agent-ready`, and
  no claim that it is executable. A concrete M3 typed-input dependency may be
  attached when its live issue number and applicability are already proven.
- Do not attach an unidentified M6 blocker or invent an M6 source, threshold,
  fixture, or evidence issue during rollup publication.
- Before executable admission work, each rollup must be decomposed into an
  acyclic staged graph: M6 source readiness -> M4 internal implementation ->
  M6 final evidence -> M4 activation. Every leaf keeps its owning milestone.
- No GitHub mutation occurs without the root workflow's artifact review and
  publication approval.

---

## Source Evidence

- Source spec:
  `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`.
- Live open parents: #361 Phase Equilibrium and #363 LLE family.
- Closed shared contract #362 is reusable foundation evidence.
- Closed historical children: #364-#371 and #373-#375.
- Existing future issues: #330 standalone CE, #331 CPE interface, #372
  reactive electrolyte LLE, and #376 reactive/coupled PE.
- Current public routes remain `bubble_pressure`, `dew_pressure`, and scoped
  nonassociating hydrocarbon `single_component_vle`.

## Existing Hierarchy Record

The original hierarchy remains valid historical state:

1. #361 Phase Equilibrium parent (open).
2. #362 shared production-route certification leaf (closed).
3. #363 LLE broad parent (open).
4. #364-#369 neutral/associating LLE governance and evidence (closed).
5. #370-#371 electrolyte LLE governance/residual integration (closed).
6. #372 reactive electrolyte LLE boundary (open).
7. #373 VLE parent (closed).
8. #374 flash/multiphase parent (closed).
9. #375 boundary parent (closed).
10. #376 reactive/coupled PE parent (open).
11. #191 retained electrolyte history (closed).
12. #331 CPE interface remains in the reactive/coupled subtree (open).

## Planned Successor Rollups

| Stable title | Parent | Parent dependency | Activation family | Future design decomposition |
| --- | ---: | --- | --- | --- |
| `M4 LLE: re-admit neutral LLE only after scoped phase-discovery proof` | #363 | successor blocks #363 | `neutral_lle` | Later design creates M6 source-readiness, M4 internal-route, M6 final-evidence, and M4 activation leaves |
| `M4 LLE: re-admit electrolyte LLE only after scoped charge-neutral proof` | #363 | successor blocks #363 | `electrolyte_lle` | Later design creates M6 source-readiness, M4 reduced-electroneutral-route, M6 final-evidence, and M4 activation leaves |
| `M4 PE: admit neutral multiphase only after scoped phase-set discovery` | #361 | successor blocks #361 | `neutral_multiphase` | Later design creates M6 source-readiness, M4 scoped-discovery/refinement, M6 final-evidence, and M4 activation leaves |
| `M4 PE: admit neutral TP flash only after live source-backed proof` | #361 | successor blocks #361 | `neutral_tp_flash` | Later design creates M6 source-readiness, M4 selector/refinement, M6 final-evidence, and M4 activation leaves |

## Test Complete And Metrics

- GitHub contains exactly one open issue with each stable title.
- Each issue has milestone M4, native type Feature, matching type label, one
  expected parent, one parent-completion `blocking` edge, and no parent under a
  closed issue.
- Each issue body names one activation family, one source spec/plan, explicit
  non-goals, the finite-candidate limitation, `status:needs-design`, and the
  required future four-stage decomposition without pretending its source or
  thresholds are selected.
- A native M3 `blocked_by` edge exists only when a concrete, applicable live
  typed-input issue is already known. No M6 dependency is required at rollup
  publication.
- Native dependency queries show #363 `blocked_by` both new LLE successors and
  #361 `blocked_by` both new PE successors, while none of the four successors
  is `blocked_by` its parent.
- Local mirrors match GitHub titles, milestone, type, parent, optional concrete
  M3 dependency, and non-executable design status.
- Current activation rows and public capabilities remain unchanged after
  tracker publication.

## Outcome Proof

**Intent:** Turn Task 15 from one incoherent batch-admission request into four
separately governed family outcomes while preserving the existing CE and
reactive issue chains.

**Current Behavior:** The live hierarchy has open broad parents and useful
closed governance history, but no current successor issue owns neutral LLE,
electrolyte LLE, neutral multiphase, or neutral TP-flash re-admission after the
validation-correctness reconciliation.

**Expected Outcome:** Four non-executable M4 rollups appear under the correct
open parents with `status:needs-design`, each open parent is natively blocked
by its direct successors, each successor may have an optional concrete M3 edge,
and the future-decomposition rule stays acyclic while no capability claim
changes.

**Target Output:** Four GitHub Feature rollups, native sub-issue relationships,
four successor-to-parent completion-blocking relationships, optional concrete
M3 dependency relationships, four validated local mirrors, updated M4
milestone table, and an unchanged activation/capability snapshot.

**Owner:** M4 owns the rollups and eventual internal/activation leaves; M3 owns
typed model input; future M6 issues own source readiness and final evidence
only after their own design defines exact scope; the root orchestrator owns
GitHub mutation and mirror integration.

**Interface:** GitHub issue/sub-issue/dependency APIs, M4 issue mirrors,
`docs/superpowers/milestones/M4-equilibrium/README.md`, activation generator,
and capability contract tests.

**Cutover:** These four successors become the only active Task 15 admission
owners for their families. Closed governance parents remain historical and are
not reopened or used as implied proof.

**Replaced Path:** One batch Task 15 issue, new children under closed #364/#370/
#374, title-encoded blocker prefixes, prose-only dependencies, and sibling
capability inference are displaced.

**Evidence:** GitHub API query receipts, parent/dependency graphs, issue bodies,
mirror-validator output, milestone README diff, activation generation check,
and focused capability tests.

**Acceptance Proof:** The four rollups are uniquely present under #363/#361,
carry correct M4 metadata and `status:needs-design`, block completion of their
respective parents without inverse parent dependencies, state the acyclic
future decomposition, contain no invented M6 evidence contract, leave all
affected activation rows closed, and have validated mirrors.

**Stop Criteria:** Stop before mutation if a duplicate title exists, a proposed
M3 dependency is not concrete/applicable, the body invents M6 evidence scope,
the GitHub token cannot create native sub-issues/dependencies, a proposed
parent edge would create a cycle, or publication approval has not been
obtained.

**Avoid:** Do not reopen closed issues, mark design rollups agent-ready, create
an M9 milestone, put several activation families in one issue, pre-create
unscoped M6 work, or treat finite candidate replay as global certification.

**Risk:** GitHub relationship APIs may accept issue creation but fail during
sub-issue/dependency attachment. Retain created issue numbers, report the exact
missing edge, and do not misstate the hierarchy as complete.

## Implementation Boundaries

**Files To Create:** Four issue mirrors under `docs/superpowers/issues/` using
the issue numbers returned by GitHub.

**Files To Modify:** This plan if GitHub IDs require recording,
`docs/superpowers/milestones/M4-equilibrium/README.md`, and the umbrella
roadmap task mapping.

**Files To Avoid:** Package/native source, activation rows, scientific data or
plots, closed issue mirrors except link-only references, release metadata, and
other milestone issue bodies.

**Source Of Truth:** GitHub live issue state for tracker relationships; the
source spec for scientific scope; the native activation/capability contract for
current route state.

**Read Path:** Source spec -> live parent/duplicate/dependency audit -> dry issue
packet -> publication approval -> GitHub issue -> sub-issue/dependency graph ->
local mirror/table.

**Write Path:** Create one rollup, attach one parent, add the successor as a
completion blocker of that parent, add only a proven concrete M3 blocker to the
successor when applicable, verify live metadata, write/validate its mirror,
then proceed to the next family.

**Integration Points:** #361, #363, an applicable concrete M3 typed-input
tracker, future milestone-owned M6/M4 leaves, GitHub native relationships, M4
milestone README, activation generator, and capability tests.

**Migration Or Cutover:** Add successors without modifying closed history.
Update umbrella Task 15 mapping to the four new issue numbers after all
relationships verify.

**Replaced Path Handling:** Do not delete historical mirrors; add explicit
successor links only where a live reader would otherwise follow a closed issue
as current work.

**Acceptance Proof Gate:** Publication is complete only after all four live
rollups, sub-issue parents, successor-to-parent completion blockers, optional
concrete M3 dependencies, mirrors, milestone rows, activation checks, diff,
and cleanup verify.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Use open parents | #364/#370/#374 are closed while #361/#363 remain open | Attach successors to #363 or #361 | M4 |
| Split by family | Variables, derivatives, discovery, and evidence differ | Four independent activation-family issues | M4 |
| Preserve #330 | Standalone CE is not phase splitting | #330 remains sole CE admission | M4 |
| Preserve reactive tree | #331/#372/#376 already govern coupled work | No duplicate reactive successor | M4 |
| Scope completeness | Finite candidates do not prove all phases globally | Require declared domain/search receipt in each body | M4/M6 |
| Defer M6 leaf scope | No family-specific source/threshold design is approved in this tracker action | Create no M6 issue or edge now | Future M6 design owner |
| Preserve acyclic order | Source readiness, implementation, evidence, and activation have different owners | Require M6 -> M4 -> M6 -> M4 staged leaves before execution | M4/M6 |
| Use concrete blockers only | Repo tracker policy makes dependencies authoritative | Attach an M3 issue only when live and applicable | Root orchestrator |
| Make parent completion explicit | Sub-issue hierarchy does not drive dependency readiness | Each successor blocks its open parent; no successor is blocked by its parent | Root orchestrator |

### Task 1: Audit The Live Graph And Prove The RED State

**Use Cases:**

- Duplicate or wrongly parented successor work is detected before publication.
- The dry graph proves the four missing rollups and preserves the completed
  historical tree.

**Files:**

- Modify only after publication: this plan's issue-number record and the M4
  milestone README

**Interfaces:**

- Consumes `gh issue list/view` and `/issues/<parent>/sub_issues`.
- Produces a dry packet with title, body, milestone, type, labels, parent,
  parent-completion blocking edge, `status:needs-design`, optional concrete M3
  dependency, and future staged decomposition rule for all four rollups.

- [ ] **Step 1: Query titles, parents, and existing concrete M3 work.** Confirm no open or
  closed issue already owns an equivalent successor and record #361/#363 live
  state.

- [ ] **Step 2: Verify RED.** Run sub-issue and `blocked_by` queries for #361
  and #363. Expected: none of the four stable titles appears as a child or
  parent blocker.

- [ ] **Step 3: Render the four complete issue bodies and obtain root
  publication approval.** Bodies must include the family-specific acceptance
  rows below, scoped-completeness language, current closed state, and non-goals.

- [ ] **Step 4: Checkpoint commit.** The dry packet/spec/plan documentation may
  be committed as `docs(equilibrium): plan Task 15 successor rollups`; no issue
  number is invented before GitHub returns it.

### Task 2: Create The Neutral LLE Successor Under #363

**Use Cases:**

- Neutral LLE has one current admission owner instead of relying on closed
  sampled-evidence issues.
- Its proof visibly replaces finite-candidate inference with declared-scope
  discovery and canonical selector/result evidence.

**Files:**

- Create after GitHub returns the number:
  `docs/superpowers/issues/2026-07-10-m4-equilibrium-issue-${ISSUE_NUMBER}-re-admit-neutral-lle-after-scoped-phase-discovery.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

**Interfaces:**

- Produces one non-executable M4 Feature rollup under #363 for activation
  family `neutral_lle`, labeled `status:needs-design` without `agent-ready`.
- Produces one native dependency in which this successor blocks #363; #363
  does not block the successor.
- Records the future acyclic decomposition M6 source readiness -> M4 internal
  implementation -> M6 final evidence -> M4 activation; it does not select the
  M6 source, thresholds, or fixture now.

- [ ] **Step 1: Create the rollup from the approved packet.** Apply M4 milestone,
  Feature type, matching labels, and `status:needs-design`.

- [ ] **Step 2: Attach hierarchy and completion dependencies.** Attach the
  successor to #363 as a sub-issue, then add the successor as a `blocked_by`
  dependency of #363. Add only a concrete M3 blocker to the successor if
  applicable; add no M6 issue or dependency now and do not use closed
  #364-#366 as blockers.

- [ ] **Step 3: Verify GREEN and write the mirror.** Query live metadata/edges,
  write the returned-number mirror, validate it, and confirm the activation row
  remains closed.

- [ ] **Step 4: Checkpoint commit.** Commit
  `docs(equilibrium): track neutral LLE re-admission`.

### Task 3: Create The Electrolyte LLE Successor Under #363

**Use Cases:**

- Electrolyte LLE has a current charge-neutral admission owner while closed
  #191/#314/#343/#350/#370/#371 remain history.
- The issue requires real typed electrolyte input and a retained literature/
  model plot before any activation change.

**Files:**

- Create after GitHub returns the number:
  `docs/superpowers/issues/2026-07-10-m4-equilibrium-issue-${ISSUE_NUMBER}-re-admit-electrolyte-lle-after-scoped-charge-neutral-proof.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

**Interfaces:**

- Produces one non-executable M4 Feature rollup under #363 for
  `electrolyte_lle`, labeled `status:needs-design` without `agent-ready`.
- Produces one native dependency in which this successor blocks #363; #363
  does not block the successor.
- Records the same milestone-owned four-stage future decomposition while
  leaving exact electrolyte sources, thresholds, and evidence scope to its
  later design.

- [ ] **Step 1: Create the rollup from the approved packet.** Preserve
  `status:needs-design` and closed current capability.

- [ ] **Step 2: Attach hierarchy and completion dependencies.** Attach the
  successor to #363 as a sub-issue, then add the successor as a `blocked_by`
  dependency of #363. Add only a concrete M3 blocker to the successor if
  applicable and no M6 issue or edge now. Historical closed issues are links,
  not proof of the successor outcome.

- [ ] **Step 3: Verify GREEN and write the mirror.** Validate live metadata,
  graph, mirror, and unchanged activation/capability state.

- [ ] **Step 4: Checkpoint commit.** Commit
  `docs(equilibrium): track electrolyte LLE re-admission`.

### Task 4: Create The Neutral Multiphase Successor Under #361

**Use Cases:**

- Multiphase admission is governed independently of TP flash and cannot reuse
  finite sampled-candidate diagnostics as a global claim.
- The issue replaces closed #374 as current work while retaining its historical
  contract evidence.

**Files:**

- Create after GitHub returns the number:
  `docs/superpowers/issues/2026-07-10-m4-equilibrium-issue-${ISSUE_NUMBER}-admit-neutral-multiphase-after-scoped-phase-set-discovery.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

**Interfaces:**

- Produces one non-executable M4 Feature rollup under #361 for
  `neutral_multiphase`, labeled `status:needs-design` without `agent-ready`.
- Produces one native dependency in which this successor blocks #361; #361
  does not block the successor.
- Requires later design to define the declared phase-kind/state/search domain
  and the four-stage M6/M4/M6/M4 graph; no source or threshold is selected now.

- [ ] **Step 1: Create, parent, and attach the completion dependency.** Use
  #361, not closed #374, apply `status:needs-design`, attach the successor as a
  #361 sub-issue, and add the successor as a `blocked_by` dependency of #361.

- [ ] **Step 2: Add no unidentified source blocker.** Attach only a concrete
  applicable M3 dependency. Keep sampled finite records internal and state
  `global_phase_set_certified=false` unless mathematical global proof exists.

- [ ] **Step 3: Verify GREEN and write the mirror.** Validate metadata, graph,
  mirror, and closed activation state.

- [ ] **Step 4: Checkpoint commit.** Commit
  `docs(equilibrium): track neutral multiphase admission`.

### Task 5: Create The Neutral TP-Flash Successor Under #361

**Use Cases:**

- Neutral TP flash receives its own live source-backed route gate instead of
  sharing multiphase or inverse-workbook evidence.
- The rollup replaces prose-only future work with a governed design home.

**Files:**

- Create after GitHub returns the number:
  `docs/superpowers/issues/2026-07-10-m4-equilibrium-issue-${ISSUE_NUMBER}-admit-neutral-tp-flash-after-live-source-proof.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

**Interfaces:**

- Produces one non-executable M4 Feature rollup under #361 for
  `neutral_tp_flash`, labeled `status:needs-design` without `agent-ready`.
- Produces one native dependency in which this successor blocks #361; #361
  does not block the successor.
- Requires later design to create the four-stage milestone-owned graph; the
  live source fixture and numerical thresholds are deliberately not chosen in
  this publication task.

- [ ] **Step 1: Create, parent, and attach the completion dependency.** Use
  #361, apply `status:needs-design`, attach the successor as a #361 sub-issue,
  add the successor as a `blocked_by` dependency of #361, and preserve the
  closed route.

- [ ] **Step 2: Add no unidentified source blocker.** Attach only a concrete
  applicable M3 dependency. Workbook or inverse-consistency rows remain
  historical context, not a selected M6 evidence contract.

- [ ] **Step 3: Verify GREEN and write the mirror.** Validate metadata, graph,
  mirror, and unchanged route set.

- [ ] **Step 4: Checkpoint commit.** Commit
  `docs(equilibrium): track neutral TP flash admission`.

### Task 6: Reconcile The Roadmap And Prove No Capability Mutation

**Use Cases:**

- The M4 dashboard and umbrella Task 15 mapping point to the four current
  successors, replacing closed-parent ambiguity.
- Tracker publication has executable evidence and cannot be mistaken for route
  implementation or admission.

**Files:**

- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/specs/2026-07-10-m0-validation-correctness-tasks-9-22-roadmap-reconciliation.md`
- Modify: this plan with returned issue numbers

**Interfaces:**

- Consumes all four verified live issue IDs/graphs.
- Produces current roadmap links while activation and capability output remain
  byte-equivalent to the pre-publication snapshot.

- [ ] **Step 1: Update dashboard and Task 15 mapping.** Record each issue
  number, parent, milestone, blocked readiness, and evidence owner.

- [ ] **Step 2: Validate mirrors and hierarchy.** Run the mirror validator for
  all four files and query #361/#363 sub-issues plus every `blocked_by` edge.
  Require #363 to be blocked by both LLE successors and #361 to be blocked by
  both PE successors, with no inverse parent dependency on a successor.

- [ ] **Step 3: Verify capability GREEN.** Run activation generation check and
  focused capability tests. Expected: no new public route or proof route.

- [ ] **Step 4: Checkpoint commit.** Commit
  `docs(equilibrium): reconcile Task 15 issue hierarchy`.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
gh api /repos/ePC-SAFT/ePC-SAFT/issues/361/sub_issues
gh api /repos/ePC-SAFT/ePC-SAFT/issues/363/sub_issues
gh api /repos/ePC-SAFT/ePC-SAFT/issues/361/dependencies/blocked_by
gh api /repos/ePC-SAFT/ePC-SAFT/issues/363/dependencies/blocked_by
titles=(
  "M4 LLE: re-admit neutral LLE only after scoped phase-discovery proof"
  "M4 LLE: re-admit electrolyte LLE only after scoped charge-neutral proof"
  "M4 PE: admit neutral multiphase only after scoped phase-set discovery"
  "M4 PE: admit neutral TP flash only after live source-backed proof"
)
for title in "${titles[@]}"; do
  issue_number="$(gh issue list --state all --limit 500 --search "${title} in:title" --json number,title --jq ".[] | select(.title == \"${title}\") | .number")"
  test -n "$issue_number"
  gh api "/repos/ePC-SAFT/ePC-SAFT/issues/${issue_number}/dependencies/blocked_by"
  gh api "/repos/ePC-SAFT/ePC-SAFT/issues/${issue_number}/dependencies/blocking"
  mirror="$(rg -l "issues/${issue_number}" docs/superpowers/issues | head -n 1)"
  test -n "$mirror"
  uv run --no-sync python scripts/validate_issue_mirror.py --repo-root . --issue-file "$mirror" --milestone-required
done
uv run --no-sync python scripts/docs/generate_equilibrium_activation.py --check
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/contracts/test_phase_equilibrium_certification_contract.py -q
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

The loop resolves returned issue numbers and mirror paths from the four stable
titles; it does not invent planning IDs.
