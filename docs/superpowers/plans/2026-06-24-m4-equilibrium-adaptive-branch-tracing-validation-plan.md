# M4 Equilibrium Adaptive Branch Tracing Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an internal adaptive branch-tracing layer that makes M4 boundary-route validation depend on solved equilibrium branch points instead of sparse interpolation.

**Architecture:** Implement an internal Python branch tracer in `packages/epcsaft-equilibrium` that drives existing `Equilibrium(...).solve()` point routes, carries continuation state, adaptively refines invalid segments, and exports retained trace diagnostics. Wire Gross/Sadowski 2002 Figure 2 through the shared tracer and make the full-replication checker block accepted figures when required trace anchors or segment-density evidence are missing.

**Tech Stack:** Python dataclasses, pytest, `epcsaft_equilibrium.Equilibrium`, native Ipopt route diagnostics, Gross/Sadowski 2002 paper-validation scripts, PowerShell plan validators, `uv run --no-sync python`, Matplotlib artifact generation.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-24-m4-equilibrium-adaptive-branch-tracing-and-validation.md`
- Auto Mode authorization: `.superpowers/runs/2026-06-24-equilibrium-branch-tracing/auto-mode-authorization.json`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- First validation target: `analyses/paper_validation/2002_gross/figures/figure_02`
- Existing prerequisite context: `docs/superpowers/plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md`
- Existing figure plan context: `docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md`
- Plan validation helper added during this route: `scripts/validate_plan_outcome_proof.py`

## Outcome Proof

**Intent:** Add reusable internal branch tracing so boundary-route validation proves solved branch density, required source-anchor solves, exact-Hessian receipts, and postsolve receipts before a paper-validation curve can count as accepted.
**Current Behavior:** Figure 2 branch solving is open-coded inside `analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py`, and the shared checker does not require retained branch trace completeness before accepting a smooth plotted curve.
**Expected Outcome:** Figure 2 generation uses package-owned branch tracing, writes retained trace diagnostics, and the checker rejects accepted Figure 2 records when required traces, required anchors, exact-Hessian evidence, postsolve evidence, or segment-density metrics are missing.
**Target Output:** `scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native` exits `0` only when Figure 2 has accepted branch trace summaries for `bubble_line` and `dew_line` plus solved model rows behind the rendered `figure_02.png`, `figure_02.svg`, and `figure_02.pdf`.
**Owner:** `packages/epcsaft-equilibrium` owns the reusable branch tracer; `analyses/paper_validation/2002_gross/figures/figure_02` owns Figure 2 source/model/plot artifacts; `scripts/validation/check_gross_2002_full_replication.py` owns campaign admission.
**Interface:** Internal module `epcsaft_equilibrium.branch_tracing` with explicit trace data objects and `trace_boundary_route(...)`; Figure 2 consumes that internal module and writes `analyses/paper_validation/2002_gross/shared/results/figure_02_trace_summary.json`; the checker reads manifest fields `requires_branch_trace`, `trace_requirements`, and artifact `trace_summary_json`.
**Cutover:** Replace Figure 2's figure-local `_solve_route_point(...)` and `_solve_series(...)` route loop with the shared tracer while keeping Figure 2 source acquisition, scoring, rendering, and manifest update ownership in the figure script.
**Replaced Path:** The old path where a figure-local loop could produce sparse model rows and rely on renderer smoothing is displaced by trace completeness gates and shared package branch tracing.
**Evidence:** Package tracer tests, checker regression tests, retained Figure 2 shared trace summary, regenerated Figure 2 model/plot artifacts, full Gross 2002 checker output, exact-Hessian receipts, fresh-native receipt, and cleanup hook output.
**Acceptance Proof:** A reviewer can inspect the Figure 2 trace summary and see both required series complete, every required anchor solved, maximum coordinate gap `<= 0.075`, maximum pressure interpolation error `<= 0.35 bar`, exact-Hessian and postsolve status true for every accepted trace point, and no checker blockers.
**Stop Criteria:** Stop if the native point route cannot solve a required Figure 2 anchor exactly, if accepted points do not expose exact-Hessian or postsolve receipts, if trace completeness requires broad native continuation work, or if branch tracing cannot remain internal without public API claims.
**Avoid:** Do not add electrolyte, reactive, CE, CPE, generalized phase-count, HELD Stage I/II, public branch-tracing API, Gross-specific native C++ code, hidden coordinate substitution, or acceptance credit based only on interpolation.
**Risk:** If the trace gate is too weak, smooth plots can still mask missing branch solves; if it is too broad, this slice can turn into native continuation work and block near-term M4 validation.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py`; `packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py`; `analyses/paper_validation/2002_gross/shared/results/figure_02_trace_summary.json`.
**Files To Modify:** `analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py`; `scripts/validation/check_gross_2002_full_replication.py`; `tests/native/contracts/test_gross_2002_full_replication_checker.py`; `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`; `docs/superpowers/milestones/M4-equilibrium/README.md`.
**Files To Avoid:** Native C++ equilibrium implementation files, public `epcsaft_equilibrium.__init__.py` exports, provider EOS files, regression package files, electrolyte/reactive route files, unrelated Gross 2002 figure folders except shared manifest/summary output.
**Source Of Truth:** Approved spec, Figure 2 retained source rows, `Equilibrium(...).solve()` point-route contract, normalized result diagnostics, full-replication checker schema, and M4 GFPE evidence doctrine.
**Read Path:** Figure 2 source rows become `BranchTraceAnchor` records; `trace_boundary_route(...)` calls `Equilibrium(...).solve()`; branch trace diagnostics become model CSV rows and the shared Figure 2 trace summary; checker reads manifest artifacts and trace requirements.
**Write Path:** Reusable trace code stays under `packages/epcsaft-equilibrium`; Figure 2 generated artifacts stay under `analyses/paper_validation/2002_gross/figures/figure_02`; checker evidence stays in the shared manifest and summary.
**Integration Points:** `epcsaft_equilibrium.Equilibrium`, `EquilibriumSolverOptions.continuation_state`, `EquilibriumResult.diagnostics`, Figure 2 generator, full-replication checker, M4 README evidence table.
**Migration Or Cutover:** Land the package tracer behind internal imports, then migrate Figure 2 to it and remove the displaced local solve loop in the same PR.
**Replaced Path Handling:** Delete the obsolete Figure 2 local route-loop helpers once the shared tracer is used; do not leave wrappers that forward to the new tracer without adding evidence.
**Acceptance Proof Gate:** The PR cannot close unless the package tests, checker tests, Figure 2 regeneration, full-replication checker, `git diff --check`, plan validators, and cleanup hook all pass.

