# Implement HELD-style neutral phase discovery and TPD certification for activation routes

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/148`
Status: `open`
Last synced: `2026-06-02`

## Summary

Implement the Stage 1 equilibrium-doctrine prerequisite: HELD-style neutral phase discovery and TPD stability certification for activation-matrix neutral flash/LLE routes.

## Acceptance Gates

- [ ] A neutral TPD evaluator exists with deterministic tests.
- [ ] A volume-composition trial-phase path can use existing EOS phase-state data without hidden pressure-root derivative dependence in production callbacks.
- [ ] Candidate phases can be generated, de-duplicated, and ranked.
- [ ] Candidate phase fractions can be selected or rejected by material-balance feasibility.
- [ ] Neutral flash/LLE seed generation can consume the candidate set.
- [ ] Postsolve certification checks per-phase stability, phase-set candidate completeness, conservation, pressure, fugacity/chemical-potential residuals, phase distinctness, and route diagnostics.
- [ ] Tests prove an optimizer-converged but uncertified or unstable point is not `production_accepted`.
- [ ] Capabilities do not broaden public route support.
- [ ] Algorithm registry and roadmap docs remain synchronized.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.
- Treat current Stage 9 neutral evidence as deterministic screening plus
  continuous TPD, HELD Stage I diagnostics, a finite-candidate Stage II bound
  audit, and current-route Stage III Ipopt refinement. Do not describe it as
  full generalized HELD unless the broader GFPE stage plan gates are extended
  with matching executable evidence.

## Non-Goals

- Do not add new public routes.
- Do not expose associating LLE.
- Do not expose electrolyte or reactive routes.
- Do not treat phase-distance as a thermodynamic equilibrium equation; it remains an anti-collapse / distinctness gate.
- Do not accept a result only because Ipopt converged.
- Keep the native activation matrix as admission control.

## Validation

- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python run_pytest.py --native-contracts -q`
- `uv run python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete`
- `uv run python scripts/dev/validate_project.py docs`
- `uv run python scripts/dev/validate_project.py quick`
