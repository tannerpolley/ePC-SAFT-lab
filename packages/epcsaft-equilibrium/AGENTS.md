# Equilibrium Package Instructions

This subtree owns `epcsaft-equilibrium`: `Equilibrium`, route specs, selector
admission, native activation matrix consumption, GFPE assembly, Ipopt NLPs,
route scaling, postsolve certification, equilibrium diagnostics, and
equilibrium capability evidence.

Provider EOS supplies thermodynamic state/property and local derivative data.
Equilibrium owns pressure-transformed objective assembly, route residuals,
Jacobians, Hessians, tensors, NLP contracts, and solver-status acceptance.

Do not expose declared-not-exposed route families as callable production
routes. Do not treat acceptable Ipopt statuses, iteration-limit seeds, or
diagnostic staged workflows as completion evidence.

Any broadened route claim must update activation/capability evidence and run a
route-appropriate focused proof.

Focused validation:
- `uv run python run_pytest.py --equilibrium-api -q`
- `uv run python run_pytest.py --native-contracts -q`
- `uv run python run_pytest.py --equilibrium-debug -q -s packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route`