## Test Complete And Metrics

Test complete means:

- `BranchTraceResult.complete` is true for Figure 2 `bubble_line` and `dew_line`.
- Every required source anchor for Figure 2 has a corresponding accepted trace point.
- `max_coordinate_gap <= 0.075` for both Figure 2 branches.
- `max_interpolation_error <= 0.35` in `P_bar` for both Figure 2 branches.
- `requested_coordinate_tolerance <= 2.0e-4` for accepted points.
- `max_refinement_iterations <= 8` and `max_points <= 240` are enforced as loud blockers.
- Every accepted trace point has `exact_hessian_available is True`, `hessian_approximation == "exact"`, and `postsolve_accepted is True`.
- Figure 2 still has `normalized_plot_score >= 8.0`, `branch_coverage_score == 1.0`, and `derivative_status == "verified_exact"` for both required series.

Initial numeric defaults for this implementation:

- `max_coordinate_gap`: `0.075`
- `max_interpolation_error`: `0.35`
- `requested_coordinate_tolerance`: `2.0e-4`
- `max_refinement_iterations`: `8`
- `max_points`: `240`

## Acceptance Coverage

- Shared trace object contract: Task 1.
- Adaptive refinement and loud incomplete traces: Task 2.
- Existing equilibrium point-route integration: Task 3.
- Checker rejection of sparse or missing trace evidence: Task 4.
- Figure 2 cutover from figure-local solve loop to shared tracer: Task 5.
- Full M4 validation evidence and docs update: Task 6.

## Non-Goals

