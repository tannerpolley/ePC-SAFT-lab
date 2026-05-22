# Association Derivative Goal Roadmap

## Purpose

This is the controlling management and tracking document for the
association-derivative issue set after the public equilibrium contract cleanup
and the first activation-driven neutral TP flash compiler slice.

Use this document before starting any work on GitHub issues #132 through #140.
It defines the dependency order, agent-sized goal grouping, guardrails, and
status tracking for the full association-derivative tranche.

Do not create a parallel roadmap, handoff, or planning ledger for this issue set
unless it links back here and leaves this document as the source of truth. If an
issue body and this roadmap disagree, treat the issue body as the acceptance
source, update this document in the same branch, and call out the discrepancy in
the PR or handoff.

## How Agents Should Use This Document

For each goal branch, use this file as the workboard:

1. Verify the live GitHub issue state before editing.
2. Read the target issue body and any blocking issue bodies.
3. Record the goal number, issue numbers, branch, production workflow, and
   validation commands in the PR or handoff.
4. Update the status ledger in this file when the branch changes the state of a
   goal.
5. Do not mark an issue complete here unless the GitHub issue is closed or the
   merged PR explicitly closes it.

Status meanings:

- `Open`: GitHub issue is still open; work may exist locally but is not done.
- `In progress`: a branch or PR is actively working the goal.
- `Review`: implementation is ready for review but not merged.
- `Closed`: GitHub issue is closed by merged work matching acceptance criteria.
- `Blocked`: next action needs a specific upstream issue, decision, or failing
  validation result resolved first.

Local commits, unmerged branches, and draft PRs are evidence, not closure.
Agents must not collapse `In progress` into `Closed`.

## Current Tracker State

As of 2026-05-22:

- #130 is closed: public equilibrium contract alignment and stale backend-option cleanup.
- #131 is closed: neutral TP flash through `ActivationPlan` and `ActivatedEquilibriumNlp`.
- #132 through #140 are open and form the association-derivative tranche.

Future agents must verify live tracker state before implementation:

```powershell
gh issue view 130 --repo tannerpolley/ePC-SAFT
gh issue view 131 --repo tannerpolley/ePC-SAFT
gh issue list --repo tannerpolley/ePC-SAFT --state open --limit 40
```

## Global Policy

These rules apply to every issue in this roadmap:

- Do not direct-tape the association fixed-point iteration with CppAD.
- Do not add non-exact production derivative backends.
- Do not expose associating equilibrium.
- Do not broaden public equilibrium routes.
- Do not treat target-kind registry presence as production optimizer support.
- Do not add SLE, precipitation, Ksp, solid diagnostics, electrolyte LLE, or reactive LLE work in this tranche.
- Do not claim regression support for `e_assoc`, `vol_a`, `k_hb_ij`, or active-association `l_ij` without derivative evidence and optimizer evidence.

The governing derivative model for State and Regression is:

```text
F(X_A, q) = 0
dX_A/dq = -F_XA^-1 F_q
d(output)/dq = output_q + output_XA dX_A/dq
```

`X_A` is a solved internal variable. Production code should use explicit
partials plus implicit sensitivities, not differentiation through the fixed-point
iteration.

## Evidence Classifications

- verified: #130 and #131 are closed, #132 through #140 are open, and their issue bodies contain the dependencies and acceptance criteria referenced here.
- verified: current roadmap policy requires association solved-state implicit sensitivities and forbids direct differentiation through iterative loops.
- inference: the six-goal grouping below is a coordination layer over the existing issues; it does not replace the issue bodies.
- assumption: issue numbers and titles remain stable after this document is written. Re-check GitHub before starting work.

## Issue Map

