# M4 Issue 286: Gross 2002 Full Figure Replication Campaign Plan

## Issue

GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/286

Milestone: M4 - Equilibrium

## Objective

Close the Gross 2002 full-replication campaign only after Figures 1-10 all have clean figure folders, retained source/model/plotted data, same-stem SVG/PNG/PDF plot outputs, and score-gated checker evidence.

## Implementation Steps

1. Confirm every child issue for Figures 1-10 is closed or has merged evidence in `analyses/paper_validation/2002_gross`.
2. Run the paper-validation figure contract for all migrated Gross 2002 figure folders.
3. Regenerate the campaign summary from the full-replication checker.
4. Render a compact contact sheet or summary artifact from retained PNG outputs for review.
5. Update issue mirrors and readiness state so no child remains marked ready or blocked incorrectly after its dependency is closed.

## Proof Oracle

- `uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native --write-summary`
- `uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/tests/test_figure_contract.py tests/workflows/repo/test_project_structure.py -q`
- cleanup hook
