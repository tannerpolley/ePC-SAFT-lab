# Regression Package Instructions

This subtree owns `epcsaft-regression`: `Regression`, target datasets, target
family summaries, Ceres residual blocks, parameter maps and bounds, optimizer
diagnostics, regression result schemas, and regression capability evidence.

Do not move regression optimizer loops, Ceres ownership, or regression result
contracts into the provider package. Provider code may supply parameter
payloads and CppAD derivative inputs only through provider-owned public
contracts.

Regression claims require native optimizer evidence, derivative evidence, and
package-local tests. Dependency presence alone is not capability evidence.

Focused validation:
- `uv run python run_pytest.py --regression -q`
- `uv run python scripts/dev/validate_project.py regression`