| Issue | Title | Primary Category | Blocks / Feeds |
| --- | --- | --- | --- |
| #132 | Harden association site-fraction solve and require convergence diagnostics | State solved-state reliability | #133, #134, #136, #137, #140 |
| #133 | Normalize active-association derivative option semantics to implicit, not plain CppAD | Public/runtime derivative semantics | #134, #136, #137, #140 |
| #134 | Add generic implicit-sensitivity helper for solved association site fractions | Native derivative infrastructure | #136, #137, #139, #140 |
| #135 | Gate regression capability claims on implemented association derivative and optimizer support | Regression capability evidence | #136, #137 and final capability claims |
| #136 | Implement implicit association parameter sensitivities for `e_assoc` and `vol_a` | Pure association parameter derivatives | #137, capability updates |
| #137 | Implement implicit association parameter sensitivities for `k_hb_ij` and `l_ij` | Binary association parameter derivatives | capability updates |
| #138 | Document associating-equilibrium architecture choice before exposing any associating Ipopt route | Equilibrium architecture | #139 |
| #139 | Repair lifted association variable block for future Ipopt use without production exposure | Equilibrium block readiness | future associating equilibrium work, not public exposure |
| #140 | Add associating-State derivative finite-check and cross-check suite | Validation | shared validation across #132, #133, #134, #136, #137 |

## Recommended Goal Grouping

Use six fresh-agent goals. This keeps each goal vertical enough to be useful while
keeping math, capability governance, and equilibrium internals separated.

### Goal 1: Association Solved-State Reliability

Issues:

- #132
- #133
- first slice of #140

Category:

- State solved-state reliability
- public/runtime derivative semantics
- validation

Branch:

```text
codex/association-solved-state-reliability
```

Goal:

Make solved association site fractions trustworthy before any broader derivative
or regression expansion.

Required outcome:

- `X_A` nonconvergence cannot silently return a final iterate.
- association solve diagnostics exist and are checked before derivative use.
- active-association public/runtime options do not imply direct CppAD through the fixed-point solve.
- active-association State paths report implicit backend semantics.
- the first #140 validation checks prove direct CppAD association recording still raises and active association derivative payloads are finite.

Files to inspect:

- `src/epcsaft/native/eos/contributions/association.cpp`
- `src/epcsaft/native/eos/residual_helmholtz.cpp`
- `src/epcsaft/model/options.py`
- `src/epcsaft/state/native_adapter.py`
- `tests/native/contracts/test_association_implicit_derivative_contract.py`
- `tests/native/state/test_eos_contributions.py`
- `tests/native/state/test_phase_state_sensitivities.py`
- `tests/api/frontend/test_state_properties.py`

Focused validation:

```powershell
uv run python run_pytest.py tests/native/contracts/test_association_implicit_derivative_contract.py tests/native/state/test_eos_contributions.py tests/native/state/test_phase_state_sensitivities.py tests/api/frontend/test_state_properties.py -q
```

Definition of done:

- #132 acceptance criteria are met.
- #133 acceptance criteria are met.
- the #140 checks relevant to existing State backend labels and direct-CppAD guards are present.
- no new parameter sensitivities are added.
- no public equilibrium behavior changes.

### Goal 2: Generic Association Implicit-Sensitivity Helper

Issues:

- #134
- helper/parity slice of #140

Category:

- native derivative infrastructure
- reusable implicit sensitivity machinery

Branch:

```text
codex/association-implicit-sensitivity-helper
```

Goal:

Extract or introduce reusable helper machinery for solved association
site-fraction implicit sensitivities, without adding new parameter families yet.

Required outcome:

- common helper covers the current `F(X_A, q) = 0` sensitivity pattern.
- current State association derivative routes can be routed through the helper or parity-tested against it.
- helper failures honor association solve diagnostics from Goal 1.
- helper preserves explicit backend labels such as `analytic_implicit`, `cppad_implicit`, and `cppad_implicit_association`.

Files to inspect:

- `src/epcsaft/native/eos/contributions/association.cpp`
- `src/epcsaft/native/eos/residual_helmholtz.cpp`
- `src/epcsaft/native/eos/core_internal.h`
- `src/epcsaft/native/autodiff/`
- `tests/native/contracts/test_association_implicit_derivative_contract.py`
- `tests/native/state/test_phase_state_sensitivities.py`
- `tests/native/equilibrium/blocks/test_eos_phase_block.py`

