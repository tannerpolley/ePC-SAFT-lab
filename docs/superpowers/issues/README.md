# Issue Mirrors

This folder preserves snapshots of GitHub issues that supplied durable handoff
or execution context during the monorepo program. Their fields describe the
state observed at the recorded synchronization date; they are not live intake,
readiness, dependency, or execution authority.

The retained mirrors may include source linkage, AFK/HITL classification,
acceptance criteria, proof oracles, and execution metadata as historical
evidence.

Commands, validators, paths, project fields, and open/closed state inside a
mirror are preserved observations and may no longer exist or be runnable.

Issue mirror filenames use the GitHub issue creation date, owning milestone,
and issue number:

```text
docs/superpowers/issues/YYYY-MM-DD-m#-milestone-issue-####-<slug>.md
```

Historical closed mirrors may carry this earlier retention marker:

```markdown
**Mirror Retention:** Keep
```
