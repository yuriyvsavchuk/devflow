---
name: executing-plans
description: Use when you have a written software implementation plan and need to execute it in batches with human review checkpoints between task groups
framework: devflow
---

# Executing Plans

## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Batch
**Default: First 3 tasks**

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Report
When batch complete:
- Show what was implemented
- Show verification output
- Say: "Ready for feedback."

### Step 4: Continue
Based on feedback:
- Apply changes if needed
- Execute next batch
- Repeat until complete

### Step 5: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use devflow:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker mid-batch (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Between batches: just report and wait
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## When NOT to Use

- No written plan exists — use devflow:writing-plans first
- Tasks are independent and can be parallelized — use devflow:subagent-driven-development instead for fresh-subagent-per-task isolation
- A spike is needed to validate an assumption before executing — resolve it with devflow:spike-executor first

## Common Mistakes

- Skipping the critical review of the plan at the start — executing a flawed plan wastes more time than the review takes
- Guessing when blocked instead of stopping — creates compounding errors that are hard to unwind
- Continuing past a failing verification — a red result means the plan's assumption was wrong, not that the verification was wrong

## Integration

**Required workflow skills:**
- devflow:using-git-worktrees — REQUIRED: Must be run first to create the isolated workspace and feature branch
- devflow:writing-plans — Creates the plan this skill executes
- devflow:finishing-a-development-branch — Complete development after all tasks

## Related Skills and Agents

- **Preceded by:** devflow:writing-plans
- **Followed by:** devflow:finishing-a-development-branch
- Use devflow:subagent-driven-development instead when task isolation matters (fresh context per task, two-stage review)
- Use devflow:requesting-code-review after each batch for additional quality assurance
- Use devflow:verification-before-completion before claiming any task done
