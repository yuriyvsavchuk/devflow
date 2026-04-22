---
name: spike-executor
description: Use when a technical idea or architectural approach needs feasibility validation before committing to a software implementation plan — time-boxed throwaway exploration, no TDD mandate
framework: devflow
---

# Spike Executor

A spike is a time-boxed, throwaway investigation that answers a specific technical question. Its output is a **decision** — proceed, pivot, or abandon — not production code.

## When to Use

- You have a technical idea but do not know if it is feasible
- You need to evaluate a library, API, or architecture before committing to it
- A key assumption in a planned implementation is unvalidated
- You want to explore two or three approaches before choosing one
- The cost of building something wrong is high and the answer is unknown

## When NOT to Use

- The approach is already well-understood — use devflow:writing-plans instead
- The goal is production-quality implementation — use devflow:subagent-driven-development
- You are debugging a known failure — use devflow:systematic-debugging

---

## Core Pattern

### Phase 1 — Frame the Hypothesis

Before any investigation, produce a clear, falsifiable hypothesis statement:

> "I believe that [approach/technology X] can [achieve goal Y] within [constraint Z]."

The hypothesis must be specific enough that evidence either confirms or refutes it. A vague hypothesis produces a vague spike.

Use the devflow:interview if the goal is unclear — do not start a spike until the hypothesis is agreed.

### Phase 2 — Research (optional, when unfamiliar territory)

If the domain is unfamiliar, dispatch a devflow:research first:
- What does the technology/API actually do?
- What are the known constraints and failure modes?
- What do existing examples look like?

This phase prevents wasted experiment time on approaches that are documented as non-viable.

### Phase 3 — Experiment

Dispatch a devflow:spike-investigator with:
- The hypothesis statement
- The constraints (time, environment, existing codebase)
- The definition of "enough evidence" (what result confirms or refutes)

The investigator works in throwaway mode: no TDD mandate, no production standards, minimal scope.

### Phase 4 — Review Finding

Review the investigator's output critically:
- Is the evidence sufficient to make a decision?
- Are the key unknowns acceptable risks, or do they require another spike?
- Is the conclusion justified by the evidence (not just hopeful)?

If evidence is insufficient → narrow the hypothesis and repeat Phase 3.  
If evidence is sufficient → proceed to Phase 5.

### Phase 5 — Decision and Retrospective

Once the hypothesis is resolved, invoke the devflow:poc-retrospective to:
- Record the decision and its reasoning
- Extract carry-forwards for the production plan
- Clean up throwaway artifacts

---

## Spike Discipline Rules

**Rule 1 — One hypothesis per spike.**  
Do not let a spike expand into multiple questions. If new questions surface, record them as follow-up spikes and stay focused.

**Rule 2 — Time-box explicitly.**  
A spike without a time-box becomes an unbounded research project. Set a limit before starting (e.g., "answer this in under 2 hours of investigation").

**Rule 3 — Throwaway artifacts must be named as such.**  
Any code written during a spike must be in a clearly marked location (e.g., `spike/`, `scratch/`) or flagged in the retrospective for deletion. Do not let spike code drift into production paths.

**Rule 4 — The output is a decision, not code.**  
A spike that produces polished code but no decision has failed its purpose.

**Rule 5 — Inconclusive is a valid outcome.**  
"We don't know yet" is an honest answer. It should specify what additional evidence would resolve the uncertainty.

---

## Quick Reference

| Phase | Worker | Output |
|---|---|---|
| Frame hypothesis | (inline, no agent) | Hypothesis statement |
| Research background | devflow:research | Key findings, constraints |
| Experiment | devflow:spike-investigator | Evidence, conclusion, recommendation |
| Decision | (inline review) | Proceed / Pivot / Abandon |
| Capture learnings | devflow:poc-retrospective | Decision record, carry-forwards |

---

## Common Mistakes

- **Starting to implement before the hypothesis is written** — forces the spike to validate the implementation rather than the idea
- **Expanding scope mid-spike** — "while I'm here" additions contaminate the conclusion
- **Treating an inconclusive spike as confirmation** — absence of failure is not proof of viability
- **Skipping the retrospective** — learnings not captured are learnings lost; future sessions start from zero
- **Keeping spike code** — throwaway code that is not thrown away becomes technical debt with no tests
