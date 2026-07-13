# Early Curated Repository Bootstrap And Stage 13 Cutover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorder the recovery program so Stage 11 establishes clean local
repository homes before blocked scientific work, move proven-owner transfer and
cutover to Stage 13, create four governance-only local skeletons, and stop.

**Architecture:** The transition monorepo remains the executable source and
reference archive. Stage 11 creates empty, independently committed repository
homes under one collision-free parent; Stages 4-6 retain their scientific
gates; Stage 13 later transfers accepted owners and proves installed-artifact
parity before any source-of-truth cutover.

**Tech Stack:** Markdown ADR/spec/plan records, YAML receipts, Git, shell
structural checks, strict Sphinx documentation validation.

## Global Constraints

- Design authority:
  `docs/superpowers/specs/2026-07-13-m0-early-curated-repository-bootstrap-and-stage-13-cutover-design.md`.
- Local parent:
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project`.
- Create exactly `ePC-SAFT`, `ePC-SAFT-equilibrium`,
  `ePC-SAFT-regression`, and `ePC-SAFT-organization` beneath that parent.
- Defer the optional validation repository.
- Initialize each skeleton with `git init --initial-branch=main` and one local
  bootstrap commit; add no remote.
- Copy `LICENSE` byte-for-byte from the transition monorepo.
- Treat the checked-out transition `LICENSE` as the copy source. Record its
  pre-existing normalized `HEAD:LICENSE` hash separately; do not rewrite
  transition history. Destination worktree and committed license hashes must
  both match the checked-out source.
- Create no `pyproject.toml`, `CMakeLists.txt`, build backend, package module,
  executable test, workflow, capability file, or release configuration.
- Copy no production source, native library, build output, distribution,
  environment, paper, analysis, scientific result, branch, stash, or Git
  history.
- Do not mutate GitHub repositories, issues, milestones, Projects,
  organization settings, remotes, releases, or publications.
- Do not modify or clean the retired paths
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-regression` and
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-CE`.
- Their `.git` pointer SHA-256 values must remain respectively
  `da3d66692907ab7d8e18ca01c66c474b333a4facd49bba3daa8eae787f8903d9`
  and
  `0d74eae9dee9277d3669dbf2122a89a70f87676369ae45a2dc567d983e636df7`.
- Preserve the staged Chapman paper. The existing July 12 multi-repository
  wording is in scope and becomes part of the coordinated program amendment.
- No push is authorized.
- `ePC-SAFT/ePC-SAFT` is already the transition monorepo's `origin` identity.
  Do not attach the clean provider skeleton to it or imply a new repository can
  be created at that name. Retain/rename/repurpose strategy is deferred to an
  explicit later gate and must forbid force-push or history replacement.

---

## Repository Skeleton Content Matrix

Every package home tracks exactly:

```text
.gitattributes
.gitignore
AGENTS.md
CONTEXT.md
LICENSE
README.md
docs/README.md
docs/ownership.md
docs/migration/bootstrap-receipt.yaml
src/README.md
tests/README.md
```

The organization-policy home tracks exactly:

```text
.gitattributes
.gitignore
AGENTS.md
CONTEXT.md
LICENSE
README.md
docs/ownership.md
docs/migration/bootstrap-receipt.yaml
profile/README.md
```

All `.gitattributes` files contain:

```gitattributes
* text=auto eol=lf
LICENSE -text
```

All `.gitignore` files contain:

```gitignore
.venv/
__pycache__/
*.py[cod]
*.so
*.pyd
.pytest_cache/
.ruff_cache/
.mypy_cache/
build/
dist/
*.egg-info/
.idea/
.vscode/
```

Each package receipt uses schema
`epcsaft.curated-repository-bootstrap-receipt`, schema version `1`, date
`2026-07-13`, its exact role/path/intended GitHub home, and the exact
program-amendment commit captured after Task 1. Every receipt contains:

```yaml
stage: 11
initial_branch: main
initial_commit_policy: clean_history_single_bootstrap_commit
production_owners_transferred: []
scientific_capabilities_claimed: []
remote_created: false
push_performed: false
source_of_truth: false
```

The Task 2 contract stores a `content_markers` map for every repository. At a
minimum, validation must require literal markers proving:

- the exact local identity, intended GitHub home, and repository role in the
  root `README.md`;
- `governance-only skeleton`, `not a usable package`, and
  `source_of_truth: false` in the root context;
- the allowed owners, `depends_on`, and `forbidden_dependencies` in
  `docs/ownership.md`;
- the transition monorepo and Task 1 program-amendment commit in
  `docs/README.md` for package homes;
- `reserved` and `no accepted runtime owner` in `src/README.md`;
- `reserved` and `no accepted proof owner` in `tests/README.md`;
- the no-transfer, no-capability, no-remote, no-push, and no-source-of-truth
  receipt fields; and
- for the organization home, its organization-policy role, deferred live
  policy, package-owned boundaries, and reserved profile instead of package
  source/test assertions.

The final validator loads these markers from the contract and checks every
literal against the corresponding tracked file. Exact paths alone are not
acceptance evidence.

---

### Task 1: Amend The Program And Supersede The Monorepo-Target ADR

**Use Cases:**

- A future agent can distinguish repository-home bootstrap from
  proven-runtime transfer and source-of-truth cutover.
- Stage 12 cannot retire the transition repository before Stage 13 passes.

**Files:**

- Modify:
  `docs/superpowers/specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md`
- Modify:
  `docs/superpowers/plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md`
- Modify: `docs/adr/0005-package-extension-split.md`
- Create: `docs/adr/0006-curated-multi-repository-ownership.md`
- Modify: `docs/adr/README.md`

**Interfaces:**

- Consumes: the approved July 13 bootstrap design and current Stage 4 blocker.
- Produces: the controlling `3 -> 11 -> 4 -> 5 -> 6 -> 13 -> 12` core DAG,
  Stage 11 bootstrap contract, Stage 13 transfer/cutover contract, and ADR 0006.

- [ ] **Step 1: Record the pre-amendment RED evidence.**

Run:

```bash
rg -n "Stage 13|Task 13|3 -> 11" \
  docs/superpowers/specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md \
  docs/superpowers/plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md \
  docs/adr
