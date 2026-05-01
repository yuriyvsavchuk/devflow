---
name: using-devflow
description: Use at the start of any software development task — routes all work through the correct worker agent pipeline before any coding, planning, reviewing, debugging, or documentation begins
framework: devflow
---

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill or worker agent might apply to what you are doing, you ABSOLUTELY MUST use it.

IF A SKILL OR WORKER AGENT APPLIES TO THE TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Purpose

This skill enforces disciplined execution by requiring:

1. **Skill-first thinking**
2. **Worker-agent routing before any task work**
3. **Visible worker self-identification**
4. **Structured outputs per worker**
5. **No silent fallback to generic behavior**

This skill is a **router + gatekeeper**. It must be applied before planning, coding, testing, reviewing, or clarifying questions whenever a relevant worker agent might help.

---

## Core Rule

**Before any response or action, you must:**

1. Determine whether any skill applies (even 1% chance = yes)
2. Determine whether any worker agent applies
3. Select and announce the worker agent(s)
4. Execute only the current worker
5. Require worker self-identification and structured output

If no worker agent applies, explicitly say so and proceed normally.

---

## Mandatory Worker Routing (No Exceptions)

### Required routing step (before any task work)

Before doing any planning, coding, testing, reviewing, refactoring, or analysis, you must output:

- `Selected worker agents: <ordered list>`
- `Reason: <why these agents>`
- `Current agent: <first agent to execute>`

### No work before routing

Do **not**:
- write code
- propose implementation steps
- review code
- write tests
- summarize fixes
- ask clarifying questions about execution details

until worker routing has been announced.

---

## Worker Self-Identification (Required)

Every response produced under a worker agent must begin with:

- `Active agent: <agent name>`
- `Purpose: <one sentence>`
- `Scope: <what is in scope / out of scope>`

This is required so compliance is visible and auditable.

---

## Worker Compliance Footer (Required)

Every worker response must end with:

- `Worker compliance: followed <agent-name> format`

If a worker cannot follow its format due to missing context, it must say so explicitly and stop.

If more workers remain in the pipeline, re-announce before beginning the next one:

- `Current agent: <next agent>`

---

## If No Worker Applies

If no worker agent clearly applies, you must explicitly output:

- `Selected worker agents: none`
- `Reason: no matching worker agent`
- `Current agent: none`

Then proceed with a normal response.

Do not silently skip routing.

---

## Worker Selection Heuristics (Default Pipelines)

Use these default pipelines unless there is a strong reason to change them. Pipelines follow the natural lifecycle of a task: specify → validate → learn → build → fix → clean → cover → gate → document → optimize → audit.

---

### 0) Requirements gathering

**Use when:**
- a task or feature request is vague, unclear, or underspecified
- requirements, constraints, or acceptance criteria are not yet written down
- the scope of the work is undefined or cannot be determined yet
- a stakeholder or user has an idea that needs to be made concrete before any design or planning begins
- you cannot yet determine which implementation pipeline applies

**Default pipeline:** `interview → brainstorming → scope-estimator → writing-plans`

**Variants:**
- Skip devflow:interview if requirements are already partially specified — start with devflow:brainstorming directly
- Skip devflow:brainstorming if the design approach is already agreed — go straight to devflow:scope-estimator or devflow:writing-plans
- Skip devflow:scope-estimator if the scope is small and well-understood
- Insert devflow:spike-executor between devflow:brainstorming and devflow:scope-estimator when the feasibility of the proposed design is unknown
- Insert devflow:adr-writer after devflow:brainstorming when the design session produces a significant architectural decision — a choice affecting multiple components, hard to reverse, or made between named alternatives; the ADR is written before devflow:scope-estimator or devflow:writing-plans begins
- Insert devflow:adr-writer after devflow:technology-selector (when used as a Variant) — the technology-selector recommendation is the decision that the ADR records

**Notes:**
- devflow:interview produces a written spec; devflow:brainstorming turns the spec into a concrete design
- Do not start devflow:writing-plans until the design is agreed and the spec document is saved
- devflow:scope-estimator gates the proceed decision: if the estimate is XL or confidence is Low, split or simplify before opening a plan
- No code is written in this pipeline — the output is a spec and a plan, not an implementation
- Use devflow:session-continuity at session boundaries to preserve requirements and design state across sessions

**Transition:**
- devflow:scope-estimator recommends **Proceed** → devflow:writing-plans, then route to the appropriate implementation pipeline (2, 3, 4, etc.)
- devflow:scope-estimator recommends **Investigate first** → open Pipeline 1 (Spike/POC) to validate the key unknown
- devflow:scope-estimator recommends **Split** → break into multiple plans, each routed independently through the appropriate pipeline

---

### 1) Spike / POC investigation

