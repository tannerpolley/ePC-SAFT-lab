# M0 Validation Correctness Tasks 9-22 Roadmap Reconciliation

Milestones: `M0`, `M1`, `M3`, `M4`, `M5`, `M6`
Packages: provider, equilibrium, regression, and repository validation
Status: `approved for milestone-owned planning`
Last reviewed: `2026-07-10`

## Context

This document reconciles the remaining Tasks 9-22 from the legacy
[2026-07-09 program spec](2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md)
and [implementation plan](../plans/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program-plan.md)
with the current package split, ADRs, milestone pages, live GitHub issues, and
the user's private single-user scope.

The active objective is reproducible local thermodynamic work: exact inputs,
correct native problem ownership, retained real-data comparisons, inspectable
residuals, and a clean Linux repository. Public release hardening, broad
platform support, and marketing-oriented capability presentation are outside
the active program unless later requested.

## Goals

- Decide whether each remaining task is coherent and still needed.
- Merge tasks that share one owner and data flow; split tasks that cross package
  or milestone ownership.
- Reuse live issues and canonical specs instead of creating duplicate trackers.
- Preserve scientific stop gates without requiring paper-specific repairs in
  an unrelated architecture task.
- Produce a dependency graph that can later drive implementation plans.

## Non-Goals

- No implementation, build, scientific regeneration, or plot change.
- No broad capability or equilibrium-family activation.
- No PyPI, manylinux, multi-Python, or public release campaign.
- No reopening of closed historical issues merely because their proof is now
  known to be incomplete.
- No deletion of the July 9 source program documents at closeout.

## Evidence Labels

- **Verified** means checked against current files, code, retained artifacts,
  or live GitHub issue state.
- **Inference** means the selected organization follows from verified package
  and dependency boundaries.
- **Unknown** means implementation evidence must be gathered by a later plan;
  the conservative outcome is no admission or no change.

## Task-By-Task Audit

