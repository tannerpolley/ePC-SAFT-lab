# Khudaida Electrolyte LLE And HELD2 Flash Validation Plan

**Goal:** Resolve GitHub issue #320 by making the full Khudaida 2026
electrolyte LLE figure-reproduction checker pass and by adding a retained
HELD2 flash scenario gate that proves the electrolyte extension against the
already-proven HELD 1.0-style neutral base.

**Architecture:** #320 is the reopened #191 closeout blocker. #314 remains
valid as representative public-route admission evidence, but it is no longer
sufficient evidence for electrolyte LLE model performance. The resolving PR
must prove source-data reproduction and multi-scenario HELD2 flashing through
retained checkers, plots, and tests.

**Tech Stack:** `packages/epcsaft-equilibrium`, public
`Equilibrium(..., route="electrolyte_lle")`, native Ipopt-backed equilibrium
diagnostics, Khudaida paper-validation scripts, retained CSV/SVG/PNG/PDF plot
artifacts, and pytest contracts.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation.md`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/320`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `AFK`

## Outcome Proof

**Intent:** Replace the premature #191 closeout boundary with a source-backed
model-reproduction gate that proves electrolyte LLE behavior across the
Khudaida figure set and exercises HELD2 flashing beyond one representative
feed.
**Current Behavior:** The public electrolyte route admission checker proves a
representative certified payload, while the Khudaida figure checker reports
complete artifacts but failed model reproduction.
**Expected Outcome:** `check_khudaida_2026_figure_validation.py` reports
complete artifacts, complete model reproduction, zero blockers, and every
modeled figure or panel score at least `8.0`.
**Target Output:** Retained Khudaida figure artifacts and HELD2 flash tests that
fail when model curves collapse near the feed, miss the source tie-lines, lose
electroneutrality, drop exact reduced-Hessian evidence, or regress the neutral
HELD 1.0 base behavior.
**Evidence:** Retained checker JSON, source/model CSVs, fit-statistics CSVs,
figure SVG/PNG/PDF artifacts, public-admission JSON, and pytest output listing
the executed electrolyte HELD2 flash scenario node ids.
**Owner:** `packages/epcsaft-equilibrium` owns the solver behavior;
`analyses/paper_validation/2026_khudaida` owns retained source/model plot
artifacts.
**Interface:** Public `Equilibrium(..., route="electrolyte_lle")`, retained
paper-validation scripts, figure fit-statistics CSVs, and pytest scenario
contracts.
**Cutover:** #191 cannot close on the #314 representative admission checker
alone; it closes only after #320 passes and updates parent evidence.
**Replaced Path:** Single-feed public admission as a proxy for electrolyte LLE
model validity.
**Acceptance Proof:** The proof oracle commands in this plan pass from the repo
root and the #191 mirror names #320 as closed provenance after merge.
**Stop Criteria:** Stop if source inputs, parameter provenance, species basis,
charge balance, solver seeds, or plotted data cannot be verified against
retained inputs before changing solver logic.
**Avoid:** Do not count collapsed near-feed splits, source-only figures,
synthetic payloads, downstream metrics, or broad electrolyte/release claims as
completion evidence.
**Risk:** A numerically certified local point can still be scientifically wrong
if it is not compared to the retained figure data. This issue explicitly makes
plot/data reproduction part of the M4 gate.

## Implementation Boundaries

**Files To Create:** HELD2 scenario tests if no existing test file covers the
required flash cases.
**Files To Modify:** `analyses/paper_validation/2026_khudaida/**`,
`scripts/validation/check_khudaida_2026_figure_validation.py`,
`packages/epcsaft-equilibrium/**`, focused equilibrium tests, #191/#320 mirrors,
and M4 capability/registry/docs only where the proven claim changes.
**Files To Avoid:** Regression package files, downstream repositories,
application-specific lithium extraction metrics, and unrelated provider EOS
refactors.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, Khudaida retained
source data, electrolyte methodology context, and the HELD2 reduced-coordinate
diagnostics introduced by #300/#302/#306/#312/#313/#314.
**Read Path:** Trace each failing figure from source CSV to feed construction,
species order, parameter bundle, solver options, model output CSV, fit
statistics, and plotted artifact before changing solver logic.
**Write Path:** Change the smallest production owner needed to make the public
route produce source-matching electrolyte LLE results, then regenerate retained
artifacts from scripts.
**Integration Points:** Public route payload, native reduced-coordinate
discovery/refinement diagnostics, postsolve certification, Khudaida plot
generation, and capability evidence.
**Migration Or Cutover:** Keep #191 blocked by #320 until the full figure
checker and HELD2 scenario tests pass.
**Replaced Path Handling:** Update docs and mirrors to state that #314 was
representative public admission, not full electrolyte LLE reproduction.
**Acceptance Proof Gate:** The resolving PR must include retained command
output showing both artifact and model reproduction gates pass.

