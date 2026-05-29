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
| [#168](issues/0168-move-provider-distribution-into-packages-epcsaft.md) | `ready` | `future` | Move the provider distribution into `packages/epcsaft` after prerequisites. |
| [#169](issues/0169-post-move-cleanup-and-install-proof.md) | `blocked` | `future` | Prove final installs and remove stale post-move compatibility residue. |
