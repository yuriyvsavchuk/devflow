---
name: devflow-spike
description: Feasibility playbook — state a hypothesis, run a throwaway experiment, close with a mandatory retrospective and a Proceed/Pivot/Abandon decision. Selected by devflow-dispatch for "is X feasible / which approach / can we use Y" questions.
framework: devflow
---

# Spike — Hypothesis → Experiment → Retrospective

Validate before committing. Spike code is throwaway by definition — the deliverable is the **decision and what was learned**, never the code.

## Steps

### 1. Hypothesis

One sentence: what question this spike answers and what evidence would settle it. For a narrow single-assumption question, run a **designed experiment**: define the pass/fail criteria *before* running anything, then evaluate strictly against them.

### 2. Research — only if the domain is unfamiliar

The `researcher` agent gathers context (docs, known constraints, prior art). Skip when the domain is already understood.

### 3. Experiment (throwaway mode)

- No TDD, no production standards — speed of learning is the only quality bar.
- Code artifacts go on an isolated branch or worktree that can be deleted or archived cleanly. On Claude Code, the `spike-investigator` agent gets this automatically — it runs in a temporary git worktree (`isolation: worktree`, auto-cleaned if unchanged); elsewhere, `using-git-worktrees` is the manual path.
- Stay on the stated hypothesis. New questions discovered along the way become new spikes — not scope growth in this one.

### 4. Retrospective — mandatory; the spike is not closed without it

Use `poc-retrospective`: the decision (**Proceed / Pivot / Abandon**), the evidence, key learnings, carry-forwards, and a cleanup checklist. If a Proceed decision constitutes an architectural commitment, ask the developer whether an ADR is warranted before closing.

## Exit

- **Proceed** → production work starts in a **new session**, oriented from the retrospective — spike-mode context is not carried forward. Route to `devflow-shape` (if a spec is needed) or `devflow-build`.
- **Pivot** → a new spike with the refined hypothesis.
- **Abandon** → the retrospective closes the record; no further work.

## Boundaries

- Does: validate one stated hypothesis with evidence; record the decision and learnings.
- Does not: produce production code; skip the retrospective; let spike code drift into the product.
