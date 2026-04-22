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

Use these default pipelines unless there is a strong reason to change them. Pipelines follow the natural lifecycle of a task: specify → validate → learn → build → fix → clean → cover → gate → document.

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

**Notes:**
- devflow:interview produces a written spec; devflow:brainstorming turns the spec into a concrete design
- Do not start devflow:writing-plans until the design is agreed and the spec document is saved
- devflow:scope-estimator gates the proceed decision: if the estimate is XL or confidence is Low, split or simplify before opening a plan
- No code is written in this pipeline — the output is a spec and a plan, not an implementation

**Transition:**
- devflow:scope-estimator recommends **Proceed** → devflow:writing-plans, then route to the appropriate implementation pipeline (3, 4, etc.)
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

**Notes:**
- devflow:spike-investigator works in throwaway mode: no TDD, no production standards apply
- devflow:poc-retrospective is **mandatory** — do not close a spike without capturing the decision
- Use devflow:spike-executor to orchestrate the full lifecycle
- Use devflow:session-continuity at session boundaries to preserve state across sessions

**Transition:**
- **Proceed** → devflow:writing-plans for the production implementation
- **Pivot** → open a new spike with the refined hypothesis
- **Abandon** → devflow:poc-retrospective closes the record; no further work

---

### 2) Unfamiliar API / library / framework

**Use when:**
- integrating a library, framework, or external API not previously used in this project
- the implementation approach depends on understanding undocumented or complex behavior
- version differences or breaking changes may affect the approach

**Default pipeline:** `api-researcher → task-planner → feature-implementer → test-engineer → code-reviewer`

**Variants:**
- Prepend devflow:technology-selector when the library or framework has not yet been chosen and two or more options are under consideration
- Skip devflow:api-researcher only if the API is already well-understood and documented internally
- Prepend devflow:using-git-worktrees before devflow:feature-implementer when the project uses git — creates an isolated worktree and feature branch before any code changes begin

**Notes:**
- devflow:api-researcher must produce actionable findings before devflow:task-planner begins
- Do not let devflow:feature-implementer start until devflow:api-researcher findings are incorporated into the plan

**Transition:**
- Append devflow:acceptance-checker if formal acceptance criteria exist
- Append devflow:docs-updater if the integration introduces new usage patterns worth documenting

---

### 3) New feature / behavior change

**Use when:**
- adding new user-visible behavior or a new system capability
- changing existing behavior in a backward-incompatible way
- extending or modifying a public API, configuration, or interface

**Default pipeline:** `task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker`

**Variants:**
- Prepend devflow:scope-estimator when scope is unclear or the feature touches many areas of the codebase
- Append devflow:docs-updater when public behavior, API, configuration, or migration notes change
- Prepend devflow:using-git-worktrees before devflow:feature-implementer when the project uses git — creates an isolated worktree and feature branch before any code changes begin

**Notes:**
- devflow:task-planner defines done criteria before devflow:feature-implementer starts
- devflow:test-engineer writes tests before the branch is merged, not after
- devflow:acceptance-checker maps evidence to stated criteria — it does not invent missing evidence
- Use devflow:session-continuity at session boundaries to preserve implementation state across sessions

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback that requires fixes before proceeding
- devflow:docs-updater if documentation is required
- devflow:finishing-a-development-branch when all pipeline steps are complete

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

**Notes:**
- Reproduce first — do not propose or apply a fix before the failure is confirmed
- devflow:test-engineer writes a failing regression test before devflow:feature-implementer applies the fix
- devflow:feature-implementer applies the minimal fix only — no unrelated cleanup or refactoring
- Use devflow:session-continuity at session boundaries to preserve investigation and fix state across sessions

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback that requires fixes before proceeding
- devflow:acceptance-checker confirms the regression is closed
- devflow:finishing-a-development-branch when done

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

**Notes:**
- devflow:code-simplifier must not alter external behavior or broaden scope beyond the refactor target
- devflow:acceptance-checker confirms behavior is preserved — not improved or extended

**Transition:**
- devflow:receiving-code-review if devflow:code-reviewer returns feedback that requires fixes before proceeding
- devflow:finishing-a-development-branch when done

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

**Notes:**
- devflow:test-engineer must not modify production code unless absolutely necessary for testability, and must explain why if it does
- devflow:code-reviewer is required for complex or shared test infrastructure changes

