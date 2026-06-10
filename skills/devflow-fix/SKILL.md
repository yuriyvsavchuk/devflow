---
name: devflow-fix
description: Bug-fix playbook — reproduce, write a failing regression test, apply the minimal fix, review, confirm the regression is closed. Selected by devflow-dispatch for defects, stack traces, and wrong behavior.
framework: devflow
---

# Fix — Reproduce → RED → Minimal Fix → Review → Accept

The discipline of this playbook is the same at every tier: **no fix before the failure is reproduced, and no fix before a failing test encodes the expected behavior.** Tiers change who does each step, not their order.

**Rails:** when `.devflow/` exists, record each phase as you pass it (`python .devflow/devflow.py mark <phase>`) — at standard+ tier the edit gate mechanically denies production-file edits until `red-confirmed` is marked. Phases: `repro-confirmed → red-confirmed → fix-applied → review-passed → accepted`, then `finish`.

## Steps

### 1. Reproduce and triage

Confirm the failure with evidence — a failing command, the stack trace, observed-vs-expected behavior. At standard+, the `bug-repro-triager` agent produces repro steps, a root-cause hypothesis, and an investigation plan. Skip triage only when a minimal reproduction and root cause are already confirmed with evidence. Three or more independent failures across different subsystems → dispatch one triage per failure domain in parallel.

### 2. Failing regression test (RED)

Write the test that fails for the reported reason and will pass once behavior is correct.

- When a contract exists in `docs/interfaces/`, the test asserts the **contracted** behavior — not the previously observed broken behavior.
- If triage reveals the contract itself is wrong (wrong error shape, wrong field type), correct the contract first, then write the test against the corrected contract.
- Rails: `mark red-confirmed --evidence <test-path>` — this is what unlocks production edits.

### 3. Minimal fix (GREEN)

The smallest change that makes the regression test pass. No unrelated cleanup, no refactoring — if the surrounding code needs it, note it for a separate `devflow-build` (refactor) run.

### 4. Review

Fresh-context reviewer subagent at standard+ (inline checklist at quick). Findings use **Blocking / Non-blocking / Question** severity. Blocking → fix → re-review.

### 5. Acceptance

Regression test green, full suite green, evidence mapped to the bug's done criteria. A gap loops back to the owning step, then re-review.

## Exit

Regression closed → `finishing-a-development-branch`. If the investigation exposed missing coverage elsewhere, note it for a separate test-only pass — not scope creep here.

## Boundaries

- Does: reproduce, regression-test, minimally fix, review, confirm closure.
- Does not: mitigate live incidents (that is `devflow-hotfix` — mitigation first, root cause later); refactor; fix anything without a confirmed reproduction.
