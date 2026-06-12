---
issue: 246
title: "M4: add fresh-native receipts to HELD and GFPE validation artifacts"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/246"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md"
source_plan: "docs/superpowers/plans/2026-06-12-m4-equilibrium-fresh-native-held-gfpe-validation-receipts-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0246-fresh-native-held-gfpe-validation-receipts
last_synced: "2026-06-12"
---

# M4: add fresh-native receipts to HELD and GFPE validation artifacts

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/246
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md
**Source Plan:** docs/superpowers/plans/2026-06-12-m4-equilibrium-fresh-native-held-gfpe-validation-receipts-plan.md
Branch: codex/issue-0246-fresh-native-held-gfpe-validation-receipts
AFK/HITL: AFK
**Classification:** AFK
**Labels:** docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task
**Goal Command:** Create a native execution goal for #246 from this mirror.
**Execution Mode:** Direct current-thread issue resolution or issue-backed orchestration.
**Worktree Policy:** Native Codex worktree thread first when delegated.
**Integration Policy:** PR reviewed and merged by the main thread.
**TDD Policy:** Required for changed receipt behavior.
**Parallelization Plan:** None.
**Reviewer Role:** Main thread orchestrator.
**Script Gate Mode:** Safety and proof oracle.

## What To Build

Add a fresh-native evidence receipt to the HELD/GFPE validation path so stale
native builds cannot produce false Stage II/III status or misleading milestone
plots.

## Acceptance Criteria

- [ ] The phase-discovery checker or retained summary records current commit,
  native module path, and build-refresh command or freshness proof.
- [ ] Neutral TP-flash fixture evidence records the same native freshness
  fields.
- [ ] The issue 188 analysis evidence regenerates HELD gate rows from the
  fresh native extension and refuses stale status text.
- [ ] Validation docs explain that closed PRs are evidence only after the local
  native extension has been rebuilt or proven current.
- [ ] No new HELD algorithm, public route, family admission, associating,
  electrolyte, reactive, CE, CPE, or source-backed neutral LLE benchmark claim
  is added.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
```

```powershell
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
```

```powershell
uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete
```

```powershell
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
```

```powershell
uv run --no-sync python scripts/dev/validate_project.py docs
```

## Non-Goals

- No new HELD algorithm work.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No source-backed neutral LLE benchmark; that is tracked by the neutral
  nonassociating LLE showcase spec.

## GitHub Body Text

Add a fresh-native evidence receipt to the HELD/GFPE validation path so stale
native builds cannot produce false Stage II/III status or misleading milestone
plots.

Source spec:
docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md

Source plan:
docs/superpowers/plans/2026-06-12-m4-equilibrium-fresh-native-held-gfpe-validation-receipts-plan.md

Acceptance:
- The phase-discovery checker or retained summary records current commit,
  native module path, and build-refresh command or freshness proof.
- Neutral TP-flash fixture evidence records the same native freshness fields.
- The issue 188 analysis evidence regenerates HELD gate rows from the fresh
  native extension and refuses stale status text.
- Validation docs explain that closed PRs are evidence only after the local
  native extension has been rebuilt or proven current.