- No public `EquilibriumTrace` or `Equilibrium(...).trace()` API.
- No native continuation, tangent, arclength, HELD Stage I/II, or phase-discovery implementation.
- No changes to Figures 3-10 beyond shared checker behavior and shared manifest schema compatibility.
- No broad capability claim beyond Figure 2 branch-trace evidence.
- No plot score threshold reduction.

### Task 1: Add Internal Branch Trace Data Contract

**Use Cases:**
- A package developer can create branch anchors, trace options, trace points, segments, and results without importing analysis scripts.
- Invalid route names, empty anchors, duplicate anchor ids, and out-of-range coordinates fail before any solver call.
- Acceptance evidence has stable fields for later checker cutover.

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py`
- Create: `packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py`

- [x] **Step 1: Write the failing data-contract tests**

  Add `packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py` with these tests:

  ```python
  from __future__ import annotations

  import pytest

  from epcsaft_equilibrium.branch_tracing import (
      BranchTraceAnchor,
      BranchTraceOptions,
      validate_branch_trace_inputs,
  )


  def test_branch_trace_options_validate_supported_route_and_anchor_ids() -> None:
      anchors = [
          BranchTraceAnchor(anchor_id="low", coordinate=0.05, source_role="bubble_line", required=True),
          BranchTraceAnchor(anchor_id="high", coordinate=0.25, source_role="bubble_line", required=True),
      ]
      options = BranchTraceOptions(route="bubble_pressure", component_index=1, fixed_variable="T_K", fixed_value=373.15)

      validate_branch_trace_inputs(options, anchors)


  def test_branch_trace_options_reject_duplicate_anchor_ids() -> None:
      anchors = [
          BranchTraceAnchor(anchor_id="same", coordinate=0.05, required=True),
          BranchTraceAnchor(anchor_id="same", coordinate=0.25, required=True),
      ]
      options = BranchTraceOptions(route="bubble_pressure", component_index=1, fixed_variable="T_K", fixed_value=373.15)

      with pytest.raises(ValueError, match="duplicate branch trace anchor id"):
          validate_branch_trace_inputs(options, anchors)


  def test_branch_trace_options_reject_unsupported_route() -> None:
      anchors = [BranchTraceAnchor(anchor_id="a", coordinate=0.5, required=True)]
      options = BranchTraceOptions(route="flash", component_index=1, fixed_variable="T_K", fixed_value=373.15)

      with pytest.raises(ValueError, match="unsupported branch trace route"):
          validate_branch_trace_inputs(options, anchors)
  ```

- [x] **Step 2: Run the failing test**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py -q
  ```

  Expected before implementation: fail with `ModuleNotFoundError: No module named 'epcsaft_equilibrium.branch_tracing'`.

- [x] **Step 3: Implement the data objects and validation**

  Create `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py` with frozen dataclasses for:

  ```python
  BranchTraceAnchor
  BranchTraceOptions
  BranchSolveRequest
  BranchTracePoint
  BranchTraceSegment
  BranchTraceResult
  ```

  Implement:

  ```python
  SUPPORTED_BOUNDARY_ROUTES = frozenset(
      {"bubble_pressure", "dew_pressure", "bubble_temperature", "dew_temperature"}
  )


  def validate_branch_trace_inputs(options: BranchTraceOptions, anchors: Sequence[BranchTraceAnchor]) -> None:
      ...
  ```

  Required validation behavior:

  - route must be in `SUPPORTED_BOUNDARY_ROUTES`;
  - `component_index` must be non-negative;
  - `fixed_variable` must be `T_K` or `P_bar`;
  - at least one anchor is required;
  - anchor ids must be unique;
  - anchor coordinates must be finite and strictly between `0.0` and `1.0`;
  - numeric tolerances and budgets must be positive.

- [x] **Step 4: Run the contract tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py -q
  ```

  Expected after implementation: the three data-contract tests pass.

- [x] **Step 5: Commit**

  Commit:

  ```bash
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py
  git commit -m "Add branch trace data contract"
  ```

### Task 2: Implement Adaptive Branch Refinement With Fake Solves

**Use Cases:**
- Required source anchors are solved before optional midpoint refinement.
- Segment acceptance blocks sparse branch evidence when coordinate gaps or interpolation error exceed configured thresholds.
- Continuation state from an accepted point is passed to neighboring solves.
- Replaced sparse-grid behavior cannot report completion when refinement budget is exhausted.
- Coordinate drift evidence blocks acceptance instead of silently substituting a nearby point.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py`

