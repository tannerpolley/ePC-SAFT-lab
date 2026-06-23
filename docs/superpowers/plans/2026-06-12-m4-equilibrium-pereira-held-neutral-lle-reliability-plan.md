# Pereira-Style HELD 1.0 Neutral LLE Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the full-campaign neutral LLE HELD reliability gate needed before associating GFPE can borrow the neutral HELD 1.0 algorithm path.

**Architecture:** Build a Python validation harness around the existing native neutral LLE phase-discovery and route-refinement paths. The harness samples neutral LLE-capable TP flash conditions, keeps only conditions that pass the unstable LLE prefilter, repeats each accepted condition independently, and writes retained JSON/CSV evidence for Stage I, Stage II, Stage III, material balance, phase count, objective agreement, and start-policy receipts. #246 fresh-native receipts remain a prerequisite and source-backed neutral LLE remains a separate showcase gate.

**Tech Stack:** Python validation scripts, pytest, `epcsaft_equilibrium._native`, Ipopt-backed native route refinement, retained CSV/JSON analysis artifacts, Superpowers Project docs validation.

---

## Source Evidence And Decisions

- Source specs:
  - `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
  - `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md`
  - `docs/superpowers/specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md`
  - `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
  - `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md`
- Milestone: `M4 - Equilibrium`
- Package: `packages/epcsaft-equilibrium`
- User decision: the reliability plan must target LLE/stability behavior, not a VLE-only TP flash fixture.
- User decision: require a full campaign rather than a smoke-only reliability gate.
- User decision: after this neutral reliability gate and exact association derivatives exist, a narrow two-phase associating proof may start while explicitly excluding generalized phase-set and LLLE claims until #189 is complete.
- Current evidence: `scripts/validation/check_phase_discovery.py` evaluates a synthetic neutral LLE binary, and `data/reference/equilibrium_benchmarks/neutral_tp_flash/methane_ethane_propane` is a source-backed liquid/vapor TP flash fixture. This plan keeps the workbook case as source-backed neutral TP evidence, but the new reliability campaign is LLE-centered.

## What Counts As Test Complete

The implementation is complete only when all of these are true:

- #246 fresh-native receipt work is merged or this plan's proof command records the same commit, native module path, build-refresh command, checker command, and pass/fail fields.
- `uv run --no-sync python scripts/validation/check_held_reliability.py --family neutral-lle --conditions 100 --repeats 100 --seed 1729 --require-complete --json --output-dir analyses/package_validation/held_lle_reliability/shared/results` completes with `complete: true`.
- The campaign accepts exactly 100 unstable neutral LLE conditions and runs exactly 100 independent route-refinement repeats for each accepted condition.
- The retained summary records `attempted_repeats: 10000`, `failed_repeats: 0`, and `accepted_conditions: 100`.
- Every accepted repeat reports:
  - `continuous_tpd_status == "converged"`
  - `held_stage_ii_status == "dual_loop_verified"`
  - `held_stage_ii_dual_loop_status == "verified"`
  - `held_stage_ii_bound_gap <= held_stage_ii_bound_tolerance`
  - `held_stage_iii_status == "ipopt_refinement_completed_current_route"`
  - `held_stage_iii_consumed_stage_ii_replay_metadata is true`
  - `solver_status == "success"`
  - `application_status == "solve_succeeded"`
  - `material_balance_norm <= 1.0e-8`
  - `pressure_consistency_norm <= 1.0e-3`
  - `ln_fugacity_consistency_norm <= 1.0e-6`
  - `phase_distance >= 1.0e-6`
  - `selected_candidate_count == 2`
- For each condition, all 100 repeats agree on phase count and selected phase roles.
- For each condition, the max spread in pressure-transformed objective across repeats is `<= 1.0e-6`.
- A failing repeat produces a compact reproduction record with condition index, repeat index, temperature, pressure, feed composition, random seed, native module path, stage statuses, and rejection reason.

## Non-Goals

- No associating, electrolyte, reactive, CE, or CPE route admission.
- No generalized phase-count or LLLE production claim.
- No source-backed neutral LLE public showcase; that remains owned by the neutral nonassociating LLE showcase spec.
- No replacement of #246; fresh-native receipt work remains the immediate ready issue.
- No capability promotion solely from this reliability campaign.

