# Khudaida Paper Validation With Figiel Parameters Plan

**Goal:** Route the Khudaida 2026 figure-reproduction campaign as M6 paper
validation while preserving M4 for equilibrium implementation defects and M5
for parameter regression defects.

**Owning milestone:** M6 - Validation
**Owning package:** `benchmark`
**Tracking issues:** #420 and #421
**Ready leaf:** #407

## Outcome Proof

**Intent:** Reorganize the Khudaida figure issues so each figure is a retained
paper-validation proof rather than an equilibrium implementation bucket.
**Current Behavior:** #407-#417 were created under M4, and their local mirrors
and bodies describe figure reproduction as M4 equilibrium validation even when
the work is artifact and tolerance evidence.
**Expected Outcome:** #406-#417 are sub-issues of #421 under M6, #421 is a
sub-issue of #420, and active mirrors/bodies say to open M4 or M5 blockers
only when validation proves a solver or parameter defect.
**Target Output:** Native GitHub parent/sub-issue hierarchy, M6 milestones,
updated issue bodies, local issue mirrors, and this M6 source plan/spec.
**Owner:** M6 validation owner for paper evidence, with M4/M5 owners receiving
follow-up blockers only when the validation evidence demands them.
**Interface:** GitHub issue hierarchy fields, local issue mirrors under
`docs/superpowers/issues`, Khudaida retained artifacts, validation checkers,
and package-level public-route proof commands.
**Cutover:** Replace the active Khudaida issue route from closed #405 and the
M4 figure plan to #420/#421 and this M6 plan.
**Replaced Path:** Treating each Khudaida figure as direct M4 equilibrium work
even when the issue is literature artifact validation or metric reproduction.
**Evidence:** GitHub parent/sub-issue JSON, milestone fields, issue labels,
local mirror validation, plan validators, and docs validation.
**Acceptance Proof:** #420 owns #421, #421 owns #406-#417, #407 is the next
ready leaf, local mirrors validate, and no active Khudaida figure mirror claims
M4 ownership for validation-only work.
**Stop Criteria:** Stop if GitHub hierarchy fields cannot be set, if issue
bodies cannot be updated, or if local mirror validation fails after the
cutover.
**Avoid:** Do not reopen completed figure issues, erase the closed #405 history,
hide parameter fitting in M6, or remove M4/M5 blockers when evidence requires
them.
**Risk:** Moving validation issues to M6 could obscure real equilibrium defects
unless every figure retains the rule to open or block on M4/M5 issues.

## Implementation Boundaries

**Files To Create:** M6 Khudaida source spec, M6 Khudaida source plan, and
local issue mirrors for #420 and #421.
**Files To Modify:** Local mirrors for #406-#417, and superseding notes in the
old M4 Khudaida source spec/plan.
**Files To Avoid:** Solver code, parameter data, figure scripts, retained plot
artifacts, package tests, and unrelated milestone registries.
**Source Of Truth:** the historical GitHub Issues #420/#421/#406-#417 and the
retained Khudaida/Figiel validation folders.
**Read Path:** Inspect GitHub issue milestone, label, parent, and sub-issue
fields before editing local mirrors.
**Write Path:** Update GitHub issue hierarchy with first-class `gh issue`
flags, then update local docs to mirror the live tracker state.
**Integration Points:** `gh issue create --parent`, `gh issue edit --parent`,
`gh issue view --json parent,subIssues`, local mirror validators, and docs
validation.
**Migration Or Cutover:** Keep #405 closed as historical M4 context; move the
active figure execution path to #421 and this M6 plan.
**Replaced Path Handling:** Add explicit superseded notes to the old M4
Khudaida plan/spec and point active mirrors at the M6 plan/spec.
**Acceptance Proof Gate:** Final handoff must report the GitHub hierarchy,
changed mirrors, validation commands, and clean git state.

## Tasks

### Task 1: Establish GitHub Hierarchy

**Use Cases:**
- Acceptance evidence shows #420 owns #421 and #421 owns #406-#417 through
  first-class sub-issue fields.
- Cutover evidence shows #407 is ready under M6 after #406 closed.

**Files:**
- GitHub Issues #420, #421, #406-#417.

**Steps:**
- Create #420 and #421 if absent.
- Move #406-#417 to M6 and parent them under #421.
- Confirm hierarchy with `gh issue view --json parent,subIssues`.

### Task 2: Sync Local Mirrors And Plans

**Use Cases:**
- Acceptance evidence shows the active Khudaida mirrors point to the M6
  validation plan and no longer claim M4 ownership for validation-only work.
- Replaced-path evidence shows the old M4 plan is explicitly superseded for the
  active figure campaign.

**Files:**
- `docs/superpowers/issues/*khudaida*0406*.md`
- `docs/superpowers/issues/*khudaida*0417*.md`
- `docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md`
- `docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md`

**Steps:**
- Add #420/#421 local mirrors.
- Move active figure mirrors to M6 filenames and metadata.
- Update non-goals so M4/M5 blockers remain explicit.

### Task 3: Validate The Tracker Cutover

**Use Cases:**
- Acceptance evidence comes from mirror validators, plan validators, docs
  validation, and a clean git status.
- Cutover evidence shows the next ready issue remains #407 under the M6
  hierarchy.

**Files:**
- `scripts/validate_issue_mirror.py`
- `scripts/validate_plan_task_use_cases.py`
- `scripts/validate_plan_outcome_proof.py`
- `scripts/dev/validate_project.py`

**Steps:**
- Run plan validators for this M6 plan.
- Run issue mirror validators for #420/#421 and #406-#417.
- Run docs validation and cleanup.

## Proof Oracle

```bash
gh issue view 420 --json number,title,milestone,subIssues
gh issue view 421 --json number,title,milestone,parent,subIssues
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <mirror>
uv run --no-sync python scripts/dev/validate_project.py docs
```
