# M4 Issue 283: Gross 2002 Figure 8 LLE+VLE Envelope Plan

## Issue

GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/283

Milestone: M4 - Equilibrium

## Objective

Upgrade Gross 2002 Figure 8 from retained diagnostic evidence to a full methanol/cyclohexane LLE+VLE envelope replication with source data, package-generated model curves, and score-gated paper-scale plot artifacts.

## Implementation Steps

1. Normalize the Figure 8 folder to the paper-validation contract: `source/`, `scripts/`, and `results/` only.
2. Keep reusable mixture or pure-component data under `data/reference/` taxonomy homes and copy the figure-local working data into `source/`.
3. Generate model-envelope data with the public equilibrium route that becomes available after the associating GFPE admission prerequisite lands.
4. Render `figure_08.svg`, `figure_08.png`, and `figure_08.pdf` with `plotted_data.csv`, `model_curve.csv`, and `fit_statistics.csv`.
5. Update the Gross 2002 full-replication manifest and summary so Figure 8 is accepted only when every retained branch clears the plot-score threshold.

## Proof Oracle

- `uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/tests/test_figure_contract.py -q`
- cleanup hook
