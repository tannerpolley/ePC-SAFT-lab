# Harden GFPE pretreatment and selector admission pipeline

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/186`
Status: `open`
Last synced: `2026-06-05`

## Summary

Harden the early GFPE pretreatment, closure, stage-state, and selector/admission pipeline so later Ipopt/GFPE work starts from deterministic package-local contracts instead of route-specific assumptions.

## Acceptance Gates

- [ ] GFPE input and runtime state contracts are package-owned and deterministic.
- [ ] Pretreatment and selector/admission logic has focused tests for admissible and rejected route states.
- [ ] Legacy route-specific assumptions are either removed or isolated behind explicit tests.
- [ ] Capability evidence remains conservative and does not broaden production routes.
- [ ] Docs and local mirrors identify this as a ready M4 selector/admission verification issue.

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
- Treat current selector/admission code as existing evidence to verify first:
  request pretreatment, route-shape validation, thermodynamic input
  classification, parameter readiness checks, activation-plan validation, and
  activation-matrix production certification.
- Do not broaden activation-matrix admission, bypass `NlpProblem`, or claim
  generalized HELD readiness from selector/admission evidence alone.

## Non-Goals

- No associating LLE admission.
- No electrolyte or reactive route admission.
- No public API rename.
- No release publication.

## Validation

- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python run_pytest.py --native-contracts -q`
- `uv run python scripts/dev/validate_project.py docs`
- `uv run python scripts/dev/validate_project.py quick`
