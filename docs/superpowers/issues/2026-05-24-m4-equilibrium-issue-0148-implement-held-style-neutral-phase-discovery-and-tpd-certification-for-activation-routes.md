---
issue: 148
title: "Implement HELD-style neutral phase discovery and TPD certification for activation routes"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/148"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md"
source_plan: "docs/superpowers/plans/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-a
last_synced: "2026-06-02"
---

# Implement HELD-style neutral phase discovery and TPD certification for activation routes

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/148
Source Spec: docs/superpowers/specs/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md
Source Plan: docs/superpowers/plans/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes-plan.md
Branch: codex/issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-a
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Implement the Stage 1 equilibrium-doctrine prerequisite: HELD-style neutral phase discovery and TPD stability certification for activation-matrix neutral flash/LLE routes.

## Supplemental Context

- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Acceptance Criteria

- [ ] A neutral TPD evaluator exists with deterministic tests.
- [ ] A volume-composition trial-phase path can use existing EOS phase-state data without hidden pressure-root derivative dependence in production callbacks.
- [ ] Candidate phases can be generated, de-duplicated, and ranked.
- [ ] Candidate phase fractions can be selected or rejected by material-balance feasibility.
- [ ] Neutral flash/LLE seed generation can consume the candidate set.
- [ ] Postsolve certification checks per-phase stability, phase-set candidate completeness, conservation, pressure, fugacity/chemical-potential residuals, phase distinctness, and route diagnostics.
- [ ] Tests prove an optimizer-converged but uncertified or unstable point is not `production_accepted`.
- [ ] Capabilities do not broaden public route support.
- [ ] Algorithm registry and roadmap docs remain synchronized.

## Proof Oracle

- uv run python run_pytest.py tests/native/equilibrium/diagnostics/test_selector_core_contracts.py tests/native/contracts/test_equilibrium_activation_capabilities.py -q
- uv run python run_pytest.py --native-contracts -q
- uv run python scripts/dev/validate_project.py docs
- uv run python scripts/dev/validate_project.py quick

## Non-Goals And Boundaries

- Do not add new public routes.
- Do not expose associating LLE.
- Do not expose electrolyte or reactive routes.
- Do not treat phase-distance as a thermodynamic equilibrium equation; it remains an anti-collapse / distinctness gate.
- Do not accept a result only because Ipopt converged.
- Keep the native activation matrix as admission control.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