**Transition:**
- No further pipeline steps required unless coverage gaps remain after review

---

### 7) Review-only

**Use when:**
- an explicit review of existing code or a pull request is requested
- a second opinion on a diff is needed before merging
- no implementation change is intended — only evaluation

**Default pipeline:** `code-reviewer`

**Variants:**
- Add devflow:acceptance-checker if formal acceptance criteria need to be verified against the diff
- Add devflow:test-engineer if review surfaces missing or insufficient coverage
- Add devflow:find-bugs when the review is security-focused or the diff touches auth, input handling, or external calls

**Notes:**
- devflow:code-reviewer critiques correctness, regressions, standards, and test adequacy — it does not rewrite unless explicitly asked
- State the review scope before devflow:code-reviewer begins

**Transition:**
- Use devflow:receiving-code-review if review feedback needs to be processed and acted on

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

**Transition:**
- No further pipeline steps required

---

## Worker Roles and Boundaries (Enforce Role Discipline)

Workers must stay in role. Do not let one worker silently do another worker's job unless explicitly requested.

| Worker | Does | Does not |
|--------|------|----------|
| devflow:interview | Extract requirements, constraints, and acceptance criteria through structured one-at-a-time questioning; produce a written spec document | Propose designs, make architectural decisions, or write plans |
| devflow:brainstorming | Turn a written spec into a concrete design by exploring approaches and trade-offs; produce an agreed design ready for planning | Write a plan, implement code, or gather requirements (that is devflow:interview) |
| devflow:task-planner | Clarify goals, define scope, plan steps, risks, tests, done criteria | Write production code |
| devflow:feature-implementer | Implement one scoped plan step with minimal diff | Broad refactor, rewrite plan, review code, do unrelated cleanup |
| devflow:test-engineer | Write/update tests, regression coverage, edge cases, repro tests | Change production code unless absolutely necessary and explicitly justified |
| devflow:code-reviewer | Critique correctness, regressions, standards, test adequacy | Rewrite implementation unless asked |
| devflow:acceptance-checker | Map implementation/tests to acceptance criteria with evidence | Optimize code or invent missing evidence |
| devflow:docs-updater | Update docs/readme/changelog/migration notes for recent changes | Invent undocumented behavior |
| devflow:api-researcher | Research external APIs/libraries and produce implementation guidance | Implement production code unless explicitly asked |
| devflow:bug-repro-triager | Produce repro steps, hypotheses, investigation plan, failing-test strategy | Implement fix |
| devflow:code-simplifier | Orchestrate code simplification — dispatches devflow:code-simplification to do the work | Simplify code directly |
| devflow:code-simplification | Simplify/refine recently modified code while preserving behavior | Alter functionality or broaden scope |
| devflow:research | Research any technology, library, framework, or concept and produce actionable findings | Write production code or make implementation decisions |
| devflow:spike-investigator | Run hands-on experiments to confirm or refute a hypothesis; works in throwaway mode | Write production-ready code, enforce TDD, or expand scope beyond the stated hypothesis |
| devflow:poc-retrospective | Capture spike decision, evidence, key learnings, carry-forwards, and cleanup checklist | Implement anything or reopen a closed investigation |
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
- `Selected worker agents: api-researcher → task-planner → feature-implementer → test-engineer → code-reviewer`
- `Reason: unfamiliar external API — research before planning (pipeline 2)`
- `Current agent: api-researcher`

### Example: "Add pagination to the users list"
- `Selected worker agents: task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker`
- `Reason: new behavior change with regression risk (pipeline 3)`
- `Current agent: task-planner`

### Example: "Fix this stack trace"
- `Selected worker agents: bug-repro-triager → test-engineer → feature-implementer → code-reviewer → acceptance-checker`
- `Reason: runtime failure — reproduce and regression-cover before fixing (pipeline 4)`
- `Current agent: bug-repro-triager`

### Example: "Can you review these recent changes?"
- `Selected worker agents: code-reviewer`
- `Reason: explicit review request, no implementation intended (pipeline 7)`
- `Current agent: code-reviewer`

---

## Final Principle

User instructions define **WHAT** needs to happen.
This skill enforces **HOW** the work is approached.

Do not skip routing. Do not skip worker selection. Do not do silent generic work when a worker applies.
