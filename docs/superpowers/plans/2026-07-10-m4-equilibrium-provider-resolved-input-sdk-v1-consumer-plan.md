# M4 Provider Resolved-Input SDK V1 Consumer Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or
> `superpowers:executing-plans`, `superpowers:test-driven-development`,
> `chemical-engineer` for state/composition semantics, and
> `superpowers:verification-before-completion`.

**Goal:** Resolve #443 by moving `epcsaft-equilibrium` to the complete M3
resolved-input SDK v1 after #442 lands, without creating an M4 serializer,
default policy, or new public route.

**Architecture:** The public `Equilibrium` request supplies its exact T and
composition conditions to the provider-owned resolver and retains the returned
immutable evaluated input/receipt for the lifetime of the configured problem.
M4 passes the provider-owned native handle through its selector boundary;
native and Python M4 code never reconstruct the provider payload. Closed
internal routes migrate only when their own caller/correctness issue permits
it.

**Tech Stack:** Python 3.13 local baseline, C++/pybind11, CMake, Ipopt, pytest,
Ruff, Sphinx, `uv`, and Git.

## Outcome Proof

**Intent:** Give equilibrium one versioned provider input at the request conditions and remove direct dependence on static `Mixture.native` payload assembly.
**Current Behavior:** Public equilibrium construction passes `mixture.native` repeatedly into problem configuration, structure, and solve paths; that static seam cannot represent state-evaluated correlations and duplicates provider payload ownership.
**Expected Outcome:** Every admitted public equilibrium request owns one immutable evaluated M3 input and detached receipt; M4 selector/solve calls receive its native handle without mapping serialization or default insertion.
**Target Output:** Focused M4 adapter/call-site changes, a provider-integration contract test, native receipt propagation, removed static public calls, updated M4 docs, and unchanged public capability snapshots.
**Owner:** M4 and `packages/epcsaft-equilibrium`; M3 owns configuration, evaluation, native-handle construction, and receipt schema.
**Interface:** The complete SDK contract produced by #442, M4 `Equilibrium`, configured problem/structure/selector calls, result diagnostics, and `provider_contract()` discovery.
**Cutover:** Replace public-route `mixture.native` consumption with the provider-owned evaluated-input object in one M4 commit based on #442.
**Replaced Path:** Direct static native payload access in admitted public workflow construction, structure, and solve calls.
**Evidence:** Provider-contract mutation tests, exact evaluated-receipt identity through configure/structure/solve, public route tests, native selector receipts, capability snapshots, docs, and replaced-path scans.
**Acceptance Proof:** Bubble pressure, dew pressure, and scoped nonassociating hydrocarbon single-component VLE pass through one evaluated input each; dynamic inputs resolve at request conditions; injected missing/mismatched receipts fail before native dispatch; public/closed route state is unchanged.
**Stop Criteria:** Stop if #442 is incomplete, the provider SDK lacks an immutable native handle/receipt, composition semantics are ambiguous, or a caller belongs to a separate closed-route/paper issue.
**Avoid:** Do not serialize provider fields in M4, infer configuration, preserve a compatibility payload, edit M3 internals, migrate deferred paper callers, or broaden capability state.
**Risk:** A partial migration could evaluate the provider twice or leave structure and solve on different native inputs; identity tests must bind all stages to one receipt.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py` and only a small M4-owned adapter module if direct typed consumption cannot remain in `equilibrium.py`.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`, `_native.py`, the public selector workflow seam, focused API/contract tests, package docs, and M4 milestone evidence.
**Files To Avoid:** `packages/epcsaft/**`, `packages/epcsaft-regression/**`, paper-validation programs, closed-route implementation, and capability activation tables except unchanged snapshot assertions.
**Source Of Truth:** M3 SDK v1 evaluated-input/native-handle/receipt contract from #442.
**Read Path:** Validate SDK identity, resolve once from the exact public request conditions, retain the evaluated object, and read its detached receipt for diagnostics.
**Write Path:** Pass only the provider native handle into existing M4 configured-problem/selector interfaces and attach the detached receipt to result evidence.
**Integration Points:** `Equilibrium.__init__`, structure, selector solve, `_native.provider_contract`, public API tests, native selector contracts, and M3/M1 combined cutover gates.
**Migration Or Cutover:** Land after #442; update admitted public callers directly and leave every route-gated/internal/paper caller for its named owner.
**Replaced Path Handling:** Delete migrated `mixture.native` public calls and any M4 payload helper; add no alias or fallback.
**Acceptance Proof Gate:** Require one-evaluation identity tests, loud missing/mismatch tests, public route/confidence tests, unchanged activation snapshots, strict docs, Ruff, diff check, and cleanup.

### Task 1: Define The M4 Evaluated-Input Consumer Contract

**Use Cases:**

- A public equilibrium request resolves exactly once at its explicit T/composition conditions.
- Missing, wrong-version, or condition-mismatched provider receipts fail visibly before selector dispatch.
- RED scans identify every admitted public `mixture.native` call that the cutover replaces.

**Files:**

- Create: `packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py`
- Modify: focused M4 API/native contract tests

- [ ] Pin #442 and read the final public SDK names rather than importing provider-private types.
- [ ] Add RED identity, missing-receipt, version, condition, and replaced-path tests.
- [ ] Inventory internal/paper callers and exclude them unless their owning dependency is already accepted.

### Task 2: Cut Admitted Public Equilibrium Calls To One Evaluated Input

**Use Cases:**

- Configure, structure, and solve share one provider native handle and receipt identity.
- State-dependent provider correlations are evaluated at the request conditions, not at a static mixture default.
- The old static public payload path is replaced without a wrapper or second serializer.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native.py`
- Modify: the focused public selector workflow owner selected by Task 1

- [ ] Resolve and retain the provider evaluated input in the configured M4 request.
- [ ] Pass its native handle through configuration, structure, and solve exactly once.
- [ ] Attach the detached receipt identity to M4 diagnostics/results without copying mutable mappings.
- [ ] Delete migrated static payload calls and reject unsupported dynamic/internal static access loudly.

### Task 3: Prove Capability-Neutral Integration And Handoff

**Use Cases:**

- Public bubble/dew and scoped single-component VLE behavior remains numerically characterized after cutover.
- Closed routes and global capability rows remain unchanged and visible in snapshots.
- The final proof replaces the old consumer seam and supplies the receipt required by #444/M1.

**Files:**

- Modify: focused M4 docs and milestone evidence
- Modify: package/repository integration tests named by the final #442 SDK

- [ ] Rebuild equilibrium against the installed provider SDK and run the focused contract/API lanes.
- [ ] Run replaced-path scans and unchanged activation/capability snapshots.
- [ ] Run strict docs, Ruff, diff check, mirror/plan validators, cleanup, and independent review.
- [ ] Record the accepted M4 consumer commit/receipt for #444 and #438.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m4-equilibrium-provider-resolved-input-sdk-v1-consumer-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m4-equilibrium-provider-resolved-input-sdk-v1-consumer-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile equilibrium --parallel 1
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py -q
uv run --no-sync ruff check packages/epcsaft-equilibrium/src packages/epcsaft-equilibrium/tests
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