- [x] **Step 1: Add failing adaptive-refinement tests**

  Extend `test_branch_tracing.py` with a fake solver and tests for refinement:

  ```python
  from epcsaft_equilibrium.branch_tracing import (
      BranchSolveRequest,
      BranchTracePoint,
      trace_boundary_route,
  )


  def _fake_point(request: BranchSolveRequest, *, pressure_bar: float, solved_coordinate: float | None = None) -> BranchTracePoint:
      coordinate = request.coordinate if solved_coordinate is None else solved_coordinate
      return BranchTracePoint(
          point_id=f"{request.route}:{coordinate:.6f}",
          route=request.route,
          requested_coordinate=request.coordinate,
          solved_coordinate=coordinate,
          paired_coordinate=min(0.999, coordinate + 0.1),
          pressure_bar=pressure_bar,
          temperature_k=request.fixed_value if request.fixed_variable == "T_K" else 373.15,
          continuation_state_used=request.continuation_state,
          continuation_state_returned={"variables": [coordinate, pressure_bar]},
          exact_hessian_available=True,
          hessian_approximation="exact",
          postsolve_accepted=True,
          route_status="accepted",
          solver_status="Solve_Succeeded",
          residuals={},
          source_anchor_id=request.source_anchor_id,
          accepted=True,
          rejection_reason="",
      )


  def test_trace_refines_until_coordinate_gap_is_bounded() -> None:
      calls: list[float] = []

      def solver(request: BranchSolveRequest) -> BranchTracePoint:
          calls.append(request.coordinate)
          return _fake_point(request, pressure_bar=10.0 + request.coordinate)

      result = trace_boundary_route(
          anchors=[
              BranchTraceAnchor(anchor_id="left", coordinate=0.0 + 1.0e-3, required=True),
              BranchTraceAnchor(anchor_id="right", coordinate=0.30, required=True),
          ],
          options=BranchTraceOptions(
              route="bubble_pressure",
              component_index=1,
              fixed_variable="T_K",
              fixed_value=373.15,
              max_coordinate_gap=0.075,
              max_interpolation_error=0.35,
              max_refinement_iterations=8,
              max_points=240,
          ),
          solve_point=solver,
      )

      assert result.complete is True
      assert result.max_coordinate_gap <= 0.075
      assert len(calls) > 2


  def test_trace_rejects_coordinate_drift_beyond_tolerance() -> None:
      def solver(request: BranchSolveRequest) -> BranchTracePoint:
          return _fake_point(request, pressure_bar=10.0, solved_coordinate=request.coordinate + 0.01)

      result = trace_boundary_route(
          anchors=[BranchTraceAnchor(anchor_id="a", coordinate=0.25, required=True)],
          options=BranchTraceOptions(
              route="bubble_pressure",
              component_index=1,
              fixed_variable="T_K",
              fixed_value=373.15,
              requested_coordinate_tolerance=2.0e-4,
          ),
          solve_point=solver,
      )

      assert result.complete is False
      assert "coordinate_drift_exceeds_tolerance" in result.blockers
  ```

- [x] **Step 2: Run the failing adaptive tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py -q
  ```

  Expected before implementation: fail because `trace_boundary_route` and adaptive metrics do not exist.

- [x] **Step 3: Implement `trace_boundary_route(...)`**

  In `branch_tracing.py`, implement:

  ```python
  def trace_boundary_route(
      *,
      anchors: Sequence[BranchTraceAnchor],
      options: BranchTraceOptions,
      solve_point: Callable[[BranchSolveRequest], BranchTracePoint],
  ) -> BranchTraceResult:
      ...
  ```

  Required behavior:

  - solve required anchors first;
  - build accepted points from successful solves only;
  - reject points with missing exact Hessian, non-exact Hessian approximation, missing postsolve acceptance, or coordinate drift beyond tolerance;
  - carry the nearest accepted point's returned continuation state into midpoint refinement solves;
  - compute segment coordinate gap and linear-interpolation error from midpoint solves;
  - refine segments while any segment violates `max_coordinate_gap` or `max_interpolation_error`;
  - stop with blockers when `max_refinement_iterations` or `max_points` is exhausted;
  - set `BranchTraceResult.complete` only when required anchors and all segments pass.

- [x] **Step 4: Run the branch tracing tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py -q
  ```

  Expected after implementation: all branch tracing tests pass.

