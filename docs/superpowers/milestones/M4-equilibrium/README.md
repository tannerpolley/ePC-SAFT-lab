# M4 - Equilibrium

epcsaft-equilibrium, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase discovery, and VLE/LLE/electrolyte/reactive equilibrium workflows.

## Project Field Defaults

- Package: `equilibrium`
- Capability: `vle`, `lle`, `electrolyte`, or `reactive`
- Backend: usually `Ipopt`
- Release target: `equilibrium-0.x`

## Current Ownership

| Owner | Scope |
| --- | --- |
| [Generalized fluid-phase equilibrium](generalized-fluid-phase-equilibrium.md) | Package architecture and current equilibrium boundary. |
| [M4 algorithm/admission registry](registries/equilibrium-algorithm-admission-registry.yaml) | Algorithm families, mathematical contracts, local-proof readiness, and admission gates. |
| [M6 equilibrium evidence registry](../M6-validation/registries/equilibrium-evidence-registry.yaml) | Literature cases, commands, tolerances, fixtures, and evidence maturity. |
| [Native activation descriptor](../../../../packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h) | Sole authority for runtime route exposure. |

Neither M4 nor M6 registry duplicates runtime route lists. Public equilibrium remains bubble pressure, dew pressure, and scoped nonassociating hydrocarbon single-component VLE.

## Algorithm Doctrine

| Document | Summary |
| --- | --- |
| [Pereira HELD](algorithms/neutral-held.md) | Three-stage neutral molecular HELD identity and direct free-energy Stage III. |
| [Perdomo HELD2](algorithms/strong-electrolyte-held2.md) | Strong-electrolyte modified-mole formulation and independent modified-potential conditions. |
| [Ascani electrolyte equilibrium](algorithms/ascani-electrolyte-equilibrium.md) | Separate counterion-pair coordinates, mean-ionic conditions, and successive phase addition. |
| [Chemical and coupled equilibrium](algorithms/chemical-and-coupled-equilibrium.md) | Separate standalone CE and simultaneous CPE problem families. |

## Current Program

- [Source-faithful equilibrium recovery and curated migration specification](../../specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md)
- [Source-faithful equilibrium recovery and curated migration plan](../../plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md)
- [Standalone CE diagnostic repair and admission](../../plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md)
- [Provider resolved-input SDK v1 consumer](../../plans/2026-07-10-m4-equilibrium-provider-resolved-input-sdk-v1-consumer-plan.md)
- [Canonical-owner decomposition](../../plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md)

Historical specs, plans, evidence tables, queue prose, and closed-issue narratives remain available in the [2026-07-12 dashboard archive](archive/2026-07-12-pre-source-faithful-dashboard.md).

## Current Open Work

### Phase-Equilibrium Certification And Re-admission

