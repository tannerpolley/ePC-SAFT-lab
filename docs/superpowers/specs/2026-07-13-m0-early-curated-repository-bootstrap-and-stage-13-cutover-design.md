# Early Curated Repository Bootstrap And Stage 13 Cutover

Milestone: `M0 - Governance`, with repository-local follow-on ownership in
`M1 - Packages`, `M3 - EOS`, `M4 - Equilibrium`, and `M5 - Regression`
Status: `approved for bounded local bootstrap`
Date: `2026-07-13`
Parent program:
`2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md`

## Authority And Bounded Outcome

The user approved the recommendation to establish the final repository homes
before continuing the blocked scientific migration. The user also directed
that the former Stage 11 runtime-transfer and cutover work become its own
Stage 13, and that execution stop after the new local repository skeletons are
created.

This design authorizes:

1. amending the parent program and its execution DAG;
2. superseding ADR 0005's final-monorepo target while preserving that ADR's
   historical transition decision;
3. creating four local, clean-history, governance-only Git repositories under
   one collision-free parent; and
4. recording exact bootstrap receipts in the source and destination
   repositories.

It does not authorize production-code transfer, remote creation, push,
publication, package release, organization-setting changes, or GitHub issue,
milestone, or Project mutation.

## Context

The current Stage 11 combines two responsibilities with different entry
conditions:

- establishing repository homes, ownership, governance, and tracker routing;
- transferring accepted runtime owners, proving installed-artifact parity,
  and changing the development sources of truth.

The first responsibility can be completed without relaxing any thermodynamic,
numerical, source, or capability gate. The second requires accepted Stage 4,
Stage 5, and Stage 6 receipts and therefore remains blocked.

The intended local repository names also collide with existing paths:

- `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT` is the active transition
  monorepo;
- `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-regression` is a retired
  1.4 GB Windows-worktree remnant whose `.git` file points to a missing
  `C:/Users/...` worktree administration directory; and
- `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-CE` is a separate retired
  1.3 GB Windows-worktree remnant with the same failure class.

Both retired remnants contain unowned build products, environments, paper
sources, analyses, and results. They remain untouched migration evidence and
must not be reinitialized, overwritten, renamed, or cleaned by this stage.

## Approaches Considered

### Selected: governance-only bootstrap followed by Stage 13 cutover

Create clean repository homes with explicit ownership and empty transfer
receipts. Continue scientific stages only after their own child designs. Move
accepted owners and change the sources of truth during Stage 13.

This approach satisfies the user's organization goal while preserving every
scientific and numerical gate.

### Rejected: transfer the current package roots during bootstrap

This would copy a blocked Stage 4 integration state, pre-empt Stage 5 and
Stage 6 canonical-owner work, and make the new repositories appear more mature
than their evidence.

### Rejected: create placeholder buildable packages

Invented package versions, empty public APIs, dummy native targets, or fake
capability reports would be compatibility structure without accepted owners.
The skeletons fail loudly by omitting package and build metadata until a real
vertical slice owns them.

## Revised Execution Order

The dependency graph, not numeric order, controls execution:

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

Stage 11 may create and govern empty local homes before Stage 4. It does not
make any runtime owner accepted. Stages 4-6 retain their existing scientific
entry and exit gates. A stage may later receive a separately approved transfer
leaf that moves its accepted baseline and new work into the appropriate
repository; until then the transition monorepo remains the executable source.

Stage 13 consumes the accepted core Stage 4-6 receipts. It owns remaining
core proven-owner transfer, installed provider compatibility,
cross-repository API and numerical parity, source/native identity, provenance
closure, and a separately user-approved development-source-of-truth cutover.
Stages 7-10 are independent optional branches from Stage 6, not Stage 13
inputs. Any accepted optional branch requires its own bounded transfer leaf;
when deferred, its algorithm family remains closed.

Stage 12 consumes Stage 13 and remains the sole final retirement/archive
decision. Stage 13 does not archive or retire the transition repository.

## Stage 11 Repository-Home Contract

### Entry

