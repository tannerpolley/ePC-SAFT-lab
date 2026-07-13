# Associating Neutral LLE Gross 2002 Proof Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #145 by adding a source-backed internal neutral associating LLE proof that exercises implicit association Jacobian and Hessian coverage before any public associating GFPE admission.

**Architecture:** Keep #145 as an internal proof lane: Gross and Sadowski 2002 methanol/cyclohexane validates the association-aware LLE path, while public associating `route="lle"` admission stays closed until #190. Reuse the existing provider implicit-association sensitivity code and the equilibrium association mass-action block so every proof uses exact site sensitivities and Hessian evidence instead of an approximate association closure.

**Tech Stack:** Python validation scripts and pytest; C++/pybind11 native equilibrium blocks; CppAD implicit association sensitivities; Ipopt exact-Hessian route diagnostics; retained Gross and Sadowski 2002 paper-validation data.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md`
- Source Issue: `docs/superpowers/issues/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/145`
- Milestone: `M4 - Equilibrium`
- Package: `packages/epcsaft-equilibrium`
- Upstream provider package touched only for derivative evidence: `packages/epcsaft`
- Current queue state: #145 is `ready`; #190 is blocked by #145; #191 electrolyte waits behind the associating gates.
- IntelliJ receipt: IntelliJ MCP discovery exposed index/build tools, but the ePC-SAFT project was not attached in this session. Semantic code implementation must attach the repo in IntelliJ before changing native or Python route behavior.

## Source Evidence

- Gross and Sadowski 2002 paper markdown: `analyses/paper_validation/2002_gross/docs/md/source_01_gross_2002.md`
- Gross and Sadowski 2002 pure-component table: `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv`
- Gross and Sadowski 2002 binary-interaction table: `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv`
- Retained parameter bundle: `analyses/paper_validation/2002_gross/parameters/`
- Methanol/cyclohexane LLE/VLE source figure: `analyses/paper_validation/2002_gross/figures/figure_08/source/paper_source_01_gross_2002_figure_008.png`
- Water/1-pentanol stress source figure: `analyses/paper_validation/2002_gross/figures/figure_10/source/paper_source_01_gross_2002_figure_010.png`

## Acceptance Criteria

- [ ] Gross and Sadowski 2002 methanol/cyclohexane source data, parameters, and thresholds are retained in the repo and checked by a replayable command.
- [ ] Active association reports bounded site fractions, low mass-action residuals, exact first sensitivities, and exact second sensitivities for every solved liquid phase in the proof fixture.
- [ ] Native equilibrium block and phase-system diagnostics report exact association Hessian coverage for objective, pressure, mass-action, and Lagrangian-Hessian values.
- [ ] The associating LLE proof route solves or certifies the source-backed methanol/cyclohexane split without weakening neutral HELD/TPD postsolve checks.
- [ ] Public `Equilibrium(..., route="lle")` associating admission remains closed until #190.
- [ ] Capability and milestone evidence names the narrow proven configuration and does not broaden electrolyte, reactive, LLLE, or generalized associating phase-set claims.

## Test Complete And Metrics

Test complete means all #145 proof commands pass and the retained JSON checker reports `complete: true`.

Required numerical gates:

- `paper_data_rows >= 6` for the digitized Figure 8 liquid-liquid branch.
- All solved association site fractions satisfy `0.0 < XA <= 1.0 + 1e-12`.
- Per-phase mass-action infinity norm is `<= 1e-8`.
- Association first- and second-sensitivity arrays are finite and have nonzero entries above `1e-12`.
- Objective, pressure, mass-action, and Lagrangian Hessian blocks are finite and symmetric within `1e-8` absolute error.
- The source-backed methanol/cyclohexane checker records two liquid phases on opposite sides of the retained binodal with branch composition absolute error `<= 0.10` and temperature absolute error `<= 5.0 K` for the first internal proof. Tighter thresholds belong in follow-up validation after the route is stable.
- The public associating route gate remains closed for #145: the checker must report `public_route_state: closed_for_associating_inputs`.

### Task 1: Build The Gross 2002 Associating LLE Fixture

**Use Cases:**
- A validation worker can load methanol/cyclohexane PC-SAFT parameters and `k_ij=0.051` from retained Gross and Sadowski 2002 artifacts without hand-copying values from prose.
- The source-data checker fails loudly when Figure 8 data, parameter rows, thresholds, or source notes are missing.
- The fixture records the first proof target as one-associating-component LLE and records water/1-pentanol as a later stress target without expanding #145 completion.

**Files:**
- Create: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane/metadata.json`
- Create: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane/source_notes.md`
- Create: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane/pure_component_parameters.csv`
- Create: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane/binary_interactions.csv`
- Create: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane/experimental_phase_points.csv`
- Create: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane/thresholds.json`
- Create: `scripts/validation/check_associating_lle_gross_2002.py`
- Create: `tests/native/contracts/test_associating_lle_gross_2002_checker.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Write the failing checker contract.** Add tests that call `scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-route-closed` and assert missing fixture files produce explicit blocker keys: `source_data_missing`, `parameter_bundle_missing`, `thresholds_missing`, or `public_route_open_too_early`.
- [ ] **Step 2: Run the checker contract and verify the expected failure.** Run `uv run python run_pytest.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q`; expected result before fixture creation is failure on `source_data_missing`.
- [ ] **Step 3: Create the fixture from existing source artifacts.** Populate the new `data/reference/.../methanol_cyclohexane/` files from `analyses/paper_validation/2002_gross/parameters/`, Table 1, Table 2, and digitized Figure 8 points. Record units, pressure basis `1.013 bar`, source-line references, and digitization uncertainty in `source_notes.md`.
- [ ] **Step 4: Implement the checker.** The checker must parse the fixture, verify `methanol`, `cyclohexane`, `assoc_scheme=2B` for methanol, no association sites for cyclohexane, `k_ij=0.051`, finite thresholds, and at least six retained liquid-liquid source rows.
- [ ] **Step 5: Register the benchmark.** Add an `associating_lle` entry to `equilibrium-evidence-registry.yaml` naming the fixture path, source key `gross_2002`, phase family `neutral_associating_lle`, and status `internal_proof_for_issue_145`.
- [ ] **Step 6: Run the checker contract again.** Run `uv run python run_pytest.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q`; expected result is pass with the public route still closed.
- [ ] **Step 7: Commit.** Commit the fixture, checker, tests, and registry update with message `test: add Gross 2002 associating LLE source fixture`.

