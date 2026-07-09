# M4 CE Robustness Follow-Up Audit Findings

## Scope And Review Question

This audit reviews how the seven CE robustness issues landed on branch
`codex/m4-ce-generic-pope-homotopy-continuation` and converts the remaining
risks into implementation-ready repair work.

Review question: after retained diagnostics, physical proof correction, EOS
activity continuation, caller-seed escalation, reaction scaling, feasible
initialization, and failure taxonomy landed, what still keeps CE convergence
from being sharply diagnosable and robust?

## Companion Skills Used

- `superpowers-project:initiate-workflow`
- `superpowers-project:audit-project`
- `diagnose`
- `chemical-engineer`
- `jetbrains`

## Checked Artifacts

- Commit range: `79a6bc52..2eeb868f`
- Native CE solver: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Native CE objective: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.cpp`
- Native feasible initializer: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/feasible_initialization.cpp`
- Python diagnostics adapter: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Public API tests: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Native EOS activity tests: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`
- Standalone CE checker: `scripts/validation/check_standalone_ce_gate.py`
- Retained MEA artifacts under `analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/results/`

## Findings

### P2: EOS Activity Failures Still Hide The Exact Failing Proof Gate

**Evidence:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py:277`
classifies any rejected EOS-activity payload as `eos_activity_failure` before
checking balance, stationarity, proof-corrector, or Ipopt status.

**Impact:** The classification preserves the EOS context, but it weakens the
stated acceptance goal: failures should identify the exact failing proof gate.
EOS activity should be context evidence, not a replacement for the failing gate.

**Repair Requirement:** Preserve `activity_model` and add EOS context metadata,
but classify rejected EOS payloads by initialization, balance, stationarity,
proof correction, or Ipopt gate first. Add tests for EOS stationarity,
balance, proof-corrector, and Ipopt failure cases.

**Proof Oracle Candidate:** Focused API tests in
`packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py` plus
standalone checker proof.

### P2: Caller-Seed Escalation Drops Original Native Exception Evidence

**Evidence:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp:1247`
and `:1324` catch `std::exception` from caller-seeded solves and continue to
CE-owned initialization without preserving the exception type or message.

**Impact:** Escalation is useful, but a failed caller seed can become a generic
`caller_seed_final_proof_accepted: false` with no reproducible cause. This
makes seed sensitivity harder to debug.

**Repair Requirement:** Record caller-seed rejection reason, exception message,
and whether escalation followed an exception or a rejected proof. Expose these
fields through pybind and public diagnostics without changing accepted results.

**Proof Oracle Candidate:** A red test with a pathological positive caller seed
that forces escalation and asserts preserved rejection evidence.

### P3: EOS Activity Continuation Uses A Fixed Three-Point Grid

**Evidence:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp:1131`
sets `activity_lambdas = {0.0, 0.5, 1.0}`.

**Impact:** The landed path is useful, but it is a fixed ladder rather than a
robust continuation controller. Hard EOS activity cases may need step
reduction or more gradual advance, and easy cases should not require a
hard-coded interpretation of robustness.

**Repair Requirement:** Add an adaptive activity-continuation controller with
minimum step, maximum stages, accepted-step trace, rejected-step trace, and
final proof diagnostics. Preserve the current `{0.0, 0.5, 1.0}` behavior as the
normal easy-case trace when it succeeds.

**Proof Oracle Candidate:** Native tests that force a rejected intermediate
activity step and verify step bisection/recovery evidence, plus current EOS
activity success tests.

### P3: Assistance Level Is Not Summarized As A First-Class Diagnostic

**Evidence:** The branch now exposes seed escalation, homotopy, initializer
ladder, reaction scaling, and physical proof-corrector details, but callers must
manually infer how assisted a solve was from several nested fields.

**Impact:** Users still cannot quickly answer whether a point was direct,
initialized, homotopy-assisted, corrected, escalated from a bad seed, or
EOS-activity assisted. This was the user-facing question that triggered the
review.

