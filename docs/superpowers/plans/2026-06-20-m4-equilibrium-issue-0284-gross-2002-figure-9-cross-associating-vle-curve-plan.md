# M4 Issue 284: Gross 2002 Figure 9 Cross-Associating VLE Curve Plan

## Issue

GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/284

Milestone: M4 - Equilibrium

## Objective

Fully replicate Gross 2002 Figure 9 for the methanol/1-octanol cross-associating VLE curve with retained source points, package-generated model data, and score-gated paper-scale plots.

## Implementation Steps

1. Normalize `analyses/paper_validation/2002_gross/figures/figure_09` to the `source/`, `scripts/`, `results/` contract.
2. Move reusable source data into the correct `data/reference/` taxonomy home and copy figure-local inputs into `source/`.
3. Generate a smooth model curve with enough intermediate points to match the paper-scale VLE trend.
4. Render `figure_09.svg`, `figure_09.png`, and `figure_09.pdf` from retained CSV snapshots.
5. Update the Gross 2002 full-replication manifest and checker evidence so Figure 9 contributes only after source, model, plotted-data, and score artifacts are present.

## Proof Oracle

- `uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/tests/test_figure_contract.py -q`
- cleanup hook