```

Expected: no controlling Stage 13 or early-Stage-11 DAG exists.

- [ ] **Step 2: Amend the parent spec.**

Make Stage 11 a repository-home bootstrap with the exact paths and skeleton
contract from the design. Add Stage 13 with the former core transfer, installed
artifact, parity, provenance, and separately approved development-source
cutover obligations. Reserve transition-repository retirement/archive mutation
solely for Stage 12, which consumes Stage 13. Replace the DAG with:

```text
1 -> 2 -> 3 -> 11 repository-home bootstrap
                   |
                   +-> 4 -> 5 -> 6
                                  |
                                  +-> 13 core transfer/cutover -> 12 core closeout
                                  |
                                  +-> 7 neutral HELD
                                  |     +-> 8 association
                                  |     +-> 9 electrolyte HELD2
                                  +-> 10 standalone CE -> later CPE
```

Reconcile every cardinality and ownership statement: replace controlling
`twelve`/`Twelve-Stage` wording with thirteen-stage wording; move former Stage
11 runtime, package, repository-readiness, migration, and M5 admission duties
to Stage 13; keep Stage 11 governance-only; and make Stage 12 the only
retirement/archive owner. Stages 7-10 are optional branches from Stage 6 and
are not Stage 13 inputs; each needs its own later transfer leaf if accepted.

- [ ] **Step 3: Amend the parent plan.**

Replace Task 11 with the local-home/governance bootstrap task. Add Task 13 with
the former core owner-transfer and installed-artifact proof. Make Task 12
consume Task 13 and exclusively own retirement/archive. Reconcile all thirteen-
task, M5, metadata, proof-receipt, and migration-consumer references rather
than editing only task headings. Record that this execution stops after the
Task 11 skeleton checkpoint.

- [ ] **Step 4: Create ADR 0006 and mark ADR 0005 superseded.**

ADR 0006 must decide:

- final separate repositories for provider, equilibrium, regression, and
  organization policy;
- optional validation ownership remains deferred;
- one-way provider-to-extension dependencies;
- early governance bootstrap is not runtime transfer;
- Stage 13 owns core proof and separately approved development-source cutover;
- Stage 12 alone owns transition-repository retirement/archive; and
- remote creation, push, publication, and source-of-truth changes remain
  separate user gates.

Change only ADR 0005's status to `Superseded by ADR 0006`; preserve its context,
decision, consequences, and migration gate verbatim. Add ADR 0006 to the ADR
index.

- [ ] **Step 5: Run GREEN documentation checks.**

Run:

```bash
rg -n "Stage 13|Task 13|11 repository-home bootstrap" \
  docs/superpowers/specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md \
  docs/superpowers/plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md \
  docs/adr/0006-curated-multi-repository-ownership.md
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
```

Expected: all commands pass and the three documents agree on dependency order.

- [ ] **Step 6: Commit the program amendment.**

```bash
git add \
  docs/adr/0005-package-extension-split.md \
  docs/adr/0006-curated-multi-repository-ownership.md \
  docs/adr/README.md \
  docs/superpowers/specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md \
  docs/superpowers/plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md