| Task | Verdict and correction | Milestone / package | Source docs and issues | Dependencies and selected group |
| --- | --- | --- | --- | --- |
| 9. Typed model configuration | **Verified: necessary, but too large as one implementation slice.** Keep public `ModelOptions`; require versioned preset or complete explicit formulation; put correlations in `ParameterSet`, T/x resolution in `State`, and native mapping in one `ResolvedModelInput`. Fold the provider half of Task 21 into this owner cutover. Separate paper-bundle repair. | M3 / `packages/epcsaft` | New detailed M3 spec; closed #156/#157/#159/#160 are superseded behavior; #158 is retained history. | First provider dependency. M4/M5 consume the SDK; incomplete M6 bundles fail loudly. |
| 10. Native regression controls | **Verified: necessary after narrowing.** Every accepted control must change the submitted Ceres problem or fail before dispatch. Use a typed global loss plus row weights/scales; do not add row-loss precedence without a use case. Add native receipt and correct success semantics. | M5 / `packages/epcsaft-regression` | Detailed M5 contract spec; open #193 is the exact tracker; closed #53/#66/#94 are history. | Merge with Task 11; native-problem slice depends on Task 9. |
| 11. Strict target contracts | **Verified: necessary and inseparable from Task 10's receipt.** Require row/source identity, canonical family units, finite values, conditional citation metadata, and composition basis only for composition-bearing rows. | M5 / regression | Detailed M5 contract spec; #193; closed #88 is incomplete history. | Target module can start before Task 9; compiler/receipt follows Task 9. |
| 12. Real-data regression admission | **Verified: relevant only with narrower claims and split ownership.** Reset admitted families, then prove a NIST pure-neutral operational fit and Susial observed-state `k_ij` residual fit. Do not claim Gross reproduction, paper-parameter identity, or an M4 `x-y` curve. | M5 behavior; M6 retained evidence | Detailed M5/M6 spec; parents #193 and #194; closed #67/#95/#119 are history; #338 stays separate. | M5 native contract -> M5 reset/evidence schema -> M6 NIST/Susial gates -> final M5 scoped re-admission. |
| 13. Complete CE diagnostic receipt | **Verified: conditionally sane.** First audit what closed diagnostics #382-#402 already retain, correct the checker path to `scripts/validation/check_standalone_ce_gate.py`, then add only missing per-stage primal, constraint, activity, derivative, multiplier, scaling, and independently recomputed KKT evidence. | M4 / equilibrium | Refresh the standalone-CE spec and plan dated 2026-06-25/26; parent #321; ladder #329. | Precedes Task 14. A source-qualified nonideal MEA input is a separate M6 evidence child under #194. |
| 14. Repair CE formulation | **Verified: sane only after Task 13.** Permit the diagnosis to conclude that inputs, rather than implementation, are defective. If code is defective, repair the exact equation/derivative/scaling owner; solver tuning is not the first action. Closed #384 is partial history, not final proof. | M4 / equilibrium | Existing CE parent #321, ladder #329, activation #330; refreshed CE spec/plan. | Task 13 -> proven defect leaf -> repair leaf. Final local gate remains balance <=1e-8, stationarity <=1e-6, lambda=1, accepted native status. |
| 15. Re-admit closed equilibrium families | **Verified: not coherent as one task.** Shared certification already exists through closed #362. Use one blocked leaf per family and do not batch-admit. Reactive speciation remains #330; neutral LLE, electrolyte LLE successor, neutral multiphase, and TP flash remain separate leaves. | M4 / equilibrium | Existing unified PE certification spec/plan dated 2026-06-29; parents #361/#363; #330/#372/#376; closed #314/#350/#370 are historical. | Each family depends on its own solver, derivative, source, phase-discovery, postsolve, and checker gates. No new umbrella issue. |
| 16. manylinux compatibility | **Verified: public-release form is irrelevant to the selected private scope.** Replace it with a reproducible local Linux native build receipt: exact compiler, dependencies, package versions, commands, and ELF closure. Do not create or relabel a manylinux claim. | M1 / all package build boundaries | New M1 local Linux build/package spec and tracker. Broad M7 #195 remains deferred. | Reordered after Task 18's active-runtime record. |
| 17. artifact combinations | **Verified: retain only a minimal local install proof.** In clean local environments outside the checkout, install the four locally supported combinations: provider, provider+equilibrium, provider+regression, and all three; run representative currently admitted/component smokes and inspect local shared-library resolution. | M1 / provider and extensions | Same new M1 group; existing build helpers are inputs, not proof. | Task 18 -> Task 16 -> Task 17. Does not admit regression/equilibrium science. |
| 18. Python versions | **Verified: open-ended public support matrix is irrelevant.** Record and test the active Linux Python runtime used by this workspace. Do not widen CI or narrow published metadata solely for this private task. | M1 / package metadata and local workflow docs | Same new M1 group; broad #195 deferred. | Runs first in the local Linux group. |
| 19. characterization and size gates | **Verified: sane but partly complete.** Provider size gating and M4 ownership maps already exist. Replace a blunt absolute line limit with a committed baseline, no-growth rule, ratchet-on-shrink, and owner/ADR exception. | M0 governance with package-owned maps | New M0 characterization/ratchet spec and issue; PR #203 and closed #362 are existing evidence. | Precedes behavior-moving decomposition; maps update after Tasks 9-15 stabilize. |
| 20. equilibrium decomposition | **Verified: relevant.** Build on the selector and canonical result builder; do not recreate them. The May 27 cleanup plan is stale where it calls closed routes production. Decompose only behind characterized contracts. | M4 / equilibrium | New M4 canonical-owner decomposition spec/issue; ADR 0003; closed shared-contract leaf #362. | Leaf-level dependencies use the M0 ratchet and only the active correctness issue for each touched path; the whole tracker is not blocked by #361. |
| 21. regression and dataset decomposition | **Verified: invalid as one cross-package task.** Fold provider data/provenance/lookup separation into Task 9 and regression targets/compiler/results/persistence separation into Tasks 10-11. | M3 provider; M5 regression | M3 and M5 specs in this reconciliation; reuse #193 for M5. | Occurs during each contract cutover, after characterization; no standalone issue. |
| 22. full proof and plan retirement | **Verified: closeout is relevant, but plan deletion is wrong.** Run active local package, scientific, docs, Linux-build, diff, cleanup, and review gates. Gross/Sadowski Figures 2-9 remains an active M6 refresh because current public bubble/dew capability rows and registered confidence lanes consume it; unrelated paper bundles remain deferred. Retain the July 9 spec/plan, mark them complete, and link durable receipts. | M0 integration plus focused M6 public-route evidence | New M0 closeout spec/issue; new focused M6 Gross public bubble/dew evidence spec/leaf under #194; new M1 issue owns local Linux proof; broad #195 stays deferred. | Blocked by every active domain group and the focused Gross public-route receipt. Closeout cannot substitute for an unfinished package or capability-evidence task. |