- [x] **Step 5: Commit**

  Commit:

  ```bash
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py
  git commit -m "Add adaptive branch trace refinement"
  ```

### Task 3: Add The Equilibrium Point-Solve Adapter

**Use Cases:**
- Figure scripts can request branch traces without reimplementing `Equilibrium(...).solve()` loops.
- Bubble routes use liquid composition `x`; dew routes use vapor composition `y`.
- Exact-Hessian and postsolve receipts are copied from `EquilibriumResult.diagnostics`.
- The internal tracer remains importable from `epcsaft_equilibrium.branch_tracing` but is not exported from public `epcsaft_equilibrium.__init__`.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py`

- [x] **Step 1: Add failing adapter tests with a fake `Equilibrium` class**

  Add tests that monkeypatch the adapter's equilibrium class and assert:

  - `bubble_pressure` calls are constructed with `x=[1.0 - coordinate, coordinate]`;
  - `dew_pressure` calls are constructed with `y=[1.0 - coordinate, coordinate]`;
  - `continuation_state` is forwarded through `solver_options`;
  - result diagnostics populate `BranchTracePoint`.

- [x] **Step 2: Run the adapter tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py -q
  ```

  Expected before implementation: fail because the equilibrium adapter does not exist.

- [x] **Step 3: Implement the default point solver**

  In `branch_tracing.py`, add:

  ```python
  def solve_equilibrium_boundary_point(
      request: BranchSolveRequest,
      *,
      mixture: Any,
      solver_options: Mapping[str, Any] | None = None,
  ) -> BranchTracePoint:
      ...
  ```

  Required behavior:

  - construct `Equilibrium(mixture, route=request.route, T=..., x=...)` for bubble pressure traces;
  - construct `Equilibrium(mixture, route=request.route, T=..., y=...)` for dew pressure traces;
  - construct the temperature-route equivalents when `fixed_variable == "P_bar"`;
  - merge user solver options with `continuation_state` from the request;
  - convert pressure from Pa to bar for trace output;
  - copy `exact_hessian_available`, `hessian_approximation`, `postsolve_accepted`, `route_status`, `solver_status`, `iteration_count`, `pressure_consistency_norm`, and `chemical_potential_consistency_norm` into the trace point.

- [x] **Step 4: Add a convenience wrapper**

  Add:

  ```python
  def trace_equilibrium_boundary_route(
      mixture: Any,
      *,
      anchors: Sequence[BranchTraceAnchor],
      options: BranchTraceOptions,
  ) -> BranchTraceResult:
      ...
  ```

  This wrapper should call `trace_boundary_route(...)` with `solve_equilibrium_boundary_point(...)`.

