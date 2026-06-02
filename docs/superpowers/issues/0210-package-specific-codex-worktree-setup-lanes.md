---
issue: 210
title: "Add package-specific Codex worktree setup lanes"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/210"
state: "open"
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: null
capability: null
backend: null
readiness: "ready"
release_target: null
last_synced: "2026-06-01"
---

# Package-Specific Codex Worktree Setup Lanes

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/210`
Status: `ready`
Last synced: `2026-06-01`
Local issue file: `docs/superpowers/issues/0210-package-specific-codex-worktree-setup-lanes.md`

## Summary

Create package-specific Codex worktree setup lanes so new threads can start in
the right package context without requiring unrelated native extensions. The
repo should keep one shared Codex environment, but that environment should route
threads through explicit provider, equilibrium, regression, and full-native
setup profiles.

The current `Provider Smoke` split is the baseline. This issue extends that
model into package lanes and reusable Codex thread prompts so agents choose the
right setup path before starting implementation work.

## Outcome

Codex worktree threads can be launched against the provider, equilibrium,
regression, or cross-package lane with setup commands, Doctor strictness, docs,
and workflow tests that match the owning package boundary.

## Key Changes

- Keep one shared `.codex/environments/environment.toml` and
  `.codex/environments/setup.ps1`.
- Add package-specific setup profiles/actions:
  - `Provider Smoke`: fresh worktree sync plus provider/core Doctor.
  - `Provider Native`: provider-only native build/check lane.
  - `Equilibrium Native`: provider prerequisites plus equilibrium extension
    native checks.
  - `Regression Native`: provider prerequisites plus regression extension
    native checks.
  - `Full Native`: all provider and extension native checks for cross-package
    proof only.
- Move profile selection into `scripts/dev/bootstrap.py` or a closely related
  repo-owned helper so `setup.ps1` stays a thin wrapper.
- Split Doctor strictness into package-owned requirements:
  - `--require-provider-sdk`
  - `--require-provider-native`
  - `--require-equilibrium-native`
  - `--require-regression-native`
  - `--require-extension-native` remains shorthand for both extension modules.
- Add reusable Codex thread launch guidance or prompt templates that make the
  lane explicit before work starts:
  - M1/M3 provider work uses `Provider Smoke` or `Provider Native`.
  - M4 equilibrium work uses `Equilibrium Native`.
  - M5 regression work uses `Regression Native`.
  - Cross-package proof uses `Full Native`.
- Keep each worktree's build outputs local to that worktree while continuing to
  reuse shared external dependencies and caches such as `uv`, Ceres SDK/cache,
  and Ipopt SDK discovery.
- Update workflow docs and guard tests so fresh worktree setup never requires
  both extension-native modules unless the selected lane explicitly asks for
  that proof.

## Public Interfaces

No package runtime API change. This is a source-checkout, Codex, build-helper,
and workflow-docs issue.

## Acceptance Criteria

- [x] `.codex/environments/environment.toml` exposes provider, equilibrium,
  regression, and full-native setup actions with clear names.
- [x] `.codex/environments/setup.ps1` delegates profile behavior instead of owning
  growing package-specific logic.
- [x] `scripts/dev/bootstrap.py` or a dedicated helper can dry-run each package
  lane and prints the exact commands it would execute.
- [x] `scripts/dev/doctor.py` supports package-specific strictness flags for
  provider native, equilibrium native, and regression native checks.
- [x] Fresh worktree smoke setup does not fail solely because equilibrium or
  regression native modules are absent.
- [x] Equilibrium and regression setup lanes require only their own extension
  native module plus provider prerequisites, not the sibling extension module.
- [x] Full-native setup remains available for cross-package proof and requires both
  extension-native modules.
- [x] Reusable Codex thread prompts or launch guidance tell agents which lane to
  choose for M1/M3 provider, M4 equilibrium, M5 regression, and cross-package
  work.
- [x] Workflow tests guard the action list, profile dry-runs, Doctor strictness,
  and docs wording.

## Non-Goals

- No provider EOS behavior changes.
- No equilibrium solver or route behavior changes.
- No regression optimizer behavior changes.
- No release packaging redesign beyond setup-lane docs and command routing.
- No automatic build of every native lane for every fresh worktree.
- No cross-milestone implementation bundled into this issue.

## Suggested Implementation Shape

Use one shared environment with thin PowerShell routing:

```text
.codex/environments/environment.toml
.codex/environments/setup.ps1
scripts/dev/bootstrap.py
scripts/dev/doctor.py
docs/agents/new-agent-start-here.md
docs/pages/development_workflows.rst
docs/protocols/build_package_dependency_protocol.rst
tests/workflows/repo/test_workflow_entrypoints.py
tests/workflows/repo/test_package_extension_boundary.py
tests/workflows/build/test_build_epcsaft.py
```

The setup profile names should reflect claims:

```text
Smoke              -> sync + provider/core Doctor
ProviderNative     -> provider-only native proof
EquilibriumNative  -> provider prerequisite + equilibrium native proof
RegressionNative   -> provider prerequisite + regression native proof
FullNative         -> provider + equilibrium + regression native proof
```

Thread prompts should name both milestone and lane. Example:

```text
For M4 equilibrium work in a new Codex worktree, run the Equilibrium Native lane.
Do not run Regression Native or Full Native unless the issue explicitly asks for
cross-package proof.
```

## Proof Oracle

```powershell
uv run python scripts/dev/bootstrap.py --dry-run --step smoke
uv run python scripts/dev/bootstrap.py --dry-run --step provider-native
uv run python scripts/dev/bootstrap.py --dry-run --step equilibrium-native
uv run python scripts/dev/bootstrap.py --dry-run --step regression-native
uv run python scripts/dev/bootstrap.py --dry-run --step full-native
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .codex/environments/setup.ps1 -Step Smoke
uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q
uv run python scripts/dev/validate_project.py quick
```

Run package-native build lanes in proportion to the implementation risk and
available dependencies. At minimum, profile dry-runs must prove the command
selection for each lane, and the fresh worktree smoke lane must be executed.

## Candidate Allowed Files

- `.codex/environments/environment.toml`
- `.codex/environments/setup.ps1`
- `.codex/environments/README.md`
- `scripts/dev/bootstrap.py`
- `scripts/dev/doctor.py`
- `scripts/dev/build_epcsaft.py`
- `scripts/dev/build_extension_dists.py`
- `scripts/dev/configure_jetbrains_project.py`
- `scripts/dev/jetbrains_run_manifest.py`
- `docs/agents/new-agent-start-here.md`
- `docs/superpowers/issues/0210-package-specific-codex-worktree-setup-lanes.md`
- `docs/pages/development_workflows.rst`
- `docs/protocols/build_package_dependency_protocol.rst`
- `tests/workflows/repo/test_workflow_entrypoints.py`
- `tests/workflows/repo/test_package_extension_boundary.py`
- `tests/workflows/build/test_build_epcsaft.py`

## Source Context

This issue comes from a post-smoke-test design discussion after `Environment
Smoke` was split from strict extension-native Doctor. The confirmed principle:
fresh Codex worktree setup should be package-lane aware, and only the selected
lane should require extension-native modules.

<!-- resolve-issue-with-goal
{
  "ready": true,
  "slug": "package-specific-codex-worktree-setup-lanes",
  "implementation_skill": "resolve-issue-with-goal",
  "issue_source_policy": "local-main-sync",
  "target_repo": "ePC-SAFT/ePC-SAFT",
  "target_repo_root": "C:\\Users\\Tanner\\Documents\\Workspaces\\Engineering\\ePC-SAFT",
  "plan_file": "docs/superpowers/issues/0210-package-specific-codex-worktree-setup-lanes.md",
  "branch_policy": "create",
  "milestone_policy": "hard",
  "milestone_title": "M1 - Packages",
  "full_roadmap": "docs/superpowers/PROJECT_CONTEXT.md",
  "full_roadmap_milestone_section": "Required milestones",
  "project_policy": "dashboard-only",
  "required_checks_policy": "allow-none-with-local-proof",
  "scope": "Codex worktree setup lanes, Doctor strictness, workflow docs, and workflow guards only",
  "proof_oracle": [
    "uv run python scripts/dev/bootstrap.py --dry-run --step smoke",
    "uv run python scripts/dev/bootstrap.py --dry-run --step provider-native",
    "uv run python scripts/dev/bootstrap.py --dry-run --step equilibrium-native",
    "uv run python scripts/dev/bootstrap.py --dry-run --step regression-native",
    "uv run python scripts/dev/bootstrap.py --dry-run --step full-native",
    "pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .codex/environments/setup.ps1 -Step Smoke",
    "uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q",
    "uv run python scripts/dev/validate_project.py quick"
  ],
  "non_goals": [
    "No provider EOS behavior changes.",
    "No equilibrium solver or route behavior changes.",
    "No regression optimizer behavior changes.",
    "No release packaging redesign beyond setup-lane docs and command routing.",
    "No automatic build of every native lane for every fresh worktree.",
    "No cross-milestone implementation bundled into this issue."
  ],
  "candidate_allowed_files": [
    ".codex/environments/environment.toml",
    ".codex/environments/setup.ps1",
    ".codex/environments/README.md",
    "scripts/dev/bootstrap.py",
    "scripts/dev/doctor.py",
    "scripts/dev/build_epcsaft.py",
    "scripts/dev/build_extension_dists.py",
    "scripts/dev/configure_jetbrains_project.py",
    "scripts/dev/jetbrains_run_manifest.py",
    "docs/agents/new-agent-start-here.md",
    "docs/superpowers/issues/0210-package-specific-codex-worktree-setup-lanes.md",
    "docs/pages/development_workflows.rst",
    "docs/protocols/build_package_dependency_protocol.rst",
    "tests/workflows/repo/test_workflow_entrypoints.py",
    "tests/workflows/repo/test_package_extension_boundary.py",
    "tests/workflows/build/test_build_epcsaft.py"
  ],
  "forbidden": [
    "implementation branch creation during issue publication",
    "package runtime API changes",
    "provider EOS behavior changes",
    "equilibrium solver behavior changes",
    "regression optimizer behavior changes",
    "PR creation during issue publication"
  ]
}
-->

```json convert_idea_to_issue_handoff
{
  "slug": "package-specific-codex-worktree-setup-lanes",
  "target_repo": "ePC-SAFT/ePC-SAFT",
  "target_repo_root": "C:\\Users\\Tanner\\Documents\\Workspaces\\Engineering\\ePC-SAFT",
  "source_repo": "ePC-SAFT/ePC-SAFT",
  "issue_source_policy": "local-main-sync",
  "title": "Add package-specific Codex worktree setup lanes",
  "outcome": "Codex worktree threads can select provider, equilibrium, regression, or full-native setup lanes with matching Doctor strictness, docs, reusable launch guidance, and workflow guards.",
  "issue_policy": "create",
  "milestone_policy": "hard",
  "milestone_title": "M1 - Packages",
  "full_roadmap": "docs/superpowers/PROJECT_CONTEXT.md",
  "full_roadmap_milestone_section": "Required milestones",
  "project_policy": "dashboard-only",
  "plan_file": "docs/superpowers/issues/0210-package-specific-codex-worktree-setup-lanes.md",
  "required_checks_policy": "allow-none-with-local-proof",
  "labels": ["type:task", "status:ready", "agent-ready", "area:build", "area:core", "area:equilibrium", "area:regression", "native"],
  "acceptance_criteria": [
    ".codex/environments/environment.toml exposes provider, equilibrium, regression, and full-native setup actions with clear names.",
    ".codex/environments/setup.ps1 delegates profile behavior instead of owning growing package-specific logic.",
    "scripts/dev/bootstrap.py or a dedicated helper can dry-run each package lane and prints the exact commands it would execute.",
    "scripts/dev/doctor.py supports package-specific strictness flags for provider native, equilibrium native, and regression native checks.",
    "Fresh worktree smoke setup does not fail solely because equilibrium or regression native modules are absent.",
    "Equilibrium and regression setup lanes require only their own extension native module plus provider prerequisites, not the sibling extension module.",
    "Full-native setup remains available for cross-package proof and requires both extension-native modules.",
    "Reusable Codex thread prompts or launch guidance tell agents which lane to choose for M1/M3 provider, M4 equilibrium, M5 regression, and cross-package work.",
    "Workflow tests guard the action list, profile dry-runs, Doctor strictness, and docs wording."
  ],
  "non_goals": [
    "No provider EOS behavior changes.",
    "No equilibrium solver or route behavior changes.",
    "No regression optimizer behavior changes.",
    "No release packaging redesign beyond setup-lane docs and command routing.",
    "No automatic build of every native lane for every fresh worktree.",
    "No cross-milestone implementation bundled into this issue."
  ],
  "proof_oracle": [
    "uv run python scripts/dev/bootstrap.py --dry-run --step smoke",
    "uv run python scripts/dev/bootstrap.py --dry-run --step provider-native",
    "uv run python scripts/dev/bootstrap.py --dry-run --step equilibrium-native",
    "uv run python scripts/dev/bootstrap.py --dry-run --step regression-native",
    "uv run python scripts/dev/bootstrap.py --dry-run --step full-native",
    "pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .codex/environments/setup.ps1 -Step Smoke",
    "uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q",
    "uv run python scripts/dev/validate_project.py quick"
  ],
  "candidate_allowed_files": [
    ".codex/environments/environment.toml",
    ".codex/environments/setup.ps1",
    ".codex/environments/README.md",
    "scripts/dev/bootstrap.py",
    "scripts/dev/doctor.py",
    "scripts/dev/build_epcsaft.py",
    "scripts/dev/build_extension_dists.py",
    "scripts/dev/configure_jetbrains_project.py",
    "scripts/dev/jetbrains_run_manifest.py",
    "docs/agents/new-agent-start-here.md",
    "docs/superpowers/issues/0210-package-specific-codex-worktree-setup-lanes.md",
    "docs/pages/development_workflows.rst",
    "docs/protocols/build_package_dependency_protocol.rst",
    "tests/workflows/repo/test_workflow_entrypoints.py",
    "tests/workflows/repo/test_package_extension_boundary.py",
    "tests/workflows/build/test_build_epcsaft.py"
  ],
  "canonical_issue_scope": {
    "source": "user prompt",
    "selected_slice": "Full automation for package-specific Codex worktree setup lanes.",
    "included_scope": [
      "Package-specific environment actions and setup profiles.",
      "Package-specific Doctor strictness flags.",
      "Reusable Codex thread launch prompts or guidance for M1/M3, M4, M5, and cross-package lanes.",
      "Workflow docs and tests that prevent fresh worktree setup from requiring unrelated native extensions."
    ],
    "excluded_scope": [
      "Provider EOS implementation changes.",
      "Equilibrium solver implementation changes.",
      "Regression optimizer implementation changes.",
      "Release packaging redesign outside setup-lane command routing."
    ],
    "canonical_reason": "The user selected full automation, and the package split docs show this is package-boundary workflow work best handled as one M1 coordination issue rather than implementation in M3, M4, or M5.",
    "question_id": "canonical_scope"
  },
  "issue_count_policy": "single-issue",
  "decomposition_policy": "single-issue",
  "issue_set": [],
  "execution_boundary": {
    "skill_scope": "issue-and-plan-publication-only",
    "approval_meaning": "publish-issue-and-plan-only",
    "implementation_skill": "resolve-issue-with-goal",
    "allowed_after_approval": [
      "repo-qualified GitHub issue create/update",
      "durable local issue file writes",
      "default-branch commit/push for local issue docs only"
    ],
    "forbidden_after_approval": [
      "implementation branch creation",
      "implementation edits",
      "implementation commits",
      "implementation pushes",
      "PR creation",
      "merge",
      "GoalBuddy board",
      "native goal activation"
    ]
  },
  "doc_grill_evidence": {
    "docs_read": [
      "docs/agents/issue-tracker.md",
      "docs/agents/triage-labels.md",
      "docs/superpowers/PROJECT_CONTEXT.md",
      "docs/superpowers/milestones/M1-packages/README.md",
      "docs/adr/0005-package-extension-split.md",
      "docs/protocols/build_package_dependency_protocol.rst"
    ],
    "constraints_found": [
      "M1 - Packages owns monorepo package layout, package ownership, provider-only build proof, extension-native boundaries, and package CI/docs/release structure.",
      "ADR 0005 assigns provider ownership to epcsaft, Ipopt-backed equilibrium to epcsaft-equilibrium, and Ceres-backed regression to epcsaft-regression.",
      "The build protocol already separates provider-only, equilibrium extension, regression extension, full native, and package-boundary validation claims.",
      "Issue tracker rules require one milestone per issue and a split only when implementation scope truly belongs to different milestones."
    ],
    "contradictions_found": [
      "Fresh worktree setup can be treated as one generic environment action even though package-native proof has different provider, equilibrium, and regression requirements."
    ],
    "questions_derived": [
      "Whether to publish one M1 issue or split by package lane.",
      "Whether the canonical scope should be setup lanes, full automation, or docs only.",
      "Whether to publish immediately or draft locally first."
    ]
  },
  "decision_log": [
    {
      "decision": "Target repository and tracker",
      "status": "discoverable",
      "source": "repo gate and tracker docs",
      "no_question_needed_reason": "repo-gate passed for ePC-SAFT/ePC-SAFT and docs/agents/issue-tracker.md proves GitHub Issues usage."
    },
    {
      "decision": "Milestone assignment",
      "status": "discoverable",
      "source": "PROJECT_CONTEXT, M1 README, ADR 0005, build protocol",
      "no_question_needed_reason": "The work changes package-boundary setup lanes, build-helper routing, Doctor strictness, and source-checkout workflow docs, which M1 owns."
    },
    {
      "decision": "Issue count",
      "status": "locked",
      "source": "user",
      "question_id": "issue_shape"
    },
    {
      "decision": "Canonical scope",
      "status": "locked",
      "source": "user",
      "question_id": "canonical_scope"
    },
    {
      "decision": "Publication approval",
      "status": "locked",
      "source": "user",
      "question_id": "publish_approval"
    }
  ],
  "question_log": [
    {
      "id": "issue_shape",
      "decision": "Issue count",
      "tool": "request_user_input",
      "question": "How should this worktree setup idea be published as one issue or multiple issues?",
      "answer": "One M1 Issue (Recommended)",
      "source": "user"
    },
    {
      "id": "canonical_scope",
      "decision": "Canonical scope",
      "tool": "request_user_input",
      "question": "What should the issue require as the canonical scope?",
      "answer": "Full Automation",
      "source": "user"
    },
    {
      "id": "publish_approval",
      "decision": "Publication approval",
      "tool": "request_user_input",
      "question": "After I draft the local issue file, should I publish it to GitHub and commit it to main?",
      "answer": "Publish (Recommended)",
      "source": "user"
    }
  ],
  "unresolved_decisions": [],
  "skills_used": [
    {
      "skill": "convert-idea-to-issue",
      "why": "The user explicitly requested an official GitHub issue from the design discussion.",
      "evidence": "Repo gate passed; this plan includes issue policy, milestone, local plan file, acceptance criteria, proof oracle, and execution boundary."
    },
    {
      "skill": "grill-with-docs",
      "why": "Mandatory for repo-backed issue planning against tracker docs, roadmap, ADRs, and package-boundary protocol.",
      "evidence": "PROJECT_CONTEXT, issue tracker docs, ADR 0005, M1 README, and build protocol shaped the M1 package-boundary scope."
    },
    {
      "skill": "superpowers:brainstorming",
      "why": "The request turns a workflow design idea into implementation scope.",
      "evidence": "The canonical-scope question selected full automation rather than docs-only or minimal setup lanes."
    },
    {
      "skill": "improve-codebase-architecture",
      "why": "The issue affects package/workflow boundaries and setup-lane architecture.",
      "evidence": "The plan separates provider, equilibrium, regression, and cross-package proof lanes while keeping one shared environment."
    }
  ]
}
```
