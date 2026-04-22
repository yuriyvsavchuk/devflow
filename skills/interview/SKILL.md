---
name: interview
description: Use when a software feature or system requirement needs a detailed written spec before design or implementation — extracts requirements, constraints, and acceptance criteria through structured one-at-a-time questioning
framework: devflow
---

# Interview

Conduct a structured, in-depth interview to turn a vague idea or request into a complete, written specification. The interview is the entry point for any work where the requirements are not yet fully understood.

## When to Use

- A new feature or behavior change has been requested but requirements are not written down
- The scope, constraints, or success criteria of a task are unclear
- A user or stakeholder has an idea that needs to be made concrete before designing or planning
- The devflow:brainstorming is the next step and you need a clear input for it

## When NOT to Use

- Requirements are already clearly defined in a spec or TASK.md — skip to devflow:brainstorming or devflow:writing-plans
- The task is a bug fix with a clear reproduction — use devflow:bug-repro-triager instead
- The work is exploratory/unknown-feasibility — use devflow:spike-executor to validate before specifying

---

## Core Pattern

### Phase 1 — Orient

Before asking anything, read available context:
- Existing files, docs, recent commits
- Any partial notes or prior conversation
- The current project state

Use this to avoid asking questions already answered.

### Phase 2 — Ask One Question at a Time

Use the `AskUserQuestion` tool. Ask questions one at a time — never multiple questions in a single message.

Cover these areas in order, adapting based on answers:

1. **Goal**: What should this do? What problem does it solve?
2. **Success criteria**: How will you know it works? What does "done" look like?
3. **Users / consumers**: Who uses this, and in what context?
4. **Constraints**: Technical, time, compatibility, or resource limits
5. **Edge cases**: What happens when inputs are invalid, missing, or unusual?
6. **Non-goals**: What is explicitly out of scope?
7. **Trade-offs**: If there are competing approaches, which properties matter most?
8. **Open questions**: What is still uncertain?

Prefer multiple-choice questions when reasonable — they are easier to answer and reveal implicit assumptions.

Ask follow-up questions on any answer that is vague, contradictory, or incomplete. Do not move to the next area until the current one is clear.

### Phase 3 — Validate Understanding

Before writing the spec, restate your understanding in plain language and ask for confirmation or corrections.

### Phase 4 — Write the Spec

Use the `Write` tool to save the specification to:

```
docs/specs/YYYY-MM-DD-<feature-slug>.md
```

**Spec structure:**

```markdown
# Spec: <Feature Name>

**Date:** YYYY-MM-DD
**Status:** Draft

## Goal

One paragraph: what this does and why.

## Success Criteria

- [ ] Concrete, verifiable acceptance criterion
- [ ] ...

## Users / Consumers

Who uses this and in what context.

## Requirements

Numbered list of specific requirements.

## Constraints

Technical, compatibility, time, or resource limits.

## Edge Cases

How specific unusual or invalid inputs should be handled.

## Non-Goals

What is explicitly out of scope.

## Open Questions

Unresolved questions that will need answers before or during implementation.
```

---

## Rules

**Rule 1 — One question per message.**
Never ask multiple questions at once. If a topic needs several questions, ask them sequentially.

**Rule 2 — Non-obvious questions only.**
Do not ask about things that are evident from context, the codebase, or prior answers.

**Rule 3 — Keep going until complete.**
Continue interviewing until all areas are covered and no significant open questions remain.

**Rule 4 — Write the spec before finishing.**
The interview is not complete until the spec document is written and saved.

---

## Common Mistakes

- Asking all questions at once — overwhelming and produces surface-level answers
- Moving to design before the spec is agreed — results in building the wrong thing
- Writing a vague spec with "TBD" everywhere — defeats the purpose of the interview
- Skipping edge cases — the most common source of rework

---

## Related Skills and Agents

- **Followed by:** devflow:brainstorming (explore approaches) or devflow:writing-plans (if approach is already clear)
- **Use instead for bugs:** devflow:bug-repro-triager
- **Use instead when feasibility unknown:** devflow:spike-executor
