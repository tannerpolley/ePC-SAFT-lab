# Pure 2B Associating Single-Component VLE Prerequisite Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the native prerequisite out of Gross 2002 Figure 1 replication by admitting only pure neutral 2B associating components through the public `single_component_vle` route with exact association derivative evidence.

**Architecture:** This is an M4 equilibrium prerequisite for #280. It owns the native route admission, selector/capability wording, and route tests required before any Gross 2002 Figure 1 artifact generator can run package-owned model curves. It does not own digitization, retained figure artifacts, plot rendering, score JSON, or full-replication manifest acceptance.

**Tech Stack:** `epcsaft_equilibrium.Equilibrium`, existing `single_component_vle` Ipopt route, native equilibrium selector and derivative blocks, CppAD/implicit association diagnostics, pytest through `run_pytest.py`, and focused native equilibrium build validation.

## Intake

- Source spec: `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`
- Triggering issue: #280, whose kill criteria require splitting prerequisite work when pure associating `single_component_vle` cannot already produce certified vapor/liquid densities.
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `association`
- Backend: `Ipopt`

## Outcome Contract

**Intent:** Make the native package route capable of solving pure 2B associating saturated vapor/liquid states before Figure 1 replication consumes it.
**Current Behavior:** Public `single_component_vle` is nonassociating-only, so Figure 1 replication either has to change native route code or cannot generate package-owned model curves.
**Expected Outcome:** A pure neutral 2B associating component such as Gross/Sadowski 2002 methanol can solve through `Equilibrium(..., route="single_component_vle", T=...).solve()` with exact association derivative metadata, while binary associating, electrolyte, reactive, and generalized associating surfaces remain closed.
**Target-Perspective Output:** A reviewer can run the route test and see a native Ipopt result with vapor/liquid densities, pressure consistency, chemical-potential consistency, and exact association derivative diagnostics for a Gross 2002 pure alcohol case.
**Truth Owner:** The public `single_component_vle` API contract, the native selector activation matrix, and exact association derivative diagnostics.
**Contract Interface:** `epcsaft_equilibrium.Equilibrium(..., route="single_component_vle", T=...).solve()` plus route/capability metadata.
**Cutover Decision:** #280 may generate Figure 1 model curves only after this prerequisite is merged and `single_component_vle` admits the narrow pure 2B associating case.
**Displaced Path:** The old blanket associating rejection remains displaced only for one-component neutral 2B association; every broader associating route remains governed by its own proof gate.
**Acceptance Proof:** Focused API/native route tests, activation capability tests, native equilibrium build, and cleanup hook.
**Stop Criteria:** Stop and create a deeper derivative/route issue if the implementation requires broad binary associating VLE, electrolyte, reactive, or generalized phase-set admission.
**Avoid:** Do not create or modify Gross 2002 figure artifacts, lower checker thresholds, claim binary associating VLE, or use a Python-owned production solver.

## Acceptance Criteria

- [ ] Public `single_component_vle` accepts exactly one neutral 2B associating component.
- [ ] Public `single_component_vle` still rejects binary associating mixtures and out-of-scope ionic/reactive inputs.
- [ ] Native route diagnostics report exact association derivative/Hessian evidence for the accepted pure associating case.
- [ ] Existing nonassociating single-component VLE tests remain green.
- [ ] Capability and activation metadata describe the narrow pure 2B associating admission without broad association overclaiming.

## Tasks

### Task 1: Add Failing Public Route Coverage

- [ ] Replace or complement the associating rejection test with a Gross/Sadowski 2002 methanol 2B acceptance test.
- [ ] Assert finite vapor density, liquid density, saturation pressure, phase-distance diagnostics, and exact association derivative metadata.
- [ ] Keep a separate rejection test for binary associating `single_component_vle` input.

### Task 2: Narrow Python Admission

- [ ] Allow exactly one neutral associating component in `single_component_vle` validation.
- [ ] Preserve existing guards for mixture size, ions, unsupported route families, and out-of-scope association configurations.

### Task 3: Wire Native Exact-Hessian Support

- [ ] Route the pure associating case through the existing association phase-system block.
- [ ] Use the existing implicit association derivative path for first and second derivative evidence.
- [ ] Preserve nonassociating route behavior and native activation family labels.

### Task 4: Update Capability Evidence

- [ ] Update `epcsaft_equilibrium.capabilities()` and generated activation metadata narrowly.
- [ ] State that the route admits pure 2B associating single-component VLE only, not binary associating VLE or generalized associating phase sets.

### Task 5: Validate And Handoff

- [ ] Build equilibrium native code.
- [ ] Run focused single-component VLE and activation capability tests.
- [ ] Run cleanup hook.
- [ ] Hand #280 a concise prerequisite receipt: route name, accepted association scheme, derivative backend, and test commands.

## Non-Goals

- No Gross 2002 Figure 1 source CSV, PNG, SVG, plot score, manifest acceptance, or campaign summary updates.
- No binary associating VLE admission.
- No electrolyte, reactive, LLLE, CE, CPE, or generalized associating phase-count admission.
- No regression package changes.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Follow-On

After this prerequisite merges, #280 should be revised to remove native route implementation tasks and should contain only Figure 1 source/model artifact generation, plotting, scoring, checker, and manifest acceptance work.
