# M6 - Validation

Executable literature benchmarks, registry evidence, capability evidence,
docs/test proof, and release-quality validation gates.

## Project Field Defaults

- Package: `benchmark` unless the validation issue is package-specific
- Capability: set only when the benchmark proves a named package capability
- Backend: set only when backend behavior is the validation target
- Release target: `future` unless tied to a specific release train

## Current Open Issues

| Issue | Package | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#192](../../issues/0192-close-gfpe-registry-capability-and-benchmark-evidence.md) | `benchmark` | `Ipopt` | `blocked` | Close GFPE registry, capability, and benchmark evidence after M4 proof gates. |
| [#194](../../issues/0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog.md) | `benchmark` | - | `needs design` | Re-open executable literature benchmark and capability evidence backlog. |
