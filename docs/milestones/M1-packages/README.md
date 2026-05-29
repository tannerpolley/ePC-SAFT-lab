# M1 - Packages

Monorepo package layout, package ownership, test relocation, provider-only build
proof, extension-native boundaries, and package CI/docs/release structure.

## Project Field Defaults

- Package: `core`, `equilibrium`, or `regression`
- Capability: blank unless the issue is tied to a named capability
- Backend: blank unless native dependency ownership is central
- Release target: `future` until the specific package release lane is known

## Current Open Issues

| Issue | Readiness | Release target | Summary |
| --- | --- | --- | --- |
| [#154](issues/0154-move-core-provider-package-into-packages-epcsaft.md) | `needs design` | `future` | Track the eventual move of the root provider package into `packages/epcsaft`. |
| [#164](issues/0164-prove-provider-only-build-without-ceres-or-ipopt.md) | `ready` | `future` | Prove provider-only build/import behavior without Ceres or Ipopt. |
| [#165](issues/0165-remove-extension-native-objects-from-provider-core.md) | `needs design` | `future` | Stop linking extension-native implementations into provider `_core`. |
| [#166](issues/0166-finish-extension-owned-test-routing-after-package-consolidation.md) | `ready` | `future` | Finish extension-owned test routing after package consolidation. |
| [#167](issues/0167-design-root-workspace-controller-and-packages-epcsaft-move.md) | `needs design` | `future` | Design the root workspace-controller shape before moving the provider package. |
| [#168](issues/0168-move-provider-distribution-into-packages-epcsaft.md) | `blocked` | `future` | Move the provider distribution into `packages/epcsaft` after prerequisites. |
| [#169](issues/0169-post-move-cleanup-and-install-proof.md) | `blocked` | `future` | Prove final installs and remove stale post-move compatibility residue. |