Focused validation:

```powershell
uv run python run_pytest.py tests/native/contracts/test_association_implicit_derivative_contract.py tests/native/state/test_phase_state_sensitivities.py tests/native/equilibrium/blocks/test_eos_phase_block.py -q
```

Definition of done:

- #134 acceptance criteria are met.
- helper parity tests are in place.
- no `e_assoc`, `vol_a`, `k_hb_ij`, or active-association `l_ij` sensitivity expansion is added.
- no non-exact production derivative path appears.

### Goal 3: Regression Capability Firewall

Issues:

- #135 baseline

Category:

- regression capability evidence
- no-overclaim governance
- documentation and validation

Branch:

```text
codex/regression-capability-firewall
```

Goal:

Make capability output and algorithms documentation distinguish target-kind
registry presence from derivative support, optimizer support, and public
production support.

Required outcome:

- capability evidence distinguishes:
  - `registry_known_target_kind`
  - `derivative_supported_target_kind`
  - `optimizer_supported_target_kind`
  - `public_production_supported_target_kind`
- association-affecting parameters remain non-production until derivative and optimizer tests exist.
- tests fail if a target family is marked production without evidence.

Files to inspect:

- `src/epcsaft/regression/core.py`
- `src/epcsaft/runtime/capability_evidence.py`
- `src/epcsaft/runtime/core.py`
- `docs/algorithms.md`
- `docs/algorithms_registry.yaml`
- `tests/native/contracts/`
- `tests/native/regression/`
- `tests/api/regression/`

Focused validation:

```powershell
uv run python run_pytest.py tests/native/contracts tests/api/regression -q
```

Definition of done:

- #135 baseline acceptance criteria are met.
- current production claims remain narrow.
- no derivative formulas or optimizer support are added.
- the issue notes or PR body state that #135 must be revisited after #136 and #137 land.

### Goal 4: Pure Association Parameter Sensitivities

Issues:

- #136
- #135 update for proven derivative support

Category:

- pure association parameter derivatives
- State/property parameter derivatives
- capability evidence update

Branch:

```text
codex/association-pure-parameter-sensitivities
```

Goal:

Add implicit sensitivities for pure association-affecting parameters
`e_assoc` and `vol_a`, then update capability evidence only for proven support.

Required outcome:

- `e_assoc` derivative result exists and reports an implicit backend.
- `vol_a` derivative result exists and reports an implicit backend.
- result payload preserves parameter order and component order.
- solved `X_A` diagnostics are checked before derivative use.
- capability evidence distinguishes derivative support from optimizer support.

Files to inspect:

- `src/epcsaft/native/eos/contributions/association.cpp`
- `src/epcsaft/native/eos/residual_helmholtz.cpp`
- `src/epcsaft/native/bindings/module.cpp`
- `src/epcsaft/state/native_adapter.py`
- `src/epcsaft/regression/core.py`
- `src/epcsaft/runtime/capability_evidence.py`
- `docs/algorithms.md`
- `tests/native/state/test_phase_state_sensitivities.py`
- `tests/native/contracts/test_association_implicit_derivative_contract.py`
- `tests/native/regression/`

Focused validation:

```powershell
uv run python run_pytest.py tests/native/state/test_phase_state_sensitivities.py tests/native/contracts/test_association_implicit_derivative_contract.py -q
```

Definition of done:

- #136 acceptance criteria are met.
- #135 capability evidence is updated only as far as the new evidence supports.
- no `k_hb_ij` or active-association `l_ij` sensitivity work is bundled.
- no Ceres optimizer claim is made unless optimizer tests are included.

### Goal 5: Binary Association Parameter Sensitivities

Issues:

- #137
- #135 update for proven derivative support

Category:

- binary association parameter derivatives
- regression readiness
- capability evidence update

Branch:

```text
codex/association-binary-parameter-sensitivities
```

Goal:

Add implicit sensitivities for binary association-relevant parameters `k_hb_ij`
and active-association `l_ij`, preserving current nonassociating `k_ij` and
`l_ij` behavior.

Required outcome:

- `k_hb_ij` derivative result exists and reports an implicit backend.
- active-association `l_ij` derivative result exists and reports an implicit backend.
- nonassociating `k_ij` and `l_ij` behavior is unchanged.
- existing binary `k_ij` tests still pass.
- capability evidence is updated only for proven support.

Files to inspect:

- `src/epcsaft/native/model/parameter_setup.cpp`
- `src/epcsaft/native/eos/contributions/association.cpp`
- `src/epcsaft/native/eos/residual_helmholtz.cpp`
- `src/epcsaft/native/bindings/module.cpp`
- `src/epcsaft/state/native_adapter.py`
- `src/epcsaft/regression/core.py`
- `src/epcsaft/runtime/capability_evidence.py`
- `docs/algorithms.md`
- `tests/native/state/test_phase_state_sensitivities.py`
- `tests/native/regression/`

Focused validation:

```powershell
uv run python run_pytest.py tests/native/state/test_phase_state_sensitivities.py tests/native/regression/test_binary.py -q
```

Definition of done:

- #137 acceptance criteria are met.
- #135 capability evidence is updated only as far as the new evidence supports.
- no public associating equilibrium support is exposed.
- no full binary Ceres optimizer support is claimed unless optimizer tests are included.

### Goal 6: Associating-Equilibrium Architecture And Lifted Block Readiness

Issues:

- #138
- #139

Category:

- equilibrium architecture
- non-production lifted association block readiness
- Ipopt exact-Hessian preparation

Branch:

```text
codex/associating-equilibrium-block-readiness
```

Goal:

Document the associating-equilibrium architecture choice and repair the lifted
`X_A` phase-system block as a future internal building block, without exposing
associating equilibrium.

Required outcome:

- ADR or design document states:
  - State and Regression eliminate `X_A` and differentiate implicitly.
  - current production Equilibrium remains nonassociating.
  - future associating Equilibrium must use either complete implicit second-order closure or lifted `X_A` variables with exact mass-action constraints and exact Lagrangian Hessian support.
- lifted block uses true site count, not species count.
- lifted block carries `site_component_index`.
- association objective weighting follows owning component amount.
- delta terms are recomputed from current phase state or explicitly modeled as differentiated dependencies with a clear contract.
- mass-action Jacobian and Hessian rows are populated and tested.
- production selector still rejects active association.

Files to inspect:

- `docs/adr/`
- `docs/pages/equilibrium_architecture.rst`
- `src/epcsaft/native/equilibrium/blocks/eos_phase_block.cpp`
- `src/epcsaft/native/equilibrium/blocks/association_block.cpp`
- `src/epcsaft/native/eos/contributions/association.cpp`
- `src/epcsaft/native/model/parameter_setup.cpp`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `tests/native/equilibrium/blocks/test_eos_phase_block.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`

Focused validation:

```powershell
uv run python run_pytest.py tests/native/equilibrium/blocks/test_eos_phase_block.py tests/native/equilibrium/diagnostics/test_selector_core_contracts.py -q
uv run python scripts/dev/validate_project.py docs
```

Definition of done:

- #138 acceptance criteria are met.
- #139 acceptance criteria are met.
- associating mixtures remain rejected by production public equilibrium selector routes.
- no public Python route or backend control is added.

## Parallelization Plan

Use waves to avoid dependency collisions:

| Wave | Goals | Parallel? | Notes |
| --- | --- | --- | --- |
| 1 | Goal 1 and Goal 3 | Yes | Goal 3 can tighten claims while Goal 1 hardens solved-state behavior. |
| 2 | Goal 2 | No | Wait for Goal 1 diagnostics and backend semantics. |
| 3 | Goal 4 and Goal 5 | Partly | Goal 5 depends on #136; start only after Goal 4's pure-parameter pattern is proven. |
| 4 | Goal 6 | Mostly no | ADR can begin earlier, but lifted-block repair should wait until helper and diagnostics conventions are stable. |