**Use when:**
- a technical idea needs feasibility validation before committing to a plan
- a key assumption in a planned implementation is unvalidated
- evaluating competing approaches or libraries before choosing one
- the cost of building something wrong is high and the answer is unknown

**Default pipeline:** `research → spike-investigator → poc-retrospective`

**Variants:**
- Replace devflow:spike-investigator with devflow:hypothesis-validator when the question is narrow and one specific assumption needs a designed experiment rather than open exploration
- Insert devflow:technology-selector after devflow:research when the investigation includes a technology choice between named options
- Insert devflow:scope-estimator before devflow:poc-retrospective when a Proceed decision needs a sizing estimate before opening a plan
- Skip devflow:research if the domain is already well-understood
- Prepend devflow:using-git-worktrees before devflow:spike-investigator when the spike will produce code artifacts — keeps throwaway code on an isolated branch that can be cleanly archived or deleted after the retrospective
- Append devflow:adr-writer after devflow:poc-retrospective when the Proceed decision constitutes an architectural commitment — the retrospective records what the experiment revealed; the ADR records the architectural decision that follows from it

**Notes:**
- devflow:spike-investigator works in throwaway mode: no TDD, no production standards apply
- devflow:poc-retrospective is **mandatory** — do not close a spike without capturing the decision
- Use devflow:spike-executor to orchestrate the full lifecycle
- Use devflow:session-continuity at session boundaries to preserve state across sessions
- When the spike produces a **Proceed** decision, start the production implementation in a **new session** — read the retrospective document to orient, do not carry spike-mode context forward

**Transition:**
- **Proceed** → devflow:writing-plans for the production implementation (new session, starting from the retrospective and any ADR written in this session)
- **Pivot** → open a new spike with the refined hypothesis
- **Abandon** → devflow:poc-retrospective closes the record; no further work

---

### 2) Unfamiliar API / library / framework

**Use when:**
- integrating a library, framework, or external API not previously used in this project
- the implementation approach depends on understanding undocumented or complex behavior
- version differences or breaking changes may affect the approach

**Default pipeline:** `api-researcher`

**Variants:**
- Prepend devflow:technology-selector when the library or framework has not yet been chosen and two or more options are under consideration
- Append devflow:adr-writer after devflow:api-researcher when adopting this library or API is a significant architectural commitment — documents the adoption decision before Pipeline 3 begins
- Skip this pipeline entirely and go straight to Pipeline 3 if the API is already well-understood and documented internally

**Notes:**
- This pipeline is a research gate only — it produces findings, not implementation
- devflow:api-researcher must produce actionable findings before transitioning — do not proceed while critical behavior is still unknown
- Use devflow:session-continuity at session boundaries to preserve research state across sessions

**Transition:**
- **Findings are clear and approach is viable** → route to Pipeline 3 (New feature / behavior change), carrying api-researcher findings into devflow:task-planner
- **Findings reveal an unknown that requires hands-on validation** (e.g. undocumented behavior, version incompatibility that needs a proof-of-concept) → route to Pipeline 1 (Spike/POC) to resolve the unknown before planning begins
- **Findings reveal the integration is fundamentally incompatible or the requirement cannot be met with this approach** → route to Pipeline 0 (Requirements gathering) to rethink the design before committing to an alternative

---

### 3) New feature / behavior change

**Use when:**
- adding new user-visible behavior or a new system capability
- changing existing behavior in a backward-incompatible way
- extending or modifying a public API, configuration, or interface

**Default pipeline:** `task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker`

**Variants:**
- Prepend devflow:scope-estimator when scope is unclear or the feature touches many areas of the codebase
- Prepend devflow:using-git-worktrees before devflow:feature-implementer when the project uses git — creates an isolated worktree and feature branch before any code changes begin
- Insert devflow:interface-designer after devflow:task-planner when the change introduces or modifies a public API endpoint, shared module exports, or service boundary — produces a binding interface contract (OpenAPI 3.x spec, TypeScript interfaces, or AsyncAPI schema) before devflow:feature-implementer begins; any deviation from the contract during implementation requires updating the contract first
- Move devflow:test-engineer before devflow:feature-implementer when devflow:interface-designer has run and the project follows TDD — the contract provides complete behavioral specifications (all endpoints, parameters, and error cases) enabling test-first; test-engineer writes contract compliance tests (RED phase) before any production code is written; feature-implementer then implements to GREEN; this repositions the standard post-implementation devflow:test-engineer step — no separate post-implementation pass is needed when the contract tests are comprehensive
- Insert devflow:context-mapper after devflow:task-planner (or after devflow:interface-designer when both are active) when the codebase is large or the change touches a shared module — traces reverse dependencies and test coverage from the plan's target files; downstream workers read the context map instead of scanning the codebase themselves
- Append devflow:dependency-auditor after devflow:test-engineer when the implementation adds or modifies package manifests (package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, etc.) — run before devflow:code-reviewer so audit findings are available as review context; if dependency-auditor reports Critical or High findings, escalate to Pipeline 10 before merging
- Append devflow:docs-updater when public behavior, API, configuration, or migration notes change

