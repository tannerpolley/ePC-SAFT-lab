# M3 - EOS

Provider EOS/state/parameters, native SDK contract, exact derivatives,
CppAD/implicit sensitivities, and provider-only capability claims.

## Project Field Defaults

- Package: `core`
- Capability: `eos` or `derivatives`
- Backend: `analytic`, `CppAD`, or `implicit` when the implementation depends on it
- Release target: `core-0.x` for committed provider behavior, `future` for design work

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#161](../../issues/0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md) | `eos` | `analytic` | `needs design` | Design explicit PC-SAFT association-site closures for EOS evaluation. |
