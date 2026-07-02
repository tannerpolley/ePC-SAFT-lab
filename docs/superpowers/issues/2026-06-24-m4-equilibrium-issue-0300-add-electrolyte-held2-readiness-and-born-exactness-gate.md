---
issue: 300
title: "M4: add electrolyte HELD2 readiness and Born exactness gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/300"
state: "closed"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "closed"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md"
afk_hitl: "AFK"
branch: null
last_synced: "2026-06-24"
---

# M4: add electrolyte HELD2 readiness and Born exactness gate

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/300
**Pull Request:** https://github.com/ePC-SAFT/ePC-SAFT/pull/301
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/300 using docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md and docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Auto Mode
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## What To Build

Add the next #191 prerequisite gate by proving that the Khudaida electrolyte
source fixture can be represented through an exact charge-neutral reduced
amount basis and can carry exact Born SSM/DS derivative receipts into HELD2
readiness diagnostics while public electrolyte routes remain closed.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocks: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocked by: None.

## Acceptance Criteria

- [x] Khudaida electrolyte source rows pass the existing closed-admission source gate.
- [x] A retained checker proves an exact reduced electroneutral amount lift for the source-backed NaCl electrolyte fixture, including explicit charge-balance residual <= `1.0e-10`.
- [x] The checker consumes CppAD-backed Born SSM/DS derivative evidence from a liquid electrolyte state and records finite composition, fugacity, activity-parameter, `d_born`, and `f_solv` derivative receipts.
- [x] The checker reports HELD2 status as readiness-only: reduced variables, source fixture, and derivative prerequisites present; electrolyte TPD, dual candidate discovery, postsolve certification, and public route admission remain pending.
- [x] Capability and M4 registry evidence distinguish this prerequisite from public electrolyte GFPE support.

## Resolution Notes

- Added `scripts/validation/check_electrolyte_held2_readiness.py` as the retained #300 proof checker.
- The checker consumes the #269 Khudaida closed-admission source gate before any readiness credit is granted.
- The reduced-basis proof lifts source-backed `H2O`, ethanol, isobutanol/Butanol, and NaCl amounts to explicit `H2O`, ethanol, Butanol, Na+, and Cl- native amounts with charge residual <= `1.0e-10`.
- The Born SSM/DS receipt comes from public provider state APIs and records CppAD composition, ln-fugacity, activity-parameter, `d_born`, and `f_solv` derivative evidence.
- HELD2 remains readiness-only: electrolyte TPD, HELD2 dual phase discovery, Stage III refinement, postsolve electrolyte phase-set certification, and public electrolyte route admission remain pending.
- The M4 capability and registry rows classify this work as prerequisite evidence, not production electrolyte GFPE support.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validation/check_electrolyte_held2_readiness.py --json --require-source-gate --require-reduced-basis --require-born-ssm-ds --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Non-Goals

- No public `electrolyte_lle` route admission.
- No electrolyte TPD minimizer or full HELD2 dual-loop implementation.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.
- No provider EOS rewrite unless a focused contract test proves the existing Born derivative receipt is insufficient.