**Notes:**
- devflow:task-planner defines done criteria before devflow:feature-implementer starts
- devflow:test-engineer writes tests before the branch is merged, not after
- devflow:acceptance-checker maps evidence to stated criteria — it does not invent missing evidence
- Use devflow:session-continuity at session boundaries to preserve implementation state across sessions
- When devflow:context-mapper has run, all downstream workers must read the context map from `docs/context-maps/` before loading any project files — the map is the scoping contract for the pipeline
- If arriving from Pipeline 2 and devflow:task-planner finds the api-researcher findings incomplete for a critical edge case, pause and return to Pipeline 2 for a second research pass before continuing the plan
- If an ADR exists in `docs/decisions/` for this feature or component, devflow:task-planner must read it before producing the plan — the ADR constrains the plan and may have already rejected alternatives the planner might otherwise propose
- When devflow:interface-designer has run, devflow:test-engineer must read the contract from `docs/interfaces/` and derive contract compliance tests — one test per documented error case at minimum; devflow:code-reviewer must verify the implementation matches the contract exactly, treating any undisclosed deviation as a defect; devflow:acceptance-checker must also read the contract and verify the shipped behavior matches it — a gap between contract and implementation is an unmet acceptance criterion even if all unit tests pass
- When devflow:code-reviewer or devflow:acceptance-checker determines the contract in `docs/interfaces/` is itself incorrect or insufficient (not just the implementation), route back to devflow:interface-designer for a revision before continuing — the contract is the source of truth but can be corrected when implementation reveals a design error; after the revision, re-run devflow:feature-implementer (changed sections only), devflow:test-engineer (if the revision affects test expectations), and devflow:code-reviewer
- **Maintenance note:** Pipeline 3 and Pipeline 4 share identical completion rules — when updating Transition or completion Notes in one, apply the same change to the other

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback that requires fixes — after fixes are applied, re-run devflow:code-reviewer then proceed to devflow:acceptance-checker
- devflow:code-reviewer or devflow:acceptance-checker determines the contract in `docs/interfaces/` is incorrect or insufficient → route back to devflow:interface-designer for a revision, then re-run devflow:feature-implementer (changed sections only) and devflow:test-engineer if the revision affects test expectations, then re-run devflow:code-reviewer — do not implement against a known-wrong contract
- devflow:acceptance-checker finds unmet criteria due to missing implementation → return to devflow:feature-implementer, then re-run devflow:test-engineer and devflow:code-reviewer before re-checking
- devflow:acceptance-checker finds unmet criteria due to missing test coverage → return to devflow:test-engineer, then re-run devflow:code-reviewer before re-checking
- devflow:finishing-a-development-branch when all acceptance criteria are met

---

### 4) Bug fix / runtime failure / stack trace

**Use when:**
- a reported defect or runtime failure needs investigation and a targeted fix
- a stack trace, error log, or user report points to broken behavior
- a regression was introduced by a recent change

**Default pipeline:** `bug-repro-triager → test-engineer → feature-implementer → code-reviewer → acceptance-checker`

**Variants:**
- Skip devflow:bug-repro-triager only if a minimal reproduction and root cause are already confirmed with evidence
- Prepend devflow:using-git-worktrees before devflow:feature-implementer when the project uses git — creates an isolated worktree and feature branch before any code changes begin
- Use devflow:dispatching-parallel-agents when 3 or more independent failures exist across different subsystems — dispatch one agent per failure domain instead of investigating sequentially
- Insert devflow:context-mapper after devflow:bug-repro-triager when the codebase is large or the failure implicates a shared module — traces reverse dependencies and test coverage from the triage's affected code paths; downstream workers read the context map instead of scanning the codebase themselves
- Insert devflow:interface-designer after devflow:bug-repro-triager when the bug reveals the API contract in `docs/interfaces/` is itself incorrect (wrong error shape, missing endpoint, incorrect field type in the documentation) — correct the contract before the regression test is written so the test asserts the correct contracted behavior, not the previously-observed broken behavior
- Append devflow:dependency-auditor after devflow:feature-implementer when the fix adds or modifies package manifests (package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, etc.) — run before devflow:code-reviewer so audit findings are available as review context; if dependency-auditor reports Critical or High findings, escalate to Pipeline 10 before merging

