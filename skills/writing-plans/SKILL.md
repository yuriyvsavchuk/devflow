---
name: writing-plans
description: Use when you have an agreed spec or design for a software feature and need to create a bite-sized, step-by-step implementation plan before writing any code
framework: devflow
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** Run after devflow:brainstorming or devflow:interview when design is agreed, and after devflow:using-git-worktrees has created the isolated workspace. All file edits and commits produced by this plan execute inside the worktree.

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use devflow:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## Remember
- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Execution Handoff

After saving the plan, immediately proceed with subagent-driven execution. Do not ask — always use this approach:

- **REQUIRED SUB-SKILL:** Use devflow:subagent-driven-development
- Dispatch independent tasks in parallel where possible (use devflow:dispatching-parallel-agents)
- Stay in this session
- Fresh subagent per task + code review between tasks

## When NOT to Use

- The spec or design is not yet agreed — use devflow:interview or devflow:brainstorming first
- Feasibility is unknown — use devflow:spike-executor first; only plan after a Proceed decision
- The task is a single small change — route directly to devflow:task-planner instead

## Common Mistakes

- Writing vague steps like "add validation" instead of exact code and commands
- Missing the test step between implementation and commit
- Omitting exact file paths — implementers should not need to search for them
- Planning too many tasks at once — plans longer than ~8 tasks are usually too large for one session
- Skipping the devflow:scope-estimator when the scope is unclear

## Related Skills and Agents

- **Preceded by:** devflow:brainstorming or devflow:interview
- **Followed by:** devflow:subagent-driven-development or devflow:executing-plans
- Use devflow:scope-estimator before writing plans when scope is uncertain
- Use devflow:dispatching-parallel-agents to parallelize independent tasks within the plan
- Use devflow:spike-executor if any plan step relies on an unvalidated technical assumption
