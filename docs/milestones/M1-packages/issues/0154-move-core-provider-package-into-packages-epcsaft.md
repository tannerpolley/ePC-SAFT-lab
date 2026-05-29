---
issue: 154
title: "Tracking: move core provider package into packages/epcsaft"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/154"
state: "open"
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: "core"
capability: null
backend: null
readiness: "needs design"
release_target: "future"
last_synced: "2026-05-29"
---

# Tracking: move core provider package into packages/epcsaft

Move the core provider distribution from the repository root into
`packages/epcsaft` after provider-only build proof and extension-native
ownership boundaries are stable.

The move must preserve `import epcsaft` and the `epcsaft` distribution name.
Root `pyproject.toml` becomes a workspace/controller only. No compatibility
wrappers or duplicate provider source trees should remain after the move.

Next useful agent action: design the package-move slice only after provider-only
build and extension-native boundary gates are stable.
