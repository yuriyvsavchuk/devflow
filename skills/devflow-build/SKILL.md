---
name: devflow-build
description: Implementation playbook for new features, behavior changes, refactors, and performance work — plan → contract → tests → implement → review → acceptance. Selected by devflow-dispatch; use the refactor or performance adapter when dispatch says so.
framework: devflow
---

# Build — Plan → Tests → Implement → Review → Accept

One skeleton for three kinds of change. The **feature** adapter is the default; **refactor** and **performance** adjust the front of the flow. At `quick` tier the steps compress — they do not disappear.

**Rails:** when `.devflow/` exists, record phases as you pass them (`python .devflow/devflow.py mark <phase>`): `plan-confirmed → [contract-confirmed] → red-confirmed → implemented → review-passed → accepted`, then `finish`. At standard+ tier the edit gate denies production-file edits before `red-confirmed`; standard ordering (implement-then-test) requires the explicit exception `mark implemented --no-tdd "<why>"` — recorded, never silent.

## Skeleton

### 1. Plan

Arriving from `devflow-shape`: the spec and plan exist — read both and proceed. Otherwise produce a plan first (`task-planner` agent at standard+; a brief inline plan at quick). The plan states scope, non-goals, files likely to change, ordered steps, and done criteria — referencing the spec's `AC-n` IDs when a spec exists. Read relevant ADRs in `docs/decisions/` before planning; do not propose what an ADR already rejected.

### 2. Interface contract — when the change touches a public API or shared module boundary

`interface-designer` creates or updates the contract in `docs/interfaces/` before implementation begins. The contract is binding: a deviation discovered during implementation updates the contract first, then the code. At `full` tier, also map the blast area (`context-mapper`) before touching shared code.

### 3. Tests

- **TDD-first** (preferred when acceptance criteria are clear): write the AC/contract compliance tests before implementation — RED. When a contract exists: at minimum one test per documented error case.
- **Standard ordering** (implement → test) is acceptable when the work is exploratory or directly follows a completed spike.
- Tests reference the `AC-n` IDs they verify.

### 4. Implement

Minimal diff, one plan step at a time. Preserve all behavior outside the requested change; no opportunistic refactoring. Work on a feature branch (or worktree) at standard+.

### 5. Review

Fresh-context reviewer subagent (standard and full tiers; inline checklist at quick). Findings use **Blocking / Non-blocking / Question** severity. When a contract exists, the reviewer verifies the implementation matches it exactly — an undisclosed deviation is a Blocking finding.

### 6. Acceptance

Map evidence — tests, observed behavior, measurements — to every `AC-n` / done criterion. Missing evidence is a reported gap, never invented. At `full` tier this runs as a fresh-context `acceptance-checker` subagent.

## Loop-backs

- Review returns Blocking findings → fix → re-review.
- Acceptance gap, missing implementation → implement → re-test → re-review → re-check.
- Acceptance gap, missing coverage → tests → re-review → re-check.
- The contract itself is wrong → revise the contract → re-implement the changed sections → re-review. Never implement against a known-wrong contract.

## Adapters

### refactor

- Behavior is preserved, not improved — acceptance confirms preservation only.
- If existing coverage cannot prove preservation, write behavior-preservation tests **before** any change. A test failing before the refactor is a pre-existing defect to report — not to fix silently here.
- Contract drift is a defect even when all tests pass — callers depend on the documented shape.

### performance

- Profile first: measured baseline, concrete hotspot, measurable target. If measurement is impossible, stop and resolve that gap — never optimize on guesswork.
- The benchmark codifies the target as a failing test (RED) **before** optimization — written after the fact it proves nothing.
- One hotspot at a time. Re-run the benchmark after every loop-back. "Feels faster" is not evidence.

## Exit

All criteria met → `finishing-a-development-branch` (merge / PR / cleanup). If public behavior, API, or configuration changed → update docs (`docs-updater`) before closing.

## Boundaries

- Does: plan, contract, tests, minimal implementation, review, acceptance — for feature, refactor, and performance changes.
- Does not: handle live production incidents (`devflow-hotfix`); investigate feasibility (`devflow-spike`); broaden scope beyond the plan.
