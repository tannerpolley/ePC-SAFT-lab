---
issue: 168
title: "M1: move provider distribution into packages/epcsaft"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/168"
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

# M1: move provider distribution into packages/epcsaft

Child slice of #154. Performs the provider distribution move only after the
provider-only and native-extension prerequisite slices are complete.

Active plan: `docs/milestones/M1-packages/plans/move-provider-distribution-into-packages-epcsaft.md`

## Acceptance Criteria

- [x] Public import remains `import epcsaft`.
- [x] Public distribution remains `epcsaft`.
- [x] Root package metadata no longer owns provider source/build configuration.
- [x] No duplicate provider source tree or compatibility wrapper remains.
- [x] Provider source, provider build backend, scikit-build config, and provider package tests live under `packages/epcsaft`.
- [x] Active build, test, docs, and CI workflow paths resolve the provider package root from `packages/epcsaft`.

## Proof Receipts

- Provider package metadata/source/build backend/tests now live under `packages/epcsaft`.
- Root `pyproject.toml` is workspace/controller-only.
- Provider package import, provider/no-Ipopt native builds, provider wheel smoke, focused package tests, provider API, native contracts, integration, regression, equilibrium API, quick validation, and docs validation pass.
- Path audit confirms no tracked provider files remain under root `src/epcsaft` or root `epcsaft`.
