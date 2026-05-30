# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `agent-ready`        | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role, use the corresponding label string from this table.

Edit the right-hand column if the GitHub label vocabulary changes.

Milestone routing labels:

- Use `area:*` labels for the owning package or subsystem.
- Use `backend:*` labels for CppAD, Ceres, or Ipopt-specific work.
- Use `type:bug`, `type:feature`, and `type:task` as compatibility labels for
  the native GitHub issue types `Bug`, `Feature`, and `Task`.
- Use `status:*` labels only for durable issue state that should remain visible
  outside the GitHub Project.
- Use `release:blocker` only for work that blocks the issue's target milestone
  or release gate.