- [x] **Step 5: Run the adapter tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py -q
  ```

  Expected after implementation: all adapter tests pass without requiring native execution.

- [x] **Step 6: Commit**

  Commit:

  ```bash
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/branch_tracing.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py
  git commit -m "Add equilibrium branch trace adapter"
  ```

### Task 4: Gate Full Replication On Retained Trace Completeness

**Use Cases:**
- An accepted Figure 2 manifest record without `trace_summary_json` is blocked.
- A trace summary with missing required series is blocked.
- A trace summary with incomplete anchors, excessive coordinate gap, excessive pressure interpolation error, missing exact-Hessian proof, or missing postsolve proof is blocked.
- The checker cutover prevents the old sparse-curve acceptance path from returning a clean campaign result.

**Files:**
- Modify: `scripts/validation/check_gross_2002_full_replication.py`
- Modify: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [x] **Step 1: Add failing checker tests for trace requirements**

  Extend `tests/native/contracts/test_gross_2002_full_replication_checker.py` with tests that add this accepted Figure 2 record:

  ```python
  {
      "figure_id": "figure_02",
      "plot_family": "vle",
      "replication_status": "accepted",
      "counts_toward_completion": True,
      "acceptance_threshold": 8.0,
      checker.SECOND_ORDER_REQUIRED_FIELD: True,
      "source_identity_status": "resolved",
      "required_series": ["bubble_line", "dew_line"],
      "requires_branch_trace": True,
      "trace_requirements": {
          "max_coordinate_gap": 0.075,
          "max_interpolation_error": 0.35,
          "required_series": ["bubble_line", "dew_line"],
      },
      "artifacts": artifacts,
  }
  ```

  Add one test where `artifacts` lacks `trace_summary_json` and expect blocker:

  ```text
  gross_2002_figure_02_trace_summary_json_missing
  ```

  Add one test where the trace summary reports `complete: false` for `bubble_line` and expect blocker:

  ```text
  gross_2002_figure_02_trace_bubble_line_incomplete
  ```

- [x] **Step 2: Run the failing checker tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected before implementation: fail because trace requirements are ignored.

- [x] **Step 3: Implement trace summary validation**

  In `check_gross_2002_full_replication.py`, add helper functions that:

  - read `artifacts["trace_summary_json"]` when `record["requires_branch_trace"] is true`;
  - require a `traces` array;
  - index traces by `series`;
  - require every `trace_requirements.required_series` item;
  - require `complete is true`;
  - require `solved_required_anchor_count >= required_anchor_count`;
  - require `max_coordinate_gap <= trace_requirements.max_coordinate_gap`;
  - require `max_interpolation_error <= trace_requirements.max_interpolation_error`;
  - require `exact_hessian_verified is true`;
  - require `postsolve_verified is true`;
  - append deterministic blocker names under `gross_2002_<figure_id>_trace_<series>_<reason>`.

- [x] **Step 4: Run checker tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected after implementation: checker tests pass.

- [x] **Step 5: Commit**

  Commit:

  ```bash
  git add scripts/validation/check_gross_2002_full_replication.py tests/native/contracts/test_gross_2002_full_replication_checker.py
  git commit -m "Require branch trace evidence for accepted Figure 2"
  ```

### Task 5: Cut Figure 2 Generation Over To The Shared Tracer

**Use Cases:**
- Figure 2 model generation uses the shared tracer for both `bubble_line` and `dew_line`.
- The displaced figure-local solve loop is removed rather than wrapped.
- The retained trace summary proves the low-composition branch is continuous because points were solved, not because the renderer smoothed a sparse curve.
- Render-only mode still reads retained model data and native receipt without running new native solves.

**Files:**
- Modify: `analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Create: `analyses/paper_validation/2002_gross/shared/results/figure_02_trace_summary.json`
- Modify generated artifacts under `analyses/paper_validation/2002_gross/figures/figure_02/results/`

- [x] **Step 1: Add Figure 2 trace summary writing**

  In `generate_data.py`, add constants:

  ```python
  TRACE_SUMMARY_JSON = SHARED_DIR / "results" / f"{FIGURE_ID}_trace_summary.json"
  FIGURE_2_TRACE_OPTIONS = {
      "max_coordinate_gap": 0.075,
      "max_interpolation_error": 0.35,
      "requested_coordinate_tolerance": 2.0e-4,
      "max_refinement_iterations": 8,
      "max_points": 240,
  }
  ```

- [x] **Step 2: Replace `_solve_route_point(...)` and `_solve_series(...)`**

  Remove the old route-loop helpers and add a Figure 2 function that:

  - creates `BranchTraceAnchor` records from `_series_compositions(...)`;
  - calls `trace_equilibrium_boundary_route(...)` once for `bubble_line`;
  - calls `trace_equilibrium_boundary_route(...)` once for `dew_line`;
  - fails with `RuntimeError` when either result is incomplete;
  - converts accepted `BranchTracePoint` records into existing model CSV rows.

