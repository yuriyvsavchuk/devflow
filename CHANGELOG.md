# Changelog

All notable changes to Devflow are recorded here. This file covers the public
individual framework; the private `devflow-team` extension tracks its own
history. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [2.4.0] — 2026-07-02

Context-isolation release — aligns the framework with Claude Code's
skills/subagents model: verbose work runs in isolated contexts, handoffs ride
durable artifacts instead of conversation state, and the definitions use the
platform's native mechanisms. Informed by a spec-conformance review of every
skill and agent definition.

### Added
- **Artifact-mediated security audit chain.** In the `devflow-audit` security
  adapter, `threat-modeler` now writes its full threat model to
  `docs/audits/<date>-threat-model-<slug>.md` and `dependency-auditor` its
  report to `docs/audits/<date>-dependency-audit-<slug>.md`; each returns only
  the path and headline items. `find-bugs` runs in its own isolated context
  (`context: fork`) and reads both artifacts from disk — the full-diff reading
  no longer floods the main conversation, and the artifacts double as the
  audit trail for the confirmation pass.
- **Skill preloading**: `test-engineer` preloads `test-driven-development`
  (subagents never see skills invoked in the main session; the platform's
  `skills` field replaces drift-prone duplication).
- **Native worktree isolation**: `spike-investigator` runs in a temporary
  auto-cleaned git worktree (`isolation: worktree`) — experiments cannot touch
  the developer's working tree. `using-git-worktrees` remains the manual,
  tool-agnostic path and now says so.
- **ADOPTION: "Subagents and context isolation"** — which roles run isolated
  and why, why the rails' gates still bind subagent tool calls, and which
  dialogue-driven skills deliberately stay in the main conversation.

### Changed
- Agent definitions declare model **aliases** (`sonnet`, `haiku`) instead of
  pinned model IDs, so each role tracks the current model generation and the
  cost tiering cannot silently break when an ID drifts.
- `find-bugs` Phase 0 discovers upstream security context from `docs/audits/`
  artifacts (or invocation arguments) instead of sniffing the conversation —
  required by the fork, and it makes standalone vs chained mode explicit.
- `subagent-driven-development` no longer implies subagents can ask the user
  questions mid-run: questions return to the coordinator and continue on
  re-dispatch or resume.
- `threat-modeler` and `dependency-auditor` gain `Write` — read-only with
  respect to everything except their own `docs/audits/` artifact.

## [2.3.0] — 2026-06-24

SDD Tier-1 — spec-anchored *verification*. Makes acceptance criteria
machine-checkable and surfaces when a spec and its tests drift apart, without
ever auto-rewriting either. Every check is advisory (detect-and-prompt).

### Added
- **Structured acceptance-criteria notation.** An `AC-n` line can carry a `gwt`
  (Given/When/Then), `ears` (EARS), or `prose` tag to declare its form; a bare
  `- AC-1:` stays valid. The `devflow-shape` spec template also gains first-class
  **Non-Goals**, expressed in the EARS `If…then` unwanted-behavior form.
- **`verify` spec-coverage check** — flags acceptance criteria (`AC-n`) that no
  test references, gated by a convention-in-use detector so it stays silent until
  a repo actually links specs to tests.
- **`verify` spec-drift check** — flags a spec edited more recently than the tests
  that cover it (word-boundary slug matching; `docs/specs/` excluded from the
  test scan).

## [2.2.0] — 2026-06-13

Validation layer — makes the framework's behavior regression-testable and its
value measurable.