## File Map

- Create: `scripts/validation/check_held_reliability.py`
- Create: `tests/native/contracts/test_held_reliability_checker.py`
- Create: `analyses/package_validation/held_lle_reliability/README.md`
- Create: `analyses/package_validation/held_lle_reliability/shared/results/.gitkeep`
- Modify: `scripts/validation/check_phase_discovery.py`
- Modify: `scripts/validation/equilibrium_validation_runtime.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
- Modify: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

### Task 1: Extract Shared Neutral LLE Validation Runtime

**Use Cases:**
- The phase-discovery checker and reliability checker both need the same neutral LLE synthetic binary without duplicating parameters.
- A worker changes the LLE synthetic fixture once and both checker paths must exercise the same temperature, pressure, feed, and route metadata.
- A VLE-only TP flash fixture must not be accidentally used as LLE reliability evidence.

**Files:**
- Modify: `scripts/validation/equilibrium_validation_runtime.py`
- Modify: `scripts/validation/check_phase_discovery.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`

- [ ] **Step 1: Write the failing shared-runtime import test**

  Add this assertion block to `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py` in `test_stage9_phase_discovery_ladder_reports_distinct_layers` after the local `mix` construction:

  ```python
  from scripts.validation import equilibrium_validation_runtime as runtime

  runtime_case = runtime.neutral_lle_synthetic_case()
  assert runtime_case["route"] == "neutral_lle"
  assert runtime_case["temperature"] == pytest.approx(225.0)
  assert runtime_case["pressure"] == pytest.approx(1.0e6)
  assert runtime_case["composition"] == pytest.approx([0.5, 0.5])
  assert runtime_case["evidence_scope"] == "synthetic_neutral_lle_algorithm"
  ```

- [ ] **Step 2: Run the focused test and verify the expected failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
  ```

  Expected result before implementation: failure with `AttributeError: module 'scripts.validation.equilibrium_validation_runtime' has no attribute 'neutral_lle_synthetic_case'`.

- [ ] **Step 3: Add the shared runtime case**

  Add these functions to `scripts/validation/equilibrium_validation_runtime.py`:

  ```python
  def neutral_lle_synthetic_parameters() -> dict[str, np.ndarray]:
      return {
          "m": np.asarray([1.0, 2.0], dtype=float),
          "s": np.asarray([3.5, 4.0], dtype=float),
          "e": np.asarray([150.0, 250.0], dtype=float),
          "k_ij": np.asarray([[0.0, 0.5], [0.5, 0.0]], dtype=float),
      }


  def neutral_lle_synthetic_mixture() -> ePCSAFTMixture:
      return ePCSAFTMixture.from_params(neutral_lle_synthetic_parameters(), species=["A", "B"])


  def neutral_lle_synthetic_case() -> dict[str, object]:
      return {
          "case_label": "Synthetic neutral binary LLE phase-discovery case",
          "family_label": "PE-Neutral TP Flash",
          "route": "neutral_lle",
          "temperature": 225.0,
          "pressure": 1.0e6,
          "composition": [0.5, 0.5],
          "composition_role": "feed",
          "evidence_scope": "synthetic_neutral_lle_algorithm",
      }
  ```

- [ ] **Step 4: Replace duplicate checker parameters**

  In `scripts/validation/check_phase_discovery.py`, replace `_nonideal_lle_binary_mixture()` with `runtime.neutral_lle_synthetic_mixture()` and replace hard-coded route values with `runtime.neutral_lle_synthetic_case()`.