## Selected Design

1. **M3 state-resolved model input:** Task 9 plus provider half of Task 21.
   Canonical spec: [M3 versioned state-resolved model input](2026-07-10-m3-eos-versioned-state-resolved-model-input.md).
2. **M5 native regression problem:** Tasks 10-11 plus regression half of Task
   21. Canonical spec: [M5 traceable native problem contract](2026-07-10-m5-regression-traceable-native-problem-contract.md). Reuse #193.
3. **M5/M6 real-data regression admission:** Task 12. Canonical spec:
   [M5/M6 regression real-data admission](2026-07-10-m5-m6-regression-real-data-admission.md). Reuse #193/#194 with milestone-owned children.
4. **M4 standalone CE diagnosis and repair:** Tasks 13-14 plus the reactive
   speciation leaf of Task 15. Use
   [the reconciled CE diagnostic/repair spec](2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md),
   refresh the existing standalone-CE source contract, and retain
   #321/#329/#330.
5. **M4 family-specific phase-equilibrium admission:** remaining Task 15.
   Reuse the unified certification spec/plan and #361 issue tree.
6. **M1 minimal local Linux reproducibility:** reordered Tasks 18, 16, 17.
   Use [the local Linux package reproducibility spec](2026-07-10-m1-local-linux-package-reproducibility.md),
   its plan, and one M1 tracker; keep M7 #195 inactive.
7. **M0 maintainability ratchets:** corrected Task 19. Create one M0 spec/plan
   and tracker from
   [the characterized-ownership spec](2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md).
8. **M4 equilibrium canonical-owner decomposition:** Task 20. Create one M4
   plan and tracker after the behavior gates, using
   [the canonical-owner decomposition spec](2026-07-10-m4-equilibrium-canonical-owner-decomposition.md).
9. **M0 program closeout:** corrected Task 22. Create one M0 closeout spec/plan
   and tracker from
   [the validation-correctness closeout spec](2026-07-10-m0-validation-correctness-program-closeout.md),
   retaining the source program documents.
10. **M6 Gross public bubble/dew evidence refresh:** focused prerequisite of
    Task 22 because current public capability rows cite Figures 2-9. Use
    [the Gross public-route evidence spec](2026-07-10-m6-gross-2002-public-bubble-dew-evidence-refresh.md)
    and its M6 plan; keep all unrelated paper repair deferred.

## Alternatives Considered

### Keep the original six phases and one cross-milestone plan

This preserves numbering but repeats the scope explosion seen in paused Task 9
and violates one-milestone issue ownership.

### Create one issue for every original task

This is easy to count but duplicates existing #193/#194 and creates artificial
seams between targets, controls, receipts, and admission evidence.

### Preserve task numbers as audit references and plan by canonical owner

This is selected. The umbrella keeps traceability while implementation specs,
plans, and issues follow milestone and package ownership.

## Package And Milestone Ownership

M0 owns cross-repository characterization policy and final closeout. M1 owns
minimal local Linux package/build reproducibility. M3 owns provider inputs and
resolved EOS records. M4 owns equilibrium diagnosis, formulation, selector,
and family admission. M5 owns regression data/problem/result behavior. M6 owns
retained literature/source artifacts and strict evidence checkers.

No issue spans milestones. A cross-workstream spec maps to milestone-owned
plans and issues with native dependency edges.

## Interfaces And Data Flow

`ParameterSet + ModelOptions + State conditions` produce one resolved M3 input
receipt. M5 consumes that receipt with a strict `TargetDataset` to produce one
native Ceres problem/result receipt. M6 compares retained observations with
model outputs derived from that exact receipt. M4 independently consumes the
M3 seam for equilibrium diagnostics and family-specific solves. M1 proves the
active package set runs in the local Linux environment. M0 closes only after
those owner-specific gates pass.

