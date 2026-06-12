# Fresh-Native HELD/GFPE Validation Receipts Implementation Plan

## Goal

Resolve GitHub issue #246: add fresh-native receipts to HELD and GFPE
validation artifacts so stale local native extensions cannot produce false
Stage II/III status, false blocked-state analysis, or misleading milestone
plots.

## Source Links

- Source Spec: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md`
- Source Issue: `docs/superpowers/issues/2026-06-12-m4-equilibrium-issue-0246-add-fresh-native-receipts-to-held-and-gfpe-validation-artifacts.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/246`
- Milestone: `M4 - Equilibrium`
- Package: `packages/epcsaft-equilibrium`

## Scope

This is a validation-evidence guard. It does not add a new HELD algorithm,
route, family, benchmark, or public capability. The task is to make the current
HELD/GFPE proof scripts and retained analysis artifacts loudly record or reject
native freshness before claiming Stage II/III completion.

## Task 1 - Add A Reusable Native Freshness Receipt

**Use Cases:**

- A developer runs the phase-discovery checker after merging native C++ changes
  and needs the retained JSON to show which commit and native extension were
  used.
- A stale local `.pyd` is accidentally imported after a merge; the validation
  path must avoid silently producing milestone evidence that looks current.

**Files:**

- `scripts/validation/check_phase_discovery.py`
- `scripts/validation/check_neutral_tp_flash_fixture.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/**`

**Steps:**

1. Inspect how each checker currently discovers the native module path and
   emits JSON.
2. Add a shared receipt shape that records current Git commit, imported native
   module path, build-refresh command or freshness proof, and checker command.
3. Keep failures loud when required freshness data cannot be determined for a
   milestone proof run.
4. Preserve existing checker behavior for ordinary diagnostic runs where
   `--require-complete` is not used.

## Task 2 - Carry Receipts Into Retained HELD/GFPE Analysis Evidence

**Use Cases:**

- The issue 188 analysis regenerates the HELD status plot and the CSV rows must
  prove they came from the fresh native extension.
- A future plot renderer sees stale or missing Stage II/III receipt data and
  must refuse stale explanatory text instead of rendering an outdated claim.

**Files:**

- `analyses/package_validation/issue_0188_neutral_tp_flash/scripts/generate_data.py`
- `analyses/package_validation/issue_0188_neutral_tp_flash/scripts/render_figures.py`
- `analyses/package_validation/issue_0188_neutral_tp_flash/shared/results/**`

**Steps:**

1. Extend retained JSON/CSV outputs with the fresh-native receipt fields.
2. Regenerate the HELD stage status retained data from the current native
   extension.
3. Keep figure text data-driven: Stage II and Stage III can only render as
   verified when the retained gate rows and native receipt agree.

## Task 3 - Document The Completion Rule And Validate The Gate

**Use Cases:**

- A future agent asks why closed PRs were not enough; the docs should point to
  the native freshness receipt as the actual completion evidence.
- The M4 queue needs a focused proof oracle that can be run before merge without
  broad equilibrium sweeps.

**Files:**

- `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md`
- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/pages/development_workflows.rst`

**Steps:**

1. Add or update the docs section that says closed PRs are evidence only after
   the local native extension has been rebuilt or proven current.
2. Update any retained HELD/GFPE evidence text that currently allows stale
   native status ambiguity.
3. Run the focused proof oracle and docs validation.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
uv run --no-sync python scripts/dev/validate_project.py docs
```

## Non-Goals

- No new HELD algorithm work.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No source-backed neutral LLE benchmark.
- No public capability promotion beyond the receipt-backed evidence already
  proven by #241 and #188.