### Task 2: Prove Exact Implicit Association Hessian Coverage

**Use Cases:**
- Active association reports `cppad_implicit_association` first and second site sensitivities for the same state variables used by equilibrium phase blocks.
- Equilibrium Hessian diagnostics include association objective and pressure corrections, not only nonassociating phase-block curvature.
- Singular or unconverged association mass-action solves fail loudly with diagnostics instead of being accepted as proof.

**Files:**
- Modify: `packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py`
- Modify: `packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py`
- Modify: `packages/epcsaft/tests/native/state/test_fugacity_derivatives.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/blocks/test_association_block.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py`
- Modify if tests expose gaps: `packages/epcsaft/src/epcsaft/native/eos/residual/implicit_association/sensitivities.cpp`
- Modify if tests expose gaps: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/association_corrections.cpp`
- Modify if tests expose gaps: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/state_sensitivities.cpp`
- Modify if tests expose gaps: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/association_block.*`
- Modify if tests expose gaps: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/derivatives/phase_system_derivatives.*`

- [ ] **Step 1: Add failing coverage assertions.** Extend existing tests so they assert exact backend labels, finite first and second site sensitivities, symmetric association Hessian tensors, nonzero association Hessian contribution, and explicit failure for invalid association solves.
- [ ] **Step 2: Run the focused derivative tests.** Run `uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_fugacity_derivatives.py packages/epcsaft-equilibrium/tests/native/blocks/test_association_block.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py -q`; expected result is failure only on the newly added proof assertions.
- [ ] **Step 3: Repair native derivative propagation.** If a proof assertion fails, carry the implicit association first and second sensitivity response through the provider phase-state outputs and equilibrium phase-system Hessian assembly. Do not add approximation flags or alternate acceptance modes.
- [ ] **Step 4: Re-run the focused derivative tests.** Run the same command; expected result is pass with exact backend labels and symmetric Hessians.
- [ ] **Step 5: Commit.** Commit derivative proof updates with message `test: prove implicit association hessian coverage`.

