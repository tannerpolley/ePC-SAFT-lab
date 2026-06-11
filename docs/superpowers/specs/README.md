# Specs

This folder stores active Superpowers Project specs and durable planning
overlays that still describe unimplemented work. Use specs for repo-backed
design intent, tradeoffs, non-goals, milestone linkage, and proof-oracle
candidates before implementation planning.

When an implementation-specific spec is fully delivered, remove it from this
folder unless it has become canonical doctrine that future work still depends
on. Move lasting rules into `docs/superpowers/PROJECT_CONTEXT.md`, an ADR,
or the relevant package documentation instead of keeping completed specs here.

New specs created by `project-brainstorm` should include the creation date and
owning milestone slug:

```text
docs/superpowers/specs/YYYY-MM-DD-m#-milestone-<slug>.md
```

Examples:

```text
docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md
```