**Notes:**
- Reproduce first — do not propose or apply a fix before the failure is confirmed
- devflow:test-engineer writes a failing regression test before devflow:feature-implementer applies the fix
- devflow:feature-implementer applies the minimal fix only — no unrelated cleanup or refactoring
- When the bug involves a public API boundary with an existing contract in `docs/interfaces/`, devflow:test-engineer must read the contract before writing the regression test — the test should assert the correct contracted behavior, not the previously-observed broken behavior
- Use devflow:session-continuity at session boundaries to preserve investigation and fix state across sessions
- When devflow:context-mapper has run, all downstream workers must read the context map from `docs/context-maps/` before loading any project files — the map is the scoping contract for the pipeline
- **Maintenance note:** Pipeline 3 and Pipeline 4 share identical completion rules — when updating Transition or completion Notes in one, apply the same change to the other

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback that requires fixes — after fixes are applied, re-run devflow:code-reviewer then proceed to devflow:acceptance-checker
- devflow:code-reviewer or devflow:acceptance-checker determines the contract in `docs/interfaces/` is incorrect or insufficient → route back to devflow:interface-designer for a revision, then re-run devflow:feature-implementer (changed sections only) and devflow:test-engineer if the revision affects test expectations, then re-run devflow:code-reviewer — do not implement against a known-wrong contract
- devflow:acceptance-checker finds unmet criteria due to missing implementation → return to devflow:feature-implementer, then re-run devflow:test-engineer and devflow:code-reviewer before re-checking
- devflow:acceptance-checker finds unmet criteria due to missing test coverage → return to devflow:test-engineer, then re-run devflow:code-reviewer before re-checking
- devflow:finishing-a-development-branch when all acceptance criteria are met

---

### 5) Refactor / simplification / maintainability

**Use when:**
- code structure needs improvement without changing external behavior
- recently merged code needs cleanup or simplification
- a scheduled technical debt item is being addressed

**Default pipeline:** `task-planner → code-simplifier → code-reviewer → acceptance-checker`

**Variants:**
- Prepend devflow:test-engineer if behavior-preservation risk is non-trivial and existing coverage is insufficient
- Prepend devflow:using-git-worktrees before devflow:code-simplifier when the project uses git — creates an isolated worktree and feature branch before any code changes begin
- Insert devflow:context-mapper after devflow:task-planner when the refactor targets a shared module — maps reverse dependents before any changes begin so the blast area is known upfront
- Append devflow:interface-designer after devflow:acceptance-checker when the refactor changes the public surface of a module or endpoint with an existing contract in `docs/interfaces/` (renamed parameter, restructured export, changed return shape) — updates the contract to match the confirmed-correct simplified shape; runs last so the contract reflects only the accepted final state

**Notes:**
- devflow:code-simplifier must not alter external behavior or broaden scope beyond the refactor target
- When the refactor target has an existing contract in `docs/interfaces/`, devflow:code-reviewer must verify the simplified implementation still matches the contract — contract drift is a defect even if all tests pass, because callers depend on the documented shape; surface any drift as a Critical Issue
- devflow:acceptance-checker confirms behavior is preserved — not improved or extended
- Use devflow:session-continuity at session boundaries to preserve refactor state across sessions
- When devflow:context-mapper has run, all downstream workers must read the context map from `docs/context-maps/` before loading any project files — the map is the scoping contract for the pipeline

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback that requires fixes — after fixes are applied, re-run devflow:code-reviewer then proceed to devflow:acceptance-checker
- devflow:acceptance-checker finds unmet criteria due to altered behavior → return to devflow:code-simplifier, then re-run devflow:code-reviewer before re-checking
- devflow:acceptance-checker finds unmet criteria due to insufficient test coverage to confirm behavior preservation → add devflow:test-engineer before devflow:code-simplifier if not already present in this pipeline run, then re-run devflow:code-simplifier and devflow:code-reviewer before re-checking
- devflow:finishing-a-development-branch when all acceptance criteria are met

---

### 6) Test-only

**Use when:**
- coverage gaps need to be filled without changing production code
- an explicit request to add, update, or review tests is made
- a bug fix was applied and regression tests need to be added in a separate pass

**Default pipeline:** `test-engineer → code-reviewer`

**Variants:**
- Add devflow:acceptance-checker if tests must map to formal acceptance criteria
- Skip devflow:code-reviewer if tests are trivial and isolated
- Prepend devflow:using-git-worktrees before devflow:test-engineer when the project uses git — creates an isolated worktree and feature branch before any test changes begin
- Insert devflow:context-mapper before devflow:test-engineer when the codebase is large — maps existing test files and coverage gaps so test-engineer targets the right files without scanning the broader test suite

**Notes:**
- devflow:test-engineer must not modify production code unless absolutely necessary for testability, and must explain why if it does
- devflow:code-reviewer is required for complex or shared test infrastructure changes
- Use devflow:session-continuity at session boundaries to preserve test coverage state across sessions
- When devflow:context-mapper has run, devflow:test-engineer must read the context map from `docs/context-maps/` before loading any project files — the Associated Test Files list is the primary input

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback on test quality or shared test infrastructure — after fixes are applied, re-run devflow:code-reviewer before closing
- Coverage gaps remain after review → return to devflow:test-engineer for another pass
- Coverage gaps require production code changes to enable testability → route to Pipeline 3 (New feature) or Pipeline 4 (Bug fix) as appropriate
- devflow:code-reviewer returns no blocking issues and all coverage goals are confirmed (when the devflow:acceptance-checker Variant is not active) → devflow:finishing-a-development-branch
- devflow:acceptance-checker confirms all coverage criteria met (when the devflow:acceptance-checker Variant is active) → devflow:finishing-a-development-branch