- [ ] **Step 5: Run the focused checks**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
  uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
  ```

  Expected result: both commands pass and the checker still reports `complete: true`.

- [ ] **Step 6: Commit**

  ```powershell
  git add scripts/validation/equilibrium_validation_runtime.py scripts/validation/check_phase_discovery.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py
  git commit -m "Share neutral LLE validation runtime"
  ```

### Task 2: Add The Full-Campaign Reliability Checker

**Use Cases:**
- A milestone worker needs one command that runs the Pereira-style full neutral LLE reliability campaign.
- A bad condition must fail loudly with a reproduction row instead of being averaged away.
- A passing campaign must retain enough data to support later #189 and associating-readiness planning.

**Files:**
- Create: `scripts/validation/check_held_reliability.py`
- Create: `tests/native/contracts/test_held_reliability_checker.py`
- Create: `analyses/package_validation/held_lle_reliability/shared/results/.gitkeep`
- Test: `tests/native/contracts/test_held_reliability_checker.py`

- [ ] **Step 1: Write checker unit tests around a fake runner**

  Create `tests/native/contracts/test_held_reliability_checker.py` with tests for:

  ```python
  def test_reliability_summary_requires_exact_campaign_size() -> None:
      from scripts.validation import check_held_reliability as checker

      summary = checker.summarize_campaign(
          conditions=[checker.ConditionResult(condition_index=0, accepted=True, repeats=[checker.accepted_repeat_for_test()])],
          required_conditions=100,
          required_repeats=100,
      )

      assert summary["complete"] is False
      assert "accepted_condition_count_mismatch" in summary["blockers"]
      assert "attempted_repeat_count_mismatch" in summary["blockers"]
  ```

  Add companion tests named:

  - `test_reliability_summary_accepts_full_clean_campaign`
  - `test_reliability_summary_rejects_objective_spread_above_tolerance`
  - `test_reliability_summary_records_first_failure_reproduction`

- [ ] **Step 2: Run the new tests and verify the expected failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_held_reliability_checker.py -q
  ```

  Expected result before implementation: import failure for `scripts.validation.check_held_reliability`.

- [ ] **Step 3: Implement the checker data model and summary logic**

  Create `scripts/validation/check_held_reliability.py` with:

  - `RepeatResult`
  - `ConditionResult`
  - `ReliabilityThresholds`
  - `accepted_repeat_for_test()`
  - `summarize_campaign(...)`
  - `build_parser()`
  - `main(...)`

  Required defaults:

  ```python
  DEFAULT_CONDITIONS = 100
  DEFAULT_REPEATS = 100
  DEFAULT_SEED = 1729
  DEFAULT_OUTPUT_DIR = Path("analyses/package_validation/held_lle_reliability/shared/results")
  DEFAULT_THRESHOLDS = ReliabilityThresholds(
      objective_spread_abs=1.0e-6,
      material_balance_norm=1.0e-8,
      pressure_consistency_norm=1.0e-3,
      ln_fugacity_consistency_norm=1.0e-6,
      phase_distance_min=1.0e-6,
  )
  ```

- [ ] **Step 4: Implement deterministic LLE condition sampling**

  Use this candidate pool:

  ```python
  FEED_GRID = [round(value, 6) for value in np.linspace(0.10, 0.90, 41)]
  TEMPERATURE_GRID = [215.0, 220.0, 225.0, 230.0, 235.0]
  PRESSURE_GRID = [0.8e6, 1.0e6, 1.2e6]
  ```

  Shuffle the Cartesian product with `np.random.default_rng(seed)` and keep a candidate only when the native phase-discovery and route-refinement result satisfies the accepted-repeat criteria. Fail if the fixed pool cannot provide 100 accepted unstable LLE conditions.

- [ ] **Step 5: Write retained outputs**

  The checker must write:

  - `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_summary.json`
  - `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_conditions.csv`
  - `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_repeats.csv`

  The summary JSON must include `complete`, `blockers`, `accepted_conditions`, `attempted_repeats`, `failed_repeats`, `seed`, `thresholds`, `native_receipt`, and `first_failure`.

