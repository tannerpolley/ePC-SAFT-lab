# Early Package PR Gate Policy

Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/182
Milestone: `M0 - Governance`
Status: `complete pending merge`
Last synced: `2026-05-29`

## Summary

Formalize the early package-development merge policy. Ordinary PRs use
risk-based local proof first, and GitHub branch protection remains configured
with no required status checks or required reviews. Only lightweight smoke
checks run automatically on `pull_request`; heavy native, package, release, and
installed-provider lanes are manual-only.

Full heavy proof remains required when a PR claims release readiness, capability
support, or production native behavior. This policy reduces routine PR friction
without weakening evidence required for release, PyPI, milestone completion, or
capability claims.

## Acceptance Gates

- [x] CI policy documents local proof first, lightweight smoke PR checks,
      manual-only heavy lanes, and release/capability proof exceptions.
- [x] `.github/workflows/native-build-profiles.yml` and
      `.github/workflows/package-build-lanes.yml` no longer run automatically on
      `pull_request`.
- [x] `.github/workflows/wheels.yml` keeps only lightweight PR smoke behavior on
      `pull_request`, with full wheel/package matrix still manual.
- [x] Branch protection is audited and remains no required checks/reviews unless
      explicitly changed later.
- [x] `.github/PULL_REQUEST_TEMPLATE.md` removes the universal production-proof
      question block.
- [x] Docs explain ordinary PRs do not need boilerplate skipped-heavy-lane
      notes.
- [x] Structural tests enforce workflow trigger policy and PR template shape.

## Non-Goals

- Do not delete heavy package/native/release workflows.
- Do not add fake green fallback behavior for missing Ceres or Ipopt evidence.
- Do not weaken release, PyPI, milestone-completion, or capability-claim proof.
- Do not rename public packages, distributions, or imports.
- Do not split this into child issues.

## Validation

```powershell
gh api repos/ePC-SAFT/ePC-SAFT/branches/main/protection
uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_project_structure.py tests/workflows/build/test_build_dist.py tests/workflows/build/test_build_extension_dists.py -q
uv run python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