---

### 7) Review-only

**Use when:**
- an explicit review of existing code or a pull request is requested
- a second opinion on a diff is needed before merging
- no implementation change is intended — only evaluation

**Default pipeline:** `code-reviewer`

**Variants:**
- Add devflow:acceptance-checker if formal acceptance criteria need to be verified against the diff
- Add devflow:test-engineer if review surfaces missing or insufficient coverage — prepend devflow:using-git-worktrees before devflow:test-engineer when the project uses git, since test-engineer produces real file changes
- Add devflow:find-bugs when the review is security-focused or the diff touches auth, input handling, or external calls — for a full threat-model-led security audit use Pipeline 10 instead
- Insert devflow:context-mapper before devflow:code-reviewer when reviewing changes to shared modules — the Reverse Dependents list directly informs regression risk assessment

**Notes:**
- devflow:code-reviewer critiques correctness, regressions, standards, and test adequacy — it does not rewrite unless explicitly asked
- State the review scope before devflow:code-reviewer begins
- Use devflow:session-continuity at session boundaries to preserve review state across sessions
- When devflow:context-mapper has run, devflow:code-reviewer must read the context map from `docs/context-maps/` before loading any project files — use the Reverse Dependents list to scope the blast-area review

**Transition:**
- devflow:code-reviewer returns feedback → devflow:receiving-code-review to process and document the findings; route to Pipeline 3 (New feature) or Pipeline 4 (Bug fix) to apply the fixes, then return to Pipeline 7 for a confirmation review pass — Pipeline 7 does not implement
- devflow:acceptance-checker finds unmet criteria → Pipeline 7 does not implement — route to Pipeline 3 (New feature) or Pipeline 4 (Bug fix) as appropriate to address the gaps, then return to Pipeline 7 for a final review pass
- devflow:code-reviewer returns no blocking issues (and the devflow:acceptance-checker Variant is not active) → devflow:finishing-a-development-branch
- devflow:acceptance-checker confirms all criteria met (when the devflow:acceptance-checker Variant is active) → devflow:finishing-a-development-branch

---

### 8) Docs-only

**Use when:**
- documentation needs updating after a code change
- a changelog, migration note, or API reference needs to be written
- README or usage docs are out of date with the current implementation

**Default pipeline:** `docs-updater`

**Variants:**
- Add devflow:code-reviewer if docs describe technically complex or risky behavior that requires accuracy verification

**Notes:**
- devflow:docs-updater must not invent undocumented behavior — document only what shipped
- Scope docs updates to the changes that actually landed
- Use devflow:session-continuity at session boundaries to preserve docs state across sessions

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback on doc accuracy — after fixes are applied, re-run devflow:code-reviewer to confirm the issues are resolved
- devflow:finishing-a-development-branch when docs are complete and no blocking issues remain

---

### 9) Performance / optimization

**Use when:**
- a feature or component is measurably slow or fails to meet a performance target
- a performance regression has been introduced by a recent change
- optimization work is requested on any part of the system

**Default pipeline:** `performance-profiler → test-engineer → feature-implementer → code-reviewer → acceptance-checker`

**Variants:**
- Prepend devflow:using-git-worktrees before devflow:test-engineer when the project uses git — creates an isolated worktree and branch before any optimization changes begin
- Insert devflow:context-mapper after devflow:performance-profiler when the hotspot implicates a shared module — maps reverse dependents so optimization changes do not silently degrade callers
- Skip devflow:test-engineer if the project has no benchmarking infrastructure and adding it is explicitly out of scope — note the gap
- Append devflow:docs-updater when performance characteristics are documented (SLAs, benchmarks in README, API contracts)

