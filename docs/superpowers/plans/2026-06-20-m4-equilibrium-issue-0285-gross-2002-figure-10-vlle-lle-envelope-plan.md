# M4 Issue 285: Gross 2002 Figure 10 VLLE/LLE Envelope Plan

## Issue

GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/285

Milestone: M4 - Equilibrium

## Objective

Upgrade Gross 2002 Figure 10 from a diagnostic stress sample to a full water/1-pentanol VLLE/LLE envelope replication with retained branch-level evidence and paper-scale plot artifacts.

## Implementation Steps

1. Normalize `analyses/paper_validation/2002_gross/figures/figure_10` to the `source/`, `scripts/`, `results/` contract.
2. Preserve the water-rich, alcohol-rich, vapor, and three-phase branch source data with traceable provenance.
3. Generate full envelope model curves after the associating route prerequisite is merged and the public route can execute the source-backed system.
4. Render `figure_10.svg`, `figure_10.png`, and `figure_10.pdf` from retained `plotted_data.csv` and `model_curve.csv`.
5. Score each branch separately and gate campaign completion on the weakest branch score, not only on an aggregate figure score.

## Proof Oracle

- `uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/tests/test_figure_contract.py -q`
- cleanup hook
