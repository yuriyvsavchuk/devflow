# Adopting Devflow

Three levels. Each is independently useful, takes minutes, and is fully reversible — start at Level 1 today, add the next level when you feel the need, never before.

## Level 1 — Core: playbooks and artifacts (~5 minutes)

```sh
cp -r skills/* ~/.claude/skills/
cp -r agents/* ~/.claude/agents/
```

Add one line to `~/.claude/CLAUDE.md` (or a project's `.claude/CLAUDE.md`):

```markdown
When a new development task begins, invoke the devflow-dispatch skill to classify it. Do not re-invoke for mid-task messages or follow-up confirmations.
```

**What you get:** per-task dispatch into six playbooks with effort tiers; fresh-context reviewer subagents with Blocking / Non-blocking / Question findings; durable artifacts — specs with testable `AC-n` criteria, ADRs, interface contracts, hotfix debt records. No Python, no hooks, no moving parts: pure guidance plus artifacts, and it works (degraded) on non-Claude-Code tools too.

**Step back:** remove the CLAUDE.md line. Nothing else to clean up.

## Level 2 — + Rails: mechanical verification (~2 minutes)

Prerequisites: Python 3 on PATH; on Windows, Git Bash (ships with Git for Windows).

```sh
cd /path/to/your-project
python /path/to/devflow/devflow.py init
python .devflow/devflow.py doctor
```

**What you get on top of Level 1:**

| Mechanism | What it does |
|---|---|
| Session brief | Every session (and every post-compaction resume) starts oriented: open run, open hotfix debt, latest decisions |
| TDD gate | In `fix`/`build` runs at standard+ tier, production edits are mechanically denied until `mark red-confirmed` |
| Protected paths | Files you list in `.devflow/config.json` are denied to the agent unconditionally |
| Run ledger | `stats` (all-time), `digest --days N` (recent window) — your process becomes measurable |
| `verify` | Structural checks: spec/AC linkage, spec-coverage & spec-drift, out-of-band commits, contract and ADR staleness — advisory by default |

**Step back:** set `"enabled": false` in `.devflow/config.json`, or delete `.devflow/`. The rails are fail-open at every layer — they can be wrong, they cannot break your session. Your project keeps its own version-pinned copy; upgrade by re-running `init` (doctor flags version skew).

## Level 3 — + Team-lite: shared awareness through git (~10 minutes)

For a small team sharing one repository — coordination as a side effect of artifacts, no new ceremonies:

1. Commit `.devflow/config.json` (state and ledger stay gitignored — they're personal evidence; the *configuration* is shared, including protected paths the team agrees on).
2. Keep `docs/decisions/index.md` and `docs/interfaces/index.md` maintained (the playbooks do this) — **the session brief becomes your decision broadcast**: a teammate's ADR from yesterday appears in your brief this morning, via nothing more than `git pull`.
3. Copy the CI templates from `ci/github-actions/` into `.github/workflows/`: `devflow-verify.yml` (advisory PR comments; flip `STRICT_GATE` for a required check) and `protected-todo-gate.yml` (fails PRs that add unresolved human-authorship markers).

**Step back:** delete the workflows; stop committing the config. Larger teams with ceremony needs (dashboards, digests-to-standup, forecasting, spec-driven QA audit): that's the separate [Team Extension](../team/README.md).

## Ten-minute quickstart (solo, Levels 1+2)

1. Install Level 1, open Claude Code in your project, say: *"add an `--output json` flag to the export command"*.
2. Watch dispatch classify (`Playbook: devflow-build (standard) — …`) and open a run.
3. Try to make it edit production code before a failing test exists — watch the gate deny it (that denial is the rails working, not a bug).
4. Let the playbook finish: tests → implementation → reviewer subagent → acceptance → `finish`.
5. Run `python .devflow/devflow.py stats` — your first ledger entry.

## Subagents and context isolation

Devflow's reviewer, acceptance, researcher, and triager roles run as **subagents** — each in its own isolated context window. The verbose part of their work (reading full diffs, logs, web research) happens in that window and never enters your main conversation; only the structured findings return. This is context isolation, not just delegation: your main session stays at coordination altitude while the noisy exploration is contained.

Two facts worth knowing:

- **The rails hold under delegation.** PreToolUse gates fire for subagent tool calls too (hook payloads carry an `agent_id` when fired inside a subagent), so the TDD gate and protected paths bind an implementer subagent exactly as they bind the main session. Delegating is not an enforcement bypass.
- **Some skills deliberately stay in the main conversation.** `brainstorming`, `interview`, `session-continuity`, `receiving-code-review`, and `devflow-dispatch` are dialogue-driven or operate on the conversation history — things a subagent's fresh context never receives. Do not move them to an isolated context (`context: fork`); it would sever exactly the input they run on.

## Artifact front-matter conventions

These formats are the contract `verify` checks against. Deviations are treated as absence (a skip-note, never an error) — but stable formats are what make your artifacts machine-checkable.

| Artifact | Location | Required shape |
|---|---|---|
| Spec | `docs/specs/<slug>.md` | YAML front-matter `type: spec`, `status: draft\|agreed\|accepted`, `date:`; criteria as `- AC-1 \`gwt\|ears\|prose\`: <statement>` bullets (the notation tag is optional; bare `- AC-1: …` still valid). Plans reference the spec path(s) and their `AC-n` IDs — a plan may cite several specs; ACs are checked against the union |
| Hotfix debt | `docs/sessions/hotfix-debt-<slug>.md` | Front-matter `type: hotfix-debt`, `status: open\|closed`, `date:`. The brief nags while `open`; only a follow-up fix run closes it |
| ADR | `docs/decisions/NNNN-<slug>.md` | Header lines `**Status:** Accepted` and optional `**Relates-to:** <glob>, <glob>` — globs of paths the decision constrains; enables the staleness nudge |
| Indexes | `docs/decisions/index.md`, `docs/interfaces/index.md` | One `- <entry>` bullet per item, newest appended last; consumed by brief and digest |
| Contract map | `.devflow/config.json` → `contract_map` | `{"docs/interfaces/<file>": ["src/api/*", …]}` — enables contract-staleness checking |

Two semantics worth knowing: **staleness checks are all-time** comparisons of git commit dates (`--window-days` scopes only the out-of-band check), and the `contract_map` / `Relates-to` patterns are passed to git as **pathspecs, where `*` matches across directory separators by default** — `src/api/*` covers the whole subtree, verified empirically. Header forms accepted for ADRs: `**Relates-to:**`, `Relates-to:`, or `relates-to:`.

### Spec ↔ test linkage (SDD Tier-1)

`verify` adds two **detect-and-prompt** checks (advisory; they never modify a file):

- **spec-coverage** — an agreed spec's `AC-n` with no referencing test. A test *covers* a spec's `AC-n` when a **test file** (a `test`/`tests`/`spec` path segment, or a `test_*` / `*_test` / `*.test.*` / `*.spec.*` filename) mentions both the spec **slug** (its filename stem, matched on word boundaries) and the token `AC-n` — e.g. a test named `test_<slug>_ac3` or a `# covers: <slug> AC-3` comment. This is a lightweight ID-reference convention, not a requirements database. The check stays silent until the convention is in use (≥1 test references a spec AC), so it never floods a project that hasn't adopted it.
- **spec-drift** — an agreed spec whose covering tests have a newer last-commit date than the spec itself (the behavior evolved; the spec lagged). Bidirectional with spec-coverage; both reuse the git-date staleness machinery.

Neither check auto-syncs spec and code — they surface a gap for you to reconcile, by design.