git commit --only -m "docs(governance): bootstrap repository homes before cutover" -- \
  docs/adr/0005-package-extension-split.md \
  docs/adr/0006-curated-multi-repository-ownership.md \
  docs/adr/README.md \
  docs/superpowers/specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md \
  docs/superpowers/plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md
```

Expected: the Chapman paper remains staged and excluded.

### Task 2: Record The Machine-Readable Bootstrap Contract

**Use Cases:**

- Skeleton creation rejects path collisions and scope expansion.
- Final verification compares each repository against one exact file contract.

**Files:**

- Create:
  `docs/superpowers/milestones/M0-governance/curated-repository-bootstrap-contract.yaml`

**Interfaces:**

- Consumes: the Task 1 program-amendment commit.
- Produces: exact local paths, intended GitHub homes, repository roles, tracked
  file lists, protected remnants, license hash, and negative transfer flags.

- [ ] **Step 1: Prove the destination parent is absent and remnants match.**

Run:

```bash
test ! -e /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project
sha256sum \
  /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-regression/.git \
  /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-CE/.git
sha256sum LICENSE
```

Expected: the parent is absent; remnant hashes equal the Global Constraints;
the GPL license hash is
`0b383d5a63da644f628d99c33976ea6487ed89aaa59f0b3257992deac1171e6b`.

- [ ] **Step 2: Write the exact YAML contract.**

Record the four local paths, intended GitHub homes, roles, exact tracked
file arrays from the Content Matrix, program-amendment commit, protected path
hashes, GPL hash, clean-history policy, `remote_created: false`, and
`production_transfer_authorized: false`. Record `content_markers` for every
governance file using the minimum assertions in the Content Matrix section.
For the provider, record `github_home_state:
existing_transition_remote_identity` and a deferred retain/rename/repurpose
decision that forbids force-push and history replacement. Treat the other
GitHub names as intended mappings, not created remotes.

- [ ] **Step 3: Parse and validate the contract.**

```bash
uv run --no-sync python - <<'PY'
from pathlib import Path
import yaml

path = Path("docs/superpowers/milestones/M0-governance/curated-repository-bootstrap-contract.yaml")
data = yaml.safe_load(path.read_text(encoding="utf-8"))
assert data["schema"] == "epcsaft.curated-repository-bootstrap-contract"
assert data["schema_version"] == 1
assert len(data["repositories"]) == 4
assert data["production_transfer_authorized"] is False
assert all(repo["remote_created"] is False for repo in data["repositories"])
assert all(repo["content_markers"] for repo in data["repositories"])
provider = next(repo for repo in data["repositories"] if repo["role"] == "provider")
assert provider["github_home_state"] == "existing_transition_remote_identity"
PY
git diff --check
```

Expected: PASS.

- [ ] **Step 4: Commit the contract.**

```bash
git add docs/superpowers/milestones/M0-governance/curated-repository-bootstrap-contract.yaml
git commit --only -m "docs(governance): define curated repository skeleton contract" -- \
  docs/superpowers/milestones/M0-governance/curated-repository-bootstrap-contract.yaml
```

### Task 3: Bootstrap The Provider Repository Home

**Use Cases:**

- Provider work has a clean future home without importing Ipopt, Ceres, or
  unaccepted runtime owners.

**Files:**

- Create the package skeleton matrix under:
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT`

**Interfaces:**

- Consumes: Task 2 contract and the Task 1 program revision.
- Produces: one local Git repository for distribution/import `epcsaft`, future
  GitHub repository `ePC-SAFT/ePC-SAFT`.

- [ ] **Step 1: Create directories and governance files.**

Create exactly the package tree from the Content Matrix. State that this home
owns provider EOS/state/parameters, CppAD, and the resolved-input SDK; forbids
Ipopt, Ceres, equilibrium dispatch, and regression workflows; and currently
contains no transferred runtime owner.

