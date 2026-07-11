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
| [#161](../../issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md) | `eos` | `CppAD` | `needs direct CppAD proof` | Independent explicit-association and Picard CppAD evidence issue; not a HELD, M4, or #208 dependency. |
| [#439](../../issues/2026-07-11-m3-eos-issue-0439-m3-establish-versioned-state-resolved-model-input.md) | `eos` | native | `ready` | Non-executable tracker for the versioned state-resolved input cutover. |
| [#440](../../issues/2026-07-11-m3-eos-issue-0440-m3-require-complete-configuration-and-typed-scientific-records.md) | `eos` | Python | `ready` | Require a complete configuration and typed source-bearing correlations. |
| [#441](../../issues/2026-07-11-m3-eos-issue-0441-m3-compile-one-resolved-native-input-and-immutable-state-receipt.md) | `eos` | native | `blocked` | Evaluate one immutable native input and detached state receipt. |
| [#442](../../issues/2026-07-11-m3-eos-issue-0442-m3-cut-provider-frontend-and-native-calls-to-the-resolved-graph.md) | `eos` | native | `blocked` | Cut provider frontends, calls, and tests to the resolved graph. |
| [#444](../../issues/2026-07-11-m3-eos-issue-0444-m3-publish-resolved-input-sdk-v1-and-remove-displaced-serializers.md) | `eos` | native | `blocked` | Publish SDK v1 only after M4/M5 consumers land, then delete displaced serializers. |

#440 is technically scoped and ready, but Task 9 execution remains paused until
the user explicitly resumes that bounded leaf. It is deliberately not marked
`agent-ready`; the abandoned monolithic Task 9 branch is not a continuation
path.

## Current Plan

- [Versioned state-resolved model input](../../plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md)

## Recently Closed

| Issue | PR | Capability | Backend | Summary |
| --- | --- | --- | --- | --- |
| [#207](../../issues/2026-06-01-m3-eos-issue-0207-expose-objective-free-local-phase-eos-derivative-bundle.md) | [commit 58bcf830](https://github.com/ePC-SAFT/ePC-SAFT/commit/58bcf830) | `derivatives` | `CppAD` | Exposed the objective-free local phase EOS derivative bundle needed by #208. |
| [#214](https://github.com/ePC-SAFT/ePC-SAFT/issues/214) | [#215](https://github.com/ePC-SAFT/ePC-SAFT/pull/215) | `eos` | `analytic` | Built Python toybox for explicit association closure accuracy. |
| [#216](https://github.com/ePC-SAFT/ePC-SAFT/issues/216) | [#217](https://github.com/ePC-SAFT/ePC-SAFT/pull/217) | `explicit-association-toybox` | `none` | Added hard-chain and dispersion context to the explicit association toybox. |
| [#218](https://github.com/ePC-SAFT/ePC-SAFT/issues/218) | [#219](https://github.com/ePC-SAFT/ePC-SAFT/pull/219) | `explicit-association-toybox` | `none` | Extended explicit association toybox with follow-up analysis evidence lanes. |
