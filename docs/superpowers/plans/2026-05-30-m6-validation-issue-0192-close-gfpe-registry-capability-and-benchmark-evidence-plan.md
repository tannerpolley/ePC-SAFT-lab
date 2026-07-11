# Current GFPE Registry, Capability, And Benchmark Evidence Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or
> `superpowers:executing-plans`, `superpowers:test-driven-development`,
> `chemical-engineer` for capability/evidence interpretation, and
> `superpowers:verification-before-completion`.

**Goal:** Resolve #192 by reconciling current public equilibrium registry and
capability evidence after #236 and #455 pass, without reopening any closed
route family.

**Architecture:** Treat accepted #236 and #455 receipts as immutable M6 inputs.
Derive one exact public capability snapshot, validate it against selector and
registry state, update docs/generated resources, and retain one deterministic
closeout receipt. M3 model schemas, M4 route admission, and M6 evidence remain
separate owners.

**Tech Stack:** Python 3.13 local baseline, JSON, pytest, Sphinx, `uv`, and Git.

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m6-validation-issue-0192-m6-close-gfpe-registry-capability-and-benchmark-evidence.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/192`
- Milestone: `M6 - Validation`
- Active blockers: #236 and #455

## Outcome Proof

**Intent:** Make every public equilibrium claim point to current executable evidence and keep internal/closed routes out of public capability state.
**Current Behavior:** The old #192 plan used retired paths and described neutral, associating, electrolyte, and reactive scope too broadly; #236 also recorded a stale four-family surface.
**Expected Outcome:** Registry, capability payloads, docs, and confidence checks expose only bubble pressure, dew pressure, and scoped nonassociating hydrocarbon single-component VLE with exact current receipts.
**Target Output:** One deterministic #192 evidence receipt plus synchronized generated registries, capability snapshots, user docs, tests, issue state, and local mirror.
**Owner:** M6 Validation owns evidence reconciliation; M3 and M4 remain authoritative for model schemas and route admission.
**Interface:** Accepted #236/#455 receipts, algorithm registry, capability payloads, generated docs/resources, confidence tests, GitHub dependencies, and local mirror.
**Cutover:** Replace stale four-family and historical-route interpretations with the exact three-workflow public surface after both active blockers close.
**Replaced Path:** Retired `docs/milestones/**` references, planned-only evidence, and closed/internal route receipts used as public capability authority.
**Evidence:** Hash-identified #236 and #455 checker receipts, exact public selector/capability snapshots, generated-registry checks, and strict docs output.
**Acceptance Proof:** A clean run accepts only the three public workflows, rejects injected closed/internal route rows, validates current child-receipt hashes, and leaves live/local tracker state synchronized.
**Stop Criteria:** Stop if either blocker is open/rejected, an active row lacks a current receipt, selector/capability state conflicts, or reconciliation would require M3/M4 implementation changes.
**Avoid:** Do not repair paper programs, invent evidence, broaden route support, collapse global schemas into instance policy, or describe local validation as release readiness.
**Risk:** Historical internal receipts are extensive and can make a stale route appear supported unless the checker ties every active row to current selector and evidence identities.

## Implementation Boundaries

**Files To Create:** A focused #192 receipt/checker artifact only if no existing canonical M6 registry receipt can own the result.
**Files To Modify:** M6 registry/capability resources, focused repository/capability tests, user-facing capability docs, the #192 mirror, and M6 milestone page.
**Files To Avoid:** Provider/equilibrium production implementation, unrelated paper-validation folders, M5 regression code, release workflows, and closed historical receipts.
**Source Of Truth:** Live public selector/capability state plus accepted #236 and #455 checker receipts.
**Read Path:** Load and validate blocker receipts, inspect exact public selector/capability snapshots, then compare registry and docs state.
**Write Path:** Update derived registry/docs resources and atomically write one deterministic #192 receipt after every strict check passes.
**Integration Points:** Provider schema capability metadata, equilibrium activation/capability contracts, Gross current-evidence checker, single-component VLE evidence, generated docs, and confidence routing.
**Migration Or Cutover:** Replace retired path references and stale family lists in one reviewed M6 change after dependencies close.
**Replaced Path Handling:** Delete obsolete registry rows and prose; do not retain aliases, fallback rows, or compatibility capability names.
**Acceptance Proof Gate:** Require focused RED mutation tests, child-receipt hash/freshness proof, exact public snapshot equality, strict docs, diff check, and cleanup.

### Task 1: Establish The Dependency And RED Capability Contract

**Use Cases:**

- A checker reports #236 or #455 as an explicit blocker instead of using stale evidence.
- Injecting a closed LLE, TP-flash, reactive, electrolyte, or multiphase row produces visible RED evidence.
- Retired registry paths and old four-family prose are identified for cutover and deletion.

**Files:**

- Modify: focused M6 capability/registry tests
- Modify: `docs/superpowers/issues/2026-05-30-m6-validation-issue-0192-m6-close-gfpe-registry-capability-and-benchmark-evidence.md`

- [ ] Snapshot the live #236/#455 dependency state and exact accepted-receipt contract.
- [ ] Add RED tests for missing/stale child receipts and injected closed route rows.
- [ ] Inventory stale docs, generated resources, and checker ownership without changing M3/M4 production code.

### Task 2: Reconcile Current Public Evidence And Cut Over Derived State

**Use Cases:**

- Accepted evidence yields exactly bubble pressure, dew pressure, and scoped nonassociating hydrocarbon single-component VLE.
- Provider global schema/preset facts remain distinct from mixture/state instance policy.
- Old planned/internal capability rows are replaced and cannot survive through a duplicate registry owner.

**Files:**

- Modify: M6 registry/capability resources selected by Task 1
- Modify: focused capability, activation, and confidence tests
- Modify: user-facing capability documentation and generated resources

- [ ] Consume exact accepted blocker receipts and validate their hashes/freshness.
- [ ] Update the canonical derived registry/capability snapshot and delete displaced rows/prose.
- [ ] Keep every closed route absent from public selectors and capability payloads.
- [ ] Write the deterministic #192 receipt only after all structural checks pass.

### Task 3: Prove The Integrated Gate And Synchronize Tracker State

**Use Cases:**

- The strict checker and docs make the current three-workflow scope visible and reproducible.
- Mutation tests prove stale or broader route evidence is rejected.
- The old blocked tracker/mirror state is replaced only after live dependencies and acceptance evidence agree.

**Files:**

- Modify: `docs/superpowers/milestones/M6-validation/README.md`
- Modify: the #192 local mirror and generated documentation outputs

- [ ] Run focused capability/activation/confidence and receipt tests.
- [ ] Run generated-registry checks, strict Sphinx, Ruff on touched Python, and `git diff --check`.
- [ ] Validate the source plan and issue mirror, run cleanup, and reconcile live/local readiness.
- [ ] Obtain independent scientific/capability review before closing #192.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/workflows/repo/test_run_pytest.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
