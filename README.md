# Devflow

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) custom skills and worker agent definitions for disciplined, playbook-guided AI-assisted development.

**v2 model: playbooks guide, rails verify.** A lightweight dispatch skill classifies each new task into one of six playbooks at one of three effort tiers. Playbooks shape the order of work — requirements before plans, reproduction before fixes, measurement before optimization — and produce durable artifacts: specs, plans, ADRs, interface contracts, session records. The **rails** (a single-file CLI with run state, wired into Claude Code hooks) verify the discipline mechanically: sessions self-orient, the TDD gate holds, protected paths stay human-only, and every run leaves a ledger record. Copy-in CI templates carry the same checks to the merge boundary.

**New here? Start with [docs/ADOPTION.md](docs/ADOPTION.md)** — three levels, each a few minutes, each reversible.

## How It Works

1. A new task arrives → **`devflow-dispatch`** classifies it in one line: playbook + effort tier (~800 tokens of routing context, loaded once per task — not per message).
2. Only the **selected playbook** loads. It guides the work step by step and produces its artifacts along the way.
3. **Reviewer and acceptance roles run as fresh-context subagents** at standard/full tiers — independence by construction, with findings ranked Blocking / Non-blocking / Question.
4. Mid-course corrections are expected: every playbook transition re-checks "still the right playbook and tier?"

## Playbooks

| Playbook | Use for | Flow |
|---|---|---|
| `devflow-shape` | Requirements analysis, specification, planning | clarify → research gate → spec with `AC-n` criteria → size → plan |
| `devflow-build` | Features, behavior changes, refactors, performance | plan → contract → tests → implement → review → accept |
| `devflow-fix` | Bugs, stack traces, wrong behavior | reproduce → failing test → minimal fix → review → accept |
| `devflow-hotfix` | Production incidents | mitigate → verify → ship → record tracked debt → follow-up fix |
| `devflow-spike` | Feasibility questions, approach comparison | hypothesis → throwaway experiment → mandatory retrospective |
| `devflow-audit` | Review requests, security audits | scoped review → severity-ranked findings (security: threat model → dependency scan → review) |

Tests-only and docs-only work goes directly to the `test-engineer` / `docs-updater` agents — no playbook ceremony.

## Effort Tiers

| Tier | When | What runs |
|---|---|---|
| `quick` | Small, low-risk, no new interfaces | Playbook checklist inline; no subagents |
| `standard` *(default)* | Everything else | Playbook in main session + one fresh-context reviewer subagent |
| `full` | Public APIs, shared modules, risk keywords (auth, payment, migration…) | Independent reviewer + acceptance subagents; contracts; context maps |

The user's one-word override always wins: `quick: fix the date format` / `full: change the billing API`.

## Rails — what's enforced vs guided

Install once per project — run from **your project's root** (the directory you open Claude Code in), pointing at the framework's copy:

```sh
cd /path/to/your-project
python /path/to/devflow/devflow.py init   # scaffolds .devflow/, wires hooks merge-safe into .claude/settings.json
python .devflow/devflow.py doctor         # health check (your project now has its own pinned copy)
```

Prerequisites: Python 3 on PATH; on Windows, Git Bash (ships with Git for Windows — hooks run shell commands through it).

| Mechanism | Kind | What it does |
|---|---|---|
| Session brief (SessionStart hook, incl. after compaction) | **Automatic** | Injects orientation: open run + phase, open hotfix debt, latest decision/interface entries |
| TDD gate (PreToolUse hook) | **Enforced** | In a `fix`/`build` run at standard+ tier, production-file edits are denied until `mark red-confirmed`; tests/docs are never gated |
| Protected paths (PreToolUse hook) | **Enforced** | Paths listed in `.devflow/config.json` are denied to the agent unconditionally — human authorship required |
| Stop reminder | **Advisory** | A still-open run produces a gentle note; it never blocks the human |
| Run ledger + `stats` + `digest` | **Evidence** | One JSON record per run; all-time aggregates and a recent-window summary — the process becomes measurable |
| `verify` chains (+ CI templates in `ci/github-actions/`) | **Advisory → CI-enforceable** | Spec/AC linkage, spec-coverage & spec-drift (SDD), out-of-band commits, contract & ADR staleness; advisory locally, `--strict` at the merge boundary |
| Playbook discipline (step order, artifacts, severity-ranked review) | **Guided** | Prompt-level; the playbooks work with or without rails |

Fail-open by design: any rails error, missing config, or `"enabled": false` in `.devflow/config.json` means nothing is ever blocked — the rails can be wrong, they cannot break your session.

## What's Inside

- **`skills/`** — the dispatch skill, six playbooks, and the supporting process skills they call (`writing-plans`, `test-driven-development`, `systematic-debugging`, `poc-retrospective`, `session-continuity`, `finishing-a-development-branch`, and more).
- **`agents/`** — worker subagents with focused roles and per-role model tiers: planner, implementer, test engineer, reviewer, acceptance checker, researcher, triager, profiler, and others. Planning runs on Sonnet by default and escalates to Opus only for `full`-tier or XL/low-confidence work.

Every artifact lands in the repo: `docs/specs/`, `docs/decisions/` (ADRs), `docs/interfaces/` (contracts), `docs/sessions/` (continuity snapshots and hotfix debt), `docs/context-maps/`.

## Installation

```sh
# Skills
cp -r skills/* ~/.claude/skills/

# Agents
cp -r agents/* ~/.claude/agents/
```

Then add the activation line to your `~/.claude/CLAUDE.md` (or a project's `CLAUDE.md`):

```markdown
When a new development task begins, invoke the devflow-dispatch skill to classify it. Do not re-invoke for mid-task messages or follow-up confirmations.
```

**Migrating from v1:** the v1 `using-devflow` router is now a redirect with a full pipeline→playbook mapping — see [skills/using-devflow/SKILL.md](skills/using-devflow/SKILL.md). All v1 artifact directories and formats are unchanged.

## Team Extension

Devflow makes one developer (or a small team sharing a repo) more effective. The **Team Extension** (`devflow-team`) adds coordination for larger teams — structural ledger, decision broadcast, spec-driven QA, cadence/ceremony support. It is private and access-controlled; see [`team/README.md`](team/README.md) and [`team/GETTING-ACCESS.md`](team/GETTING-ACCESS.md).

## Releases

Version history is in [CHANGELOG.md](CHANGELOG.md) (Keep a Changelog + SemVer);
tagged releases with notes are on the [Releases page](https://github.com/yuriyvsavchuk/devflow/releases).
Upgrading from v1 → v2: [MIGRATION-v2.md](MIGRATION-v2.md).

## License

MIT — see [LICENSE](LICENSE). The private `devflow-team` extension is licensed separately.