- [ ] **Step 2: Write the provider receipt.**

Use the shared receipt fields plus:

```yaml
repository_role: provider
distribution_name: epcsaft
import_name: epcsaft
intended_github_home: ePC-SAFT/ePC-SAFT
depends_on: []
forbidden_dependencies:
  - epcsaft-equilibrium
  - epcsaft-regression
  - Ipopt
  - Ceres
```

- [ ] **Step 3: Initialize and commit.**

```bash
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT init --initial-branch=main
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT add .
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT commit -m "chore: bootstrap provider repository home"
```

- [ ] **Step 4: Verify exact emptiness and isolation.**

Assert the tracked file list equals the package Content Matrix, `git status
--short` is empty, `git remote` is empty, and no `.py`, `.pyi`, `.cpp`, `.h`,
`.so`, `.pyd`, wheel, archive, or CMake file exists.

### Task 4: Bootstrap The Equilibrium Repository Home

**Use Cases:**

- Equilibrium and Ipopt work has a clean future home without provider or Ceres
  ownership.

**Files:**

- Create the package skeleton matrix under:
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-equilibrium`

**Interfaces:**

- Consumes: Task 2 contract and the Task 1 program revision.
- Produces: one local Git repository for distribution `epcsaft-equilibrium`,
  import `epcsaft_equilibrium`, intended GitHub home
  `ePC-SAFT/ePC-SAFT-equilibrium`.

- [ ] **Step 1: Create directories and governance files.**

Create exactly the package tree from the Content Matrix. State that this home
owns equilibrium routes, phase discovery, local NLPs, Ipopt, certification,
and equilibrium results; consumes only a compatible installed provider; and
forbids provider and Ceres ownership.

- [ ] **Step 2: Write the equilibrium receipt.**

Use the shared fields plus:

```yaml
repository_role: equilibrium
distribution_name: epcsaft-equilibrium
import_name: epcsaft_equilibrium
intended_github_home: ePC-SAFT/ePC-SAFT-equilibrium
depends_on:
  - epcsaft
forbidden_dependencies:
  - epcsaft-regression
  - Ceres
```

- [ ] **Step 3: Initialize and commit.**

```bash
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-equilibrium init --initial-branch=main
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-equilibrium add .
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-equilibrium commit -m "chore: bootstrap equilibrium repository home"
```

- [ ] **Step 4: Verify exact emptiness and isolation.**

Apply the same tracked-file, clean-status, no-remote, and forbidden-source
checks as Task 3.

### Task 5: Bootstrap The Regression Repository Home

**Use Cases:**

- Regression and Ceres work, including deferred issue #469, has a clean future
  home without provider or Ipopt ownership.

**Files:**

- Create the package skeleton matrix under:
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-regression`

**Interfaces:**

- Consumes: Task 2 contract and the Task 1 program revision.
- Produces: one local Git repository for distribution `epcsaft-regression`,
  import `epcsaft_regression`, intended GitHub home
  `ePC-SAFT/ePC-SAFT-regression`.

- [ ] **Step 1: Create directories and governance files.**

Create exactly the package tree from the Content Matrix. State that this home
owns strict target datasets, fitted parameters, Ceres, fit receipts, and
regression results; consumes only a compatible installed provider; and forbids
provider, equilibrium, and Ipopt ownership.

- [ ] **Step 2: Write the regression receipt.**

Use the shared fields plus:

```yaml
repository_role: regression
distribution_name: epcsaft-regression
import_name: epcsaft_regression
intended_github_home: ePC-SAFT/ePC-SAFT-regression
deferred_issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/469
depends_on:
  - epcsaft
forbidden_dependencies:
  - epcsaft-equilibrium
  - Ipopt
```

- [ ] **Step 3: Initialize and commit.**

```bash
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-regression init --initial-branch=main
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-regression add .
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-regression commit -m "chore: bootstrap regression repository home"
```

- [ ] **Step 4: Verify exact emptiness and isolation.**

Apply the same tracked-file, clean-status, no-remote, and forbidden-source
checks as Task 3.

### Task 6: Bootstrap The Organization-Policy Repository Home

**Use Cases:**

- Shared organization policy has a future home without prematurely changing
  live organization settings or repository-local release ownership.

**Files:**

- Create the organization skeleton matrix under:
  `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization`

**Interfaces:**