**Notes:**
- devflow:performance-profiler must establish measurable baselines and identify the concrete hotspot before devflow:feature-implementer begins — never optimize without a measured target
- If devflow:performance-profiler cannot identify a concrete hotspot (tooling unavailable, environment not representative), stop and resolve the measurement gap before proceeding — do not guess
- devflow:feature-implementer addresses one hotspot at a time — do not combine multiple optimizations in a single pass
- devflow:acceptance-checker validates before/after measurements against the criteria defined by devflow:performance-profiler — subjective "it feels faster" is not evidence
- Use devflow:session-continuity at session boundaries to preserve profiling state and baseline measurements across sessions
- When devflow:context-mapper has run, all downstream workers must read the context map from `docs/context-maps/` before loading any project files — the map is the scoping contract for the pipeline

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback — after fixes are applied, devflow:test-engineer re-runs the benchmark if the fix touches the optimized code path, then re-run devflow:code-reviewer and proceed to devflow:acceptance-checker
- devflow:acceptance-checker finds performance target not met → return to devflow:feature-implementer for another targeted optimization pass; devflow:test-engineer re-runs the benchmark to take the new measurement, then devflow:code-reviewer before re-checking
- devflow:acceptance-checker finds a regression introduced → return to devflow:feature-implementer to revert or correct; devflow:test-engineer re-runs the benchmark to confirm the regression is cleared, then devflow:code-reviewer before re-checking
- devflow:finishing-a-development-branch when performance targets are met and no regressions are introduced

---

### 10) Security audit

**Use when:**
- a security audit is explicitly requested on a change or feature
- the change introduces new user inputs, authentication/authorization paths, external calls, or sensitive data handling
- a new dependency is introduced or an existing one is significantly upgraded
- a pre-release or pre-merge security gate is required

**Default pipeline:** `threat-modeler → dependency-auditor → find-bugs`

**Variants:**
- Prepend devflow:using-git-worktrees before devflow:threat-modeler when remediation findings are expected — isolates audit work from main branch
- Skip devflow:dependency-auditor if no dependencies were added or changed and the last audit is recent — document the decision
- Skip devflow:threat-modeler if the audit scope is purely dependency-level (no application code changes) — dependency-auditor can run standalone
- Append devflow:feature-implementer pipeline (Pipeline 3 or 4) when findings require code remediation — the security pipeline finds, not fixes
- Append devflow:docs-updater when findings result in documented security decisions (accepted risk, threat model in docs, updated security policy)

**Notes:**
- devflow:threat-modeler produces the threat checklist that devflow:find-bugs uses as its investigation context — without it, find-bugs operates on generic heuristics rather than change-specific threats
- devflow:dependency-auditor findings feed into devflow:find-bugs context — the auditor notes which package APIs and call sites to prioritize in code review
- Security audit (Pipeline 10) is separate from functional correctness review (Pipeline 7) — run both independently on the same change; do not conflate them
- devflow:find-bugs does not fix anything — it produces a findings report; confirmed vulnerabilities exit to Pipeline 4 (bug fix) with the security report as triage input
- If no audit tooling is available for the detected ecosystem, devflow:dependency-auditor stops and reports the gap — do not proceed with findings from memory
- Use devflow:session-continuity at session boundaries to preserve threat model and audit findings across sessions

**Transition:**
- devflow:find-bugs finds code vulnerabilities requiring fixes → exit to Pipeline 4 for each confirmed finding, with the security report as triage input for devflow:bug-repro-triager
- devflow:find-bugs finds dependency issues requiring upgrades → resolve dependency upgrades, re-run devflow:dependency-auditor to confirm clean, then re-run devflow:find-bugs
- devflow:find-bugs finds no actionable issues → close audit; optionally append devflow:docs-updater to record the clean audit or document accepted risks
- Security audit requested alongside a feature review → run Pipeline 10 in a separate pass before or after Pipeline 7; do not merge the two pipelines

---

## Worker Roles and Boundaries (Enforce Role Discipline)

Workers must stay in role. Do not let one worker silently do another worker's job unless explicitly requested.

