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
| [#161](../../issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md) | `eos` | `CppAD` | `needs direct CppAD proof` | Independent explicit-association CppAD evidence issue; not a HELD, M4, or #208 dependency. |

## Recently Closed

| Issue | PR | Capability | Backend | Summary |
| --- | --- | --- | --- | --- |
| [#207](../../issues/2026-06-01-m3-eos-issue-0207-expose-objective-free-local-phase-eos-derivative-bundle.md) | [commit 58bcf830](https://github.com/ePC-SAFT/ePC-SAFT/commit/58bcf830) | `derivatives` | `CppAD` | Exposed the objective-free local phase EOS derivative bundle needed by #208. |
| [#214](https://github.com/ePC-SAFT/ePC-SAFT/issues/214) | [#215](https://github.com/ePC-SAFT/ePC-SAFT/pull/215) | `eos` | `analytic` | Built Python toybox for explicit association closure accuracy. |
| [#216](https://github.com/ePC-SAFT/ePC-SAFT/issues/216) | [#217](https://github.com/ePC-SAFT/ePC-SAFT/pull/217) | `explicit-association-toybox` | `none` | Added hard-chain and dispersion context to the explicit association toybox. |
| [#218](https://github.com/ePC-SAFT/ePC-SAFT/issues/218) | [#219](https://github.com/ePC-SAFT/ePC-SAFT/pull/219) | `explicit-association-toybox` | `none` | Extended explicit association toybox with follow-up analysis evidence lanes. |