## Required Scenarios

- Khudaida single-salt mixed-solvent LLE across every modeled figure and panel.
- Neutral/no-charge limit compared against the HELD 1.0-style neutral route.
- Stable one-phase feeds and unstable two-liquid feeds.
- Near-boundary feeds that should not pass by collapsing phases together.
- Phase-label permutations to prove phase ordering does not affect the result.
- Common-ion or mixed-salt reduced-coordinate cases that exercise the
  independent counterion-pair matrix.

## Acceptance Criteria

- [ ] The Khudaida checker returns `artifact_complete=true`,
  `model_reproduction_complete=true`, and zero artifact/model blockers.
- [ ] Every modeled Khudaida figure or panel has retained source data, retained
  model data, retained fit statistics, and plot score `>= 8.0`.
- [ ] Figures without model-comparable equilibrium data are explicitly recorded
  by the checker and cannot hide failed model rows.
- [ ] Accepted electrolyte flashes report noncollapsed phase distance, positive
  phase amounts, per-phase charge residuals, neutral transfer residuals,
  mean-ionic transfer residuals, pressure consistency, exact reduced Hessian
  availability, and finite domain margins.
- [ ] HELD2 flash tests cover neutral-limit parity with the HELD 1.0-style
  base, source-backed electrolyte LLE, common-ion or mixed-salt reduced
  coordinates, stable feeds, unstable feeds, boundary feeds, and phase-label
  permutations.
- [ ] The HELD2 pytest proof collects and runs at least one real electrolyte
  HELD2 flash scenario test; zero selected tests fails the gate.
- [ ] Public capability and docs language is narrowed to the behavior proven by
  the full checker.
- [ ] #191 remains open and blocked by #320 until all #320 proof commands pass.

## Non-Goals

- No reactive electrolyte LLE route.
- No parameter regression target.
- No application-specific downstream metrics.
- No release claim.

## Tasks

### Task 1: Prove And Fix Figure-Level Reproduction

**Use Cases:**
- A reviewer can see every retained Khudaida figure and the matching model
  curve or source-only rationale.
- The retained source/model data and fit statistics become the acceptance
  evidence for electrolyte LLE model reproduction.
- A resolver can identify whether a figure failure is data, parameter, or
  equilibrium-method driven.
- A regression test fails when a modeled figure drops below score `8.0`.

**Files:**
- `analyses/paper_validation/2026_khudaida/figures/figure_01` through
  `figure_12`
- `analyses/paper_validation/2026_khudaida/scripts/**`
- `scripts/validation/check_khudaida_2026_figure_validation.py`

- [ ] Verify source inputs, species basis, units, and parameter provenance for
  every failing figure.
- [ ] Regenerate model curves with dense, smooth model outputs where a curve is
  expected.
- [ ] Make every modeled fit-statistics row pass with score `>= 8.0`.
- [ ] Render SVG/PNG/PDF artifacts for every updated figure.

### Task 2: Add HELD2 Flash Scenario Contracts

**Use Cases:**
- The electrolyte route is tested on more than one representative feed.
- The electrolyte extension is checked against the neutral HELD base where
  charges are removed or inactive.
- Collapsed phases and phase-order artifacts cannot pass.

**Files:**
- `packages/epcsaft-equilibrium/tests/**`
- `tests/native/contracts/**` when native diagnostics are exposed there
- `packages/epcsaft-equilibrium/**`

- [ ] Add focused tests for the required scenarios in this plan.
- [ ] Assert postsolve diagnostics, noncollapsed split metrics, and exact
  reduced-Hessian availability.
- [ ] Include neutral-limit parity with the HELD 1.0-style base behavior.
- [ ] Report exact pytest node ids or checker output proving non-empty scenario
  test execution.

### Task 3: Align Capability Evidence And Parent State

**Use Cases:**
- #191 cannot be closed until #320 is merged.
- The cutover from single-feed route admission to full figure-reproduction
  evidence is explicit in #191 and #320.
- Capability text does not overclaim unsupported electrolyte behavior.
- M6 benchmark evidence receives a clean handoff only after M4 behavior works.

**Files:**
- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- `docs/superpowers/issues/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation.md`
- M4 registry/capability docs touched by the resolving PR

- [ ] Update #320 with retained proof after merge.
- [ ] Update #191 only after #320 passes.
- [ ] Keep #191 blocked while #320 remains open.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --json --require-complete --require-model-pass
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and flash"
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

The pytest proof must report the exact collected scenario tests when the selector
changes; zero selected tests fails the plan gate.
