# Neutral VLE Selector Expansion

## Objective

Implement the neutral VLE selector expansion so the reset public equilibrium workflow exposes and validates:

- `Equilibrium(mixture).solve(route="bubble_pressure", T=..., x=...)`
- `Equilibrium(mixture).solve(route="bubble_temperature", P=..., x=...)`
- `Equilibrium(mixture).solve(route="dew_pressure", T=..., y=...)`
- `Equilibrium(mixture).solve(route="dew_temperature", P=..., y=...)`
- `Equilibrium(mixture).solve(route="flash", T=..., P=..., z=...)`

The implementation must preserve selector-core ownership, activation-matrix source-of-truth behavior, exact derivative requirements, and hard postsolve certification.

## Implementation Contract

- Start from the current `ipopt` branch.
- Use the existing methane/ethane/propane hydrocarbon fixture as the shared VLE proof case.
- Prove the existing production owner before route edits: neutral VLE route specs
  are owned by the selector-dispatched bubble/dew residual core, not by a
  standalone flash route.
- Keep a route-spec matrix for all five VLE calls: route, knowns, unknowns,
  residual rows, constraints, certification rows, activation key, and public
  entrypoint.
- Treat activation matrix rows as selector admission metadata, not permission to
  invent independent route families.
- Keep `Equilibrium.solve(route=..., ...)` as the only public equilibrium
  execution method; route-specific methods are wrappers and are not allowed.
- Negative tests must fail before implementation if direct flash bindings appear,
  Python dispatches around the selector, flash uses a standalone production
  route implementation, or certification accepts optimizer success without
  residual closure.
- If the implementation path forks between shared-core route specs and new route
  families, stop for clarification before writing code.
- Complete owner review before final design acceptance.
- Replace the selector boundary shaped as `route + scalar + composition` with a typed native selector request carrying route, temperature, pressure, composition, and composition role.
- Promote `neutral_tp_flash` to production-exposed only after selector-owned two-phase flash seed generation and certification are proven.
- Keep neutral VLE production scope limited to neutral, non-reactive, non-electrolyte, non-associating mixtures.
- Do not add short aliases, root free functions, direct route pybind entrypoints, compatibility stubs, or Python-owned dispatch around the selector.
- Keep public capability reporting honest and generated from native activation metadata.

## Proof

The goal is complete only when the board checker passes, role-owner review is recorded, strict validation passes, local commits exist, and the worktree is clean.

Run at minimum:

```powershell
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python run_pytest.py tests/native/equilibrium/diagnostics tests/native/contracts -q
uv run python run_pytest.py tests/api/frontend/test_equilibrium.py --allow-long-native-tests -q
uv run python scripts/dev/generate_equilibrium_activation.py --check
uv run python scripts/docs/sync_algorithm_registry.py --check --strict-traceability
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
uv run python scripts/dev/validate_project.py quick
node <resolved-goalbuddy-checker> docs/goals/neutral-vle-selector-expansion/state.yaml
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
git diff --check
git status --short
```
