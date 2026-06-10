---
name: devflow-dispatch
description: Classify a new development task into a playbook and effort tier before work begins. Invoke once when a new task arrives — not for mid-task messages, follow-up confirmations, or conversational questions.
framework: devflow
---

# Devflow Dispatch

Classify the task, announce the result in one line, load the selected playbook skill, and begin. Do not re-invoke for messages inside an already-running task.

## When NOT to dispatch (answer directly, no announcement)

- Conversational or meta questions — explanations, opinions, "how does X work?"
- Mid-task messages — confirmations ("yes", "continue", "looks good"), follow-ups inside an active playbook run
- Trivial mechanical edits (fix a typo, rename one symbol, bump a version string) — just make the edit
- Questions about Devflow itself

## Classification

| Task signal | Playbook |
|---|---|
| Vague idea, unclear requirements, "what should we build?", spec needed | `devflow-shape` |
| New feature, behavior change, public API change | `devflow-build` |
| "Clean up / simplify / refactor" — no behavior change | `devflow-build` (refactor adapter) |
| "Too slow / optimize" / performance regression | `devflow-build` (performance adapter) |
| Bug report, stack trace, wrong behavior | `devflow-fix` |
| Production incident — mitigation needed now | `devflow-hotfix` |
| "Is X feasible? Which approach? Can we use Y?" | `devflow-spike` |
| "Review this / check this diff" | `devflow-audit` |
| Security review; new auth / input / external-call surface | `devflow-audit` (security adapter) |
| Unfamiliar library or API involved | `devflow-shape` (research gate), then `devflow-build` |

**Direct skills — no playbook, no tier:** tests only → `test-engineer` agent; docs only → `docs-updater` agent.

## Effort tier

| Tier | When | What runs |
|---|---|---|
| `quick` | Small, low-risk, no new interfaces — a few lines or one file | Playbook checklist applied inline; no subagents, no ceremony |
| `standard` *(default)* | Everything else | Playbook in the main session; artifacts; one fresh-context reviewer subagent at the end |
| `full` | Public API or shared-module change; multi-component scope; risk keywords (auth, payment, billing, migration, production data, security); XL or low-confidence sizing | Independent reviewer and acceptance subagents; interface contract; context map |

Rules:

- The user's one-word override always wins: "quick: …" / "full: …".
- Suggest the tier from blast radius and risk keywords; when in doubt, `standard`.
- Model escalation: planning runs on Sonnet by default; use Opus only at `full` tier or when sizing returns XL / low confidence.

## Announcement format

`Playbook: <name> (<tier>) — <one-line reason>`
or `Direct: <skill> — <one-line reason>`

Nothing else — no headers, no footers. Then load the playbook skill and begin.

## Routing challenge

At every playbook step transition, one-line self-check: *is this still the right playbook and tier?* If not, say what changed in one line and re-dispatch. Mid-course correction is expected, not a failure.
