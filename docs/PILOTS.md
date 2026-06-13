# Piloting Devflow v2 — a two-week protocol

Thank you for piloting. This protocol is designed so that two weeks of your
normal work produces **comparable evidence** — for you (did this pay rent?)
and for the framework (the controlled before/after that its own development
cannot produce). Nothing here changes *what* you work on; it changes only
which Devflow level is active.

## Who this is for

A developer (or 2–5 person team sharing a repo) using Claude Code daily on a
real project. You should be comfortable copying files into `~/.claude/` and
running one Python command. Windows, macOS, and Linux all work (Windows needs
Git for Windows — its Git Bash runs the hooks).

## Setup (15 minutes, before week 1)

Follow [ADOPTION.md](ADOPTION.md) **Level 1 (Core)** only: copy `skills/` and
`agents/`, add the activation line to your `CLAUDE.md`. Do **not** install
the rails yet — week 1 runs playbooks-only, that's the experiment.

## Week 1 — Core only (playbooks, no rails)

Work normally. The dispatch skill will classify tasks; playbooks guide order
and artifacts; nothing is mechanically enforced. At the end of the week,
note (a paragraph each):

1. How often dispatch routed correctly vs. ceremonialized something trivial.
2. Which artifacts (specs, plans, debt records) you actually kept or reread.
3. Any moment you abandoned a playbook mid-way — and why.

## Week 2 — add the Rails (Level 2)

`cd your-project && python /path/to/devflow/devflow.py init`, then
`python .devflow/devflow.py doctor` (all checks must PASS — doctor exists to
catch hook-wiring problems that would otherwise silently un-gate your week 2).
Then work normally again. The rails add: the session auto-brief, the TDD gate during
fix/build runs, protected paths (add 1–3 of your genuinely human-only files
to `.devflow/config.json`), and the run ledger.

At the end of the week, capture:

1. `python .devflow/devflow.py stats` and `... digest --days 7` output —
   **these aggregates are all we ask for; never share `runs.jsonl` itself**
   (its task strings are your private work descriptions).
2. Your reaction the first time the gate denied you (justified? annoying?
   did the denial message tell you what to do?).
3. Whether any session started usefully oriented by the auto-brief.
4. The same three week-1 questions, for contrast.

## Reporting

Open one issue in the [devflow repo](https://github.com/yuriyvsavchuk/devflow/issues)
using the **Pilot feedback** template — it mirrors the questions above, so
reports stay comparable across pilots. Two smaller asks:

- Report **friction immediately** (separate issue, label `pilot-friction`)
  rather than batching it — a confusing denial message or a wrong dispatch is
  most diagnosable fresh.
- If you abandon the pilot, that is *also* a result we want — the template's
  last section asks only for the moment and reason you stopped.

## What we do with it

Pilot aggregates feed the public evidence record (anonymized, opt-in
otherwise) and directly steer the roadmap: the parked MCP adapter, the
headless smoke transport, and dispatch tuning all have explicit
"pilot-evidence" triggers. Your two weeks move real decisions.
