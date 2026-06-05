# Picard Step Damping Policy Grid

## Context

The explicit-association toybox currently treats seven damped Picard steps with
`lambda = 0.5` as the retained Picard approximation candidate. That single
policy is useful, but it does not answer whether lower fixed graph depth is
acceptable for easy topologies or whether deeper unrolled policies are worth the
extra autodiff cost for water-like, cross-associating, and mixed-topology cases.

## Idea

Evaluate the same Picard fixed-point form as a deterministic policy family. A
policy is selected before evaluation and has a fixed step count and fixed
damping value. The closure remains a finite unrolled expression; it is not an
adaptive convergence loop.

The exploratory grid should cover step counts `3`, `5`, `7`, `9`, and `11`
with damping values `0.35`, `0.5`, `0.65`, `0.8`, and `1.0`.

## Evidence Needed

- exact implicit association as the reference baseline;
- site-fraction, mass-action residual, and `a_assoc` errors;
- pressure-density and total-EOS proxy propagation errors;
- first-derivative and Hessian/Jacobian-style agreement;
- timing and graph-depth or evaluation-cost proxies;
- Pareto-style ranking that identifies fast, balanced, and high-accuracy
  policy lanes when supported by evidence;
- C++/CppAD stress-test handoff rows naming cases, variables, derivative
  orders, tolerances, and failure modes.

## Boundaries

This is M8 toybox evidence only. It must not promote Picard into provider EOS,
change public package APIs, or add adaptive convergence branches to the Picard
closure.