### Added
- **Prompt-regression smoke harness** (`tests/smoke/`): an outcome-assertion
  checker (`smoke_check.py`) that judges scenarios by what verifiably happened —
  artifacts on disk, phase journals, ledger records, gate denials — never by
  model prose, so it survives model-version changes. Ships 10 scenarios: six
  playbook, three negative (asserting the dispatcher's restraint), one
  adversarial (asserting the gate denies a forced TDD violation).
- **Rails evidence journals**: `.devflow/marks-log.jsonl` and
  `.devflow/gate-log.jsonl`, written by the rails themselves so regression
  evidence never depends on the model reporting on its own behavior. Fail-open;
  gitignored.
- **Pilot kit**: [`docs/PILOTS.md`](docs/PILOTS.md) — a two-week protocol
  (week 1 Core-only, week 2 +Rails) — plus a structured feedback issue template.

### Changed
- The advisory `Stop` reminder is debounced to once per hour (it was re-firing
  every turn while a run stayed open).

## [2.1.0] — 2026-06-12

The v2 "everyday tool" rewrite. Replaces the per-message router with per-task
dispatch, adds a deterministic verification layer, and trims the framework to a
small, adoptable core. (There was no public 2.0.0 release; v2 first shipped as
2.1.0.) Upgrading from v1: see [MIGRATION-v2.md](MIGRATION-v2.md).

### Added
- **Dispatch + six playbooks + effort tiers.** `devflow-dispatch` classifies each
  task in one line (~800 tokens, once per task) into `devflow-shape` / `-build` /
  `-fix` / `-hotfix` / `-spike` / `-audit`, at a `quick` / `standard` / `full`
  effort tier. `devflow-hotfix` (production incidents with tracked debt) is new.
- **Rails** — a single-file stdlib CLI (`devflow.py`) with per-project run state
  in `.devflow/`, wired into Claude Code hooks: a SessionStart auto-brief
  (orientation, open hotfix debt, recent decisions; re-injects after compaction),
  a PreToolUse TDD gate (production edits denied until a failing test is marked)
  and protected-paths gate (human-only files), an advisory Stop reminder, and a
  run ledger with `stats`. Install with `python devflow.py init`; check with
  `doctor`. Fail-open by design.
- **`verify` chains** — spec/acceptance-criteria linkage, out-of-band commits,
  contract and ADR staleness; advisory locally, `--strict` for CI.
- **`digest`** — a recent-window summary of runs, debt, and decisions.
- **CI templates** (`ci/github-actions/`) — `verify` on PRs and a protected-TODO
  merge gate; advisory by default, hard-gate documented.
- **[`docs/ADOPTION.md`](docs/ADOPTION.md)** — three install levels (Core /
  +Rails / +Team-lite), each independently useful, plus the artifact front-matter
  conventions `verify` checks.
- Optional `Relates-to:` header on ADRs (enables the staleness check).

### Changed
- `using-devflow` is now a thin redirect carrying the full v1-pipeline →
  v2-playbook mapping; the slash command still resolves.
- Planning agents default to Sonnet and escalate to Opus only at `full` tier or
  XL/low-confidence sizing.
- `research` + `api-researcher` merged into a single `researcher` (general + API
  modes); `scope-estimator` folded into `task-planner` as a required sizing
  section.

### Removed
- Worker self-identification headers and `Worker compliance:` footers (the audit
  trail moved to durable artifacts and the run ledger).
- Per-message routing and persuasion-pressure routing language.
- The `hypothesis-validator` and `code-simplifier` skills (now modes of
  `devflow-spike` and the `code-simplification` agent).

## [1.0.0] — 2026-06-10

Initial public baseline — the router-based v1 framework: 22 skills, 18 agents,
and 11 named pipelines routed through the `using-devflow` skill before any work
begins. Superseded by the v2 line above; preserved as the migration starting
point.

[Unreleased]: https://github.com/yuriyvsavchuk/devflow/compare/v2.4.0...HEAD
[2.4.0]: https://github.com/yuriyvsavchuk/devflow/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/yuriyvsavchuk/devflow/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/yuriyvsavchuk/devflow/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/yuriyvsavchuk/devflow/compare/v1.0.0...v2.1.0
[1.0.0]: https://github.com/yuriyvsavchuk/devflow/releases/tag/v1.0.0
