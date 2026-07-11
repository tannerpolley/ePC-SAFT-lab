# M5 - Regression

epcsaft-regression, TargetDataset/result contracts, Ceres optimizer,
parameter sensitivities, and pure/binary/electrolyte regression workflows.

## Project Field Defaults

- Package: `regression`
- Capability: `regression`
- Backend: usually `Ceres`
- Release target: `regression-0.x`

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#193](../../issues/2026-05-30-m5-regression-issue-0193-m5-traceable-regression-contract-and-scoped-admission.md) | `regression` | `Ceres` | `ready` | Non-executable parent for the strict native contract and scoped readmission leaves. |
| [#445](../../issues/2026-07-11-m5-regression-issue-0445-m5-require-strict-target-and-source-contracts.md) | `regression` | `Ceres` | `ready` | Require strict observation/source records, units, weights, and scales. |
| [#446](../../issues/2026-07-11-m5-regression-issue-0446-m5-compile-explicit-controls-and-fitted-parameters-from-resolved-input.md) | `regression` | `Ceres` | `blocked` | Compile effective controls and fitted parameters from resolved M3 input. |
| [#447](../../issues/2026-07-11-m5-regression-issue-0447-m5-make-native-ceres-receipts-and-configured-regression-authoritative.md) | `regression` | `Ceres` | `blocked` | Make the configured workflow and native Ceres receipt authoritative. |
| [#448](../../issues/2026-07-11-m5-regression-issue-0448-m5-make-fitted-interaction-persistence-rollback-safe.md) | `regression` | `Ceres` | `blocked` | Make matrix/manifest persistence rollback-safe after the receipt-backed workflow exists. |
| [#449](../../issues/2026-07-11-m5-regression-issue-0449-m5-delete-displaced-regression-owners-and-close-native-contract.md) | `regression` | `Ceres` | `blocked` | Delete displaced owners after native workflow, persistence, and SDK cutover. |
| [#450](../../issues/2026-07-11-m5-regression-issue-0450-m5-reset-capability-admission-and-package-strict-evidence-schema.md) | `regression` | `Ceres` | `blocked` | Separate component facts from admitted workflows and reset admission. |
| [#451](../../issues/2026-07-11-m5-regression-issue-0451-m5-import-two-accepted-real-data-workflows-and-close-scoped-admission.md) | `regression` | `Ceres` | `blocked` | Import only accepted methane/NIST and ethanol-water/Susial receipts. |
| [#338](https://github.com/ePC-SAFT/ePC-SAFT/issues/338) | `electrolyte_lle` | `Ceres` | `deferred` | Separate Khudaida electrolyte-LLE parameter-regression lane; not part of the scoped #193 admission tree. |

## Current Plans

- [Traceable native regression problem contract](../../plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md)
- [Capability reset and scoped readmission](../../plans/2026-07-10-m5-regression-capability-reset-and-scoped-readmission-plan.md)
