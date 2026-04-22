---
name: session-continuity
description: Use at the start or end of a software development or technical investigation session to save or restore work state — prevents losing context on multi-session implementation, debugging, or research work
framework: devflow
---

# Session Continuity

Complex investigations, multi-step plans, and POC work frequently span multiple sessions. Without a snapshot, each session restarts from scratch: re-reading files, re-establishing what was tried, and rediscovering decisions already made.

This skill ensures state is captured at the end of a session and restored at the start of the next one.

---

## When to Use

**At session end** (write mode):
- You have made significant progress on an investigation, plan, or implementation
- The work is not complete and will continue in a future session
- You want to hand off context cleanly — whether to yourself or to another agent

**At session start** (read mode):
- Resuming work from a previous session
- Starting a new session on a project with existing in-progress work
- An agent is being spawned into a context it did not participate in

---

## Snapshot File Location

```
docs/sessions/YYYY-MM-DD-HH-MM-<topic-slug>.md
```

Always use the current date and time. If a snapshot already exists for the topic, update it in place rather than creating a duplicate.

---

## Write Mode — Capturing State

Invoke the `Write` tool to produce the snapshot. Use this structure:

```markdown
# Session Snapshot: <topic>

**Date:** YYYY-MM-DD  
**Status:** In Progress / Blocked / Ready for Next Step  
**Next action:** <single most important thing to do next>

## Goal

What this work is trying to achieve. One paragraph maximum.

## Current State

Where things stand right now. What exists, what works, what does not.

## Decisions Made

Key decisions recorded with their reasoning. Include what was ruled out and why.

| Decision | Reasoning | Alternatives Ruled Out |
|---|---|---|
| ... | ... | ... |

## Work Completed

What has been done so far. Be specific — file names, step numbers, test results.

- [ ] completed: <item>
- [ ] completed: <item>

## Work Remaining

What still needs to be done to reach the goal.

- [ ] <next step>
- [ ] <following step>

## Open Questions

Unresolved questions or blockers that need answers before work can continue.

- <question or blocker>

## Context for Resumption

What a fresh session needs to know to pick up without re-reading everything. Include:
- Key files to read first
- Constraints or gotchas discovered
- What NOT to do (and why)
- Any in-progress or temporary state (open branches, temp files, running processes)

## Related Artifacts

| Type | Location | Notes |
|---|---|---|
| Plan | docs/plans/... | |
| Spike retrospective | docs/spikes/... | |
| Scratch / throwaway code | spike/ or scratch/ | |
```

---

## Read Mode — Restoring State

At the start of a session, before any work:

1. Check for an existing snapshot: `docs/sessions/`
2. Read the most recent snapshot for the current topic
3. Output a brief orientation:
   - **Goal**: one sentence
   - **Status**: current state
   - **Next action**: what to do first
   - **Blockers / open questions**: anything that needs resolution
4. Ask the user to confirm or update the state before proceeding

Do not assume the snapshot is fully accurate — it was written at a point in time. Verify that key files and states mentioned still exist before acting on them.

---

## Rules

**Rule 1 — Write before closing, not after.**  
A snapshot written from memory is less accurate than one written while the context is active. Capture state before ending the session.

**Rule 2 — "Next action" must be a single, unambiguous instruction.**  
"Continue work" is not a next action. "Run the failing test in `auth.test.ts` and diagnose the error" is.

**Rule 3 — Decisions section is the most important section.**  
Rediscovering a decision costs time. Relitigating a ruled-out option costs more. Always record what was considered and why it was rejected.

**Rule 4 — Verify before acting on a restored snapshot.**  
Check that files, branches, and states referenced in the snapshot still exist before using them as a starting point.

**Rule 5 — One snapshot per topic, updated in place.**  
Do not accumulate daily snapshot files. Update the existing file so the topic's history is in one place.

---

## Integration with Other Skills

| Trigger | Action |
|---|---|
| Starting investigation / spike | Create snapshot early with Goal and initial decisions |
| After each significant decision | Update Decisions Made section |
| After devflow:poc-retrospective completes | Update Status to complete; link to retrospective doc |
| Before ending a multi-session plan execution | Capture Work Completed and Work Remaining |
| At start of resumed session | Read mode — orient before acting |
