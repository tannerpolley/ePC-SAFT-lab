# M1 - Packages

Monorepo package layout, package ownership, test relocation, provider-only build
proof, extension-native boundaries, and package CI/docs/release structure.

## Project Field Defaults

- Package: `core`, `equilibrium`, or `regression`
- Capability: blank unless the issue is tied to a named capability
- Backend: blank unless native dependency ownership is central
- Release target: `future` until the specific package release lane is known

## Current Open Issues

| Issue | Role | Readiness | Summary |
| --- | --- | --- | --- |
| [#435](../../issues/2026-07-11-m1-packages-issue-0435-m1-prove-current-host-linux-package-reproducibility.md) | rollup | `ready` | Track the current-Zorin/Python-3.13 package proof without a release claim. |
| [#436](../../issues/2026-07-11-m1-packages-issue-0436-m1-record-active-linux-environment-and-receipt-contract.md) | leaf | `ready` | Define the current-host receipt, clean-tree refusal, and dependency identity. |
| [#437](../../issues/2026-07-11-m1-packages-issue-0437-m1-build-six-local-package-artifacts.md) | leaf | `blocked` | Build six local artifacts from one clean post-cutover commit. |
| [#438](../../issues/2026-07-11-m1-packages-issue-0438-m1-prove-four-isolated-install-combinations-with-native-smokes.md) | leaf | `blocked` | Prove four exact-wheel installs, native smokes, and installed-module ELF closure. |

## Current Plan

- [Local Linux package reproducibility](../../plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md)
