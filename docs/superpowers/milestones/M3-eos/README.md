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
| _None_ | - | - | - | M3 has no current open provider EOS issues after #161 design-record closure. |

## Recently Closed

| Issue | PR | Capability | Backend | Summary |
| --- | --- | --- | --- | --- |
| [#161](../../issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md) | design record | `eos` | `analytic` | Closed the retired Picard path without provider implementation; future explicit association candidates return through M8 first. |
| [#214](https://github.com/ePC-SAFT/ePC-SAFT/issues/214) | [#215](https://github.com/ePC-SAFT/ePC-SAFT/pull/215) | `eos` | `analytic` | Built Python toybox for explicit association closure accuracy. |
| [#216](https://github.com/ePC-SAFT/ePC-SAFT/issues/216) | [#217](https://github.com/ePC-SAFT/ePC-SAFT/pull/217) | `explicit-association-toybox` | `none` | Added hard-chain and dispersion context to the explicit association toybox. |
| [#218](https://github.com/ePC-SAFT/ePC-SAFT/issues/218) | [#219](https://github.com/ePC-SAFT/ePC-SAFT/pull/219) | `explicit-association-toybox` | `none` | Extended explicit association toybox with follow-up analysis evidence lanes. |
