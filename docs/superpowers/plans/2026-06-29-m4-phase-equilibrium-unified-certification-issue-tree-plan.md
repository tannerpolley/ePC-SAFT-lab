# M4 Phase Equilibrium Unified Certification Issue Tree Plan

## Source

Spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`

## Outcome Proof

The M4 tracker has a native GitHub sub-issue hierarchy for unified
phase-equilibrium certification, and the first executable leaf can be resolved
without more scope design.

## Approved Decisions

- Use native GitHub sub-issues.
- Create one Phase Equilibrium parent above #191.
- Keep a direct core unified-contract leaf under the Phase Equilibrium parent.
- Use broad family parents and a detailed LLE subtree in this pass.
- Do not impose an artificial issue-depth maximum.
- Move #191 as a subtree under the new Electrolyte LLE parent.
- Enforce the first contract gate on production-exposed routes.
- Use `gh` first; patch Superpowers Project tooling only if native sub-issue
  operations are blocked.

## Planned Issue Tree

1. #361 Phase Equilibrium parent.
2. #362 Direct core-contract implementation leaf.
3. #363 LLE broad parent.
4. #364 Neutral nonassociating LLE detailed parent.
5. #365 Neutral Stage II replay-to-Stage III receipt repair leaf.
6. #366 Neutral source-backed tolerance integration leaf.
7. #367 Associating LLE detailed parent.
8. #368 Associating proof-route applicability metadata leaf.
9. #369 Gross 2002 associating tolerance integration leaf.
10. #370 Electrolyte LLE detailed parent.
11. #371 Electrolyte reduced-electroneutral residual integration leaf.
12. #372 Reactive electrolyte LLE detailed parent.
13. #373 VLE broad parent.
14. #374 Flash and multiphase broad parent.
15. #375 Boundary-route broad parent.
16. #376 Reactive/coupled phase-equilibrium broad parent.

#191 is reparented under #370. Its existing closed children remain nested under
#191 unless GitHub requires a direct move. #331 is reparented under #376 so the
current CPE contract work is visible in the reactive/coupled PE subtree.

## Shared Acceptance Rules

- Parent issues are tracking issues and close only when their child evidence is
  complete.
- Leaf issues must be PR-sized and must include an executable proof oracle.
- AFK leaves need enough source, candidate files, acceptance criteria, and proof
  commands for `superpowers-project:resolve-issue`.
- HITL parents may remain blocked while child implementation slices execute.
- Capability and registry text may only broaden after the matching route-family
  contract passes.

## Proof Oracle

```powershell
gh api /repos/ePC-SAFT/ePC-SAFT/issues/361/sub_issues
gh api /repos/ePC-SAFT/ePC-SAFT/issues/370/sub_issues
gh issue view 191 --json parent
gh issue view 331 --json parent
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Mirror validation:

```powershell
uv run --no-sync python scripts/validate_issue_mirror.py --repo-root . --issue-file <mirror> --milestone-required
```

## Non-Goals

- No solver implementation in this tracker/spec PR.
- No #191 closure.
- No M5 parameter-regression work.
- No release or downstream capability claim.