- [ ] **Step 6: Run unit tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_held_reliability_checker.py -q
  ```

  Expected result: all checker contract tests pass without invoking the full native campaign.

- [ ] **Step 7: Commit**

  ```powershell
  git add scripts/validation/check_held_reliability.py tests/native/contracts/test_held_reliability_checker.py analyses/package_validation/held_lle_reliability/shared/results/.gitkeep
  git commit -m "Add HELD LLE reliability checker"
  ```

### Task 3: Add Independent Repeat And Start-Policy Receipts

**Use Cases:**
- The campaign must prove that repeats are independent calculations and do not reuse hidden state from a prior accepted solve.
- If native initialization is deterministic, the retained evidence must say so honestly instead of implying Pereira's random tunneling behavior.
- Associating planning must be able to inspect whether neutral HELD reliability was proven with deterministic multi-starts or explicit random seeds.

**Files:**
- Modify: `scripts/validation/check_held_reliability.py`
- Modify: `scripts/validation/check_phase_discovery.py`
- Modify: `tests/native/contracts/test_held_reliability_checker.py`
- Test: `tests/native/contracts/test_held_reliability_checker.py`

- [ ] **Step 1: Add failing receipt tests**

  Add tests requiring every repeat row to contain:

  - `condition_index`
  - `repeat_index`
  - `run_id`
  - `process_id`
  - `native_start_policy`
  - `stage_i_start_count`
  - `candidate_start_sources`
  - `stage_ii_stopping_reason`
  - `hidden_state_carryover_allowed`

  Expected values for accepted campaign rows:

  ```python
  assert repeat["native_start_policy"] in {"deterministic_multistart", "seeded_multistart"}
  assert repeat["hidden_state_carryover_allowed"] is False
  assert repeat["stage_i_start_count"] > 0
  assert repeat["candidate_start_sources"]
  assert repeat["stage_ii_stopping_reason"] == "bound_gap_closed"
  ```

- [ ] **Step 2: Run tests and verify the expected failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_held_reliability_checker.py -q
  ```

  Expected result before implementation: receipt-key assertions fail.

- [ ] **Step 3: Implement repeat receipts**

  In `scripts/validation/check_held_reliability.py`, create a fresh `runtime.neutral_lle_synthetic_mixture()` for each repeat and record:

  ```python
  run_id = f"condition-{condition_index:03d}-repeat-{repeat_index:03d}"
  native_start_policy = "deterministic_multistart"
  hidden_state_carryover_allowed = False
  process_id = os.getpid()
  candidate_start_sources = list(postsolve.get("tpd_candidate_sources", []))
  ```

  If a future native start seed is added, switch only the receipt value to `seeded_multistart` when the repeat row includes the native seed used.

- [ ] **Step 4: Refuse incomplete start-policy evidence under `--require-complete`**

  The checker must add `missing_start_policy_receipt` to `blockers` when any accepted repeat lacks `native_start_policy`, `stage_i_start_count`, or `candidate_start_sources`.

- [ ] **Step 5: Run tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_held_reliability_checker.py -q
  ```

  Expected result: all checker contract tests pass.

- [ ] **Step 6: Commit**

  ```powershell
  git add scripts/validation/check_held_reliability.py scripts/validation/check_phase_discovery.py tests/native/contracts/test_held_reliability_checker.py
  git commit -m "Record HELD reliability start receipts"
  ```

### Task 4: Run And Retain The Full LLE Reliability Campaign

**Use Cases:**
- M4 needs retained proof that the neutral LLE HELD path is reliable across the full selected campaign.
- A future #189 or associating worker needs a concrete retained campaign artifact, not a prose claim.
- A failure must produce a compact first-failure record for debugging.

**Files:**
- Modify: `analyses/package_validation/held_lle_reliability/README.md`
- Generate: `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_summary.json`
- Generate: `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_conditions.csv`
- Generate: `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_repeats.csv`
- Test: `scripts/validation/check_held_reliability.py`

- [ ] **Step 1: Build fresh native equilibrium extension**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  ```

  Expected result: build succeeds and the checker imports the rebuilt native module.

- [ ] **Step 2: Run the prerequisite HELD stage gate**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
  ```

  Expected result: JSON contains `complete: true`, Stage II `verified_dual_loop_replayable`, and Stage III `verified_current_route_refinement_consumed_stage_ii_replay`.

- [ ] **Step 3: Run the full campaign**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_held_reliability.py --family neutral-lle --conditions 100 --repeats 100 --seed 1729 --require-complete --json --output-dir analyses/package_validation/held_lle_reliability/shared/results
  ```

  Expected result: JSON contains `complete: true`, `accepted_conditions: 100`, `attempted_repeats: 10000`, and `failed_repeats: 0`.

