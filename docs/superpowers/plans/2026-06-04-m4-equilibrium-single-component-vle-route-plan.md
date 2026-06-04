# Single-Component VLE Route For Equilibrium Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add production pure-component VLE solving to `epcsaft-equilibrium` using the modular Ipopt/NLP route discipline.

**Architecture:** Keep EOS state/property evaluation in the provider and implement coexistence route assembly in the equilibrium extension. Build a one-component VLE block and route path that solves vapor/liquid density roots and common saturation pressure from pressure equality and chemical-potential or fugacity equality, with exact derivative evidence and route diagnostics.

**Tech Stack:** Python, C++17, CMake, CppAD/provider derivative substrate, Ipopt, pytest.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m4-equilibrium-single-component-vle-route.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m4-equilibrium-single-component-vle-route-plan.md`
- GitHub Issue: `none`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `HITL` until route naming and public activation policy are approved for the production surface.

## Dependencies

User decision: this M4 route plan is independent from the M8 toybox SciPy solver. The M8 solver can provide analysis evidence, but this production plan may proceed from the existing equilibrium framework and provider EOS contracts.

Related M4 work:

- `docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md`
- `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate-plan.md`
- `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md`

## Acceptance Criteria

- [ ] `epcsaft-equilibrium` exposes a production-owned single-component VLE route or route block; the provider package does not expose a new vapor-pressure API.
- [ ] The route solves common `P_sat`, vapor density, and liquid density from pressure equality and chemical-potential or fugacity equality.
- [ ] Route initialization, variable scaling, bounds, diagnostics, and failure policy are owned by the equilibrium extension.
- [ ] Exact derivative/NLP evidence is reported consistently with existing equilibrium capability contracts.
- [ ] Public result payloads include `P_sat`, vapor density, liquid density, residuals, solver status, and route diagnostics without claiming broader binary bubble/dew or GFPE behavior.
- [ ] CMake/source lists and focused equilibrium tests cover the new files.

## Tasks

### Task 1: Route Contract And Native Block Shape

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/single_component_vle_block.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/single_component_vle_block.cpp`
- Test: `packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py`
- Modify: `packages/epcsaft-equilibrium/CMakeLists.txt`

- [ ] **Step 1: Write the failing native block tests**

Assert that the block accepts a one-component provider payload, fixed
temperature, and initial guesses, then returns structured residuals for
pressure equality and chemical-potential or fugacity equality.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:
`uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py -q`

Expected before implementation: block bindings or native symbols are missing.

- [ ] **Step 3: Implement the native block**

Implement the variable layout, residual assembly, and diagnostics for
`log_rho_v`, `log_rho_l`, and `log_p_sat`. Use provider EOS quantities rather
than duplicating provider equations in equilibrium.

- [ ] **Step 4: Build and run the block tests**

Run:
`pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Target epcsaft_equilibrium_native_core -Parallel 10`

Then:
`uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py -q`

- [ ] **Step 5: Commit**

Stage only the native block, CMake, and native block tests. Commit with:
`equilibrium: add single component vle block`

### Task 2: Route Assembly And Result Payload

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/single_component_vle.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/route_metadata.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/result_builder.cpp`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py`

- [ ] **Step 1: Write route and result tests**

Assert that a single-component VLE route has route metadata, a result payload
with `P_sat`, vapor density, liquid density, residuals, solver status, and no
binary bubble/dew or GFPE capability claim.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:
`uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py -q`

- [ ] **Step 3: Implement route assembly**

Wire the single-component VLE block into the equilibrium route layer and result
builder. Keep route failure messages loud for missing vapor root, missing liquid
root, invalid one-component payload, and near-critical degeneracy.

- [ ] **Step 4: Build and run tests**

Run:
`pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Target epcsaft_equilibrium_native_core -Parallel 10`

Then rerun the route/result tests.

- [ ] **Step 5: Commit**

Stage only route/result files and tests. Commit with:
`equilibrium: route single component vle results`

### Task 3: Python API And Capability Evidence

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py`
- Test: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Write API and capability tests**

Assert that the route is available only for one-component mixtures, returns the
production result payload, and reports exact derivative/IPOPT evidence without
claiming binary or generalized equilibrium activation.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:
`uv run python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`

- [ ] **Step 3: Implement Python surface**

Add the route to the public equilibrium workflow shape selected by the existing
route architecture. Do not add provider aliases or duplicate package exports.

- [ ] **Step 4: Run focused API tests**

Run:
`uv run python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`

- [ ] **Step 5: Commit**

Stage only API/capability files and tests. Commit with:
`equilibrium: expose single component vle route`

## Proof Oracle

- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Target epcsaft_equilibrium_native_core -Parallel 10`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python scripts/dev/validate_project.py quick`