| Worker | Does | Does not |
|--------|------|----------|
| devflow:interview | Extract requirements, constraints, and acceptance criteria through structured one-at-a-time questioning; produce a written spec document | Propose designs, make architectural decisions, or write plans |
| devflow:brainstorming | Turn a written spec into a concrete design by exploring approaches and trade-offs; produce an agreed design ready for planning | Write a plan, implement code, or gather requirements (that is devflow:interview) |
| devflow:task-planner | Clarify goals, define scope, plan steps, risks, tests, done criteria | Write production code |
| devflow:interface-designer | Define the interface contract (OpenAPI 3.x spec, TypeScript interfaces, or AsyncAPI schema) for a new or modified public API, shared module, or service boundary before implementation begins; save artifact to `docs/interfaces/` | Write implementation code; make technology selection decisions; review application logic |
| devflow:context-mapper | Trace direct dependencies and reverse dependents of target files; identify associated test files and coverage gaps; write a context map for downstream workers to consume | Modify any file; make implementation decisions; recurse into transitive dependencies without explicit instruction |
| devflow:feature-implementer | Implement one scoped plan step with minimal diff — when devflow:interface-designer has run, implement against the contract in `docs/interfaces/`; deviations require updating the contract first | Broad refactor, rewrite plan, review code, do unrelated cleanup |
| devflow:test-engineer | Write/update tests, regression coverage, edge cases, repro tests | Change production code unless absolutely necessary and explicitly justified |
| devflow:code-reviewer | Critique correctness, regressions, standards, test adequacy | Rewrite implementation unless asked |
| devflow:find-bugs | Audit branch diffs for security vulnerabilities, bugs, and logic issues using a structured checklist | Make code changes; review for style or readability; debug known failures (use devflow:systematic-debugging for that) |
| devflow:acceptance-checker | Map implementation/tests to acceptance criteria with evidence | Optimize code or invent missing evidence |
| devflow:docs-updater | Update docs/readme/changelog/migration notes for recent changes | Invent undocumented behavior |
| devflow:api-researcher | Research external APIs/libraries and produce implementation guidance | Implement production code unless explicitly asked |
| devflow:bug-repro-triager | Produce repro steps, hypotheses, investigation plan, failing-test strategy | Implement fix |
| devflow:performance-profiler | Establish performance baselines through profiling, identify concrete hotspots with evidence, define measurable acceptance criteria before optimization begins | Optimize or rewrite code; recommend changes without profiling evidence |
| devflow:threat-modeler | Map attack surface for a change (inputs, auth paths, trust boundaries, external calls, sensitive data flows); produce an applicability-assessed threat checklist for downstream security workers | Fix vulnerabilities; review code for correctness; scan dependencies (that is devflow:dependency-auditor) |
| devflow:dependency-auditor | Run ecosystem-native scanners (npm audit, pip-audit, cargo audit, etc.); report CVEs, license issues, and outdated pins with evidence; produce handoff notes for the downstream worker (devflow:find-bugs in Pipeline 10; devflow:code-reviewer in Pipeline 3/4) | Fix vulnerabilities or upgrade packages; review application code; produce findings from memory when scanner tooling is unavailable |
| devflow:dispatching-parallel-agents | Split independent problem domains across concurrent agents when 3+ failures or tasks have no shared state | Investigate related failures together; work on problems with shared state or file conflicts |
| devflow:code-simplifier | Orchestrate code simplification — dispatches devflow:code-simplification to do the work | Simplify code directly |
| devflow:code-simplification | Simplify/refine recently modified code while preserving behavior | Alter functionality or broaden scope |
| devflow:research | Research any technology, library, framework, or concept and produce actionable findings | Write production code or make implementation decisions |
| devflow:spike-investigator | Run hands-on experiments to confirm or refute a hypothesis; works in throwaway mode | Write production-ready code, enforce TDD, or expand scope beyond the stated hypothesis |
| devflow:poc-retrospective | Capture spike decision, evidence, key learnings, carry-forwards, and cleanup checklist | Implement anything or reopen a closed investigation |
| devflow:adr-writer | Write a structured Architecture Decision Record documenting the decision, options considered, rationale, trade-offs, and conditions for revisiting; save to `docs/decisions/` | Evaluate options or make the decision (that is devflow:technology-selector or devflow:brainstorming); implement anything |
| devflow:hypothesis-validator | Design a minimal experiment with explicit criteria, run it, and evaluate the result against pre-defined evidence | Expand beyond the single stated assumption or produce implementation code |
| devflow:technology-selector | Evaluate 2–4 technology options against stated requirements and produce a single recommendation with trade-offs | Implement the chosen technology or evaluate options not relevant to the stated requirement |
| devflow:scope-estimator | Produce rough effort/complexity sizing per work area with confidence levels and expansion risks | Produce step-by-step implementation plans or make architectural decisions |
| devflow:using-git-worktrees | Create an isolated git worktree and feature branch before implementation begins; verify base branch state; announce the workspace path | Write plans, execute tasks, or close/clean up the worktree (that is devflow:finishing-a-development-branch) |
| devflow:session-continuity | Write or read a structured state snapshot to preserve investigation/implementation context across sessions | Perform task work — only captures and restores state |

---

## Skill Priority

When multiple skills or worker agents might apply, use this order:

1. **Process / routing skill first** (this skill)
2. **Research / triage workers** (when uncertainty exists)
3. **Planning worker**
4. **Implementation worker**
5. **Test worker**
6. **Review worker**
7. **Acceptance worker**
8. **Docs/simplification workers** as needed

### Principle
Process determines **how** to approach the task before implementation determines **what** to change.

---

## Red Flags (Rationalization Warnings)

If you think any of these, stop and route to worker agents first:

- "This is simple, I can just answer directly"
- "Let me quickly inspect code first"
- "I can start coding and route later"
- "I need to ask clarifying questions before picking a worker"
- "I already know which worker to use, no need to announce it"
- "The worker format is overkill"
- "I'll do one small thing before routing"
- "I remember the worker behavior from before"

These are signs you are about to skip discipline.

---

## Clarifying Questions Rule

If clarifying questions are needed **and** a worker likely applies:

