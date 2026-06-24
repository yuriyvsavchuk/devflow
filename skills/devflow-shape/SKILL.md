---
name: devflow-shape
description: Requirements-to-plan playbook — clarify a vague or new task into a written spec with testable acceptance criteria, size it, and produce an implementation plan. Selected by devflow-dispatch for requirements analysis, specification, and planning work.
framework: devflow
---

# Shape — Requirements → Spec → Plan

Turn an idea or rough request into three durable outputs: a spec with testable acceptance criteria, a size estimate, and an implementation plan. **No production code is written in this playbook.**

## Steps

### 1. Clarify

If requirements are vague, ask questions **one at a time** — wait for each answer before asking the next. Stop when you can state:

- the goal and who/what triggers it
- the desired observable outcome
- what is explicitly out of scope

If requirements are already partially written, confirm only the gaps — do not re-interview settled points.

### 2. Research gate — only when unfamiliar technology is involved

If the task depends on a library, API, or framework not previously used in this project, dispatch the `researcher` agent (API mode) before writing the spec. The findings must answer the load-bearing unknowns (auth model, error behavior, version constraints, rate limits). Do not write the spec while critical behavior is unknown; carry the findings into it.

### 3. Spec

Write the spec to `docs/specs/<slug>.md`:

```markdown
---
type: spec
status: draft
date: YYYY-MM-DD
---

# <Title>

## Goal

## Context

## Acceptance criteria
- AC-1 `gwt`: Given <precondition>, When <action>, Then <observable outcome>.
- AC-2 `ears`: When <trigger>, the system shall <response>.
- AC-3 `prose`: <independently testable statement>

## Non-Goals
- `ears`: If <unwanted condition>, then the system shall <safe response>. (What it does NOT do.)

## Assumptions

## Size
<S | M | L | XL> — confidence <High | Medium | Low>: <one line of reasoning>

## Open questions
```

Rules:

- Acceptance criteria are numbered `AC-n` and each is **independently testable** — downstream tests, reviews, and acceptance checks reference these IDs. A criterion that cannot fail a test is not a criterion. (Format contract: docs/ADOPTION.md → front-matter conventions; the rails' `verify` checks it.)
- **Notation (SDD Tier-1):** each criterion may carry a notation tag — pick the form that fits the requirement type, keeping the `AC-n` ID:
  - `` `gwt` `` (Given/When/Then) for **behavioral flows** — carries concrete example data, ideal for test generation.
  - `` `ears` `` (EARS) for **constraints, invariants, and unwanted-behavior** — terse; the `If <condition>, then …` pattern is the recommended form for **Non-Goals** ("what it does NOT do").
  - `` `prose` `` (or no tag) — the always-valid fallback, especially at `quick` tier.
  Mixing notations within one spec is expected; choose per criterion, not per spec.
- **Non-Goals are first-class** — articulate what the system does NOT do as clearly as what it does.
- **XL size or Low confidence → split** into multiple specs before any planning; each spec routes through dispatch separately.

### 4. Decision checkpoint

If shaping settled a decision between named alternatives (technology choice, architectural approach, data model), ask the developer whether it warrants an ADR — write it via `adr-writer` before planning if yes. Do not silently bury decisions in the spec.

### 5. Plan

Use the `writing-plans` skill. The plan must reference the spec and its `AC-n` IDs in its done criteria. Save it beside the spec or in the project's plans location. Spec is saved and agreed **before** the plan is written — never plan from an unwritten spec.

## Exit

- Offer a **paste-ready tracker block** — title, description, acceptance criteria — for Jira or whatever the team uses. Devflow produces the content; the tracker remains the system of record.
- Hand off: `devflow-build` (or `devflow-fix` for defect-shaped work) executes the plan.
- At `quick` tier (small, well-understood change): steps 1–3 may compress into a short inline spec section in the conversation, but numbered `AC-n` criteria are still required — they are what the rest of the flow verifies against.

## Boundaries

- Does: clarify requirements; run the research gate; produce spec, sizing, ADR checkpoint, and plan.
- Does not: write production code; make architectural decisions silently; start planning while requirements or critical research findings are missing.
