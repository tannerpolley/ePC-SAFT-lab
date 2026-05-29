# M6 - Validation

Executable literature benchmarks, registry evidence, capability evidence,
docs/test proof, and release-quality validation gates.

## Project Field Defaults

- Package: `benchmark` unless the validation issue is package-specific
- Capability: set only when the benchmark proves a named package capability
- Backend: set only when backend behavior is the validation target
- Release target: `future` unless tied to a specific release train

## Current Open Issues

| Issue | Readiness | Release target | Summary |
| --- | --- | --- | --- |
| [#155](issues/0155-rebase-figiel-validation-branch-onto-current-main.md) | `ready` | `future` | Rebase Figiel validation work onto current main. |
| [#159](issues/0159-migrate-validation-and-template-parameter-bundles-to-new-schema.md) | `ready` | `future` | Migrate validation and template parameter bundles to the new schema. |
