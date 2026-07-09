# Issue Mirrors

This folder stores local mirrors for GitHub issues that need durable handoff or
execution context. GitHub remains authoritative for issue state, labels,
comments, dependencies, and PR links.

Issue mirrors used by `project-resolve` must include source spec or source plan
linkage, AFK/HITL classification, acceptance criteria, proof oracle, and goal
execution metadata.

Issue mirror filenames use the GitHub issue creation date, owning milestone,
and issue number:

```text
docs/superpowers/issues/YYYY-MM-DD-m#-milestone-issue-####-<slug>.md
```

Keep mirrors only for unresolved GitHub issues that need local handoff or
execution context. Delete mirrors for closed issues unless a repo maintainer
explicitly marks the file as archival documentation with:

```markdown
**Mirror Retention:** Keep
```
