# Migrating from Devflow v1 to v2

**Date:** 2026-06-10
**Scope of this note:** the v2 Phase 1 restructuring ("Slim the Core"). Deterministic verification (CLI, hooks, CI) arrives in Phase 2 and will be documented separately.

## Why v2

Two independent audits of v1 reached the same conclusions: the 670-line router loaded on every message taxed every interaction, per-message routing over-triggered on trivial work, self-reported compliance footers proved nothing, and prompt-level "enforcement" was a claim the architecture could not honor. v2 keeps what worked — the artifact system, the sequencing doctrine, the loop-back discipline — and removes the rest. The new model: **playbooks guide, rails verify** (rails ship in Phase 2).

## The one-line change that activates v2

Replace the v1 line in your `~/.claude/CLAUDE.md` (and any project `CLAUDE.md`):

```markdown
# v1 — remove this:
Before responding to EVERY user message — no exceptions — invoke the `using-devflow` skill before doing any work.

# v2 — add this:
When a new development task begins, invoke the devflow-dispatch skill to classify it. Do not re-invoke for mid-task messages or follow-up confirmations.
```

## Upgrade steps

```sh
# 1. Re-copy skills and agents (overwrites updated files)
cp -r skills/* ~/.claude/skills/
cp -r agents/* ~/.claude/agents/

# 2. Remove components retired in v2 from your installation
rm -rf ~/.claude/skills/hypothesis-validator ~/.claude/skills/code-simplifier
rm -f  ~/.claude/agents/research.agent.md ~/.claude/agents/api-researcher.agent.md ~/.claude/agents/scope-estimator.agent.md

# 3. Update the CLAUDE.md activation line (see above)
```

## What replaced what

| v1 | v2 |
|---|---|
| `using-devflow` router (~12K tokens, every message) | `devflow-dispatch` (~0.8K tokens, once per task) + six playbooks loaded on selection |
| Pipeline 0 (Requirements) + Pipeline 2 (Unfamiliar API) | `devflow-shape` (research gate built in) |
| Pipeline 3 (Feature) + 5 (Refactor) + 9 (Performance) | `devflow-build` with feature / refactor / performance adapters |
| Pipeline 4 (Bug fix) | `devflow-fix` |
| — *(no v1 equivalent)* | `devflow-hotfix` — production incidents: mitigate → verify → ship → tracked debt |
| Pipeline 1 (Spike) + `hypothesis-validator` skill | `devflow-spike` (designed-experiment mode for narrow assumptions) |
| Pipeline 7 (Review) + Pipeline 10 (Security) | `devflow-audit` (security adapter) |
| Pipeline 6 (Test-only), Pipeline 8 (Docs-only) | Direct agent calls: `test-engineer`, `docs-updater` — no routing ceremony |
| `research` + `api-researcher` agents | `researcher` agent (general + API modes) |
| `scope-estimator` agent | task-planner's required **Size & Confidence** section |
| `code-simplifier` skill | `code-simplification` agent, invoked directly |
| Worker self-ID headers + `Worker compliance:` footers | Removed. Artifacts are the audit trail |
| "1% chance = MUST" routing pressure | Neutral classification with explicit negative triggers (trivial edits and conversation are exempt by design) |

## New in v2

- **Effort tiers** — `quick` / `standard` / `full`; dispatch suggests, your one-word override wins ("quick: …" / "full: …").
- **Review independence** — reviewer (and at `full` tier, acceptance) runs as a fresh-context subagent; findings ranked **Blocking / Non-blocking / Question**.
- **Model economy** — planning defaults to Sonnet; Opus only for `full`-tier or XL/low-confidence work.
- **Specs with stable IDs** — `devflow-shape` writes `docs/specs/<slug>.md` with numbered `AC-n` criteria that tests, reviews, and acceptance reference.
- **Hotfix debt tracking** — every production mitigation writes `docs/sessions/hotfix-debt-<slug>.md` (`status: open`) that only a follow-up `devflow-fix` run closes.

## What is unchanged

- **All artifact directories and formats:** `docs/decisions/` (ADRs), `docs/interfaces/` (contracts), `docs/sessions/`, `docs/context-maps/`. Nothing you produced with v1 needs migration.
- **The supporting skills:** `writing-plans`, `test-driven-development`, `systematic-debugging`, `poc-retrospective`, `session-continuity`, `finishing-a-development-branch`, `using-git-worktrees`, and the rest are still there and still invoked by the playbooks.
- **The discipline:** reproduce before fixing, test before merging, profile before optimizing, retrospective before closing a spike, decision records before implementation.

## Phase 2 upgrade — the rails (shipped)

Pull the latest framework, then per project — run `init` **from your project's root**, pointing at the framework's copy (running it inside the framework repo would scaffold the framework itself):

```sh
cd /path/to/your-project
python /path/to/devflow/devflow.py init   # one command: .devflow/ + hooks (merge-safe, idempotent, .bak before first change)
python .devflow/devflow.py doctor         # verify: python, Git Bash (Windows), hooks wired, version match
```

What changes day-to-day:

- **Every session starts oriented** — the SessionStart hook injects the brief (open run + phase, open hotfix debt, latest decisions); it re-injects after context compaction.
- **The TDD gate is mechanical** — in `fix`/`build` runs at standard+ tier, production edits are denied until `mark red-confirmed --evidence <test>`; tests and docs are never gated; `build` may record an explicit exception (`mark implemented --no-tdd "<why>"`).
- **Protected paths** — list human-only files (auth, billing, LICENSE…) in `.devflow/config.json` → the agent is denied unconditionally and instructed to leave a `TODO: [PROTECTED — human authorship required]`.
- **Runs leave evidence** — `python .devflow/devflow.py stats` shows runs, loop-backs, abandonment, durations.

Prerequisites: Python 3 on PATH; Git Bash on Windows. Escape hatch: `"enabled": false` in `.devflow/config.json` — or delete `.devflow/` — and nothing is ever blocked (the rails are fail-open at every layer). Install at the directory you open Claude Code in — that's the project root the hooks see.

## Phase 3 upgrade — everyday value (shipped)

Re-run `init` in each project to refresh the pinned copy (now **2.1.0** — `doctor` flags version skew):

- **`verify`** — structural checks over your artifacts: agreed specs must define `AC-n`, plans may only reference defined ACs, contracts and Accepted ADRs are nudged when their constrained paths churn after them, and commits outside run windows are surfaced. Advisory by default; `--strict` for CI; `--skip <check>` excludes visibly (a note, never silence).
- **`digest --days N`** — the windowed middle lens between `brief` (now) and `stats` (all time): recent runs with outcomes and loop-backs, in-flight work, open debt, latest decisions.
- **CI templates** at `ci/github-actions/` — `devflow-verify.yml` (advisory PR comment; `STRICT_GATE` switch for required-check enforcement) and `protected-todo-gate.yml` (fails PRs adding unresolved human-authorship markers).
- **ADR `Relates-to:`** — optional header line of path globs a decision constrains; powers the staleness nudge.
- **[docs/ADOPTION.md](docs/ADOPTION.md)** — the three-level install path and the artifact front-matter conventions in one place.
