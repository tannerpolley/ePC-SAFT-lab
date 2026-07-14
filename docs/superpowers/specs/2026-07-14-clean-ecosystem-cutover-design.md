# Clean ePC-SAFT Ecosystem Cutover Design

Status: approved canonical cutover design

Approved: 2026-07-14

Permanent doctrine: `ePC-SAFT/.github/GOVERNANCE.md`, revision 1

## Context

The transition monorepo is clean and synchronized at `64fdf314`, and four
governance-only local skeletons exist under `ePC-SAFT-project`. No remotes or
runtime owners have moved. The accepted July 13 bootstrap accurately records
that historical four-skeleton checkpoint, but its four-home target, deferred
validation repository, and eventual retirement of the transition repository
no longer describe the approved destination.

The permanent target is the six-home ecosystem in the organization doctrine.
The current repository will become `tannerpolley/ePC-SAFT-lab`, remain active
for experiments and provenance, and remain authoritative for each runtime
slice until a validated promotion receipt transfers that slice.

## Goals

- Publish clean repository homes without importing monorepo history or gunk.
- Preserve all current GitHub history and scientific provenance in the lab.
- Route active work to its production owner without breaking issue metadata.
- Transfer runtime authority one complete, independently proven slice at a
  time, beginning with the smallest complete provider thermodynamic path.
- Keep the cutover checkpointed and stop-safe at every explicit external-write
  or authority gate.

## Non-goals

- No remote, issue, Project, release, or organization mutation is authorized by
  this design alone.
- No runtime source moves when this design is accepted.
- No full-history import, force push, history replacement, or bulk file copy.
- No release workflow, version promise, public C++ ABI promise, or capability
  expansion.
- No cleanup of preserved branches or stashes without separate approval.

## Alternatives considered

### Replace the existing provider remote history

Rejected. It destroys provenance, risks live collaboration state, and makes
the new provider inherit the very structure the cutover is intended to remove.

### Transfer the current repository to the personal account first

Rejected. GitHub transfers issues only between repositories owned by the same
account. Moving the lab first would block direct transfer of active issues into
the organization repositories.

### Keep validation inside package repositories

Rejected. Cross-package and literature acceptance needs an installed-artifact
owner that cannot be mistaken for production implementation.

### Selected: rename, establish clean homes, reconcile, then transfer the lab

The current remote is first renamed inside the organization. Clean production
homes are then created. Active issues are reconciled while source and
destination remain organization-owned. Only after tracker and URL verification
does the lab move to the personal account. Runtime authority moves later by
slice receipt.

## Selected structure

| Local home | Intended remote | Role |
|---|---|---|
| `ePC-SAFT-project/ePC-SAFT` | `ePC-SAFT/ePC-SAFT` | Provider |
| `ePC-SAFT-project/ePC-SAFT-equilibrium` | `ePC-SAFT/ePC-SAFT-equilibrium` | Equilibrium |
| `ePC-SAFT-project/ePC-SAFT-regression` | `ePC-SAFT/ePC-SAFT-regression` | Regression |
| `ePC-SAFT-project/ePC-SAFT-validation` | `ePC-SAFT/ePC-SAFT-validation` | Validation |
| `ePC-SAFT-project/ePC-SAFT-organization` | `ePC-SAFT/.github` | Organization policy |
| current transition checkout | `tannerpolley/ePC-SAFT-lab` | Lab and remaining source authority |

The validation skeleton is created only in its approved bootstrap checkpoint.
Existing placeholder `src/` and `tests/` marker files in the first three
skeletons are removed before publication; real package structure materializes
with the first accepted owner.

## Cutover sequence

Each phase ends with a receipt and an explicit continuation gate.

### 0. Freeze and export

1. Verify the lab commit, worktree, branches, stashes, remotes, and remote hash.
2. Export repository settings, rules, issue types, labels, milestones, issues,
   pull requests, releases, discussions, Projects, dependencies, and URLs.
3. Classify every tracked `ePC-SAFT/ePC-SAFT` URL as historical-lab,
   transferred-work, or future-provider.
4. Record repository-name availability and required GitHub token scopes.

### 1. Prepare local homes

1. Create the governance-only validation skeleton with the same negative
   capability contract as the other homes.
2. Install doctrine-revision pointers in every local home.
3. Remove speculative directory markers and confirm no package, target, test,
   workflow, release, or capability exists.
4. Define the transfer-receipt schema and executable validator before any
   runtime transfer.

### 2. Rename and create remotes

Under a separately approved external-write plan:

1. Rename `ePC-SAFT/ePC-SAFT` to `ePC-SAFT/ePC-SAFT-lab`.
2. Create public organization repositories for equilibrium, regression,
   validation, and `.github`.
3. Create the clean provider at `ePC-SAFT/ePC-SAFT`.
4. Attach each local skeleton to exactly its intended remote and push its clean
   history.
5. Apply descriptions, topics, and protected-main rules. Reject force pushes
   and deletion; record any approved bootstrap bypass.
6. Verify every local and remote commit and confirm that no runtime owner or
   capability moved.

The `.github` repository must be public for organization defaults. Shared
reusable workflows do not execute automatically; package repositories retain
small caller workflows when real checks exist.

### 3. Reconcile trackers while the lab remains in the organization

1. Seed matching labels, milestones, issue types, and package tracker policy.
2. Select only active, reconciled issues. Closed history remains with the lab.
3. Transfer each selected issue to its owning package repository while both
   repositories are owned by `ePC-SAFT`.
4. Rebuild blocker, sub-issue, milestone, assignee, and organization Project
   relationships; validate counts and URLs.