- [ ] **Step 4: Document retained artifacts**

  Create `analyses/package_validation/held_lle_reliability/README.md` with:

  ```markdown
  # HELD LLE Reliability Campaign

  This retained evidence is the neutral LLE Pereira-style reliability campaign
  for M4 HELD 1.0 pre-association planning. It is synthetic neutral LLE
  algorithm evidence, not source-backed public LLE showcase evidence.

  Retained outputs:

  - `shared/results/held_lle_reliability_summary.json`
  - `shared/results/held_lle_reliability_conditions.csv`
  - `shared/results/held_lle_reliability_repeats.csv`
  ```

- [ ] **Step 5: Commit**

  ```powershell
  git add analyses/package_validation/held_lle_reliability scripts/validation/check_held_reliability.py
  git commit -m "Retain HELD LLE reliability campaign"
  ```

### Task 5: Wire The Reliability Gate Into M4 Planning Docs

**Use Cases:**
- A future M4 worker must see that neutral LLE reliability is now a prerequisite for associating GFPE planning.
- #189 must continue to own generalized phase-set and LLLE-ready completeness rather than inheriting those claims from the two-phase reliability campaign.
- #190 must be allowed to start only as a narrow two-phase associating proof until #189 closes.

**Files:**
- Modify: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- Modify: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Test: `scripts/dev/validate_project.py`

- [ ] **Step 1: Update full-adoption status**

  Update `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md` so Gate B points to the retained campaign artifacts and says the reliability issue is complete only when the summary JSON reports `complete: true`.

- [ ] **Step 2: Preserve #189 scope**

  Add one sentence to #189's spec: "The neutral LLE reliability campaign is two-phase reliability evidence; generalized phase-set completion still requires #189's arbitrary phase-count and LLLE-ready checks."

- [ ] **Step 3: Preserve #190 scope**

  Add one sentence to #190's spec: "After the neutral LLE reliability gate and exact association derivatives, #190 may start a narrow two-phase associating proof, but it cannot claim generalized phase-set or associating LLLE coverage until #189 closes."

- [ ] **Step 4: Run docs validation**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

  Expected result: Sphinx docs build succeeds.

- [ ] **Step 5: Commit**

  ```powershell
  git add docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Document HELD LLE reliability gate"
  ```

## Proof Oracle

Run the proof in this order:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_held_reliability_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_held_reliability.py --family neutral-lle --conditions 100 --repeats 100 --seed 1729 --require-complete --json --output-dir analyses/package_validation/held_lle_reliability/shared/results
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Issue Creation Packet

Published M4 issue:

- https://github.com/ePC-SAFT/ePC-SAFT/issues/247

Execute this issue only after #246 is complete:

```text
Title: M4: add Pereira-style neutral LLE HELD reliability campaign
Milestone: M4 - Equilibrium
Type: Feature
Package: equilibrium
Backend: Ipopt
Readiness: blocked by #246 until fresh-native receipts are complete
Blocks: #189 and #190 where they depend on neutral HELD reliability evidence
```

Acceptance:

- `scripts/validation/check_held_reliability.py` exists with `--family neutral-lle`, `--conditions`, `--repeats`, `--seed`, `--require-complete`, `--json`, and `--output-dir`.
- Unit tests cover complete campaign summary, campaign-size rejection, objective-spread rejection, missing start-policy receipts, and first-failure reproduction output.
- The full command runs 100 accepted unstable neutral LLE conditions with 100 repeats each and writes retained JSON/CSV evidence.
- The campaign records current commit, native module path, build-refresh command or #246 freshness receipt, candidate start sources, start policy, stage statuses, route status, and first failure if any.
- The issue does not claim source-backed neutral LLE public evidence, generalized phase-count completeness, associating GFPE, electrolyte GFPE, reactive routes, CE, CPE, or capability promotion.

## Risk Notes

- The full campaign is intentionally expensive. Workers should use the unit tests and a small `--conditions 2 --repeats 2` local smoke command while developing, but completion requires the full 100 by 100 command.
- If the fixed synthetic LLE candidate pool cannot produce 100 accepted unstable conditions, the implementation must stop with the retained candidate audit instead of loosening the metric.
- If native initialization remains deterministic, the campaign can prove repeat reliability under deterministic multi-start receipts, but it must not claim stochastic tunneling equivalence.
- Source-backed neutral nonassociating LLE remains a separate public-evidence issue.
