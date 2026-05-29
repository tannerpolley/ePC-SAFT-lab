---
issue: 179
title: "M1: harden package onboarding and release ergonomics"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/179"
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

# M1: harden package onboarding and release ergonomics

Local mirror for the #179 PGIM run. GitHub remains authoritative for issue
state, acceptance checkboxes, comments, labels, and PR linkage.

This issue closes only when bootstrap, doctor, dependency reuse guidance,
package CI lanes, local release/install proof, and new-agent guidance all match
executable repo behavior.

Addendum from issue review:

- Extension package proof should consume a reusable Ceres package/cache when one
  exists instead of recompiling Ceres source for repeated regression package
  builds.
- `epcsaft-equilibrium` wheels should package an audited Ipopt runtime
  dependency payload, not every DLL from the SDK `bin` directory.
- Bootstrap, doctor, and docs should make Ipopt SDK root provenance explicit and
  show how to override the active root.

Implementation receipt:

- `scripts/dev/bootstrap.py` is the first-run entrypoint and reports Ipopt SDK
  provenance.
- `scripts/dev/doctor.py` reports provider SDK, extension native, Ceres cache,
  and Ipopt SDK state.
- Extension package builds prefer reusable Ceres and load MSVC for MSVC-style
  Ipopt SDK roots.
- `epcsaft-equilibrium` packages the audited runtime dependency closure for the
  native module instead of globbing every SDK DLL.
- Extension package PEP 517 builds use compact `build/xd` roots to reduce
  Windows object-path friction.
- Local release install proof passed for `epcsaft`, provider plus each
  extension, and all three packages together.
