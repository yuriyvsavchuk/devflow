# Devflow User Manual

> **Applies to Devflow v2.** This is the usage guide. For the one-page conceptual overview see [README.md](README.md); to install step-by-step see [docs/ADOPTION.md](docs/ADOPTION.md); to upgrade from v1 see [MIGRATION-v2.md](MIGRATION-v2.md); for version history see [CHANGELOG.md](CHANGELOG.md).

Devflow keeps AI-assisted development *disciplined*: requirements before code, a failing test before a fix, measurement before optimization, verification before "done." It does this two ways — **playbooks guide** the order of work, and **rails verify** the discipline mechanically. You keep working in plain language; Devflow supplies the structure and leaves a durable trail behind.

## Contents

1. [The idea in 60 seconds](#1-the-idea-in-60-seconds)
2. [Before you start](#2-before-you-start)
3. [A day with Devflow](#3-a-day-with-devflow)
4. [The six playbooks](#4-the-six-playbooks)
5. [Effort tiers](#5-effort-tiers)
6. [The rails](#6-the-rails)
7. [Specs and the SDD practice](#7-specs-and-the-sdd-practice)
8. [Artifacts](#8-artifacts)
9. [Worked examples](#9-worked-examples)
10. [Quick reference](#10-quick-reference)

---

## 1. The idea in 60 seconds

Ask an AI assistant for help and it tends to *start doing* immediately — writing code before the problem is understood, fixing before the cause is confirmed, claiming done without checking. The capability is there; the **discipline** isn't.

Devflow adds that discipline as two cooperating layers:

- **Playbooks guide.** Each task is routed to a short playbook that sequences the work — clarify before plan, reproduce before fix, hypothesis before spike — and drops durable artifacts (specs, plans, ADRs, contracts, session records) as it goes.
- **Rails verify.** An optional single-file CLI, wired into Claude Code hooks, checks the discipline mechanically: sessions self-orient, the test-first gate holds, human-only files stay human-only, and every run leaves a ledger record.

**Who it's for:** solo developers who want consistent AI assistance across sessions, and small teams who want shared discipline to fall out of ordinary `git` use — no new ceremonies. Best on Claude Code; the guidance layer still works (degraded) on other AI tools.

You can adopt just the guidance layer and stop there. The rails are additive, and everything is reversible.

## 2. Before you start

This guide assumes Devflow is installed. There are two states you might be in:

- **Level 1 — Core (guidance + artifacts):** the dispatch skill and worker agents copied into `~/.claude/`, plus one activation line in your `CLAUDE.md`. Pure prompt-level guidance — no Python, no hooks.
- **Level 2 — + Rails (mechanical verification):** Level 1 plus `devflow.py init` run in your project, so the session brief, the TDD gate, protected paths, and `verify` are live (see §6).

Both take a few minutes and are fully reversible. **[docs/ADOPTION.md](docs/ADOPTION.md) is the canonical install guide** — the exact commands, all three levels (including team-lite), prerequisites, the ten-minute quickstart, and the artifact-format rules. Install there, then come back here for how to use it.

## 3. A day with Devflow

You don't memorize commands. You describe the task in plain language; Devflow routes it.

1. **You state a task** — "add an `--output json` flag to the export command."
2. **`devflow-dispatch` classifies it once** — one line naming the playbook and effort tier, e.g. `Playbook: devflow-build (standard) — small feature, no new public interface`. This costs ~800 tokens of routing context, loaded once per task, not on every message.
3. **Only the selected playbook loads** and guides the work step by step, producing its artifacts along the way.
4. **Independent review happens by construction** — at `standard` and `full` tiers, reviewer and acceptance roles run as *fresh-context subagents*, so the reviewer never just agrees with the implementer. Findings come back ranked **Blocking / Non-blocking / Question**.
5. **Course corrections are expected** — at each playbook transition Devflow re-asks "still the right playbook and tier?" and switches if the work changed shape.

**You're always in control of routing.** A one-word prefix overrides the classifier: `quick: fix the date format` or `full: change the billing API`. And purely mechanical work skips the ceremony entirely — tests-only requests go straight to the `test-engineer` agent, docs-only to `docs-updater`.

## 4. The six playbooks

| Playbook | Reach for it when… | Flow |
|---|---|---|
| **`devflow-shape`** | Requirements are unclear, or you need a spec or a plan | clarify → research gate → spec with `AC-n` criteria → size → plan |
| **`devflow-build`** | Building a feature, changing behavior, refactoring, or optimizing | plan → contract → tests → implement → review → accept |
| **`devflow-fix`** | Something is broken — a bug, a stack trace, wrong output | reproduce → failing test → minimal fix → review → accept |
| **`devflow-hotfix`** | Production is down and speed beats ceremony | mitigate → verify → ship → record tracked debt → follow-up fix |
| **`devflow-spike`** | "Is X feasible?" / "which approach?" | hypothesis → throwaway experiment → mandatory retrospective |
| **`devflow-audit`** | "Review this" or "run a security audit" | scoped review → severity-ranked findings (security adds: threat model → dependency scan → review) |

The playbooks call shared process skills as needed — `writing-plans`, `test-driven-development`, `systematic-debugging`, `poc-retrospective`, `session-continuity`, `finishing-a-development-branch`, and others — so the same disciplines show up consistently across tasks.

## 5. Effort tiers

The same playbook runs at the depth the task warrants.

| Tier | When it's chosen | What runs |
|---|---|---|
| **`quick`** | Small, low-risk, no new interfaces | Playbook checklist inline; no subagents |
| **`standard`** *(default)* | Most work | Playbook in the main session + one fresh-context reviewer subagent |
| **`full`** | Public APIs, shared modules, risk keywords (auth, payment, migration, crypto…) | Independent reviewer **and** acceptance subagents; interface contracts; context maps |

Your explicit one-word override always wins over the classifier's guess.

## 6. The rails

Level 2 turns prompt-level guidance into mechanical checks. They work *for* you in the background:

| What you get | Kind | In plain terms |
|---|---|---|
| **Session brief** | Automatic | Every session — including after a context compaction — starts oriented: any open run and its phase, open hotfix debt, the latest decisions and interface entries. |
| **TDD gate** | Enforced | Inside a `fix`/`build` run at `standard`+ tier, edits to production files are denied until you've marked a confirmed failing test (`mark red-confirmed`). Tests and docs are never gated. |
| **Protected paths** | Enforced | Files you list in `.devflow/config.json` are off-limits to the agent unconditionally — human authorship required (licenses, ownership files, anything you reserve). |
| **Stop reminder** | Advisory | If a run is still open when you stop, you get a gentle nudge. It never blocks you. |
| **Ledger + `stats` + `digest`** | Evidence | One JSON record per run; `stats` gives all-time aggregates, `digest` a recent window. Your process becomes measurable. |
| **`verify` chain** | Advisory → CI | Structural checks (see §7) — advisory locally, `--strict` at the merge boundary via the CI templates. |

**Fail-open by design.** Any rails error, missing config, or `"enabled": false` means *nothing is blocked*. The rails can be wrong; they cannot break your session. Each project keeps its own version-pinned copy — `doctor` flags version skew, and re-running `init` upgrades it.

The lifecycle commands (`start` / `mark` / `finish`) are normally driven by the playbooks during a run; the ones you'll run yourself are `init`, `doctor`, `verify`, `stats`, and `digest` (see §10).

## 7. Specs and the SDD practice

Devflow's specs are lightweight and *machine-checkable*. A spec lives at `docs/specs/<slug>.md`, carries YAML front-matter, and lists acceptance criteria as `AC-n` bullets. Each criterion may declare its **notation** with an optional tag — and a bare `- AC-1: …` is always still valid:

- **`gwt`** — Given / When / Then, for behavioral criteria
- **`ears`** — EARS phrasing, best for constraints, invariants, and unwanted behavior
- **`prose`** — plain language, the fallback

First-class **Non-Goals** state what the change must *not* do, in the EARS `If…then` unwanted-behavior form. Example:

```markdown
---
type: spec
status: agreed
date: 2026-06-24
---

# Export command — JSON output

- AC-1 `gwt`: Given the export command, when run with `--output json`, then it writes valid JSON to stdout and exits 0.
- AC-2 `ears`: While `--output json` is set, the command shall emit no human-readable log lines on stdout.
- AC-3 `prose`: `--output` defaults to `text` when the flag is omitted.

## Non-Goals
- `ears`: If the user passes an unknown `--output` value, then the command shall exit non-zero — it shall not silently fall back to a default.
```

**Keeping specs and tests honest (SDD Tier-1).** `verify` adds two *detect-and-prompt* checks — advisory, and they never modify a file:

- **spec-coverage** — flags an agreed spec's `AC-n` that no test references. A test *covers* an `AC-n` when a test file mentions both the spec **slug** and the token `AC-n` — e.g. a test named `test_export_command_ac1`, or a `# covers: export-command AC-1` comment. It's a lightweight ID convention, not a requirements database, and it stays silent until at least one test uses it — so it never floods a project that hasn't opted in.
- **spec-drift** — flags an agreed spec whose covering tests were edited more recently than the spec itself: the behavior moved on and the spec lagged.

Neither check auto-syncs spec and code — by design they surface the gap and let you reconcile it. (`verify` also checks spec/plan `AC` linkage, out-of-band commits, and contract/ADR staleness; full format rules are in [docs/ADOPTION.md](docs/ADOPTION.md#artifact-front-matter-conventions).)

## 8. Artifacts

Every playbook leaves its work in the repo, in predictable places. That's what makes the discipline durable and — with Level 3 — shareable: a teammate's ADR from yesterday shows up in your session brief this morning via nothing more than `git pull`.

| Artifact | Lives in | Is |
|---|---|---|
| Specs | `docs/specs/` | requirements with testable `AC-n` criteria |
| ADRs | `docs/decisions/` | architecture decisions (`NNNN-<slug>.md`) + an `index.md` |
| Interface contracts | `docs/interfaces/` | API/module boundaries agreed before implementation |
| Session records | `docs/sessions/` | continuity snapshots and hotfix-debt records |
| Context maps | `docs/context-maps/` | the blast radius traced for a change |

## 9. Worked examples

| You say… | Devflow routes to… |
|---|---|
| "I have an idea for a feature but haven't pinned down the requirements." | **`devflow-shape`** → a spec with `AC-n` criteria and a sized plan, before any code. |
| "Add an `--output json` flag to the export command." | **`devflow-build` (standard)** → plan → failing tests → implementation → reviewer subagent → acceptance. |
| "Users are getting a 500 on checkout — here's the stack trace." | **`devflow-fix`** → reproduce → failing regression test → minimal fix → review. |
| "Payments are failing in production right now." | **`devflow-hotfix`** → mitigate and verify first, then a recorded debt item for the real fix. |
| "Can we use WebSockets here before we commit to it?" | **`devflow-spike`** → throwaway experiment → retrospective with a Proceed/Pivot/Abandon call. |
| "Review the changes on this branch." / "Security-audit the payment flow." | **`devflow-audit`** → severity-ranked findings (the security path adds a threat model and dependency scan). |
| "We're out of time — pick this up tomorrow." | **`session-continuity`** → a snapshot so the next session resumes without re-deriving context. |

## 10. Quick reference

**Pick a playbook**

- Unclear requirements / need a spec or plan → **shape**
- Build / change / refactor / optimize → **build**
- Something's broken → **fix**
- Production incident → **hotfix**
- Feasibility or approach question → **spike**
- Review or security audit → **audit**
- Only tests → `test-engineer`; only docs → `docs-updater`
- Override routing with a one-word prefix: `quick:` / `standard:` / `full:`

**Rails commands** — recurring use, once installed (setup is in [docs/ADOPTION.md](docs/ADOPTION.md)). Run from your project root:

```sh
python .devflow/devflow.py doctor            # health check / version-skew check
python .devflow/devflow.py verify            # structural checks (add --strict in CI)
python .devflow/devflow.py stats             # all-time ledger aggregates
python .devflow/devflow.py digest --days 7   # recent-window summary
```

(`start` / `mark` / `finish` exist too, but the playbooks usually drive them for you.)

**Go deeper**

- [README.md](README.md) — the model at a glance
- [docs/ADOPTION.md](docs/ADOPTION.md) — install levels and artifact format rules
- [MIGRATION-v2.md](MIGRATION-v2.md) — upgrading from the v1 router
- [CHANGELOG.md](CHANGELOG.md) — what changed, version by version
- [team/README.md](team/README.md) — the private Team Extension (coordination at larger scale)
