# ePC-SAFT Agent Instructions

This is tracked repo policy for agents working in this repository. Keep it short.
Durable workflow details belong in the referenced docs, not in this file.

## Start Here

- Read `docs/superpowers/PROJECT_CONTEXT.md` before planning, coding, reviewing, or merging. It is the package-context and completion-standard document unless the user narrows scope.
- For fresh setup and first commands, read `docs/agents/new-agent-start-here.md`.
- For test selection, validation, and routine development workflows, read `docs/pages/development_workflows.rst`.
- For build, package, CMake, dependency, Ceres, CppAD, Ipopt, CI-lane, wheel, or sdist changes, read `docs/protocols/build_package_dependency_protocol.rst`.
- For direct CMake preset work, read `CMAKE.md` and use the repo wrapper policy there.
- For GitHub Issues, milestones, Projects, labels, issue types, dependencies, and PR policy, read `docs/agents/issue-tracker.md`.
- For IntelliJ-backed work, read `docs/agents/INTELLIJ.md`.
- For file and analysis layout, read `docs/pages/project_structure.rst`.

## Tooling Rules


- IMPORTANT: Using intellij-index MCP tools for code navigation and refactoring.
- For non-trivial code, build, native, test, refactor, debug, architecture, or validation work, use IntelliJ Bridge/MCP first. Before falling back to shell, run tool discovery for IntelliJ/JetBrains MCP tools and record a short receipt: `IntelliJ MCP available: yes/no`, `tools found: ...`, and `fallback approved by user: yes/no`.
- If IntelliJ/JetBrains MCP tools are not exposed for a non-trivial task, stop and ask the user to open or focus IntelliJ on this repo. Do not continue with shell fallback unless the user explicitly approves fallback for that task.
- Simple docs edits, issue checks, status checks, and small Q&A may use shell and `rg` directly but only after trying Intellij Tools.
- Use the user-level `chemical-engineer` skill for thermodynamics, phase or chemical equilibrium, equation tracing, native seams, and scientific validation.

## Agent skills

### Issue tracker

Issues and PRDs are tracked in GitHub Issues for `ePC-SAFT/ePC-SAFT`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the repo triage vocabulary, including `agent-ready` for AFK-ready issues. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo; read root `CONTEXT.md`, `docs/superpowers/PROJECT_CONTEXT.md`, and relevant `docs/adr/` entries. See `docs/agents/domain.md`.

## Repo Invariants

- The active package layout is `packages/epcsaft`, `packages/epcsaft-equilibrium`, and `packages/epcsaft-regression`.
- Before creating or updating any issue, milestone plan, proof oracle, candidate
  file list, acceptance criteria, or hidden execution marker, identify the
  owning milestone and package. M3 provider/EOS work is `packages/epcsaft/**`
  plus provider-owned repo docs/build metadata/SDK manifests/provider tests; M4
  is `packages/epcsaft-equilibrium/**`; M5 is
  `packages/epcsaft-regression/**`. Search hits in sibling packages are
  follow-up candidates only unless the user explicitly approves a
  cross-milestone issue set.
- Public repo tools, scripts, tests, and docs must use developer-neutral names. Do not add tracked Codex-branded public workflow files.
- Do not reintroduce Conda, Cython, setuptools editable installs, `setup.py build_ext`, retired sibling-repo workflows, or old compatibility shims.
- Keep capability claims honest. Do not broaden provider, equilibrium, regression, native, Ceres, Ipopt, or CppAD claims without matching validation evidence.
- Before adding a file, inspect nearby structure and choose the existing category that matches repo conventions.
- When deleting tracked files, also remove now-empty owned folders and stale references unless the folder is an intentional documented skeleton.
- Paper-validation parameter snapshots follow `docs/pages/project_structure.rst`; do not duplicate that layout rule here.
- Downstream projects own application studies and metrics. Upstream fixes should reduce repeated downstream friction to compact public API reproductions before adding package tests or fixtures.

## Delegation

- Use repo owner/sub-agents for non-trivial work when slices can proceed independently with non-overlapping file ownership.
- Keep final integration, cross-cutting decisions, GitHub state, and branch/merge/cleanup actions on the main thread.
- Do not delegate tasks that require coordinated native clean/rebuild actions unless the active issue or goal plan explicitly assigns that ownership.

## Validation And Handoff

- Validate in proportion to risk and report skipped validation clearly.
- Tests that compute model predictions must use real, traceable literature data
  and must write a retained fit plot showing the literature data and model
  predictions together.
- When creating or updating plots, figures, or visual analysis artifacts, the
  final chat/handoff must render every new or updated plot inline with absolute
  filesystem paths and include a compact Markdown table summarizing the real
  retained data behind the plot. Do not describe plots only in prose. If a plot
  cannot be rendered, report the exact path and blocker.
- Keep user-facing docs updated when public API behavior, install/build/test workflow, package layout, or capability claims change.
- Before handoff, review `git status --short` and do not leave your own tracked changes unstaged or uncommitted unless the user requested that.
- Run the repo cleanup hook before reporting completion:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
