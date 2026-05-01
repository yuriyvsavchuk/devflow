---
name: adr-writer
description: Write a structured Architecture Decision Record when a significant design decision is made during planning, technology selection, or API research — before implementation begins. Triggered after brainstorming, technology-selector, or api-researcher when the decision affects multiple components, is hard to reverse, or involves named trade-offs.
framework: devflow
---

# ADR Writer

An Architecture Decision Record (ADR) is the closing step whenever a significant architectural decision is reached. It converts the decision — and the reasoning behind it — into a durable document that future contributors can find, understand, and challenge.

This skill is the design-decision parallel to `poc-retrospective`. Where `poc-retrospective` records what a hands-on experiment revealed, `adr-writer` records what a design discussion concluded.

## When to Use

Write an ADR when a decision meets **at least two** of the following criteria:

1. **Affects multiple components** — the decision is not contained within a single file or function; it shapes how parts of the system relate to each other
2. **Hard to reverse** — changing the decision later would require significant rework across the codebase or team
3. **Involves named alternatives** — at least two viable options were considered and one was chosen over the other(s)
4. **Drives future decisions** — other implementation or architecture choices will reference or depend on this one

**Common triggers:**
- `technology-selector` produces a recommendation (library, framework, database, protocol choice)
- `brainstorming` concludes with a significant structural or data model decision
- `api-researcher` reveals an adoption pattern that commits the project to a specific integration approach
- A spike (`poc-retrospective`) produces a Proceed decision that also constitutes an architectural commitment

## When NOT to Use

- Minor implementation details contained within a single function or file
- Decisions that are obvious from the requirements with no real alternatives considered
- Decisions already fully captured in a `poc-retrospective` document for the same topic — link to the retrospective instead of duplicating it
- Simply flip a previous decision without re-evaluating alternatives and trade-offs — if the earlier ADR should be superseded, write a full new ADR (using this skill) that names the old ADR, explains what changed, and goes through the same structure; then update the old ADR's Status to `Superseded by ADR-NNNN`

---

## Output

### Step 1 — Determine the next ADR number

Check the `docs/decisions/` directory for existing ADR files. If the directory does not exist, create it. ADR files are named `NNNN-short-title.md`. Take the highest existing number and increment by one. If no ADRs exist yet, start at `0001`.

### Step 2 — Write the ADR file

Save to:

```
docs/decisions/NNNN-short-title.md
```

Where `short-title` is a kebab-case slug derived from the decision title (e.g., `use-postgresql-for-persistence`, `event-sourcing-for-order-domain`).

### Document Structure

```markdown
# ADR-NNNN: [Decision Title]

**Date:** YYYY-MM-DD
**Status:** Accepted
<!-- Valid values: Proposed | Accepted | Deprecated | Superseded by ADR-NNNN -->
**Context source:** [brainstorming | technology-selector | api-researcher | poc-retrospective | architecture discussion]

## Context

What forces are at play? What problem or requirement is this decision responding to?
What constraints (technical, organisational, time) apply?

## Decision

State the decision in one or two sentences. Be specific — name the technology, pattern, or approach chosen.

## Options Considered

| Option | Summary | Key trade-off |
|---|---|---|
| **[Chosen]** ✓ | Brief description | What it costs |
| [Option B] | Brief description | Why it was not chosen |
| [Option C] | Brief description | Why it was not chosen |

## Rationale

Why this option over the alternatives? What criteria drove the decision?
Reference specific constraints, requirements, or findings from `technology-selector` or `api-researcher` where applicable.

## Trade-offs Accepted

What are we explicitly giving up or accepting as a consequence of this decision?
Be honest — future readers need to know what was knowingly sacrificed.

## Consequences

**Becomes easier:** What this decision enables or simplifies.

**Becomes harder:** What this decision makes more difficult or more constrained.

**Opens new questions:** What follow-on decisions or investigations this decision surfaces.

## Conditions That Would Change This Decision

Under what specific circumstances should this ADR be revisited or superseded?
Examples: "If the team grows beyond X engineers", "If latency requirements tighten to Y", "If the vendor deprecates Z".
```

---

## After Writing the ADR

| Situation | Next Step |
|---|---|
| Decision made during Pipeline 0 | Continue to `scope-estimator` or `writing-plans`; link the ADR in the implementation plan |
| Decision made after a spike Proceed | Continue to `writing-plans` for production implementation; the plan's constraints section should reference this ADR |
| Decision made during Pipeline 2 | Continue to Pipeline 3; `task-planner` should read this ADR before producing the implementation plan |
| Decision supersedes an earlier ADR | Update the earlier ADR's Status to `Superseded by ADR-NNNN` |

---

## Rules

**Rule 1 — Write the ADR before implementation begins.**
A decision recorded after the fact is a reconstruction, not a record. It omits the alternatives that were seriously considered and hardens the chosen option as the only option that ever existed.

**Rule 2 — Name the alternatives explicitly.**
"We considered other approaches" is not an ADR. Name the options and state why each non-chosen option was rejected. Future readers need to understand the trade-offs, not just the outcome.

**Rule 3 — Separate rationale from decision.**
The Decision section states *what* was decided. The Rationale section states *why*. Keep them distinct so the reasoning can be evaluated independently of the conclusion.

**Rule 4 — Conditions That Would Change This Decision is mandatory.**
No architectural decision is permanent. Stating the conditions for revisiting it prevents both premature reopening and cargo-cult preservation of decisions that should have been superseded.

**Rule 5 — One ADR per decision.**
If a single session produces multiple significant decisions, write multiple ADRs. Do not combine unrelated decisions into one document — they may be superseded independently.

## Related Skills and Agents

- **Preceded by:** devflow:brainstorming, devflow:technology-selector, devflow:api-researcher, or devflow:poc-retrospective — one of these produces the decision that this skill records
- **Followed by:** devflow:writing-plans (Pipeline 0/1 transitions) or devflow:task-planner via Pipeline 3 — the ADR is an input to the implementation plan; `task-planner` checks `docs/decisions/` before planning
- **Complementary to:** devflow:poc-retrospective — retrospective records what a hands-on experiment revealed; ADR records the architectural decision that follows from it; both may be written in sequence for a single spike that produces a Proceed decision with architectural consequences
- Use devflow:poc-retrospective for spike/experiment records; use devflow:adr-writer for design decisions derived from analysis, discussion, or technology selection rather than hands-on experiment