- Consumes: Task 2 contract and the Task 1 program revision.
- Produces: one local Git repository mapped to intended GitHub home
  `ePC-SAFT/.github`.

- [ ] **Step 1: Create directories and governance files.**

Create exactly the organization Content Matrix. Record future ownership of the
organization profile, shared issue/PR templates, reusable workflow policy, and
roadmap conventions. State that repository-local tests, builds, releases,
capabilities, and package docs remain package-owned.

- [ ] **Step 2: Write the organization receipt.**

Use the shared negative fields plus:

```yaml
repository_role: organization_policy
intended_github_home: ePC-SAFT/.github
live_organization_policy_changed: false
issues_transferred: []
milestones_transferred: []
project_items_transferred: []
```

- [ ] **Step 3: Initialize and commit.**

```bash
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization init --initial-branch=main
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization add .
git -C /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization commit -m "chore: bootstrap organization policy home"
```

- [ ] **Step 4: Verify exact emptiness and isolation.**

Assert the tracked file list equals the organization Content Matrix, status is
clean, remotes are empty, and no live template or workflow file exists.

### Task 7: Record The Stage 11 Bootstrap Receipt And Stop

**Use Cases:**

- A future agent can verify every local repository identity without treating a
  skeleton as transferred capability.
- The checkpoint cannot drift into source transfer or external mutation.
- Acceptance proof records that Stage 11 cutover is deliberately deferred to
  Stage 13 and that no displaced executable owner moved during bootstrap.

**Files:**

- Create:
  `docs/superpowers/milestones/M0-governance/stage-11-curated-repository-bootstrap-receipt.yaml`

**Interfaces:**

- Consumes: the four clean local repository commit hashes and Task 2 contract.
- Produces: the accepted Stage 11 local-bootstrap receipt and an explicit stop
  before Stage 4, Stage 13, or external tracker work.

- [ ] **Step 1: Capture exact repository identities.**

Run for each skeleton:

```bash
for repo in \
  /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT \
  /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-equilibrium \
  /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-regression \
  /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization
do
  git -C "$repo" rev-parse HEAD
  git -C "$repo" branch --show-current
  git -C "$repo" status --short
  git -C "$repo" remote -v
  git -C "$repo" ls-files
done
```

Record the exact hashes; require branch `main`, empty status, empty remotes, and
the exact tracked file arrays.

- [ ] **Step 2: Write the source receipt.**

Record program/design/contract commits, the four local paths and commits,
license hashes, protected remnant hashes, `production_owners_transferred: []`,
`scientific_capabilities_claimed: []`, `issues_transferred: []`,
`remote_created: false`, `push_performed: false`, `source_of_truth_changed:
false`, `stage_13_started: false`, and `stop_reason:
user_requested_stop_after_local_skeleton_creation`.

- [ ] **Step 3: Run the full structural proof.**

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py \
  --plan-path docs/superpowers/plans/2026-07-13-m0-early-curated-repository-bootstrap-and-stage-13-cutover-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py \
  --plan-path docs/superpowers/plans/2026-07-13-m0-early-curated-repository-bootstrap-and-stage-13-cutover-plan.md
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

Also load every repository's `content_markers` from the Task 2 contract and
assert each literal occurs in its required tracked file. Assert all four Git
repositories are clean and remote-free, the package homes contain no
implementation/build suffixes, license hashes match, and the protected remnant
hashes are unchanged.

- [ ] **Step 4: Obtain independent review.**

Review the DAG, ADR relationship, exact tracked trees, ownership boundaries,
negative transfer flags, protected remnants, and absence of production or
external mutation. Fix all Critical and Important findings before commit.

- [ ] **Step 5: Commit only the source receipt.**

```bash
git add docs/superpowers/milestones/M0-governance/stage-11-curated-repository-bootstrap-receipt.yaml
git commit --only -m "docs(governance): record curated repository bootstrap" -- \
  docs/superpowers/milestones/M0-governance/stage-11-curated-repository-bootstrap-receipt.yaml
```

- [ ] **Step 6: Stop.**

Do not begin Stage 4 transfer, Stage 13, remote setup, push, package metadata,
workflows, issue/milestone moves, or optional validation-repository work.

## Outcome Proof

