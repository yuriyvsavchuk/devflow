# Devflow smoke harness — prompt regression for the playbooks

**Why this exists.** Skills and playbooks are prompts, and prompts have no
compiler: a wording change, a new model version, or a refactor can silently
change behavior. This harness is the regression net. Its design rule (D30):
**never assert on what the model said — assert on what verifiably happened.**
Each scenario runs a small task through a fresh model context in a throwaway
workspace; `smoke_check.py` then checks *outcomes*: artifacts on disk, the
phase journal (`marks-log.jsonl`), the run ledger (`runs.jsonl`), and the
gate-denial log (`gate-log.jsonl`) — all written by the rails themselves, so
no assertion ever depends on the model reporting on its own behavior.

## Layout

```
tests/smoke/
  smoke_check.py            the assertion core (deterministic, stdlib, unit-tested)
  scenarios/*.json          one manifest per scenario: prompt, fixtures, assertions
  fixtures/<scenario>/...   seed files copied into the scenario workspace
  _generate_scenarios.py    reviewable generator for the shipped set
```

Scenario set: **6 playbook scenarios** (shape, build, fix, hotfix, spike,
audit — happy-path discipline), **3 negative scenarios** (trivial edit,
question, mid-task confirmation — they assert *restraint*: `no_run_opened`,
guarding against over-routing, the classic adoption-killer), and **1
adversarial scenario** (`gate-adversarial` — instructs the model to violate
TDD order and asserts the gate denied it).

## Running a scenario — in-session transport (the default today)

1. Create a temp workspace; copy each manifest `fixtures` entry into place.
2. Install rails there: `python <framework>/devflow.py --root <ws> init`.
3. Hand the manifest's `prompt` to a **fresh agent context** scoped to that
   workspace (e.g. a Claude Code subagent told to work only in `<ws>`).
4. Check outcomes: `python tests/smoke/smoke_check.py --scenario
   tests/smoke/scenarios/<name>.json --workspace <ws>`.
5. A FAIL means one of three things — diagnose which before "fixing":
   the playbook prompt regressed, the scenario over-specifies (assertion too
   tight for legitimate variance), or the checker is wrong.

**Transport limitation, stated honestly:** Claude Code hooks are bound to the
session's own project root, so a subagent working in a temp workspace is NOT
gated by that workspace's hooks. In-session runs therefore verify *playbook
discipline* (artifacts, phases, ledger) but not *hook enforcement*. Scenarios
marked `"transport": "hooked"` (currently `gate-adversarial`) are skipped
in-session and require a transport where the scenario workspace is the session
root — i.e. headless.

## Headless transport (future)

`claude -p "<prompt>"` executed *in* the scenario workspace would make every
scenario fully testable (hooks included) and CI-schedulable. Precondition:
the Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
with auth available — empirically absent on the reference machine as of
2026-06-12 (desktop-app-only install), so the wrapper is deliberately not
shipped half-tested. When the CLI is present: loop scenarios → seed workspace
→ `claude -p` with the manifest prompt → `smoke_check.py`; wire into CI on a
release cadence (each run costs real model usage — this is a release gate,
not a per-commit check).

## When to run

Before merging changes to any playbook/dispatch skill; after a model-version
change; before tagging a release. Cost: minutes per scenario at standard tier.