## Status Ledger

Update this table after each issue closes or a branch merges.

| Goal | Issues | Tracker State | Work State | Next Owner Action | Tracking Notes |
| --- | --- | --- | --- | --- | --- |
| Goal 1 | #132, #133, #140-lite | Open as of 2026-05-22 verification | Implemented locally on `codex/association-solved-state-reliability`; not closed until merged | Keep the Goal 1 focused State/contract validation in any Goal 2 proof run. | First implementation goal after #130/#131. |
| Goal 2 | #134, #140-helper | Open as of 2026-05-22 verification | Implemented and validated locally on `codex/association-implicit-sensitivity-helper`; review until merged | Review the helper extraction, focused tests, and IntelliJ validation evidence before PR merge. | Starts after Goal 1. |
| Goal 3 | #135 baseline | Open as of 2026-05-22 verification | Not started on merged tracker state | Tighten capability evidence vocabulary without adding derivative or optimizer support. | Can run with Goal 1. |
| Goal 4 | #136, #135 update | Open as of 2026-05-22 verification | Blocked by Goals 2 and 3 | Add pure association parameter sensitivities only after helper and capability firewall are in place. | Starts after Goal 2 and Goal 3 baseline. |
| Goal 5 | #137, #135 update | Open as of 2026-05-22 verification | Blocked by Goal 4 | Extend the proven pure-parameter pattern to binary association parameters. | Starts after Goal 4. |
| Goal 6 | #138, #139 | Open as of 2026-05-22 verification | ADR can start; lifted-block repair waits for stable helper conventions | Document architecture first, then repair the non-production lifted `X_A` block. | ADR may start early; block repair later. |

## Worker Startup Checklist

Before editing for any goal:

1. Read `docs/roadmaps/FULL_ROADMAP.md`.
2. Read this document.
3. Read `docs/roadmaps/unified_equilibrium_core_algorithm.md` if touching equilibrium internals.
4. Read `docs/pages/development_workflows.rst` before running pytest or `validate_project.py`.
5. Verify #130 and #131 are closed on GitHub.
6. Verify the target issue is still open and read its current body.
7. State the goal number, issue numbers, production workflow, and tests in the branch handoff.
8. Rebase or branch from current `origin/main`.

## Handoff Requirements

Every PR or handoff for this roadmap must include:

- goal number and issue numbers covered.
- files changed.
- whether any capability evidence changed.
- whether any public API changed; expected answer is usually no.
- focused validation commands and results.
- explicit statement that no direct CppAD fixed-point recording or non-exact production derivative backend was added.
- explicit statement that associating equilibrium remains not production-exposed.
- remaining blockers for later goals.

## Completion Criteria For The Tranche

This roadmap is complete only when:

- #132 through #140 are closed by merged implementation, validation, or ADR work matching their issue acceptance criteria.
- active association solved-state diagnostics are enforced before derivative use.
- active association backend semantics are implicit, not plain direct CppAD.
- reusable implicit-sensitivity machinery exists or equivalent tested extraction is in place.
- regression capability evidence distinguishes registry, derivative support, optimizer support, and production support.
- `e_assoc`, `vol_a`, `k_hb_ij`, and active-association `l_ij` derivative support is evidence-backed before any support claim is broadened.
- associating-equilibrium architecture is documented.
- lifted `X_A` block internals are repaired for future use while remaining non-production.
- #140 validation proves active association derivative payloads are finite, implicit-labeled, and guarded against direct CppAD fixed-point recording.

## Do Not Close By

Do not close any issue in this roadmap by:

- inventorying files.
- adding documentation that merely explains an unsupported path.
- adding fallback behavior.
- adding approximate validation and calling it production derivative support.
- exposing route strings or backend knobs before native support exists.
- moving scope to downstream studies.
- claiming capability because labels, target kinds, or registry names exist.