- Stages 1-3 have durable accepted records.
- The current Stage 4 blocker remains explicit and unresolved.
- Exact local paths and clean-history policy are recorded by this design.
- Existing stale worktrees are classified and protected.

### Deliverables

- a superseding ADR that establishes the final multi-repository topology;
- collision-free local repository homes;
- one ownership contract and one bootstrap receipt per repository;
- an intended GitHub-home identity and tracker-routing map;
- a clean independent Git history with no remotes; and
- an explicit record that no production owner or scientific capability moved.

### Exit

Every mandatory repository home exists as a clean local Git repository with
the exact governance skeleton, one initial commit, no remote, no production
source, and a receipt linked to the parent program revision. The optional
validation repository remains deferred.

### Stop

Stop immediately after the source receipt records the four local skeleton
commit identities. Do not transfer package code or mutate GitHub state.

## Stage 13 Transfer-And-Cutover Contract

Stage 13 receives the former runtime half of Stage 11. Its entry requires
Stages 4-6 to be accepted. Its deliverables are:

- transfer of the provider core and resolved-input SDK to `ePC-SAFT`;
- transfer of the minimal equilibrium kernel and public-green routes to
  `ePC-SAFT-equilibrium`;
- transfer of proven regression owners to `ePC-SAFT-regression`;
- installed provider wheel/sdist consumption by both extensions;
- minimum/latest compatible provider proof;
- no sibling-source or fixed-relative-path dependency;
- API, schema, source/native identity, and numerical parity;
- package-local tests, docs, capability reports, release ownership, and
  provenance; and
- a separate user-approved development-source-of-truth cutover that preserves
  the transition repository pending Stage 12.

Stage 13 cannot convert a Stage 4 blocker into deferred success. Issue #469
remains M5-owned work and must pass before Stage 13 admits the regression
owner.

## Exact Local Repository Set

The collision-free parent is:

`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project`

It contains:

| Local path | Intended GitHub home | Owner |
| --- | --- | --- |
| `ePC-SAFT` | `ePC-SAFT/ePC-SAFT` | Provider, CppAD, resolved-input SDK |
| `ePC-SAFT-equilibrium` | `ePC-SAFT/ePC-SAFT-equilibrium` | Equilibrium, Ipopt, certification |
| `ePC-SAFT-regression` | `ePC-SAFT/ePC-SAFT-regression` | Regression, Ceres, fit receipts |
| `ePC-SAFT-organization` | `ePC-SAFT/.github` | Organization profile and shared policy |

The optional `ePC-SAFT/ePC-SAFT-validation` repository is not created. Its M6
and cross-package evidence boundary needs a separate ownership decision.

`ePC-SAFT/ePC-SAFT` is the existing `origin` identity of the transition
monorepo, not an unallocated future repository. This bootstrap does not attach
the clean local provider skeleton to that remote. Before Stage 13 changes any
remote or development source of truth, a separate approved strategy must choose
how to retain, rename, or repurpose the existing remote without force-pushing,
replacing its history, or destroying the transition record. The other intended
GitHub homes are mappings only until their own external-creation gates pass.

## Exact Governance Skeletons

The three package repository homes use this tree:

```text
<repository>/
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── CONTEXT.md
├── LICENSE
├── README.md
├── docs/
│   ├── README.md
│   ├── ownership.md
│   └── migration/
│       └── bootstrap-receipt.yaml
├── src/
│   └── README.md
└── tests/
    └── README.md
```

The organization-policy home uses:

```text
ePC-SAFT-organization/
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── CONTEXT.md
├── LICENSE
├── README.md
├── docs/
│   ├── ownership.md
│   └── migration/
│       └── bootstrap-receipt.yaml
└── profile/
    └── README.md
```

No `pyproject.toml`, `CMakeLists.txt`, build backend, import package,
executable test, workflow, release configuration, or capability file is
created. Those files appear only when a child plan transfers an accepted
owner that can make them truthful.

## Repository Content Contract

Each package repository records:

- its exact package and milestone ownership;
- the one-way dependency rule;
- forbidden sibling responsibilities;
- intended distribution and import names;
- the transition monorepo and source commit;
- `production_owners_transferred: []`;
- `scientific_capabilities_claimed: []`;
- `remote_created: false`;
- `push_performed: false`; and
- `source_of_truth: false`.

The source contract also stores literal `content_markers` for every governance
file. Structural validation must load that contract and prove the repository
identity, bootstrap-only state, intended ownership, dependency and forbidden
dependency boundaries, transition-source identity, reserved-directory state,
and all negative capability/transfer/source-of-truth claims appear in the
required files. A matching filename without its required content does not pass.

The `src/README.md` and `tests/README.md` files state that the directories are
reserved and contain no accepted runtime or proof owner. They must not contain
placeholder Python modules or fake tests.

The organization-policy repository records its future ownership of the public
organization profile, shared issue and pull-request templates, reusable
workflow policy, and roadmap conventions. It creates none of those live
GitHub resources during this checkpoint.

## Git, License, And History Policy

- Initialize each repository with `git init --initial-branch=main`.
- Copy the transition repository's GPL-3.0-only license byte-for-byte.
- Create one local bootstrap commit per repository.
- Add no Git remote.
- Preserve LF-normalized text through `.gitattributes`, with `LICENSE -text`
  so the copied GPL bytes remain identical to the transition source.
- Ignore environments, caches, build outputs, distributions, compiled native
  modules, and editor metadata.
- Do not copy source history, `.git` metadata, branches, stashes, artifacts,
  or generated files from the transition or retired repositories.

Stage 13 may approve a bounded history-transfer policy, but clean skeleton
histories remain the default.

The transition worktree's checked-out `LICENSE` bytes are the bootstrap copy
source. Its pre-existing `HEAD:LICENSE` blob is LF-normalized and has a
different hash; this stage does not rewrite transition history. The bootstrap
contract records both source hashes and requires each destination worktree and
committed `HEAD:LICENSE` blob to match the checked-out source bytes.

## Tracker And Milestone Routing

Stage 11 defines, but does not execute, the routing:

- M3/provider issues -> `ePC-SAFT/ePC-SAFT`;
- M4/equilibrium issues -> `ePC-SAFT/ePC-SAFT-equilibrium`;
- M5/regression issues, including #469 ->
  `ePC-SAFT/ePC-SAFT-regression`;
- package-specific M6 evidence -> its package repository;
- approved cross-package M6 evidence -> a later validation owner; and
- M0 organization policy -> `ePC-SAFT/.github` when that remote is approved.

Issue transfer, recreation, dependency repair, milestone recreation, Project
field reconciliation, and redirects require a later dry-run manifest and
separate external-write approval.

## Validation

The bootstrap checkpoint proves:

1. the exact four directories exist under the approved parent;
2. each directory is an independent clean Git repository on `main`;
3. each has exactly the approved tracked tree and one bootstrap commit;
4. none has a remote;
5. no Python, C++, shared library, wheel, archive, or scientific output was
   copied;
6. all license hashes equal the transition license;
7. every receipt names the source program revision and denies runtime transfer,
   capability, push, and source-of-truth status;
8. the retired Windows worktree paths and hashes of their `.git` pointer files
   are unchanged; and
9. parent-program docs, plan validators, strict docs, diff checks, and cleanup
   pass.

## Non-Goals

- No Stage 4 repair or reinterpretation.
- No M5 issue #469 implementation.
- No Stage 5 kernel extraction or Stage 6 route consolidation.
- No Stage 7-10 algorithm work.
- No package source or build transfer.
- No remote, push, publication, release, organization, issue, milestone, or
  Project mutation.
- No cleanup or recovery of retired worktrees.
- No optional validation repository.
- No capability or API claim.

## Acceptance Criteria

The design is accepted when the parent program names Stage 11 and Stage 13
separately, the superseding ADR and execution DAG agree, the four exact local
skeletons and receipts pass structural validation, the transition repository
records their commit identities, all unrelated user changes remain preserved,
and execution stops before any transfer or external mutation.