5. Record a machine-readable old-to-new issue and URL map.
6. Update tracked historical links to the lab and active links to their new
   package homes. Do not rely on repository redirects after the old provider
   name is reused.

### 4. Transfer the lab

Only after Phase 3 passes:

1. Transfer `ePC-SAFT/ePC-SAFT-lab` to
   `tannerpolley/ePC-SAFT-lab` without renaming or replacing history.
2. Update the local lab `origin` to the final URL.
3. Verify issues, pull requests, releases, discussions, branches, stashes,
   links, settings, and remote hashes against the export.
4. Publish a compact crosswalk from the new provider to the historical lab.

The lab remains active, public, and non-archived. It remains source authority
for every unpromoted runtime slice.

### 5. Promote runtime slices

For each bounded slice:

1. Identify the exact result and scientific contract to preserve.
2. Distill the smallest source-faithful implementation into its production
   owner without copying monorepo structure.
3. Build the destination independently against installed dependencies.
4. Run package-owned equation, derivative, native, and contract proofs.
5. Build immutable artifacts and run validation-owned black-box evidence.
6. Run the transfer-receipt validator, displaced-owner checks, and
   architecture-ratchet review.
7. Ask the user to approve the effective authority change.
8. Mark the corresponding lab implementation non-authoritative; do not delete
   provenance.

The first slice is the provider's smallest complete thermodynamic path. The
provider SDK transport decision must be accepted before a native consumer
slice moves.

## Interfaces and records

The cutover owns four machine-readable record types:

- bootstrap receipt: proves a repository home exists without runtime claims;
- URL and tracker crosswalk: preserves historical and active identifiers;
- promotion receipt: proves one slice and changes its production authority;
- architecture baseline: records the accepted maintenance surface after a
  repository's first complete slice.

Records contain immutable commit and artifact hashes. Human status text is not
acceptance unless the corresponding validator passes.

## Data flow

```text
lab candidate
  -> distilled package slice
  -> package white-box proofs
  -> immutable installed artifacts
  -> validation black-box proofs
  -> validated promotion receipt
  -> explicit authority approval
```

No arrow points from a production repository back to the lab as a runtime
dependency. A failed proof stops the flow before authority changes.

## Errors and failure handling

- A failed preflight stops before an external write.
- A remote mismatch stops before issue or lab transfer.
- A tracker mismatch leaves the lab inside the organization until repaired.
- A package or validation failure leaves runtime authority with the lab.
- A derivative, root-identity, topology, or certification gap closes the
  capability; it is not converted into a fallback.
- No phase deletes history, branches, stashes, papers, or failed evidence.

## Testing

Each phase verifies local cleanliness, exact commits, remote identity, absent
forbidden owners, and its phase-specific manifest. Scientific promotion also
verifies source equations and units, derivative order, root or topology
conditions, solver diagnostics, source-backed data, and installed-artifact
behavior.

The canonical doctrine and this design require decision-ledger validation
before they are treated as complete records.

## Risks

- Reusing `ePC-SAFT/ePC-SAFT` invalidates historical redirects; mitigate with a
  classified URL crosswalk and explicit historical-lab links.
- Issue metadata can be lost or split; mitigate by exporting first and moving
  active issues before the lab leaves the organization.
- Clean repositories can regrow monorepo structure; mitigate with unique
  ownership, installed-artifact boundaries, and the architecture ratchet.
- LOC pressure can incentivize unreadable code; mitigate by tracking multiple
  surface metrics and rejecting code-golf reductions.
- Exact-Hessian claims can omit implicit or higher-order terms; mitigate with
  derivative-order receipts and formulation-specific white-box proof.

## Unresolved decisions

These do not block doctrine acceptance, but they block their named phase:

- provider SDK native transport mechanism: blocks native extension transfer;
- exact active-issue set and mapping: blocks lab transfer;
- organization Project token scope and automation: blocks Project mutation;
- first release versions and release machinery: blocks publication only.

## Decision ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
|---|---|---|---|---|---|
| C-001 History strategy | User clean-repository objective | Keep clean histories and preserve old history in the lab | Avoids importing monorepo structure while retaining provenance | No | Migration owner |
| C-002 Rename order | GitHub transfer audit | Rename inside the organization before creating the new provider | Avoids destructive history replacement and namespace-retirement risk | No | Remote cutover owner |
| C-003 Issue-transfer order | GitHub issue-transfer constraint | Transfer active issues before the lab leaves the organization | Preserves direct issue-transfer capability | No | Tracker cutover owner |
| C-004 URL crosswalk | URL inventory and GitHub redirect rules | Add a classified URL crosswalk before relying on the reused provider name | Prevents historical links from silently targeting the new provider | No | Tracker cutover owner |
| C-005 Tracker scope | User issue-scope decision | Keep closed tracker history in the lab and move only active reconciled work | Avoids copying stale work into clean repositories | No | Tracker cutover owner |
| C-006 Lab lifecycle | User lab-role decision | Keep the lab active; mark only promoted slices non-authoritative | Preserves experimentation without duplicate runtime authority | No | Lab and migration owners |
| C-007 Slice order | User slice-order decision | Promote one complete slice at a time, provider first | Establishes the provider contract before consumers | No | Migration owner |
| C-008 Receipt gate | Receipt integrity audit | Require executable receipts before authority changes | Prevents self-attested cutover claims | No | Migration owner |
| C-009 Deferred bounded decisions | Sanity-check unresolved decisions | Decide SDK transport, Project mutation, and releases in bounded follow-ups | Blocks only the affected later phase | Yes | Provider, tracker, and release owners |
