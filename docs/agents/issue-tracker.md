# Issue Tracker: GitHub

Issues and PRDs for this repo live in GitHub Issues for the repository shown by
`git remote -v`. Before the organization transfer this is
`tannerpolley/ePC-SAFT`; after transfer it should be `ePC-SAFT/ePC-SAFT`. Use
the `gh` CLI for issue operations from inside this clone.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`
- **Read an issue**: `gh issue view <number> --comments`
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments`
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` or `--remove-label "..."`
- **Close an issue**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`. The GitHub CLI does this automatically when run inside this clone.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in the repository shown by `git remote -v`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
