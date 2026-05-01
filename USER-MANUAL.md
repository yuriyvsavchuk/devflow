# Devflow User Manual

A practical guide to the Devflow framework — what it is, why it exists, how to install it, and how to get the most out of it.

---

## Table of Contents

1. [Why Devflow Exists](#1-why-devflow-exists)
2. [Core Concepts](#2-core-concepts)
3. [Framework Structure](#3-framework-structure)
4. [Architecture Overview](#4-architecture-overview)
5. [The Eleven Pipelines](#5-the-eleven-pipelines)
6. [Pipeline Flow Diagrams](#6-pipeline-flow-diagrams)
7. [Usage Examples](#7-usage-examples)
8. [Installation — Claude Code](#8-installation--claude-code)
9. [Installation — Other AI Tools](#9-installation--other-ai-tools)
10. [Creating New Skills and Agents](#10-creating-new-skills-and-agents)
11. [Limitations](#11-limitations)
12. [Quick Reference](#12-quick-reference)

---

## 1. Why Devflow Exists

### The Problem

When you ask an AI assistant to help with software development, the default behavior is to start doing things immediately — writing code, proposing solutions, reviewing diffs — without first asking: *Is this the right approach? Have we understood the problem? What could go wrong?*

This produces several recurring failure modes:

- **Code written before requirements are understood** — builds the wrong thing
- **Fixes applied before the root cause is confirmed** — masks the real problem
- **Tests written after implementation** — proves nothing, catches nothing
- **Reviews that are rubber stamps** — performative agreement, no technical rigor
- **Work claimed complete without verification** — false confidence

Each of these failures is not a capability problem. The AI can do better. The problem is *discipline* — there is no structure forcing the right sequence of steps.

### The Solution

Devflow is a framework of **skills** and **worker agents** for Claude Code that enforces disciplined, sequenced software development workflows. It acts as a **router and gatekeeper**: before any code is written, any plan is made, or any review is given, the right worker for the job is selected and announced.

The result is that every task follows a proven pipeline — requirements before design, design before planning, planning before implementation, tests before merge, verification before completion claims.

### Who It Is For

- **Solo developers** using Claude Code who want consistent, high-quality AI assistance across sessions
- **Teams** who want to enforce shared development discipline through AI tooling
- **Anyone who has been burned** by AI assistants confidently doing the wrong thing

---

## 2. Core Concepts

### Skills

A **skill** is a reusable process guide stored in `~/.claude/skills/`. It is invoked via a slash command (e.g., `/using-devflow`, `/test-driven-development`). Skills define *how* to approach a category of work — the steps, the rules, the checks.

Skills are loaded into Claude's context when invoked. They constrain and guide behavior for that session. Skills have no `model:` field — they are model-agnostic process guides.

### Agents

An **agent** is a worker definition stored in `~/.claude/agents/`. Each agent has a focused role, strict boundaries, a defined output format, and a model chosen for its cognitive tier. Agents are dispatched by skills to do specific work: plan, implement, test, review, document.

An agent knows what it **does** and — equally important — what it **does not** do. A `test-engineer` writes tests; it does not change production code. A `code-reviewer` critiques; it does not rewrite.

### The Router

`using-devflow` is the master routing skill. It must be invoked at the start of every task. It:

1. Reads the task description
2. Selects the correct **pipeline** (ordered sequence of workers)
3. Announces the pipeline and the first active agent
4. Enforces that no work begins before routing is complete

### Pipelines

A **pipeline** is an ordered sequence of workers matched to a task type. There are eleven pipelines covering the full software development lifecycle:

```
0   Requirements gathering     → understand the problem first
1   Spike / POC investigation  → validate before committing
2   Unfamiliar API / library   → research gate before building
3   New feature                → plan → build → test → review → verify
4   Bug fix                    → reproduce → test → fix → review → verify
5   Refactor                   → plan → simplify → review → verify
6   Test-only                  → add coverage without touching production
7   Review-only                → evaluate without implementing
8   Docs-only                  → document what shipped
9   Performance / optimization → profile → optimize targeted area → verify
10  Security audit             → threat-model → audit dependencies → code security review
```

### Worker Self-Identification

Every agent response begins with a three-line header:

```
Active agent: <agent name>
Purpose: <one sentence>
Scope: <what is in scope / out of scope>
```

And ends with:

```
Worker compliance: followed <agent-name> format
```

This makes compliance visible and auditable. You always know which worker is active and what it is responsible for.

---

## 3. Framework Structure

### Skills Catalog (22 skills)

| Category | Skill | Purpose |
|---|---|---|
| **Routing** | `using-devflow` | Master router — selects pipeline before any work begins |
| **Requirements** | `interview` | Structured questioning to produce a written spec |
| | `brainstorming` | Turns a spec into a concrete design through dialogue |
| **Decision records** | `adr-writer` | Documents significant architectural decisions in `docs/decisions/` before implementation begins |
| **Investigation** | `spike-executor` | Orchestrates full spike/POC lifecycle |
| | `hypothesis-validator` | Minimal experiment to test one specific assumption |
| | `poc-retrospective` | Captures spike decision, learnings, carry-forwards |
| | `find-bugs` | Security and quality audit of branch changes |
| **Planning** | `writing-plans` | Bite-sized, TDD-anchored implementation plans |
| | `executing-plans` | Runs a plan step-by-step with review checkpoints |
| **Implementation** | `test-driven-development` | RED-GREEN-REFACTOR cycle enforcement |
| | `code-simplifier` | Orchestrates code cleanup for clarity while preserving behavior |
| | `subagent-driven-development` | Parallel plan execution via independent subagents |
| | `dispatching-parallel-agents` | Parallelizes independent tasks across subagents |
| | `using-git-worktrees` | Isolated git worktree before implementation begins |
| **Review** | `requesting-code-review` | Verifies work meets requirements before merging |
| | `receiving-code-review` | Technical rigor when processing review feedback |
| | `verification-before-completion` | Evidence-based check before any completion claim |
| **Completion** | `finishing-a-development-branch` | Guides branch to merge, PR, or cleanup |
| **Continuity** | `session-continuity` | Snapshots work state for multi-session continuity |
| **Meta** | `writing-skills` | TDD-based approach to creating and testing new skills |
| **Debugging** | `systematic-debugging` | Root-cause investigation before proposing fixes |

### Agents Catalog (18 agents)

| Agent | Role | Model |
|---|---|---|
| `task-planner` | Translates tasks into minimal, executable implementation plans | Opus |
| `context-mapper` | Traces dependency blast area and writes a context map for downstream workers | Haiku |
| `feature-implementer` | Implements one scoped plan step with minimal diff | Sonnet |
| `test-engineer` | Writes/updates tests, regression coverage, and edge cases | Sonnet |
| `code-reviewer` | Critiques correctness, regressions, standards, and test adequacy | Sonnet |
| `acceptance-checker` | Maps implementation to acceptance criteria with evidence | Sonnet |
| `docs-updater` | Keeps documentation aligned with recent code changes | Haiku |
| `api-researcher` | Researches external APIs/libraries and produces implementation guidance | Sonnet |
| `bug-repro-triager` | Produces repro steps, root cause hypotheses, and investigation plans | Sonnet |
| `code-simplification` | Simplifies recently modified code while preserving exact behavior | Sonnet |
| `research` | General-purpose technical research for any domain, library, or concept | Sonnet |
| `spike-investigator` | Hands-on throwaway experimentation to validate a hypothesis | Sonnet |
| `technology-selector` | Evaluates technology options and produces a single recommendation with trade-offs | Opus |
| `scope-estimator` | Rough effort and complexity sizing before writing a full plan | Sonnet |
| `performance-profiler` | Establishes baselines, identifies hotspots through profiling, defines measurable acceptance criteria before optimization | Sonnet |
| `threat-modeler` | Maps attack surface for a change (inputs, auth paths, trust boundaries, data flows) and produces a threat checklist for security review | Sonnet |
| `dependency-auditor` | Runs ecosystem-native scanners (npm/pip/cargo audit), flags CVEs, license issues, and outdated pins | Sonnet |
| `interface-designer` | Defines interface contracts (OpenAPI 3.x specs, TypeScript interfaces, AsyncAPI schemas) before implementation begins — saves to `docs/interfaces/` | Sonnet |

**Model tiers:** Opus for high-stakes reasoning (planning, architecture decisions); Haiku for mechanical tasks (dependency mapping, doc sync); Sonnet for code reasoning, analysis, and writing.

---

## 4. Architecture Overview

### How a Task Flows Through Devflow

```mermaid
graph TD
    classDef startEnd fill:#E8F4FD,stroke:#555
    classDef router fill:#FFF3CD,stroke:#555
    classDef pipeline fill:#D5E8D4,stroke:#555
    classDef worker fill:#FFE8E8,stroke:#555
    classDef other fill:#F0F0F0,stroke:#555

    task([User Task]):::startEnd
    router[using-devflow<br/>Router + Gatekeeper]:::router

    subgraph Pipelines[Pipeline Selection]
        p0[0: Requirements]:::pipeline
        p1[1: Spike/POC]:::pipeline
        p2[2: New API]:::pipeline
        p3[3: Feature]:::pipeline
        p4[4: Bug Fix]:::pipeline
        p5[5: Refactor]:::pipeline
        p6[6: Tests]:::pipeline
        p7[7: Review]:::pipeline
        p8[8: Docs]:::pipeline
        p9[9: Performance]:::pipeline
        p10[10: Security]:::pipeline
    end

    subgraph Workers[Worker Agents — examples]
        w1[task-planner]:::worker
        w2[feature-implementer]:::worker
        w3[test-engineer]:::worker
        w4[code-reviewer]:::worker
        w5[...14 more agents]:::other
    end

    output([Structured Output<br/>+ Compliance Footer]):::startEnd

    task --> router
    router --> p0 & p1 & p2 & p3 & p4 & p5 & p6 & p7 & p8 & p9 & p10
    p3 --> w1 & w2 & w3 & w4
    p4 --> w3 & w2 & w4 & w5
    w1 & w2 & w3 & w4 --> output
```

### Pipeline Lifecycle

Pipelines follow the natural lifecycle of software development work:

```mermaid
graph LR
    classDef req fill:#D5E8D4,stroke:#555
    classDef spike fill:#DAE8FC,stroke:#555
    classDef api fill:#FFF2CC,stroke:#555
    classDef feat fill:#FFF2CC,stroke:#555
    classDef bug fill:#FFE6CC,stroke:#555
    classDef ref fill:#E1D5E7,stroke:#555
    classDef tst fill:#D5E8D4,stroke:#555
    classDef rev fill:#DAE8FC,stroke:#555
    classDef doc fill:#F8CECC,stroke:#555
    classDef perf fill:#FFD6E7,stroke:#555
    classDef sec fill:#F4CCCC,stroke:#555

    p0[0<br/>Requirements]:::req
    p1[1<br/>Spike/POC]:::spike
    p2[2<br/>New API]:::api
    p3[3<br/>Feature]:::feat
    p4[4<br/>Bug Fix]:::bug
    p5[5<br/>Refactor]:::ref
    p6[6<br/>Tests]:::tst
    p7[7<br/>Review]:::rev
    p8[8<br/>Docs]:::doc
    p9[9<br/>Performance]:::perf
    p10[10<br/>Security]:::sec

    p0 -.->|unknown feasibility| p1
    p0 -->|proceed| p3
    p1 -->|proceed| p3
    p2 -->|research complete| p3
    p2 -.->|needs proof-of-concept| p1
    p3 -.->|coverage gap| p6
    p3 -.->|review requested| p7
    p3 -.->|docs needed| p8
    p3 -.->|perf concern| p9
    p3 -.->|security surface| p10
    p4 -.->|coverage gap| p6
    p4 -.->|perf regression| p9
    p4 -.->|security concern| p10
    p5 -.->|review feedback| p7
    p6 -.->|production change needed| p3
    p6 -.->|bug-driven gap| p4
    p7 -.->|unmet criteria| p3
    p7 -.->|unmet criteria| p4
    p9 -.->|regression found| p4
    p10 -.->|vulnerability confirmed| p4
```

---

## 5. The Eleven Pipelines

Each pipeline maps a task type to an ordered sequence of workers. Workers are selected, announced, and executed in sequence. The router always makes the pipeline visible before work begins.

---

### Pipeline 0 — Requirements Gathering

**Use when:** The task is vague, requirements are not written down, or you cannot determine which implementation pipeline applies.

**Default pipeline:**
```
interview → brainstorming → scope-estimator → writing-plans
```

**Key rules:**
- No code is written in this pipeline — the output is a written spec and an implementation plan
- `interview` extracts requirements one question at a time; `brainstorming` turns them into a concrete design
- `scope-estimator` gates the proceed decision — if the estimate is XL or confidence is Low, split the work before opening a plan
- Do not start `writing-plans` until the design is agreed and the spec document is saved

**Useful variants:**
- Skip `interview` if requirements are partially specified — start directly with `brainstorming`
- Insert `spike-executor` between `brainstorming` and `scope-estimator` when feasibility of the proposed design is unknown
- Insert `adr-writer` after `brainstorming` when the design session produces a significant architectural decision — a choice affecting multiple components, hard to reverse, or made between named alternatives; write the ADR before `scope-estimator` or `writing-plans` begins
- Insert `adr-writer` after `technology-selector` (when used as a Variant) — the recommendation is the decision that the ADR records

**Exit transitions:**
- Scope is manageable → `writing-plans`, then route to Pipeline 3 or 4
- Key assumption unvalidated → Pipeline 1 (Spike/POC)
- Scope too large → split into multiple plans, each routed independently

---

### Pipeline 1 — Spike / POC Investigation

**Use when:** A technical idea needs feasibility validation before committing to a plan, or a key implementation assumption is unvalidated.

**Default pipeline:**
```
research → spike-investigator → poc-retrospective
```

**Key rules:**
- `spike-investigator` works in throwaway mode — no TDD, no production standards apply
- `poc-retrospective` is **mandatory** — never close a spike without capturing the decision, evidence, and carry-forwards
- When the spike produces a **Proceed** decision, start production implementation in a **new session** — read the retrospective to orient; do not carry spike-mode context forward

**Useful variants:**
- Replace `spike-investigator` with `hypothesis-validator` when the question is narrow and one specific assumption needs a designed experiment
- Insert `technology-selector` after `research` when the investigation includes a technology choice between named options
- Prepend `using-git-worktrees` before `spike-investigator` when the spike produces code artifacts — keeps throwaway code on an isolated branch
- Append `adr-writer` after `poc-retrospective` when the Proceed decision constitutes an architectural commitment — the retrospective records what the experiment revealed; the ADR records the architectural decision that follows from it

**Exit transitions:**
- Proceed → `writing-plans` in a new session, starting from the retrospective and any ADR written in this session
- Pivot → new spike with refined hypothesis
- Abandon → `poc-retrospective` closes the record; no further work

---

### Pipeline 2 — Unfamiliar API / Library / Framework

**Use when:** Integrating a library, framework, or external API not previously used in this project, or when version differences may affect the approach.

**Default pipeline:**
```
api-researcher
```

This pipeline is a **research gate only** — it produces findings, not implementation. No code is written here.

**Key rules:**
- `api-researcher` must produce actionable findings before any planning begins — do not proceed while critical behavior is still unknown
- If the findings are clear and the approach is viable, carry them explicitly into `task-planner` in Pipeline 3

**Useful variants:**
- Prepend `technology-selector` when the library or framework has not yet been chosen and two or more options are under consideration
- Append `adr-writer` after `api-researcher` when adopting this library or API is a significant architectural commitment — documents the adoption decision before Pipeline 3 begins

**Exit transitions:**
- Findings are clear and approach is viable → Pipeline 3 (Feature build), carrying research findings into `task-planner`
- Findings reveal an unknown that requires hands-on validation → Pipeline 1 (Spike/POC) to resolve before planning
- Findings reveal the integration is fundamentally incompatible → Pipeline 0 (Requirements) to rethink the design

---

### Pipeline 3 — New Feature / Behavior Change

**Use when:** Adding new user-visible behavior, changing existing behavior, or extending a public API or interface.

**Default pipeline:**
```
task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker
```

**Key rules:**
- `task-planner` defines done criteria before `feature-implementer` starts — no implementation without a plan
- `test-engineer` writes tests before the branch is merged, not after
- `acceptance-checker` maps evidence to stated criteria — it does not invent missing evidence
- If arriving from Pipeline 2 and `task-planner` finds the research findings incomplete for a critical edge case, return to Pipeline 2 for a second research pass before continuing

**Useful variants:**
- Prepend `scope-estimator` when scope is unclear or the feature touches many areas
- Prepend `using-git-worktrees` before `feature-implementer` to isolate work on a feature branch
- Insert `interface-designer` after `task-planner` when the change introduces or modifies a public API endpoint, shared module exports, or service boundary — produces a binding contract (OpenAPI 3.x spec, TypeScript interfaces, or AsyncAPI schema) in `docs/interfaces/` before `feature-implementer` begins; any deviation from the contract requires updating it first
- Move `test-engineer` before `feature-implementer` when `interface-designer` has run and the project follows TDD — the contract provides complete behavioral specifications (all endpoints, parameters, and error cases), enabling test-first; `test-engineer` writes contract compliance tests (RED) before any production code is written; `feature-implementer` then implements to GREEN
- Insert `context-mapper` after `task-planner` (or after `interface-designer` when both are active) when the codebase is large or the change touches a shared module — maps reverse dependencies and existing test coverage so downstream workers don't scan the full codebase
- Append `dependency-auditor` after `test-engineer` when the implementation adds or modifies package manifests (package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, etc.) — surfaces CVE exposure, license conflicts, and outdated pins from newly introduced packages before the code reviewer sees the diff; if Critical or High findings are reported, escalate to Pipeline 10 before merging
- Append `docs-updater` when public behavior, API, configuration, or migration notes change

**Exit transitions:**
- `code-reviewer` returns feedback → `receiving-code-review`, then re-run `code-reviewer`, then proceed to `acceptance-checker`
- `code-reviewer` or `acceptance-checker` determines the contract in `docs/interfaces/` is incorrect → route to `interface-designer` for a revision, then re-run `feature-implementer` (changed sections only) and `test-engineer` if the revision affects test expectations, then re-run `code-reviewer`
- `acceptance-checker` finds missing implementation → return to `feature-implementer`, re-run `test-engineer` and `code-reviewer` before re-checking
- `acceptance-checker` finds missing test coverage → return to `test-engineer`, re-run `code-reviewer` before re-checking
- All acceptance criteria met → `finishing-a-development-branch`

---

### Pipeline 4 — Bug Fix / Runtime Failure

**Use when:** A reported defect or runtime failure needs investigation and a targeted fix.

**Default pipeline:**
```
bug-repro-triager → test-engineer → feature-implementer → code-reviewer → acceptance-checker
```

**Key rules:**
- Reproduce first — no fix is proposed or applied before the failure is confirmed
- `test-engineer` writes a **failing regression test** before `feature-implementer` applies the fix
- `feature-implementer` applies the minimal fix only — no unrelated cleanup or refactoring

**Useful variants:**
- Skip `bug-repro-triager` only if a minimal reproduction and root cause are already confirmed with evidence
- Prepend `using-git-worktrees` before `feature-implementer` to isolate the fix on a branch
- Use `dispatching-parallel-agents` when 3 or more independent failures exist across different subsystems
- Insert `context-mapper` after `bug-repro-triager` when the codebase is large or the failure implicates a shared module
- Insert `interface-designer` after `bug-repro-triager` when the bug reveals the API contract in `docs/interfaces/` is itself incorrect (wrong error shape, missing endpoint, incorrect field type in the documentation) — correct the contract before the regression test is written so the test asserts the correct contracted behavior, not the previously-observed broken behavior
- Append `dependency-auditor` after `feature-implementer` when the fix adds or modifies package manifests (package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, etc.) — surfaces CVE exposure, license conflicts, and outdated pins from newly introduced packages before the code reviewer sees the diff; if Critical or High findings are reported, escalate to Pipeline 10 before merging

**Exit transitions:**
- `code-reviewer` returns feedback → `receiving-code-review`, then re-run `code-reviewer`, then proceed to `acceptance-checker`
- `code-reviewer` or `acceptance-checker` determines the contract in `docs/interfaces/` is incorrect → route to `interface-designer` for a revision, then re-run `feature-implementer` (changed sections only) and `test-engineer` if the revision affects test expectations, then re-run `code-reviewer`
- `acceptance-checker` finds missing implementation → return to `feature-implementer`, re-run `test-engineer` and `code-reviewer` before re-checking
- `acceptance-checker` finds missing test coverage → return to `test-engineer`, re-run `code-reviewer` before re-checking
- All acceptance criteria met → `finishing-a-development-branch`

> **Note:** Pipelines 3 and 4 share identical completion rules. Any change to the Transition or completion behavior of one applies to the other.

---

### Pipeline 5 — Refactor / Simplification

**Use when:** Code structure needs improvement without changing external behavior, or a scheduled technical debt item is being addressed.

**Default pipeline:**
```
task-planner → code-simplifier → code-reviewer → acceptance-checker
```

**Key rules:**
- `code-simplifier` must not alter external behavior or broaden scope beyond the refactor target
- `acceptance-checker` confirms behavior is preserved — not improved or extended
- If behavior-preservation risk is non-trivial and existing coverage is insufficient, add `test-engineer` before `code-simplifier`
- When the refactor target has an existing contract in `docs/interfaces/`, `code-reviewer` must verify the simplified implementation still matches the contract — contract drift is a defect even if all tests pass

**Useful variants:**
- Prepend `test-engineer` when existing test coverage is insufficient to confirm behavior preservation
- Prepend `using-git-worktrees` before `code-simplifier` to isolate refactor work on a branch
- Insert `context-mapper` after `task-planner` when the refactor targets a shared module — maps reverse dependents before any changes begin
- Append `interface-designer` after `acceptance-checker` when the refactor changes the public surface of a module or endpoint with an existing contract in `docs/interfaces/` (renamed parameter, restructured export, changed return shape) — updates the contract to match the confirmed-correct simplified shape

**Exit transitions:**
- `code-reviewer` returns feedback → `receiving-code-review`, re-run `code-reviewer`, then proceed to `acceptance-checker`
- `acceptance-checker` finds altered behavior → return to `code-simplifier`, re-run `code-reviewer` before re-checking
- `acceptance-checker` finds insufficient test coverage → add `test-engineer` before `code-simplifier` if not already in this pipeline run, then re-run `code-simplifier` and `code-reviewer` before re-checking
- All acceptance criteria met → `finishing-a-development-branch`

---

### Pipeline 6 — Test-Only

**Use when:** Coverage gaps need to be filled without changing production code, or regression tests need to be added after a bug fix in a separate pass.

**Default pipeline:**
```
test-engineer → code-reviewer
```

**Key rules:**
- `test-engineer` must not modify production code unless absolutely necessary for testability — and must explain why if it does
- `code-reviewer` is required for complex or shared test infrastructure changes; may be skipped for trivial isolated tests

**Useful variants:**
- Add `acceptance-checker` if tests must map to formal acceptance criteria
- Prepend `using-git-worktrees` before `test-engineer` to isolate test changes on a branch
- Insert `context-mapper` before `test-engineer` when the codebase is large — maps existing test files and coverage gaps so `test-engineer` targets the right files

**Exit transitions:**
- `code-reviewer` returns feedback → `receiving-code-review`, re-run `code-reviewer` before closing
- Coverage gaps remain after review → return to `test-engineer` for another pass
- Coverage gaps require production code changes → route to Pipeline 3 (new feature) or Pipeline 4 (bug fix)
- `code-reviewer` returns no blocking issues and all coverage goals are confirmed (when the `acceptance-checker` Variant is not active) → `finishing-a-development-branch`
- `acceptance-checker` confirms all coverage criteria met (when the `acceptance-checker` Variant is active) → `finishing-a-development-branch`

---

### Pipeline 7 — Review-Only

**Use when:** An explicit review of existing code or a pull request is requested, with no implementation change intended.

**Default pipeline:**
```
code-reviewer
```

**Key rules:**
- State the review scope before `code-reviewer` begins
- `code-reviewer` critiques — it does not rewrite unless explicitly asked
- If `acceptance-checker` finds unmet criteria, Pipeline 7 does not implement — route to Pipeline 3 or 4 to address the gaps, then return to Pipeline 7 for a final review pass

**Useful variants:**
- Add `acceptance-checker` if formal acceptance criteria need to be verified against the diff
- Add `test-engineer` if review surfaces missing or insufficient coverage — prepend `using-git-worktrees` since test-engineer produces real file changes
- Add `find-bugs` when the review is security-focused or the diff touches auth, input handling, or external calls — for a full threat-model-led security audit use Pipeline 10 instead
- Insert `context-mapper` before `code-reviewer` when reviewing changes to shared modules — the Reverse Dependents list directly informs regression risk assessment

**Exit transitions:**
- `code-reviewer` returns feedback → `receiving-code-review` to document findings; route to Pipeline 3 or 4 to apply fixes; return to Pipeline 7 for a confirmation review pass — Pipeline 7 does not implement
- `acceptance-checker` finds unmet criteria → Pipeline 3 or 4, then return to Pipeline 7 for final review
- `code-reviewer` returns no blocking issues (and the `acceptance-checker` Variant is not active) → `finishing-a-development-branch`
- `acceptance-checker` confirms all criteria met (when the `acceptance-checker` Variant is active) → `finishing-a-development-branch`

---

### Pipeline 8 — Docs-Only

**Use when:** Documentation needs updating after a code change, or a README, changelog, or API reference is out of date.

**Default pipeline:**
```
docs-updater
```

**Key rules:**
- `docs-updater` must not invent undocumented behavior — document only what shipped
- Scope docs updates to the changes that actually landed

**Useful variants:**
- Add `code-reviewer` if docs describe technically complex or risky behavior that requires accuracy verification

**Exit transitions:**
- `code-reviewer` returns feedback on doc accuracy → `receiving-code-review`, re-run `code-reviewer` to confirm
- Docs complete and no blocking issues → `finishing-a-development-branch`

---

### Pipeline 9 — Performance / Optimization

**Use when:** A feature or component is measurably slow, a performance regression has been introduced, or optimization work is explicitly requested.

**Default pipeline:**
```
performance-profiler → test-engineer → feature-implementer → code-reviewer → acceptance-checker
```

**Key rules:**
- `performance-profiler` establishes a measurable baseline and identifies the concrete hotspot before any code changes begin — the performance analog of "reproduce before fix"
- If `performance-profiler` cannot identify a concrete hotspot (tooling unavailable, environment not representative), stop and resolve the measurement gap — do not proceed on guesswork
- `feature-implementer` addresses one hotspot at a time — do not combine multiple optimizations in a single pass
- `acceptance-checker` validates before/after measurements against the criteria defined by `performance-profiler` — "it feels faster" is not evidence

**Useful variants:**
- Prepend `using-git-worktrees` before `test-engineer` to isolate optimization work on a branch
- Insert `context-mapper` after `performance-profiler` when the hotspot implicates a shared module — maps reverse dependents so optimization does not silently degrade callers
- Skip `test-engineer` if the project has no benchmarking infrastructure and adding it is explicitly out of scope — note the gap
- Append `docs-updater` when performance characteristics are externally documented (SLAs, benchmarks in README)

**Exit transitions:**
- `code-reviewer` returns feedback → `receiving-code-review`; if the fix touches the optimized code path, `test-engineer` re-runs the benchmark; then re-run `code-reviewer` and proceed to `acceptance-checker`
- `acceptance-checker` finds target not met → return to `feature-implementer` for another targeted pass; `test-engineer` re-runs the benchmark to take the new measurement, then `code-reviewer` before re-checking
- `acceptance-checker` finds a regression introduced → return to `feature-implementer` to revert or correct; `test-engineer` re-runs the benchmark to confirm the regression is cleared, then `code-reviewer` before re-checking
- All performance targets met and no regressions introduced → `finishing-a-development-branch`

---

### Pipeline 10 — Security Audit

**Use when:** A security audit is explicitly requested; the change introduces new auth paths, user inputs, external calls, or sensitive data handling; a new dependency is added or upgraded; a pre-release security gate is required.

**Default pipeline:**
```
threat-modeler → dependency-auditor → find-bugs
```

**Key rules:**
- `threat-modeler` maps the attack surface and produces a threat checklist *before* code review begins — `find-bugs` uses this as its investigation context, making security review change-specific rather than generic
- Security audit (Pipeline 10) is separate from functional correctness review (Pipeline 7) — run both independently on the same change; do not conflate them
- `find-bugs` produces findings only — confirmed vulnerabilities exit to Pipeline 4 (bug fix) with the security report as triage input; the security pipeline does not fix
- If `dependency-auditor` has no scanner available for a detected ecosystem, it stops and reports the gap — do not proceed with findings from memory

**Useful variants:**
- Prepend `using-git-worktrees` before `threat-modeler` when remediation findings are expected
- Skip `dependency-auditor` if no dependencies changed and the last audit is recent — document the decision
- Skip `threat-modeler` if the scope is purely dependency-level (no application code changes)
- Append Pipeline 3 or 4 when findings require code remediation
- Append `docs-updater` when findings result in documented security decisions (accepted risk, threat model in ADR)

**Exit transitions:**
- `find-bugs` finds code vulnerabilities → exit to Pipeline 4 for each confirmed finding; the `find-bugs` report serves as triage input for `bug-repro-triager`
- `find-bugs` finds dependency issues → resolve upgrades, re-run `dependency-auditor` to confirm clean, then re-run `find-bugs`
- `find-bugs` finds no actionable issues → close audit; optionally append `docs-updater` to record the clean audit or document accepted risks

---

## 6. Pipeline Flow Diagrams

### Pipeline 0 — Requirements Gathering

```mermaid
graph TD
    classDef startEnd fill:#E8F4FD,stroke:#555
    classDef work fill:#D5E8D4,stroke:#555
    classDef planning fill:#FFF2CC,stroke:#555
    classDef decision fill:#FFF3CD,stroke:#555
    classDef transition fill:#DAE8FC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555

    start([Vague Task / Idea]):::startEnd
    interview[interview<br/>Extract requirements<br/>one question at a time]:::work
    brainstorm[brainstorming<br/>Turn spec into concrete design]:::work
    adr[adr-writer<br/>optional: significant architectural decision]:::optional
    scope[scope-estimator<br/>Size the work]:::planning
    plans[writing-plans<br/>Write implementation plan]:::planning
    decision{Scope decision}:::decision
    p1([Pipeline 1 — Spike/POC]):::transition
    p3_4([Pipeline 3 or 4 — Implementation]):::work
    split([Split into multiple plans]):::optional

    start --> interview
    start -.->|partially specified| brainstorm
    interview --> brainstorm
    brainstorm -.->|significant architectural decision| adr
    adr --> scope
    brainstorm --> scope
    scope --> decision
    decision -->|manageable scope| plans
    decision -->|key unknown exists| p1
    decision -->|XL or low confidence| split
    plans --> p3_4
    split -.->|each plan routes independently| p3_4
```

---

### Pipeline 1 — Spike / POC Investigation

```mermaid
graph TD
    classDef startEnd fill:#DAE8FC,stroke:#555
    classDef research fill:#FFF2CC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef spike fill:#FFE6CC,stroke:#555
    classDef retro fill:#D5E8D4,stroke:#555
    classDef decision fill:#FFF3CD,stroke:#555
    classDef proceed fill:#D5E8D4,stroke:#555
    classDef pivot fill:#FFF2CC,stroke:#555
    classDef abandon fill:#F8CECC,stroke:#555

    start([Unvalidated Assumption<br/>or Feasibility Question]):::startEnd
    research[research<br/>Domain knowledge and context]:::research
    techsel[technology-selector<br/>optional: choosing between options]:::optional
    worktree[using-git-worktrees<br/>optional: spike produces code artifacts]:::optional
    hval[hypothesis-validator<br/>alternative: narrow single assumption]:::optional
    spike[spike-investigator<br/>Throwaway experiments — no TDD]:::spike
    retro[poc-retrospective<br/>Mandatory — capture decision + carry-forwards]:::retro
    sizing[scope-estimator<br/>optional: before committing to plan]:::optional
    adr[adr-writer<br/>optional: architectural commitment]:::optional
    newsession{New Session<br/>start from retrospective}:::decision
    proceed([Proceed → writing-plans]):::proceed
    pivot([Pivot → New spike with refined hypothesis]):::pivot
    abandon([Abandon → Record closed]):::abandon

    start --> research
    research -.->|technology choice| techsel
    research -.->|code artifacts expected| worktree
    research -.->|narrow question| hval
    research --> spike
    techsel --> spike
    worktree --> spike
    hval --> retro
    spike --> retro
    retro -.-> sizing
    retro -->|Proceed| newsession
    retro -.->|architectural commitment| adr
    sizing --> newsession
    adr --> newsession
    newsession --> proceed
    retro -->|Pivot| pivot
    retro -->|Abandon| abandon
```

---

### Pipeline 2 — Unfamiliar API / Library

```mermaid
graph TD
    classDef startEnd fill:#FFF2CC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef research fill:#FFF2CC,stroke:#555
    classDef decision fill:#FFF3CD,stroke:#555
    classDef toP3 fill:#D5E8D4,stroke:#555
    classDef toP1 fill:#DAE8FC,stroke:#555
    classDef toP0 fill:#FFE6CC,stroke:#555

    start([Unknown API / Library / Framework]):::startEnd
    techsel[technology-selector<br/>optional: choosing between named options]:::optional
    researcher[api-researcher<br/>Research behavior, constraints,<br/>version differences, gotchas]:::research
    decision{Findings}:::decision
    adr[adr-writer<br/>optional: significant adoption decision]:::optional
    p3([Pipeline 3 — Feature build<br/>Carry findings into task-planner]):::toP3
    p1([Pipeline 1 — Spike/POC<br/>Hands-on validation needed]):::toP1
    p0([Pipeline 0 — Requirements<br/>Rethink design approach]):::toP0

    start -.->|multiple options under consideration| techsel
    techsel --> researcher
    start --> researcher
    researcher --> decision
    decision -->|clear and viable| p3
    decision -.->|architectural commitment| adr
    adr --> p3
    decision -->|unknown behavior<br/>needs proof-of-concept| p1
    decision -->|fundamentally incompatible| p0
```

---

### Pipeline 3 — New Feature / Behavior Change

```mermaid
graph TD
    classDef startEnd fill:#E8F4FD,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef planning fill:#FFF2CC,stroke:#555
    classDef impl fill:#FFE6CC,stroke:#555
    classDef testing fill:#D5E8D4,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef audit fill:#FFF2CC,stroke:#D6B656
    classDef contract fill:#D5E8F0,stroke:#4A90A4

    start([New Feature Request]):::startEnd
    scope[scope-estimator<br/>optional: if scope unclear]:::optional
    worktree[using-git-worktrees<br/>optional: isolate on branch]:::optional
    plan[task-planner<br/>Define done criteria, steps, risks]:::planning
    iface[interface-designer<br/>optional: public API or shared boundary]:::contract
    mapper[context-mapper<br/>optional: shared module / large codebase]:::optional
    impl[feature-implementer<br/>Minimal diff — one step at a time]:::impl
    test[test-engineer<br/>Write tests before merge]:::testing
    dep_audit[dependency-auditor<br/>optional: if packages added or changed]:::audit
    review[code-reviewer<br/>Correctness, regressions, standards]:::review
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    accept[acceptance-checker<br/>Map evidence to criteria]:::testing
    docs[docs-updater<br/>optional: if public behavior changed]:::feedback
    finish[finishing-a-development-branch]:::optional
    done([Done]):::startEnd

    start -.-> scope & worktree
    start --> plan
    scope --> plan
    worktree --> plan
    plan -.-> iface
    iface -.-> mapper
    iface --> impl
    plan -.-> mapper
    mapper --> impl
    plan --> impl
    impl --> test
    test -.-> dep_audit
    dep_audit --> review
    test --> review
    review -.->|has feedback| rcr
    rcr -.->|fix → re-test → re-review| impl
    review -.->|contract incorrect| iface
    accept -.->|contract incorrect| iface
    review -->|no blocking issues| accept
    accept -.->|missing implementation| impl
    accept -.->|missing coverage| test
    accept -.->|optional| docs
    accept -->|all criteria met| finish
    docs --> finish
    finish --> done
```

---

### Pipeline 4 — Bug Fix / Runtime Failure

```mermaid
graph TD
    classDef startEnd fill:#F8CECC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef triage fill:#FFE6CC,stroke:#555
    classDef testing fill:#D5E8D4,stroke:#555
    classDef impl fill:#FFE6CC,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555
    classDef audit fill:#FFF2CC,stroke:#D6B656
    classDef contract fill:#D5E8F0,stroke:#4A90A4

    start([Bug Report / Stack Trace<br/>Runtime Failure]):::startEnd
    parallel[dispatching-parallel-agents<br/>optional: 3+ independent failures]:::optional
    triage[bug-repro-triager<br/>Reproduce, hypothesize, plan]:::triage
    iface[interface-designer<br/>optional: contract itself is incorrect]:::contract
    mapper[context-mapper<br/>optional: shared module / large codebase]:::optional
    worktree[using-git-worktrees<br/>optional: isolate fix on branch]:::optional
    test[test-engineer<br/>Write FAILING regression test first]:::testing
    impl[feature-implementer<br/>Minimal fix only]:::impl
    dep_audit[dependency-auditor<br/>optional: if packages added or changed]:::audit
    review[code-reviewer<br/>Correctness, regressions, standards]:::review
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    accept[acceptance-checker<br/>Confirm regression closed]:::testing
    finish[finishing-a-development-branch]:::optional
    done([Done]):::done

    start -.->|3+ independent failures| parallel
    start --> triage
    parallel --> triage
    triage -.->|contract incorrect| iface
    triage -.-> mapper & worktree
    iface --> test
    mapper --> test
    worktree --> test
    triage --> test
    test --> impl
    impl -.-> dep_audit
    dep_audit --> review
    impl --> review
    review -.->|has feedback| rcr
    rcr -.->|fix → re-test → re-review| impl
    review -->|no blocking issues| accept
    accept -.->|missing implementation| impl
    accept -.->|missing coverage| test
    accept -->|all criteria met| finish
    finish --> done
```

---

### Pipeline 5 — Refactor / Simplification

```mermaid
graph TD
    classDef startEnd fill:#E8F4FD,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef planning fill:#FFF2CC,stroke:#555
    classDef simplify fill:#E1D5E7,stroke:#555
    classDef testing fill:#D5E8D4,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555
    classDef contract fill:#D5E8F0,stroke:#4A90A4

    start([Refactor / Cleanup Request]):::startEnd
    worktree[using-git-worktrees<br/>optional: isolate on branch]:::optional
    plan[task-planner<br/>Define scope — what must not change]:::planning
    mapper[context-mapper<br/>optional: shared module]:::optional
    pretest[test-engineer<br/>optional: if coverage insufficient]:::testing
    simplify[code-simplifier<br/>Clarity and consistency<br/>no behavior change]:::simplify
    review[code-reviewer<br/>Verify no regressions]:::review
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    accept[acceptance-checker<br/>Confirm behavior preserved]:::testing
    iface[interface-designer<br/>optional: public surface changed]:::contract
    finish[finishing-a-development-branch]:::optional
    done([Done]):::done

    start -.-> worktree
    start --> plan
    worktree --> plan
    plan -.-> mapper
    plan -.->|coverage insufficient| pretest
    mapper --> simplify
    pretest --> simplify
    plan --> simplify
    simplify --> review
    review -.->|has feedback| rcr
    rcr -.->|fix → re-review| simplify
    review -->|no blocking issues| accept
    accept -.->|altered behavior| simplify
    accept -.->|insufficient coverage| pretest
    accept -.->|surface changed| iface
    accept -->|behavior preserved| finish
    iface --> finish
    finish --> done
```

---

### Pipeline 6 — Test-Only

```mermaid
graph TD
    classDef startEnd fill:#D5E8D4,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef testing fill:#D5E8D4,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef decision fill:#FFF3CD,stroke:#555
    classDef escalate fill:#FFE6CC,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555

    start([Coverage Gap / Test Request]):::startEnd
    worktree[using-git-worktrees<br/>optional: isolate on branch]:::optional
    mapper[context-mapper<br/>optional: large codebase]:::optional
    engineer[test-engineer<br/>Write / update tests<br/>No production code changes]:::testing
    review[code-reviewer<br/>Required for shared test infrastructure]:::review
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    decision{Coverage goals met?}:::decision
    accept[acceptance-checker<br/>optional: formal criteria]:::testing
    escalate([Pipeline 3 or 4<br/>production change needed]):::escalate
    finish[finishing-a-development-branch]:::optional
    done([Done]):::done

    start -.-> worktree & mapper
    worktree --> engineer
    mapper --> engineer
    start --> engineer
    engineer --> review
    review -.->|has feedback| rcr
    rcr -.->|fix → re-review| engineer
    review -->|no blocking issues| decision
    decision -->|gaps remain| engineer
    decision -->|production change needed| escalate
    decision -.->|formal criteria| accept
    decision -->|all goals met| finish
    accept -->|criteria met| finish
    accept -.->|criteria gap| engineer
    finish --> done
```

---

### Pipeline 7 — Review-Only

```mermaid
graph TD
    classDef startEnd fill:#DAE8FC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef security fill:#FFE6CC,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef testing fill:#D5E8D4,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef escalate fill:#FFE6CC,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555

    start([Review Request / Pull Request]):::startEnd
    mapper[context-mapper<br/>optional: shared module review]:::optional
    bugs[find-bugs<br/>optional: security-focused review]:::security
    review[code-reviewer<br/>Correctness, regressions<br/>standards, test adequacy]:::review
    accept[acceptance-checker<br/>optional: formal criteria]:::testing
    tests[test-engineer<br/>optional: coverage gaps surfaced]:::testing
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    escalate([Pipeline 3 or 4 — apply fixes<br/>then return to Pipeline 7 for confirmation review]):::escalate
    finish[finishing-a-development-branch]:::optional
    done([Done]):::done

    start -.-> mapper
    start -.->|security focused| bugs
    mapper --> review
    bugs --> review
    start --> review
    review -.->|formal criteria| accept
    review -.->|coverage gaps found| tests
    review -.->|has feedback| rcr
    rcr --> escalate
    tests --> review
    accept -.->|unmet criteria| escalate
    accept -->|criteria met| finish
    review -->|no blocking issues / all criteria met| finish
    finish --> done
```

---

### Pipeline 8 — Docs-Only

```mermaid
graph TD
    classDef startEnd fill:#F8CECC,stroke:#555
    classDef docs fill:#F8CECC,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555

    start([Docs Update Request<br/>Changelog / README]):::startEnd
    updater[docs-updater<br/>Update docs to match what actually shipped]:::docs
    review[code-reviewer<br/>optional: complex or risky behavior described]:::review
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    finish[finishing-a-development-branch]:::optional
    done([Done]):::done

    start --> updater
    updater -.->|complex behavior described| review
    updater -->|no review needed| finish
    review -.->|has feedback| rcr
    rcr -.->|fix → re-review| updater
    review -->|no blocking issues| finish
    finish --> done
```

---

### Pipeline 9 — Performance / Optimization

```mermaid
graph TD
    classDef startEnd fill:#FFD6E7,stroke:#555
    classDef profiler fill:#FFD6E7,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef impl fill:#FFE6CC,stroke:#555
    classDef testing fill:#D5E8D4,stroke:#555
    classDef review fill:#DAE8FC,stroke:#555
    classDef feedback fill:#F8CECC,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555

    start([Performance Concern<br/>Slow Feature / Regression / Target]):::startEnd
    worktree[using-git-worktrees<br/>optional: isolate on branch]:::optional
    profiler[performance-profiler<br/>Establish baseline — identify hotspot<br/>Define acceptance criteria]:::profiler
    mapper[context-mapper<br/>optional: shared module hotspot]:::optional
    impl[feature-implementer<br/>One targeted optimization at a time]:::impl
    test[test-engineer<br/>Write failing benchmark<br/>codifying the acceptance criteria]:::testing
    review[code-reviewer<br/>Correctness, regressions, standards]:::review
    rcr[receiving-code-review<br/>if reviewer returns feedback]:::feedback
    accept[acceptance-checker<br/>Validate before/after metrics<br/>against profiler criteria]:::testing
    docs[docs-updater<br/>optional: if SLAs or benchmarks documented]:::feedback
    finish[finishing-a-development-branch]:::optional
    done([Done]):::done

    start -.-> worktree
    start --> profiler
    worktree --> profiler
    profiler -.-> mapper
    mapper --> test
    profiler --> test
    test --> impl
    impl --> review
    review -.->|has feedback| rcr
    rcr -.->|fix → re-test → re-review| impl
    review -->|no blocking issues| accept
    accept -.->|target not met → optimize → re-benchmark → re-review| impl
    accept -.->|regression → revert → re-benchmark → re-review| impl
    accept -.->|optional| docs
    accept -->|targets met, no regressions| finish
    docs --> finish
    finish --> done
```

---

### Pipeline 10 — Security Audit

```mermaid
graph TD
    classDef startEnd fill:#F4CCCC,stroke:#555
    classDef threat fill:#F4CCCC,stroke:#555
    classDef audit fill:#FCE5CD,stroke:#555
    classDef review fill:#EAD1DC,stroke:#555
    classDef optional fill:#E1D5E7,stroke:#555
    classDef fix fill:#FFE6CC,stroke:#555
    classDef done fill:#E8F4FD,stroke:#555

    start([Security Audit Requested<br/>or Change Introduces Security Surface]):::startEnd
    worktree[using-git-worktrees<br/>optional: if remediation expected]:::optional
    tm[threat-modeler<br/>Map attack surface<br/>Produce threat checklist]:::threat
    da[dependency-auditor<br/>Run npm / pip / cargo audit<br/>Flag CVEs + license issues]:::audit
    fb[find-bugs<br/>Code security review<br/>Using threat checklist as context]:::review
    p4[Pipeline 4 — Bug Fix<br/>optional: for confirmed vulnerabilities]:::fix
    dep_rerun[dependency-auditor re-run<br/>after upgrades applied]:::audit
    docs[docs-updater<br/>optional: record decisions / clean audit]:::optional
    done([Done]):::done

    start -.-> worktree
    start --> tm
    worktree --> tm
    tm --> da
    da --> fb
    fb -.->|vulnerability confirmed| p4
    fb -.->|dep upgrade needed| dep_rerun
    fb -.->|optional: record audit| docs
    fb -->|no actionable issues| done
    dep_rerun --> fb
    p4 --> done
    docs --> done
```

---

## 7. Usage Examples

### Example 1: "I have an idea for a new feature"

The task is vague — requirements are not written down.

**What Devflow does:**

```
Selected worker agents: interview → brainstorming → scope-estimator → writing-plans
Reason: requirements undefined — spec and design must be established before any planning or coding (pipeline 0)
Current agent: interview
```

`interview` asks questions one at a time to produce a written spec. `brainstorming` turns it into a concrete design. `scope-estimator` checks if the scope is manageable before opening a plan.

---

### Example 2: "Can we use WebSockets for real-time updates before we commit to it?"

A feasibility question before committing to a technical approach.

**What Devflow does:**

```
Selected worker agents: research → spike-investigator → poc-retrospective
Reason: unvalidated feasibility assumption — validate before committing to a plan (pipeline 1)
Current agent: research
```

`research` gathers context on WebSocket behavior, browser support, and integration patterns. `spike-investigator` runs a throwaway proof-of-concept. `poc-retrospective` captures the decision (Proceed / Pivot / Abandon) and carry-forwards for the production implementation.

**Critical discipline enforced:** Production implementation starts in a **new session** from the retrospective — spike-mode context is not carried forward.

---

### Example 3: "We're integrating Stripe for the first time"

Unfamiliar external API — research before building.

**What Devflow does:**

```
Selected worker agents: api-researcher
Reason: unfamiliar external API — research gate before planning (pipeline 2)
Current agent: api-researcher
```

`api-researcher` investigates Stripe's relevant endpoints, authentication patterns, webhook behavior, and version-specific gotchas. When findings are clear, they are carried explicitly into `task-planner` at the start of Pipeline 3 — no implementation begins until the research gate is passed.

---

### Example 4: "Add pagination to the users list"

A well-understood feature request — plan, build, test, verify.

**What Devflow does:**

```
Selected worker agents: task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker
Reason: new behavior change with regression risk (pipeline 3)
Current agent: task-planner
```

`task-planner` defines done criteria, identifies files likely to change, and writes the implementation steps. `feature-implementer` makes the minimal diff. `test-engineer` covers the new behavior and edge cases. `code-reviewer` checks for regressions. `acceptance-checker` maps evidence to the stated criteria before the branch is closed.

---

### Example 5: "Fix this stack trace"

A bug report with a stack trace.

**What Devflow does:**

```
Selected worker agents: bug-repro-triager → test-engineer → feature-implementer → code-reviewer → acceptance-checker
Reason: runtime failure — reproduce and regression-cover before fixing (pipeline 4)
Current agent: bug-repro-triager
```

`bug-repro-triager` confirms the reproduction steps and root cause hypothesis. `test-engineer` writes a failing regression test. `feature-implementer` applies the minimal fix. `code-reviewer` checks correctness. `acceptance-checker` confirms the regression is closed.

**Critical discipline enforced:** The fix is never applied before the failure is reproduced and a failing test is written.

---

### Example 6: "This module has gotten hard to read — clean it up without changing behavior"

Refactor request — structure improvement, no behavior change.

**What Devflow does:**

```
Selected worker agents: task-planner → code-simplifier → code-reviewer → acceptance-checker
Reason: code structure improvement without behavior change (pipeline 5)
Current agent: task-planner
```

`task-planner` defines what "clean" means and what must not change. `code-simplifier` applies targeted clarity improvements. `acceptance-checker` confirms that external behavior is preserved — not improved or extended.

---

### Example 7: "We merged the auth fix but never added regression tests"

Retroactive test coverage for a landed fix.

**What Devflow does:**

```
Selected worker agents: test-engineer → code-reviewer
Reason: explicit test-only request — no production code change intended (pipeline 6)
Current agent: test-engineer
```

`test-engineer` writes regression tests scoped to the auth fix. `code-reviewer` checks test quality and ensures they actually cover the failure path. No production code is touched.

---

### Example 8: "Can you review these recent changes?"

Explicit review request — evaluation only, no implementation.

**What Devflow does:**

```
Selected worker agents: code-reviewer
Reason: explicit review request, no implementation intended (pipeline 7)
Current agent: code-reviewer
```

`code-reviewer` checks correctness, regressions, standards, and test adequacy. If feedback requires fixes, `receiving-code-review` processes it and `code-reviewer` re-runs to confirm resolution before closing.

---

### Example 9: "Update the README to reflect the new config options we shipped"

Documentation update scoped to a recent code change.

**What Devflow does:**

```
Selected worker agents: docs-updater
Reason: documentation update scoped to recent code changes — no implementation intended (pipeline 8)
Current agent: docs-updater
```

`docs-updater` reads the recent changes and updates only the documentation affected by them — no broad rewrites, no invented behavior.

---

### Example 10: "The checkout flow is too slow — can you optimize it?"

A performance concern with no confirmed root cause yet.

**What Devflow does:**

```
Selected worker agents: performance-profiler → test-engineer → feature-implementer → code-reviewer → acceptance-checker
Reason: performance optimization — profile first, write failing benchmark to codify criteria, then optimize (pipeline 9)
Current agent: performance-profiler
```

`performance-profiler` runs profiling against the checkout flow, captures baseline metrics (e.g., p95 latency: 2,100ms), and identifies the actual hotspot — not the assumed one. In this case, the profiler discovers an N+1 query in the cart loading logic, not the payment gateway call that was suspected. It defines the acceptance criteria: "p95 latency ≤ 300ms under the same load conditions." `test-engineer` writes a failing benchmark test that codifies those criteria in executable form — the test asserts p95 ≤ 300ms and fails immediately against the unoptimized baseline, establishing a concrete RED state before any production code changes. `feature-implementer` targets the N+1 query specifically, implementing the fix until the benchmark turns GREEN. `acceptance-checker` validates the before/after numbers against the profiler's criteria.

**Critical discipline enforced:** No code is changed until the hotspot is confirmed by measurement. The suspected bottleneck is never assumed to be the real one.

---

### Example 11: "Three test files are failing in unrelated subsystems"

Multiple independent failures — parallel dispatch.

**What Devflow does:**

```
Selected worker agents: dispatching-parallel-agents → bug-repro-triager (×3) → test-engineer → feature-implementer → code-reviewer → acceptance-checker
Reason: 3 independent failures in different subsystems — parallel dispatch saves time (pipeline 4 + parallel variant)
Current agent: dispatching-parallel-agents
```

`dispatching-parallel-agents` splits the three failures into independent tracks: one `bug-repro-triager` per domain runs simultaneously instead of sequentially — one for the auth subsystem, one for the payment queue, one for the notification service. Each produces its own reproduction steps and root-cause hypothesis without waiting for the others.

Once all three triagers complete, `test-engineer` writes a failing regression test for each confirmed failure — three separate tests, one per domain, each pinning the exact broken behavior before any fix is applied. `feature-implementer` then applies three minimal, targeted fixes. Before integrating them, the fixes are reviewed together for conflicts (e.g. a shared utility changed by two independent fixes). `code-reviewer` evaluates correctness, regression risk, and whether the fixes interact. `acceptance-checker` confirms all three regressions are closed and no new failures were introduced.

**Critical discipline enforced:** The three failures are investigated in parallel but converge at a single review and acceptance gate — not three separate merges that skip cross-fix conflict review.

---

### Example 12: "We're about to ship the new payment flow — run a security audit"

A pre-release security gate on a change that introduces auth, external calls, and sensitive data handling.

**What Devflow does:**

```
Selected worker agents: threat-modeler → dependency-auditor → find-bugs
Reason: pre-release security gate on a change introducing auth paths, external API calls, and PII handling (pipeline 10)
Current agent: threat-modeler
```

`threat-modeler` reads the diff, maps the attack surface (new `/checkout` endpoint with user input, Stripe API call, PII stored to database), and produces a threat checklist with 4 applicable threats ranked: IDOR on order IDs (High), missing CSRF on the checkout form (High), secrets in error logs (Medium), and rate-limiting gap (Low). `dependency-auditor` runs `npm audit` and finds one High-severity CVE in a transitive dependency of the Stripe SDK — a fix version exists. `find-bugs` uses both reports as context: it confirms the IDOR by tracing the order lookup, confirms the CSRF gap, and flags two call sites that could log the API key.

**Critical discipline enforced:** Security review is separate from the functional code review (Pipeline 7) that ran on this same change. Security findings exit to Pipeline 4 — `find-bugs` reports, not fixes. The dependency CVE gets its own upgrade commit, then `dependency-auditor` re-runs to confirm clean before closing the audit.

---

### Example 13: "We need to decide between PostgreSQL and MongoDB for the new service"

A technology choice between named alternatives before any implementation plan is written.

**What Devflow does:**

```
Selected worker agents: technology-selector → adr-writer → writing-plans
Reason: technology choice between named alternatives with architectural consequences — decision must be documented before planning begins (pipeline 0 + adr-writer variant)
Current agent: technology-selector
```

`technology-selector` evaluates PostgreSQL vs MongoDB against the stated requirements (strong consistency needed, relational data model, team SQL experience) and produces a structured recommendation: PostgreSQL, with reasoning and the conditions that would change it. `adr-writer` immediately follows — it reads the recommendation from context and writes `docs/decisions/0001-use-postgresql-for-order-service.md`, recording the decision, both options, the rationale, the trade-offs accepted (schema migration overhead), and the conditions for revisiting (if the data model becomes document-shaped or horizontal scale requirements change). `writing-plans` then opens with the ADR already committed — the plan references it rather than re-arguing the choice.

**Critical discipline enforced:** The decision is recorded *before* implementation begins — not reconstructed after the fact. Three months later, when someone asks "why PostgreSQL?", the answer is in the repository with full context, not lost in a chat history or a team member's memory.

---

### Example 14: "Add the Stripe package and implement payment processing"

A new feature that introduces an external dependency — the dependency-auditor Variant in Pipeline 3.

**What Devflow does:**

```
Selected worker agents: task-planner → feature-implementer → test-engineer → dependency-auditor → code-reviewer → acceptance-checker
Reason: new feature that introduces an external package — audit newly added dependencies before code review (pipeline 3 + dependency-auditor variant)
Current agent: task-planner
```

`task-planner` produces an implementation plan with Stripe integration steps, done criteria, and risks. `feature-implementer` adds the `stripe` package to `package.json` and implements the payment processing logic. `test-engineer` writes integration tests, potentially adding `stripe-mock` as a dev dependency. `dependency-auditor` now activates — it detects two manifest changes (`package.json` with `stripe` added, dev dependency `stripe-mock` added) and runs `npm audit`. It reports: no CVEs on `stripe` at the pinned version; `stripe-mock` has one Low advisory (no fix needed); license is MIT for both — no conflict. Handoff to `code-reviewer`: "no blocking findings — proceed; note the Low advisory on stripe-mock is acknowledged". `code-reviewer` and `acceptance-checker` complete normally.

If instead `npm audit` had returned a High CVE on a transitive dependency of `stripe`, `dependency-auditor` would report: "**Recommend escalating to Pipeline 10 before merging** — `axios@1.2.0` (transitive via `stripe`) has CVE-YYYY-NNNN, CVSS 7.5, fixed in `axios@1.4.0`". The team decides: either upgrade the pin and re-run, or proceed to Pipeline 10 for a full threat model before the PR is merged.

**Critical discipline enforced:** Third-party risk is caught at the point of introduction — not discovered weeks later in a periodic audit or, worse, post-incident.

---

### Example 15: "Add a user search endpoint to the REST API"

A new public REST endpoint consumed by a frontend client — the interface-designer Variant in Pipeline 3.

**What Devflow does:**

```
Selected worker agents: task-planner → interface-designer → feature-implementer → test-engineer → code-reviewer → acceptance-checker
Reason: new REST endpoint with external consumers — define the contract before implementation so caller and implementer agree on the shape before any code is written (pipeline 3 + interface-designer variant)
Current agent: task-planner
```

`task-planner` produces a plan: add `GET /users/search?q=<query>` with pagination, returning a list of matching users. `interface-designer` activates — it reads the plan, finds `openapi.yaml` in the project root, detects REST context, and produces an updated OpenAPI 3.x YAML saved to `docs/interfaces/users-api.yaml`. The spec defines the `q` query parameter (required, min 2 chars), the `page` and `limit` parameters, the `UserSummary` response schema (id, name, email, avatarUrl), and three error responses: `400 Bad Request` (query too short), `401 Unauthorized` (unauthenticated), `500 Internal Server Error`. It also notes: "BREAKING CHANGE: none — this is a new endpoint with no existing callers."

`feature-implementer` receives the handoff: "implement against `docs/interfaces/users-api.yaml` exactly — any added field, changed type, or removed error case requires updating the contract first." The backend engineer implements the search endpoint, the full-text query, and the pagination logic. `test-engineer` derives contract tests from the spec — one test per documented error case, plus a happy-path test verifying the response schema matches. `code-reviewer` checks that the implementation response shape matches the OpenAPI schema exactly.

**Critical discipline enforced:** The frontend team can begin mocking the API against the OpenAPI spec the moment `interface-designer` finishes — before `feature-implementer` writes a single line. No integration surprise at PR time.

**TDD-first variant:** When the project follows strict TDD, the pipeline reorders to `task-planner → interface-designer → test-engineer → feature-implementer → code-reviewer → acceptance-checker`. `test-engineer` writes all contract compliance tests in RED phase — one per endpoint, one per documented error case — before `feature-implementer` writes a single line. The contract provides complete test specifications immediately, making test-first fully practical. `feature-implementer` then implements to GREEN against the already-written tests.

---

### Example 16: "We ran out of time — let's pick this up tomorrow"

A multi-session scenario: a bug fix is partially done at the end of one working session and must resume cleanly the next day. This example shows `session-continuity` in both write mode (end of session) and read mode (start of next session).

> **Important:** `session-continuity` is always invoked **manually** by the user as a slash command (`/session-continuity`). It is a skill, not a routed agent — the router never dispatches it automatically. The instruction "Use devflow:session-continuity at session boundaries" that appears in every pipeline's Notes is a reminder to the **human** to remember to invoke it at the right moment. See also Section 11 (Limitations): *"It does not manage long context automatically. For very long sessions, use session-continuity manually at session boundaries to preserve state."*

#### End of Session — Write Mode

The team has been working on Pipeline 4 (Bug fix). `bug-repro-triager` confirmed the root cause, `test-engineer` wrote a failing regression test, and `feature-implementer` is mid-fix — one file changed, one still to go. The session must close.

The developer invokes the skill directly — no routing step, no agent selection:

```
You: /session-continuity
```

`session-continuity` activates in write mode, reads the current session context, and produces a snapshot file at `docs/sessions/2026-05-01-14-30-auth-token-bug.md`:

```markdown
# Session Snapshot: Auth token expiry bug fix

**Date:** 2026-05-01
**Status:** In Progress
**Next action:** Open `src/auth/token-validator.ts` and apply the same
null-guard fix as in `src/auth/session-handler.ts` — the root cause
is an unguarded `user.token.expiresAt` access when the token object
is present but its `expiresAt` field is null (populated lazily by the
legacy API).

## Goal

Fix the NullReferenceError crash in the auth token validation path that
affects users logging in via legacy SSO providers.

## Current State

Regression test is written and failing (RED confirmed).
Fix applied to `src/auth/session-handler.ts` — tests now pass for that file.
`src/auth/token-validator.ts` has the same pattern and needs the same fix.

## Decisions Made

| Decision | Reasoning | Alternatives Ruled Out |
|---|---|---|
| Null-guard at access site, not at ingestion | Legacy API contract cannot be changed; callers must be defensive | Fixing the API to always populate expiresAt — would require coordinating with the legacy team and a separate release |
| One fix per file, not a shared utility | The pattern is simple enough that a utility adds abstraction without payoff | Extracted helper — rejected; adds indirection for a one-liner |

## Work Completed

- [x] Root cause confirmed: `user.token.expiresAt` is null for legacy SSO tokens
- [x] Regression test written: `auth/token-expiry.test.ts` line 44 — fails correctly
- [x] Fix applied to `src/auth/session-handler.ts`

## Work Remaining

- [ ] Apply same null-guard fix to `src/auth/token-validator.ts`
- [ ] Run full test suite to confirm no regressions
- [ ] `code-reviewer` pass
- [ ] `acceptance-checker` pass

## Open Questions

None — root cause is confirmed, fix approach is decided.

## Context for Resumption

- Read `src/auth/session-handler.ts` lines 78–85 to see the fix pattern before touching `token-validator.ts`
- The regression test is in `src/auth/__tests__/token-expiry.test.ts`
- Do NOT touch `src/auth/token-ingestion.ts` — the root cause is in the validation path, not ingestion
- Branch: `fix/auth-token-null-expiry` — one commit already on this branch

## Related Artifacts

| Type | Location | Notes |
|---|---|---|
| Bug repro | `docs/sessions/2026-05-01-14-30-auth-token-bug.md` | This file |
| Regression test | `src/auth/__tests__/token-expiry.test.ts` | Written in RED state |
```

---

#### Start of Next Session — Read Mode

The next day, a new Claude Code session opens on the same project. Before invoking the router or doing any development work, the developer invokes the skill directly:

```
You: /session-continuity
```

`session-continuity` activates in read mode — it scans `docs/sessions/`, finds `2026-05-01-14-30-auth-token-bug.md`, and outputs an orientation before any work begins:

```
Session snapshot found: Auth token expiry bug fix (2026-05-01)

Goal:     Fix NullReferenceError crash in auth token validation path (legacy SSO users)
Status:   In Progress
Branch:   fix/auth-token-null-expiry — verified, one commit present ✓
Test:     src/auth/__tests__/token-expiry.test.ts — verified, failing correctly ✓

Next action: Apply null-guard fix to src/auth/token-validator.ts (same pattern
as session-handler.ts lines 78–85 — read that first)

Blockers: None

Do not touch: src/auth/token-ingestion.ts (root cause is in validation, not ingestion)

Ready to continue. Confirm or update before proceeding?
```

The team confirms. Work resumes from the exact stopping point — no re-reading of files to rediscover context, no relitigating the null-guard decision, no wondering which files are already fixed.

**Routing continues as if the session never ended:**

```
Selected worker agents: feature-implementer → code-reviewer → acceptance-checker
Reason: bug fix in progress — repro confirmed, test written, fix partially applied;
resuming at feature-implementer (pipeline 4, mid-pipeline resume)
Current agent: feature-implementer
```

---

**Critical discipline enforced:** The "Decisions Made" section is what makes the snapshot valuable. Without it, the next session re-opens the question of whether to fix the API ingestion path or the validation path — spending 15 minutes rediscovering a decision that was already made with reasoning. The snapshot is written while context is active, not reconstructed from memory after the session closes.

**When to invoke:** Any pipeline that spans more than one session — P0 (requirements evolve over days), P1 (spikes that need multiple experiment rounds), P4 (bugs with unclear root cause), P9 (performance work with profiling runs spread across sessions). Every pipeline's Notes section contains the reminder "Use devflow:session-continuity at session boundaries" — this is a prompt to the human, not an automated trigger. The human must type `/session-continuity` at each boundary.

---

## 8. Installation — Claude Code

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- Bash or a compatible shell

### Step 1: Copy Skills

```bash
cp -r skills/* ~/.claude/skills/
```

### Step 2: Copy Agents

```bash
cp -r agents/* ~/.claude/agents/
```

### Step 3: Configure the Router

Add the routing instruction to your `~/.claude/CLAUDE.md` (create it if it does not exist):

```markdown
For EVERY task — no exceptions — invoke the `using-devflow` skill before doing any work.
```

This single line is what activates Devflow. Without it, Claude Code will not automatically apply the router.

### Step 4: Verify

Start a new Claude Code session and give a task. You should see the routing announcement before any work begins:

```
Selected worker agents: ...
Reason: ...
Current agent: ...
```

If you do not see this, check that `~/.claude/CLAUDE.md` contains the routing instruction and that the skills directory is correctly populated.

### Optional: Project-Specific Configuration

Add a `CLAUDE.md` in any project directory to enable Devflow for that project specifically:

```markdown
For EVERY task — no exceptions — invoke the `using-devflow` skill before doing any work.
```

This scopes Devflow to that project without affecting global behavior.

---

## 9. Installation — Other AI Tools

Devflow's pipeline discipline and worker roles are model-agnostic. The routing logic, structured output formats, and eleven-pipeline structure all transfer to any AI coding assistant. What differs is how each tool loads instructions and whether it supports automatic agent dispatch.

### What Transfers and What Doesn't

| Feature | Claude Code | Other AI tools |
|---|---|---|
| Pipeline structure and discipline | ✅ Native | ✅ Fully portable |
| Worker self-identification headers | ✅ Native | ✅ Fully portable |
| Structured output formats | ✅ Native | ✅ Fully portable |
| Routing logic (`using-devflow`) | ✅ Auto-loaded via `CLAUDE.md` | ⚠️ Must be loaded via tool-specific mechanism |
| Agent files (`.agent.md`) | ✅ Auto-dispatched | ❌ Must be inlined or pasted manually |
| Slash commands (`/skill-name`) | ✅ Native | ❌ Manual invocation only |
| Per-agent model selection | ✅ Enforced via `model:` frontmatter | ❌ Single model for all roles |
| Per-agent tool restrictions | ✅ Enforced via `tools:` frontmatter | ❌ All tools available to all roles |

### Step 1: Load the Router

The routing skill (`using-devflow/SKILL.md`) must be loaded into the AI's context at the start of every session. Each tool has its own mechanism:

| Tool | Instruction file / mechanism |
|---|---|
| **Cursor** | `.cursor/rules/devflow.mdc` or `.cursorrules` |
| **GitHub Copilot** | `.github/copilot-instructions.md` |
| **Windsurf** | `.windsurfrules` |
| **Aider** | `--system-prompt devflow-system.md` flag or `.aider.system.md` |
| **Continue** | `systemMessage` field in `.continue/config.json` |
| **Any tool with a system prompt** | Paste `using-devflow/SKILL.md` content into the system prompt field |

Copy the full content of `devflow/skills/using-devflow/SKILL.md` into the appropriate file for your tool. This gives the AI the routing logic, pipeline definitions, and worker discipline rules — without needing slash commands.

### Step 2: Make Agent Definitions Available

Without native agent dispatch, worker definitions must reach the AI another way. Choose one of two strategies based on your workflow:

---

**Strategy A — Full Inline (simpler, higher token cost)**

Append all agent definitions to the same instruction file as the router. The AI always has all worker roles in context and can switch between them automatically when the pipeline advances.

Create a single combined file:

```
devflow-system.md
├── [content of using-devflow/SKILL.md]
├── --- WORKER DEFINITIONS ---
├── [content of agents/task-planner.agent.md]
├── [content of agents/feature-implementer.agent.md]
├── [content of agents/test-engineer.agent.md]
├── [content of agents/code-reviewer.agent.md]
├── [content of agents/acceptance-checker.agent.md]
└── ... remaining agents
```

Load this combined file via your tool's instruction mechanism. Remove the YAML frontmatter from each agent file before merging — the `name:`, `model:`, `tools:`, and `framework:` fields are Claude Code-specific and will just add noise.

**Pros:** Zero manual work per session. The AI always knows all roles.
**Cons:** Significant token cost on every request. May exceed context limits for smaller models.

---

**Strategy B — On-Demand Pasting (leaner, more deliberate)**

Keep `using-devflow/SKILL.md` as the only always-loaded content. Keep individual agent files as reference documents. When a pipeline step begins, paste the relevant agent's content directly into the chat.

```
You are now acting as task-planner. Follow these rules exactly:

[paste content of agents/task-planner.agent.md here, without YAML frontmatter]
```

When the pipeline transitions to the next worker:

```
task-planner is complete. You are now acting as feature-implementer.

[paste content of agents/feature-implementer.agent.md]
```

**Pros:** Lean context — only the active worker is loaded. Works well within tight token budgets.
**Cons:** Requires manual pasting at each pipeline transition. More deliberate but also more visible.

---

### Step 3: Activate a Pipeline

Without slash commands, trigger the router explicitly at the start of every task:

```
New task: [describe the task here]

Please apply using-devflow now: select the correct pipeline, announce the worker sequence,
and begin with the first worker.
```

The AI will output the routing announcement using the rules it loaded in Step 1:

```
Selected worker agents: task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker
Reason: new behavior change with regression risk (pipeline 3)
Current agent: task-planner
```

### Step 4: Advance Through the Pipeline

At each transition point, prompt the AI to move to the next worker:

```
task-planner output looks good. Move to feature-implementer now.
```

Or, if using Strategy A (all agents inline), the AI can advance automatically — just confirm the transition:

```
Proceed to the next pipeline step.
```

### What Is Lost Without Native Agent Support

| Capability | Impact |
|---|---|
| **Per-agent model tiering** | All roles run on the same model. `task-planner` and `docs-updater` both use the same model rather than Opus and Haiku respectively. |
| **Automatic agent dispatch** | Pipeline transitions require an explicit prompt or manual paste. The AI will not advance unprompted. |
| **Per-agent tool restrictions** | A `test-engineer` can technically modify production files — role discipline is behavioral only, not enforced by the tool. |
| **Slash command invocation** | No `/using-devflow` shortcut. The router must be triggered by natural language. |

### Minimal Example: Cursor

Create `.cursor/rules/devflow.mdc`:

```markdown
---
alwaysApply: true
---

[paste full content of devflow/skills/using-devflow/SKILL.md here]

---

## WORKER DEFINITIONS

[paste agent definitions here, without YAML frontmatter — or use Strategy B and paste on demand]
```

For Strategy B, keep individual agent files in a `devflow/agents/` folder in the project and paste them into the Cursor chat at each pipeline step.

---

## 10. Creating New Skills and Agents

### Creating a New Skill

Devflow uses **Test-Driven Development for skills** (via `writing-skills`). The process mirrors RED-GREEN-REFACTOR:

1. **RED** — Write a pressure test: a scenario where an agent violates the rule you want to enforce, before the skill exists. Document the exact rationalization it uses to skip the discipline.
2. **GREEN** — Write the skill (`SKILL.md`) that addresses those specific violations. Keep it minimal.
3. **REFACTOR** — Run the test again. Find new rationalizations. Close the loopholes. Repeat until the agent consistently complies.

**Skill file structure:**

```
~/.claude/skills/<skill-name>/SKILL.md
```

**Required frontmatter:**

```yaml
---
name: skill-name
description: One sentence — when to use and what it does (used for routing decisions)
framework: devflow
---
```

**Required sections:**

- `## When to Use` — specific trigger conditions
- `## When NOT to Use` — explicit exclusions
- Core process / rules
- `## Related Skills and Agents` — cross-references

**Key principle:** The `description` field in the frontmatter is what Claude reads when deciding whether to invoke the skill. Write it as a precise trigger condition, not a marketing sentence.

### Creating a New Agent

**Agent file structure:**

```
~/.claude/agents/<agent-name>.agent.md
```

**Required frontmatter:**

```yaml
---
name: agent-name
description: Focused role description
framework: devflow
model: claude-sonnet-4-6
tools: ["read", "search", "execute"]
---
```

**Model selection guidance:**
- Use `claude-opus-4-7` for planning and architecture decisions where reasoning depth matters most
- Use `claude-haiku-4-5` for mechanical, structured tasks (file scanning, doc sync, dependency mapping)
- Use `claude-sonnet-4-6` for everything else — code reasoning, analysis, test writing, review

**Required sections:**

- Brief role statement (2–3 sentences)
- Numbered capability sections (`1. **What it does**:`)
- `## Boundaries` with `- Does:` and `- Does not:` lines
- `## Output Format` — the structured output schema the agent must follow
- `## Worker Compliance Footer` — ending with `Worker compliance: followed <agent-name> format`

**Key design rules:**

- Every agent must end every response with the compliance footer
- Boundaries must state both what the agent **does** and what it **does not** do
- Output format must use structured headers, not prose paragraphs
- Keep agents narrowly scoped — one thing done well beats several things done adequately

### Registering a New Worker in the Router

After creating the agent, add it to `using-devflow/SKILL.md`:

1. Add a row to the **Worker Roles and Boundaries** table
2. Add it to the relevant **pipeline(s)** as either a default step or a Variant
3. Update the **Transition** blocks of affected pipelines if the new worker introduces loop-back paths

---

## 11. Limitations

### What Devflow Does Not Do

**It does not enforce tool use directly.** Devflow is a behavioral framework — it guides what Claude does, not what tools it can access. Permission boundaries are set separately in Claude Code settings.

**It does not guarantee output quality.** Devflow enforces the right sequence of steps and the right worker for each step. It cannot guarantee that a `feature-implementer` writes good code, only that it follows the defined scope and stays in role.

**It does not cover all task types.** The eleven pipelines cover common software development scenarios. Highly specialized tasks (hardware integration, data science pipelines, legal document review) may not map cleanly to any pipeline. Use the closest matching pipeline or route to `none` and proceed normally.

**It does not replace human review.** Devflow's `code-reviewer` and `acceptance-checker` agents are useful checks, but they are not a substitute for human judgment on critical changes.

**It does not manage long context automatically.** For very long sessions, use `session-continuity` manually at session boundaries to preserve state.

**Agents are role-constrained, not capability-constrained.** A `test-engineer` can technically read production code, but its role definition tells it not to change it. Role discipline depends on the model following the agent's boundaries — it is a soft constraint, not a hard one.

### Known Friction Points

**Overhead on small tasks.** For a one-line typo fix, routing through `task-planner → feature-implementer → code-reviewer` adds friction. Use Pipeline 7 (Review-only) or route to `none` for genuinely trivial changes.

**Pipeline selection is not always obvious.** Some tasks genuinely span pipelines (e.g., a feature that also fixes a latent bug). When in doubt, route to the pipeline that matches the *primary* intent and add workers from the secondary pipeline as Variants.

**Session context limits.** Devflow loads skill content into context when invoked. In very long sessions with many skills active, this consumes context tokens. Use `session-continuity` at natural breakpoints to reset and preserve state.

---

## 12. Quick Reference

### Pipeline Selection Cheatsheet

| Task description | Pipeline |
|---|---|
| "I have an idea" / "What should we build?" | 0 — Requirements |
| "Can we do X?" / "Is Y feasible?" / "Which approach?" | 1 — Spike/POC |
| "We're using [new library] for the first time" | 2 — Unfamiliar API |
| "Add feature X" / "Change behavior of Y" | 3 — Feature |
| "Fix this bug" / "This is crashing" / "Stack trace" | 4 — Bug fix |
| "Clean this up" / "Simplify" / "Reduce complexity" | 5 — Refactor |
| "Add tests for X" / "Coverage is too low" | 6 — Test-only |
| "Review this" / "Check this diff" | 7 — Review-only |
| "Update the README" / "Write changelog entry" | 8 — Docs-only |
| "This is too slow" / "Optimize X" / "Performance regression" | 9 — Performance |
| "Security audit" / "Pre-release security gate" / "New auth or external call" | 10 — Security |

### Routing Announcement Format

```
Selected worker agents: <worker1> → <worker2> → <worker3>
Reason: <why this pipeline>
Current agent: <first worker>
```

### Worker Response Format

```
Active agent: <agent name>
Purpose: <one sentence>
Scope: <in scope / out of scope>

[... structured output ...]

Worker compliance: followed <agent-name> format
Current agent: <next agent>    ← only if pipeline continues
```

### Discipline Checklist

Before claiming a task is complete:

- [ ] Was routing announced before any work began?
- [ ] Did each worker stay in its defined role?
- [ ] Was a failing test written before any fix was applied?
- [ ] Was the fix verified (not just written)?
- [ ] Did `acceptance-checker` map evidence to stated criteria?
- [ ] Was `poc-retrospective` written before closing any spike?
- [ ] Was `session-continuity` used at session boundaries for long work?
- [ ] Was `threat-modeler` run before `find-bugs` for security-sensitive changes?
- [ ] Did `find-bugs` report findings only — not fix them inline?
- [ ] If `interface-designer` ran, was the contract in `docs/interfaces/` checked by `test-engineer` (before writing tests), `code-reviewer` (before approving), and `acceptance-checker` (before marking done)?

### Key Rules Summary

| Rule | Why |
|---|---|
| Route before any work | Without routing, there is no discipline — just speed |
| Reproduce before fixing | Fixes without repro mask the real problem |
| Test before implementing | Tests-after prove nothing; tests-first catch bugs |
| Verify before completing | Evidence before claims — always |
| Retrospective before closing spike | Memory fades; decisions must be recorded |
| New session after spike Proceed | Spike-mode thinking contaminates production planning |
| One worker at a time | Mixed roles produce muddled outputs |
| Minimal diff | Broader scope = harder review = more bugs |
| Threat-model before security review | Generic checklists miss change-specific attack surface |
| Security audit finds, not fixes | Mixing audit and remediation in one pipeline loses traceability |
| Document decisions before implementing | Decisions recorded after the fact omit the alternatives seriously considered |
| Context map before scanning | Avoids redundant codebase sweeps in large projects |