### Task 3: Add The Internal Associating LLE Proof Route

**Use Cases:**
- A native diagnostic can solve or certify the Gross 2002 methanol/cyclohexane two-liquid split with active association and exact Hessian evidence.
- HELD/TPD postsolve diagnostics remain present for the selected liquid-liquid pair.
- The public Python `Equilibrium(..., route="lle")` constructor continues to reject associating inputs for #145, leaving public admission to #190.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/tests/equilibrium_support/equilibrium_cases.py`
- Modify if diagnostics need native exposure: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.*`
- Modify if eligibility diagnostics need refinement: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.*`
- Modify if result fields need Python access: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify if pybind exports need a diagnostic hook: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/extension.cpp`

- [ ] **Step 1: Write the failing native proof test.** Add `test_associating_lle_reference_values.py` to build the retained methanol/cyclohexane mixture, feed, and pressure, then assert active association, two liquid phases, exact Hessian diagnostics, bounded site fractions, low mass-action residuals, and retained HELD/TPD evidence.
- [ ] **Step 2: Keep the public route closed.** Extend `test_equilibrium.py` so `Equilibrium(mixture, route="lle", ...)` still raises for associating inputs during #145 and the error names the #190 admission gate.
- [ ] **Step 3: Run the focused tests and verify the expected failure.** Run `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py -q`; expected result is failure on missing internal proof diagnostics, while the public route rejection still passes.
- [ ] **Step 4: Implement the internal diagnostic path.** Add or expose a native diagnostic that accepts the Gross 2002 fixture, runs the two-liquid associating phase system with exact Hessian callbacks, reports site-fraction diagnostics per phase, and returns checker-ready fields. Keep this diagnostic out of the public route map.
- [ ] **Step 5: Re-run the focused tests.** Run the same command; expected result is pass with public route closed and internal proof complete.
- [ ] **Step 6: Commit.** Commit the internal route proof with message `feat: prove internal associating neutral LLE route`.

### Task 4: Close #145 And Prepare #190 Readiness

**Use Cases:**
- The M4 queue clearly shows #145 closed by internal proof, #190 as the next associating admission issue, and #191 electrolyte after association.
- Capability evidence names only the narrow Gross 2002 internal proof and does not claim public associating GFPE.
- GitHub dependency automation can move #190 from blocked to ready after #145 merges.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/issues/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md`

- [ ] **Step 1: Add narrow capability evidence.** Record an internal proof row such as `associating_neutral_lle_gross_2002_internal_exact_hessian` with source fixture, exact association Hessian backend, and public admission state `closed_until_issue_190`.
- [ ] **Step 2: Update contract tests.** Assert the capability row exists, names the Gross 2002 fixture, keeps `route="lle"` public associating admission closed, and keeps electrolyte/reactive route claims unchanged.
- [ ] **Step 3: Update M4 docs and issue mirrors.** Mark the proof evidence, explain why #190 is the next issue after #145, and keep #191 electrolyte behind the associating queue.
- [ ] **Step 4: Run the proof oracle.** Run every command in the Proof Oracle section below.
- [ ] **Step 5: Commit.** Commit closeout evidence with message `docs: record associating LLE proof gate for issue 145`.

## Proof Oracle

- `uv run python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete`
- `uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_fugacity_derivatives.py packages/epcsaft-equilibrium/tests/native/blocks/test_association_block.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py -q`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py tests/native/contracts/test_associating_lle_gross_2002_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Non-Goals And Boundaries

- No public associating GFPE admission in #145.
- No electrolyte route behavior or electrolyte capability claim.
- No reactive, CE, CPE, or LLLE behavior.
- No approximate explicit association closure accepted as exact evidence.
- No broad associating phase-count claim from the methanol/cyclohexane proof.
