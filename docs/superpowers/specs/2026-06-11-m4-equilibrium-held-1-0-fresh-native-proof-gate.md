# M4 Equilibrium HELD 1.0 Fresh Native Proof Gate

Milestone: `M4 - Equilibrium`
Affected package: `packages/epcsaft-equilibrium`
Status: `draft`
Created: `2026-06-11`

## Summary

This spec records the post-merge truth for HELD 1.0 after #241 and #188:
Stage II and Stage III are complete on current `main` when the native extension
has been rebuilt from the merged sources. The earlier incomplete Stage II/III
result came from running the validation scripts against a stale local native
extension after the PRs had merged.

The purpose of this spec is to prevent stale native artifacts from creating
false HELD status, false blocked-state analysis, or misleading validation
plots. Any future HELD 1.0 admission evidence, GFPE fixture checker output, or
milestone plot must include a fresh native build receipt or an equivalent
native freshness receipt tied to the current commit.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` says deterministic
  TPD/candidate screening is useful route support, not full HELD.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  requires continuous TPD, HELD Stage I, Stage II dual discovery, and Stage III
  Ipopt refinement before phase-discovery admission can be counted.
- Verified: #241 closed the neutral Stage II replay gate and #188 closed the
  source-backed neutral TP-flash fixture gate.
- Verified: after rebuilding the native extension on current `main`, the
  command `uv run --no-sync python scripts/validation/check_phase_discovery.py
  --json --include-route-refinement` reports `complete: true`,
  `held_stage_ii_dual_phase_discovery:
  verified_dual_loop_replayable`, and `held_stage_iii_ipopt_refinement:
  verified_current_route_refinement_consumed_stage_ii_replay`.
- Verified: after the same rebuild, `uv run --no-sync python
  scripts/validation/check_neutral_tp_flash_fixture.py
  --generate-phase-discovery --json --require-complete` reports `complete:
  true` and `held_tpd_admission.accepted: true`.
- Verified: after the same rebuild, focused neutral LLE HELD route tests pass:
  `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian`
  and
  `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers`.

## What Actually Happened

The status rows were not algorithm failures after the rebuild. They were a
validation hygiene failure:

1. `main` was synced and #241/#188 code was merged.
2. The local native `.pyd` still reflected an older C++ build.
3. `check_phase_discovery.py` loaded that older extension and reported
   deterministic candidate screening with no Stage II replay metadata.
4. The local evidence plot was generated from that stale extension.
5. Rebuilding with
   `uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium
   --build-only --parallel 4` restored the expected Stage II replay and Stage
   III replay-consumption diagnostics.

Closed issue state was not the proof. The fresh native validation receipts were
the proof.

## Fresh-Native Evidence Contract

Any future HELD 1.0, GFPE, neutral TP flash, neutral LLE, boundary workflow, or
phase-discovery evidence generator must satisfy this contract before its output
is treated as milestone evidence:

- The repo is synced to the intended commit.
- Native equilibrium sources changed since the last trusted build, or the build
  freshness state is unknown.
- The equilibrium native build is refreshed before running admission scripts.
- The evidence records the command used for native build refresh.
- The evidence records the commit hash used for the run.
- The evidence records the native module path imported by Python.
- The evidence records the relevant gate command and its pass/fail result.
- Generated figures and retained CSVs are regenerated after the fresh build,
  not before it.

## Acceptance Criteria

- A HELD/GFPE validation receipt cannot claim Stage II or Stage III status
  unless it also records a fresh-native receipt for the current commit.
- `scripts/validation/check_phase_discovery.py` with
  `--include-route-refinement --require-complete` is the canonical neutral HELD
  1.0 stage gate.
- `scripts/validation/check_neutral_tp_flash_fixture.py
  --generate-phase-discovery --json --require-complete` is the canonical
  source-backed neutral TP-flash fixture gate.
- Plot-generating analysis scripts that display HELD stage status must retain
  the gate output used for plotting.
- Plot text must be data-driven. It must not keep stale text saying Stage II or
  Stage III are incomplete when retained status rows are verified.
- The cleanup hook and `git status --short --branch` are run before any final
  merge or evidence handoff.

## Recommended Implementation Issue

Create one M4 task if this proof gate should be enforced by scripts instead of
process discipline:

```text
Title: M4: add fresh-native receipts to HELD and GFPE validation artifacts
Milestone: M4 - Equilibrium
Type: Task
Package: equilibrium
Backend: Ipopt
Readiness: ready
```

Issue body:

```text
Add a fresh-native evidence receipt to the HELD/GFPE validation path so stale
native builds cannot produce false Stage II/III status or misleading milestone
plots.

Acceptance:
- The phase-discovery checker or its retained summary records current commit,
  native module path, and build-refresh command or freshness proof.
- Neutral TP-flash fixture evidence records the same native freshness fields.
- The issue 188 analysis evidence regenerates HELD gate rows from the fresh
  native extension and refuses stale status text.
- Validation docs explain that closed PRs are evidence only after the local
  native extension has been rebuilt or proven current.

Proof:
- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium
  --build-only --parallel 4
- uv run --no-sync python scripts/validation/check_phase_discovery.py --json
  --include-route-refinement --require-complete
- uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py
  --generate-phase-discovery --json --require-complete
- uv run --no-sync python run_pytest.py
  packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers
  -q
- uv run --no-sync python scripts/dev/validate_project.py docs
```

## Non-Goals

- No new HELD algorithm work is requested by this spec.
- No associating, electrolyte, reactive, CE, or CPE admission is created here.
- No public route is added here.
- No source-backed neutral LLE benchmark is created here; that is a separate
  spec.

## Self-Review

- Placeholder scan: no unresolved placeholders remain.
- Scope check: this is a validation-evidence guard, not a broad algorithm spec.
- Ambiguity check: Stage II/III are complete after a fresh build; the remaining
  gap is preventing stale native evidence.
- Capability check: no new family or public route claim is made by this spec.
