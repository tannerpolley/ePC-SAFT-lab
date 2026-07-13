# M6 - Validation

Executable literature benchmarks, registry evidence, capability evidence,
docs/test proof, and reproducible validation gates.

## Equilibrium Evidence Ownership

| Owner | Scope |
| --- | --- |
| [M6 equilibrium evidence registry](registries/equilibrium-evidence-registry.yaml) | Literature cases, executable fixtures, retained commands, tolerances, blockers, and evidence maturity. |
| [M4 algorithm/admission registry](../M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml) | Algorithm families, mathematical contracts, local-proof readiness, and admission gates. |
| [Native activation descriptor](../../../../packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h) | Sole authority for runtime route exposure. |

The M6 registry preserves neutral, associating, multiphase, electrolyte, CE,
and derived-workflow evidence without activating a route or completing an M4
algorithm gate by implication. The former M4 evidence ledger remains available
in the [dated M4 dashboard archive](../M4-equilibrium/archive/2026-07-12-pre-source-faithful-dashboard.md).

## Project Field Defaults

- Package: `benchmark` unless the validation issue is package-specific
- Capability: set only when the benchmark proves a named package capability
- Backend: set only when backend behavior is the validation target
- Release target: `future` unless tied to a specific release train

## Current Open Issues

| Issue | Package | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#194](../../issues/2026-05-30-m6-validation-issue-0194-m6-executable-validation-evidence-backlog.md) | `benchmark` | `-` | `ready` | Non-executable parent for reproducible validation evidence; broad parent state is not a closeout gate. |
| [#192](../../issues/2026-05-30-m6-validation-issue-0192-m6-close-gfpe-registry-capability-and-benchmark-evidence.md) | `benchmark` | `Ipopt` | `blocked` | Reconcile current public bubble/dew and scoped single-component VLE evidence after #236/#455. |
| [#236](../../issues/2026-06-08-m6-validation-issue-0236-m6-reconcile-single-component-vle-activation-and-capability-evidence-registries.md) | `benchmark` | `Ipopt` | `blocked` | Reconcile scoped nonassociating hydrocarbon single-component VLE evidence after #444. |
| [#452](../../issues/2026-07-11-m6-validation-issue-0452-m6-establish-regression-real-data-evidence-framework.md) | `benchmark` | `Ceres` | `blocked` | Establish the common real-data evidence/checker/receipt framework. |
| [#453](../../issues/2026-07-11-m6-validation-issue-0453-m6-retain-methane-nist-configured-fit-evidence.md) | `benchmark` | `Ceres` | `blocked` | Retain the exact methane/NIST configured-fit and independent prediction evidence. |
| [#454](../../issues/2026-07-11-m6-validation-issue-0454-m6-retain-ethanol-water-susial-residual-fit-evidence.md) | `benchmark` | `Ceres` | `blocked` | Retain exact ethanol-water/Susial observed-state residual evidence. |
| [#467](../../issues/2026-07-11-m6-validation-issue-0467-m6-close-combined-regression-real-data-evidence-gate.md) | `benchmark` | `Ceres` | `blocked` | Validate both lane receipts together and publish the combined M6 checker receipt. |
| [#455](../../issues/2026-07-11-m6-validation-issue-0455-m6-refresh-gross-2002-figures-2-9-public-bubble-dew-evidence.md) | `benchmark` | `Ipopt` | `blocked` | Refresh post-cutover Gross Figures 2-9 current public bubble/dew evidence. |
| [#456](../../issues/2026-07-11-m6-validation-issue-0456-m6-complete-source-qualified-nonideal-mea-evidence.md) | `benchmark` | `Ipopt` | `blocked` | Complete source-qualified MEA evidence without treating a rejected model result as missing evidence. |
| [#420](../../issues/2026-07-02-m6-validation-issue-0420-m6-paper-validation-campaign-parent.md) | `benchmark` | `-` | `ready` | Deferred paper-validation campaigns; not an exact Tasks 9-22 closeout gate. |
| [#421](../../issues/2026-07-02-m6-validation-issue-0421-khudaida-2026-paper-validation-parent.md) | `benchmark` | `Ipopt` | `ready` | Deferred Khudaida/Figiel paper subtree under #420; individual figure leaves remain separate. |

## Current Plans

- [Current GFPE registry and capability evidence](../../plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md)
- [Single-component VLE capability evidence reconciliation](../../plans/2026-07-10-m6-single-component-vle-capability-evidence-reconciliation-plan.md)
- [Regression real-data evidence gates](../../plans/2026-07-10-m6-regression-real-data-evidence-gates-plan.md)
- [Gross 2002 public bubble/dew evidence refresh](../../plans/2026-07-10-m6-gross-2002-public-bubble-dew-evidence-refresh-plan.md)
- [Standalone CE nonideal input evidence](../../plans/2026-07-10-m6-standalone-ce-nonideal-input-evidence-plan.md)
