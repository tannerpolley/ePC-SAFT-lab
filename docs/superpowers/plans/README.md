# Plans

This folder stores active implementation plans written from approved specs or
issue mirrors. Plans should be executable by an agent and should name exact
files, tasks, proof commands, and acceptance criteria.

After a plan is fully implemented and its durable behavior has moved into code,
tests, ADRs, project context, or package docs, remove the completed plan from
this folder. This directory should show the work that remains to be done, not
the historical implementation log.

New issue execution plans should use the GitHub issue creation date, owning
milestone, and issue number:

```text
docs/superpowers/plans/YYYY-MM-DD-m#-milestone-issue-####-<slug>-plan.md
```

Milestone or spec-only plans that do not come from one GitHub issue should still
include the creation date and milestone:

```text
docs/superpowers/plans/YYYY-MM-DD-m#-milestone-<slug>-plan.md
```