**Intent:** Establish truthful repository homes before further scientific migration without treating empty skeletons as package, runtime, capability, or cutover evidence.
**Current Behavior:** The transition monorepo owns all active packages; Stage 11 combines repository governance with post-Stage-6 runtime transfer; desired local names collide with the active monorepo and two retired Windows-worktree remnants.
**Expected Outcome:** Stage 11 owns only local governance bootstrap, Stage 13 owns proven-owner transfer and installed-artifact cutover, Stage 12 consumes Stage 13, and exactly four clean remote-free local repository homes exist.
**Target Output:** ADR 0006, amended parent spec/plan, one machine-readable bootstrap contract, provider/equilibrium/regression/organization-policy skeleton repositories, four destination receipts, and one source Stage 11 receipt.
**Owner:** M0 owns sequencing, repository homes, organization policy, and receipts; M1 owns later package bootstrap; M3 owns provider runtime; M4 owns equilibrium runtime; M5 owns regression runtime; the user owns remote, publication, and source-of-truth gates.
**Interface:** Local Git repositories under `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project`, YAML bootstrap contracts/receipts, intended GitHub-home mappings, and the revised Stage 11/13 DAG.
**Cutover:** This checkpoint performs no runtime or source-of-truth cutover; Stage 13 later consumes accepted core Stage 4-6 receipts and requires separate user approval for development-source cutover, while Stage 12 alone may authorize retirement/archive mutation.
**Replaced Path:** The former combined Stage 11 is replaced by governance-only Stage 11 plus transfer-and-cutover Stage 13; ADR 0005's final-monorepo target is superseded by ADR 0006 while its historical text is preserved.
**Evidence:** Exact tracked-file lists, clean independent Git histories, empty remotes, matching GPL hashes, empty transfer/capability arrays, protected remnant hashes, plan validators, strict docs, diff checks, cleanup, and independent review.
**Acceptance Proof:** ADR/spec/plan dependency order agrees; all four skeletons have one clean `main` commit and the exact approved trees; no implementation/build artifacts or remotes exist; protected remnants are unchanged; the source receipt records exact commits and negative transfer flags.
**Stop Criteria:** Stop on any destination collision, unexpected existing file, changed remnant hash, copied runtime/build/scientific artifact, nonempty remote, invented package metadata, documentation contradiction, failed validator, or request to cross an unapproved external gate.
**Avoid:** Do not recover stale worktrees, create the optional validation repository, transfer source, add placeholder APIs/builds/tests, create workflows/remotes/releases, move issues or milestones, push, publish, broaden capabilities, or start Stage 4 or Stage 13.
**Risk:** Empty homes may be mistaken for usable packages or become parallel owners; explicit negative receipts, absent build metadata, source-of-truth false flags, and the mandatory stop prevent that ambiguity.

## Implementation Boundaries

**Files To Create:** ADR 0006, the bootstrap contract and source receipt, and the exact governance files listed for the four local skeleton repositories.
**Files To Modify:** ADR 0005 status, ADR index, and the July 12 parent recovery spec/plan including the user's existing multi-repository wording.
**Files To Avoid:** Production package/native/test/build trees, paper and analysis data, optional validation repository, retired worktree contents, remotes, GitHub state, releases, and unrelated staged Chapman content.
**Source Of Truth:** The approved July 13 bootstrap design, the amended parent program, ADR 0006, the machine-readable skeleton contract, and exact Git/bootstrap receipts.
**Read Path:** Read the transition repository's ownership docs and GPL license, the destination contract, Git identities, tracked-file lists, remote lists, and protected remnant pointer hashes.
**Write Path:** Write only governance Markdown/YAML/text files, initialize four independent local Git histories, and record exact commit identities in the source receipt.
**Integration Points:** M0 milestone records, ADR index, parent execution DAG, future provider/equilibrium/regression repositories, future organization `.github` owner, and later Stage 13 transfer proof.
**Migration Or Cutover:** Stage 11 creates empty homes only; later stage-owned transfer leaves accepted provenance; Stage 13 performs core installed-artifact parity and a separately approved development-source cutover after Stages 4-6; Stage 12 alone owns retirement/archive.
**Replaced Path Handling:** Preserve ADR 0005 body and retired worktrees as evidence; replace only the combined Stage 11 program semantics; retain the transition monorepo as the executable source.
**Acceptance Proof Gate:** Do not commit the source Stage 11 receipt unless the exact trees, one-commit histories, empty remotes, negative receipts, license hashes, remnant hashes, docs, plan validators, cleanup, and independent review all pass.
