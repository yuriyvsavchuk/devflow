---
name: hypothesis-validator
description: Use in software development when a specific technical assumption must be tested with a minimal designed experiment before committing to an implementation approach — lighter than a full spike
framework: devflow
---

# Hypothesis Validator

A hypothesis validator is a focused experiment-design discipline. It is lighter than a full spike (devflow:spike-executor) and sharper than informal exploration. Use it when you have **one specific assumption** that must be true for your plan to work and you need to verify it with the minimum possible effort.

## When to Use

- One critical assumption underpins an implementation plan and it is unverified
- You want to validate a narrow technical claim before opening a full spike
- You are mid-plan and hit an assumption that could invalidate the rest
- You want to sanity-check a library, API call, data shape, or performance bound before building on it

## When NOT to Use

- Multiple assumptions need testing simultaneously — open a spike with devflow:spike-executor instead
- The question is broad ("is X a good fit?") — use devflow:spike-executor or devflow:interview first to sharpen it
- The assumption is about design, not technical feasibility — use devflow:brainstorming

---

## Core Pattern

### Step 1 — Write the Assumption Statement

State the assumption precisely. It must be falsifiable:

```
Assumption: [Technology/API/behavior X] can [do Y] [within constraint Z].
```

Bad: "Redis is fast."  
Good: "Redis pub/sub can deliver messages to 100 concurrent subscribers within 50ms on our target hardware."

### Step 2 — Define Confirmation and Refutation Criteria

Before running any experiment, decide what evidence counts as proof:

| | Criteria |
|---|---|
| **Confirmed if** | Specific observable outcome that proves the assumption holds |
| **Refuted if** | Specific observable outcome that proves it does not hold |
| **Inconclusive if** | What would make the result uninterpretable (noise, environment, wrong test) |

Do not run the experiment until these criteria are written down.

### Step 3 — Design the Minimum Sufficient Experiment

The experiment must be the smallest thing that produces definitive evidence. Ask:

- What is the shortest path to confirmation or refutation?
- Can I test this with a 10-line script instead of a full integration?
- What inputs and environment do I need?
- What would make this test invalid?

Document the experiment design before executing it.

### Step 4 — Run and Record

Execute the experiment. Record:
- Exact inputs used
- Exact outputs / measurements observed
- Any surprises or unexpected behavior
- Environment details (versions, config, hardware) if relevant

### Step 5 — Evaluate Against Criteria

Match observations to the pre-defined criteria from Step 2. Do not interpret post-hoc — the criteria were written in advance precisely to prevent rationalization.

### Step 6 — State the Result

One of:
- `Confirmed` — assumption holds, proceed with the plan
- `Refuted` — assumption does not hold, the plan must change
- `Inconclusive` — experiment was insufficient; refine and retry with a better design

---

## Output Format

```
Assumption: <the precise statement>

Confirmation criteria: <what would prove it>
Refutation criteria: <what would disprove it>

Experiment: <what was done, minimum description>

Observations: <raw results, measurements, errors>

Result: Confirmed / Refuted / Inconclusive
Reasoning: <how observations map to criteria>

Next step: <proceed with plan / adjust plan because X / retry with different experiment>
```

---

## Rules

**Rule 1 — Criteria before execution.**  
If you write the confirmation criteria after seeing the results, you are rationalizing, not validating.

**Rule 2 — One assumption per validation.**  
Testing two assumptions at once makes it impossible to know which one caused a failure.

**Rule 3 — Record the raw output.**  
"It worked" is not evidence. The actual output, measurement, or error message is evidence.

**Rule 4 — Inconclusive demands a better experiment, not a guess.**  
An inconclusive result means the experiment was flawed, not that the assumption is half-true.

---

## Relationship to Other Skills

| Situation | Use |
|---|---|
| One specific assumption to test | devflow:hypothesis-validator (this skill) |
| Multiple unknowns, full investigation needed | devflow:spike-executor |
| Technology choice between options | devflow:technology-selector |
| Assumption confirmed, ready to plan | devflow:writing-plans |
| Assumption refuted, need to reconsider approach | devflow:brainstorming |
