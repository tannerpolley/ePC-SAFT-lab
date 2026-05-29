---
issue: 166
title: "M1: finish extension-owned test routing after package consolidation"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/166"
state: "open"
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: null
capability: null
backend: null
readiness: "ready"
release_target: "future"
last_synced: "2026-05-29"
---

# M1: finish extension-owned test routing after package consolidation

Child slice of #154. Finishes routing extension-owned tests through package
test trees and validation selectors after monorepo consolidation.

## Acceptance Gates

- [x] Regression API/native/Ceres tests run from
  `packages/epcsaft-regression/tests/`.
- [x] Equilibrium API/native/Ipopt tests run from
  `packages/epcsaft-equilibrium/tests/`.
- [x] Package-local tests do not import root `tests.support`.
- [x] `run_pytest.py` and capability evidence route extension lanes to
  package-owned paths.

## Receipt

Proof passed on branch `codex/finish-extension-owned-test-routing` on
`2026-05-29`.

- Focused structural/routing proof: 5 passed.
- Path audit: no package-local tests import root `tests.support`; no files
  remain under root `tests/native/equilibrium` or `tests/native/regression`.
- Workflow/repo closure proof: 114 passed.
- Regression package slice: 13 passed.
- Equilibrium API package slice: 23 passed.
- Native-contract package slice: 50 passed.
- Docs validation: Sphinx build passed.
- No code/test relocation was needed in this closure slice because the prior
  test-ownership relocation plan had already completed the route changes.
