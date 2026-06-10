---
name: devflow-hotfix
description: Production-incident playbook — mitigate the harm now, verify, ship, and record the owed root-cause work as tracked debt. Selected by devflow-dispatch when production is impacted and speed beats ceremony.
framework: devflow
---

# Hotfix — Mitigate → Verify → Ship → Record Debt

When production is bleeding, the right order inverts: stop the harm first, understand it fully later. This playbook is fast — and it guarantees the follow-up is not forgotten.

## Steps

### 1. Mitigate

Apply the smallest action that stops the harm: rollback, feature flag off, guard clause, config change, dependency pin. Prefer reversible mitigations. Root-cause analysis is **not** required now — only enough understanding to choose a safe mitigation.

### 2. Verify the mitigation

Evidence that the harm stopped: error rate down, the failing path now guarded, a repro attempt that no longer reproduces. State what was checked. If the mitigation didn't work, try the next-smallest one — do not start root-causing under fire unless no mitigation works at all.

### 3. Ship

Use the project's fastest sanctioned path. Tell the humans who need to know.

### 4. Record the debt — mandatory, never skipped

Write `docs/sessions/hotfix-debt-<slug>.md`:

```markdown
---
type: hotfix-debt
status: open
date: YYYY-MM-DD
---

# Hotfix: <title>

**What happened:** <2–3 lines>
**Mitigation applied:** <what + commit/PR>
**Verified by:** <evidence>
**Owed:** root-cause fix · regression test · review of the mitigation diff
**Retro (5 lines max):** what failed · why it wasn't caught · what would catch it next time
```

### 5. Schedule the follow-up

The debt is closed only by a `devflow-fix` run: root cause, failing regression test, proper fix, review (including the mitigation diff), then set the debt record to `status: closed`.

*(Phase 2 wires open debt records into the session auto-brief; until then, check `docs/sessions/` for `status: open` debt at session start as part of the session ritual.)*

## Boundaries

- Does: mitigate, verify, ship, record debt, route the follow-up.
- Does not: root-cause under fire; skip the debt record; close debt without the follow-up fix run.
