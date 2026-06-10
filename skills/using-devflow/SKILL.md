---
name: using-devflow
description: Deprecated v1 router — v2 replaces it with devflow-dispatch (one-line per-task classification) plus six lazy-loaded playbooks. This file only maps v1 pipelines to their v2 homes.
framework: devflow
---

# using-devflow (v1) → devflow-dispatch (v2)

The v1 all-in-one router is retired. In v2, invoke **`devflow-dispatch`** once when a new task begins — it classifies the task into a playbook and an effort tier in one line, and only the selected playbook is loaded. Routing context cost drops from ~12K tokens per message to under 1K per task.

If this skill was invoked, apply `devflow-dispatch` now and continue there.

## v1 pipeline → v2 home

| v1 pipeline | v2 home |
|---|---|
| 0 — Requirements gathering | `devflow-shape` |
| 1 — Spike / POC | `devflow-spike` |
| 2 — Unfamiliar API / library | `devflow-shape` (research gate) |
| 3 — New feature / behavior change | `devflow-build` |
| 4 — Bug fix | `devflow-fix` |
| — *(new in v2)* production incident | `devflow-hotfix` |
| 5 — Refactor / simplification | `devflow-build` (refactor adapter) |
| 6 — Test-only | direct: `test-engineer` agent |
| 7 — Review-only | `devflow-audit` |
| 8 — Docs-only | direct: `docs-updater` agent |
| 9 — Performance | `devflow-build` (performance adapter) |
| 10 — Security audit | `devflow-audit` (security adapter) |

## What else changed

- **Per-task activation** replaces per-message routing. CLAUDE.md line: *"When a new development task begins, invoke the devflow-dispatch skill to classify it. Do not re-invoke for mid-task messages or follow-up confirmations."*
- **Worker self-identification headers and compliance footers are retired.** Artifacts and the run record are the audit trail — not transcript decoration.
- **All artifact locations are unchanged:** `docs/decisions/`, `docs/interfaces/`, `docs/specs/`, `docs/sessions/`, `docs/context-maps/` work exactly as before.