**Repair Requirement:** Add a compact `assistance_summary` diagnostic with
level, mechanisms, final proof source, seed source, homotopy stage count,
corrector use, and escalation status. Keep detailed diagnostics unchanged.

**Proof Oracle Candidate:** API tests for direct ideal, bad caller seed,
homotopy/corrector-assisted MEA, and EOS activity paths.

### P3: Retained Artifact Diffs Are Too Noisy For Review

**Evidence:** The seven-issue commit range updates retained CSV artifacts with
large row-level diffs even when the primary semantic change is diagnostic
metadata.

**Impact:** Reviewers must scan thousands of CSV changed lines to discover the
actual semantic change. That increases review risk and makes future retained
artifact updates harder to trust.

**Repair Requirement:** Add a retained-artifact review digest that reports row
counts, column sets, numeric extrema, and stable hashes for retained CE CSV/JSON
artifacts. Wire it into the standalone checker so semantic review can start
from the digest before inspecting raw CSV diffs.

**Proof Oracle Candidate:** Checker contract tests that reject missing digest
fields and validate the digest against current retained artifacts.

### P3: There Is No Single Follow-Up Confidence Gate For This Robustness Tranche

**Evidence:** The loop used many focused commands, but there is no durable
repo-owned command that says the CE robustness follow-up branch is healthy.

**Impact:** Future agents must reconstruct which tests, checkers, and lint
commands matter for this tranche. That makes regression proof harder than it
needs to be.

**Repair Requirement:** Add a lightweight `check_ce_robustness_followup.py`
validator or equivalent checker mode that emits JSON evidence for the core
follow-up invariants without running an unbounded full suite.

**Proof Oracle Candidate:** A contract test for the checker plus one direct
checker execution with `--require-complete`.

### P3: EOS Nonideality Evidence Is Thinner Than Ideal MEA Evidence

**Evidence:** EOS activity continuation has native/API tests, while ideal MEA
has retained 322-state evidence, shuffled replay, and strict checker gates.

**Impact:** The branch improves EOS activity mechanics, but it should not be
interpreted as MEA-level EOS nonideality validation.

**Repair Requirement:** Add an EOS activity diagnostic matrix that exercises
both `eos_x_phi` and `eos_x_gamma` through public diagnostics, success and
classified-failure cases, derivative backend evidence, and retained checker
summary fields. Avoid claiming literature MEA nonideality until source-backed
data exists.

**Proof Oracle Candidate:** Native/API tests and checker JSON evidence showing
EOS activity modes, derivative backend, continuation trace, failure gate, and
explicit capability boundary.

## Healthy Checks And Non-Findings

- Verified: final acceptance remains based on unscaled physical balance and
  reaction stationarity, not scaled diagnostic stationarity.
- Verified: retained MEA ideal speciation evidence is substantially stronger
  than before, with 322 accepted state points, no source-oracle seed use, and
  physical proof-corrector repair evidence.
- Verified: issue #389 added a failure taxonomy and the checker rejects
  retained `unclassified_failure`.
- Inference: the algorithm is materially more robust than before, but still
  assisted; a direct solve is not the common hard-case story.

## Recommended Repair Route

Route this audit to `superpowers-project:write-plan`, then
`superpowers-project:create-issues`, then `superpowers-project:loop-controller`
with direct current-thread `superpowers-project:resolve-issue` execution for
AFK-ready slices.

## Proof Oracle Candidates

- `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q`
- `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py -q`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_standalone_ce_gate.py -q`
- `uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete`
- `uv run --no-sync python -m ruff check <changed-python-files>`
- `uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path <plan>`
- `uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path <plan>`
- `uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <issue-mirror>`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Open Questions

- No blocker: this follow-up should remain M4-owned under
  `packages/epcsaft-equilibrium`, with only small provider/core touches when
  public exception diagnostics require it.
- No blocker: issue mirrors can be local pre-publication mirrors for immediate
  loop execution, then published later if desired.