## Loud Errors And Stop Gates

- Missing scientific values, configuration choices, units, bases, source
  identities, or correlation domains stop at their typed owner.
- Unsupported regression controls are rejected before native dispatch.
- Failed CE residual or KKT gates remain failed regardless of solver exit.
- A finite phase-candidate set never establishes a global phase-set result.
- No equilibrium family is admitted by an umbrella task.
- Missing public-release proof does not block the selected private workflow;
  no release claim is made.
- Closeout stops when any active owner issue remains incomplete.

## Testing And Proof

Each detailed plan defines focused red/green tests. The final local proof joins:

- provider input/receipt/property/derivative contracts;
- regression target/control/native receipt and real-data lanes;
- CE diagnostics and each independently admitted equilibrium family;
- local Linux clean-environment package imports and representative admitted
  native smokes;
- retained source/model tables and every changed plot;
- official collection/default/confidence lanes that remain in active scope;
- strict docs, Ruff, diff, status, and repository cleanup; and
- independent code and thermodynamic review.

No release matrix, manylinux tag, or multi-Python proof is implied.

## Migration And Cutover

Write milestone-owned specs first, then implementation plans, then update or
create GitHub issues and dependency edges. Existing backlog #193/#194
source links must be corrected from retired `docs/milestones/...` paths to
`docs/superpowers/...`. Old plans are marked superseded when their capability
boundary conflicts with current ADRs. The July 9 task numbers remain in this
reconciliation and closeout record; implementation commits follow the new
owner groups.

## Risks

- Consolidation can hide a requirement if the task-to-group mapping is not
  maintained.
- Cross-workstream specs can be mistaken for permission to edit sibling
  packages; milestone-owned plans prevent that.
- Local-only build proof can later be mistaken for portable distribution
  proof; its receipts must state host/runtime scope.
- Characterizing incorrect behavior can freeze it; Tasks 9-15 establish the
  corrected owner before final decomposition baselines.
- Tracker updates can duplicate closed history unless #193/#194 and existing M4
  issue trees remain canonical.

## Publication And Execution Facts

- Exact new issue numbers do not exist until GitHub creates the approved M0,
  M1, M3, and M4 trackers.
- Exact extraction boundaries for Tasks 19-20 remain unknown until corrected
  behavior from Tasks 9-15 is stable; the conservative rule is no behavior move
  without a current characterization map.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Program framing | User clarification, 2026-07-10 | Optimize for private local validation correctness and reproducibility. | Public-release work is removed from the active program. | No | M0 |
| Task traceability | July 9 plan | Preserve task numbers in this reconciliation only. | New plans organize by owner. | No | M0 |
| Task 9 | Code/paused-branch audit | One M3 resolved-input group; paper repair separate. | Avoid another 304-file slice. | No | M3 |
| Tasks 10-11 | Shared compiler/receipt ownership | Merge under #193. | One target-to-native problem contract. | No | M5 |
| Task 12 | Tracker and artifact ownership | One spec, separate M5/M6 plans and children. | One milestone per issue. | No | M5/M6 |
| Tasks 13-14 | Live CE evidence | Refresh existing CE tree and diagnose before repair. | Tuning cannot precede evidence. | No | M4 |
| Task 15 | Existing #361/#363 tree | Split into family leaves; no new umbrella. | No batch admission. | No | M4 |
| Tasks 16-18 | Private Linux scope | Replace release matrix with minimal M1 local Linux proof ordered 18->16->17. | No manylinux or multi-Python claim. | No | M1 |
| Task 19 | Existing gates/maps | Use baseline/no-growth ratchets, not line count as architecture proof. | Existing progress is retained. | No | M0/packages |
| Task 21 | Package boundary policy | Fold each half into its owning contract group. | No cross-milestone refactor issue. | No | M3/M5 |
| Task 22 | Later user instruction | Retain and mark source spec/plan complete. | No deletion of requested history. | No | M0 |
| New issue numbers | GitHub state | Assign only on issue creation. | No fictional tracker IDs. | Yes | M0 |