1. Route first
2. Set `Current agent` to the worker most appropriate for framing the question (usually devflow:task-planner or devflow:bug-repro-triager)
3. Ask the clarifying question **in that worker's role format**

Do not skip routing just because the next step is a question.

---

## Scope and Recency Rule (Global)

Unless explicitly instructed otherwise, workers should:
- focus on recently modified code / current task scope
- avoid broad codebase sweeps
- preserve behavior outside scope
- prefer minimal, reviewable diffs
- list assumptions explicitly instead of guessing

---

## Structured Output Enforcement

Workers must follow their own defined output schema. If a worker output does not match its schema, correct course before continuing.

At minimum, all worker outputs must include:
- active identity
- scope
- structured findings/work
- assumptions (when relevant)
- compliance footer

---

## Examples (Behavioral)

### Example: "I have an idea for a new feature but I'm not sure what it should do exactly"
- `Selected worker agents: interview → brainstorming → scope-estimator → writing-plans`
- `Reason: requirements undefined — spec and design must be established before any planning or coding (pipeline 0)`
- `Current agent: interview`

### Example: "I want to know if we can use library X to do Y before we build it"
- `Selected worker agents: research → spike-investigator → poc-retrospective`
- `Reason: unvalidated feasibility assumption — validate before committing to a plan (pipeline 1)`
- `Current agent: research`

### Example: "We're integrating Stripe for the first time"
- `Selected worker agents: api-researcher`
- `Reason: unfamiliar external API — research gate before planning; carry findings into task-planner at the start of Pipeline 3 (pipeline 2)`
- `Current agent: api-researcher`

### Example: "Add pagination to the users list"
- `Selected worker agents: task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker`
- `Reason: new behavior change with regression risk (pipeline 3)`
- `Current agent: task-planner`

### Example: "Fix this stack trace"
- `Selected worker agents: bug-repro-triager → test-engineer → feature-implementer → code-reviewer → acceptance-checker`
- `Reason: runtime failure — reproduce and regression-cover before fixing (pipeline 4)`
- `Current agent: bug-repro-triager`

### Example: "This module has gotten hard to read — clean it up without changing behavior"
- `Selected worker agents: task-planner → code-simplifier → code-reviewer → acceptance-checker`
- `Reason: targeted refactor with behavior-preservation requirement (pipeline 5)`
- `Current agent: task-planner`

### Example: "We merged the auth fix but never added regression tests"
- `Selected worker agents: test-engineer → code-reviewer`
- `Reason: explicit test-only request — no production code change intended (pipeline 6)`
- `Current agent: test-engineer`

### Example: "Can you review these recent changes?"
- `Selected worker agents: code-reviewer`
- `Reason: explicit review request, no implementation intended (pipeline 7)`
- `Current agent: code-reviewer`

### Example: "Update the README to reflect the new config options we shipped"
- `Selected worker agents: docs-updater`
- `Reason: documentation update scoped to recent code changes — no implementation intended (pipeline 8)`
- `Current agent: docs-updater`

### Example: "The search endpoint is timing out under load — bring p95 latency under 200ms"
- `Selected worker agents: performance-profiler → test-engineer → feature-implementer → code-reviewer → acceptance-checker`
- `Reason: performance target with measurable threshold — profile the hotspot first, then codify criteria as a failing benchmark before optimizing (pipeline 9)`
- `Current agent: performance-profiler`

### Example: "We need to decide between PostgreSQL and MongoDB for the new service"
- `Selected worker agents: technology-selector → adr-writer → writing-plans`
- `Reason: technology choice between named alternatives with significant architectural consequences — decision must be documented before planning begins (pipeline 0 + adr-writer variant)`
- `Current agent: technology-selector`

### Example: "We're about to ship the new payment flow — run a security audit first"
- `Selected worker agents: threat-modeler → dependency-auditor → find-bugs`
- `Reason: pre-release security gate on a change that introduces auth paths, external calls, and sensitive data handling (pipeline 10)`
- `Current agent: threat-modeler`

### Example: "Add a user search endpoint to the REST API"
- `Selected worker agents: task-planner → interface-designer → feature-implementer → test-engineer → code-reviewer → acceptance-checker`
- `Reason: new REST endpoint consumed by a frontend client — define the contract before implementation so caller and implementer agree on the shape before any code is written (pipeline 3 + interface-designer variant)`
- `Current agent: task-planner`

### Example: "Add the stripe package and implement payment processing"
- `Selected worker agents: task-planner → feature-implementer → test-engineer → dependency-auditor → code-reviewer → acceptance-checker`
- `Reason: new feature that introduces an external package — audit newly added dependencies before code review (pipeline 3 + dependency-auditor variant)`
- `Current agent: task-planner`

---

## Final Principle

User instructions define **WHAT** needs to happen.
This skill enforces **HOW** the work is approached.

Do not skip routing. Do not skip worker selection. Do not do silent generic work when a worker applies.
