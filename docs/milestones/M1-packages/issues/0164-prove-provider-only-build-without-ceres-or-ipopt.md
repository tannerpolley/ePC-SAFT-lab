---
issue: 164
title: "M1: prove provider-only build without Ceres or Ipopt"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/164"
state: "open"
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: "core"
capability: null
backend: null
readiness: "ready"
release_target: "future"
last_synced: "2026-05-29"
---

# M1: prove provider-only build without Ceres or Ipopt

Child slice of #154. Proves the core provider can build and import without
Ceres or Ipopt before the final `packages/epcsaft` move.

## Acceptance Gates

- [x] Provider-only build profile disables Ceres and Ipopt.
- [x] `import epcsaft` and `import epcsaft._core` work in that profile.
- [x] Provider-only `_core` exposes provider-owned symbols only.
- [x] Validation docs name the provider-only proof command.

## Receipt

Proof passed on branch `codex/provider-only-build-proof` on `2026-05-29`.

- Provider build command: `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
- Regeneration check: `uv run python scripts/dev/build_epcsaft.py --profile provider --build-only`
- Status proof: `build_profile: provider`, Ceres OFF, Ipopt OFF,
  equilibrium native OFF, regression native OFF, CppAD ON.
- SDK proof: `provider_only_core=True`, `equilibrium_native_enabled=False`,
  `regression_native_enabled=False`, and forbidden native dependencies are
  Ceres and Ipopt.
- Symbol proof: `tests/native/contracts/test_provider_only_core_symbols.py`
  passed.