- [x] **Step 3: Write `trace_summary.json`**

  Serialize a summary shaped like:

  ```json
  {
    "figure_id": "figure_02",
    "trace_contract": "m4_boundary_route_trace_v1",
    "traces": [
      {
        "series": "bubble_line",
        "route": "bubble_pressure",
        "complete": true,
        "required_anchor_count": 0,
        "solved_required_anchor_count": 0,
        "accepted_point_count": 0,
        "max_coordinate_gap": 0.0,
        "max_interpolation_error": 0.0,
        "exact_hessian_verified": true,
        "postsolve_verified": true,
        "blockers": []
      }
    ]
  }
  ```

  Fill every numeric value from `BranchTraceResult`; do not leave zero counts in the real artifact.

- [x] **Step 4: Update manifest artifacts and trace requirements**

  Update Figure 2's manifest record to include:

  ```json
  "requires_branch_trace": true,
  "trace_requirements": {
    "max_coordinate_gap": 0.075,
    "max_interpolation_error": 0.35,
    "required_series": ["bubble_line", "dew_line"]
  }
  ```

  Add artifact:

  ```json
  "trace_summary_json": "analyses/paper_validation/2002_gross/shared/results/figure_02_trace_summary.json"
  ```

- [x] **Step 5: Regenerate Figure 2**

  Run:

  ```bash
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py
  ```

  Expected: the script exits `0`, writes `model_curve.csv`, `plotted_data.csv`, `fit_statistics.csv`, `trace_summary.json`, `figure_02.png`, `figure_02.svg`, and `figure_02.pdf`.

- [x] **Step 6: Run Figure 2 folder contract**

  Run:

  ```bash
  uv run --no-sync python analyses/paper_validation/scripts/check_figure_contract.py analyses/paper_validation/2002_gross/figures/figure_02
  ```

  Expected: exits `0` and prints `paper_validation_figure_contract_ok`.

- [x] **Step 7: Commit**

  Commit:

  ```bash
  git add analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_02/results analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json
  git commit -m "Use branch tracing for Gross 2002 Figure 2"
  ```

### Task 6: Validate The Full Acceptance Gate And Update M4 Evidence

**Use Cases:**
- The final PR proves the package tracer, checker cutover, Figure 2 regenerated artifacts, and M4 evidence view together.
- The old sparse-curve acceptance path is displaced by a retained branch trace artifact.
- Validation receipts are complete enough for issue closure and later merge.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify generated summaries under `analyses/paper_validation/2002_gross/shared/results/`

- [x] **Step 1: Build the equilibrium native target if needed**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  ```

  Expected: exits `0`.

- [x] **Step 2: Run focused tests**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected: exits `0`.

- [x] **Step 3: Run full Gross 2002 replication checker**

  Run:

  ```bash
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native --write-summary
  ```

  Expected: exits `0`, reports `complete: true`, and reports no Figure 2 trace blockers.

- [x] **Step 4: Update M4 README evidence**

  Update `docs/superpowers/milestones/M4-equilibrium/README.md` to record:

  - the new plan path;
  - the shared internal branch tracer as a validation primitive;
  - Figure 2 trace-summary evidence;
  - the checker command from Step 3.

- [x] **Step 5: Run docs validation**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

  Expected: exits `0`.

- [x] **Step 6: Run diff and cleanup checks**

  Run:

  ```bash
  git diff --check
  ```

  Expected: exits `0`.

  Run:

  ```bash
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: exits `0` and reports no matching leftover Codex processes.

- [x] **Step 7: Commit**

  Commit:

  ```bash
  git add docs/superpowers/milestones/M4-equilibrium/README.md analyses/paper_validation/2002_gross/shared/results
  git commit -m "Record branch tracing validation evidence"
  ```

## Proof Oracle

Run the full oracle before issue or PR closeout:

```bash
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py
uv run --no-sync python analyses/paper_validation/scripts/check_figure_contract.py analyses/paper_validation/2002_gross/figures/figure_02
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native --write-summary
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

## Route Policy For Implementation

Use `superpowers:test-driven-development` for Tasks 1-5. Use systematic diagnosis if any Figure 2 generated trace is incomplete, if exact-Hessian receipts disappear, or if the regenerated Figure 2 score drops below `8.0`.

Use `superpowers:verification-before-completion` before claiming the plan is complete.

Recommended next route after this plan is accepted:

```text
superpowers-project:create-issues
```

Recommended issue count: one vertical-slice issue titled:

```text
Add internal adaptive branch tracing for M4 boundary-route validation
```