| Issue | Capability | Readiness | Summary |
| --- | --- | --- | --- |
| [#361](../../issues/2026-06-29-m4-equilibrium-issue-0361-m4-pe-unify-phase-equilibrium-certification-contracts.md) | `phase-equilibrium` | `blocked` | Parent for enforceable production-route certification contracts. |
| [#363](../../issues/2026-06-29-m4-equilibrium-issue-0363-m4-pe-govern-lle-family-certification.md) | `lle` | `blocked` | LLE family certification parent. |
| [#372](../../issues/2026-06-29-m4-equilibrium-issue-0372-govern-reactive-electrolyte-lle-certification-boundary.md) | `electrolyte`/`reactive` | `blocked` | Future reactive-electrolyte LLE boundary. |
| [#376](../../issues/2026-06-29-m4-equilibrium-issue-0376-govern-reactive-and-coupled-phase-equilibrium-certification.md) | `cpe` | `blocked` | Reactive/coupled PE certification parent. |
| [#458](../../issues/2026-07-11-m4-equilibrium-issue-0458-m4-lle-re-admit-neutral-lle-only-after-scoped-phase-discovery-proof.md) | `neutral_lle` | `needs design` | Re-admission only after scoped complete phase discovery. |
| [#459](../../issues/2026-07-11-m4-equilibrium-issue-0459-m4-lle-re-admit-electrolyte-lle-only-after-scoped-charge-neutral-proof.md) | `electrolyte_lle` | `needs design` | Re-admission only after source-faithful charge-neutral proof. |
| [#460](../../issues/2026-07-11-m4-equilibrium-issue-0460-m4-pe-admit-neutral-multiphase-only-after-scoped-phase-set-discovery.md) | `neutral_multiphase` | `needs design` | Admission only after scoped complete phase-set discovery. |
| [#461](../../issues/2026-07-11-m4-equilibrium-issue-0461-m4-pe-admit-neutral-tp-flash-only-after-live-source-backed-proof.md) | `neutral_tp_flash` | `needs design` | Admission only after live source-backed proof. |

### CE, CPE, Resolved Inputs, And Canonical Owners

| Issue | Capability | Readiness | Summary |
| --- | --- | --- | --- |
| [#321](../../issues/2026-06-26-m4-equilibrium-issue-0321-m4-ce-standalone-chemical-speciation-equilibrium-foundation-before-cpe.md) | `ce` | `ready` | Standalone CE foundation before CPE. |
| [#328](../../issues/2026-06-26-m4-equilibrium-issue-0328-m4-ce-design-standalone-speciation-public-api-and-result-schema.md) | `ce` | `ready` | Design the standalone CE API and result schema. |
| [#329](../../issues/2026-06-26-m4-equilibrium-issue-0329-m4-ce-complete-primitive-receipts-and-independent-component-checker.md) | `ce` | `blocked` | Primitive receipts and independent component checker. |
| [#330](../../issues/2026-06-26-m4-equilibrium-issue-0330-m4-ce-activate-standalone-ce-only-after-gates-pass.md) | `ce` | `blocked` | CE activation only after all gates pass. |
| [#331](../../issues/2026-06-26-m4-equilibrium-issue-0331-m4-cpe-define-simultaneous-phase-plus-chemistry-interface-contract.md) | `cpe` | `blocked` | Simultaneous phase-plus-chemistry interface after CE. |
| [#443](../../issues/2026-07-11-m4-equilibrium-issue-0443-m4-consume-provider-resolved-input-sdk-v1.md) | `equilibrium` | `blocked` | Consume provider resolved-input SDK v1. |
| [#457](../../issues/2026-07-11-m4-equilibrium-issue-0457-m4-ce-classify-source-qualified-nonideal-mea-outcome-and-repair-exact-defect.md) | `ce` | `blocked` | Classify M6 MEA evidence and repair only reproduced M4 defects. |
| [#462](../../issues/2026-07-11-m4-equilibrium-issue-0462-m4-decompose-equilibrium-extension-around-canonical-owners.md) | `equilibrium` | `ready` | Canonical-owner decomposition tracker. |
| [#463](../../issues/2026-07-11-m4-equilibrium-issue-0463-m4-characterize-equilibrium-ownership-against-the-shared-ratchet-schema.md) | `equilibrium` | `blocked` | Characterize current owners against the shared ratchet. |
| [#464](../../issues/2026-07-11-m4-equilibrium-issue-0464-m4-extract-public-green-equilibrium-owners-without-behavior-drift.md) | `equilibrium` | `blocked` | Extract current public-green owners only after ratchet activation. |
| [#465](../../issues/2026-07-11-m4-equilibrium-issue-0465-m4-extract-route-gated-electrolyte-native-owners.md) | `electrolyte` | `blocked` | Extract gated native owners after exact charge-neutral gates. |
| [#466](../../issues/2026-07-11-m4-equilibrium-issue-0466-m4-retire-route-gated-internal-binding-and-python-owners.md) | `equilibrium` | `blocked` | Retire internal owners only after caller cutovers. |
