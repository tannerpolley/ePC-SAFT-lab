# Architecture Decision Records

This directory records durable architecture decisions for the `epcsaft` package when a decision is hard to reverse, surprising without context, and the result of a real trade-off.

Use sequential filenames:

```text
0001-short-title.md
0002-short-title.md
```

Keep each ADR short. A single paragraph is acceptable when it states the context, the decision, and why the decision was made.

Accepted ADRs:

- `0001-architecture-deepening-public-api-boundaries.md`: records the current public API boundaries for typed equilibrium problems, canonical parameter sets, shared regression target-family summaries, and evidence-backed capability claims.
- `0002-hard-public-api-reset-cppad-only-frontend.md`: records the hard public API cutoff, `ModelOptions` boundary, and CppAD-only public derivative policy.
- `0003-selector-core-activation-capabilities.md`: records selector-core ownership, activation-matrix capability reporting, and deletion of non-production equilibrium routes.
- `0004-associating-equilibrium-architecture.md`: records the nonassociating production-equilibrium boundary and the required complete implicit or lifted-`X_A` architecture for any future associating route.
- `0005-package-extension-split.md`: historical transition-monorepo package split, superseded by ADR 0006 while its package ownership decisions remain source evidence.
- `0006-curated-multi-repository-ownership.md`: records the final separate repository homes, early governance-only bootstrap, and later proven-owner transfer and cutover gates.
