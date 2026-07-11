# M6 Single-Component VLE Capability Evidence Reconciliation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or
> `superpowers:executing-plans`, `superpowers:test-driven-development`,
> `chemical-engineer` for scope/evidence interpretation, and
> `superpowers:verification-before-completion`.

**Goal:** Resolve #236 after #444 by reconciling provider/equilibrium ownership,
activation metadata, validation routing, and current evidence for the scoped
nonassociating methane/ethane/propane `single_component_vle` route.

**Architecture:** Treat the native M4 activation matrix as active route policy,
the M3 capability payload as global model-schema/preset discovery, and the
retained NIST checker receipt as route evidence. Compare them through one
strict M6 checker/test slice; do not copy instance policy into provider-global
metadata or infer support from installed native symbols.

**Tech Stack:** Python 3.13 local baseline, JSON, pytest, Sphinx, `uv`, and Git.

## Outcome Proof

**Intent:** Remove the stale four-family interpretation and make single-component VLE ownership/evidence exact after the resolved-input cutover.
**Current Behavior:** The live activation tests already describe two production families and three public routes, but #236's historical body claimed neutral TP flash and neutral LLE were production-exposed and lacked a focused post-cutover proof plan.
**Expected Outcome:** Provider metadata advertises supported configuration schemas/presets only; M4 advertises active `single_component_vle` policy and exact NIST scope; validation routing and docs agree.
**Target Output:** One M6/repository comparison checker, a current #236 evidence receipt, corrected derived docs/routing, and an accepted blocker receipt for #192.
**Owner:** M6 owns evidence reconciliation; M3 owns global model-configuration capability metadata; M4 owns route activation and result acceptance.
**Interface:** M3 `capabilities()`, M4 native activation matrix and `capabilities()`, NIST single-component checker/receipt, `run_pytest` confidence routing, docs, and #192.
**Cutover:** Replace the stale four-family text/expectation after #444 with the exact scoped nonassociating hydrocarbon route contract.
**Replaced Path:** Any provider-side active-route policy duplication, three-family/four-family stale snapshot, or capability row inferred only from native availability.
**Evidence:** Exact activation snapshots, provider global-capability snapshots, NIST receipt identity/range/species checks, routing tests, docs, and mutation tests.
**Acceptance Proof:** Tests accept methane/ethane/propane only within retained NIST ranges, reject associating/unproven/out-of-range inputs, and prove provider-global metadata does not select an active route.
**Stop Criteria:** Stop if #444 is incomplete, current NIST receipt is stale, provider and equilibrium ownership conflict, or fixing the issue requires new route/solver implementation.
**Avoid:** Do not expose neutral TP flash/LLE, associating/electrolyte/reactive/multiphase routes, invent evidence, or treat provider schema support as instance admission.
**Risk:** A duplicated provider route list can drift independently of the M4 activation matrix and make an unavailable workflow appear public.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_single_component_vle_capability_evidence.py`, a focused repository/M6 test, and the deterministic #236 receipt if the current single-component checker cannot express ownership/freshness facts.
**Files To Modify:** `tests/workflows/repo/test_run_pytest.py`, focused derived capability docs, #236 mirror, and M6 milestone evidence.
**Files To Avoid:** Provider/equilibrium package code and package-owned contract tests, solver implementation, other paper validations, regression code, activation of closed route families, and release workflows.
**Source Of Truth:** Post-#444 provider capability schema plus the native M4 activation matrix and accepted NIST single-component receipt.
**Read Path:** Load provider global capability metadata, native activation rows, and exact NIST evidence; compare scope/ownership/freshness.
**Write Path:** Update only M6/repository comparison tests, derived docs/routing, and the deterministic #236 receipt when every read-only package source agrees.
**Integration Points:** `epcsaft.runtime.capability_evidence`, `epcsaft_equilibrium.capability_evidence`, activation contract tests, NIST checker, `run_pytest`, and #192 dependency readiness.
**Migration Or Cutover:** Execute after #444 and replace old four-family prose/snapshots in one M6 slice.
**Replaced Path Handling:** Delete stale expectations and duplicated policy; do not keep aliases or compatibility rows.
**Acceptance Proof Gate:** Require RED mutation tests, exact scope/receipt checks, docs, mirror/plan validators, diff check, cleanup, and independent review.

### Task 1: Establish The Post-Cutover Ownership And RED Contract

**Use Cases:**

- Provider global schema/preset discovery cannot masquerade as active route policy.
- Injected neutral TP flash/LLE or associating single-component public rows fail visibly.
- Old three-/four-family expectations are identified for replacement.

**Files:**

- Create: focused M6/repository comparison checker tests
- Modify: `tests/workflows/repo/test_run_pytest.py`

- [ ] Require #444 and the accepted NIST receipt identity/freshness.
- [ ] Add RED mutations for duplicated policy, unsupported species/ranges, closed families, and stale receipts.
- [ ] Inventory docs/routing expectations that predate the current activation matrix.

### Task 2: Reconcile Exact Single-Component VLE Evidence

**Use Cases:**

- Methane, ethane, and propane within retained NIST ranges have one current public evidence chain.
- Associating, unproven, binary, or out-of-range inputs remain rejected.
- Stale provider-active-policy and route-family snapshots are replaced, not wrapped.

**Files:**

- Create: `scripts/validation/check_single_component_vle_capability_evidence.py`
- Modify: selected M6/repository evidence tests and derived docs/resources
- Modify: the focused #236 checker/receipt if Task 1 proves it is needed

- [ ] Derive the exact public route/scope from M4 activation and NIST evidence.
- [ ] Assert M3 exposes only global schema/preset support and receipt interfaces.
- [ ] Update routing/docs and delete stale expectations without changing activation state.
- [ ] Write one deterministic #236 receipt that #192 can validate.
- [ ] If a read-only M3/M4 contract source disagrees, stop and route a separate package-owned defect issue instead of editing sibling package tests here.

### Task 3: Prove And Hand Off To The #192 Gate

**Use Cases:**

- Focused tests and docs display the exact scoped route and its evidence identity.
- Mutation tests prove broader/stale rows cannot pass.
- The old #236 ambiguity is replaced by a current receipt and synchronized tracker state.

**Files:**

- Modify: #236 mirror and M6 milestone page
- Modify: focused generated capability resources selected by Task 1

- [ ] Run focused capability/activation/NIST/routing tests and generated checks.
- [ ] Run strict docs, Ruff on touched Python, diff check, cleanup, and both plan validators.
- [ ] Obtain independent capability/scientific review.
- [ ] Close #236 only with an accepted receipt and let dependency readiness keep #192 blocked on #455 as needed.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m6-single-component-vle-capability-evidence-reconciliation-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m6-single-component-vle-capability-evidence-reconciliation-plan.md
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/workflows/repo/test_run_pytest.py -q
uv run --no-sync python scripts/validation/check_single_component_vle_nist_saturation.py --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
