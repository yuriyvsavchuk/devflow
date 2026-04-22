---
name: poc-retrospective
description: Use after a technical spike or proof-of-concept investigation completes — captures the decision, learnings, and carry-forwards before transitioning to production software implementation planning
framework: devflow
---

# POC Retrospective

A retrospective is the closing step of every spike. It converts raw investigation findings into a structured decision record that can be handed to the next phase — or revisited in a future session.

## When to Use

- A spike has reached a conclusion (confirmed / refuted / inconclusive)
- A POC has produced enough evidence to make a go/no-go decision
- You are ending an investigation session and need to preserve state
- You want to extract what should carry forward into a production implementation plan

## When NOT to Use

- The spike is not yet finished — complete the investigation first
- You are writing a post-mortem for a production incident — use devflow:docs-updater instead

---

## Output

Invoke the `Write` tool to save the retrospective to:

```
docs/spikes/YYYY-MM-DD-<hypothesis-slug>.md
```

### Document Structure

```markdown
# Spike Retrospective: <hypothesis title>

**Date:** YYYY-MM-DD  
**Decision:** Proceed / Pivot / Abandon  
**Confidence:** High / Medium / Low  

## Hypothesis

> The original hypothesis statement.

## What We Tried

Brief description of the experiment(s) run.

## Evidence

What was observed. Include relevant output, measurements, or error messages.

## What Worked

Findings that support the hypothesis or reveal viable paths.

## What Did Not Work

Findings that refuted the hypothesis or revealed blockers.

## Key Learnings

Non-obvious insights discovered during the investigation that are worth preserving.

## Decision Reasoning

Why this decision was made given the evidence. Include trade-offs considered.

## Carry-Forwards

If decision is **Proceed** or **Pivot**:
- Constraints or assumptions the production plan must respect
- Patterns or code snippets from the spike worth keeping or adapting
- Risks or unknowns the production implementation must address

If decision is **Abandon**:
- Why this path is not viable
- What alternative approaches remain open

## Follow-Up Spikes

Questions that surfaced during this investigation that are not yet answered:
- [ ] <unanswered question>

## Cleanup Checklist

- [ ] Delete or archive spike code in `spike/` / `scratch/`
- [ ] Remove temporary dependencies added for investigation
- [ ] Close or note any open branches created for the spike
```

---

## After the Retrospective

| Decision | Next Step |
|---|---|
| **Proceed** | Use devflow:writing-plans to create a production implementation plan informed by the carry-forwards |
| **Pivot** | Open a new spike with the refined hypothesis; link back to this retrospective |
| **Abandon** | Record why in the document; no further action unless a new approach surfaces |

---

## Rules

**Rule 1 — Write the document before closing the session.**  
Memory of investigation details fades. The retrospective must be written while the evidence is fresh.

**Rule 2 — Distinguish evidence from interpretation.**  
State what was observed separately from what it means. Future readers need to evaluate both.

**Rule 3 — Carry-forwards must be actionable.**  
"We learned X" is a learning. "The production plan must account for X because of Y" is a carry-forward. Write carry-forwards as constraints or requirements, not observations.

**Rule 4 — Honest inconclusive is better than forced conclusion.**  
If the evidence does not support a clear decision, say so. List what would be needed to reach one.
